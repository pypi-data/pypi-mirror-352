#import datetime
import os
import pandas as pd
import numpy as np
import math
import argparse

from astropy.stats import sigma_clip
from astropy.time import Time
from astropy import units as u
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker

from pydriftn.GenerateCatalogue import Cataloguer
from pydriftn.DriftAstrom import DriftAstrometry
from pydriftn.DriftSkysub import SkyEstimator
from pydriftn.DriftExtract import TimeSeriesGenerator


# add arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ignore_existing', action='store_true', help='Option to ignore an existing master catalogue file and generate a new one.')
args = parser.parse_args()

# create a list of all CCD names
s_names = ['S' + str(s) for s in range(1,32)]
n_names = ['N' + str(n) for n in range(1,32)]
n_names.remove('N30')
ccd_names = s_names + n_names

# saves output to this directory
output_parent_dir = 'demo-output'

photometry_cat = os.path.join(output_parent_dir, 'master_catalogue.csv')

# 1. GenerateCatalogue
g_path = 'demo/g_ooi_exp012923.fits'
r_path = 'demo/r_ooi_exp013253.fits'

generate_new_cat = True
# check if there is an existing master catalogue file
if os.path.isfile(photometry_cat):
    # if there is an existing master catalogue file 
    # and there is no ignore_existing flag given,
    # skip GenerateCatalogue.py
    if not args.ignore_existing:        
        generate_new_cat = False
    
if generate_new_cat:
    print ("Loading Cataloguer")
    test_cataloguer = Cataloguer(g_path, r_path, ccd_names, output_parent_dir, perform_cosmicray_removal=False, debug=True)
    # saves to 'master_catalogue.csv'
    print ("Generating master_catalogue.csv")
    test_cat = test_cataloguer.generate_whole_catalogue()
else:
    print('Using the existing master_catalogue.csv in folder {}.'.format(output_parent_dir))


# 2. DriftAstrom
vr_img_path = 'demo/c4d_211211_015142_ooi_VR_v1.fits.fz'
crmask_img_path = 'demo/c4d_211211_015142_ood_VR_v1.fits.fz'
track_rate = 15
anchor = 'm'
image_basename = os.path.splitext(os.path.basename(vr_img_path))[0].replace('.fits','')
centroids = os.path.join(output_parent_dir, 'centroids-{}.csv'.format(image_basename))
updated_centroids = os.path.join(output_parent_dir, 'centroids_with_sky_values-{}.csv'.format(image_basename))
timeseries_df = pd.read_csv(os.path.join(output_parent_dir, 'timeseries-{}.csv'.format(image_basename)))

print ("Loading DriftAstrometry")
centroids_finder = DriftAstrometry(vr_img_path, photometry_cat, ccd_names, output_parent_dir, track_rate, anchor, crmask_img_path)
print('Generating centroids.csv')
centroids_df = centroids_finder.update_whole_image()


# 3. DriftSkysub
print ("Loading SkyEstimator")
sky_finder = SkyEstimator(vr_img_path, centroids, ccd_names, output_parent_dir)
print('Generating centroids_with_sky_values.csv')
updated_centroids_df = sky_finder.update_whole_table_with_sky_values()


# 4. DriftExtract
print("Loading TimeSeriesGenerator")
drift_extractor = TimeSeriesGenerator(vr_img_path, updated_centroids, ccd_names, output_parent_dir)
print('Generating timeseries.csv')
timeseries_df = drift_extractor.extract_stars_from_whole_image()


# Plot time series
print('Plotting timeseries')
if not os.path.exists(os.path.join(output_parent_dir, 'timeseries_plots')):
    os.makedirs(os.path.join(output_parent_dir, 'timeseries_plots'))

timeseries_df = pd.read_csv(os.path.join(output_parent_dir,'timeseries-c4d_211211_015142_ooi_VR_v1.csv'))

# drift columns
cols = []
for i in range(32):
    cols.append('extraction_{}'.format(str(i)))

# sort by standard deviation
timeseries_df['median_drift'] = timeseries_df[cols].median(numeric_only=True, axis=1)
timeseries_df['std_drift'] = timeseries_df[cols].std(numeric_only=True, axis=1)
sorted_df = timeseries_df.sort_values(by='std_drift').reset_index()

# one plot per ccd
for ccd in ccd_names:
    cmap = plt.get_cmap('viridis')
    
    subset_df = sorted_df[sorted_df['chp'] == ccd]
    subset_df = subset_df.reset_index()
    
    # split df into 4 for better plotting
    for index, row in subset_df.iterrows():
        if (row[cols].isna().any()):
            subset_df.loc[index, 'ax_index'] = 0
        elif (row[cols].abs() > 100).any():
            subset_df.loc[index, 'ax_index'] = 0
        elif (row[cols].abs() > 10).any():
            subset_df.loc[index, 'ax_index'] = 1
        elif (row[cols].abs() > 2).any():
            subset_df.loc[index, 'ax_index'] = 2
        else:
            subset_df.loc[index, 'ax_index'] = 3

    subtitles = ['at least one brightness magnitude in range (100, 1000]',
                'at least one brightness magnitude in range (10, 100]',
                'at least one brightness magnitude in range (2,10]',
                'all brightness values between -2 and 2']

    df_by_ax_index = subset_df.groupby('ax_index')

    fig, axs = plt.subplots(1, 4, layout='constrained', figsize=(40,22)) 

    #plotting each subplot
    for a in df_by_ax_index.groups:
        ax_subset_df = df_by_ax_index.get_group(a)
        ax_subset_df = ax_subset_df.reset_index(drop=True)

        norm = mpl.colors.Normalize(vmin=0,vmax=len(ax_subset_df))

        top_value = -np.inf
        bottom_value = np.inf

        for index, row in ax_subset_df.iterrows():
            ax_index = int(row['ax_index'])
            drifts = row[cols].values.tolist()
            min_drift = min(drifts)
            max_drift = max(drifts)

            # do sigma clipping to avoid displaying extreme outliers
            clipped = sigma_clip(drifts, masked=False, sigma=10)
            ymin = max(min(clipped), row['median_drift']-500)
            ymax = max(clipped)

            # offset variations for better plotting
            if row['ax_index'] == 3:
                offset = 0.2
            elif row['ax_index']== 2:
                offset = 1.5
            elif row['ax_index'] == 1:
                offset = 5
            else: 
                offset = 40

            # for ylim
            max_y = min(ymax+index*offset, index*offset+500)
            if max_y > top_value:
                top_value = max_y

            if ymin < bottom_value:
                bottom_value = ymin

            # change linestyle if the drift is affeted by cosmic ray
            if row['cosmic_ray_affected'] == 1:
                # dashed
                linestyle = '--'
            else:
                # solid
                linestyle = '-'

            # TODO: ADD VARIABLE STARS HERE
            # potentially, N24-star-1244 is the eb variable star (92.253, -70.7387)
            # and N22-star-1532 is the RR lyrae (90.3174, -70.7318)
            linewidth = 1
            vstars = []
            if row['ref_star_id'] in vstars:
                linewidth = 3

            axs[ax_index].plot([index*offset + d for d in drifts], color=cmap(norm(index)), linestyle=linestyle, linewidth=linewidth)

            # add star reference ID to the plot
            #left_box_pos = max(min(top_value, index*offset + drifts[0]), bottom_value)
            label_left = row['ref_star_id'].replace(row['ref_star_id'].split('-')[0]+'-', '')
            axs[ax_index].text(-1, index*offset + np.median(drifts), label_left, fontsize=10, bbox=dict(facecolor='lightskyblue', edgecolor='black', pad=3))

            # add min and max drift values to the plot
            label_right = ('({}, {})'.format(round(min_drift,1), round(max_drift,1)))
            axs[ax_index].text(31.5, index*offset + np.median(drifts), label_right, fontsize=12, bbox=dict(facecolor='pink', edgecolor='black', pad=3))
        
        axs[ax_index].set_xlim(0,32.5)
        axs[ax_index].set_ylim(bottom_value, top_value)
        axs[ax_index].set_xticks(np.arange(32).tolist())
        axs[ax_index].set_yticks([])
        axs[ax_index].yaxis.set_major_locator(ticker.MultipleLocator(100))
        axs[ax_index].yaxis.set_minor_locator(ticker.MultipleLocator(20))
        axs[ax_index].grid(True, which='both', axis='y')
        axs[ax_index].set_title(subtitles[ax_index], fontsize=15)

        # add legend
        if ax_index == 0:
            handles, labels = plt.gca().get_legend_handles_labels()
            blue_patch = mpatches.Patch(color='lightskyblue', label='Reference star ID')
            pink_patch = mpatches.Patch(color='pink', label='Standard deviation')
            dashed_line = Line2D([0], [0], label='Affected by cosmic ray', linestyle='--', color='black')
            solid_line = Line2D([0], [0], label='Not affected by cosmic ray', linestyle='-', color='black')
            vstars = Line2D([0], [0], label='Variable stars', linestyle='-', linewidth=3, color='black')
            handles.extend([solid_line, dashed_line, vstars, blue_patch, pink_patch])
            axs[ax_index].legend(handles=handles, fontsize=12)

    fig.supxlabel("Time", fontsize = 17)
    fig.supylabel("Normalised brightness", fontsize=17)

    fig.suptitle('Extracted Timeseries for CCD #{}'.format(ccd), fontsize=30)
    fig.savefig(os.path.join(output_parent_dir, 'timeseries_plots', 'timeseries-{}.png'.format(ccd)))
    plt.close()
