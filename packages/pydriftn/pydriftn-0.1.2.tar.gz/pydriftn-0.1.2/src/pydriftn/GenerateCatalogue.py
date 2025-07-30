import astroscrappy
import datetime
import math
import numpy as np
import pandas as pd
import scipy as scp
import warnings
from collections import Counter
import os

from astropy import units as u
from astropy.coordinates import match_coordinates_sky, SkyCoord
from astropy.io import fits
from astropy.modeling.fitting import LevMarLSQFitter
from astropy.modeling.models import  Gaussian2D, Const2D, Box2D
from astropy.nddata import NDData
from astropy.stats import sigma_clipped_stats, gaussian_sigma_to_fwhm, gaussian_fwhm_to_sigma
from astropy.table import Table
from astropy.utils.exceptions import AstropyUserWarning
from astropy.visualization import SqrtStretch
from astropy.visualization.mpl_normalize import ImageNormalize, simple_norm
from astropy.visualization.wcsaxes import SphericalCircle
from astropy.wcs import WCS
from astropy.wcs.utils import fit_wcs_from_points

from urllib.parse import quote
from io import BytesIO
import requests
from astropy.io.votable import parse_single_table, parse

from photutils.aperture import CircularAperture, SkyCircularAperture
from photutils.morphology import data_properties
from photutils.psf import extract_stars, IntegratedGaussianPRF, DAOPhotPSFPhotometry, PSFPhotometry

from photutils.detection import DAOStarFinder
from photutils.psf import SourceGrouper, IterativePSFPhotometry

#for centroiding
from astropy.convolution.kernels import Model2DKernel
from astropy.convolution import convolve
from photutils.detection import find_peaks
from photutils.centroids import centroid_sources, centroid_com

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
#matplotlib.use('Agg')

from pydriftn.Utils import ImageImporter

from multiprocessing import Pool
from functools import partial
import logging
import sys


file_handler = logging.FileHandler("logfile.log")
console_handler = logging.StreamHandler()
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


class Cataloguer:
    '''
    This object class compiles several inputs into a deep photometry catalogue.
    
    Parameters
    ----------
    g_path: str
        Path to g_file.fits
    r_path: str
        Path to r_file.fits
    ccd_names: list
        A list of all CCD names to be included in the catalogue.
    output_path: str
        Path to desired output directory.
    gaia_path: str
        Path to existing GAIA_catalogue.csv.
        (Default: ``None``)
    num_target: float
        The number of target stars to be returned as references for astrometric correction to DSI and/or as
        a sample for psf modelling.
        (Default: 20)
    edge_crit: float
        The percentage of each axis length on the data image to denote as the image edge. Stars within 
        this edge_criterion are considered to be too close to the edge of the image, and won't be part of the final
        reference star selection. Default value is 5% from each edge = 0.05*data.shape.
        (Default: 0.05)
    iso_perc: float
        The percentile threshold to determine the most isolated stars, with isolation calculated as on-image pixel
        distance to nearest on-sky neighbour (using Astropy.match_coordinates_sky()). Default value is the 99th upper
        percentile of all stars.
        (Default: 0.99)
    flux_perc: float
        The percentile threshold to determine the brightest stars. It is suggested to select a moderate value 
        for the Flux threshold. This threhold is more concerned with removing faint stars from the reference catalogue,
        rather than finding the most bright of the stars. It is possible that a stringent upper threshold for Flux_Perc
        may either a: return saturated or contaminated stars, or b: return a minimal sample of reference stars below the
        required Num_target. Default value is 50th upper percentile of all stars.
        (Default: 0.5)
    morph_perc: float
        The percentile threshold to determine the least elliptical sources. Ellipticity is
        measure as '1.0 minus the ratio of the lengths of the semimajor and semiminor axes' (PhotUtils, 2023).
        This threshold works to avoid selecting saturated stars as reference objects.
        Default values is the lower 25th percentile.
        (Default: 0.25)
    timestamp: str
        a string from the Header or data file containing the date of the exposure. Intended for saving plots.
        Default value is the datetime at plotting, but can take a FITS Header['DATE'] as well.
        (Default: ``None``)
    generate_plot: boolean
        Option to save the plot each of the reference stars as cutouts on a 5X(Num_target//5) figure.
        File saved to working directory as '/reference_psf_stars.plt'.
        (Default: ``True``)
    perform_cosmicray_removal: boolean
        Option to perform cosmic ray removal at the beginning of the pipeline.
        (Default: ``False``)
    debug: boolean
        Option to save the GAIA catalogue as a .csv file.
        (Default: False)


    '''
    def __init__(self, g_path, r_path, ccd_names,  output_path, gaia_path=None, num_target=20, edge_crit=0.05, iso_perc=0.99,
                flux_perc=0.5, morph_perc=0.25, timestamp=None, generate_plot=True, perform_cosmicray_removal=False, debug=False):
        '''
        Initialises Cataloguer with file paths, ccd_names, output_path, pixscale, num_target, edge_crit,
        iso_perc, flux_perc, morph_perc, timestamp, generate_plot, perform_cosmicray_removal.
        '''
        ccd_names = [ccd_names] if isinstance(ccd_names, str) else ccd_names
        
        self.num_target = num_target
        self.edge_crit = edge_crit
        self.iso_perc = iso_perc
        self.flux_perc = flux_perc
        self.morph_perc = morph_perc

        self.generate_plot = generate_plot
        self.perform_cosmicray_removal = perform_cosmicray_removal

        self.ccd_names = ccd_names

        self.g_path = g_path
        self.r_path = r_path

        self.output_path = output_path
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        if not timestamp:
            timestamp = str(datetime.datetime.now().isoformat())
        self.timestamp = timestamp
        self.debug = debug

        plot_output_dir = os.path.join(self.output_path, 'sample_stars')
        self.plot_output_dir = plot_output_dir
        if generate_plot:
            if not os.path.exists(plot_output_dir):
                os.makedirs(plot_output_dir)

        if gaia_path is None:
            gaia_path = os.path.join(self.output_path, 'gaia_catalogue.csv')
            if not os.path.exists(gaia_path):
                gaia_path = None
        self.gaia_path = gaia_path


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
        ccd_data: float ``numpy.ndarray`` of the image.
        ccd_header: FITS header class.
        wcs_fits: ``astropy.wcs.WCS`` class object.
        clean_mask: boolean ``numpy.ndarray``
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
            clean_mask, clean_data = Image.cosmicray_removal(ccd_hdr=ccd_header, ccd_data=ccd_data)
            # TODO: save
        else:
            # TODO: read from the fits file assuming it's saved there as an extension.
            clean_mask = clean_data = None

        return fits_header, ccd_data, ccd_header, background, wcs_fits, clean_mask, clean_data, pixscale


    def tap_query_gaia(self, ra_center, dec_center, telescope_rad):
        '''
        Runs a TAP query to GAIA DR 3 to get Parallax, Gmag and VCR values.

        Parameters
        ----------
        ra_center: float
            The RA exposure centre.
        dec_center: float
            The DEC exposure centre.
        telescope_rad: float
            The FOV radius of the telescope.
        '''

        query = """SELECT g.RAJ2000, g.DEJ2000, g.Plx, g.Gmag, v.VCR, g.PM, g.pmRA, g.e_pmRA, g.pmDE, g.e_pmDE, g.e_Gmag, g.RPmag, g.e_RPmag \
                    FROM "I/355/gaiadr3" g join "I/358/varisum" v ON g.Source = v.Source \
                    WHERE 1=CONTAINS(POINT('ICRS',g.RAJ2000,g.DEJ2000), CIRCLE('ICRS', {}, {}, {}))""".format(ra_center, dec_center, telescope_rad)

        url = "http://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync?REQUEST=doQuery&lang=ADQL&FORMAT=votable&QUERY=" + quote(query)
        try:
            df = parse_single_table(BytesIO(requests.get(url).content)).to_table(use_names_over_ids=True).to_pandas()
        except requests.exceptions.ConnectionError:
            logger.error('Failed to connect to tapvizier.cds.unistra.fr')
            return None
        else:
            return df


    def find_all_peaks(self, pixscale, wcs_fits, ccd_img_data, background):
        '''
        Finds local peaks in an image using photutils ``find_peaks``.
        Takes the median of the three-sigma-clipped data as the background threshold.

        Parameters
        ----------
        pixscale: float
            the pixelscale of the image.
        wcs_fits: ``astropy.wcs.WCS`` class object.
        ccd_img_data: float ``numpy.ndarray`` of the image.
        background: float
            The estimated background value.

        Returns
        -------
        all_peaks: Table or None
            A table containing the x and y pixel location of the peaks and their values,
            unique reference IDs, the on-sky closest neighbours,
            as well as the pixel separation between them.
            If no peaks are found then None is returned.
        '''
        # TODO: see if the rr lyrae in the catalogues are in the peaks, compare to background value
        pix_scale = u.pixel_scale(pixscale*u.arcsec/u.pixel)

        all_peaks = find_peaks(ccd_img_data, threshold=background)

        if not all_peaks:
            return None

        all_peaks.rename_column('x_peak', 'x') #makes life easier with nndata conventions
        all_peaks.rename_column('y_peak', 'y')

        #Match all peaks to nearest neighbour and calculate pixel separation
        wcs_peaks = wcs_fits.pixel_to_world(all_peaks['x'], all_peaks['y'])

        #nthneighbour =2 for nearest neighbour, 1 for self-matching
        match, sep, d3sep = match_coordinates_sky(wcs_peaks, wcs_peaks, nthneighbor = 2)
        sep_arcsec = sep.arcsecond*u.arcsecond  #annoying Astropy convention
        sep_pix = sep_arcsec.to(u.pixel, pix_scale)

        #add data columns
        all_peaks['ref_id'] = np.arange(len(all_peaks))
        all_peaks['neighbour'] = match
        all_peaks['pix_sep'] = sep_pix.value

        return all_peaks


    def strip_sources(self, ccd_img_data, all_peaks_table):
        '''
        Selects isolated, bright stars.
        Strips edges, neighbouring sources that are closer than the Iso_Perc percentile,
        as well as the lower Flux_Perc percentile of faint sources.

        Parameters
        ----------
        ccd_img_data: float ``numpy.ndarray`` of the image.
        all_peaks_table: Table
            Output of the ``find_all_peaks`` function.
            A table containing the x and y pixel location of the peaks and their values,
            unique reference IDs, the on-sky closest neighbours,
            as well as the pixel separation between them.

        Returns
        -------
        inter_stars: ``astropy.table.table.QTable``
            A table containing the filtered x and y pixel locations
            of the peaks and their values,
            unique reference IDs, the on-sky closest neighbours,
            as well as the pixel separation between them.
        '''

        #converts fractional edge_crit to a number of pixels to avoid searching
        edge_y = ccd_img_data.shape[0]*self.edge_crit
        edge_x = ccd_img_data.shape[1]*self.edge_crit

        #Strip edge sources from detected peaks
        central_peaks = all_peaks_table[(all_peaks_table['x'] < ccd_img_data.shape[1]-edge_x) & (all_peaks_table['x'] > edge_x) &
            (all_peaks_table['y'] < ccd_img_data.shape[0]-edge_y) & (all_peaks_table['y'] > edge_y)]
        
        # Strip neighbouring sources closer than the Iso_Perc percentile
        sep_pix = all_peaks_table['pix_sep']
        # the most isolated stars
        sep_cut = np.quantile(sep_pix,(self.iso_perc))
        sep_mask = central_peaks['pix_sep'] > sep_cut
        iso_peaks = central_peaks[sep_mask]

        # Strip the lower Flux_Perc percentile of faint sources
        # upper 50% of brightest stars
        flux_cut = np.quantile(central_peaks['peak_value'].data,(self.flux_perc))
        flux_mask = central_peaks['peak_value'] > flux_cut
        # intermediate selection of isolated, bright stars
        inter_stars = central_peaks[flux_mask]

        return inter_stars


    def select_reference_stars(self, pixscale, wcs_fits, ccd_img_data, background):
        '''
        Finds reference stars.
        Utilises ``photutils.psf.extract_stars`` to extract intermediate stars
        then provides morphological properties of the stars, masks on ellipticity,
        and performs random sampling to output ``num_target`` stars.

        Parameters
        ----------
        pixscale: float
            the pixelscale of the image.
        wcs_fits: ``astropy.wcs.WCS`` class object.
        ccd_img_data: float ``numpy.ndarray`` of the image.
        background: float
            The estimated background value.

        Returns
        -------
        ref_sample: ``pandas.DataFrame``
            A Pandas dataframe containing the x,y pixel, skycoordinates, peak flux,
            morphology measurements such as the semimajor sigma, semiminor sigma,
            fwhm and ellipticity values,
            as well as the nearest neighbour pixel separation
            of ``num_target`` bright, isolated reference stars.
        all_df_with_ref_indicator: ``pandas.DataFrame``
            A Pandas dataframe containing all the stars, including non reference stars.
        all_stars: ``photutils.psf.EPSFStars`` instance
            An EPSFStars instance containing the extracted intermediate stars.
        '''
        all_peaks = self.find_all_peaks(pixscale, wcs_fits, ccd_img_data, background)
        all_peaks_df = all_peaks.to_pandas()

        inter_stars = self.strip_sources(ccd_img_data, all_peaks)
        inter_stars_df = inter_stars.to_pandas()

        #Extract all intermediate stars
        star_nddata = NDData(data=ccd_img_data)
        all_stars = extract_stars(star_nddata, inter_stars, size=15)

        #Mask unuseable extracted stars (from overlapping cutout regions)
        extract = pd.DataFrame(all_stars.center_flat, columns = ['x', 'y'])
        ref_stars = inter_stars_df.merge(extract.drop_duplicates(), on=['x','y'], how='right')

        semimajor_sigmas = []
        semiminor_sigmas = []
        fwhms = []
        ellipticities = []

        for star in all_stars:
            star_properties = data_properties(star)
            semimajor_sigmas.append(star_properties.semimajor_sigma.value)
            semiminor_sigmas.append(star_properties.semiminor_sigma.value)
            fwhms.append(star_properties.fwhm.value)
            ellipticities.append(star_properties.ellipticity.value)

        ref_stars = ref_stars.assign(semimajor_sigma=semimajor_sigmas,
                                    semiminor_sigma=semiminor_sigmas,
                                    fwhm=fwhms,
                                    ellipticity=ellipticities)
        
        #Mask on ellipticity 
        morph_lower = np.quantile(ref_stars['ellipticity'],(self.morph_perc))
        ref_stars = ref_stars[(ref_stars['ellipticity'] <= morph_lower)]

        #Return final random sample COULD be a sampling function (linear, highest, lowest, random)
        ref_sample = ref_stars.sample(n=self.num_target, random_state=123)
        all_df_with_ref_indicator = pd.merge(all_peaks_df, ref_stars[['ref_id', 'semimajor_sigma', 'semiminor_sigma', 'fwhm', 'ellipticity']],
                                            on=['ref_id'], how='outer', indicator='ref_star')
        all_df_with_ref_indicator = all_df_with_ref_indicator.replace(np.nan, 0.0)
        all_df_with_ref_indicator['ref_star'] = np.where(all_df_with_ref_indicator.ref_star == 'both', True, False)
        all_df_with_ref_indicator = all_df_with_ref_indicator[all_df_with_ref_indicator['ref_id'].notna()]

        #all_df_with_ref_indicator.to_csv(os.path.join(self.output_path, 'all_stars.csv'), index=False)

        return ref_sample, all_df_with_ref_indicator, all_stars



    def plot_psf_stars(self, sample_df, all_stars, ccd_name):
        '''
        Plots stars and saves it into a .png file.
        Takes the indices of the sampled stars dataframe and
        creates a plot based on the EPSFStars instance.

        Parameters
        ----------
        sample_df: ``Pandas.dataframe``
            Output of the ``select_reference_stars`` function.
            A Pandas dataframe containing the sampled stars and their information.
        all_stars: ``photutils.psf.EPSFStars`` instance
            Output of the ``select_reference_stars`` function.
            An EPSFStars instance containing extracted intermediate stars.
        ccd_name: str
            The name of the ccd image extension in the fits file.
        '''

        # Saves into 'sample_stars/psf_stars_{timestamp}.png'
        #get the extracted data array for the psf_stars
        logger.info("Plotting sample reference stars...")
        sample_ind = sample_df.index.values
        psf_stars = [all_stars[i-1] for i in sample_ind]

        nrows = 5
        ncols = int(len(psf_stars)/nrows) #will not plot all stars if Num_target is not a multiple of 5.

        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(20, 20),
                                squeeze=True)
        ax = ax.ravel()
        for i in range(nrows*ncols):
            norm = simple_norm(psf_stars[i], 'log', percent=99.0)
            ax[i].imshow(psf_stars[i], norm=norm, origin='lower', cmap='viridis')
        fig_save = plt.gcf()

        output_fig_path = os.path.join(self.plot_output_dir, "psf_stars-{}-{}.png".format(ccd_name, self.timestamp))
        fig_save.savefig(output_fig_path)
        logger.info("Succesfully saved sample reference stars plot as {}".format(output_fig_path))
        #plt.show()


    def pointed_catalogue(self, ccd_name, ccd_img_data, background, wcs_fits, stars_df):
        '''
        Generates a catalogue for the sample reference stars.
        Takes the FWHM (full width at half maximum) values
        to define the PSF (point spread function) sigma guess
        for the PRF (pixel response function) model,
        then runs photometry on the CCD image data
        and uses the WCS convention to get an estimate of local RA, Dec for X-match
        between the r and g bands.

        Parameters
        ----------
        ccd_name: str
            The name of the ccd image extension in the fits file.
        ccd_img_data: float ``numpy.ndarray`` of the image.
        background: float
            The estimated background value.
        wcs_fits: ``astropy.wcs.WCS`` class object.
        stars_df: ``pandas.DataFrame``
            A Pandas dataframe containing the x and y pixel
            location of the sampled stars and their peak values
            unique reference IDs, the on-sky closest neighbours
            and the pixel separation between them,
            as well as the semimajor sigma, semiminor sigma,
            fwhm and ellipticity values of the star.

        Returns
        -------
        comb_phot: ``Pandas.DataFrame``
            A Pandas dataframe containing reference IDs, x and y pixel values, flux values, ra and dec.
        '''
        #Use FWHM to define the PSF sigma guess for the PRF model
        psf_fwhm_stats = sigma_clipped_stats(stars_df['fwhm'].values, sigma=3.0, mask_value=0.0)
        psf_fwhm = psf_fwhm_stats[1]

        sigma_psf = psf_fwhm * gaussian_fwhm_to_sigma
        #Run photometry on the CCD images
        fitter = LevMarLSQFitter()
        psf_model = IntegratedGaussianPRF(sigma=sigma_psf)

        '''
        photometry = DAOPhotPSFPhotometry(crit_separation = 3*psf_fwhm, threshold = background,
                                        fwhm = psf_fwhm, sigma = 3, psf_model=psf_model, fitter=LevMarLSQFitter(),
                                        niters=1, fitshape=(7,7))
        table = photometry(image=ccd_img_data)
        S = photometry.get_residual_image()
        '''

        # TODO: params for IterativePSFPhotometry and make_residual_image:
        aperture_rad = 3
        #sigma_rad = 1.5 * psf_fwhm/(2.0*np.sqrt(2.0*np.log(2.0)))
        psfshape = (7,7)

        grouper = SourceGrouper(min_separation=3*psf_fwhm)
        finder = DAOStarFinder(threshold=background, fwhm=psf_fwhm)
        photometry = IterativePSFPhotometry(psf_model=psf_model, fit_shape=(7,7), 
                                            finder=finder, grouper=grouper, fitter=fitter,
                                            aperture_radius=aperture_rad)
        
        # Using DAOStarFinder.find_stars instead of PSFPhotometry
        table = finder.find_stars(data=ccd_img_data)
        # pd_table = table.to_pandas()
        # pd_table.to_csv('finder-find_stars.csv', index=False)
        # try:
        # table = photometry(data=ccd_img_data)
        # pd_table = table.to_pandas()
        # pd_table.to_csv('iterativepsfphotometry.csv', index=False)
        # except ValueError:
        # print(ccd_name)
        # return None
        # S = photometry.make_residual_image(data=ccd_img_data, psf_shape=psfshape)

        #Use WCS convention to get estimate of local RA, Dec for X-match between r and g band
        sky_positions = wcs_fits.pixel_to_world(table['xcentroid'], table['ycentroid'])

        #Make final frame
        ids = [ccd_name + '-star-' + str(i-1) for i in table['id']]
        comb_phot = pd.DataFrame()
        comb_phot['chp'] = [ccd_name]*len(sky_positions)
        comb_phot['ref_star_id'] =  ids
        comb_phot['x'] = table['xcentroid']
        comb_phot['y'] = table['ycentroid']
        comb_phot['flux'] = table['flux']
        # NOTE: no 'flux_unc' from IterativePSFPhotometry
        #comb_phot['flux_unc'] = table['flux_unc']
        comb_phot['ra'] = np.array([i.ra.degree for i in sky_positions])
        comb_phot['dec'] = np.array([i.dec.degree for i in sky_positions])
        comb_phot['ref_star'] = 'True'

        return comb_phot


    def match_catalogues(self, photometry_df, gaia_df):
        '''
        Matches the photometry catalogue with the GAIA catalogue.

        Parameters
        ----------
        photometry_df: ``Pandas.DataFrame``
            A Pandas dataframe containing reference stars from the FITS image (one CCD).
        gaia_df: ``Pandas.DataFrame``
            A Pandas dataframe of the GAIA catalogue.

        Returns
        -------
        photometry_df: ``Pandas DataFrame``
            A Pandas dataframe with the combined information from both catalogues.
        '''

        # Get matches
        match_2, sep_2, d3sep_2 = match_coordinates_sky(SkyCoord(photometry_df['ra'].values, photometry_df['dec'].values,unit="deg"), 
                                                        SkyCoord(gaia_df['RAJ2000'].values, gaia_df['DEJ2000'].values, unit="deg"), 
                                                        nthneighbor = 1)
        
        # add best match ra, dec and separation (in arcseconds) to the photometry dataframe
        for col in gaia_df.columns:
            photometry_df[col] = [gaia_df[col][i] for i in match_2]

        photometry_df.rename(columns={"RAJ2000": "ra_GAIA", "DEJ2000": "dec_GAIA"}, inplace=True)
        photometry_df['separation'] = sep_2.arcsecond

        return photometry_df


    def generate_master_catalogue(self, filepath, ccd_name):
        '''
        Generates a master catalogue for one CCD, which is a subset of the whole catalogue.

        Parameters
        ----------
        filepath: str
            Local path to the FITS file.
        ccd_name: str
            The name of the ccd image extension in the fits file.

        Returns
        -------
        master_catalogue: ``Pandas.DataFrame``
            A Pandas dataframe of the master catalogue for one CCD.

        '''

        # For one ccd
        # import image
        fits_header, ccd_data, ccd_header, background, wcs_fits, crmask, cleanarr, pixscale = self.import_image(filepath, ccd_name)

        if cleanarr:
            # if cosmicray removal was just performed.
            data = cleanarr
        else:
            data = ccd_data
        
        # Get GAIA catalogue
        if self.gaia_path:
            try:
                gaia_cat = pd.read_csv(self.gaia_path)
            except FileNotFoundError:
                logger.fatal('Fatal: GAIA catalogue not found. Please check input path.')
                gaia_cat = None
        else:
            logger.info('Connecting to VizieR to get GAIA catalogue...')
            ra_center = fits_header['CENTRA']
            dec_center = fits_header['CENTDEC']
            telescope_rad = 1.1

            gaia_cat = self.tap_query_gaia(ra_center, dec_center, telescope_rad)
            
        if gaia_cat is None:
            logger.fatal('Fatal: need a GAIA catalogue.')
            return None

        if self.debug:
            # save the GAIA catalogue as a csv file
            new_gaia_path = os.path.join(self.output_path, 'gaia_catalogue.csv')
            if new_gaia_path != self.gaia_path:
                if not os.path.exists(new_gaia_path):
                    if gaia_cat is not None:
                        gaia_cat.to_csv(new_gaia_path, index=False)
                    logger.info('Saved GAIA catalogue as {}.'.format(new_gaia_path))
        
        # select reference stars
        sample_reference_stars, all_stars_df, all_stars = self.select_reference_stars(pixscale, wcs_fits, data, background)

        # plot
        if self.generate_plot:
            self.plot_psf_stars(sample_reference_stars, all_stars, ccd_name)

        # photutils photometry
        photometry_cat = self.pointed_catalogue(ccd_name, ccd_data, background, wcs_fits, all_stars_df)

        if photometry_cat is None:
            logger.fatal('Fatal: Photutils.finder.find_stars - empty table returned.')
            return None

        # get GAIA best match
        photometry_and_gaia_cat = self.match_catalogues(photometry_cat, gaia_cat)

        return photometry_and_gaia_cat


    def compile_g_r_catalogues(self, ccd_name):
        '''
        Generates and compiles catalogues of the g and r images.
        Keep everything in r catalogue, add matched g coordinates to each entry in the r catalogue.

        Parameters
        ----------
        ccd_name: str
            The name of the ccd image extension in the fits file.

        Returns
        -------
        r_cat: ``Pandas DataFrame``
            The combined g and r catalogue for the CCD.

        '''       
        # get photometry + GAIA catalogues for g and r images
        g_cat = self.generate_master_catalogue(self.g_path, ccd_name)
        r_cat = self.generate_master_catalogue(self.r_path, ccd_name)

        if g_cat is None:
            return None
        elif r_cat is None:
            return None
        #g_cat.to_csv('g_stars.csv', index=False)
        #r_cat.to_csv('r_stars.csv', index=False)

        # match g catalogue to r catalogue (main)
        match_3, sep_3, d3sep_3 = match_coordinates_sky(SkyCoord(r_cat['ra_GAIA'].values, r_cat['dec_GAIA'].values, unit="deg"),
                                                        SkyCoord(g_cat['ra_GAIA'].values, g_cat['dec_GAIA'].values, unit="deg"),
                                                        nthneighbor = 1)

        matched_g = g_cat.reindex(match_3)
        matched_g = matched_g.reset_index()

        # add ra and dec from the g catalogue to the r catalogue
        r_cat['ra_g'] = matched_g['ra']
        r_cat['dec_g'] = matched_g['dec']
        #r_cat.to_csv('combined_r_g_stars.csv', index=False)

        return r_cat


    def generate_whole_catalogue(self):
        '''
        Generates catalogues for all specified CCDs in both g and r files and concatenates them into *the* 'whole catalogue'.

        Returns
        -------
        whole_cat: ``Pandas.DataFrame``
            A Pandas dataframe of the whole catalogue which consists of 
            master catalogues of all specified CCDs.

        '''
        with Pool(2) as p:
            # this should give a list of dataframes
            ccd_cats = p.map(self.compile_g_r_catalogues, self.ccd_names)

        if all(c is None for c in ccd_cats):
            logger.warning('Empty catalogue: check above errors. Quitting program...')
            sys.exit()

        whole_cat = pd.concat(ccd_cats)
        output_csv_path = os.path.join(self.output_path, 'master_catalogue.csv')
        whole_cat.to_csv(output_csv_path, index=False)
        logger.info("Successfully saved the main catalogue as {}.".format(output_csv_path))

        return whole_cat
