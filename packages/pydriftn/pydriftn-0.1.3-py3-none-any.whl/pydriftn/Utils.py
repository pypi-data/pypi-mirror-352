from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy.wcs.utils import skycoord_to_pixel
import astropy.units as u

import os 
import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, ListedColormap
import matplotlib.patches as mpatches
import cmasher as cm
from skimage.draw import circle_perimeter, rectangle_perimeter

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
    This class object imports the data from the given FITS file path.
    Also includes a cosmic ray removal function. 

    Parameters
    ----------
    filepath: str
        The local path to the FITS file.
        
    '''
    def __init__(self, filepath):
        '''Initialises ImageImporter with ccd_name and filepath.'''
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
            logger.error("Cannot open file: {}.".format(self.filepath), exc_info=True)
            fits_file = None
        except FileNotFoundError as fe:
            logger.error("Cannot find file: {}.".format(self.filepath), exc_info=True)
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

        return pixscale
    
    def get_mean_ellipticity(self, fits_file):
        ellipticities = []
        for i in range(1, 62):
            # extensions in DECam data
            ccd_hdr = fits_file[i].header
            ellipticity = ccd_hdr['ELLIPTIC']
            if ellipticity != 0:
                ellipticities.append(ellipticity)
        mean_ellipticity = np.mean(ellipticities)

        return mean_ellipticity

    def get_fits_image(self, ccd_name):
        '''
        Retrieves the header and data for a given extension of the FITS file.

        Parameters
        ----------
        ccd_name: str
            The name of the CCD.


        Returns
        -------
        ccd_hdr: ``astropy.io.fits.hdu.compressed.header.CompImageHeader`` class object.
        ccd_data: ``numpy.ndarray`` of the image.
        '''

        fits_file = self.open_fits()
        if fits_file:
            with fits_file:
                try:
                    ccd_hdr = fits_file[ccd_name].header 
                    ccd_data = fits_file[ccd_name].data
                except (KeyError, AttributeError) as e:
                    logger.error("CCD name not found for file: {}.".format(self.filepath), exc_info=True)
                    ccd_hdr = ccd_data = None                             
        else:
            ccd_hdr = ccd_data = None
        
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

        Parameter
        ---------
        header: ``astropy.io.fits.hdu.compressed.header.CompImageHeader`` class object.
        
        Returns
        -------
        wcs_fits: ``astropy.wcs.WCS`` class
        
        '''

        if header:
            try:
                wcs_fits = WCS(header)
            except (MemoryError, ValueError, KeyError) as e:
                logger.error("Failed to perform WCS transformations for file: {}.".format(self.filepath), exc_info=True)
                wcs_fits = None
            else: 
                logger.info("{}: successfully transformed the fits file header into WCS.".format(self.filepath))  
        else: 
            wcs_fits = None
        #self.wcs_fits = wcs_fits # previously self.wcs

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
        
        try:
            crmask, clean_data = astroscrappy.detect_cosmics(ccd_data, gain=gain_median,
                                                                readnoise=readnoise_median, satlevel=saturation_median, cleantype='medmask')
        except Exception as e: # TODO: specify the error
            logger.error("Cannot generate cosmic ray mask.", exc_info=True)
            clean_mask = clean_data = None

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


def find_which_ccd(fits_path, ra, dec):
    '''
    Given a path to a FITS file, ra and dec values, 
    loop through extensions to find where the pair of coordinates belongs to.

    Parameters
    ----------
    fits_path: str
        The local path to the FITS file.
    ra: float
    dec: float

    Returns
    -------
    found_in: list
        The list of name(s) or index(es) of the extension(s) that contains the coordinates.

    '''
    found_in = []
    Image = ImageImporter(found_in, fits_path)
    fits_file = Image.open_fits()

    for e in range(1, len(fits_file)):
        # loop through all extensions
        ccd_header = fits_file[e].header

        try:
            img_w = int(ccd_header['NAXIS1'])
        except KeyError as k:
            logger.warning('No NAXIS1 info in FITS header. Please check the keyword.')
            img_w = 2046
            logger.info('Using 2046 as the default image width value.')

        try:
            img_h = int(ccd_header['NAXIS2'])
        except KeyError as k:
            logger.warning('No NAXIS2 info in FITS header. Please check the keyword.')
            img_h= 4094
            logger.info('Using 4094 as the default image height value.')

        # Get WCS from extension header
        ccd_wcs = Image.wcs_transform(ccd_header)
        skycoordinates = SkyCoord(ra*u.deg, dec*u.deg, unit="deg")
        pix_pos = skycoord_to_pixel(skycoordinates, ccd_wcs)
        if pix_pos is not None:
            if 0 <= pix_pos[0] <= img_w:
                if 0 <= pix_pos[1] <= img_h:
                    # the extension contains the input coordinates
                    try:
                        # get the name of the CCD
                        fits_extension = ccd_header['EXTNAME']
                    except KeyError as k:
                        # return index instead
                        logger.warning('Extension found, but there is no EXTNAME info in FITS header. Returning the extension index.')
                        fits_extension = e
                    found_in.append(fits_extension)
    return found_in


def stadium_perimeter(ref_star_id, cutout_data, x0, y0, length, radius, output_path, pad=0):
    '''
    This function uses combinations of scikit.draw perimeter objects to draw the contours of a stadium apeture
    Note that the apeture is 'jagged', it traces whole pixels; a direct result of ndarray indexing.
    
    NOTE: This function is only used for plotting apetures, since some pixel conventions differ from Photutils.
    
    Potential: there may be a smart way of joining the stadium across fractions of pixels to form a precise apeture.
    
    Parameters
    ----------
    ref_star_id: str
        The ID of the star to be plotted.
    cutout_data: float ``numpy.ndarray``
        The 2D cutout array of the CCD chip.
    x0: int
        x-coordinate of the centroid of a detected driftscan, scaled to the image cutout.
    y0: int
        y-coordinate of the centroid of a detected driftscan, scaled to the image cutout.
    length: int
        The driftscan length in the x-direction.
    radius: int
        the radius of the semi-circular caps of the stadium shape,
        and half the width of the rectangular body in the y-direction.
    output_path: str

    pad: int
        The number of pixels within the annulus,
        projected around the perimeter of the inner stadium aperture.
        (Default: 0)
    '''
    plot_output_dir = os.path.join(output_path, 'aperture_plots')
    if not os.path.exists(plot_output_dir):
        os.mkdir(plot_output_dir)
    
    #plotting global definition of colourmaps
    drift_cmap = cm.rainforest
    contour_cmap = cm.take_cmap_colors(cm.guppy, 2, return_fmt='hex')
    
    timestamp = str(datetime.datetime.now().isoformat())

    plt.figure(figsize = (5,5), dpi = 150)
    
    try:
        #Make individual apeture perimiters
        contour = np.zeros(cutout_data.shape)
        
        rlhs, clhs = circle_perimeter(int(y0), int(x0 - length//2), int(radius))
        rrhs, crhs = circle_perimeter(int(y0), int(x0 + length//2), int(radius))
        start = (int((y0-1)+radius), int(x0 - length//2))
        end = (int((y0+1)-radius), int(x0 + length//2))
        rRect, cRect = rectangle_perimeter(start = start, end=end, shape=cutout_data.shape)

        #define the additive contour lines
        # Make sure they are inside the cutout region
        rlhs = [rl if rl >= 0 else 0 for rl in rlhs]
        rlhs = [rl if rl < cutout_data.shape[0] else cutout_data.shape[0]-1 for rl in rlhs]

        clhs = [cl if cl >= 0 else 0 for cl in clhs]
        clhs = [cl if cl < cutout_data.shape[1] else cutout_data.shape[1]-1 for cl in clhs]

        rrhs = [rr if rr >= 0 else 0 for rr in rrhs]
        rrhs = [rr if rr < cutout_data.shape[0] else cutout_data.shape[0]-1 for rr in rrhs]

        crhs = [cr if cr >= 0 else 0 for cr in crhs]
        crhs = [cr if cr < cutout_data.shape[1] else cutout_data.shape[1]-1 for cr in crhs]

        contour[rlhs, clhs] = 1
        contour[rrhs, crhs] = 1
        contour[rRect, cRect] = 1

        #hollow out the inside of the apeture to avoid plotting intersections and cross-hairs
        contour[end[0]:start[0]+1, start[1]-1:end[1]+2] = 0

    except:
        logger.warning('DSI located near to image boundary. Plot_star method returning None.') 

    else:           
        plt.imshow(cutout_data, cmap=drift_cmap) # plot 1   
        plt.imshow(contour, cmap = ListedColormap(['None', contour_cmap[0]])) # plot 2
        plt.scatter([x0], [y0], c ='k', marker = '+', s = 100) # plot 3

        #if pad is not None, define a second aperture to plot the annulus of the driftscan
        if pad != 0:
            outer_contour = np.zeros(cutout_data.shape)

            rlhs, clhs = circle_perimeter(int(y0), int(x0 - length//2), int(radius+pad))
            rrhs, crhs = circle_perimeter(int(y0), int(x0 + length//2), int(radius+pad))

            start = (int((y0-1)+radius+pad), int(x0 - length//2))
            end = (int((y0+1)-(radius+pad)), int(x0 + length//2))

            rRect, cRect = rectangle_perimeter(start = start, end=end, shape=cutout_data.shape)
            
            rlhs = [rl if rl >= 0 else 0 for rl in rlhs]
            rlhs = [rl if rl < cutout_data.shape[0] else cutout_data.shape[0]-1 for rl in rlhs]

            clhs = [cl if cl >= 0 else 0 for cl in clhs]
            clhs = [cl if cl < cutout_data.shape[1] else cutout_data.shape[1]-1 for cl in clhs]

            rrhs = [rr if rr >= 0 else 0 for rr in rrhs]
            rrhs = [rr if rr < cutout_data.shape[0] else cutout_data.shape[0]-1 for rr in rrhs]

            crhs = [cr if cr >= 0 else 0 for cr in crhs]
            crhs = [cr if cr < cutout_data.shape[1] else cutout_data.shape[1]-1 for cr in crhs]
            
            outer_contour[rlhs, clhs] = 1
            outer_contour[rrhs, crhs] = 1                    
            
            outer_contour[rRect, cRect] = 1
            outer_contour[end[0]:start[0]+1, start[1]-1:end[1]+2] = 0  
        
            plt.imshow(outer_contour, cmap = ListedColormap(['None', contour_cmap[1]])) # plot 4
            
            #Combine Legend objects
            labels = {0:'DSI Centroid', 1:'Inner Aperture', 2:'Outer Aperture'}
            combined_cmaps = ['k', contour_cmap[0], contour_cmap[1]]
        
        else:
            #Combine Legend objects
            labels = {0:'DSI Centroid', 1:'Inner Aperture'}
            combined_cmaps = ['k', contour_cmap[0]]
    
        patches =[mpatches.Patch(color=combined_cmaps[i],label=labels[i]) for i in labels]
        plt.legend(handles=patches, loc = 'best')

        output_fig_path = os.path.join(plot_output_dir, "aperture_plot-{}-{}.png".format(ref_star_id, timestamp))
        plt.savefig(output_fig_path)
        plt.close()