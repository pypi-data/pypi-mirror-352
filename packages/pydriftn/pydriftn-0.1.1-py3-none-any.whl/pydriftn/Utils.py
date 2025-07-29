from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy.wcs import WCS

import astroscrappy
import warnings
import numpy as np

import logging


file_handler = logging.FileHandler("logfile.log")
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

class ImageImporter:
    '''
    This class object imports the data from the given FITS file path and ccd_name.
    Also includes a cosmic ray removal function. 

    Parameters
    ----------
    ccd_name: str
        The name of the CCD.
    filepath: str
        The local path to the FITS file.
        
    '''
    def __init__(self, ccd_name, filepath):
        '''Initialises ImageImporter with ccd_name and filepath.'''
        
        self.ccd = ccd_name
        self.filepath = filepath


    def open_fits(self):
        '''
        Opens a FITS file.

        Returns
        -------
        fits_file: ``astropy.io.fits.HDUList`` class
            ``HDUList`` containing all of the header data units in the file.
        '''

        try:
            fits_file = fits.open(self.filepath)
        except OSError as oe:
            logger.error("Cannot open file: {}.".format(filepath), exc_info=True)
            fits_file = None
        except FileNotFoundError as fe:
            logger.error("Cannot find file: {}.".format(filepath), exc_info=True)
            fits_file = None
        
        return fits_file


    def get_fits_header(self):
        '''
        Retrieves the FITS header.

        Returns
        -------
        hdr: ``astropy.io.fits.header.Header`` class object.
        '''

        fits_file = self.open_fits()
        if fits_file:
            with fits_file:
                try:
                    hdr = fits_file[0].header
                except AttributeError:
                    logger.error("Error opening file: {}.".format(self.filepath), exc_info=True)
                    hdr = None
        else:
            hdr = None 
        self.hdr = hdr

        return hdr

    
    def get_pixscale(self, primary_header):
        '''
        Retrieves pixelscale information from the primary header of a FITS file.

        Returns
        -------
        pixscale: float
            The pixel scale of the image.
        '''
        try:
            pixscale = primary_header['PIXSCAL1']
        except KeyError as k:
            logger.warning('No PIXSCAL1 info in FITs header. Please check the keyword.')
            pixscale = 0.27
            logger.info('Using 0.27 as the default pixscale.')
            
        self.pixscale = pixscale
        return pixscale


    def get_fits_image(self):
        '''
        Retrieves the header and data for a given extension of the FITS file.

        Returns
        -------
        ccd_hdr: ``astropy.io.fits.hdu.compressed.header.CompImageHeader`` class object.
        ccd_data: ``numpy.ndarray`` of the image.
        '''

        fits_file = self.open_fits()
        if fits_file:
            with fits_file:
                try:
                    ccd_hdr = fits_file[self.ccd].header 
                    ccd_data = fits_file[self.ccd].data
                except (KeyError, AttributeError) as e:
                    logger.error("CCD name not found for file: {}.".format(self.filepath), exc_info=True)
                    ccd_hdr = ccd_data = None                             
        else:
            ccd_hdr = ccd_data = None
        self.ccd_hdr = ccd_hdr
        self.ccd_data =  ccd_data # previously self.data
        
        return ccd_hdr, ccd_data


    def get_background(self, ccd_header, ccd_data):
        '''
        Retrieves the background value from a FITS image.

        Parameters
        ----------
        ccd_header: ``astropy.io.fits.hdu.compressed.header.CompImageHeader`` class object.
        ccd_data: ``numpy.ndarray`` of the image.
        
        Returns
        -------
        background: float
            The estimated background value.
        '''

        try:
            background = ccd_header['AVSKY']
        except TypeError as t:
            logger.error('Invalid extension name')
        except KeyError as k:
            logger.info('No AVSKY info in FITs header. Calculating background value with sigma_clipped_stats...')
            background = sigma_clipped_stats(ccd_data, sigma=3.0)[1] #(median value)
        
        return background


    def wcs_transform(self, header):
        '''
        Gets WCS transformations for the FITS file.

        Returns
        -------
        ``astropy.wcs.WCS`` class
        
        '''

        if header:
            try:
                wcs_fits = WCS(self.ccd_hdr)
            except (MemoryError, ValueError, KeyError) as e:
                logger.error("Failed to perform WCS transformations for file: {}.".format(self.filepath), exc_info=True)
                wcs_fits = None
            else: 
                logger.info("{}: successfully transformed the fits file header into WCS.".format(self.filepath))  
        else: 
            wcs_fits = None
        self.wcs_fits = wcs_fits # previously self.wcs

        return wcs_fits       


    def cosmicray_removal(self, ccd_hdr, ccd_data, gain_keyword = ['GAINA', 'GAINB'], 
                          saturation_keyword = ['SATURATA', 'SATURATB'], readnoise_keyword = ['RDNOISEA', 'RDNOISEB']):
        '''
        Detects and removes cosmic rays in the FITS image.

        Parameters
        ----------
        ccd_hdr: ``astropy.io.fits.hdu.compressed.header.CompImageHeader`` class object.
        ccd_data: ``numpy.ndarray`` of the image.
        gain_keyword: list
            Keywords for the gain values of interest.
        saturation_keyword: list
            Keywords for the gain values of interest.
        readnoise_keyword: list
            Keywords for the gain values of interest.

        Returns
        -------
        cr_mask: boolean ``numpy.ndarray``
            The cosmic ray mask (boolean) array with values of True where there are cosmic ray detections.
        clean_data: float ``numpy.ndarray``
            The cleaned data array after the cosmic ray removal.
            
        '''
        
        gain_median = np.median([ccd_hdr[gain] for gain in gain_keyword])
        readnoise_median = np.median([ccd_hdr[readnoise] for readnoise in readnoise_keyword])
        saturation_median = np.median([ccd_hdr[saturate] for saturate in saturation_keyword])

        self.gain = gain_median
        self.readnoise = readnoise_median
        self.saturation = saturation_median
        
        try:
            crmask, clean_data = astroscrappy.detect_cosmics(ccd_data, gain=gain_median,
                                                                readnoise=readnoise_median, satlevel=saturation_median, cleantype='medmask')
        except Exception as e: # TODO: specify the error
            logger.error("Cannot generate cosmic ray mask.", exc_info=True)
            clean_mask = clean_data = None
            
        self.cr_mask = crmask
        self.clean_data = clean_data

        # TODO: save 

        return crmask, clean_data


def append_to_fits_header(self, ccd_hdr, keys:list, values:list, comments:list):
    '''
    Appends lists of values and comments to a list of keys in an image header with parallel iteration.

    Parameters
    ----------
    ccd_hdr: ``astropy.io.fits.hdu.compressed.header.CompImageHeader`` class object.
    keys: list
        A list of keyword names to be added to / updated in the image header.
    values: list
        A list of values to be added to the paired keys in the image header.
    comments: list
        A list of comments to be added along with the paired values, to the paired keys in the image header.

    '''
    # always new keys?
    # set strict=True?

    for k, v, c in zip(keys, values, comments):
        ccd_hdr[k] = (v, c)


def get_bbox_coords_from_centre_coords(xcent, ycent, obj_shape, img_dim):
    '''
    Given the coordinates of the centre of a star/driftscan and the object shape,
    defines bounding box coordinates.

    Parameters
    ----------
    xcent: float or int
        The x-coordinate of the centre of the object.
    ycent: float or int
        The y-coordinate of the centre of the object.
    obj_shape: tuple
        (height, width) tuple of the object.
    img_dim: tuple
        (height, width) tuple of the whole image.

    Returns
    -------
    x1: int
        The x-min / the x-coordinate of the top left corner.
    x2: int
        The x-max/ the x-coordinate of the bottom right corner.
    y1: int
        The y-min / the y-coordinate of the top left corner.
    y2: int
        The y-max / the y-coordinate of the bottom right corner.

    '''
    h, w = obj_shape
    img_h, img_w = img_dim
    y1 = int(ycent - 0.5*h - 1)
    if y1 < 0:
        y1 = 0

    y2 = y1 + h
    if y2 > img_h:
        y2 = img_h

    x1 = int(xcent - 0.5*w - 1)
    if x1 < 0:
        x1 = 0

    x2 = x1 + w
    if x2 > img_w:
        x2 = img_w

    return (x1, x2, y1, y2)