import numpy as np
import pandas as pd
from astropy.io import fits
import matplotlib.pyplot as plt
import scipy.stats
from scipy.optimize import curve_fit
from scipy.stats import norm
from scipy.integrate import simps
import os
import logging
from Utils import ImageImporter, get_bbox_coords_from_centre_coords

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
    photometry_catalogue: str
        Local path to photometry_catalogue.csv.
    ccd_names: list

    bias_files: list
        A list of paths to bias FITS files.

    '''
    def __init__(self, driftscan_image_path, centroids_positions, ccd_names):
        '''
        Initialises TimeSeriesGenerator with lccd names and ocal file paths of the driftscan image, photometry catalogue and bias files.
        '''
        ccd_names = [ccd_names] if isinstance(ccd_names, str) else ccd_names

        self.driftscan_image = driftscan_image_path #'/Users/reneekey/Documents/drift_testset/c4d_2019B0071_exp917982.fits'
        self.centroids_positions = pd.read_csv(centroids_positions) # path to photometry_catalogue.csv.
        self.ccd_names = ccd_names
        # fit to flat part of DSI: x = 10:41 incl : 32 pixels
        self.flat_part_start = 10
        self.flat_part_end = 41
        self.flat_part_len = 1 + self.flat_part_end - self.flat_part_start


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

        Image = ImageImporter(ccd_name, filepath)

        fits_header = Image.get_fits_header()
        ccd_header, ccd_data = Image.get_fits_image()

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
        P = LF*SF**N / (np.abs(y-MF)**N + SF**N)
        return P


    def subtract_sky_from_stars(self, ccd_name, ccd_data):
        '''
        Subtracts the median sky value saved in the centroids dataframe
        from the cropped driftscan bounding box.

        Parameters
        ----------
        ccd_name: str
            The name of the ccd image extension in the fits file.
        ccd_data: float ``numpy.ndarray`` of the image.

        Returns
        -------
        subtracted_stars: list
            A list of float ``numpy.ndarray``s of the subtracted stars.
        '''
        star_shape = (11,51) # (height, width)

        subtracted_stars = []
        centroids_subset = self.centroids_positions[self.centroids_positions['chp'] == ccd_name]
        for index, row in centroids_subset.iterrows():
            # TODO: which column in centroids_positions df?
            x1, x2, y1, y2 = get_bbox_coords_from_centre_coords(row['catalogue_reference_x'], row['catalogue_reference_y'], star_shape, ccd_data.shape)
            star = ccd_data[y1:y2, x1:x2]
            if star.shape == (11,51):
                star -= row['sky']
                subtracted_stars.append(star)

        return subtracted_stars


    def perform_l3_fitting(self, stars):
        '''
        Fits the L3 function to the stars to get timeseries.

        Parameters
        ----------
        stars: 3D array
            A 3D array, essentially a list of float Numpy 2D arrays of the subtracted stars.

        Returns
        -------
        # TODO
        SNR_T_corr: list
            A list of the SNRs for the corrected spectra.
        pearson_r_best: list
            A list of the best R values.
        '''
        y = np.arange(11)
        nstars = len(stars)
        L0 = np.zeros((nstars, self.flat_part_len))
        S0 = np.zeros((nstars, self.flat_part_len))
        M0 = np.zeros((nstars, self.flat_part_len))

        eL = np.zeros((nstars, self.flat_part_len))
        eS = np.zeros((nstars, self.flat_part_len))
        eM = np.zeros((nstars, self.flat_part_len))

        for star_index, star in enumerate(stars):
            maximums = star.max(axis=0)
            col_index = 0
            for i in range(self.flat_part_start, self.flat_part_end+1):
                p0 = [maximums[i], 2., 3.5]

                try:
                    popt1, pcov1 = curve_fit(self.L3, y, star[:,i], p0)
                except RuntimeError:
                    logger.warning('Continuing after RTE at star #{}, column #{}'.format(star_index, col_index))
                    #TODO: error handling for l0, s0, m0, eL, eS, eM
                    continue
                else:
                    # shape(L0) = (20,32)
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

        ratio_brightness_L0S0 = np.ma.masked_invalid(brightness / L0S0).mean()
        std_brightness_L0S0 = np.ma.masked_invalid(brightness / L0S0).std()
        SNR_brightness = np.nanmean(brightness_nan,axis=1) / np.nanstd(brightness_nan,axis=1)
        SNR_L0S0 = np.nanmean(L0S0_nan,axis=1) / np.nanstd(L0S0_nan,axis=1)

        # TODO
        m_bests = [] # index
        T_corr = []
        SNR_T_corr = []
        pearson_r_best = []
        pearson_r = np.zeros((nstars,nstars))
        brightness_corr = np.zeros((nstars,self.flat_part_len))
        SNR_brightness_corr = []

        # normalise T to their median
        T_norm = (brightness.T / np.nanmedian(brightness_nan, axis=1)).T
        # calculate Pearsonr correlations all star pairs (20,20)
        for k in np.arange(nstars): 
            for m in np.arange(nstars):
                pearson_r[k,m], pval = scipy.stats.pearsonr(T_norm[k],T_norm[m])
                
                # for each k, find index m_best for star with the second-largest r:  i.e  largest r with r != 1
                if pearson_r[k,m] == 1:
                    # TODO
                    pearson_r[k,m] = 0
            
            m_best_at_k = np.argsort(pearson_r[k,:])[::-1][0]
            m_bests.append(m_best_at_k)

            # divide each star by the other star in the set of L stars with which it had the largest r
            T_corr.append((T_norm[k,:] / T_norm[m_best_at_k,:]))

            # now calculate the SNR for the corrected spectra
            # the r-parameter for the best match to star k is r[k,m_best[k]]
            SNR_T_corr.append(np.median(T_corr[k])/np.std(T_corr[k]))
            pearson_r_best.append(pearson_r[k,m_best_at_k])

        print(type(SNR_T_corr), type(pearson_r_best))
        return SNR_T_corr, pearson_r_best


    def extract_stars(self, ccd_name):
        '''
        Extract timeseries(?) from a CCD in the driftscan image.

        Parameters
        ----------
        ccd_name: str
            The name of the ccd image extension in the fits file.

        Returns
        -------
        # TODO
        snrs: list
            A list of the SNRs for the corrected spectra.
        r_bests: list
            A list of the best R values.

        '''

        fits_header, ccd_data, ccd_header = self.import_image(self.driftscan_image, ccd_name)
        stars = self.subtract_sky_from_stars(ccd_name, ccd_data)
        snrs, r_bests = self.perform_l3_fitting(stars)

        return snrs, r_bests

    def extract_stars_from_whole_image(self):
        '''
        Extracts stars from the whole driftscan image.

        Returns
        -------
        # TODO

        '''
        with Pool() as p:
            output = p.map(self.extract_stars, self.ccd_names)

        return output