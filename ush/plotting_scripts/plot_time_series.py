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
plt.rcParams['figure.subplot.top'] = 0.85
plt.rcParams['figure.subplot.bottom'] = 0.15
plt.rcParams['legend.handletextpad'] = 0.25
plt.rcParams['legend.handlelength'] = 1.25
plt.rcParams['legend.borderaxespad'] = 0
plt.rcParams['legend.columnspacing'] = 1.0
plt.rcParams['legend.frameon'] = False
x_figsize, y_figsize = 14, 7
legend_bbox_x, legend_bbox_y = 0.5, 0.05
legend_fontsize = 13
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
    'model8': {'color': '#332288',
               'marker': 'D', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model9': {'color': '#AA4499',
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
noaa_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.865
noaa_logo_alpha = 0.5
nws_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'nws.png')
)
nws_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.9
nws_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.865
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
if verif_case == "precip":
    average_method = "AGGREGATION"
else:
    average_method = "MEAN"
ci_method = os.environ['CI_METHOD']
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
plot_time_dates, expected_stat_file_dates = plot_util.get_date_arrays(plot_time, 
                                                                      start_date_YYYYmmdd, 
                                                                      end_date_YYYYmmdd, 
                                                                      valid_time_info, 
                                                                      init_time_info, 
                                                                      lead)
total_days = len(plot_time_dates)
stat_file_base_columns = plot_util.get_stat_file_base_columns(met_version)

# Read and plot data
logger.info("Reading in model data")
for model in model_info:
    model_num = model_info.index(model) + 1
    model_name= model[0]
    model_plot_name = model[1]
    if ci_method == "EMC_MONTE_CARLO":
        randx_model = np.loadtxt(
            os.path.join(plotting_out_dir_data, 
                         model_plot_name+"_randx.txt")
        )
    else:
        ntests = 10000
        randx_model = np.ones((ntests, total_days)) * np.nan
    randx_model = np.array([randx_model])
    if model_num == 1:
        randx = randx_model
    else:
        randx = np.append(randx, randx_model, axis=0)
    model_data_now_index = pd.MultiIndex.from_product(
        [[model_plot_name], expected_stat_file_dates],
        names=['model_plot_name', 'dates']
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
            model_now_data = pd.DataFrame(np.nan, 
                                          index=model_data_now_index, 
                                          columns=[ 'TOTAL' ])
        else:
            logger.info("Model "+str(model_num)+" "
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
            model_now_stat_file_data_fcst_valid_dates = (
                model_now_stat_file_data.loc[:]['FCST_VALID_BEG'].values
            )
            model_now_data = pd.DataFrame(np.nan, 
                                          index=model_data_now_index, 
                                          columns=stat_file_line_type_columns)
            for expected_date in expected_stat_file_dates:
                if expected_date in model_now_stat_file_data_fcst_valid_dates:
                     matching_date_index = model_now_stat_file_data_fcst_valid_dates.tolist().index(expected_date)
                     model_now_stat_file_data_indexed = model_now_stat_file_data.loc[matching_date_index][:]
                     for column in stat_file_line_type_columns:
                         if fcst_var_name == 'PRMSL' or (fcst_var_name == 'PRES' and fcst_var_level == 'Z0'):
                             if column in ['FBAR', 'OBAR']:
                                 model_now_data.loc[(model_plot_name, expected_date)][column] = (
                                     model_now_stat_file_data_indexed.loc[:][column]/100.
                                 )
                             elif column in ['FFBAR', 'FOBAR', 'OOBAR']:
                                 model_now_data.loc[(model_plot_name, expected_date)][column] = (
                                     model_now_stat_file_data_indexed.loc[:][column]/(100.*100.)
                                 )
                             else:
                                 model_now_data.loc[(model_plot_name, expected_date)][column] = (
                                     model_now_stat_file_data_indexed.loc[:][column]
                                 )
                         else:
                             model_now_data.loc[(model_plot_name, expected_date)][column] = (
                                 model_now_stat_file_data_indexed.loc[:][column]
                             )
    else:
        logger.warning("Model "+str(model_num)+" "
                       +model_name+" with plot name "
                       +model_plot_name+" file: "
                       +model_stat_file+" does not exist")
        model_now_data = pd.DataFrame(np.nan, 
                                      index=model_data_now_index,
                                      columns=[ 'TOTAL' ])
    if model_num > 1:
        model_data = pd.concat([model_data, model_now_data])
    else:
        model_data = model_now_data

nmodels = len(model_info)
logger.info("Calculating and plotting statistics")
for stat in plot_stats_list:
    logger.debug("Working on "+stat)
    stat_values, stat_values_array, stat_plot_name = plot_util.calculate_stat(logger, 
                                                                              model_data, 
                                                                              stat)
    if event_equalization == "True":
        logger.debug("Doing event equalization")
        if stat == "fbar_obar":
            stat_values_array[0,:,:] = np.ma.mask_cols(stat_values_array[0,:,:])
            stat_values_array[1,:,:] = np.ma.mask_cols(stat_values_array[1,:,:])
            stat_values_array4avg = stat_values_array
        else:
            stat_values_array = np.ma.mask_cols(stat_values_array)
            stat_values_array4avg = np.ma.array([stat_values_array])
    else:
        if stat == "fbar_obar":
            stat_values_array4avg = stat_values_array
        else:
            stat_values_array4avg = np.ma.array([stat_values_array])
    stat_min = np.ma.masked_invalid(np.nan)
    stat_max = np.ma.masked_invalid(np.nan)
    for model in model_info:
        model_num = model_info.index(model) + 1
        model_index = model_info.index(model)
        model_name = model[0]
        model_plot_name = model[1]
        model_plot_settings_dict = (
            model_obs_plot_settings_dict['model'+str(model_num)]
        )
        if stat == "fbar_obar":
            model_stat_values_array = stat_values_array[0,model_index,:]
            obs_stat_values_array = stat_values_array[1,model_index,:]
        else:
            model_stat_values_array = stat_values_array[model_index,:]
        lead_mean_filename = os.path.join(plotting_out_dir_data, 
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
        logger.debug("Writing model "+str(model_num)+" "
                     +model_name+" with name on plot "
                     +model_plot_name+" lead "+lead
                     +" mean to file: "
                     +lead_mean_filename)
        model_stat_average_array = plot_util.calculate_average(
                logger, average_method, stat, model_data.loc[[model_plot_name]],
                stat_values_array4avg[:,model_index,:]
        )
        with open(lead_mean_filename, 'a') as lead_mean_file:
            lead_mean_file.write(lead)
            for l in range(len(model_stat_average_array)):
                lead_mean_file.write(
                    ' '+str(model_stat_average_array[l])
                )
            lead_mean_file.write('\n')
        if ci_method == "NONE":
            logger.debug("Not calculating confidence intervals")
        else:
            CI_filename = os.path.join(plotting_out_dir_data,
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
            if stat == "fbar_obar":
                if ci_method == 'EMC_MONTE_CARLO':
                    logger.warning("Monte Carlo resampling not "
                                   +"done for fbar_obar")
                    stat_CI = '--'
                else:
                    stat_CI = plot_util.calculate_ci(logger, 
                                                     ci_method, 
                                                     model_stat_values_array, 
                                                     obs_stat_values_array, 
                                                     total_days,
                                                     stat, average_method,
                                                     randx[model_index,:,:])
                logger.debug("Writing "+ci_method
                             +" confidence intervals for difference between model "
                             +str(model_num)+" "+model_name+" with name on plot "
                             +model_plot_name+" and the observations at lead "
                             +lead+" to file: "+CI_filename)
                with open(CI_filename, 'a') as CI_file:
                    CI_file.write(lead+' '+str(stat_CI)+ '\n')
            else:
                if model_num == 1:
                    model1_stat_values_array = model_stat_values_array
                    model1_plot_name = model_plot_name
                    model1_name = model_name
                elif model_num > 1:
                    if ci_method == "EMC_MONTE_CARLO":
                        stat_CI = plot_util.calculate_ci(logger,
                                                         ci_method,
                                                         model_data.loc[[model_plot_name]],
                                                         model_data.loc[[model1_plot_name]],
                                                         total_days,
                                                         stat, average_method,
                                                         randx[model_index,:,:])
                    else:
                        stat_CI = plot_util.calculate_ci(logger, 
                                                         ci_method, 
                                                         model_stat_values_array, 
                                                         model1_stat_values_array, 
                                                         total_days,
                                                         stat, average_method, 
                                                         randx[model_index,:,:])
                    logger.debug("Writing "+ci_method
                                 +" confidence intervals for difference between model "
                                 +str(model_num)+" "+model_name+" with name on plot "
                                 +model_plot_name+" and model 1 "+model1_name
                                 +" with name on plot "+model1_plot_name+" at lead "+lead
                                 +" to file: "+CI_filename)
                    with open(CI_filename, 'a') as CI_file:
                        CI_file.write(lead+' '+str(stat_CI)+ '\n')
        logger.debug("Plotting model "+str(model_num)+" "
                     +model_name+" with name on plot "
                     +model_plot_name)
        if model_num == 1:
            fig, ax = plt.subplots(1,1,figsize=(x_figsize, y_figsize))
            ax.grid(True)
            ax.set_xlabel(plot_time.title()+" Date")
            ax.set_xlim([plot_time_dates[0],plot_time_dates[-1]])
            if len(plot_time_dates) <= 3:
                day_interval = 1
            elif len(plot_time_dates) > 3 and len(plot_time_dates) <= 10:
                day_interval = 2
            elif len(plot_time_dates) > 10 and len(plot_time_dates) <= 31:
                day_interval = 7 
            elif len(plot_time_dates) > 31 and len(plot_time_dates) < 60:
                day_interval = 10
            else:
                day_interval = 30
            ax.xaxis.set_major_locator(md.DayLocator(interval=day_interval))
            ax.xaxis.set_major_formatter(md.DateFormatter('%d%b%Y'))
            ax.xaxis.set_minor_locator(md.DayLocator())
            ax.set_ylabel(stat_plot_name)
            if stat == "fbar_obar":
                obs_plot_settings_dict = (
                    model_obs_plot_settings_dict['obs']
                )
                obs_count = (len(obs_stat_values_array) 
                             - np.ma.count_masked(obs_stat_values_array))
                mplot_time_dates = np.ma.array(
                    plot_time_dates,
                    mask=np.ma.getmaskarray(obs_stat_values_array)
                )
                if obs_count != 0:
                    if np.abs(obs_stat_values_array.mean()) >= 10:
                        obs_mean_for_label = round(obs_stat_values_array.mean(), 2)
                        obs_mean_for_label = format(obs_mean_for_label, '.2f')
                    else:
                        obs_mean_for_label = round(obs_stat_values_array.mean(), 3)
                        obs_mean_for_label = format(obs_mean_for_label, '.3f')
                    ax.plot_date(mplot_time_dates.compressed(),
                                 obs_stat_values_array.compressed(),
                                 color = obs_plot_settings_dict['color'],
                                 linestyle = obs_plot_settings_dict['linestyle'],
                                 linewidth = obs_plot_settings_dict['linewidth'],
                                 marker = obs_plot_settings_dict['marker'], 
                                 markersize = obs_plot_settings_dict['markersize'],
                                 label=('obs. '
                                        +str(obs_mean_for_label)
                                        +' '+str(obs_count)+' days'),
                                 zorder=4)
                    if obs_stat_values_array.min() < stat_min or np.ma.is_masked(stat_min):
                        stat_min = obs_stat_values_array.min()
                    if obs_stat_values_array.max() > stat_max or np.ma.is_masked(stat_max):
                        stat_max = obs_stat_values_array.max()
        count = (
            len(model_stat_values_array)
            - np.ma.count_masked(model_stat_values_array)
        )
        mplot_time_dates = np.ma.array(
            plot_time_dates, mask=np.ma.getmaskarray(model_stat_values_array)
        )
        if count != 0:
            if np.abs(model_stat_values_array.mean()) >= 10:
                mean_for_label = round(model_stat_values_array.mean(), 2)
                mean_for_label = format(mean_for_label, '.2f')
            else:
                mean_for_label = round(model_stat_values_array.mean(), 3)
                mean_for_label = format(mean_for_label, '.3f')
            ax.plot_date(mplot_time_dates.compressed(),
                         model_stat_values_array.compressed(),
                         color = model_plot_settings_dict['color'], 
                         linestyle = model_plot_settings_dict['linestyle'], 
                         linewidth = model_plot_settings_dict['linewidth'], 
                         marker = model_plot_settings_dict['marker'], 
                         markersize = model_plot_settings_dict['markersize'], 
                         label=(model_plot_name
                                +' '+str(mean_for_label)
                                +' '+str(count)+' days'),
                         zorder=(nmodels-model_index)+4)
            if model_stat_values_array.min() < stat_min or np.ma.is_masked(stat_min):
                stat_min = model_stat_values_array.min()
            if model_stat_values_array.max() > stat_max or np.ma.is_masked(stat_max):
                stat_max = model_stat_values_array.max()
    # Adjust y axis limits and ticks
    preset_y_axis_tick_min = ax.get_yticks()[0]
    preset_y_axis_tick_max = ax.get_yticks()[-1]
    preset_y_axis_tick_inc = ax.get_yticks()[1] - ax.get_yticks()[0]
    if stat in ['acc', 'msess', 'ets', 'rsd']:
        y_axis_tick_inc = 0.1
    else:
        y_axis_tick_inc = preset_y_axis_tick_inc
    if np.ma.is_masked(stat_min):
        y_axis_min = preset_y_axis_tick_min
    else:
        if stat in ['acc', 'msess', 'ets', 'rsd']:
            y_axis_min = round(stat_min,1) - y_axis_tick_inc
        else:
            y_axis_min = preset_y_axis_tick_min
            while y_axis_min > stat_min:
                y_axis_min = y_axis_min - y_axis_tick_inc
    if np.ma.is_masked(stat_max):
        y_axis_max = preset_y_axis_tick_max
    else:
        if stat in ['acc', 'msess', 'ets']:
            y_axis_max = 1
        elif stat in ['rsd']:
             y_axis_max = round(stat_max,1) + y_axis_tick_inc
        else:
            y_axis_max = preset_y_axis_tick_max + y_axis_tick_inc
            while y_axis_max < stat_max:
                y_axis_max = y_axis_max + y_axis_tick_inc
    ax.set_yticks(
        np.arange(y_axis_min, y_axis_max+y_axis_tick_inc, y_axis_tick_inc)
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
    # Add legend, adjust if points in legend
    if len(ax.lines) != 0:
        legend = ax.legend(bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                           loc=legend_loc, ncol=legend_ncol,
                           fontsize=legend_fontsize)
        plt.draw()
        legend_box = legend.get_window_extent() \
            .inverse_transformed(ax.transData)
        if stat_min < legend_box.y1:
            while stat_min < legend_box.y1:
                y_axis_min = y_axis_min - y_axis_tick_inc
                ax.set_yticks(
                    np.arange(y_axis_min,
                              y_axis_max + y_axis_tick_inc,
                              y_axis_tick_inc)
                )
                ax.set_ylim([y_axis_min, y_axis_max])
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
                                        +"_"+fcst_var_name+"_"+fcst_var_level
                                        +"_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
        elif verif_case == 'precip':
            savefig_name = os.path.join(plotting_out_dir_imgs,
                                        stat
                                        +"_valid"+valid_time_info[0][0:2]+"Z"
                                        +"_"+fcst_var_name+"_"+fcst_var_level+"_"+fcst_var_thresh
                                        +"_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
        else:
            savefig_name = os.path.join(plotting_out_dir_imgs, 
                                        stat
                                        +"_valid"+valid_time_info[0][0:2]+"Z"
                                        +"_"+fcst_var_name+"_"+fcst_var_level
                                        +"_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
    elif plot_time == 'init':
        if verif_case == 'grid2obs':
            savefig_name = os.path.join(plotting_out_dir_imgs,
                                        stat
                                        +"_valid"+valid_time_info[0][0:2]+"Z"
                                        +"_"+fcst_var_name+"_"+fcst_var_level
                                        +"_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
        elif verif_case == 'precip':
            savefig_name = os.path.join(plotting_out_dir_imgs,
                                        stat
                                        +"_init"+init_time_info[0][0:2]+"Z"
                                        +"_"+fcst_var_name+"_"+fcst_var_level+"_"+fcst_var_thresh
                                        +"_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
        else:
            savefig_name = os.path.join(plotting_out_dir_imgs, 
                                        stat
                                        +"_init"+init_time_info[0][0:2]+"Z"
                                        +"_"+fcst_var_name+"_"+fcst_var_level
                                        +"_fhr"+lead
                                        +"_"+gridregion
                                        +".png")
    logger.info("Saving image as "+savefig_name)
    plt.savefig(savefig_name)
    plt.close()
