from collections import Counter
import math
import numpy as np
import pandas as pd
import scipy as scp
from statistics import mean
import os

#for cosmic ray removal
import astroscrappy

import astropy
import astropy.units as u
from astropy.coordinates import match_coordinates_sky, SkyCoord
from astropy.io import fits
from astropy.visualization import SqrtStretch, astropy_mpl_style
from astropy.visualization.mpl_normalize import ImageNormalize
from astropy.visualization.wcsaxes import SphericalCircle
from astropy.wcs import WCS
from astropy.wcs.utils import fit_wcs_from_points

#for centroiding
from astropy.convolution import convolve
from astropy.convolution.kernels import Model2DKernel
from astropy.modeling.models import Box2D
from photutils.centroids import centroid_sources, centroid_com
from photutils.detection import find_peaks

from photutils.aperture import CircularAperture, SkyCircularAperture
import matplotlib.pyplot as plt
from matplotlib import colors

from multiprocessing import Pool
from functools import partial
import logging
from pydriftn.Utils import ImageImporter, append_to_fits_header, get_bbox_coords_from_centre_coords
import sys


file_handler = logging.FileHandler("logfile.log")
console_handler = logging.StreamHandler()
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


class DriftAstrometry():
    '''
    This object class finds and matches drift centroids in a VR image
    to the input catalogue(s) and updates the VR image with new WCS.

    Parameters
    ----------
    driftscan_image_path: str
        Local path to VR FITS file.
    photometry_catalogue: str
        Local path to photometry_catalogue.csv.
    ccd_names: list
        A list of all CCD names to be included in the catalogue.
    track_rate: float
        Given in arcseconds per second. 
        Defaults to the formal DECam tracking rate of 0.5"/sec.
        (Default: 0.5)
    anchor: str
        A string to represent the anchor location (x,y).
        For now, this is a linear shift in y: 
        'r' is a leftways move to +y_offset,
        'l' is a rightways move to -y_offset,
        'm' is midway, and keeps the anchor at the centroid location.
        (Default: 'm')
    cosmicray_mask_path: str
        Local path to cosmic ray mask FITS file.
        (Default: ``None``)
    n_brightest_drifts: int
        The number of sources to search for.
        From decreasing brightness the first n_brightest_drifts will be returned.
        (Default: ``None``)
    perform_cosmicray_removal: boolean
        Option to perform cosmic ray removal at the beginning of the pipeline.
        (Default: False)
    '''

    def __init__(self, driftscan_image_path, photometry_catalogue, ccd_names, track_rate=0.5,
                 anchor='m', cosmicray_mask_path=None, n_brightest_drifts=None, perform_cosmicray_removal=False):
        '''
        Initialises DriftAstrometry with driftscan_image, photometry_catalogue, ccd_names,
        track_rate, anchor, cosmicray_mask_path, n_brightest_drifts, perform_cosmicray_removal.
        '''
        ccd_names = [ccd_names] if isinstance(ccd_names, str) else ccd_names
        
        self.driftscan_image = driftscan_image_path
        self.cr_mask_image = cosmicray_mask_path
        self.photometry_catalogue = pd.read_csv(photometry_catalogue)
        self.ccd_names = ccd_names

        self.track_rate = track_rate
        self.anchor = anchor
        self.n_brightest_drifts = n_brightest_drifts
        self.perform_cosmicray_removal = perform_cosmicray_removal

        self.image_basename = os.path.splitext(os.path.basename(driftscan_image_path))[0].replace('.fits','')


    @staticmethod
    def make_odd(val):
        '''
        A simple static function that ensures an integer is odd.
        If value is not odd, add 1 to make it odd.

        Parameters
        ----------
        val: float or int
            The input value.

        Returns
        -------
        odd_value: int
            The output odd integer.
        '''
        try:
            i = int(val)
        except ValueError:
            logging.error('Invalid input value.')

        if i%2 == 0:
            odd_value = i + 1
        else:
            odd_value = i

        return odd_value


    def import_image(self, filepath, ccd_name):
        '''
        Imports a fits image and transforms into WCS.

        Parameters
        ----------
        filepath: str
            Local path to the FITS file.
        ccd_name: str
            The name of the ccd image extension in the fits file.

        Returns
        -------
        fits_header: ``astropy.io.fits.header.Header`` class object.
        ccd_data: float ``numpy.ndarray`` of the image.
        ccd_header: FITS header class.
        wcs_fits: ``astropy.wcs.WCS`` class object.
        cr_mask: boolean ``numpy.ndarray``
            The cosmic ray mask (boolean) array with values of True where there are cosmic ray detections.
        clean_data: float ``numpy.ndarray``
            The cleaned data array after the cosmic ray removal.
        '''

        Image = ImageImporter(filepath)

        fits_header = Image.get_fits_header()
        ccd_header, ccd_data = Image.get_fits_image(ccd_name)
        wcs_fits = Image.wcs_transform(ccd_header)
        pixscale = Image.get_pixscale(fits_header)
        background = Image.get_background(ccd_header, ccd_data)
        
        if self.perform_cosmicray_removal:
            cr_mask, clean_data = Image.cosmicray_removal(ccd_hdr=ccd_header, ccd_data=ccd_data)
            # TODO: save
        else:
            cr_mask = clean_data = None

        return fits_header, ccd_data, ccd_header, background, wcs_fits, cr_mask, clean_data, pixscale


    def drift_width(self, fwhm_estimate, unit='pixel', pixelscale=0.27):
        '''
        Estimates the width of a star.

        Parameters
        ----------
        fwhm_estimate: float
            The input estimated width of the star.
        unit: str
            The unit of measurement for the fwhm_estimate.
            If the fwhm_estimate is in arcsec, it will be converted into pixel.
            (Default: pixel)
        pixelscale: float
            The pixelscale of the image.
            (Default: 0.27)

        Returns
        -------
        fwhm_estimate: float
            The estimated width of the star, in pixels.
        '''
        #Estimate width of star (here we use Noirlab Community pipeline FITs headers in this function call)
        if unit == 'arcsec':
            fwhm_estimate = fwhm_estimate * pixelscale

        return fwhm_estimate


    def drift_length(self, track_rate, exp_time, unit='arcsec', pixelscale=0.27):
        '''
        Calculates the drift length from the given tracking rate, exposure duration and pixelscale.

        Parameters
        ----------
        track_rate: float
            Given in arcseconds per second. 
            Defaults to the formal DECam tracking rate of 0.5"/sec.
            (Default: 0.5)
        exp_time: int
            The exposure duration of the image.
        unit: str
            The unit of measurement for the track rate.
            (Default: arcsec)
        pixelscale: float
            The pixelscale of the image.
            (Default: 0.27)

        Returns
        -------
        length: float
            The drift length in pixels.
        '''
        #calculates drift length given user defined tracking rate, and FITs header cards for the
        #exposure duration and pixelscale
        #NOTE: rate is given in arcsec/second ---> exp_time must be in seconds

        if unit == 'arcsec':
            length = track_rate * exp_time / pixelscale

        if unit == 'pixel':
            length = track_rate * exp_time

        return length


    def drift_model(self, a, b, unit='pixel', pixelscale=0.27):
        '''
        Defines a Box2D model that makes a theoretical model drift.

        Parameters
        ----------
        a: float
            The width in y direction of the box.
        b: float
            The width in x direction of the box.
        unit: str
            The unit of measurement for the widths.
            (Default: pixel)
        pixelscale: float
            The pixelscale of the image.
            (Default: 0.27)

        Returns
        -------
        model: ``astropy.modeling.functional_models.Box2D`` class object.
        '''
        #define a Box2D model that makes a theoretical model drift given drift rate, exposure time
        #or width, length depending on unit

        #unit are pixel or 'arcsec'
        # TODO: confirm below changes
        # 2025 update: changed * into /
        if unit == 'arcsec':
            a = a / pixelscale
            b = b / pixelscale

        model = Box2D(x_0=0, x_width=b, y_0=0, y_width=a)
        return model


    def drift_centroids(self, ccd_data, background, wcs_fits, model):
        '''
        Finds centroids of the drifts in an image.

        Parameters
        ----------
        ccd_data: float ``numpy.ndarray`` of the image.
            The drifted VR image.
        background: float or array_like
            The image background or a defined threshold level to search for flux peaks.
            Below background values, no peaks will be defined (i.e for faint drifts).
        wcs_fits: ``astropy.wcs.WCS`` class object.
            The original WCS of the image.
        model: ``astropy.modeling.functional_models.Box2D`` class object.
            A simplistic model of the typical driftscan (2D rectangle of constant flux).

        Returns
        -------
        drift_map: ``astropy.table.Table`` class object
            A table containing the x and y pixel location of the peaks and their values
        '''

        shape = DriftAstrometry.make_odd(model.x_width.value), DriftAstrometry.make_odd(model.y_width.value) #must be integer values for kernel
        drift_kernel = Model2DKernel(model, x_size=int(shape[0]*2 - 1)) #what does xsize do?

        drift_conv = convolve(ccd_data, drift_kernel)

        if self.n_brightest_drifts:
            drift_map = find_peaks(drift_conv, background, box_size=20, npeaks=self.n_brightest_drifts, wcs=wcs_fits)
        else:
            drift_map = find_peaks(drift_conv, background, box_size=20, wcs=wcs_fits)

        x_peaks = drift_map['x_peak']
        y_peaks = drift_map['y_peak']

        x, y = centroid_sources(ccd_data, x_peaks, y_peaks, box_size=shape, centroid_func=centroid_com)

        drift_map['x_cent'] = x
        drift_map['y_cent'] = y

        skycoord = wcs_fits.pixel_to_world(drift_map['x_cent'], drift_map['y_cent'])
        drift_map['ra_cent'] = [i.ra.deg for i in skycoord]
        drift_map['dec_cent'] = [i.dec.deg for i in skycoord]

        return drift_map


    def project_centroids(self, centroid_table, wcs_fits, anchor, model, ccd_name, pixelscale):
        '''
        Take a centroided drift position and shift it left or right to the start of end of the drift, or keep it
        at the midpoint of the drift.

        This function anchors the drift ra, dec to a specific point along the drift.
        The exposure starts with specific coordinates of the field, and our specific tracking rate in
        declination (along the y-axis) builds the trail of the drift. Technically the WCS is built from the
        initial starting image of the start at exp_time = 0 at position (x, y) = (0,0),
        and at exp_time = 20 seconds, the star is elsewhere on the detector image (+0, +40) pixels.

        Our positions in the WCS shift should be measured with respect to the star position at the beginning
        of the exposure.

        The opposite anchor point ('r') would be equivalent to a reversed tracking rate of -0.5 arcsecs/sec in dec.
        I've included this point as a input in case other drift datasets have different tracking directions.

        Eventually this could become more sophisticated, where the user has tracking_vector = (0.5, 0.1) in (ra, dec)
        and the projection would work out the relevant x and y anchor points for the starting location of the source.

        Parameters
        ----------
        centroid_table: ``pandas.DataFrame``
            A table of the centroid locations of driftscans.
        wcs_fits: ``astropy.wcs.WCS`` class object.
            The original WCS of the image.
        anchor: str
            A string to represent the anchor location (x,y).
            For now, this is a linear shift in y:
            'r' is a leftways move to +y_offset,
            'l' is a rightways move to -y_offset,
            'm' is midway, and keeps the anchor at the centroid location.
        model: ``astropy.modeling.functional_models.Box2D`` class object.
            An astropy 2D rectangular model of the driftscan.
        ccd_name: str
            The name of the ccd image extension in the FITS file.
        pixelscale: float
            The pixelscale of the image.
            (Default: 0.27)

        Returns
        -------
        centroid_table: ``pandas.DataFrame`` 
            The updated table of the centroid locations of driftscans.
        '''
        
        #from the centroid locations, plop down a centroided model and use a specific x,y pixel as the anchor
        #for all drifts. i.e 'l' = left, 'r' = right, 'm' = middle/centroid....

        half_y = model.y_width.value/2
        anchor_x = 0  #no linear shift to centroid midline position

        if anchor == 'r':
            anchor_y = -half_y  #no linear shift to centroid midline position
        elif anchor == 'l':
            anchor_y = half_y
        elif anchor == 'm':
            anchor_y = 0
        else:
            logger.warning("Invalid anchor input value: {}. Options: 'r', 'l', or 'm'.".format(anchor))
            anchor_y = 0
            logger.info('Keeping the anchor at the centroid location.')

        centroid_table['x_a'] = centroid_table['x_cent'] + anchor_x
        centroid_table['y_a'] = centroid_table['y_cent'] + anchor_y

        skycoord = wcs_fits.pixel_to_world(centroid_table['x_cent'], centroid_table['y_cent'])
        centroid_table['ra_a'] = [i.ra.deg for i in skycoord]
        centroid_table['dec_a'] = [i.dec.deg for i in skycoord]
        centroid_table['centroid_ID'] = [ccd_name + '-centroid-' + str(i) for i in range(len(skycoord))]
        
        # --------------------------------------------------------------------
        # new edit April 2025: cluster removals
        match, sep, d3sep = match_coordinates_sky(skycoord, skycoord, nthneighbor = 2)
        sep_arcsec = sep.arcsecond*u.arcsecond
        sep_pix = sep_arcsec.value * pixelscale # where pixel_scale for DECam is 0.27''/pix
        centroid_table['neighbour'] = match
        centroid_table['pix_sep'] = sep_pix
        separation = 0.5 #let's leave this as a global parameter for now in the function
        centroid_table = centroid_table[centroid_table['pix_sep'] >= separation] #removes all 'peak' within clusters
        # --------------------------------------------------------------------
        
        centroid_table['chp'] = ccd_name

        return centroid_table


    def match_drift_ref(self, ref_cat_pos, centroid_pos, wcs_fits):
        '''
        Matches ra and dec positions on sky between the reference stars and the drifts.

        Parameters
        ----------
        ref_cat_pos: ``Pandas.DataFrame``
            The photometry catalogue.
        centroid_pos: ``pandas.DataFrame`` 
            The table of the centroid locations of driftscans.
        wcs_fits: ``astropy.wcs.WCS`` class object.
            The original WCS of the image.

        Returns
        -------
        w_SHIFT: ``astropy.wcs.WCS`` class object.
            The new WCS.
        matched_ref_x: list
            An ordered list of the x-coordinates from the reference catalogue
            that are matched to the centroid positions.
        matched_ref_y: list
            An ordered list of the y-coordinates from the reference catalogue
            that are matched to the centroid positions.
        star_ids: list
            An ordered list of the reference star IDs that are matched to the centroid positions.

        '''

        #match between ra and dec positions on sky between the reference stars and the drifts
        #Noted (20th Feb 2024) that this function is slow, and we could speed up using Stilts

        ref_coords = SkyCoord(ref_cat_pos['ra'].tolist()*u.deg, ref_cat_pos['dec'].tolist()*u.deg, frame='fk5')
        drift_coords = SkyCoord(centroid_pos['skycoord_peak.ra'].tolist()*u.deg, centroid_pos['skycoord_peak.dec'].tolist()*u.deg, frame='fk5')

        idx, d2d, d3d = drift_coords.match_to_catalog_sky(ref_coords)

        matched_refs = ref_coords[idx]

        #apply linear shift (Renee to test on Thursday/Friday)
        ref_pixel = wcs_fits.world_to_pixel(ref_coords)

        '''
        xshift = ref_pixel[0] - centroid_pos['x_a']
        yshift = ref_pixel[1] - centroid_pos['y_a']

        drift_xy = centroid_pos['x_a'] + xshift, centroid_pos['y_a'] + yshift
        '''

        matched_ref_x = [ref_pixel[0][i] for i in idx]
        matched_ref_y = [ref_pixel[1][i] for i in idx]
        star_ids = ref_cat_pos.iloc[idx]['ref_star_id'].tolist()

        xshift = [a - b for a, b in zip(matched_ref_x, centroid_pos['x_a'].tolist())]
        yshift = [a - b for a, b in zip(matched_ref_y, centroid_pos['y_a'].tolist())]
        
        # --------------------------------------------------------------------
        # new edit April 2025
        xcounts, xbins = np.histogram(xshift, bins = len(xshift)//100 * 100)
        ycounts, ybins = np.histogram(yshift, bins = len(yshift)//100 * 100)
        xind = np.where(xcounts == xcounts.max())[0][0]
        yind = np.where(ycounts == ycounts.max())[0][0]
        xs = xbins[xind]
        ys = ybins[yind]
        drift_xy = np.array([[x + xs for x in centroid_pos['x_a']], [y + ys for y in centroid_pos['y_a']]])
        # --------------------------------------------------------------------

        #take the matched drift x and y positions to the reference star skycoordinates in g, r images
        w_SHIFT = fit_wcs_from_points(xy=drift_xy, world_coords=matched_refs, projection='TAN')

        return w_SHIFT, matched_ref_x, matched_ref_y, star_ids


    def check_whether_cosmicray_affected(self, crmask_data, centroids_df, img_dim=(4094, 2046), drift_dim=(11, 51)):
        '''
        Reads in cosmic ray mask, iterates through the centroids table to check whether the driftscan
        is affected by cosmic ray.
        Default shape of the driftscan = 11*51 pixels (h*w).

        Parameters
        ----------
        crmask_data: ``numpy.ndarray``
            The cosmic ray mask (boolean) array with values of True where there are cosmic ray detections.
        centroids_df: ``pandas.DataFrame`` 
            The table of the centroid locations of driftscans.
        img_dim: tuple
            The (height, width) of the image.
            (Default: (4094, 2046))
        drift_dim: tuple
            The estimated and fixed (height, width) of the driftscan.
            (Default: (11,51))

        Returns
        -------
        centroids_df: ``pandas.DataFrame``
            The centroids table, updated with boolean information of whether the driftscan was affected by cosmic ray.
        '''
        # TODO: add sum functionality: potentially np.count_nonzero

        for index, row in centroids_df.iterrows():
            x1, x2, y1, y2 = get_bbox_coords_from_centre_coords(row['x_cent'], row['y_cent'], drift_dim, img_dim)
            centroid = crmask_data[y1:y2, x1:x2]

            if np.any(centroid):
                centroids_df.loc[index, 'cosmic_ray_affected'] = 1

                '''chp = row['chp']
                plt.style.use(astropy_mpl_style)
                plt.figure()
                plt.imshow(centroid, origin='lower')
                plt.savefig('{}-{}x-{}y.png'.format(chp, x1, y1))'''

            else: 
                centroids_df.loc[index, 'cosmic_ray_affected'] = 0

        return centroids_df


    def update_image_wcs(self, ccd_name):
        '''
        Updates an image header with new WCS and creates a table of drift centroids and matched reference stars.

        Parameters
        ----------
        ccd_name: str
            The name of the ccd image extension in the FITS file.
        fwhm_estimate: float
            The input estimated width of the star.

        Returns
        -------
        drift_map_df: ``pandas.DataFrame`` 
            The table of the centroid locations of driftscans.
        '''
        crmask = None
        cleanarr = None
        fits_header, ccd_data, ccd_header, background, wcs_fits, crmask, cleanarr, pixscale = self.import_image(self.driftscan_image, ccd_name)

        # Get image dimension for cosmicray mask checking
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

        img_dim = (img_h, img_w)

        if cleanarr is None:
            # no cosmic ray removal performed
            data = ccd_data
            if self.cr_mask_image:
                crmask_fits = fits.open(self.cr_mask_image)
                crmask = crmask_fits[ccd_name].data
        else:
            # if cosmicray removal was just performed.
            #print(cleanarr)
            data = cleanarr

	# Get FWHM and exposure time info from headers.
        try:
            fwhm_estimate = ccd_header['FWHM']
        except KeyError as k:
            logger.warning('No FWHM info in FITs header. Please check the keyword.')
            fwhm_estimate = 7
            logger.info('Using 7 as the default FWHM value.')

        drift_w = self.drift_width(fwhm_estimate, 'pixel', pixscale)

        try:
            exp_time = fits_header['EXPTIME']
        except KeyError as k:
            logger.warning('No EXPTIME info in FITs header. Please check the keyword.')
            exp_time = 20
            logger.info('Using 20 (seconds) as the default exposure time.')

        drift_l = self.drift_length(self.track_rate, exp_time, 'arcsec', pixscale)

        # drift_w should be something around 5
        # drift_l should be something around 40
        model = self.drift_model(drift_w, drift_l)

        # Get drift centroids
        drift_map_table = self.drift_centroids(ccd_data, background, wcs_fits, model)

        drift_map_df = drift_map_table.to_pandas()
        drift_map_df = self.project_centroids(drift_map_df, wcs_fits, self.anchor, model, ccd_name, pixscale)

        # Match found centroids to the photometry catalouge
        photometry_cat_subset = self.photometry_catalogue[self.photometry_catalogue['chp'] == ccd_name]
        if photometry_cat_subset.empty:
            logger.fatal('No CCD #{} in the input photometry catalogue. Please check inputs.'.format(ccd_name))
            return None

        # TODO: write new_wcs to header
        new_wcs, matched_ref_x, matched_ref_y, star_ids = self.match_drift_ref(photometry_cat_subset, drift_map_df, wcs_fits)
        drift_map_df['catalogue_reference_x'] = matched_ref_x
        drift_map_df['catalogue_reference_y'] = matched_ref_y
        drift_map_df['ref_star_id'] = star_ids

        if crmask is not None:
            drift_map_df = self.check_whether_cosmicray_affected(crmask, drift_map_df, img_dim)

        return drift_map_df


    def update_whole_image(self):
        '''
        Updates the headers of all of the specified CCDs with new WCS and
        compiles drift centroids and the matched reference stars for all specified CCDs in the VR/driftscan image.

        Returns
        -------
        centroids_df: ``Pandas.DataFrame``
            A Pandas dataframe of all drift centroids found and matched with the reference stars.
        '''

        # TODO: something we could do
        # Use the FWHM from the centre of the image (CCD S4) for more consistency
        # Image = ImageImporter("S4", self.driftscan_image)

        # ccd_header, ccd_data = Image.get_fits_image()

        # try:
        #     fwhm_estimate = ccd_header['FWHM']
        # except KeyError as k:
        #     logger.warning('No FWHM info in FITs header. Please check the keyword.')
        #     fwhm_estimate = 7
        #     logger.info('Using 7 as the default FWHM value.')

        with Pool() as p:
            # TODO: update if we want to use FWHM from the centre of the image
            #update_image_wcs_fwhm = partial(self.update_image_wcs, fwhm_estimate=fwhm_estimate)
            centroids = p.map(self.update_image_wcs, self.ccd_names)
            
        if all(c is None for c in centroids):
            logger.warning('No centroids table generated. Please check input image, catalogues and CCD names. Quitting program...')
            sys.exit()

        centroids_df = pd.concat(centroids)

        return centroids_df

