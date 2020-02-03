from __future__ import (print_function, division)
import os
import sys
import numpy as np
import plot_util as plot_util
import pandas as pd
import warnings
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

# Read in script agruments
storm_info = sys.argv[1]

warnings.filterwarnings('ignore')
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelsize'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.formatter.useoffset'] = False
colors = [
    '#000000', '#036398', '#D55E00', '#882255',
    '#2F1E80', '#D6B616', '#018C66', '#CC79A7'
]
noaa_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'noaa.png')
)

DATA = os.environ['DATA']
RUN = os.environ['RUN']
fhr_list = os.environ['fhr_list'].split(',')
fhrs = np.asarray(fhr_list, dtype=int)
init_hour_list = os.environ['init_hour_list']
valid_hour_list = os.environ['valid_hour_list']
model_atcf_name_list = os.environ['model_atcf_name_list'].split(', ')

tc_stat_file_dir = os.path.join(DATA, RUN, 'metplus_output', 'gather',
                                'tc_stat', storm_info)
plotting_out_dir_imgs = os.path.join(DATA, RUN, 'metplus_output', 'plot',
                                     storm_info, 'imgs')
if not os.path.exists(plotting_out_dir_imgs):
    os.makedirs(plotting_out_dir_imgs)

print("Working on track and intensity error plots for "+storm_info)
print("Reading in data")
summary_tcst_filename = os.path.join(tc_stat_file_dir, 'summary.tcst')
if os.path.exists(summary_tcst_filename):
    nrow = sum(1 for line in open(summary_tcst_filename))
    if nrow == 0:
        print("ERROR: "+summary_tcst_filename+" empty")
        exit(1)
    else:
        print(summary_tcst_filename+" exists")
        summary_tcst_file = open(summary_tcst_filename, 'r')
        tc_stat_job = summary_tcst_file.readline()
        summary_tcst_read_columns = summary_tcst_file.readline().split(' ')
        summary_tcst_file.close()
        tc_stat_summary_job_columns = []
        for col in summary_tcst_read_columns:
            if col != '':
                tc_stat_summary_job_columns.append(col.rstrip())
        summary_tcst_data = pd.read_csv(summary_tcst_filename,
                                        sep=" ", skiprows=2,
                                        skipinitialspace=True,
                                        header=None, dtype=str,
                                        names=tc_stat_summary_job_columns)
        summary_tcst_data_groupby_COLUMN = (
            summary_tcst_data.groupby(['COLUMN'])
        )
        for COLUMN_group in summary_tcst_data_groupby_COLUMN.groups.keys():
            print("Creating plot for "+COLUMN_group)
            if COLUMN_group == 'ABS(AMAX_WIND-BMAX_WIND)':
                units = 'knots'
            elif COLUMN_group == 'ABS(TK_ERR)': 
                units = 'nm'
            summary_tcst_data_COLUMN = (
                summary_tcst_data_groupby_COLUMN.get_group(COLUMN_group)
            )
            summary_tcst_data_COLUMN_groupby_AMODEL = (
                summary_tcst_data_COLUMN.groupby(['AMODEL'])
            )
            fig, ax = plt.subplots(1,1,figsize=(10,6))
            ax.grid(True)
            ax.tick_params(axis='x', pad=10)
            ax.set_xlabel('Forecast Hour', labelpad=30)
            if len(fhrs) > 15:
                ax.set_xticks(fhrs[::2])
                ax.set_xticks(fhrs, minor=True)
            else: 
                ax.set_xticks(fhrs)
            ax.set_xlim([fhrs[0], fhrs[-1]])
            ax.tick_params(axis='y', pad=15)
            ax.set_ylabel(COLUMN_group+' ('+units+')', labelpad=30)
            model_num = 0
            nmodels = len(
                summary_tcst_data_COLUMN_groupby_AMODEL.groups.keys()
            )
            CI_bar_max_widths = np.append(np.diff(fhrs),
                                          fhrs[-1]-fhrs[-2])/1.5
            CI_bar_min_widths = np.append(np.diff(fhrs),
                                          fhrs[-1]-fhrs[-2])/nmodels
            CI_bar_intvl_widths = (
                (CI_bar_max_widths-CI_bar_min_widths)/nmodels
            )
            #CI_bar_intvl_widths = CI_bar_intvl_widths/3600.
            #CI_bar_max_widths = CI_bar_max_widths/3600.
            #CI_bar_min_widths = CI_bar_min_widths/3600.
            tcstat_file_AMODEL_list = (
                summary_tcst_data_COLUMN_groupby_AMODEL.groups.keys()
            )
            for AMODEL in model_atcf_name_list:
                print("Plotting "+AMODEL)
                model_num+=1
                AMODEL_plot_name = AMODEL
                if AMODEL == 'AVNO' and 'GFSO' in tcstat_file_AMODEL_list:
                    print("Using operational GFS...using ATCF name as GFSO "
                         +"to find data to comply with MET")
                    AMODEL = 'GFSO'
                fhrs_column_amodel_mean = np.full_like(fhrs, np.nan,
                                                       dtype=float)
                fhrs_column_amodel_total = np.full_like(fhrs, np.nan,
                                                        dtype=float)
                fhrs_column_amodel_mean_ncl = np.full_like(fhrs, np.nan,
                                                           dtype=float)
                fhrs_column_amodel_mean_ncu = np.full_like(fhrs, np.nan,
                                                           dtype=float)
                if AMODEL not in tcstat_file_AMODEL_list:
                    print("Data for "+AMODEL+" missing...setting to NaN")
                else:
                    summary_tcst_data_COLUMN_AMODEL = (
                        summary_tcst_data_COLUMN_groupby_AMODEL. \
                        get_group(AMODEL)
                    )
                    summary_tcst_data_COLUMN_AMODEL_LEAD = (
                        summary_tcst_data_COLUMN_AMODEL['LEAD'].values
                    )
                    summary_tcst_data_COLUMN_AMODEL_MEAN = np.asarray(
                        summary_tcst_data_COLUMN_AMODEL['MEAN'].values,
                        dtype=float
                    )
                    summary_tcst_data_COLUMN_AMODEL_TOTAL = np.asarray(
                        summary_tcst_data_COLUMN_AMODEL['TOTAL'].values,
                        dtype=float
                    )
                    summary_tcst_data_COLUMN_AMODEL_MEAN_NCL = np.asarray(
                        summary_tcst_data_COLUMN_AMODEL['MEAN_NCL'].values,
                        dtype=float
                    )
                    summary_tcst_data_COLUMN_AMODEL_MEAN_NCU = np.asarray(
                        summary_tcst_data_COLUMN_AMODEL['MEAN_NCU'].values,
                        dtype=float
                    )
                    summary_tcst_data_COLUMN_AMODEL_STDEV = np.asarray(
                        summary_tcst_data_COLUMN_AMODEL['STDEV'].values,
                        dtype=float
                    )
                    leads_list = []
                    for lead in summary_tcst_data_COLUMN_AMODEL_LEAD:
                        if lead[0] != '0':
                            leads_list.append(lead[0:3])
                        else:
                            leads_list.append(lead[1:3])
                    leads = np.asarray(leads_list, dtype=int)
                    for fhr in fhrs:
                        fhr_idx = np.where(fhr == fhrs)[0][0]
                        if fhr in leads:
                            matching_lead_idx = np.where(fhr == leads)[0][0]
                            fhrs_column_amodel_mean[fhr_idx] = (
                                summary_tcst_data_COLUMN_AMODEL_MEAN[
                                    matching_lead_idx
                                ]
                            )
                            fhrs_column_amodel_total[fhr_idx] = (
                                summary_tcst_data_COLUMN_AMODEL_TOTAL[
                                    matching_lead_idx
                                ]
                            )
                            fhrs_column_amodel_mean_ncl[fhr_idx] = (
                                summary_tcst_data_COLUMN_AMODEL_MEAN_NCL[
                                    matching_lead_idx
                                ]
                            )
                            fhrs_column_amodel_mean_ncu[fhr_idx] = (
                                summary_tcst_data_COLUMN_AMODEL_MEAN_NCU[
                                    matching_lead_idx
                                ]
                            )
                fhrs_column_amodel_mean = np.ma.masked_invalid(
                    fhrs_column_amodel_mean
                )
                fhrs_column_amodel_total = np.ma.masked_invalid(
                    fhrs_column_amodel_total
                )
                fhrs_column_amodel_mean_ncl = np.ma.masked_invalid(
                    fhrs_column_amodel_mean_ncl
                )
                fhrs_column_amodel_mean_ncu = np.ma.masked_invalid(
                    fhrs_column_amodel_mean_ncu
                )
                if model_num == 1:
                    all_amodel_total = [fhrs_column_amodel_total]
                else:
                    all_amodel_total = np.vstack(
                        (all_amodel_total, fhrs_column_amodel_total)
                    )
                all_amodel_total = np.ma.masked_invalid(all_amodel_total)
                ax.plot(fhrs, fhrs_column_amodel_mean,
                        color=colors[model_num-1],
                        ls='-',
                        linewidth=2.0,
                        marker='o',
                        markersize=3,
                        label=AMODEL_plot_name,
                        zorder=(nmodels-model_num-1)+4)
                for fhr in fhrs:
                    fhr_idx = np.where(fhr == fhrs)[0][0]
                    ax.bar(fhrs[fhr_idx], 
                           (fhrs_column_amodel_mean_ncu[fhr_idx]
                            - fhrs_column_amodel_mean_ncl[fhr_idx]),
                           bottom=fhrs_column_amodel_mean_ncl[fhr_idx],
                           color='None',
                           width=CI_bar_max_widths-(CI_bar_intvl_widths*(model_num-1)),
                           edgecolor=colors[model_num-1],
                           linewidth='1')
            ax.set_ylim(ymin=0)
            xticks_axes_fraction = np.linspace(0, 1,len(fhrs), endpoint=True)
            ax.annotate('Num. Cases', xy=(-0.2,-0.125),
                        xycoords='axes fraction')
            for fhr in fhrs:
                fhr_idx = np.where(fhr == fhrs)[0][0]
                if not np.ma.is_masked(all_amodel_total[:,fhr_idx]):
                    if np.all(all_amodel_total[:,fhr_idx]
                            == all_amodel_total[0,fhr_idx]):
                        num_cases = all_amodel_total[0,fhr_idx]
                        num_cases_str = str(int(num_cases))
                        if len(num_cases_str) <= 2:
                            rot = 0
                        else:
                            rot = 45
                        ax.annotate(num_cases_str,
                                    xy=(xticks_axes_fraction[fhr_idx],-0.125),
                                    xycoords='axes fraction', ha='center', rotation=rot)
                    else:
                        print("Working with nonhomogeneous sample for fhr "
                              +str(fhr)+"...not printing number of cases")
            boxstyle = matplotlib.patches.BoxStyle("Square", pad=0.25)
            props = {'boxstyle': boxstyle, 'facecolor': 'white',
                     'linestyle': 'solid', 'linewidth': 1,
                     'edgecolor': 'black'}
            ax.annotate("Note: where two model CIs do not intersect are \n"
                        +"statistically significant at the 95% confidence \n"
                        +"interval", xy=(-0.2,-0.2),
                        xycoords='axes fraction',
                        va='top',
                        bbox=dict(boxstyle='square', fc='w', ec='black'))
            ax.legend(bbox_to_anchor=(1.025, 1.0, 0.2, 0.0),
                      loc='upper right', ncol=1, fontsize='13',
                      mode='expand', borderaxespad=0., edgecolor='black')
            if COLUMN_group == 'ABS(TK_ERR)':
                full_title = "Absolute Track Error\n"
            elif COLUMN_group == 'ABS(AMAX_WIND-BMAX_WIND)':
                full_title = "Absolute Intensity Error\n"
            else:
                full_title = COLUMN_group+'\n'
            if len(storm_info) == 2:
                full_title = full_title+'Basin: '+storm_info+'\n'
            else:
                storm_info_split = storm_info.split('_')
                full_title = (full_title+'Basin: '+storm_info_split[0]+' '
                              +'Year: '+storm_info_split[1]+' '
                              +'Storm: '+storm_info_split[2]+'\n')
            full_title = (full_title+'Cycles: '+init_hour_list
                          +', Valid Hours: '+valid_hour_list+'\n')
            savefig_name = os.path.join(
                plotting_out_dir_imgs,
                COLUMN_group.replace('(', '').replace(')', '')
                +'_fhrmean_'+storm_info+'.png'
            )
            ax.set_title(full_title, fontsize=14, fontweight='bold')
            xtickslocs = ax.get_xticks()
            ymin, _ = ax.get_ylim()
            xaxisticks_pixel_list = ax.transData.transform(
                [(xtick, ymin) for xtick in xtickslocs]
            )
            noaa_img_offset = (
                1.75 * (xaxisticks_pixel_list[-1][0]
                       - xaxisticks_pixel_list[-2][0])
            )
            noaa_img_xpixels = xaxisticks_pixel_list[-1][0] + noaa_img_offset
            fig.figimage(noaa_logo_img_array, noaa_img_xpixels, 1,
                         zorder=1, alpha=0.5)
            print("Saving image as "+savefig_name)
            plt.savefig(savefig_name, bbox_inches='tight')
            plt.close()
else:
    print("ERROR: "+summary_tcst_filename+" does not exist")
    exit(1)
