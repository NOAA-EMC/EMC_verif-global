from __future__ import (print_function, division)
import sys
import os
import numpy as np
import netCDF4 as netcdf
import re
import maps2d_plot_util as maps2d_plot_util
import warnings
import logging
import datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
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
title_loc = 'center'
cmap_diff_original = plt.cm.bwr
colors_diff = cmap_diff_original(
    np.append(np.linspace(0,0.425,10), np.linspace(0.575,1,10))
)
cmap_diff = matplotlib.colors.LinearSegmentedColormap.from_list(
    'cmap_diff', colors_diff
)
noaa_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'noaa.png')
)
noaa_logo_alpha = 0.5
nws_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'nws.png')
)
nws_logo_alpha = 0.5

# Functions
def read_series_analysis_file(series_analysis_file, var_scale):
    print(series_analysis_file+" exists")
    series_analysis_data = netcdf.Dataset(series_analysis_file)
    series_analysis_data_lat = series_analysis_data.variables['lat'][:]
    series_analysis_data_lon = series_analysis_data.variables['lon'][:]
    series_analysis_data_variable_names = []
    for var in series_analysis_data.variables:
        series_analysis_data_variable_names.append(str(var))
    if 'series_cnt_FBAR' in series_analysis_data_variable_names:
        series_analysis_data_series_cnt_FBAR =  (
            series_analysis_data.variables['series_cnt_FBAR'][:] * var_scale
        )
    else:
        print("WARNING: FBAR values not in file "+series_analysis_file
              +"...setting to NaN")
        series_analysis_data_series_cnt_FBAR = np.full(
            (len(series_analysis_data_lat), len(series_analysis_data_lon)),
            np.nan
        )
    if np.ma.is_masked(series_analysis_data_series_cnt_FBAR):
        np.ma.set_fill_value(series_analysis_data_series_cnt_FBAR, np.nan)
        series_analysis_data_series_cnt_FBAR = (
            series_analysis_data_series_cnt_FBAR.filled()
        )
    if 'series_cnt_OBAR' in series_analysis_data_variable_names:
        series_analysis_data_series_cnt_OBAR =  (
            series_analysis_data.variables['series_cnt_OBAR'][:] * var_scale
        )
    else:
        print("WARNING: OBAR values not in file "+series_analysis_file
              +"...setting to NaN")
        series_analysis_data_series_cnt_OBAR = np.full(
            (len(series_analysis_data_lat), len(series_analysis_data_lon)),
            np.nan
        )
    if np.ma.is_masked(series_analysis_data_series_cnt_OBAR):
        np.ma.set_fill_value(series_analysis_data_series_cnt_OBAR, np.nan)
        series_analysis_data_series_cnt_OBAR = (
            series_analysis_data_series_cnt_OBAR.filled()
        )
    return (series_analysis_data_series_cnt_FBAR,
            series_analysis_data_series_cnt_OBAR,
            series_analysis_data_lat, series_analysis_data_lon)

def draw_subplot_map(subplot_num, subplot_title, nsubplots, latlon_area,
                     var_levels):
    """ Draw map for subplot.

            Args:
                subplot_num   - integer of the subplot
                                location number
                subplot_title - string of the title for
                                subplot
                nsubplots     - integer of the number
                                of total subplots in
                                image
                latlon_area   - list of the bounding
                                latitudes and longitudes
                                for the map
                var_levels    - list of variables pressure
                                levels
           Returns:
                ax_tmp     -    subplot axis object
    """
    llcrnrlat_val = float(latlon_area[0])
    urcrnrlat_val = float(latlon_area[1])
    lat_ticks = np.linspace(llcrnrlat_val, urcrnrlat_val, 7, endpoint=True)
    ax_tmp = plt.subplot(gs[subplot_num])
    ax_tmp.set_xticks(lat_ticks)
    ax_tmp.set_yscale("log")
    ax_tmp.invert_yaxis()
    ax_tmp.minorticks_off()
    ax_tmp.set_yticks(np.asarray(var_levels, dtype=float))
    ax_tmp.set_yticklabels(var_levels)
    if ax_tmp.is_last_row() or \
            (nsubplots % 2 != 0 and subplot_num == nsubplots - 2):
       ax_tmp.set_xlabel('Latitude')
    else:
        plt.setp(ax_tmp.get_xticklabels(), visible=False)
    if ax_tmp.is_first_col():
        ax_tmp.set_ylabel('Pressure Level (hPa)')
    else:
        plt.setp(ax_tmp.get_yticklabels(), visible=False)
    ax_tmp.set_aspect('auto')
    ax_tmp.set_title(subplot_title, loc='left')
    return ax_tmp

def plot_subplot_data(ax_tmp, plot_data, plot_data_lat, plot_data_levels,
                      plot_levels, plot_cmap, latlon_area):
    """ Plot data for subplot.

            Args:
                ax_tmp           - subplot axis object
                plot_data        - array of the data to plot
                plot_data_lat    - array of the data latitudes
                plot_data_levels - array of the data levels
                plot_levels      - array of the contour levels
                plot_cmap        - string of the colormap to use
                latlon_area      - list of the bounding
                                   latitudes and longitudes
                                   for the map
           Returns:
                CF_tmp           -    subplot contour fill object
    """
    llcrnrlat_val = float(latlon_area[0])
    urcrnrlat_val = float(latlon_area[1])
    # Get plotting levels, if needed
    if np.all(np.isnan(plot_levels)):
        if np.isnan(np.nanmax(plot_data)):
            levels_max = 1
        else:
            levels_max = (
                np.nanmax(plot_data)
                + np.abs((0.01 * np.nanmax(plot_data)))
            )
        if np.isnan(np.nanmin(plot_data)):
            levels_min = -1
        else:
            levels_min = (
                np.nanmin(plot_data)
                - np.abs((0.01 * np.nanmin(plot_data)))
            )
        if np.abs(levels_max) > 1 and np.abs(levels_max) < 100:
            levels_max = round(levels_max, 0)
        elif np.abs(levels_max) > 100:
            levels_max = round(levels_max, -1)
        else:
            levels_max = round(levels_max, 2)
        if np.abs(levels_min) > 1 and np.abs(levels_min) < 100:
            levels_min = round(levels_min, 0)
        elif np.abs(levels_min) > 100:
            levels_min = round(levels_min, -1)
        else:
            levels_min = round(levels_min, 2)
        plot_levels = np.linspace(levels_min, levels_max, 11, endpoint=True)
    if not np.all(np.diff(plot_levels) > 0):
        plot_levels = np.linspace(0, 1, 11, endpoint=True)
    # Plot model data
    x, y = np.meshgrid(plot_data_lat, plot_data_levels)
    if np.count_nonzero(~np.isnan(plot_data)) != 0:
        CF_tmp = ax_tmp.contourf(
            x, y, plot_data,
            levels=plot_levels, cmap=plot_cmap, extend='both'
        )
        if ax_tmp.rowNum == 0 and ax_tmp.colNum == 0:
            C_tmp = ax_tmp.contour(
                x, y, plot_data,
                levels=plot_levels, colors='k', linewidths=1.0, extend='both'
            )
            C_tmp_labels_list = []
            for level in C_tmp.levels:
                if str(level).split('.')[1] == '0':
                    C_tmp_labels_list.append(str(int(level)))
                else:
                    C_tmp_labels_list.append(
                        str(round(level,3)).rstrip('0')
                    )
            fmt = {}
            for lev, label in zip(C_tmp.levels, C_tmp_labels_list):
                fmt[lev] = label
            ax_tmp.clabel(C_tmp, C_tmp.levels,
                         fmt=fmt,
                         inline=True,
                         fontsize=12.5,
                         color='k')
    else:
        CF_tmp = None
    return CF_tmp

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']
START_DATE = os.environ['START_DATE']
END_DATE = os.environ['END_DATE']
forecast_to_plot = os.environ['forecast_to_plot']
hour_beg = os.environ['hour_beg']
hour_end = os.environ['hour_end']
hour_inc = os.environ['hour_inc']
regrid_to_grid = os.environ['regrid_to_grid']
latlon_area = os.environ['latlon_area'].split(' ')
var_group = os.environ['var_group']
var_name = os.environ['var_name']
var_levels = os.environ['var_levels'].split(', ')
forecast_anl_diff = os.environ['forecast_anl_diff']
RUN_type = os.environ['RUN_type']

# Set up information
if forecast_to_plot == 'anl':
    forecast_anl_diff = 'NO'
env_var_model_list = []
regex = re.compile(r'model(\d+)$')
for key in os.environ.keys():
    result = regex.match(key)
    if result is not None:
        env_var_model_list.append(result.group(0))
env_var_model_list = sorted(env_var_model_list, key=lambda m: m[-1])
nmodels = len(env_var_model_list)
make_met_data_by_hrs = []
hr = int(hour_beg) * 3600
while hr <= int(hour_end)*3600:
    make_met_data_by_hrs.append(str(int(hr/3600)).zfill(2)+'Z')
    hr+=int(hour_inc)
make_met_data_by_hrs_title = ', '.join(make_met_data_by_hrs)
if forecast_to_plot == 'anl':
    forecast_to_plot_title = 'analysis'
elif forecast_to_plot[0] == 'f':
    forecast_to_plot_title = 'forecast hour '+forecast_to_plot[1:]
elif forecast_to_plot[0] == 'd':
    forecast_day = int(forecast_to_plot[1:])
    forecast_day_fhr4 = forecast_day * 24
    forecast_day_fhr3 = str(forecast_day_fhr4 - 6).zfill(2)
    forecast_day_fhr2 = str(forecast_day_fhr4 - 12).zfill(2)
    forecast_day_fhr1 = str(forecast_day_fhr4 - 18).zfill(2)
    forecast_day_fhr4 = str(forecast_day_fhr4).zfill(2)
    forecast_to_plot_title = (
        'forecast hours '+forecast_day_fhr1+', '+forecast_day_fhr2+', '
        +forecast_day_fhr3+', '+forecast_day_fhr4
    )
START_DATE_dt = datetime.datetime.strptime(START_DATE, '%Y%m%d')
END_DATE_dt = datetime.datetime.strptime(END_DATE, '%Y%m%d')
dates_title = (make_met_data_by.lower()+' '
               +START_DATE_dt.strftime('%d%b%Y')+'-'
               +END_DATE_dt.strftime('%d%b%Y'))
nvar_levels = len(var_levels)
var_level_num_list = []
for var_level in var_levels:
    var_level_num_list.append(var_level.replace('hPa', ''))
var_levels_num = np.asarray(var_level_num_list, dtype=float)

# Get input and output directories
series_analysis_file_dir = os.path.join(DATA, RUN, 'metplus_output',
                                        'make_met_data_by_'+make_met_data_by,
                                        'series_analysis', RUN_type,
                                        var_group)
plotting_out_dir_imgs = os.path.join(DATA, RUN, 'metplus_output',
                                     'plot_by_'+plot_by,
                                     RUN_type, var_group,
                                     'imgs')
if not os.path.exists(plotting_out_dir_imgs):
    os.makedirs(plotting_out_dir_imgs)

# Build data array for all models for all levels
print("Working on zonal mean error plots for "+var_name)
model_num = 0
for env_var_model in env_var_model_list:
    model_num+=1
    model = os.environ[env_var_model]
    var_level_num = 0
    for var_level in var_levels:
        var_level_num+=1
        var_info_title, levels, levels_diff, cmap, var_scale, cbar00_title = (
            maps2d_plot_util.get_maps2d_plot_settings(var_name, var_level)
        )
        model_series_analysis_netcdf_file = os.path.join(
            series_analysis_file_dir, model,
            forecast_to_plot+'_'+var_name+'_'
            +var_level.replace(' ', '')+'.nc'
        )
        if os.path.exists(model_series_analysis_netcdf_file):
            (model_data_series_cnt_FBAR, model_data_series_cnt_OBAR,
             model_data_lat, model_data_lon) = (
                read_series_analysis_file(model_series_analysis_netcdf_file,
                                          var_scale)
            )
            if not 'model_var_levels_zonalmean_FBAR' in locals():
                model_var_levels_zonalmean_FBAR = np.ones(
                    [nmodels, nvar_levels, len(model_data_lat)]
                ) * np.nan
            if not 'model_var_levels_zonalmean_OBAR' in locals():
                model_var_levels_zonalmean_OBAR = np.ones(
                    [nmodels, nvar_levels, len(model_data_lat)]
                ) * np.nan
            model_var_levels_zonalmean_FBAR[model_num-1,var_level_num-1,:] = (
                model_data_series_cnt_FBAR.mean(axis=1)
            )
            model_var_levels_zonalmean_OBAR[model_num-1,var_level_num-1,:] = (
                model_data_series_cnt_OBAR.mean(axis=1)
            )
        else:
            print("WARNING: "+model_series_analysis_netcdf_file+" "
                  +"does not exist")
# Set up plot
if RUN_type == 'model2obs':
    nsubplots = nmodels + 1
elif RUN_type == 'model2model':
    if forecast_anl_diff == 'YES':
        nsubplots = nmodels * 2
    else:
        nsubplots = nmodels
if nsubplots == 1:
    x_figsize, y_figsize = 14, 7
    row, col = 1, 1
    hspace, wspace = 0, 0
    bottom, top = 0.175, 0.825
    suptitle_y_loc = 0.92125
    noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.865
    nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.865
    cbar_bottom = 0.06
    cbar_height = 0.02
elif nsubplots == 2:
    x_figsize, y_figsize = 14, 7
    row, col = 1, 2
    hspace, wspace = 0, 0.1
    bottom, top = 0.175, 0.825
    suptitle_y_loc = 0.92125
    noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.865
    nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.865
    cbar_width_vert = 0.01
    cbar_bottom = 0.06
    cbar_height = 0.02
elif nsubplots > 2 and nsubplots <= 4:
    x_figsize, y_figsize = 14, 14
    row, col = 2, 2
    hspace, wspace = 0.15, 0.1
    bottom, top = 0.125, 0.9
    suptitle_y_loc = 0.9605
    noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
    nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
    cbar_bottom = 0.03
    cbar_height = 0.02
elif nsubplots > 4 and nsubplots <= 6:
    x_figsize, y_figsize = 14, 14
    row, col = 3, 2
    hspace, wspace = 0.15, 0.1
    bottom, top = 0.125, 0.9
    suptitle_y_loc = 0.9605
    noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
    nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
    cbar_bottom = 0.03
    cbar_height = 0.02
elif nsubplots > 6 and nsubplots <= 8:
    x_figsize, y_figsize = 14, 14
    row, col = 4, 2
    hspace, wspace = 0.175, 0.1
    bottom, top = 0.125, 0.9
    suptitle_y_loc = 0.9605
    noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
    nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
    cbar_bottom = 0.03
    cbar_height = 0.02
elif nsubplots > 8 and nsubplots <= 10:
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
    logger.error("Too many subplots selected, max. is 10")
    sys.exit(1)
suptitle_x_loc = (
    plt.rcParams['figure.subplot.left']
    +plt.rcParams['figure.subplot.right']
)/2.
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
model_num = 0
subplot_CF_dict = {}
for env_var_model in env_var_model_list:
    model_num+=1
    model = os.environ[env_var_model]
    model_obtype = os.environ[env_var_model+'_obtype']
    model_plot_name = os.environ[env_var_model+'_plot_name']
    # Set up observation subplot map and title, if needed
    if RUN_type == 'model2obs' and model_num == 1:
        obs_subplot_num = 0
        obs_subplot_title = maps2d_plot_util.get_obs_subplot_title(
            model_obtype, use_monthly_mean
        )
        ax_obs = draw_subplot_map(
            obs_subplot_num, obs_subplot_title, nsubplots, latlon_area,
            var_level_num_list
        )
        print("Plotting "+model_obtype+" observations")
        ax_obs_subplot_loc = str(ax_obs.rowNum)+','+str(ax_obs.colNum)
        ax_obs_plot_data = model_var_levels_zonalmean_OBAR[model_num-1,:,:]
        ax_obs_plot_data_lat = model_data_lat
        ax_obs_plot_data_levels = var_levels_num
        ax_obs_plot_levels = levels
        ax_obs_plot_cmap = cmap
        CF_ax_obs = plot_subplot_data(
            ax_obs, ax_obs_plot_data, ax_obs_plot_data_lat,
            ax_obs_plot_data_levels, ax_obs_plot_levels, ax_obs_plot_cmap,
            latlon_area
        )
        subplot_CF_dict[ax_obs_subplot_loc] = CF_ax_obs
    # Set up analysis subplot map and title, if needed
    if RUN_type == 'model2model' and forecast_anl_diff == 'YES':
        anl_subplot_num = (2 * (model_num - 1) + 1)
        anl_subplot_title = model_plot_name+'-'+model_obtype
        ax_anl = draw_subplot_map(
            anl_subplot_num, anl_subplot_title, nsubplots, latlon_area,
            var_level_num_list
        )
        print("Plotting "+model+" - "+model_obtype)
        ax_anl_subplot_loc = str(ax_anl.rowNum)+','+str(ax_anl.colNum)
        ax_anl_plot_data = (
            model_var_levels_zonalmean_FBAR[model_num-1,:,:]
            - model_var_levels_zonalmean_OBAR[model_num-1,:,:]
        )
        ax_anl_plot_data_lat = model_data_lat
        ax_anl_plot_data_levels = var_levels_num
        ax_anl_plot_levels = levels_diff
        ax_anl_plot_cmap = cmap_diff
        CF_ax_anl = plot_subplot_data(
            ax_anl, ax_anl_plot_data, ax_anl_plot_data_lat,
            ax_anl_plot_data_levels, ax_anl_plot_levels, ax_anl_plot_cmap,
            latlon_area
        )
        subplot_CF_dict[ax_anl_subplot_loc] = CF_ax_anl
    # Set up model subplot map and title
    if RUN_type == 'model2obs':
        subplot_num = model_num
        subplot_title = model_plot_name+'-'+model_obtype
        print("Plotting "+model+" - "+model_obtype)
        ax_plot_data = (
            model_var_levels_zonalmean_FBAR[model_num-1,:,:]
            - model_var_levels_zonalmean_OBAR[model_num-1,:,:]
        )
        ax_plot_levels = levels_diff
        ax_plot_cmap = cmap_diff
    elif RUN_type == 'model2model':
        if forecast_anl_diff == 'YES':
            subplot_num = 2 * (model_num - 1)
        else:
            subplot_num =  model_num - 1
        if model_num == 1:
            model1 = model
            model1_plot_name = model_plot_name
            subplot_title = model1_plot_name
            print("Plotting "+model)
            ax_plot_data = model_var_levels_zonalmean_FBAR[model_num-1,:,:]
            ax_plot_levels = levels
            ax_plot_cmap = cmap
            model1_var_levels_zonalmean_FBAR = (
                model_var_levels_zonalmean_FBAR[model_num-1,:,:]
            )
            model1_var_levels_zonalmean_OBAR = (
                model_var_levels_zonalmean_OBAR[model_num-1,:,:]
            )
        else:
            subplot_title = model_plot_name+'-'+model1_plot_name
            print("Plotting "+model+" - "+model1)
            ax_plot_data = (
                model_var_levels_zonalmean_FBAR[model_num-1,:,:]
                - model1_var_levels_zonalmean_FBAR
            )
            ax_plot_levels = levels_diff
            ax_plot_cmap = cmap_diff
    ax = draw_subplot_map(
        subplot_num, subplot_title, nsubplots, latlon_area, var_level_num_list
    )
    ax_subplot_loc = str(ax.rowNum)+','+str(ax.colNum)
    ax_plot_data_lat = model_data_lat
    ax_plot_data_levels = var_levels_num
    CF_ax = plot_subplot_data(
        ax, ax_plot_data, ax_plot_data_lat,
        ax_plot_data_levels, ax_plot_levels, ax_plot_cmap,
        latlon_area
    )
    subplot_CF_dict[ax_subplot_loc] = CF_ax
# Build formal plot title
full_title = (
    var_info_title.partition(' ')[2]+' Zonal Mean Error\n'
    +dates_title+' '+make_met_data_by_hrs_title+'\n'
    +forecast_to_plot_title
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
if len(list(subplot_CF_dict.keys())) > 1:
    cbar_subplot = None
    for subplot_loc in list(subplot_CF_dict.keys()):
        if subplot_loc != '0,0' and subplot_CF_dict[subplot_loc] != None:
            cbar_subplot = subplot_CF_dict[subplot_loc]
            cbar_subplot_loc = subplot_loc
            break
    if cbar_subplot != None:
        if nsubplots == 2:
            subplot_pos = ax.get_position()
            cbar_left = subplot_pos.x1 + 0.01
            cbar_bottom = subplot_pos.y0
            cbar_width = cbar_width_vert
            cbar_height = subplot_pos.y1 - subplot_pos.y0
            cbar_orientation = 'vertical'
        else:
            cbar_left = (
                noaa_img.get_extent()[1]
                /(plt.rcParams['figure.dpi']*x_figsize)
            )
            cbar_width = (
                nws_img.get_extent()[0]
                /(plt.rcParams['figure.dpi']*x_figsize)
                - noaa_img.get_extent()[1]
                /(plt.rcParams['figure.dpi']*x_figsize)
            )
            cbar_orientation = 'horizontal'
        cax = fig.add_axes(
            [cbar_left, cbar_bottom, cbar_width, cbar_height]
        )
        cbar = fig.colorbar(subplot_CF_dict[cbar_subplot_loc],
                            cax = cax,
                            orientation = cbar_orientation,
                            ticks = subplot_CF_dict[cbar_subplot_loc] \
                                .levels)
        if nsubplots == 2:
            cbar.ax.set_ylabel('Difference', labelpad = 5)
            cbar.ax.yaxis.set_tick_params(pad=0)
        else:
            cbar.ax.set_xlabel('Difference', labelpad = 0)
            cbar.ax.xaxis.set_tick_params(pad=0)
        cbar_tick_labels_list = []
        for tick in cbar.get_ticks():
            if str(tick).split('.')[1] == '0':
                cbar_tick_labels_list.append(str(int(tick)))
            else:
                cbar_tick_labels_list.append(
                    str(round(tick,3)).rstrip('0')
                )
        if nsubplots == 2:
            cbar.ax.set_yticklabels(cbar_tick_labels_list)
        else:
            cbar.ax.set_xticklabels(cbar_tick_labels_list)
# Build savefig name
savefig_name = os.path.join(plotting_out_dir_imgs,
                            RUN_type+'_'+var_group
                            +'_'+var_name+'_zonalmean_'
                            +forecast_to_plot+'.png')
print("Saving image as "+savefig_name)
plt.savefig(savefig_name)
plt.close()
