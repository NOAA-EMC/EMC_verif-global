from __future__ import (print_function, division)
import sys
import os
import numpy as np
import netCDF4 as netcdf
import re
import plot_util as plot_util
import maps2d_plot_util as maps2d_plot_util
import warnings
import logging
import datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy import config

warnings.filterwarnings('ignore')

plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.titlepad'] = 5
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.labelpad'] = 10
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['xtick.major.pad'] = 2.5
plt.rcParams['ytick.major.pad'] = 0
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['figure.subplot.left'] = 0.1
plt.rcParams['figure.subplot.right'] = 0.95
plt.rcParams['figure.titleweight'] = 'bold'
plt.rcParams['figure.titlesize'] = 16
if float(matplotlib.__version__[0:3]) >= 3.3:
    plt.rcParams['date.epoch'] = '0000-12-31T00:00:00'
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
def bilin_interp(input_data, input_lat, input_lon, output_lat, output_lon):
    output_data = np.ones([len(output_lat), len(output_lon)]) * np.nan
    # for poles
    sumn,sums = 0.0, 0.0
    for i in range(len(input_lon)):
        sums = sums + input_data[0,i]
        sumn = sumn + input_data[-1,i]
    for i in range(len(output_lon)):
        output_data[0,i] = sums/(len(input_lon))
        output_data[-1,i] = sumn/(len(input_lon))
    dy1 = np.empty(len(input_lat))
    dy2 = np.empty(len(input_lat))
    iy = np.empty(len(input_lat), dtype=int)
    for j in range(len(output_lat)):
        for jj in range(len(input_lat)-1):
            if output_lat[j] >= input_lat[jj] \
                    and output_lat[j] < input_lat[jj+1]:
                dy1[j] = output_lat[j] - input_lat[jj]
                dy2[j] = input_lat[jj+1] - output_lat[j]
                iy[j] = jj
                break
    dx1 = np.empty(len(input_lon))
    dx2 = np.empty(len(input_lon))
    ix = np.empty(len(input_lon), dtype=int)
    for i in range(len(output_lon)):
        for ii in range(len(input_lon)-1):
            if output_lon[i] == 0:
                dx1[i] = input_lon[-1] - 360
                dx2[i] = input_lon[0]
                ix[i] = 0
            else:
                if output_lon[i] >= input_lon[ii] \
                        and output_lon[i] < input_lon[ii+1]:
                    dx1[i] = output_lon[i] - input_lon[ii]
                    dx2[i] = input_lon[ii+1] - output_lon[i]
                    ix[i] = ii
                    break
    for j in range(1,len(output_lat)-1):
        jj = iy[j]
        for i in range(len(output_lon)):
            ii = ix[i]
            tmp1 = (
                (input_data[jj,ii]*dy2[j])
                 +(input_data[jj+1,ii]*dy1[j])
            )/(dy1[j]+dy2[j])
            tmp2 = (
                (input_data[jj,ii+1]*dy2[j])
                 +(input_data[jj+1,ii+1]*dy1[j])
            )/(dy1[j]+dy2[j])
            output_data[j,i] = (
                (tmp1*dx2[i])+(tmp2*dx1[i])
            )/(dx1[i]+dx2[i])
    return output_data

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

def draw_subplot_map(subplot_num, subplot_title, nsubplots,
                     latlon_area):
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

           Returns:
                ax_tmp     -    subplot axis object
                map_ax_tmp -    subplot map information
    """
    llcrnrlat_val = float(latlon_area[0])
    urcrnrlat_val = float(latlon_area[1])
    llcrnrlon_val = float(latlon_area[2])
    urcrnrlon_val = float(latlon_area[3])
    lat_ticks = np.linspace(llcrnrlat_val, urcrnrlat_val, 7, endpoint=True)
    lon_ticks = np.linspace(llcrnrlon_val, urcrnrlon_val, 7, endpoint=True)
    ax_tmp = plt.subplot(
        gs[subplot_num],
        projection=ccrs.PlateCarree(central_longitude=180)
    )
    map_ax_tmp = ax_tmp
    if urcrnrlon_val == 360:
        urcrnrlon_val_adjust = 359.9
    else:
        urcrnrlon_val_adjust = urcrnrlon_val
    ax_tmp.set_extent(
        [llcrnrlon_val, urcrnrlon_val_adjust,
         llcrnrlat_val, urcrnrlat_val],
        ccrs.PlateCarree()
    )
    ax_tmp.set_global()
    ax_tmp.coastlines()
    ax_tmp.set_xticks(lon_ticks, crs=ccrs.PlateCarree())
    ax_tmp.set_yticks(lat_ticks, crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax_tmp.xaxis.set_major_formatter(lon_formatter)
    ax_tmp.yaxis.set_major_formatter(lat_formatter)
    if ax_tmp.is_last_row() or \
            (nsubplots % 2 != 0 and subplot_num == nsubplots - 2):
       ax_tmp.set_xlabel('Longitude')
    else:
        plt.setp(ax_tmp.get_xticklabels(), visible=False)
    if ax_tmp.is_first_col():
        ax_tmp.set_ylabel('Latitude', labelpad=2)
    else:
        plt.setp(ax_tmp.get_yticklabels(), visible=False)
    ax_tmp.set_aspect('auto')
    ax_tmp.set_title(subplot_title, loc='left')
    return ax_tmp, map_ax_tmp

def plot_subplot_data(ax_tmp, map_ax_tmp, plot_data, plot_data_lat,
                      plot_data_lon, plot_levels, plot_cmap,
                      latlon_area):
    """ Plot data for subplot.

            Args:
                ax_tmp        - subplot axis object
                map_ax_tmp    - subplot map information
                plot_data     - array of the data to plot
                plot_data_lat - array of the data latitudes
                plot_data_lon - array of the data longitudes
                plot_levels   - array of the contour levels
                plot_cmap     - string of the colormap to use
                latlon_area   - list of the bounding
                                latitudes and longitudes
                                for the map

           Returns:
                CF_tmp     -    subplot contour fill object
    """
    llcrnrlat_val = float(latlon_area[0])
    urcrnrlat_val = float(latlon_area[1])
    llcrnrlon_val = float(latlon_area[2])
    urcrnrlon_val = float(latlon_area[3])
    # Add cyclic point for model data
    plot_data_cyc, plot_data_lon_cyc = add_cyclic_point(
        plot_data, coord = plot_data_lon
    )
    # NOTE: using cartopy 0.16, using cyclic data sometimes
    #       breaks geometries so not using
    plot_data_cyc = plot_data
    plot_data_lon_cyc = plot_data_lon
    # Get area average
    plot_data_area_avg = maps2d_plot_util.calculate_area_average(
        plot_data, plot_data_lat, plot_data_lon,
        llcrnrlat_val, urcrnrlat_val, llcrnrlon_val, urcrnrlon_val
    )
    if str(plot_data_area_avg) == 'nan':
        ax_tmp.set_title('--', loc='right')
    else:
        ax_tmp.set_title(round(plot_data_area_avg, 3), loc='right')
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
    x, y = np.meshgrid(plot_data_lon_cyc, plot_data_lat)
    if np.count_nonzero(~np.isnan(plot_data_cyc)) != 0:
        CF_tmp = ax_tmp.contourf(
            x, y, plot_data_cyc,
            transform=ccrs.PlateCarree(),
            levels=plot_levels, cmap=plot_cmap, extend='both'
        )
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
latlon_area = os.environ['latlon_area'].split(' ')
var_group = os.environ['var_group']
var_name = os.environ['var_name']
var_levels = os.environ['var_levels'].split(', ')
RUN_type = os.environ['RUN_type']
machine = os.environ['machine']
if RUN_type == 'gdas':
    regrid_to_grid = os.environ['regrid_to_grid']
    plot_stats_list = ['inc', 'rmse']
elif RUN_type == 'ens':
    plot_stats_list = ['mean', 'spread']
img_quality = os.environ['img_quality']

# Set image quality
if img_quality == 'low':
    plt.rcParams['savefig.dpi'] = 50
elif img_quality == 'medium':
    plt.rcParams['savefig.dpi'] = 75

# Set up location of Natural Earth files
if machine == 'WCOSS2':
    config['data_dir']='/u/emc.vpppg/.local/share/cartopy'
elif machine == 'HERA':
    config['data_dir']='/home/Mallory.Row/.local/share/cartopy'
elif machine == 'S4':
    config['data_dir']='/home/dhuber/.local/share/cartopy'
elif machine == 'JET':
    config['data_dir']='/home/Mallory.Row/.local/share/cartopy'

# Set up information
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
if RUN_type == 'gdas':
    if forecast_to_plot[:3] == 'fhr':
        forecast_to_plot_title = (
            'First Guess Hour '+forecast_to_plot[3:]
        )
    else:
        forecast_to_plot_title = (
            'First Guess Hour '+forecast_to_plot
        )
elif RUN_type == 'ens':
    if forecast_to_plot[:3] == 'fhr':
        forecast_to_plot_title = (
            'Forecast Hour '+forecast_to_plot[3:]
        )
    else:
         forecast_to_plot_title = (
            'Forecast Hour '+forecast_to_plot
        )
else:
    forecast_to_plot_title = forecast_to_plot
START_DATE_dt = datetime.datetime.strptime(START_DATE, '%Y%m%d')
END_DATE_dt = datetime.datetime.strptime(END_DATE, '%Y%m%d')
dates_title = (make_met_data_by.lower()+' '
               +START_DATE_dt.strftime('%d%b%Y')+'-'
               +END_DATE_dt.strftime('%d%b%Y'))

# Get input and output directories
if RUN_type == 'gdas':
    input_dir = os.path.join(DATA, RUN, 'metplus_output',
                             'make_met_data_by_'+make_met_data_by,
                             'series_analysis', RUN_type,
                             var_group)
elif RUN_type == 'ens':
     input_dir = os.path.join(DATA, RUN, 'data')
plotting_out_dir_imgs = os.path.join(DATA, RUN, 'metplus_output',
                                     'plot_by_'+plot_by,
                                     RUN_type, var_group,
                                     'imgs')
if not os.path.exists(plotting_out_dir_imgs):
    os.makedirs(plotting_out_dir_imgs)

# Loop of variables levels to create
# indivdual level lat-lon plots
for stat in plot_stats_list:
    if stat == 'inc':
        stat_title = 'GDAS Analysis Increments'
    elif stat == 'rmse':
        stat_title = 'Root Mean Square Error of GDAS Analysis Increments'
    elif stat == 'mean':
        stat_title = 'Ensemble Mean'
    elif stat == 'spread':
        stat_title = 'Ensemble Spread'
    # Get coarsest grid information for ens plots
    # for any needed regridding
    if RUN_type == 'ens':
        for env_var_model in env_var_model_list:
            model = os.environ[env_var_model]
            if forecast_to_plot == 'anl':
                input_file = os.path.join(input_dir, model,
                                          'atmanl.ens'+stat+'.nc')
            else:
                input_file = os.path.join(input_dir, model,
                                          'atmf'+forecast_to_plot[3:].zfill(3)
                                          +'.ens'+stat+'.nc')
            if os.path.exists(input_file):
                tmp_model_data = netcdf.Dataset(input_file)
                tmp_model_data_lat = np.flipud(
                    tmp_model_data.variables['grid_yt'][:]
                )
                tmp_model_data_lat_res = len(tmp_model_data_lat)
                tmp_model_data_lon = tmp_model_data.variables['grid_xt'][:]
                tmp_model_data_lon_res = len(tmp_model_data_lon)
                if not 'regrid_lat' in locals():
                    regrid_lat = tmp_model_data_lat
                    regrid_lat_res = tmp_model_data_lat_res
                    regrid_lon = tmp_model_data_lon
                    regrid_lon_res = tmp_model_data_lon_res
                if regrid_lat_res > tmp_model_data_lat_res:
                    regrid_lat = tmp_model_data_lat
                    regrid_lat_res = tmp_model_data_lat_res
                if regrid_lon_res > tmp_model_data_lon_res:
                    regrid_lon = tmp_model_data_lon
                    regrid_lon_res = tmp_model_data_lon_res
    for var_level in var_levels:
        var_info_title, levels, levels_diff, cmap, var_scale, cbar00_title = (
            maps2d_plot_util.get_maps2d_plot_settings(var_name, var_level)
        )
        model_num = 0
        subplot_CF_dict = {}
        print("Working on lat-lon error plots for "+stat+" "
              +var_name+" "+var_level)
        for env_var_model in env_var_model_list:
            model_num+=1
            model = os.environ[env_var_model]
            model_plot_name = os.environ[env_var_model+'_plot_name']
            if RUN_type == 'gdas':
                model_obtype = os.environ[env_var_model+'_obtype']
                input_file = os.path.join(
                    input_dir, model,
                    forecast_to_plot+'_'+var_name+'_'
                    +var_level.replace(' ', '')+'.nc'
                )
            elif RUN_type == 'ens':
                if forecast_to_plot == 'anl':
                    input_file = os.path.join(
                        input_dir, model,
                        'atmanl.ens'+stat+'.nc'
                    )
                else:
                    input_file = os.path.join(
                        input_dir, model,
                        'atmf'+forecast_to_plot[3:].zfill(3)
                        +'.ens'+stat+'.nc'
                    )
            # Set up plot
            if model_num == 1:
                if RUN_type == 'ens':
                    nsubplots = nmodels
                    get_diff_levels = True
                    get_levels = True
                else:
                    nsubplots = nmodels + 1
                    get_inc_levels = True
                    get_diff_levels = True
                    get_levels = True
                if nsubplots == 1:
                    x_figsize, y_figsize = 14, 7
                    row, col = 1, 1
                    hspace, wspace = 0, 0
                    bottom, top = 0.175, 0.825
                    suptitle_y_loc = 0.92125
                    noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.865
                    nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.865
                    cbar00_width = 0.01
                    cbar00_left_adjust = 0.05
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
                    cbar00_width = 0.01
                    cbar00_left_adjust = 0.075
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
                    cbar00_width = 0.01
                    cbar00_left_adjust = 0.075
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
                    cbar00_width = 0.01
                    cbar00_left_adjust = 0.075
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
                    cbar00_width = 0.01
                    cbar00_left_adjust = 0.075
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
                    cbar00_width = 0.01
                    cbar00_left_adjust = 0.075
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
                # Set up control analysis subplot map and title for gdas
                if RUN_type == 'gdas':
                    cntrl_subplot_num = 0
                    cntrl_subplot_title = 'A '+model_plot_name
                    ax_cntrl, map_ax_cntrl = draw_subplot_map(
                        cntrl_subplot_num, cntrl_subplot_title, nsubplots,
                        latlon_area
                    )
            # Set up model subplot map and title
            if RUN_type == 'ens':
                subplot_num =  model_num - 1
            else:
                subplot_num =  model_num
            if stat == 'inc':
                subplot_title = '(A-B) '+model_plot_name
            elif stat == 'rmse':
                if model_num == 1:
                    model1 = model
                    model1_plot_name = model_plot_name
                    subplot_title = 'RMSE(A-B) '+model1_plot_name
                else:
                    subplot_title = ('RMSE(A-B) '+model_plot_name
                                     +'-'+model1_plot_name)
            elif stat in ['mean', 'spread']:
                if model_num == 1:
                    model1 = model
                    model1_plot_name = model_plot_name
                    subplot_title = model_plot_name
                else:
                    subplot_title = model_plot_name+'-'+model1_plot_name
            ax, map_ax = draw_subplot_map(
                subplot_num, subplot_title, nsubplots, latlon_area
            )
            if model_num == 1:
                ax_model1 = ax
            # Read data
            if not os.path.exists(input_file):
                print("WARNING: "+input_file+" "
                      +"does not exist")
                if RUN_type == 'gdas' and model_num == 1:
                    ax_cntrl.set_title('--', loc='right')
                if model_num == 1:
                    model1_stat_data = np.array([])
                ax.set_title('--', loc='right')
            else:
                if RUN_type == 'gdas':
                    (model_data_series_cnt_FBAR, model_data_series_cnt_OBAR,
                     model_data_lat, model_data_lon) = (
                        read_series_analysis_file(input_file, var_scale)
                    )
                    if stat == 'inc':
                        stat_data = (model_data_series_cnt_OBAR
                                     - model_data_series_cnt_FBAR)
                    elif stat == 'rmse':
                        if model_num == 1:
                            stat_data = np.sqrt(
                                (model_data_series_cnt_OBAR
                                 - model_data_series_cnt_FBAR)**2
                            )
                            model1_stat_data = stat_data
                        else:
                            if np.size(model1_stat_data) == 0:
                                stat_data = np.sqrt(
                                    (model_data_series_cnt_OBAR
                                     - model_data_series_cnt_FBAR)**2
                                ) - (
                                    np.ones_like(model_data_series_cnt_FBAR)
                                    * np.nan
                                )
                            else:
                                stat_data = np.sqrt(
                                    (model_data_series_cnt_OBAR
                                     - model_data_series_cnt_FBAR)**2
                                ) - model1_stat_data
                elif RUN_type == 'ens':
                    print(input_file+" exists")
                    model_data = netcdf.Dataset(input_file)
                    if var_name != 'PRES':
                        model_levels = model_data.variables['pfull'][:]
                        var_level_float = float(var_level.replace('hPa', ''))
                        model_levels_var_level_diff = np.abs(
                            model_levels - var_level_float
                        )
                        model_levels_var_level_diff_min_idx = np.where(
                            model_levels_var_level_diff \
                            == np.min(model_levels_var_level_diff)
                        )[0][0]
                        model_level = (
                            model_levels[model_levels_var_level_diff_min_idx]
                        )
                    # Get index data
                    model_data_lat = np.flipud(
                        model_data.variables['grid_yt'][:]
                    )
                    model_data_lat_res = len(model_data_lat)
                    model_data_lon = model_data.variables['grid_xt'][:]
                    model_data_lon_res = len(model_data_lon)
                    if var_name == 'PRES':
                        model_data_var = model_data.variables['pressfc'][0,:,:]
                    else:
                        model_data_var = (
                            model_data.variables[var_name.lower()]\
                            [0,model_levels_var_level_diff_min_idx,:,:]
                        )
                        model_data_var = np.flipud(model_data_var)
                    if np.ma.is_masked(model_data_var):
                        np.ma.set_fill_value(model_data_var, np.nan)
                        model_data_var = (
                            model_data_var.filled()
                        )
                    # Regrid data if needed
                    if model_data_lat_res != regrid_lat_res \
                            and model_data_lon_res != regrid_lon_res:
                        print("WARNING: Regridding "+model+" from ("
                              +str(model_data_lat_res)+","
                              +str(model_data_lon_res)+") to "
                              +"("+str(regrid_lat_res)+","
                              +str(regrid_lon_res)+")")
                        model_data_var = bilin_interp(
                            model_data_var * var_scale, model_data_lat,
                            model_data_lon, regrid_lat,
                            regrid_lon
                        )
                    else:
                        model_data_var = model_data_var * var_scale
                    if model_num == 1:
                        stat_data = model_data_var
                        model1_stat_data = stat_data
                    else:
                        if np.size(model1_stat_data) == 0:
                            stat_data = (model_data_var
                                         - (np.ones_like(model_data_var)
                                            * np.nan))
                        else:
                            stat_data = model_data_var - model1_stat_data
                # Plot model data
                if RUN_type == 'gdas':
                    if model_num == 1:
                        print("Plotting "+model+" analysis")
                        ax_cntrl_subplot_loc = (str(ax_cntrl.rowNum)
                                                +','+str(ax_cntrl.colNum))
                        ax_cntrl_plot_data = model_data_series_cnt_OBAR
                        ax_cntrl_plot_data_lat = model_data_lat
                        ax_cntrl_plot_data_lon = model_data_lon
                        if get_levels:
                            if var_name in ['UGRD', 'VGRD', 'VVEL', 'LFTX',
                                            '4LFTX', 'UFLX', 'VFLX', 'GFLX']:
                                levels = plot_util.get_clevels(
                                    ax_cntrl_plot_data, 1.25
                                 )
                            else:
                                levels = np.nan
                            get_levels = False
                        ax_cntrl_plot_levels = levels
                        ax_cntrl_plot_cmap = cmap
                        CF_ax_cntrl = plot_subplot_data(
                            ax_cntrl, map_ax_cntrl, ax_cntrl_plot_data,
                            ax_cntrl_plot_data_lat, ax_cntrl_plot_data_lon,
                            ax_cntrl_plot_levels, ax_cntrl_plot_cmap,
                            latlon_area
                        )
                        subplot_CF_dict[ax_cntrl_subplot_loc] = CF_ax_cntrl
                if RUN_type == 'gdas':
                    if stat == 'inc':
                        print("Plotting "+model+" increments")
                        if get_inc_levels:
                            levels_plot = plot_util.get_clevels(stat_data,
                                                                1.25)
                            cmap_plot_original = plt.cm.PiYG_r
                            colors_plot = cmap_plot_original(
                                np.append(np.linspace(0,0.3,10),
                                          np.linspace(0.7,1,10))
                            )
                            cmap_plot = (
                                matplotlib.colors.\
                                LinearSegmentedColormap.from_list('cmap_plot',
                                                                  colors_plot)
                            )
                            get_inc_levels = False
                    elif stat == 'rmse':
                        if model_num == 1:
                            print("Plotting "+model1+" increment RMSE")
                            levels_plot = np.nan
                            cmap_plot = plt.cm.BuPu
                        else:
                            print("Plotting "+model+" - "+model1+" "
                                  +"increment RMSE")
                            if get_diff_levels:
                                levels_plot = plot_util.get_clevels(stat_data,
                                                                    1.25)
                                cmap_plot = cmap_diff
                                get_diff_levels = False
                elif RUN_type == 'ens':
                    if model_num == 1:
                        print("Plotting "+model+" ensemble "+stat)
                        if stat == 'mean':
                            cmap_plot = cmap
                            if get_levels:
                                if var_name in ['UGRD', 'VGRD', 'VVEL', 'LFTX',
                                                '4LFTX', 'UFLX', 'VFLX',
                                                'GFLX']:
                                    levels_plot = plot_util.get_clevels(
                                        stat_data, 1.25
                                    )
                                else:
                                    levels_plot = np.nan
                            get_levels = False
                        elif stat == 'spread':
                            cmap_plot = plt.cm.afmhot_r
                            levels_plot = np.nan
                    else:
                        print("Plotting "+model+"-"+model1+" ensemble "+stat)
                        if get_diff_levels:
                            levels_plot = plot_util.get_clevels(stat_data,
                                                                1.25)
                            cmap_plot = cmap_diff
                            get_diff_levels = False
                ax_subplot_loc = str(ax.rowNum)+','+str(ax.colNum)
                ax_plot_data = stat_data
                if RUN_type == 'ens':
                    ax_plot_data_lat = regrid_lat
                    ax_plot_data_lon = regrid_lon
                else:
                    ax_plot_data_lat = model_data_lat
                    ax_plot_data_lon = model_data_lon
                ax_plot_levels = levels_plot
                ax_plot_cmap = cmap_plot
                CF_ax = plot_subplot_data(
                    ax, map_ax, ax_plot_data,
                    ax_plot_data_lat, ax_plot_data_lon,
                    ax_plot_levels, ax_plot_cmap,
                    latlon_area
                )
                subplot_CF_dict[ax_subplot_loc] = CF_ax
        # Build formal plot title
        full_title = (stat_title+'\n'+var_info_title+'\n'
                      +dates_title+' '+make_met_data_by_hrs_title+', '
                      +forecast_to_plot_title)
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
        if img_quality in ['low', 'medium']:
            noaa_img.set_visible(False)
            nws_img.set_visible(False)
        plt.subplots_adjust(
            left = noaa_img.get_extent()[1]/(plt.rcParams['figure.dpi']*x_figsize),
            right = nws_img.get_extent()[0]/(plt.rcParams['figure.dpi']*x_figsize)
        )
        # Add colorbars
        if RUN_type == 'gdas':
            subplot00_pos = ax_cntrl.get_position()
        elif RUN_type == 'ens':
            subplot00_pos = ax_model1.get_position()
        cbar00_left = subplot00_pos.x0 - cbar00_left_adjust
        cbar00_bottom = subplot00_pos.y0
        cbar00_height = subplot00_pos.y1 - subplot00_pos.y0
        if ('0,0' in list(subplot_CF_dict.keys()) \
                and subplot_CF_dict['0,0'] != None):
            cax00 = fig.add_axes(
                [cbar00_left, cbar00_bottom, cbar00_width, cbar00_height]
            )
            cbar00 = fig.colorbar(subplot_CF_dict['0,0'],
                                  cax = cax00,
                                  orientation = 'vertical',
                                  ticks = subplot_CF_dict['0,0'].levels)
            cax00.yaxis.set_ticks_position('left')
            cax00.yaxis.set_label_position('left')
            cbar00.ax.set_ylabel(cbar00_title, labelpad = 2)
            cbar00.ax.yaxis.set_tick_params(pad=0)
            cbar00_tick_labels_list = []
            for tick in cbar00.get_ticks():
                if str(tick).split('.')[1] == '0':
                    cbar00_tick_labels_list.append(str(int(tick)))
                else:
                    cbar00_tick_labels_list.append(
                        str(round(tick,3)).rstrip('0')
                    )
            cbar00.ax.set_yticklabels(cbar00_tick_labels_list)
        if RUN_type == 'ens' or \
                (RUN_type == 'gdas' and stat == 'inc'):
            if RUN_type == 'ens':
                cbar_title = 'Difference'
            elif (RUN_type == 'gdas' and stat == 'inc'):
                cbar_title = 'Increments'
            if len(list(subplot_CF_dict.keys())) >= 1:
                cbar_subplot = None
                for subplot_loc in list(subplot_CF_dict.keys()):
                    if subplot_loc != '0,0' \
                            and subplot_CF_dict[subplot_loc] != None:
                        cbar_subplot = subplot_CF_dict[subplot_loc]
                        cbar_subplot_loc = subplot_loc
                        break
                if cbar_subplot != None:
                    if nsubplots == 2:
                        subplot_pos = ax.get_position()
                        cbar_left = subplot_pos.x1 + 0.005
                        cbar_bottom = subplot_pos.y0
                        cbar_width = cbar00_width
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
                                        ticks = subplot_CF_dict \
                                            [cbar_subplot_loc].levels)
                    if nsubplots == 2:
                        cbar.ax.set_ylabel(cbar_title, labelpad = 2)
                        cbar.ax.yaxis.set_tick_params(pad=0)
                    else:
                        cbar.ax.set_xlabel(cbar_title, labelpad = 0)
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
        elif (RUN_type == 'gdas' and stat == 'rmse'):
            subplot01_pos = ax_model1.get_position()
            cbar01_left = subplot01_pos.x1 + 0.005
            cbar01_bottom = subplot01_pos.y0
            cbar01_width = cbar00_width
            cbar01_height = subplot01_pos.y1 - subplot01_pos.y0
            if ('0,1' in list(subplot_CF_dict.keys()) \
                    and subplot_CF_dict['0,1'] != None):
                cax01 = fig.add_axes(
                    [cbar01_left, cbar01_bottom, cbar01_width, cbar01_height]
                )
                cbar01 = fig.colorbar(subplot_CF_dict['0,1'],
                                      cax = cax01,
                                      orientation = 'vertical',
                                      ticks = subplot_CF_dict['0,1'].levels)
                cbar01.ax.yaxis.set_tick_params(pad=0)
                cbar01.ax.set_ylabel('RMSE', labelpad = 2)
                cbar01.ax.yaxis.set_tick_params(pad=0)
                cbar01_tick_labels_list = []
                for tick in cbar01.get_ticks():
                    if str(tick).split('.')[1] == '0':
                        cbar01_tick_labels_list.append(str(int(tick)))
                    else:
                        cbar01_tick_labels_list.append(
                            str(round(tick,3)).rstrip('0')
                        )
                cbar01.ax.set_yticklabels(cbar01_tick_labels_list)
            if len(list(subplot_CF_dict.keys())) > 2:
                cbar_subplot = None
                for subplot_loc in list(subplot_CF_dict.keys()):
                    if subplot_loc not in ['0,0', '0,1'] \
                            and subplot_CF_dict[subplot_loc] != None:
                        cbar_subplot = subplot_CF_dict[subplot_loc]
                        cbar_subplot_loc = subplot_loc
                        break
                if cbar_subplot != None:
                    if nsubplots == 3:
                        subplot_pos = ax.get_position()
                        cbar_left = cbar00_left
                        cbar_bottom = subplot_pos.y0
                        cbar_width = cbar00_width
                        cbar_height = cbar00_height
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
                                        ticks = subplot_CF_dict \
                                            [cbar_subplot_loc].levels)
                    if nsubplots == 3:
                        cax.yaxis.set_ticks_position('left')
                        cax.yaxis.set_label_position('left')
                        cbar.ax.set_ylabel('Difference', labelpad = 2)
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
                    if nsubplots == 3:
                        cbar.ax.set_yticklabels(cbar_tick_labels_list)
                    else:
                        cbar.ax.set_xticklabels(cbar_tick_labels_list)
        # Build savefig name
        savefig_name = os.path.join(plotting_out_dir_imgs,
                                    RUN_type+'_'+stat+'_'+var_group
                                    +'_'+var_name+'_'
                                    +var_level.replace(' ', '')
                                    +'.png')
        print("Saving image as "+savefig_name)
        plt.savefig(savefig_name)
        plt.close()
