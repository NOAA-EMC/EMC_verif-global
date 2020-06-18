## Edited from METplus V2.1
## for EMC purposes

from __future__ import (print_function, division)
import os
import numpy as np
import plot_util as plot_util
import plot_title as plot_title
import pandas as pd
import warnings
import logging
import datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.gridspec as gridspec

warnings.filterwarnings('ignore')

# Plot Settings
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.titlepad'] = 5
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.labelpad'] = 10
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['xtick.major.pad'] = 5
plt.rcParams['ytick.major.pad'] = 5
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['figure.subplot.left'] = 0.1
plt.rcParams['figure.subplot.right'] = 0.95
plt.rcParams['figure.titleweight'] = 'bold'
plt.rcParams['figure.titlesize'] = 16
nticks = 4
title_loc = 'center'
cmap = plt.cm.BuPu_r
cmap_diff = plt.cm.coolwarm_r
noaa_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'noaa.png')
)
noaa_logo_alpha = 0.5
nws_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'nws.png')
)
nws_logo_alpha = 0.5

# Environment variables set by METplus
verif_case = os.environ['VERIF_CASE']
verif_type = os.environ['VERIF_TYPE']
plot_time = os.environ['PLOT_TIME']
start_date_YYYYmmdd = os.environ['START_DATE_YYYYmmdd']
end_date_YYYYmmdd = os.environ['END_DATE_YYYYmmdd']
valid_time_info = os.environ['VALID_TIME_INFO'].replace('"','').split(", ")
init_time_info = os.environ['INIT_TIME_INFO'].replace('"','').split(", ")
fcst_var_name = os.environ['FCST_VAR_NAME']
fcst_var_extra = (
    os.environ['FCST_VAR_EXTRA'].replace(" ", "")
    .replace("=","").replace(";","").replace('"','')
    .replace("'","").replace(",","-").replace("_","")
)
if fcst_var_extra == "None":
    fcst_var_extra = ""
fcst_var_level = os.environ['FCST_VAR_LEVEL']
fcst_var_thresh = (
    os.environ['FCST_VAR_THRESH'].replace(" ","")
    .replace(">=","ge").replace("<=","le")
    .replace(">","gt").replace("<","lt")
    .replace("==","eq").replace("!=","ne")
)
if fcst_var_thresh == "None":
    fcst_var_thresh = ""
obs_var_name = os.environ['OBS_VAR_NAME']
obs_var_extra = (
    os.environ['OBS_VAR_EXTRA'].replace(" ", "")
    .replace("=","").replace(";","")
    .replace('"','').replace("'","")
    .replace(",","-").replace("_","")
)
if obs_var_extra == "None":
    obs_var_extra = ""
obs_var_level = os.environ['OBS_VAR_LEVEL']
obs_var_thresh = (
    os.environ['OBS_VAR_THRESH'].replace(" ","")
    .replace(">=","ge").replace("<=","le")
    .replace(">","gt").replace("<","lt")
    .replace("==","eq").replace("!=","ne")
)
if obs_var_thresh == "None":
    obs_var_thresh = ""
interp = os.environ['INTERP']
region = os.environ['REGION']
lead_list = os.environ['LEAD_LIST'].split(", ")
leads = np.asarray(lead_list).astype(float)
stat_file_input_dir_base = os.environ['STAT_FILES_INPUT_DIR']
plotting_out_dir = os.environ['PLOTTING_OUT_DIR_FULL']
plotting_out_dir_data = os.path.join(plotting_out_dir,
                                     "data",
                                     plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd
                                     +"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z"
                                     +"_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z")
plotting_out_dir_imgs = os.path.join(plotting_out_dir,
                                     "imgs")
if not os.path.exists(plotting_out_dir_data):
    os.makedirs(plotting_out_dir_data)
if not os.path.exists(plotting_out_dir_imgs):
    os.makedirs(plotting_out_dir_imgs)
plot_stats_list = os.environ['PLOT_STATS_LIST'].split(", ")
model_name_list = os.environ['MODEL_NAME_LIST'].split(" ")
nmodels = len(model_name_list)
model_plot_name_list = os.environ['MODEL_PLOT_NAME_LIST'].split(" ")
model_info = zip(model_name_list, model_plot_name_list)
grid = os.environ['VERIF_GRID']
event_equalization = os.environ['EVENT_EQUALIZATION']
met_version = os.environ['MET_VERSION']
logger = logging.getLogger(os.environ['LOGGING_FILENAME'])
logger.setLevel(os.environ['LOGGING_LEVEL'])
formatter = logging.Formatter("%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d)"
                              +"%(levelname)s: %(message)s","%m/%d %H:%M:%S")
file_handler = logging.FileHandler(os.environ['LOGGING_FILENAME'], mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stat_file_base_columns = plot_util.get_stat_file_base_columns(met_version)

# Read and plot data
logger.info("Reading in model data")
for model in model_info:
    model_num = model_info.index(model) + 1
    model_name= model[0]
    model_plot_name = model[1]
    for l in range(len(lead_list)):
        lead = lead_list[l]
        logger.debug("Processing data for forecast hour lead "+lead)
        plot_time_dates, expected_stat_file_dates = plot_util.get_date_arrays(plot_time, 
                                                                              start_date_YYYYmmdd, 
                                                                              end_date_YYYYmmdd, 
                                                                              valid_time_info, 
                                                                              init_time_info, 
                                                                              lead)
        total_days = len(plot_time_dates)
        model_lead_data_now_index = pd.MultiIndex.from_product(
            [[model_plot_name], [lead], expected_stat_file_dates], 
            names=['model_plot_name', 'leads', 'dates']
        )
        model_stat_file = os.path.join(stat_file_input_dir_base, 
                                       verif_case, 
                                       verif_type, 
                                       model_plot_name, 
                                       plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd
                                       +"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z"
                                       +"_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z", 
                                       model_plot_name
                                       +"_f"+lead
                                       +"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+fcst_var_thresh
                                       +"_obs"+obs_var_name+obs_var_level+obs_var_extra+obs_var_thresh
                                       +"_interp"+interp
                                       +"_region"+region
                                       +".stat")
        if os.path.exists(model_stat_file):
            nrow = sum(1 for line in open(model_stat_file))
            if nrow == 0:
                logger.warning("Model "+str(model_num)+" "
                               +model_name+" with plot name "
                               +model_plot_name+" file: "
                               +model_stat_file+" empty")
                model_lead_now_data = pd.DataFrame(np.nan, 
                                                   index=model_lead_data_now_index, 
                                                   columns=[ 'TOTAL' ])
            else:
                logger.debug("Model "+str(model_num)+" "
                             +model_name+" with plot name "
                             +model_plot_name+" file: "
                             +model_stat_file+" exists")
                model_now_stat_file_data = pd.read_csv(model_stat_file, 
                                                       sep=" ", 
                                                       skiprows=1, 
                                                       skipinitialspace=True, 
                                                       header=None)
                model_now_stat_file_data.rename(
                    columns=dict(
                        zip(model_now_stat_file_data.columns[:len(stat_file_base_columns)], 
                            stat_file_base_columns)
                    ), 
                    inplace=True
                )
                line_type = model_now_stat_file_data['LINE_TYPE'][0]
                stat_file_line_type_columns = plot_util.get_stat_file_line_type_columns(logger, 
                                                                                        met_version, 
                                                                                        line_type)
                model_now_stat_file_data.rename(
                    columns=dict(
                        zip(model_now_stat_file_data.columns[len(stat_file_base_columns):], 
                            stat_file_line_type_columns)
                    ),
                    inplace=True
                )
                model_now_stat_file_data_fcst_valid_dates = model_now_stat_file_data.loc[:]['FCST_VALID_BEG'].values
                model_lead_now_data = pd.DataFrame(np.nan, 
                                                   index=model_lead_data_now_index, 
                                                   columns=stat_file_line_type_columns)
                for expected_date in expected_stat_file_dates:
                    if expected_date in model_now_stat_file_data_fcst_valid_dates:
                         matching_date_index = model_now_stat_file_data_fcst_valid_dates.tolist().index(expected_date)
                         model_now_stat_file_data_indexed = model_now_stat_file_data.loc[matching_date_index][:]
                         for column in stat_file_line_type_columns:
                             model_lead_now_data.loc[(model_plot_name, lead, expected_date)][column] = model_now_stat_file_data_indexed.loc[:][column]
        else:
            logger.warning("Model "+str(model_num)+" "
                           +model_name+" with plot name "
                           +model_plot_name+" file: "
                           +model_stat_file+" does not exist")
            model_lead_now_data = pd.DataFrame(np.nan, 
                                               index=model_lead_data_now_index, 
                                               columns=[ 'TOTAL' ])
        if l > 0:
            model_now_data = pd.concat([model_now_data, model_lead_now_data])
        else:
            model_now_data = model_lead_now_data
    if model_num > 1:
        model_data = pd.concat([model_data, model_now_data])
    else:
        model_data = model_now_data

yy, xx = np.meshgrid(plot_time_dates, leads)
logger.info("Calculating and plotting statistics")
for stat in plot_stats_list:
    logger.debug("Working on "+stat)
    stat_values, stat_values_array, stat_plot_name = plot_util.calculate_stat(logger, 
                                                                              model_data,
                                                                              stat)
    if stat == "fbar_obar":
        logger.warning(stat+" is not currently supported for this type of plot")
        continue
    if event_equalization == "True":
        logger.debug("Doing event equalization")
        for l in range(len(lead_list)):
            stat_values_array[:,l,:] = np.ma.mask_cols(stat_values_array[:,l,:])
    if nmodels == 1:
        x_figsize, y_figsize = 14, 7
        row, col = 1, 1
        hspace, wspace = 0, 0
        bottom, top = 0.175, 0.825
        suptitle_y_loc = 0.92125
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.865
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.865
        cbar_bottom = 0.06
        cbar_height = 0.02
    elif nmodels == 2:
        x_figsize, y_figsize = 14, 7
        row, col = 1, 2
        hspace, wspace = 0, 0.1
        bottom, top = 0.175, 0.825
        suptitle_y_loc = 0.92125
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.865
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.865
        cbar_bottom = 0.06
        cbar_height = 0.02
    elif nmodels > 2 and nmodels <= 4:
        x_figsize, y_figsize = 14, 14
        row, col = 2, 2
        hspace, wspace = 0.15, 0.1
        bottom, top = 0.125, 0.9
        suptitle_y_loc = 0.9605
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
        cbar_bottom = 0.03
        cbar_height = 0.02
    elif nmodels > 4 and nmodels <= 6:
        x_figsize, y_figsize = 14, 14
        row, col = 3, 2
        hspace, wspace = 0.15, 0.1
        bottom, top = 0.125, 0.9
        suptitle_y_loc = 0.9605
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
        cbar_bottom = 0.03
        cbar_height = 0.02
    elif nmodels > 6 and nmodels <= 8:
        x_figsize, y_figsize = 14, 14
        row, col = 4, 2
        hspace, wspace = 0.175, 0.1
        bottom, top = 0.125, 0.9
        suptitle_y_loc = 0.9605
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
        cbar_bottom = 0.03
        cbar_height = 0.02
    elif nmodels > 8 and nmodels <= 10:
        x_figsize, y_figsize = 14, 14
        row, col = 5, 2
        hspace, wspace = 0.225, 0.1
        bottom, top = 0.125, 0.9
        suptitle_y_loc = 0.9605
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
        cbar_bottom = 0.03
        cbar_height = 0.02
    else:
        logger.error("Too many models selected, max. is 10")
        exit(1)
    suptitle_x_loc = (plt.rcParams['figure.subplot.left']
                      +plt.rcParams['figure.subplot.right'])/2.
    fig = plt.figure(figsize=(x_figsize, y_figsize))
    gs = gridspec.GridSpec(
        row, col,
        bottom = bottom, top = top,
        hspace = hspace, wspace = wspace,
    )
    noaa_logo_xpixel_loc = (
        x_figsize * plt.rcParams['figure.dpi'] * noaa_logo_x_scale
    )
    noaa_logo_ypixel_loc = (
        y_figsize * plt.rcParams['figure.dpi'] * noaa_logo_y_scale
    )
    nws_logo_xpixel_loc = (
        x_figsize * plt.rcParams['figure.dpi'] * nws_logo_x_scale
    )
    nws_logo_ypixel_loc = (
        y_figsize * plt.rcParams['figure.dpi'] * nws_logo_y_scale
    )
    for model in model_info:
        model_num = model_info.index(model) + 1
        model_index = model_info.index(model)
        model_name = model[0]
        model_plot_name = model[1]
        model_stat_values_array = stat_values_array[model_index,:,:]
        ax = plt.subplot(gs[model_index])
        ax.grid(True)
        ax.set_xticks(leads)
        ax.set_xlim([leads[0], leads[-1]])
        if ax.is_last_row() or (nmodels % 2 != 0 and model_num == nmodels -1):
            ax.set_xlabel("Forecast Hour")
        else:
            plt.setp(ax.get_xticklabels(), visible=False)
        ax.set_ylim([plot_time_dates[0],plot_time_dates[-1]])
        day_interval = int(len(plot_time_dates)/nticks)
        ax.set_yticks(plot_time_dates[::day_interval])
        ax.yaxis.set_major_formatter(md.DateFormatter('%d%b%Y'))
        if len(plot_time_dates) > 60:
            ax.yaxis.set_minor_locator(md.MonthLocator())
        else:
            ax.yaxis.set_minor_locator(md.DayLocator())
        if ax.is_first_col():
            ax.set_ylabel(plot_time.title()+" Date")
        else:
            plt.setp(ax.get_yticklabels(), visible=False)
        if stat == "bias":
            logger.debug("Plotting model "+str(model_num)+" "
                         +model_name+" with name on plot "
                         +model_plot_name)
            ax.set_title(model_plot_name, loc='left')
            if model_num == 1:
                clevels_bias = plot_util.get_clevels(model_stat_values_array)
                CF1 = ax.contourf(xx, yy, model_stat_values_array, 
                                  levels=clevels_bias, 
                                  cmap=cmap_bias, 
                                  locator=matplotlib.ticker.MaxNLocator(symmetric=True), 
                                  extend='both')
                C1 = ax.contour(xx, yy, model_stat_values_array, 
                                levels=CF1.levels, 
                                colors='k', 
                                linewidths=1.0)
                ax.clabel(C1, C1.levels, 
                          fmt='%1.2f', 
                          inline=True, 
                          fontsize=12.5)
            else:
                CF = ax.contourf(xx, yy, model_stat_values_array, 
                                 levels=CF1.levels, 
                                 cmap=cmap_bias, 
                                 extend='both')
                C = ax.contour(xx, yy, model_stat_values_array, 
                               levels=CF1.levels, 
                               colors='k', 
                               linewidths=1.0)
                ax.clabel(C, 
                          C.levels, 
                          fmt='%1.2f', 
                          inline=True, 
                          fontsize=12.5)
        else:
            if model_num == 1:
                logger.debug("Plotting model "+str(model_num)+" "
                             +model_name+" with name on plot "
                             +model_plot_name)   
                model1_name = model_name
                model1_plot_name = model_plot_name
                model1_stat_values_array = model_stat_values_array
                ax.set_title(model_plot_name, loc='left')
                if stat in ['acc']:
                    levels = np.array(
                        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5,
                         0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1]
                    )
                    CF1 = ax.contourf(xx, yy, model_stat_values_array, 
                                      levels=levels, cmap=cmap, 
                                      extend='both')
                else:
                    CF1 = ax.contourf(xx, yy, model_stat_values_array, 
                                      cmap=cmap, 
                                      extend='both')
                C1 = ax.contour(xx, yy, model_stat_values_array, 
                                levels=CF1.levels, 
                                colors='k', 
                                linewidths=1.0)
                ax.clabel(C1, 
                          C1.levels, 
                          fmt='%1.2f', 
                          inline=True, 
                          fontsize=12.5)
            else:
                logger.debug("Plotting model "+str(model_num)+" "
                             +model_name+" - model 1 "+model1_name
                             +" with name on plot "
                             +model_plot_name+"-"+model1_plot_name)
                ax.set_title(model_plot_name+"-"+model1_plot_name, loc='left')
                model_model1_diff = model_stat_values_array - model1_stat_values_array
                if model_num == 2:
                    clevels_diff = plot_util.get_clevels(model_model1_diff)
                    CF2 = ax.contourf(xx, yy, model_model1_diff, 
                                      levels=clevels_diff, 
                                      cmap=cmap_diff, 
                                      locator=matplotlib.ticker.MaxNLocator(symmetric=True),
                                      extend='both')
                    #C2 = ax.contour(xx, yy, model_model1_diff, 
                    #                levels=CF2.levels, 
                    #                colors='k', 
                    #                linewidths=1.0)
                    #ax.clabel(C2, 
                    #          C2.levels, 
                    #          fmt='%1.2f', 
                    #          inline=True, 
                    #          fontsize=12.5)
                else:
                    CF = ax.contourf(xx, yy, model_model1_diff, 
                                     levels=CF2.levels, 
                                     cmap=cmap_diff, 
                                     locator=matplotlib.ticker.MaxNLocator(symmetric=True), 
                                     extend='both')
                    #C = ax.contour(xx, yy, model_model1_diff, 
                    #               levels=CF2.levels, 
                    #               colors='k', 
                    #               linewidths=1.0)
                    #ax.clabel(C, 
                    #          C.levels, 
                    #          fmt='%1.2f', 
                    #          inline=True, 
                    #          fontsize=12.5)
    # Build formal plot title
    if grid == region:
        gridregion = grid
    else:
        gridregion = grid+region
    if interp[0:2] == 'WV':
        fcst_var_name = fcst_var_name+"_"+interp
    var_info_title = plot_title.get_var_info_title(
        fcst_var_name, fcst_var_level, fcst_var_extra, fcst_var_thresh
    )
    region_title = plot_title.get_region_title(region)
    date_info_title = plot_title.get_date_info_title(
        plot_time, valid_time_info, init_time_info,
        str(datetime.date.fromordinal(int(
            plot_time_dates[0])
        ).strftime('%d%b%Y')),
        str(datetime.date.fromordinal(int(
            plot_time_dates[-1])
        ).strftime('%d%b%Y')),
        verif_case
    )
    full_title = (
        stat_plot_name+"\n"
        +var_info_title+", "+region_title+"\n"
        +date_info_title
    )
    fig.suptitle(full_title,
                 x = suptitle_x_loc, y = suptitle_y_loc,
                 horizontalalignment = title_loc,
                 verticalalignment = title_loc)
    noaa_img = fig.figimage(noaa_logo_img_array,
                 noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
                 zorder=1, alpha=noaa_logo_alpha)
    nws_img = fig.figimage(nws_logo_img_array,
                 nws_logo_xpixel_loc, nws_logo_ypixel_loc,
                 zorder=1, alpha=nws_logo_alpha)
    plt.subplots_adjust(
        left = noaa_img.get_extent()[1]/(plt.rcParams['figure.dpi']*x_figsize),
        right = nws_img.get_extent()[0]/(plt.rcParams['figure.dpi']*x_figsize)
    )
    # Add colorbar
    cbar_left = noaa_img.get_extent()[1]/(plt.rcParams['figure.dpi']*x_figsize)
    cbar_width = (
        nws_img.get_extent()[0]/(plt.rcParams['figure.dpi']*x_figsize)
        - noaa_img.get_extent()[1]/(plt.rcParams['figure.dpi']*x_figsize)
    )
    if stat == "bias":
        make_colorbar = True
        colorbar_CF = CF1
        colorbar_CF_ticks = CF1.levels
        colorbar_label = 'Bias'
    elif stat!= "bias" and nmodels > 1:
        make_colorbar = True
        colorbar_CF = CF2
        colorbar_CF_ticks = CF2.levels
        colorbar_label = 'Difference'
    else:
        make_colorbar = False
    if make_colorbar:
        cax = fig.add_axes(
            [cbar_left, cbar_bottom, cbar_width, cbar_height]
        )
        cbar = fig.colorbar(colorbar_CF,
                            cax = cax,
                            orientation = 'horizontal',
                            ticks = colorbar_CF_ticks)
        cbar.ax.set_xlabel(colorbar_label, labelpad = 0)
        cbar.ax.xaxis.set_tick_params(pad=0)
    # Build savefig name
    if plot_time == 'valid':
        savefig_name = os.path.join(plotting_out_dir_imgs, 
                                    stat
                                    +"_valid"+valid_time_info[0][0:2]+"Z"
                                    +"_"+fcst_var_name+"_"+fcst_var_level
                                    +"_leaddate"
                                    +"_"+gridregion
                                    +".png")
    elif plot_time == 'init':
        savefig_name = os.path.join(plotting_out_dir_imgs, 
                                    stat
                                    +"_init"+init_time_info[0][0:2]+"Z"
                                    +"_"+fcst_var_name+"_"+fcst_var_level
                                    +"_leaddate"
                                    +"_"+gridregion
                                    +".png")
    logger.info("Saving image as "+savefig_name)
    plt.savefig(savefig_name)
    plt.close()
