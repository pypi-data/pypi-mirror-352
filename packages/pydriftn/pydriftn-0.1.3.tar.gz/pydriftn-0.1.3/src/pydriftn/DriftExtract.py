import numpy as np
import pandas as pd
from astropy.io import fits
import matplotlib.pyplot as plt
from astropy.nddata.utils import Cutout2D
import scipy.stats
from scipy.optimize import curve_fit, OptimizeWarning
from scipy.stats import norm
import os
import logging
import warnings
from pydriftn.Utils import ImageImporter, get_bbox_coords_from_centre_coords, stadium_perimeter

from multiprocessing import Pool
from functools import partial

file_handler = logging.FileHandler("logfile.log")
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


class TimeSeriesGenerator:
    '''
    This object class extracts drift time series from individual driftscans for each star.

    Parameters
    ----------
    driftscan_image_path: str
        Local path to VR FITS file.
    centroids_positions: str
        Local path to centroids_with_sky_values.csv.
    target_ids: list
        List of centroid IDs of interest.
    ccd_names: list
        A list of all CCD names to be included in the catalogue.
    output_path: str
        Path to desired output directory to save aperture plots.
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

    '''
    def __init__(self, driftscan_image_path, centroids_positions, target_ids, ccd_names, output_path, cutout_size=100, length=40, radius=7, pad=5):
        '''
        Initialises TimeSeriesGenerator with ccd names and local file paths of the driftscan image, photometry catalogue and bias files.
        '''
        ccd_names = [ccd_names] if isinstance(ccd_names, str) else ccd_names

        self.driftscan_image = driftscan_image_path 
        self.centroids_positions = pd.read_csv(centroids_positions) # path to centroids.csv.
        self.ccd_names = ccd_names
        self.cutout_size = cutout_size
        self.length = length
        self.radius = radius
        self.pad = pad
        # fit to flat part of DSI: x = 10:41 incl : 32 pixels
        self.flat_part_start = 10
        self.flat_part_end = 41
        self.flat_part_len = 1 + self.flat_part_end - self.flat_part_start

        self.output_path = output_path
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        self.image_basename = os.path.splitext(os.path.basename(driftscan_image_path))[0].replace('.fits','')

        self.target_ids = target_ids


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


    @staticmethod
    def L3(y, LF, SF, MF):
        '''
        The model function.

        Parameters
        ----------
        y: float
            The coordinate.
        LF: float
            The intensity of the drift.
        SF: float
            The spread of the drift.
        MF: float
            The centre of the drift.

        Returns
        -------
        P: float
            The product of the L3 function.
        '''
        # ignore background for a start
        N = 2.75
        P = LF*np.sign(SF)*pow(np.abs(SF),N) / (pow(np.abs(y-MF),N) + np.sign(SF)*pow(np.abs(SF),N))
        
        return P


    def subtract_sky_from_stars(self, ccd_data, ccd_name):
        '''
        Subtracts the median sky value saved in the centroids dataframe
        from the cropped driftscan bounding box.

        Parameters
        ----------
        ccd_data: float ``numpy.ndarray`` of the image.
        ccd_name: str
            The name of the ccd image extension in the fits file.

        Returns
        -------
        subtracted_stars: list
            A list of float ``numpy.ndarray`` s of the subtracted stars.
        stars_df: ``Pandas.DataFrame``
            Table of the centroids without duplicating reference stars.
        target_stars_idxs: list
            A list of indexes in the subtracted_stars of the target stars.

        '''

        # read table of centroids with sky values,
        # create a slice for the current ccd
        centroids_subset = self.centroids_positions[self.centroids_positions['chp'] == ccd_name]
        
        # drop duplicating reference stars
        # TODO: bring this back in when we are ready to implement catalogue matching
        #unique_stars = centroids_subset.drop_duplicates(subset=['catalogue_reference_x', 'catalogue_reference_y'], keep='first').reset_index(drop=True)
        
        star_shape = (11,51) # (height, width)

        subtracted_stars = []
        target_stars_idxs = []
        unusable_stars = []
        star_idx = 0
        for index, row in centroids_subset.iterrows():
            x1, x2, y1, y2 = get_bbox_coords_from_centre_coords(row['x_cent'], row['y_cent'], star_shape, ccd_data.shape)
            print(x1,x2,y1,y2)
            star = ccd_data[y1:y2, x1:x2]
            if star.shape == (11,51):
                star -= row['sky']
                subtracted_stars.append(star)
                if row['centroid_ID'] in self.target_ids:
                    target_stars_idxs.append(star_idx)
                
                # the index in stars_df
                star_idx += 1
            else:
                # discard cropped drift scans
                unusable_stars.append(index)

        stars_df = centroids_subset.drop(unusable_stars)
        stars_df = stars_df.reset_index(drop=True)

        return subtracted_stars, stars_df, target_stars_idxs


    def perform_l3_fitting_one_star(self, star_index, star):
        '''
        Fits L3 function to one star.

        Parameters
        ----------
        star_index: int
            Index of the star in the stars array.
        star: 2D array
            A Numpy 2D array of the subtracted star.
        
        Returns
        -------
        (star_index, popts, perrs)
            Tuple of: index of the star, array of optimal values from the curve fit function, and array of curve fit error values.
        '''
        maximums = star.max(axis=0)
        col_index = 0
        y = np.arange(11)
        popts = []
        perrs = []
        for i in range(self.flat_part_start, self.flat_part_end+1):
            p0 = [maximums[i], 2., 3.5]

            try:
                popt1, pcov1 = curve_fit(self.L3, y, star[:,i], p0)
            except RuntimeError:
                logger.warning('Continuing after RTE at star #{}, column #{}'.format(star_index, col_index))
                continue
            else:
                perr = np.sqrt(np.diag(pcov1))
                popts[col_index] = popt1
                perrs[col_index] = perr

            col_index += 1
        return (star_index, popts, perrs)
    
    
    def get_star_correlations(self, star_idxs, normalised_drift):
        '''
        Function to get the pearson correlation coefficient of two stars.

        Parameters
        ----------
        star_idxs: list
            List of len == 2 of the star indexes.
        normalised_drift: 3D array
            List of Numpy 2D arrays of the 2 normalised drifts to be compared.

        Returns
        -------
        (star_idxs, pearson_r):
            Tuple of: list of the indexes of the star, and the pearson R coefficient.
        '''
        pearson_r, p_val = scipy.stats.pearsonr(normalised_drift[star_idxs[0]],normalised_drift[star_idxs[1]])
        return (star_idxs, pearson_r)


    def perform_l3_fitting(self, target_idxs, stars, ccd_data, ccd_name, unique_stars_df):
        '''
        Fits the L3 function to the stars to get timeseries.

        Parameters
        ----------
        target_idxs: list
            A list of indexes in the stars array of the stars of interest. 
        stars: 3D array
            A 3D array, essentially a list of float Numpy 2D arrays of the subtracted stars.
        ccd_data: float ``numpy.ndarray`` of the image.
        ccd_name: str
            The name of the ccd image extension in the fits file.
        unique_stars_df: ``Pandas.DataFrame``
            Table of the centroids without duplicating reference stars.

        Returns
        -------
        extraction_df: ``Pandas.DataFrame``
            A dataframe of extracted timeseries for every star.
        '''
        df_columns = ['centroid_ID']
        for t in range(self.flat_part_len):
            df_columns.append('extraction_{}'.format(str(t)))

        extraction_df = pd.DataFrame(columns=df_columns)

        y = np.arange(11)

        nstars = len(stars)
        L0 = np.zeros((nstars, self.flat_part_len))
        S0 = np.zeros((nstars, self.flat_part_len))
        M0 = np.zeros((nstars, self.flat_part_len))

        eL = np.zeros((nstars, self.flat_part_len))
        eS = np.zeros((nstars, self.flat_part_len))
        eM = np.zeros((nstars, self.flat_part_len))

        # -------- MULTIPROCESSING -------- #
        # with Pool(30) as p:
        #     fittings = p.starmap(self.perform_l3_fitting_one_star,  enumerate(stars))
        
        # for f in fittings:
        #     star_index, popts, perrs = f
        #     L0[star_index] = [p[0] for p in popts]
        #     S0[star_index] = [p[1] for p in popts]
        #     M0[star_index] = [p[2] for p in popts]

        #     # errors for L0,S0,M0
        #     eL[star_index] = [p[0] for p in perrs]
        #     eS[star_index] = [p[1] for p in perrs]
        #     eM[star_index] = [p[2] for p in perrs]
        
        # --------------------------------- #

        for star_index, star in enumerate(stars):
            maximums = star.max(axis=0)
            col_index = 0
            for i in range(self.flat_part_start, self.flat_part_end+1):
                p0 = [maximums[i], 2., 3.5]

                try:
                    popt1, pcov1 = curve_fit(self.L3, y, star[:,i], p0)
                except RuntimeError:
                    logger.warning('Continuing after RTE at star #{}, column #{}'.format(star_index, col_index))
                    continue
                else:
                    L0[star_index, col_index] = popt1[0]
                    S0[star_index, col_index] = popt1[1]
                    M0[star_index, col_index] = popt1[2]

                    # errors for L0,S0,M0
                    perr = np.sqrt(np.diag(pcov1))
                    eL[star_index, col_index]=perr[0]
                    eS[star_index, col_index]=perr[1]
                    eM[star_index, col_index]=perr[2]

                col_index += 1

        logger.info("L3 fits done for {} stars".format(nstars))

        # shape = (L,32)
        brightness = np.sum(stars,axis=1)[:, 10:42]
        # shape(L0S0) = (L,32)
        L0S0 = L0*S0
        
        brightness_nan = np.where(brightness == 0.0, np.nan, brightness)
        L0S0_nan = np.where(L0S0 == 0.0, np.nan, L0S0)

        ratio_brightness_L0S0 = np.ma.masked_invalid(brightness_nan / L0S0_nan).mean()
        std_brightness_L0S0 = np.ma.masked_invalid(brightness_nan / L0S0_nan).std()
        SNR_brightness = np.nanmean(brightness_nan,axis=1) / np.nanstd(brightness_nan,axis=1)
        SNR_L0S0 = np.nanmean(L0S0_nan,axis=1) / np.nanstd(L0S0_nan,axis=1)

        m_bests = [] # index
        drift_corr = []
        SNR_T_corr = []
        pearson_r_best = []
        pearson_r = np.zeros((nstars,nstars))
        brightness_corr = np.zeros((nstars,self.flat_part_len))
        SNR_brightness_corr = []

        # normalise T to their median
        drift_norm = (brightness.T / np.nanmedian(brightness_nan, axis=1)).T
        # calculate Pearsonr correlations all star pairs (20,20)
        
        if target_idxs:
            star_idxs = target_idxs
        else:
            # extract all stars from centroids table
            star_idxs = np.arange(nstars)

        for k in star_idxs:
            # -------- MULTIPROCESSING -------- #
            # star_idxs = [[k, m] for m in range(nstars) if not k == m]
            # with Pool(30) as p:
            #     r_values = p.map(partial(self.get_star_correlations, normalised_drift=drift_norm), star_idxs)

            # for r in r_values:
            #     star_idxs, r_value = r
            #     pearson_r[k, star_idxs[1]] = r_value

            # pearson_r[k, k] = -np.inf
            # --------------------------------- #
            for m in np.arange(nstars):
                pearson_r[k,m], pval = scipy.stats.pearsonr(drift_norm[k],drift_norm[m])
                if k == m:
                    pearson_r[k,m] = -np.inf
                
            # for each k, find index m_best for star with the second-largest r:  i.e  largest r with r != 1
            m_best_at_k = np.argsort(pearson_r[k,:])[::-1][0]
            
            # experimental: also check whether the m_best star was affected by cosmic ray
            index_iter = 0
            cosmic_ray_affected = True            
            if 'cosmic_ray_affected' in unique_stars_df.columns:
                while cosmic_ray_affected:
                    m_best_at_k = np.argsort(pearson_r[k,:])[::-1][index_iter]
                    if unique_stars_df.iloc[m_best_at_k]['cosmic_ray_affected']:
                        index_iter+=1
                    else:
                        cosmic_ray_affected = False
                        break
            else:
                m_best_at_k = np.argsort(pearson_r[k,:])[::-1][index_iter]

            m_bests.append(m_best_at_k)

            # divide each star by the other star in the set of L stars with which it had the largest r
            drift_final = ((drift_norm[k,:] / drift_norm[m_best_at_k,:]))
            
            # plot star if the difference between two adjacent drifts is greater than the standard deviation 
            drift_final_list = drift_final.tolist()
            drift_sd = np.std(drift_final_list)
            
            # Cutout plotting
            # for e in range(len(drift_final_list)-1):
            #     if abs(drift_final_list[e] - drift_final_list[e+1]) > drift_sd:
            #         ref_star_id = unique_stars_df.at[k,'ref_star_id']
            #         x0 = unique_stars_df.at[k, 'x_cent']
            #         y0 = unique_stars_df.at[k, 'y_cent']
            #         cutout = Cutout2D(ccd_data, (x0,y0), self.cutout_size)
            #         xi, yi = cutout.to_cutout_position((x0, y0))
            #         cutout_data = cutout.data
            #         stadium_perimeter(ref_star_id, cutout_data, xi, yi, self.length, self.radius, self.output_path, self.pad)
            #         break

            drift_corr.append(drift_final_list)
            
            # now calculate the SNR for the corrected spectra
            # the r-parameter for the best match to star k is r[k,m_best[k]]
            #SNR_T_corr.append(np.median(drift_corr[k])/np.std(drift_corr[k]))
            #pearson_r_best.append(pearson_r[k,m_best_at_k])

            extraction_df.loc[k] = [unique_stars_df.at[k,'centroid_ID']] + drift_final_list

        return extraction_df


    def extract_stars(self, ccd_name):
        '''
        Extract timeseries from a CCD in the driftscan image.

        Parameters
        ----------
        ccd_name: str
            The name of the ccd image extension in the fits file.

        Returns
        -------
        extraction_df: ``Pandas.DataFrame``
            A dataframe of extracted timeseries for every star.

        '''

        fits_header, ccd_data, ccd_header = self.import_image(self.driftscan_image, ccd_name)
        
        stars, unique_stars_df, target_idxs = self.subtract_sky_from_stars(ccd_data, ccd_name)
        extraction_df = self.perform_l3_fitting(target_idxs, stars, ccd_data, ccd_name, unique_stars_df)
        extraction_df = extraction_df.dropna()

        return extraction_df


    def extract_stars_from_whole_image(self):
        '''
        Extracts stars from all specified CCDs.

        Returns
        -------
        centroids_df_with_extraction: ``Pandas.DataFrame``
            A combined dataframe of extracted timeseries and driftscan info for every star in every specified CCD.

        '''
        with Pool() as p:
            extractions = p.map(self.extract_stars, self.ccd_names)
            extraction_df = pd.concat(extractions)
        
        centroids_df_with_extraction = self.centroids_positions.merge(extraction_df, how='right', on='centroid_ID')

        return centroids_df_with_extraction

