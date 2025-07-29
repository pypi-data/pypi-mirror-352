import datetime
import os

from pydriftn import Cataloguer, DriftAstrometry, SkyEstimator, TimeSeriesGenerator


ccd_names = ['N28', 'N29', 'N31']
output_parent_dir = 'output-' + str(datetime.datetime.now().isoformat())

# GenerateCatalogue
g_path = 'demo/g_ooi_exp012923.fits'
r_path = 'demo/r_ooi_exp013253.fits'

print ("Loading Cataloguer")
test_cataloguer = Cataloguer(g_path, r_path, ccd_names, output_parent_dir, perform_cosmicray_removal=False)
# saves to 'master_catalogue.csv'
print ("Generating master_catalogue.csv")
test_cat = test_cataloguer.generate_whole_catalogue()

# DriftAstrom
photometry_cat = os.path.join(output_parent_dir, 'master_catalogue.csv')
vr_img_path = 'demo/c4d_211211_015142_ooi_VR_v1.fits.fz'
crmask_img_path = 'demo/c4d_211211_015142_ood_VR_v1.fits.fz'
track_rate = 15
anchor = 'm'

print ("Loading DriftAstrometry")
centroids_finder = DriftAstrometry(vr_img_path, photometry_cat, ccd_names, output_parent_dir, track_rate, anchor, crmask_img_path)
# saves to centroids.csv
centroids_df = centroids_finder.update_whole_image()


# DriftSkysub
centroids = os.path.join(output_parent_dir, 'centroids.csv')

print ("Loading SkyEstimator")
sky_finder = SkyEstimator(vr_img_path, centroids, ccd_names, output_parent_dir)
# saves to centroids_with_sky_values.csv
updated_centroids_df = sky_finder.update_whole_table_with_sky_values()


# DriftExtract
updated_centroids = os.path.join(output_parent_dir, 'centroids_with_sky_values.csv')

drift_extractor = TimeSeriesGenerator(vr_img_path, updated_centroids, ccd_names)
output = drift_extractor.extract_stars_from_whole_image()
print('DriftExtract.py output: ')
print(output)
