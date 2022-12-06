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
import itertools
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

# Exit early if we don't need to run this
# aka not running model2obs
type_list = os.environ['maps2d_type_list'].split(' ')
if 'model2obs' not in type_list:
    print("model2obs verification not requested..."
          +"no need to calculate special variables")
    sys.exit(1)

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
make_met_data_by = os.environ['maps2d_model2obs_make_met_data_by']
plot_by = make_met_data_by
START_DATE = os.environ['start_date']
END_DATE = os.environ['end_date']
forecast_to_plot_list = os.environ['maps2d_model2obs_forecast_to_plot_list'].split(' ')
regrid_to_grid = os.environ['maps2d_model2obs_regrid_to_grid']
latlon_area = os.environ['maps2d_latlon_area'].split(' ')
type_list = os.environ['maps2d_type_list'].split(' ')
use_monthly_mean = os.environ['maps2d_model2obs_use_monthly_mean']
use_ceres = os.environ['maps2d_model2obs_use_ceres']
hour_beg = os.environ['maps2d_model2obs_hour_beg']
hour_end = os.environ['maps2d_model2obs_hour_end']
hour_inc = os.environ['maps2d_model2obs_hour_inc']
model_list = os.environ['model_list'].split(' ')
model_plot_name_list = os.environ['maps2d_model_plot_name_list'].split(' ')
machine = os.environ['machine']
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
RUN_type = 'model2obs'
var_group = 'cloudsrad'
nmodels = int(len(model_list))

# Plot title information
START_DATE_dt = datetime.datetime.strptime(START_DATE, '%Y%m%d')
END_DATE_dt = datetime.datetime.strptime(END_DATE, '%Y%m%d')
dates_title = (make_met_data_by.lower()+' '
               +START_DATE_dt.strftime('%d%b%Y')+'-'
               +END_DATE_dt.strftime('%d%b%Y'))
make_met_data_by_hrs = []
hr = int(hour_beg) * 3600
while hr <= int(hour_end)*3600:
    make_met_data_by_hrs.append(str(int(hr/3600)).zfill(2)+'Z')
    hr+=int(hour_inc)
make_met_data_by_hrs_title = ', '.join(make_met_data_by_hrs)
forecase_to_plot_title_list = []

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

# Loop of variables levels to create lat-lon plots
var_info_forcast_to_plot_list = itertools.product(
    ['SWABSORB_atm_avg6hr', 'LWEMIT_atm_avg6hr', 'SWALBDO_sfc_avg6hr'],
    forecast_to_plot_list
)
for var_info_forcast_to_plot in var_info_forcast_to_plot_list:
    get_levels = True
    get_diff_levels = True
    var_name = var_info_forcast_to_plot[0].partition('_')[0]
    var_level = var_info_forcast_to_plot[0].partition('_')[2]
    forecast_to_plot = var_info_forcast_to_plot[1]
    print("Working on lat-lon error plots for "+var_name+" "+var_level
          +" "+forecast_to_plot)
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
    if var_name == 'SWABSORB': #shortwave absorption
        var_info_title = (
            'Atmospheric Absorbed Shortwave (W 'r'$\mathregular{m^{-2}}$'')'
        )
        levels = np.array([10,30,50,70,90,110,120,130])
        levels_diff = np.array([-60,-40,-30,-20,-10,0,10,20,30,40,60])
        cmap = plt.cm.Wistia
        var_scale = 1
        cbar00_title = 'Atmospheric Absorbed Shortwave'
        files_needed_list = [
           forecast_to_plot+'_DSWRF_toa_avg6hr_obsonly.nc',
           forecast_to_plot+'_DSWRF_sfc_avg6hr.nc',
           forecast_to_plot+'_USWRF_toa_avg6hr.nc',
           forecast_to_plot+'_USWRF_sfc_avg6hr.nc',
        ]
    elif var_name == 'LWEMIT': #longwave emitted
        var_info_title = (
            'Atmospheric Emitted Longwave (W 'r'$\mathregular{m^{-2}}$'')'
        )
        levels = np.array([100,120,140,160,180,200,220,240])
        levels_diff = np.array([-60,-40,-30,-20,-10,0,10,20,30,40,60])
        cmap = plt.cm.cool
        var_scale = 1
        cbar00_title = 'Atmospheric Emitted Longwave'
        files_needed_list = [
           forecast_to_plot+'_DLWRF_sfc_avg6hr.nc',
           forecast_to_plot+'_ULWRF_toa_avg6hr.nc',
           forecast_to_plot+'_ULWRF_sfc_avg6hr.nc',
        ]
    elif var_name == 'SWALBDO': #shortwave surface albedo
        var_info_title = 'Shortwave Surface Albedo (fraction)'
        levels = np.array([0.1,0.2,0.4,0.6,0.8,1.0])
        levels_diff = np.array(
            [-0.06,-0.04,-0.03,-0.02,-0.01,0,0.01,0.02,0.03,0.04,0.06]
        )
        cmap = plt.cm.cubehelix_r
        var_scale = 1
        cbar00_title = 'Albedo'
        files_needed_list = [
           forecast_to_plot+'_DSWRF_sfc_avg6hr.nc',
           forecast_to_plot+'_USWRF_sfc_avg6hr.nc',
        ]
    subplot_CF_dict = {}
    for model in model_list:
        index = model_list.index(model)
        model_num = index + 1
        model_plot_name = model_plot_name_list[index]
        # Only dealing with radiation variables
        if use_ceres == 'YES':
            model_obtype = 'ceres'
        else:
            model_obtype = 'rad_srb2'
        # Set up plot
        if model_num == 1:
            nsubplots = nmodels + 1
            obs_plotted = False
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
            # Set up observation subplot map and title
            obs_subplot_num = 0
            obs_subplot_title = maps2d_plot_util.get_obs_subplot_title(
                model_obtype, use_monthly_mean
            )
            ax_obs, map_ax_obs = draw_subplot_map(
                obs_subplot_num, obs_subplot_title, nsubplots,
                latlon_area
            )
        subplot_num = model_num
        subplot_title = model_plot_name+'-'+model_obtype
        ax, map_ax = draw_subplot_map(
            subplot_num, subplot_title, nsubplots, latlon_area
        )
        # Read data
        all_model_files_exist = True
        missing_file_list = []
        for file in files_needed_list:
            model_series_analysis_netcdf_file = os.path.join(
                series_analysis_file_dir, model, file
            )
            if not os.path.exists(model_series_analysis_netcdf_file):
                all_model_files_exist = False
                missing_file_list.append(model_series_analysis_netcdf_file)
        if not all_model_files_exist:
            print("Missing files for "+model+" "+', '.join(missing_file_list))
            if model_num == 1:
                ax_obs.set_title('--', loc='right')
            ax.set_title('--', loc='right')
        else:
            if var_name == 'SWABSORB': #shortwave absorption
                DSWRF_toa_obsonly_file  = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_DSWRF_toa_avg6hr_obsonly.nc'
                )
                (DSWRF_toa_obsonly_data_series_cnt_FBAR,
                 DSWRF_toa_obsonly_data_series_cnt_OBAR,
                 DSWRF_toa_obsonly_data_lat, DSWRF_toa_obsonly_data_lon) = (
                    read_series_analysis_file(DSWRF_toa_obsonly_file,
                                              var_scale)
                )
                DSWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_DSWRF_sfc_avg6hr.nc'
                )
                (DSWRF_sfc_data_series_cnt_FBAR,
                 DSWRF_sfc_data_series_cnt_OBAR,
                 DSWRF_sfc_data_lat, DSWRF_sfc_data_lon) = (
                    read_series_analysis_file(DSWRF_sfc_file, var_scale)
                )
                USWRF_toa_file  = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_USWRF_toa_avg6hr.nc'
                )
                (USWRF_toa_data_series_cnt_FBAR,
                 USWRF_toa_data_series_cnt_OBAR,
                 USWRF_toa_data_lat, USWRF_toa_data_lon) = (
                    read_series_analysis_file(USWRF_toa_file, var_scale)
                )
                USWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_USWRF_sfc_avg6hr.nc'
                )
                (USWRF_sfc_data_series_cnt_FBAR,
                 USWRF_sfc_data_series_cnt_OBAR,
                 USWRF_sfc_data_lat, USWRF_sfc_data_lon) = (
                    read_series_analysis_file(USWRF_sfc_file, var_scale)
                )
                obs_calc_var = (
                    DSWRF_toa_obsonly_data_series_cnt_OBAR
                    - DSWRF_sfc_data_series_cnt_OBAR
                    - USWRF_toa_data_series_cnt_OBAR
                    + USWRF_sfc_data_series_cnt_OBAR
                )
                model_calc_var = (
                    DSWRF_toa_obsonly_data_series_cnt_OBAR
                    - DSWRF_sfc_data_series_cnt_FBAR
                    - USWRF_toa_data_series_cnt_FBAR
                    + USWRF_sfc_data_series_cnt_FBAR
                )
                model_data_lat = USWRF_sfc_data_lat
                model_data_lon = USWRF_sfc_data_lon
            elif var_name == 'LWEMIT': #longwave emitted
                DLWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_DLWRF_sfc_avg6hr.nc'
                )
                (DLWRF_sfc_data_series_cnt_FBAR,
                 DLWRF_sfc_data_series_cnt_OBAR,
                 DLWRF_sfc_data_lat, DLWRF_sfc_data_lon) = (
                    read_series_analysis_file(DLWRF_sfc_file, var_scale)
                )
                ULWRF_toa_file  = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_ULWRF_toa_avg6hr.nc'
                )
                (ULWRF_toa_data_series_cnt_FBAR,
                 ULWRF_toa_data_series_cnt_OBAR,
                 ULWRF_toa_data_lat, ULWRF_toa_data_lon) = (
                    read_series_analysis_file(ULWRF_toa_file, var_scale)
                )
                ULWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_ULWRF_sfc_avg6hr.nc'
                )
                (ULWRF_sfc_data_series_cnt_FBAR,
                 ULWRF_sfc_data_series_cnt_OBAR,
                 ULWRF_sfc_data_lat, ULWRF_sfc_data_lon) = (
                    read_series_analysis_file(ULWRF_sfc_file, var_scale)
                )
                obs_calc_var = (
                    DLWRF_sfc_data_series_cnt_OBAR
                    + ULWRF_toa_data_series_cnt_OBAR
                    - ULWRF_sfc_data_series_cnt_OBAR
                )
                model_calc_var = (
                    DLWRF_sfc_data_series_cnt_FBAR
                    + ULWRF_toa_data_series_cnt_FBAR
                    - ULWRF_sfc_data_series_cnt_FBAR
                )
                model_data_lat = ULWRF_sfc_data_lat
                model_data_lon = ULWRF_sfc_data_lon
            elif var_name == 'SWALBDO': #shortwave surface albedo
                DSWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_DSWRF_sfc_avg6hr.nc'
                )
                (DSWRF_sfc_data_series_cnt_FBAR,
                 DSWRF_sfc_data_series_cnt_OBAR,
                 DSWRF_sfc_data_series_lat, DSWRF_sfc_data_series_lon) = (
                    read_series_analysis_file(DSWRF_sfc_file, var_scale)
                )
                USWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_USWRF_sfc_avg6hr.nc'
                )
                (USWRF_sfc_data_series_cnt_FBAR,
                 USWRF_sfc_data_series_cnt_OBAR,
                 USWRF_sfc_data_lat, USWRF_sfc_data_lon) = (
                    read_series_analysis_file(USWRF_sfc_file, var_scale)
                )
                obs_calc_var = (
                    USWRF_sfc_data_series_cnt_OBAR
                    / DSWRF_sfc_data_series_cnt_OBAR
                )
                model_calc_var = (
                    USWRF_sfc_data_series_cnt_FBAR
                    / DSWRF_sfc_data_series_cnt_FBAR
                )
                model_data_lat = USWRF_sfc_data_lat
                model_data_lon = USWRF_sfc_data_lon
            if not obs_plotted:
                print("Plotting "+model_obtype+" observations from "+model)
                ax_obs_subplot_loc = str(ax_obs.rowNum)+','+str(ax_obs.colNum)
                ax_obs_plot_data = obs_calc_var
                ax_obs_plot_data_lat = model_data_lat
                ax_obs_plot_data_lon = model_data_lon
                if get_levels:
                    if var_name in ['UGRD', 'VGRD', 'VVEL', 'LFTX',
                                    '4LFTX', 'UFLX', 'VFLX', 'GFLX']:
                        levels = plot_util.get_clevels(ax_obs_plot_data, 1.25)
                    else:
                        levels = np.nan
                    get_levels = False
                ax_obs_plot_levels = levels
                ax_obs_plot_cmap = cmap
                CF_ax_obs = plot_subplot_data(
                    ax_obs, map_ax_obs, ax_obs_plot_data,
                    ax_obs_plot_data_lat, ax_obs_plot_data_lon,
                    ax_obs_plot_levels, ax_obs_plot_cmap,
                    latlon_area
                )
                subplot_CF_dict[ax_obs_subplot_loc] = CF_ax_obs
                obs_plotted = True
            print("Plotting "+model+" - "+model_obtype)
            ax_subplot_loc = str(ax.rowNum)+','+str(ax.colNum)
            ax_plot_data = (
                model_calc_var - obs_calc_var
            )
            ax_plot_data_lat = model_data_lat
            ax_plot_data_lon = model_data_lon
            if get_diff_levels:
                levels_diff = plot_util.get_clevels(ax_plot_data, 1.25)
                get_diff_levels = False
            ax_plot_levels = levels_diff
            ax_plot_cmap = cmap_diff
            CF_ax = plot_subplot_data(
                ax, map_ax, ax_plot_data,
                ax_plot_data_lat, ax_plot_data_lon,
                ax_plot_levels, ax_plot_cmap,
                latlon_area
            )
            subplot_CF_dict[ax_subplot_loc] = CF_ax
    # Build formal plot title
    full_title = (
        var_info_title+'\n'
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
    if img_quality in ['low', 'medium']:
        noaa_img.set_visible(False)
        nws_img.set_visible(False)
    plt.subplots_adjust(
        left = noaa_img.get_extent()[1]/(plt.rcParams['figure.dpi']*x_figsize),
        right = nws_img.get_extent()[0]/(plt.rcParams['figure.dpi']*x_figsize)
    )
    # Add colorbars
    subplot00_pos = ax_obs.get_position()
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
                                ticks = subplot_CF_dict[cbar_subplot_loc] \
                                    .levels)
            if nsubplots == 2:
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
            if nsubplots == 2:
                cbar.ax.set_yticklabels(cbar_tick_labels_list)
            else:
                cbar.ax.set_xticklabels(cbar_tick_labels_list)
    # Build savefig name
    savefig_name = os.path.join(plotting_out_dir_imgs,
                                RUN_type+'_'+var_group
                                +'_'+var_name+'_'+var_level.replace(' ', '')
                                +'_'+forecast_to_plot+'.png')
    print("Saving image as "+savefig_name)
    plt.savefig(savefig_name)
    link_image_dir = os.path.join(
        DATA, RUN, 'metplus_output', 'images/.'
    )
    print("Linking image to "+link_image_dir)
    os.system('ln -sf '+savefig_name+' '+link_image_dir)
    plt.close()
    plt.close()
