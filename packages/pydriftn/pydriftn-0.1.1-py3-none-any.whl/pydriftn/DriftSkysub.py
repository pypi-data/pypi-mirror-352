from astropy.io import fits
import datetime
from astropy.nddata.utils import Cutout2D
from astropy.stats import sigma_clip
import numpy as np
import pandas as pd
from photutils.aperture import CircularAperture, RectangularAperture
from skimage.draw import circle_perimeter, rectangle_perimeter
import os

#plots
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, ListedColormap
import matplotlib.patches as mpatches
import cmasher as cm

from Utils import ImageImporter

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
    output_path: str
        Path to desired output directory.
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
    plot_stars: boolean (default = True)
        If True, creates an imshow figure of the cutout of the star with inner and outer stadium apertures.
        Plot is saved to the working directory.
        If False, no plots are made.
    verbose_save: int (default = 0)
        Defines the amount of annulus information saved to working directory.
        0: no information saved, function returns as normal.
        1: the data within the annulus is saved.
        2: both the mask and data of the annulus is saved #check if I want to project this to chip_data x,y coordinates.    
    
    '''

    def __init__(self, driftscan_image_path, centroids_positions, ccd_names, output_path,
                cutout_size=100, length=40, radius=7, pad=5, plot_star=True, verbose_save=0):
        '''
        Initialises SkyFinder with driftscan_image_path, centroids_positions, ccd_names, 
        output_path, cutout_size, length, radius, pad, plot_star, verbose_save.

        '''
        ccd_names = [ccd_names] if isinstance(ccd_names, str) else ccd_names
        
        self.driftscan_image = driftscan_image_path
        self.centroids_positions = pd.read_csv(centroids_positions)
        self.ccd_names = ccd_names

        self.cutout_size = cutout_size
        self.length = length
        self.radius = radius
        self.pad = pad
        self.plot_star = plot_star
        self.verbose_save = verbose_save

        self.output_path = output_path
        if not os.path.exists(output_path):
            os.mkdir(output_path)
    
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
        
        Image = ImageImporter(ccd_name, filepath)

        fits_header = Image.get_fits_header()
        ccd_header, ccd_data = Image.get_fits_image()

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


    def stadium_perimeter(self, ccd_name, cutout_data, x0, y0, length, radius, pad=0):
        '''
        This function uses combinations of scikit.draw perimeter objects to draw the contours of a stadium apeture
        Note that the apeture is 'jagged', it traces whole pixels; a direct result of ndarray indexing.
        NOTE: This function is only used for plotting apetures, since some pixel conventions differ from Photutils.
        Potential: there may be a smart way of joining the stadium across fractions of pixels to form a precise apeture.
        
        Parameters
        ----------
        ccd_name: str
            The name of the ccd image extension in the fits file.
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
        pad: int
            The number of pixels within the annulus,
            projected around the perimeter of the inner stadium aperture.
        '''
        plot_output_dir = os.path.join(self.output_path, 'aperture_plots')
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
            contour[rlhs, clhs] = 1
            contour[rrhs, crhs] = 1
            contour[rRect, cRect] = 1

            #hollow out the inside of the apeture to avoid plotting intersections and cross-hairs
            contour[end[0]:start[0]+1, start[1]-1:end[1]+2] = 0

        except:
            logger.warning('DSI located near to image boundary. Plot_star method returning None.') 

        else:           
            plt.imshow(cutout_data, norm = LogNorm(), cmap = drift_cmap) # plot 1   
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

            output_fig_path = os.path.join(plot_output_dir, "aperture_plot-{}-{}.png".format(ccd_name, timestamp))
            plt.savefig(output_fig_path)
            plt.close()

            
    def stadium_annulus(self, ccd_name, ccd_data, x0, y0, cutout_size, length, 
                        radius, pad, plot_star=True, verbose_save=0):           
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
        plot_star: boolean (default = True)
            If True, creates an imshow figure of the cutout of the star with inner and outer stadium apertures.
            Plot is saved to the working directory.
            If False, no plots are made.  
        verbose_save: int (default = 0)
            Defines the amount of annulus information saved to working directory.
            0: no information saved, function returns as normal.
            1: the data within the annulus is saved.
            2: both the mask and data of the annulus is saved #check if I want to project this to chip_data x,y coordinates.

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

        #verbose saves and plots
        if plot_star:
            self.stadium_perimeter(ccd_name, cutout.data, xi, yi, length, radius, pad=pad)
        
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

        Parameter
        ---------
        ccd_name: str
            The name of the ccd image extension in the fits file.

        Returns
        -------
        centroids_subset: `pandas.DataFrame``
            A table of the centroid locations of driftscans, appended with the median sky values.
        '''
        #TO ADD: DriftAstrom.py builds a dataframe of x0, y0 positions and the sky function is processed as lambda:row()
        #df['sky'] = df.apply(lambda row: stadium_annulus(full_data, row['x0'], row['y0'], cutout_size, length, radius, pad), axis = 1)
        fits_header, ccd_data, ccd_header = self.import_image(self.driftscan_image, ccd_name)

        centroids_subset = self.centroids_positions[self.centroids_positions['chp'] == ccd_name]

        # Calculate sky median for each star, update dataframe.
        for index, row in centroids_subset.iterrows():
            sky = self.stadium_annulus(ccd_name, ccd_data, row['x_cent'], row['y_cent'], self.cutout_size, self.length, self.radius, self.pad)
            sky_nan = np.where(sky == 0.0, np.nan, sky)
            sky_median = np.nanmedian(sky_nan)
            centroids_subset.loc[index, 'sky'] = sky_median

        return centroids_subset


    def update_whole_table_with_sky_values(self):
        '''
        Updates the whole centroids table with the median sky values. 

        Returns
        -------
        centroids_df_with_sky: ``Pandas.DataFrame``
            A Pandas dataframe of all drift centroids and their median sky values.
        '''
        with Pool() as p:
            updated_dfs = p.map(self.calculate_local_sky, self.ccd_names)
            centroids_df_with_sky = pd.concat(updated_dfs)

        output_csv_path = os.path.join(self.output_path, 'centroids_with_sky_values.csv')
        centroids_df_with_sky.to_csv(output_csv_path, index=False)

        return centroids_df_with_sky
