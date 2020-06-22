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
plt.rcParams['axes.titlepad'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['axes.labelpad'] = 10
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['xtick.major.pad'] = 10
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['ytick.major.pad'] = 10
plt.rcParams['figure.subplot.left'] = 0.1
plt.rcParams['figure.subplot.right'] = 0.95
plt.rcParams['figure.subplot.top'] = 0.925
plt.rcParams['figure.subplot.bottom'] = 0.075
plt.rcParams['legend.handletextpad'] = 0.25
plt.rcParams['legend.handlelength'] = 1.25
plt.rcParams['legend.borderaxespad'] = 0
plt.rcParams['legend.columnspacing'] = 1.0
plt.rcParams['legend.frameon'] = False
x_figsize, y_figsize = 14, 14
legend_bbox_x, legend_bbox_y = 0, 1
legend_fontsize = 17
legend_loc = 'upper left'
legend_ncol = 1
title_loc = 'center'
model_obs_plot_settings_dict = {
    'model1': {'color': '#000000',
               'marker': 'None', 'markersize': 0,
               'linestyle': 'solid', 'linewidth': 3},
    'model2': {'color': '#FB2020',
               'marker': '^', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model3': {'color': '#00DC00',
               'marker': 'x', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model4': {'color': '#1E3CFF',
               'marker': '+', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model5': {'color': '#E69F00',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model6': {'color': '#56B4E9',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model7': {'color': '#696969',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model8': {'color': '#8400C8',
               'marker': 'D', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model9': {'color': '#D269C1',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model10': {'color': '#F0E492',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'obs': {'color': '#AAAAAA',
            'marker': 'None', 'markersize': 0,
            'linestyle': 'solid', 'linewidth': 2}
}
noaa_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'noaa.png')
)
noaa_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.1
noaa_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.9325
noaa_logo_alpha = 0.5
nws_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'nws.png')
)
nws_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.9
nws_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.9325
nws_logo_alpha = 0.5

# Environment variables set by METplus
verif_case = os.environ['VERIF_CASE']
verif_type = os.environ['VERIF_TYPE']
plot_time = os.environ['PLOT_TIME']
start_date_YYYYmmdd = os.environ['START_DATE_YYYYmmdd']
end_date_YYYYmmdd = os.environ['END_DATE_YYYYmmdd']
start_date_YYYYmmdd_dt = datetime.datetime.strptime(os.environ['START_DATE_YYYYmmdd'], "%Y%m%d")
end_date_YYYYmmdd_dt = datetime.datetime.strptime(os.environ['END_DATE_YYYYmmdd'], "%Y%m%d")
valid_time_info = os.environ['VALID_TIME_INFO'].replace('"','').split(", ")
init_time_info = os.environ['INIT_TIME_INFO'].replace('"','').split(", ")
fcst_var_name = os.environ['FCST_VAR_NAME']
fcst_var_level_list = os.environ['FCST_VAR_LEVEL_LIST'].split(" ")
fcst_var_extra = (
    os.environ['FCST_VAR_EXTRA'].replace(" ", "")
    .replace("=","").replace(";","").replace('"','')
    .replace("'","").replace(",","-").replace("_","")
)
if fcst_var_extra == "None":
    fcst_var_extra = ""
fcst_var_thresh = (
    os.environ['FCST_VAR_THRESH'].replace(" ","")
    .replace(">=","ge").replace("<=","le")
    .replace(">","gt").replace("<","lt")
    .replace("==","eq").replace("!=","ne")
)
if fcst_var_thresh == "None":
    fcst_var_thresh = ""
obs_var_name = os.environ['OBS_VAR_NAME']
obs_var_level_list = os.environ['OBS_VAR_LEVEL_LIST'].split(" ")
obs_var_extra = (
    os.environ['OBS_VAR_EXTRA'].replace(" ", "")
    .replace("=","").replace(";","")
    .replace('"','').replace("'","")
    .replace(",","-").replace("_","")
)
if obs_var_extra == "None":
    obs_var_extra = ""
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
lead = os.environ['LEAD']
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
mean_file_cols = [ "LEADS", "VALS" ]
grid = os.environ['VERIF_GRID']
logger = logging.getLogger(os.environ['LOGGING_FILENAME'])
logger.setLevel(os.environ['LOGGING_LEVEL'])
formatter = logging.Formatter("%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d)"
                              +"%(levelname)s: %(message)s","%m/%d %H:%M:%S")
file_handler = logging.FileHandler(os.environ['LOGGING_FILENAME'], mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
fcst_var_levels = np.empty(len(fcst_var_level_list), dtype=int)
for vl in range(len(fcst_var_level_list)):
    fcst_var_levels[vl] = fcst_var_level_list[vl][1:]
if verif_type == "conus_sfc":
    obs = "_ONLYSF"
elif verif_type == "upper_air":
    obs = "_ADPUPA"
else:
    obs = ""

# Read and plot data
for stat in plot_stats_list:
    logger.debug("Working on "+stat)
    stat_plot_name = plot_util.get_stat_plot_name(logger, 
                                                  stat)
    stat_min = np.ma.masked_invalid(np.nan)
    stat_max = np.ma.masked_invalid(np.nan)
    logger.info("Reading in model data")
    for model in model_info:
        model_num = model_info.index(model) + 1
        model_index = model_info.index(model)
        model_name = model[0]
        model_plot_name = model[1]
        model_plot_settings_dict = (
            model_obs_plot_settings_dict['model'+str(model_num)]
        )
        model_level_mean_data = np.empty([len(fcst_var_level_list)])
        model_level_mean_data.fill(np.nan)
        if stat == 'fbar_obar':
            obs_level_mean_data = np.empty([len(obs_var_level_list)])
            obs_level_mean_data.fill(np.nan)
            mean_file_cols = [ "LEADS", "VALS", "OVALS" ]
        for vl in range(len(fcst_var_level_list)):
            fcst_var_level = fcst_var_level_list[vl]
            obs_var_level = obs_var_level_list[vl]
            logger.debug("Processing data for VAR_LEVEL "+fcst_var_level)
            model_mean_file = os.path.join(plotting_out_dir_data, 
                                           model_plot_name
                                           +"_"+stat
                                           #+"_"+plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd
                                           #+"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z"
                                           #+"_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z"
                                           +"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+fcst_var_thresh
                                           +"_obs"+obs_var_name+obs_var_level+obs_var_extra+obs_var_thresh
                                           +"_interp"+interp
                                           +"_region"+region
                                           +"_LEAD_MEAN.txt")
            if os.path.exists(model_mean_file):
                nrow = sum(1 for line in open(model_mean_file))
                if nrow == 0: 
                    logger.warning("Model "+str(model_num)+" "
                                   +model_name+" with plot name "
                                   +model_plot_name+" file: "
                                   +model_mean_file+" empty")
                else:
                    logger.debug("Model "+str(model_num)+" "
                                 +model_name+" with plot name "
                                 +model_plot_name+" file: "
                                 +model_mean_file+" exists")
                    model_mean_file_data = pd.read_csv(model_mean_file, 
                                                       sep=" ", 
                                                       header=None, 
                                                       names=mean_file_cols, 
                                                       dtype=str)
                    model_mean_file_data_leads = model_mean_file_data.loc[:]['LEADS'].tolist()
                    model_mean_file_data_vals = model_mean_file_data.loc[:]['VALS'].tolist()
                    if stat == 'fbar_obar':
                        obs_mean_file_data_vals = model_mean_file_data.loc[:]['OVALS'].tolist()
                    if lead in model_mean_file_data_leads:
                        model_mean_file_data_lead_index = model_mean_file_data_leads.index(lead)
                        if model_mean_file_data_vals[model_mean_file_data_lead_index] == "--":
                            model_level_mean_data[vl] = np.nan
                        else:
                            model_level_mean_data[vl] = float(
                                model_mean_file_data_vals[model_mean_file_data_lead_index]
                            )
                        if stat == 'fbar_obar':
                           if obs_mean_file_data_vals[model_mean_file_data_lead_index] == "--":
                                obs_level_mean_data[vl] = np.nan
                           else:
                                obs_level_mean_data[vl] = float(
                                     obs_mean_file_data_vals[model_mean_file_data_lead_index]
                                )    
            else:
                logger.warning("Model "+str(model_num)+" "
                                +model_name+" with plot name "
                                +model_plot_name+" file: "
                                +model_mean_file+" does not exist")
        model_level_mean_data = np.ma.masked_invalid(model_level_mean_data)
        if stat == 'fbar_obar':
            obs_level_mean_data = np.ma.masked_invalid(obs_level_mean_data)
        if model_num == 1:
            fig, ax = plt.subplots(1, 1, figsize=(x_figsize, y_figsize))
            ax.grid(True)
            ax.set_xlabel(stat_plot_name)
            ax.set_ylabel('Pressure Level (hPa)')
            ax.set_yscale("log")
            ax.invert_yaxis()
            ax.minorticks_off()
            ax.set_yticks(fcst_var_levels)
            ax.set_yticklabels(fcst_var_levels)
            ax.set_ylim([fcst_var_levels[0],fcst_var_levels[-1]])
            if stat == 'fbar_obar':
                obs_plot_settings_dict = (
                    model_obs_plot_settings_dict['obs']
                )
                obs_count = (len(obs_level_mean_data)
                             - np.ma.count_masked(obs_level_mean_data))
                mfcst_var_levels = np.ma.array(
                   fcst_var_levels,
                   mask=np.ma.getmaskarray(obs_level_mean_data)
                )
                if obs_count != 0:
                    ax.plot(obs_level_mean_data.compressed(),
                            mfcst_var_levels.compressed(),
                            color = obs_plot_settings_dict['color'],
                            linestyle = obs_plot_settings_dict['linestyle'],
                            linewidth = obs_plot_settings_dict['linewidth'],
                            marker = obs_plot_settings_dict['marker'],
                            markersize = obs_plot_settings_dict['markersize'],
                            label='obs.',
                            zorder=4)
                    if obs_level_mean_data.min() < stat_min \
                            or np.ma.is_masked(stat_min):
                        stat_min = obs_level_mean_data.min()
                    if obs_level_mean_data.max() > stat_max \
                            or np.ma.is_masked(stat_max):
                        stat_max = obs_level_mean_data.max()
        count = (len(model_level_mean_data)
                 - np.ma.count_masked(model_level_mean_data))
        mfcst_var_levels = np.ma.array(
            fcst_var_levels,
            mask=np.ma.getmaskarray(model_level_mean_data)
        )
        if count != 0:
            ax.plot(model_level_mean_data.compressed(),
                    mfcst_var_levels.compressed(),
                    color = model_plot_settings_dict['color'],
                    linestyle = model_plot_settings_dict['linestyle'],
                    linewidth = model_plot_settings_dict['linewidth'],
                    marker = model_plot_settings_dict['marker'],
                    markersize = model_plot_settings_dict['markersize'], 
                    label=model_plot_name,
                    zorder=(nmodels-model_index)+4)
            if model_level_mean_data.min() < stat_min \
                    or np.ma.is_masked(stat_min):
                stat_min = model_level_mean_data.min()
            if model_level_mean_data.max() > stat_max \
                    or np.ma.is_masked(stat_max):
                stat_max = model_level_mean_data.max()
    # Adjust x axis limits and ticks
    preset_x_axis_tick_min = ax.get_xticks()[0]
    preset_x_axis_tick_max = ax.get_xticks()[-1]
    preset_x_axis_tick_inc = ax.get_xticks()[1] - ax.get_xticks()[0]
    if stat in ['acc', 'msess', 'ets', 'rsd']:
        x_axis_tick_inc = 0.1
    else:
        x_axis_tick_inc = preset_x_axis_tick_inc
    if np.ma.is_masked(stat_min):
        x_axis_min = preset_x_axis_tick_min
    else:
        if stat in ['acc', 'msess', 'ets', 'rsd']:
            x_axis_min = round(stat_min,1) - x_axis_tick_inc
        else:
            x_axis_min = preset_x_axis_tick_min
            while x_axis_min > stat_min:
                x_axis_min = x_axis_min - x_axis_tick_inc
    if np.ma.is_masked(stat_max):
        x_axis_max = preset_x_axis_tick_max
    else:
        if stat in ['acc', 'msess', 'ets']:
            x_axis_max = 1
        elif stat in ['rsd']:
             x_axis_max = round(stat_max,1) + x_axis_tick_inc
        else:
            x_axis_max = preset_x_axis_tick_max + x_axis_tick_inc
            while x_axis_max < stat_max:
                x_axis_max = x_axis_max + x_axis_tick_inc
    ax.set_xticks(
        np.arange(x_axis_min, x_axis_max+x_axis_tick_inc, x_axis_tick_inc)
    )
    ax.set_xlim([x_axis_min, x_axis_max])
    # Check x axis limits
    if stat_max >= ax.get_xlim()[1]:
        while stat_max >= ax.get_xlim()[1]:
            x_axis_max = x_axis_max + x_axis_tick_inc
            ax.set_xticks(
                np.arange(x_axis_min,
                          x_axis_max +  x_axis_tick_inc,
                          x_axis_tick_inc)
            )
            ax.set_xlim([x_axis_min, x_axis_max])
    if stat_min <= ax.get_xlim()[0]:
        while stat_min <= ax.get_xlim()[0]:
            x_axis_min = x_axis_min - x_axis_tick_inc
            ax.set_xticks(
                np.arange(x_axis_min,
                          x_axis_max +  x_axis_tick_inc,
                          x_axis_tick_inc)
            )
            ax.set_xlim([x_axis_min, x_axis_max])
    # Add legend, adjust if points in legend
    if len(ax.lines) != 0:
        legend = ax.legend(bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                           loc=legend_loc, ncol=legend_ncol,
                           fontsize=legend_fontsize)
        plt.draw()
        legend_box = legend.get_window_extent() \
            .inverse_transformed(ax.transData)
        if stat_min < legend_box.x0:
            while stat_min < legend_box.x0:
                x_axis_min = x_axis_min - x_axis_tick_inc
                ax.set_xticks(
                    np.arange(x_axis_min,
                              x_axis_max + x_axis_tick_inc,
                              x_axis_tick_inc)
                )
                ax.set_xlim([x_axis_min, x_axis_max])
                legend = ax.legend(
                    bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                    loc=legend_loc, ncol=legend_ncol,
                    fontsize=legend_fontsize
                )
                plt.draw()
                legend_box = (
                    legend.get_window_extent() \
                    .inverse_transformed(ax.transData)
                )
    # Build formal plot title
    if grid == region:
        gridregion = grid
    else:
        gridregion = grid+region
    if interp[0:2] == 'WV':
        fcst_var_name = fcst_var_name+"_"+interp
    start_date_formatted = datetime.datetime.strptime(
        start_date_YYYYmmdd,"%Y%m%d"
    ).strftime('%d%b%Y')
    end_date_formatted = datetime.datetime.strptime(
        end_date_YYYYmmdd, "%Y%m%d"
    ).strftime('%d%b%Y')
    var_info_title = plot_title.get_var_info_title(
        fcst_var_name, 'all', fcst_var_extra, fcst_var_thresh
    )
    region_title = plot_title.get_region_title(region)
    date_info_title = plot_title.get_date_info_title(
        plot_time, valid_time_info, init_time_info,
        start_date_formatted, end_date_formatted, verif_case
    )
    forecast_lead_title = plot_title.get_lead_title(lead)
    full_title = (
        stat_plot_name+"\n"
        +var_info_title+", "+region_title+"\n"
        +date_info_title+", "+forecast_lead_title
    )
    ax.set_title(full_title, loc=title_loc)
    fig.figimage(noaa_logo_img_array,
                 noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
                 zorder=1, alpha=noaa_logo_alpha)
    fig.figimage(nws_logo_img_array,
                 nws_logo_xpixel_loc, nws_logo_ypixel_loc,
                 zorder=1, alpha=nws_logo_alpha)
    # Build savefig name
    if plot_time == 'valid':
        if verif_case == 'grid2obs':
            savefig_name = os.path.join(plotting_out_dir_imgs,
                                        stat
                                        +"_init"+init_time_info[0][0:2]+"Z"
                                        +"_"+fcst_var_name
                                        +"_all_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
        else:
            savefig_name = os.path.join(plotting_out_dir_imgs,
                                        stat
                                        +"_valid"+valid_time_info[0][0:2]+"Z"
                                        +"_"+fcst_var_name
                                        +"_all_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
    elif plot_time == 'init':
        if verif_case == 'grid2obs':
            savefig_name = os.path.join(plotting_out_dir_imgs,
                                        stat
                                        +"_valid"+valid_time_info[0][0:2]+"Z"
                                        +"_"+fcst_var_name
                                        +"_all_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
        else:
            savefig_name = os.path.join(plotting_out_dir_imgs,
                                        stat
                                        +"_init"+init_time_info[0][0:2]+"Z"
                                        +"_"+fcst_var_name
                                        +"_all_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
    logger.info("Saving image as "+savefig_name)
    plt.savefig(savefig_name)
    plt.close()
