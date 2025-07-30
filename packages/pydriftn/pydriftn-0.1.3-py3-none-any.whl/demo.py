#import datetime
import os
import pandas as pd
import numpy as np
import math
import argparse
import yaml

from multiprocessing import Pool
from functools import partial

from astropy.stats import sigma_clip
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import match_coordinates_sky, SkyCoord
from astropy.wcs.utils import skycoord_to_pixel, pixel_to_skycoord

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker
from matplotlib.backends.backend_pdf import PdfPages 

from pydriftn.GenerateCatalogue import Cataloguer
from pydriftn.DriftAstrom import DriftAstrometry
from pydriftn.DriftSkysub import SkyEstimator
from pydriftn.DriftExtract import TimeSeriesGenerator
from pydriftn.Utils import ImageImporter

# Skip generate_catalogue.py

def run_pipeline(drift_image_path, values_dict):
    demo_parent_dir = values_dict['demo_parent_dir']
    output_parent_dir = os.path.join(
        demo_parent_dir, values_dict['output_dir']
    )

    Image = ImageImporter(drift_image_path)
    photometry_cat = values_dict['photometry_cat_path']

    # saves output to this directory
    drifts_dir = os.path.basename(os.path.dirname(drift_image_path))
    if not os.path.exists(os.path.join(output_parent_dir,drifts_dir)):
        os.makedirs(os.path.join(output_parent_dir,drifts_dir))

    track_rate = values_dict['drift_astrom']['track_rate']
    anchor = values_dict['drift_astrom']['anchor']
    expnum = os.path.splitext(
        os.path.basename(
            drift_image_path
        )
    )[0].split('-')[1]

    # 2. DriftAstrom
    print ("Loading DriftAstrometry")

    drift_astrom_dfs= []
    for ccd in values_dict['ccd']:
        ccd_header, ccd_data = Image.get_fits_image(ccd)
        wcs_fits = Image.wcs_transform(ccd_header)
        if values_dict['read_mask'] == True:
            drift_mask_path = drift_image_path.replace('image', 'dqmask')
            if os.path.exists(drift_mask_path):
                centroids_finder = DriftAstrometry(
                    drift_image_path, photometry_cat, ccd,
                    track_rate, anchor, drift_mask_path
                )
            else:
                centroids_finder = DriftAstrometry(
                    drift_image_path, photometry_cat, ccd,
                    track_rate, anchor
                )
        else:
            centroids_finder = DriftAstrometry(
                drift_image_path, photometry_cat, ccd,
                track_rate, anchor
            )
        print('Generating centroids_df')
        centroids_df = centroids_finder.update_image_wcs(ccd)
        new_drift_map = centroids_df.reset_index()

        drift_astrom_dfs.append(new_drift_map)

    compiled_centroids_df = pd.concat(drift_astrom_dfs, ignore_index=True)
    driftastrom_output = os.path.join(
        output_parent_dir,
        drifts_dir,
        'driftastrom-{}.csv'.format(expnum)
    )
    compiled_centroids_df.to_csv(driftastrom_output, index=False)

    # target matching
    if values_dict['read_targets']:
        target_csv = values_dict['targets']['csv_path']
        ra_col_name = values_dict['targets']['ra_col_name']
        dec_col_name = values_dict['targets']['dec_col_name']
        separation_cut = values_dict['targets']['separation_cut']

        target_df = pd.read_csv(
            target_csv,
            na_values=["      ", '#N/A', 'N/A', 'NULL']
        )
        subset_key = values_dict['targets']['subset']['key']
        subset_values = values_dict['targets']['subset']['values']
        variables = target_df[target_df[subset_key].isin(subset_values)]
        
        match_2, sep_2, d3sep_2 = match_coordinates_sky(
            SkyCoord(
                variables[ra_col_name].values,
                variables[dec_col_name].values,unit="deg"
            ), 
            SkyCoord(
                compiled_centroids_df['skycoord_peak.ra'].values,
                compiled_centroids_df['skycoord_peak.dec'].values,
                unit="deg"
            ), 
            nthneighbor = 1
        )

        drift_map_matches = compiled_centroids_df.loc[match_2]
        
        # add best match ra, dec and separation (in arcseconds)
        # to the photometry dataframe
        variables_with_matches = pd.concat(
            [variables.reset_index(), drift_map_matches.reset_index()],
            axis=1
        )
        print(variables_with_matches)        
        # annoying Astropy convention
        variables_with_matches['separation'] = (sep_2.arcsecond*u.arcsecond).value
        close_match = variables_with_matches[variables_with_matches['separation'] <= separation_cut]
        target_centroid_ids = close_match['centroid_ID'].tolist()
    else:
        target_centroid_ids = []
    
    # TODO: optimise
    # 3. DriftSkysub
    print ("Loading SkyEstimator")

    cutout_size = values_dict['drift_skysub']['cutout_size']
    length = values_dict['drift_skysub']['length']
    radius = values_dict['drift_skysub']['radius']
    pad = values_dict['drift_skysub']['pad']

    drift_skysub_dfs= []
    for ccd in values_dict['ccd']:
        sky_finder = SkyEstimator(
            drift_image_path, driftastrom_output, ccd,
            cutout_size, length, radius, pad
        )
        print('Generating centroids_with_sky_values.csv')
        sky_df = sky_finder.calculate_local_sky(ccd)

        drift_skysub_dfs.append(sky_df)

    compiled_sky_df = pd.concat(drift_skysub_dfs, ignore_index=True)

    drift_map_with_sky = compiled_centroids_df.merge(
        compiled_sky_df,
        how='left',
        on='centroid_ID'
    )

    driftskysub_output = os.path.join(
        output_parent_dir,
        drifts_dir,
        'driftskysub-{}.csv'.format(expnum)
    )
    drift_map_with_sky.to_csv(driftskysub_output, index=False)

    # 4. DriftExtract
    print("Loading TimeSeriesGenerator")

    drift_extract_dfs= []
    for ccd in values_dict['ccd']:
        drift_extractor = TimeSeriesGenerator(
            drift_image_path, driftskysub_output,
            target_centroid_ids, ccd, output_parent_dir
        )
        print('Generating timeseries.csv')
        extraction_df = drift_extractor.extract_stars(ccd)

        drift_extract_dfs.append(extraction_df)

    compiled_extraction_df = pd.concat(drift_extract_dfs, ignore_index=True)
    timeseries_df = drift_map_with_sky.merge(
        compiled_extraction_df, how='right', on='centroid_ID'
    )
    timeseries_df['expnum'] = expnum.split('_')[1]

    if values_dict['read_targets']:
        for index, row in timeseries_df.iterrows():
            try:
                star_id = close_match.loc[close_match['centroid_ID'] == row['centroid_ID'], 'star_id'].item()
            except ValueError:
                star_id = 'no match'

            timeseries_df.loc[index, 'star_id'] = star_id
    
        if timeseries_df.empty:
            timeseries_df.loc[0, 'star_id'] = 'no match'

        driftextract_output = os.path.join(
            output_parent_dir,
            drifts_dir,
            'target-driftextract-{}.csv'.format(expnum)
        )
    else:
        driftextract_output = os.path.join(
            output_parent_dir,
            drifts_dir,
            'driftextract-{}.csv'.format(expnum)
        )

    timeseries_df.to_csv(driftextract_output, index=False)

    return timeseries_df


# MAIN

parser = argparse.ArgumentParser()
parser.add_argument('-y', '--yaml', default='../demo/demo_values.yaml')
args = parser.parse_args()


with open(args.yaml, 'r') as stream:
    values = yaml.safe_load(stream)

with open(values['pointed_images_yaml_path'], 'r') as stream2:
    pointed_images = yaml.safe_load(stream2)

drift_files = []

demo_parent_dir = values['demo_parent_dir']
output_parent_dir = os.path.join(demo_parent_dir, values['output_dir'])
for drifts_dir in values['drifts_dirs']:
    for f in os.listdir(drifts_dir):
        if 'image' in f:
            expnum = os.path.splitext(f)[0].split('-')[1]
            driftextract_output = os.path.join(
                output_parent_dir,
                drifts_dir,
                'driftextract-{}.csv'.format(expnum)
            )
            if not os.path.exists(driftextract_output):
                # skip if already exists
                if expnum not in pointed_images:
                    drift_files.append(os.path.join(drifts_dir, f))

# Run pipeline
with Pool() as p:
    timeseries_tables = p.map(
        partial(run_pipeline, values_dict=values), drift_files
    )


# Plotting all extractions
print ('Plotting timeseries')
pdf_path = os.path.join(values['output_dir'], values['pdf_output'])
with PdfPages(pdf_path) as pdf:
    meds = {}
    for timeseries_dir in values['drifts_dirs']: 
        timeseries_tables = []
        meds[timeseries_dir] = {}
        expnums_with_extractions = []
        for f in os.listdir(timeseries_dir):
            if 'driftextract' in f:
                # exposure number
                enum = int(
                    os.path.splitext(
                        os.path.basename(f)
                    )[0].split('_')[1]
                )
                
                expnums_with_extractions.append(enum)
                t = pd.read_csv(os.path.join(timeseries_dir, f))
                if t.empty:
                    # no extraction: plot gaps
                    t.loc[0, 'expnum'] = enum
                    t.loc[0, 'star_id'] = 'no match'
                timeseries_tables.append(t)

        timeseries_tables.sort(key=lambda d: d['expnum'].iloc[0])
        min_exp = timeseries_tables[0]['expnum'].iloc[0]
        max_exp = timeseries_tables[-1]['expnum'].iloc[0]
        
        # no extraction, no empty csv output either:
        # get the exposure numbers to plot gaps
        missing = set(expnums_with_extractions) ^ set(range(min_exp, max_exp+1))
        
        cols = []
        for i in range(32):
            cols.append('extraction_{}'.format(str(i)))

        target_stars = []
        for t in timeseries_tables:
            target_stars += t['star_id'].to_list()

        target_stars = sorted(list(set(target_stars)))
        if 'no match' in target_stars:
            target_stars.remove('no match')

        for s in target_stars:
            meds[timeseries_dir][s] = []

        # 1 page per star, per night
        #  40 exposures per row
        n_exp_per_row = 40
        nrows = math.ceil((max_exp - min_exp + 1) / n_exp_per_row)
        for index, s in enumerate(target_stars):
            fig, axs = plt.subplots(nrows, 1, figsize=(n_exp_per_row, 2*nrows))
            norm = mpl.colors.Normalize(vmin=0,vmax=5)
            cmap = plt.get_cmap('viridis')
            drifts_by_axs = {}
            expnums = {}
            for exp_index, t in enumerate(timeseries_tables):
                ax = int(exp_index/n_exp_per_row)
                #print(exp_index, ax)
                if ax not in drifts_by_axs:
                    drifts_by_axs[ax] = []
                if ax not in expnums:
                    expnums[ax] = []
                expnums[ax].append(t['expnum'].iloc[0])
                target = t.loc[t['star_id'] == s]
                if target.empty:
                    # gaps, then set median to nan
                    print(t['expnum'].iloc[0])
                    drifts_by_axs[ax] += [np.nan] * 34
                    meds[timeseries_dir][s].append(np.nan)
                elif t['expnum'].iloc[0] in pointed_images:
                    # gaps, then set median to nan
                    drifts_by_axs[ax] += [np.nan] * 34
                    meds[timeseries_dir][s].append(np.nan)
                else:
                    one_exp_drifts = target[cols].values.tolist()[0]
                    mean_drifts = np.median(one_exp_drifts)
                    meds[timeseries_dir][s].append(mean_drifts)
                    for n in range(2):
                        one_exp_drifts.append(np.nan)
                    
                    # check if extractions for exposure number +1 exist
                    # if not plot gaps and set median to nan
                    if (t['expnum'].iloc[0] + 1) in missing:
                        for n in range(34):
                            one_exp_drifts.append(np.nan)
                        expnums[ax].append(t['expnum'].iloc[0] + 1)
                        meds[timeseries_dir][s].append(np.nan)
                    drifts_by_axs[ax] += one_exp_drifts

            linestyle = '-'
            linewidth = 1

            for plot_ax in drifts_by_axs:
                drifts = drifts_by_axs[plot_ax]
                min_drift = min(drifts)
                max_drift = max(drifts)

                label_right = ('{}: ({}, {})'.format(
                    s, round(min_drift,1), round(max_drift,1)
                ))
                ticks = [x * 34 for x in range(len(expnums[plot_ax]))]

                if nrows == 1:
                    axs.plot(
                        drifts,
                        color=cmap(norm(index)),
                        linestyle=linestyle,
                        linewidth=linewidth
                    )
                    axs.set_ylim([0.9, 1.1])

                    # secondary x axis
                    # 1 tick per second, i.e., 2 extraction points per tick
                    ax2 = axs.twiny()
                    ax2.plot(range(len(drifts)), [1.2]*len(drifts))
                    ax2.set_xticklabels([])
                    ax2.set_xticks(range(0, len(drifts), 2), [])

                    # add min and max drift values to the plot as floating box
                    axs.text(
                        len(expnums[plot_ax]) * 34,
                        np.nanmedian(drifts),
                        label_right,
                        fontsize=6,
                        bbox=dict(
                            facecolor='lightskyblue', edgecolor='black', pad=3
                        )
                    )                 
                    axs.set_xticks(ticks, expnums[plot_ax])
                
                else:
                    axs[plot_ax].plot(
                        drifts, 
                        color=cmap(norm(index)),
                        linestyle=linestyle,
                        linewidth=linewidth
                    )
                    axs[plot_ax].set_ylim([0.9, 1.1])

                    # secondary x axis
                    # 1 tick per second, i.e., 2 extraction points per tick
                    ax2 = axs[plot_ax].twiny()
                    ax2.plot(range(0, len(drifts)), [1.2]*int(len(drifts)))
                    ax2.set_xticklabels([])
                    ax2.set_xticks(range(0, len(drifts), 2), [])
                    
                    # add min and max drift values to the plot
                    axs[plot_ax].text(
                        (len(expnums[plot_ax])) * 34,
                        np.nanmedian(drifts),
                        label_right, fontsize=6,
                        bbox=dict(
                            facecolor='lightskyblue',edgecolor='black', pad=3
                        )
                    )
                    axs[plot_ax].set_xticks(ticks, expnums[plot_ax])
        
            fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            fig.suptitle(
                'Extractions for {}, {}'.format(
                    s, timeseries_dir
                ),
                fontsize=32,
                y=0.98
            )
            pdf.savefig()
            plt.close()


# A separate pdf for medians
with PdfPages(pdf_path.replace('.pdf', '-median.pdf')) as pdf:    
    fig, axs = plt.subplots(3, len(meds), figsize=(90, 9))
    norm = mpl.colors.Normalize(vmin=0,vmax=5)
    cmap = plt.get_cmap('viridis')
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    for dir_index, d in enumerate(meds):
        for star_index, s in enumerate(meds[d]):
            axs[star_index, dir_index].plot(
                meds[d][s], color=cmap(norm(star_index))
            )
            axs[star_index, dir_index].set_title('{}, {}'.format(s, d))
            axs[star_index, dir_index].set_ylim([0.9, 1.1])
    fig.suptitle('Median drifts', fontsize=32, y=0.98)
    pdf.savefig()
    plt.close()
