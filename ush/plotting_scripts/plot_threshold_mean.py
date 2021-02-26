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
legend_bbox_x, legend_bbox_y = 0.5, 0.05
legend_fontsize = 15
legend_loc = 'center'
legend_ncol = 5
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
fcst_var_name = os.environ['FCST_VAR_NAME']
fcst_var_extra = (
    os.environ['FCST_VAR_EXTRA'].replace(" ", "")
    .replace("=","").replace(";","").replace('"','')
    .replace("'","").replace(",","-").replace("_","")
)
if fcst_var_extra == "None":
    fcst_var_extra = ""
fcst_var_level = os.environ['FCST_VAR_LEVEL']
fcst_var_thresh_list = os.environ['FCST_VAR_THRESH_LIST'].split(", ")
fcst_var_thresh_format_list = []
fcst_var_thresh_val_list = []
for thresh in fcst_var_thresh_list:
    thresh_format = (
        thresh.replace(" ","")
        .replace(">=","ge").replace("<=","le")
        .replace(">","gt").replace("<","lt")
        .replace("==","eq").replace("!=","ne")
    )
    fcst_var_thresh_format_list.append(thresh_format)
    thresh_val = (
        thresh.replace(" ","")
        .replace(">=","").replace("<=","")
        .replace(">","").replace("<","")
        .replace("==","").replace("!=","")
        .replace("ge","").replace("le","")
        .replace("gt","").replace("lt","")
        .replace("eq","").replace("ne","")
    )
    fcst_var_thresh_val_list.append(thresh_val)
fcst_var_thresh_val_array = np.asarray(fcst_var_thresh_val_list, dtype=float)
fcst_var_thresh_counts = np.arange(0, len(fcst_var_thresh_list), dtype=int)
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
obs_var_thresh_list = os.environ['OBS_VAR_THRESH_LIST'].split(", ")
obs_var_thresh_format_list = []
obs_var_thresh_val_list = []
for thresh in obs_var_thresh_list:
    thresh_format = (
        thresh.replace(" ","")
        .replace(">=","ge").replace("<=","le")
        .replace(">","gt").replace("<","lt")
        .replace("==","eq").replace("!=","ne")
    )
    obs_var_thresh_format_list.append(thresh_format)
    thresh_val = (
        thresh.replace(" ","")
        .replace(">=","").replace("<=","")
        .replace(">","").replace("<","")
        .replace("==","").replace("!=","")
        .replace("ge","").replace("le","")
        .replace("gt","").replace("lt","")
        .replace("eq","").replace("ne","")
    )
    obs_var_thresh_val_list.append(thresh_val)
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
model_plot_name_list = os.environ['MODEL_PLOT_NAME_LIST'].split(" ")
model_info = zip(model_name_list, model_plot_name_list)
mean_file_cols = [ "LEADS", "VALS", "OVALS" ]
ci_file_cols = [ "LEADS", "VALS" ]
ci_method = os.environ['CI_METHOD']
grid = os.environ['VERIF_GRID']
logger = logging.getLogger(os.environ['LOGGING_FILENAME'])
logger.setLevel(os.environ['LOGGING_LEVEL'])
formatter = logging.Formatter("%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d)"
                              +"%(levelname)s: %(message)s","%m/%d %H:%M:%S")
file_handler = logging.FileHandler(os.environ['LOGGING_FILENAME'], mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
nmodels = len(model_name_list)
fcst_var_thresh_val_array = np.asarray(fcst_var_thresh_val_list, dtype=float)
CI_bar_max_widths = np.append(np.diff(fcst_var_thresh_counts),
                              fcst_var_thresh_counts[-1]-fcst_var_thresh_counts[-2])/1.5
CI_bar_min_widths = np.append(np.diff(fcst_var_thresh_counts),
                              fcst_var_thresh_counts[-1]-fcst_var_thresh_counts[-2])/nmodels
CI_bar_intvl_widths = (
    (CI_bar_max_widths-CI_bar_min_widths)/nmodels
)

# Read and plot data
for stat in plot_stats_list:
    logger.debug("Working on "+stat)
    stat_plot_name = plot_util.get_stat_plot_name(logger, 
                                                  stat)
    stat_min_max_dict = {
        'ax1_stat_min': np.ma.masked_invalid(np.nan),
        'ax1_stat_max': np.ma.masked_invalid(np.nan),
        'ax2_stat_min': np.ma.masked_invalid(np.nan),
        'ax2_stat_max': np.ma.masked_invalid(np.nan)
    }
    logger.info("Reading in model data")
    for model in model_info:
        model_num = model_info.index(model) + 1
        model_index = model_info.index(model)
        model_name = model[0]
        model_plot_name = model[1]
        model_plot_settings_dict = (
            model_obs_plot_settings_dict['model'+str(model_num)]
        )
        if stat == "fbar_obar":
            model_mean_data = np.empty([2,len(fcst_var_thresh_list)])
        else:
            model_mean_data = np.empty(len(fcst_var_thresh_list))
        model_mean_data.fill(np.nan)
        for vt in range(len(fcst_var_thresh_format_list)):
            fcst_var_thresh = fcst_var_thresh_format_list[vt]
            obs_var_thresh = obs_var_thresh_format_list[vt]
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
                    if stat == "fbar_obar":
                        model_mean_file_data_leads = model_mean_file_data.loc[:]['LEADS'].tolist()
                        model_mean_file_data_vals = model_mean_file_data.loc[:]['VALS'].tolist()
                        model_mean_file_data_ovals = model_mean_file_data.loc[:]['OVALS'].tolist()
                        if lead in model_mean_file_data_leads:
                            model_mean_file_data_lead_index = model_mean_file_data_leads.index(lead)
                            if model_mean_file_data_vals[model_mean_file_data_lead_index] == "--":
                                 model_mean_data[0,vt] = np.nan
                            else:
                                model_mean_data[0,vt] = float(model_mean_file_data_vals[model_mean_file_data_lead_index])
                            if model_mean_file_data_ovals[model_mean_file_data_lead_index] == "--":
                                model_mean_data[1,vt] = np.nan
                            else:
                                model_mean_data[1,vt] = float(model_mean_file_data_ovals[model_mean_file_data_lead_index])
                    else:
                        model_mean_file_data_leads = model_mean_file_data.loc[:]['LEADS'].tolist()
                        model_mean_file_data_vals = model_mean_file_data.loc[:]['VALS'].tolist()
                        if lead in model_mean_file_data_leads:
                            model_mean_file_data_lead_index = model_mean_file_data_leads.index(lead)
                            if model_mean_file_data_vals[model_mean_file_data_lead_index] == "--":
                                model_mean_data[vt] = np.nan
                            else:
                                model_mean_data[vt] = float(model_mean_file_data_vals[model_mean_file_data_lead_index])
            else:
                logger.warning("Model "+str(model_num)+" "
                               +model_name+" with plot name "
                               +model_plot_name+" file: "
                               +model_mean_file+" does not exist")
        model_mean_data = np.ma.masked_invalid(model_mean_data)
        if model_num == 1:
            fig, (ax1, ax2) = plt.subplots(2, 1,
                                           figsize=(x_figsize, y_figsize),
                                           sharex=True)
            ax1.grid(True)
            ax1.set_xticks(fcst_var_thresh_counts)
            ax1.set_xlim([fcst_var_thresh_counts[0], fcst_var_thresh_counts[-1]])
            #ax1.set_xticklabels(fcst_var_thresh_val_list)
            #ax1.set_xticklabels(fcst_var_thresh_list)
            ax1.set_ylabel("Mean")
            ax2.grid(True)
            ax2.set_xlabel("Forecast Threshold")
            ax2.set_xticks(fcst_var_thresh_counts)
            ax2.set_xlim([fcst_var_thresh_counts[0], fcst_var_thresh_counts[-1]])
            ax2.set_xticklabels(fcst_var_thresh_val_list)
            ax2.set_ylabel("Difference")
            props = {
                'boxstyle': 'square',
                'pad': 0.35,
                'facecolor': 'white',
                'linestyle': 'solid',
                'linewidth': 1,
                'edgecolor': 'black'
            }
            ax2.text(0.995, 1.05,
                     "Note: differences outside the outline bars "
                     +"are significant at the 95% confidence level",
                     ha='right',
                     va='center',
                     fontsize=13,
                     bbox=props,
                     transform=ax2.transAxes)
            ax2.plot(fcst_var_thresh_counts,
                     np.zeros_like(fcst_var_thresh_counts),
                     color='black',
                     linestyle='solid',
                     linewidth=2.0,
                     zorder=4)
            if stat == "fbar_obar":
                count = (
                    len(model_mean_data[0,:])
                     - np.ma.count_masked(model_mean_data[0,:])
                )
                mfcst_var_thresh_counts = np.ma.array(
                    fcst_var_thresh_counts,
                    mask=np.ma.getmaskarray(model_mean_data[0,:])
                )
                if count != 0:
                    ax1.plot(mfcst_var_thresh_counts.compressed(),
                             model_mean_data[0,:].compressed(),
                             color = model_plot_settings_dict['color'],
                             linestyle = model_plot_settings_dict['linestyle'],
                             linewidth = model_plot_settings_dict['linewidth'],
                             marker = model_plot_settings_dict['marker'],
                             markersize = model_plot_settings_dict['markersize'],
                             label = model_plot_name,
                             zorder = (nmodels-model_index)+4)
                    stat_min_max_dict['ax1_stat_min'] = model_mean_data[0,:].min()
                    stat_min_max_dict['ax1_stat_max'] = model_mean_data[0,:].max()
                obs_plot_settings_dict = (
                    model_obs_plot_settings_dict['obs']
                )
                obs_count = (
                    len(model_mean_data[1,:])
                     - np.ma.count_masked(model_mean_data[1,:])
                )
                mfcst_var_thresh_counts = np.ma.array(
                    fcst_var_thresh_counts,
                    mask=np.ma.getmaskarray(model_mean_data[1,:])
                )
                if obs_count != 0:
                    ax1.plot(mfcst_var_thresh_counts.compressed(),
                             model_mean_data[1,:].compressed(),
                             color = obs_plot_settings_dict['color'],
                             linestyle = obs_plot_settings_dict['linestyle'],
                             linewidth = obs_plot_settings_dict['linewidth'],
                             marker = obs_plot_settings_dict['marker'],
                             markersize = obs_plot_settings_dict['markersize'],
                             label = "obs.",
                             zorder = 4)
                    if model_mean_data[1,:].min() \
                            < stat_min_max_dict['ax1_stat_min'] \
                            or np.ma.is_masked(stat_min_max_dict['ax1_stat_min']):
                        stat_min_max_dict['ax1_stat_min'] = (
                            model_mean_data[1,:].min()
                        )
                    if model_mean_data[1,:].max() \
                            > stat_min_max_dict['ax1_stat_max'] \
                            or np.ma.is_masked(stat_min_max_dict['ax1_stat_max']):
                        stat_min_max_dict['ax1_stat_max'] = (
                            model_mean_data[1,:].max()
                        )
                ax2.set_title("Difference from obs.", loc="left")
                count = (
                    len(model_mean_data[0,:]-model_mean_data[1,:])
                     - np.ma.count_masked(
                         model_mean_data[0,:]-model_mean_data[1,:]
                     )
                )
                mfcst_var_thresh_counts = np.ma.array(
                    fcst_var_thresh_counts,
                    mask=np.ma.getmaskarray(
                        model_mean_data[0,:]-model_mean_data[1,:]
                    )
                )
                if count != 0:
                    ax2.plot(mfcst_var_thresh_counts.compressed(),
                             (model_mean_data[0,:]-model_mean_data[1,:]).compressed(),
                             color = model_plot_settings_dict['color'],
                             linestyle = model_plot_settings_dict['linestyle'],
                             linewidth = model_plot_settings_dict['linewidth'],
                             marker = model_plot_settings_dict['marker'],
                             markersize = model_plot_settings_dict['markersize'],
                             zorder = (nmodels-model_index)+4)
                    stat_min_max_dict['ax2_stat_min'] = (
                        model_mean_data[0,:]-model_mean_data[1,:]
                    ).min()
                    stat_min_max_dict['ax2_stat_max'] = (
                        model_mean_data[0,:]-model_mean_data[1,:]
                    ).max() 
                if ci_method != "NONE":
                    model_ci_data = np.empty(len(fcst_var_thresh_list))
                    model_ci_data.fill(np.nan)
                    for vt in range(len(fcst_var_thresh_format_list)):
                        fcst_var_thresh = fcst_var_thresh_format_list[vt]
                        obs_var_thresh = obs_var_thresh_format_list[vt]
                        model_ci_file = os.path.join(plotting_out_dir_data, 
                                                     model_plot_name
                                                     +"_"+stat
                                                     #+"_"+plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd
                                                     #+"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z"
                                                     #+"_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z"
                                                     +"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+fcst_var_thresh
                                                     +"_obs"+obs_var_name+obs_var_level+obs_var_extra+obs_var_thresh
                                                     +"_interp"+interp
                                                     +"_region"+region
                                                     +"_CI_"+ci_method
                                                     +".txt")
                        if os.path.exists(model_ci_file):
                            nrow = sum(1 for line in open(model_ci_file))
                            if nrow == 0:
                                logger.warning("Model "+str(model_num)+" "
                                               +model_name+" with plot name "
                                               +model_plot_name+" file: "
                                               +model_ci_file+" empty")
                            else:
                                logger.debug("Model "+str(model_num)+" "
                                             +model_name+" with plot name "
                                             +model_plot_name+" file: "
                                             +model_ci_file+" exists")
                                model_ci_file_data = pd.read_csv(model_ci_file, 
                                                                 sep=" ", 
                                                                 header=None, 
                                                                 names=ci_file_cols, 
                                                                 dtype=str)
                                model_ci_file_data_leads = model_ci_file_data.loc[:]['LEADS'].tolist()
                                model_ci_file_data_vals = model_ci_file_data.loc[:]['VALS'].tolist()
                                if lead in model_ci_file_data_leads:
                                    model_ci_file_data_lead_index = model_ci_file_data_leads.index(lead)
                                    if model_ci_file_data_vals[model_ci_file_data_lead_index] == "--":
                                        model_ci_data[vt] = np.nan
                                    else:
                                        model_ci_data[vt] = float(model_ci_file_data_vals[model_ci_file_data_lead_index])
                        else:
                            logger.warning("Model "+str(model_num)+" "
                                           +model_name+" with plot name "
                                           +model_plot_name+" file: "
                                           +model_mean_file+" does not exist")
                    model_ci_data = np.ma.masked_invalid(model_ci_data)
                    top_bar_data_max = model_ci_data.max()
                    bottom_bar_data_min = model_ci_data.max() * -1
                    if bottom_bar_data_min < stat_min_max_dict['ax2_stat_min'] \
                                or np.ma.is_masked(stat_min_max_dict['ax2_stat_min']):
                            if not np.ma.is_masked(bottom_bar_data_min):
                                stat_min_max_dict['ax2_stat_min'] = (
                                    bottom_bar_data_min
                                 )
                    if top_bar_data_max > stat_min_max_dict['ax2_stat_max'] \
                                or np.ma.is_masked(stat_min_max_dict['ax2_stat_max']):
                            if not np.ma.is_masked(top_bar_data_max):
                                stat_min_max_dict['ax2_stat_max'] = (
                                    top_bar_data_max
                                )
                    for ft in fcst_var_thresh_val_array:
                        index = np.where(fcst_var_thresh_val_array == ft)[0][0]
                        ax2.bar(fcst_var_thresh_counts[index], 2*np.absolute(model_ci_data[index]),
                                bottom = -1*np.absolute(model_ci_data[index]),
                                color = 'None',
                                width = CI_bar_max_widths-(CI_bar_intvl_widths*model_index),
                                edgecolor = model_plot_settings_dict['color'], 
                                linewidth = '1.5')
            else:
                model1_mean_data = model_mean_data
                count = (
                    len(model1_mean_data)
                     - np.ma.count_masked(model1_mean_data)
                )
                mfcst_var_thresh_counts = np.ma.array(
                    fcst_var_thresh_counts,
                    mask=np.ma.getmaskarray(model1_mean_data)
                )
                if count != 0:
                    ax1.plot(mfcst_var_thresh_counts.compressed(),
                             model1_mean_data.compressed(),
                             color = model_plot_settings_dict['color'],
                             linestyle = model_plot_settings_dict['linestyle'],
                             linewidth = model_plot_settings_dict['linewidth'],
                             marker = model_plot_settings_dict['marker'],
                             markersize = model_plot_settings_dict['markersize'],
                             label = model_plot_name,
                             zorder = (nmodels-model_index)+4)
                    stat_min_max_dict['ax1_stat_min'] = model_mean_data.min()
                    stat_min_max_dict['ax1_stat_max'] = model_mean_data.max()
                ax1_stat_max = model_mean_data.max()
                ax2.set_title("Difference from "+model_plot_name, loc="left")
        else:
            if stat == "fbar_obar":
                count = (
                    len(model_mean_data[0,:])
                     - np.ma.count_masked(model_mean_data[0,:])
                )
                mfcst_var_thresh_counts = np.ma.array(
                    fcst_var_thresh_counts,
                    mask=np.ma.getmaskarray(model_mean_data[0,:])
                )
                if count != 0:
                    ax1.plot(mfcst_var_thresh_counts.compressed(),
                             model_mean_data[0,:].compressed(),
                             color = model_plot_settings_dict['color'],
                             linestyle = model_plot_settings_dict['linestyle'],
                             linewidth = model_plot_settings_dict['linewidth'],
                             marker = model_plot_settings_dict['marker'],
                             markersize = model_plot_settings_dict['markersize'],
                             label = model_plot_name,
                             zorder = (nmodels-model_index)+4)
                    if model_mean_data[0,:].min() \
                            < stat_min_max_dict['ax1_stat_min'] \
                            or np.ma.is_masked(stat_min_max_dict['ax1_stat_min']):
                        stat_min_max_dict['ax1_stat_min'] = (
                            model_mean_data[0,:].min()
                        )
                    if model_mean_data[0,:].max() \
                            > stat_min_max_dict['ax1_stat_max'] \
                            or np.ma.is_masked(stat_min_max_dict['ax1_stat_max']):
                        stat_min_max_dict['ax1_stat_max'] = (
                            model_mean_data[0,:].max()
                        )
                count = (
                    len(model_mean_data[0,:]-model_mean_data[1,:])
                     - np.ma.count_masked(
                         model_mean_data[0,:]-model_mean_data[1,:]
                     )
                )
                mfcst_var_thresh_counts = np.ma.array(
                    fcst_var_thresh_counts,
                    mask=np.ma.getmaskarray(
                        model_mean_data[0,:]-model_mean_data[1,:]
                    )
                )
                if count != 0:
                    ax2.plot(mfcst_var_thresh_counts.compressed(),
                             (model_mean_data[0,:]-model_mean_data[1,:]).compressed(),
                             color = model_plot_settings_dict['color'],
                             linestyle = model_plot_settings_dict['linestyle'],
                             linewidth = model_plot_settings_dict['linewidth'],
                             marker = model_plot_settings_dict['marker'],
                             markersize = model_plot_settings_dict['markersize'],
                            zorder = (nmodels-model_index)+4)
                    if (model_mean_data[0,:]-model_mean_data[1,:]).min() \
                            < stat_min_max_dict['ax2_stat_min'] \
                            or np.ma.is_masked(stat_min_max_dict['ax2_stat_min']):
                        stat_min_max_dict['ax2_stat_min'] = (
                            model_mean_data[0,:]-model_mean_data[1,:]
                        ).min()
                    if (model_mean_data[0,:]-model_mean_data[1,:]).max() \
                            > stat_min_max_dict['ax2_stat_max'] \
                            or np.ma.is_masked(stat_min_max_dict['ax2_stat_max']):
                        stat_min_max_dict['ax2_stat_max'] = (
                            model_mean_data[0,:]-model_mean_data[1,:]
                        ).max()
            else:
                count = (
                    len(model_mean_data)
                     - np.ma.count_masked(model_mean_data)
                )
                mfcst_var_thresh_counts = np.ma.array(
                    fcst_var_thresh_counts,
                    mask=np.ma.getmaskarray(fcst_var_thresh_counts)
                )
                if count != 0:
                    ax1.plot(mfcst_var_thresh_counts.compressed(),
                             model_mean_data.compressed(),
                             color = model_plot_settings_dict['color'],
                             linestyle = model_plot_settings_dict['linestyle'],
                             linewidth = model_plot_settings_dict['linewidth'],
                             marker = model_plot_settings_dict['marker'],
                             markersize = model_plot_settings_dict['markersize'],
                             label = model_plot_name,
                             zorder = (nmodels-model_index)+4)
                    if model_mean_data.min() \
                            < stat_min_max_dict['ax1_stat_min'] \
                            or np.ma.is_masked(stat_min_max_dict['ax1_stat_min']):
                        stat_min_max_dict['ax1_stat_min'] = (
                            model_mean_data.min()
                        )
                    if model_mean_data.max() \
                            > stat_min_max_dict['ax1_stat_max'] \
                            or np.ma.is_masked(stat_min_max_dict['ax1_stat_max']):
                        stat_min_max_dict['ax1_stat_max'] = (
                            model_mean_data.max()
                        )
                mfcst_var_thresh_counts = np.ma.array(
                    fcst_var_thresh_counts,
                    mask=np.ma.getmaskarray(
                        model_mean_data-model1_mean_data
                    )
                )
                count = (
                    len(model_mean_data-model1_mean_data)
                     - np.ma.count_masked(model_mean_data-model1_mean_data)
                )
                if count != 0:
                    ax2.plot(mfcst_var_thresh_counts.compressed(),
                             (model_mean_data-model1_mean_data).compressed(),
                             color = model_plot_settings_dict['color'],
                             linestyle = model_plot_settings_dict['linestyle'],
                             linewidth = model_plot_settings_dict['linewidth'],
                             marker = model_plot_settings_dict['marker'],
                             markersize = model_plot_settings_dict['markersize'],
                             zorder = (nmodels-model_index)+4)
                    if (model_mean_data-model1_mean_data).min() \
                            < stat_min_max_dict['ax2_stat_min'] \
                            or np.ma.is_masked(stat_min_max_dict['ax2_stat_min']):
                        stat_min_max_dict['ax2_stat_min'] = (
                            model_mean_data-model1_mean_data
                        ).min()
                    if (model_mean_data-model1_mean_data).max() \
                            > stat_min_max_dict['ax2_stat_max'] \
                            or np.ma.is_masked(stat_min_max_dict['ax2_stat_max']):
                        stat_min_max_dict['ax2_stat_max'] = (
                            model_mean_data-model1_mean_data
                        ).max()
            if ci_method != "NONE":
                model_ci_data = np.empty(len(fcst_var_thresh_list))
                model_ci_data.fill(np.nan)
                for vt in range(len(fcst_var_thresh_format_list)):
                    fcst_var_thresh = fcst_var_thresh_format_list[vt]
                    obs_var_thresh = obs_var_thresh_format_list[vt]
                    model_ci_file = os.path.join(plotting_out_dir_data, 
                                                 model_plot_name
                                                 +"_"+stat
                                                 #+"_"+plot_time+start_date_YYYYmmdd+"to"+end_date_YYYYmmdd
                                                 #+"_valid"+valid_time_info[0]+"to"+valid_time_info[-1]+"Z"
                                                 #+"_init"+init_time_info[0]+"to"+init_time_info[-1]+"Z"
                                                 +"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+fcst_var_thresh
                                                 +"_obs"+obs_var_name+obs_var_level+obs_var_extra+obs_var_thresh
                                                 +"_interp"+interp
                                                 +"_region"+region
                                                 +"_CI_"+ci_method
                                                 +".txt")
                    if os.path.exists(model_ci_file):
                        nrow = sum(1 for line in open(model_ci_file))
                        if nrow == 0:
                            logger.warning("Model "+str(model_num)+" "
                                           +model_name+" with plot name "
                                           +model_plot_name+" file: "
                                           +model_ci_file+" empty")
                        else:
                            logger.debug("Model "+str(model_num)+" "
                                     +model_name+" with plot name "
                                     +model_plot_name+" file: "
                                     +model_ci_file+" exists")
                            model_ci_file_data = pd.read_csv(model_ci_file, 
                                                             sep=" ", 
                                                             header=None, 
                                                             names=ci_file_cols, 
                                                             dtype=str)
                            model_ci_file_data_leads = model_ci_file_data.loc[:]['LEADS'].tolist()
                            model_ci_file_data_vals = model_ci_file_data.loc[:]['VALS'].tolist()
                            if lead in model_ci_file_data_leads:
                                model_ci_file_data_lead_index = model_ci_file_data_leads.index(lead)
                                if model_ci_file_data_vals[model_ci_file_data_lead_index] == "--":
                                    model_ci_data[vt] = np.nan
                                else:
                                    model_ci_data[vt] = float(model_ci_file_data_vals[model_ci_file_data_lead_index])
                    else:
                        logger.warning("Model "+str(model_num)+" "
                                       +model_name+" with plot name "
                                       +model_plot_name+" file: "
                                       +model_mean_file+" does not exist")
                model_ci_data = np.ma.masked_invalid(model_ci_data)
                top_bar_data_max = model_ci_data.max()
                bottom_bar_data_min = model_ci_data.max() * -1
                if bottom_bar_data_min < stat_min_max_dict['ax2_stat_min'] \
                            or np.ma.is_masked(stat_min_max_dict['ax2_stat_min']):
                        if not np.ma.is_masked(bottom_bar_data_min):
                            stat_min_max_dict['ax2_stat_min'] = (
                                bottom_bar_data_min
                            )
                if top_bar_data_max > stat_min_max_dict['ax2_stat_max'] \
                            or np.ma.is_masked(stat_min_max_dict['ax2_stat_max']):
                        if not np.ma.is_masked(top_bar_data_max):
                            stat_min_max_dict['ax2_stat_max'] = (
                                top_bar_data_max
                             )
                for ft in fcst_var_thresh_val_array:
                    index = np.where(fcst_var_thresh_val_array == ft)[0][0]
                    ax2.bar(fcst_var_thresh_counts[index], 2*np.absolute(model_ci_data[index]), 
                            bottom = -1*np.absolute(model_ci_data[index]), 
                            color = 'None',
                            width = CI_bar_max_widths[index]-(CI_bar_intvl_widths[index]*model_index),
                            edgecolor = model_plot_settings_dict['color'], 
                            linewidth = '1')
    subplot_num = 1
    for ax in fig.get_axes():
       # Adjust y axis limits and ticks 
       stat_min = stat_min_max_dict['ax'+str(subplot_num)+'_stat_min']
       stat_max = stat_min_max_dict['ax'+str(subplot_num)+'_stat_max']
       preset_y_axis_tick_min = ax.get_yticks()[0]
       preset_y_axis_tick_max = ax.get_yticks()[-1]
       preset_y_axis_tick_inc = ax.get_yticks()[1] - ax.get_yticks()[0]
       if stat in ['acc', 'msess', 'ets', 'rsd'] and subplot_num == 1:
           y_axis_tick_inc = 0.1
       else:
           y_axis_tick_inc = preset_y_axis_tick_inc
       if np.ma.is_masked(stat_min):
           y_axis_min = preset_y_axis_tick_min
       else:
           if stat in ['acc', 'msess', 'ets', 'rsd'] and subplot_num == 1:
               y_axis_min = round(stat_min,1) - y_axis_tick_inc
           else:
               y_axis_min = preset_y_axis_tick_min
               while y_axis_min > stat_min:
                   y_axis_min = y_axis_min - y_axis_tick_inc
       if np.ma.is_masked(stat_max):
           y_axis_max = preset_y_axis_tick_max
       else:
           if stat in ['acc', 'msess', 'ets'] and subplot_num == 1:
               y_axis_max = 1
           elif stat in ['rsd'] and subplot_num == 1:
             y_axis_max = round(stat_max,1) + y_axis_tick_inc
           else:
               y_axis_max = preset_y_axis_tick_max
               while y_axis_max < stat_max:
                   y_axis_max = y_axis_max + y_axis_tick_inc
       ax.set_yticks(
           np.arange(y_axis_min,
                     y_axis_max+y_axis_tick_inc,
                     y_axis_tick_inc)
       )
       ax.set_ylim([y_axis_min, y_axis_max])
       # Check y axis limits
       if stat_max >= ax.get_ylim()[1]:
           while stat_max >= ax.get_ylim()[1]:
               y_axis_max = y_axis_max + y_axis_tick_inc
               ax.set_yticks(
                   np.arange(y_axis_min,
                             y_axis_max +  y_axis_tick_inc,
                             y_axis_tick_inc)
               )
               ax.set_ylim([y_axis_min, y_axis_max])
       if stat_min <= ax.get_ylim()[0]:
           while stat_min <= ax.get_ylim()[0]:
               y_axis_min = y_axis_min - y_axis_tick_inc
               ax.set_yticks(
                   np.arange(y_axis_min,
                             y_axis_max +  y_axis_tick_inc,
                             y_axis_tick_inc)
               )
               ax.set_ylim([y_axis_min, y_axis_max])
       subplot_num+=1
    # Add legend, adjust if points in legend
    if len(ax1.lines) != 0:
        y_axis_tick_min = ax1.get_yticks()[0]
        y_axis_tick_max = ax1.get_yticks()[-1]
        y_axis_tick_inc = ax1.get_yticks()[1] - ax1.get_yticks()[0]
        stat_min = stat_min_max_dict['ax1_stat_min']
        stat_max = stat_min_max_dict['ax1_stat_max']
        legend = ax1.legend(bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                            loc=legend_loc, ncol=legend_ncol,
                            fontsize=legend_fontsize)
        plt.draw()
        legend_box = legend.get_window_extent() \
            .inverse_transformed(ax1.transData)
        y_axis_min = y_axis_tick_min
        y_axis_max = y_axis_tick_max
        if stat_min < legend_box.y1:
            while stat_min < legend_box.y1:
                y_axis_min = y_axis_min - y_axis_tick_inc
                ax1.set_yticks(
                    np.arange(y_axis_min,
                              y_axis_max + y_axis_tick_inc,
                              y_axis_tick_inc)
                )
                ax1.set_ylim([y_axis_min, y_axis_max])
                legend = ax1.legend(
                    bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                    loc=legend_loc, ncol=legend_ncol,
                    fontsize=legend_fontsize
                )
                plt.draw()
                legend_box = (
                    legend.get_window_extent() \
                    .inverse_transformed(ax1.transData)
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
        fcst_var_name, fcst_var_level, fcst_var_extra, 'all'
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
    ax1.set_title(full_title, loc=title_loc)
    fig.figimage(noaa_logo_img_array,
                 noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
                 zorder=1, alpha=noaa_logo_alpha)
    fig.figimage(nws_logo_img_array,
                 nws_logo_xpixel_loc, nws_logo_ypixel_loc,
                 zorder=1, alpha=nws_logo_alpha)
    # Build savefig name
    if plot_time == 'valid':
        if verif_case == 'precip':
            savefig_name = os.path.join(plotting_out_dir_imgs,
                                        stat
                                        +"_valid"+valid_time_info[0][0:2]+"Z"
                                        +"_"+fcst_var_name+"_"+fcst_var_level+"_all"
                                        +"_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
    elif plot_time == 'init':
        if verif_case == 'precip':
            savefig_name = os.path.join(plotting_out_dir_imgs,
                                        stat
                                        +"_init"+init_time_info[0][0:2]+"Z"
                                        +"_"+fcst_var_name+"_"+fcst_var_level+"_all"
                                        +"_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
    logger.info("Saving image as "+savefig_name)
    plt.savefig(savefig_name)
    plt.close()
