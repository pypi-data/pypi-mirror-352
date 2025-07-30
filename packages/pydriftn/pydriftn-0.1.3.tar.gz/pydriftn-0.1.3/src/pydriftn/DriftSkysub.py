from astropy.io import fits
import datetime
from astropy.nddata.utils import Cutout2D
from astropy.stats import sigma_clip
import numpy as np
import pandas as pd
from photutils.aperture import CircularAperture, RectangularAperture
from skimage.draw import circle_perimeter, rectangle_perimeter
import os

from pydriftn.Utils import ImageImporter, get_bbox_coords_from_centre_coords

from multiprocessing import Pool
from functools import partial
import logging


file_handler = logging.FileHandler("logfile.log")
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

class SkyEstimator:
    '''
    This object class calculates the median sky background around drifts.

    Parameters
    ----------
    driftscan_image_path: str
        Local path to VR FITS file.
    centroids_positions: str
        The local path to the centroids.csv.
    ccd_names: list
        A list of all CCD names to be included in the catalogue.
    cutout_size: int
        The size of the cutout centered around the driftscan (in pixels).
        (Default: 100)
    length: int
        The driftscan length in the x-direction.
        (Default: 40)
    radius: int
        the radius of the semi-circular caps of the stadium shape,
        and half the width of the rectangular body in the y-direction.
        (Default: 7)
    pad: int
        The number of pixels within the annulus,
        projected around the perimeter of the inner stadium aperture.
        (Default: 5)
    verbose_save: int
        Defines the amount of annulus information saved to working directory.
        0: no information saved, function returns as normal.
        1: the data within the annulus is saved.
        2: both the mask and data of the annulus is saved #check if I want to project this to chip_data x,y coordinates.
        (Default = 0)
    
    '''

    def __init__(self, driftscan_image_path, centroids_positions, ccd_names,
                cutout_size=100, length=40, radius=7, pad=5, verbose_save=0):
        '''
        Initialises SkyFinder with driftscan_image_path, centroids_positions, ccd_names, 
        cutout_size, length, radius, pad, verbose_save.

        '''
        ccd_names = [ccd_names] if isinstance(ccd_names, str) else ccd_names
        
        self.driftscan_image = driftscan_image_path
        self.centroids_positions = pd.read_csv(centroids_positions) # path to centroids.csv.
        self.ccd_names = ccd_names

        self.cutout_size = cutout_size
        self.length = length
        self.radius = radius
        self.pad = pad
        self.verbose_save = verbose_save

        self.image_basename = os.path.splitext(os.path.basename(driftscan_image_path))[0].replace('.fits','')
        #x0 = 67 + 240 + 1500   #known centroids from the astrometry positioning
        #y0 = 21 + 410 + 1000
        #self.x0 = x0
        #self.y0 = y0
        

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
        '''
        
        Image = ImageImporter(filepath)

        fits_header = Image.get_fits_header()
        ccd_header, ccd_data = Image.get_fits_image(ccd_name)

        return fits_header, ccd_data, ccd_header


    def aperture_sum(self, apertures, data_shape):
        '''
        Function takes a list of apertures and calculates the image of the aperture onto an array of size data_shape.
        
        Parameters
        ----------
        apertures: list 
            A list of ``Photutils.Aperture`` objects.
        data_shape: tuple or list 
            The array shape as number of pixels (nx, ny).

        Returns
        -------
        combined_aperture: boolean ``numpy.ndarray``
            The combined aperture as a boolean mask.

        '''
        mask_sum = sum(aper.to_mask(method = 'center').to_image(data_shape) for aper in apertures)
        combined_aperture = np.where(mask_sum != 0, 1, mask_sum)
        return(combined_aperture)

            
    def stadium_annulus(self, ccd_name, ccd_data, x0, y0, cutout_size, length,
                        radius, pad, verbose_save=0):
        '''
        Function uses combinations of Photutils aperture objects to create a stadium annulus 
        and aperture for a driftscan.
        
        Parameters
        ----------
        ccd_name: str
            The name of the ccd image extension in the fits file.
        ccd_data: float ``numpy.ndarray``
            The full, relevant data array of the CCD chip.
            Passing a slice or subsection of the data may result in Cutout2D value errors. 
        x0: int
            x-coordinate of the centroid of a detected driftscan, scaled to the image cutout.
        y0: int
            y-coordinate of the centroid of a detected driftscan, scaled to the image cutout.
        cutout_size: int
            The size of the cutout centered around the driftscan (in pixels).
        length: int
            The driftscan length in the x-direction.
        radius: int
            the radius of the semi-circular caps of the stadium shape,
            and half the width of the rectangular body in the y-direction.
        pad: int
            The number of pixels within the annulus,
            projected around the perimeter of the inner stadium aperture.
        verbose_save: int
            Defines the amount of annulus information saved to working directory.
            0: no information saved, function returns as normal.
            1: the data within the annulus is saved.
            2: both the mask and data of the annulus is saved #check if I want to project this to chip_data x,y coordinates.
            (Default = 0)

        Returns
        -------
        clipped_sky: ``numpy.ndarray`` MaskedArray
            Sigma clipped annulus data.

        '''
        #make a cutout2D object of the drift around x0, y0
        cutout = Cutout2D(ccd_data, (x0,y0), cutout_size)
        xi, yi = cutout.to_cutout_position((x0, y0))
        
        aperRect = RectangularAperture((xi, yi), w = length, h = radius*2)
        aperCirc_LHS = CircularAperture((xi - length//2, yi), radius)
        aperCirc_RHS = CircularAperture((xi + length//2, yi), radius)

        inner_aperture = self.aperture_sum([aperRect, aperCirc_LHS, aperCirc_RHS], cutout.shape)

        #Make an annulus using the same method but concentric circles
        annuRect = RectangularAperture((xi, yi), w = length + pad, h = (radius+pad)*2)
        annuCirc_LHS = CircularAperture((xi - length//2, yi), radius+pad)
        annuCirc_RHS = CircularAperture((xi + length//2, yi), radius+pad)

        outer_aperture = self.aperture_sum([annuRect, annuCirc_LHS, annuCirc_RHS], cutout.shape)
        annulus_mask = outer_aperture - inner_aperture
        annulus_data = cutout.data*annulus_mask
        
        #calculate the sky within the annulus with sigma_clipping to avoid blended pixels
        clipped_sky = sigma_clip(annulus_data, sigma=2, maxiters=10).data
        
        dsi_ID = 0 # TODO
        if verbose_save == 0:
            pass
        if verbose_save == 1:
            #save annulus data as an array
            np.save(f'annulus_data_{dsi_ID}.npy', annulus_data)
        if verbose_save == 2:
            #save annulus data and annulus mask as arrays
            np.save(f'annulus_eval_{dsi_ID}.npy', [annulus_data, annulus_mask])

        return clipped_sky


    def calculate_local_sky(self, ccd_name):
        '''
        Calculates median of the sky around the driftscan.

        Parameters
        ----------
        ccd_name: str
            The name of the ccd image extension in the fits file.

        Returns
        -------
        centroids_subset: `pandas.DataFrame``
            A table of median sky values for the driftscans.
        '''
        #TO ADD: DriftAstrom.py builds a dataframe of x0, y0 positions and the sky function is processed as lambda:row()
        #df['sky'] = df.apply(lambda row: stadium_annulus(full_data, row['x0'], row['y0'], cutout_size, length, radius, pad), axis = 1)
        fits_header, ccd_data, ccd_header = self.import_image(self.driftscan_image, ccd_name)

        df_columns = ['centroid_ID', 'sky']
        sky_df = pd.DataFrame(columns=df_columns)
        centroids_subset = self.centroids_positions[self.centroids_positions['chp'] == ccd_name]

        # Calculate sky median for each star, update dataframe.
        for index, row in centroids_subset.iterrows():
            sky = self.stadium_annulus(ccd_name, ccd_data, row['x_cent'], row['y_cent'], self.cutout_size, self.length, self.radius, self.pad)
            sky_nan = np.where(sky == 0.0, np.nan, sky)
            sky_median = np.nanmedian(sky_nan)
            sky_df.loc[index] = [row['centroid_ID'], sky_median]

        return sky_df


    def update_whole_table_with_sky_values(self):
        '''
        Updates the whole centroids table with the median sky values. 

        Returns
        -------
        centroids_df_with_sky: ``Pandas.DataFrame``
            A Pandas dataframe of all drift centroids and their median sky values.
        '''
        with Pool() as p:
            skies = p.map(self.calculate_local_sky, self.ccd_names)
            sky_df = pd.concat(skies)

        centroids_df_with_sky = self.centroids_positions.merge(sky_df, how='left', on='centroid_ID')

        return centroids_df_with_sky

