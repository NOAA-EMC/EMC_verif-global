from __future__ import (print_function, division)
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
cmap_diff = plt.cm.coolwarm_r
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

def draw_subplot_map(subplot_num, subplot_title, nsubplots,
                     py_map_pckg, latlon_area):
    """ Draw map for subplot.
            
            Args:
                subplot_num   - integer of the subplot
                                location number
                subplot_title - string of the title for
                                subplot
                nsubplots     - integer of the number
                                of total subplots in
                                image
                py_map_pckg   - string of the python
                                map plotting package
                                to use; either cartopy
                                or basemap
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
    if py_map_pckg == 'cartopy':
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
    elif py_map_pckg == 'basemap':
        ax_tmp = plt.subplot(gs[subplot_num])
        map_ax_tmp = Basemap(projection='cyl', llcrnrlat=llcrnrlat_val,
                             urcrnrlat=urcrnrlat_val, llcrnrlon=llcrnrlon_val,
                             urcrnrlon=urcrnrlon_val, resolution='c',
                             lon_0=180, ax=ax_tmp)
        map_ax_tmp.drawcoastlines(linewidth=1.5, color='k', zorder=6)
        map_ax_tmp.drawmapboundary
        map_ax_tmp.drawmeridians(lon_ticks, labels=[False,False,False,True])
        map_ax_tmp.drawparallels(lat_ticks, labels=[True,False,False,False])
    if ax_tmp.is_last_row() or \
            (nsubplots % 2 != 0 and subplot_num == nsubplots - 2):
       ax_tmp.set_xlabel('Longitude')
    else:
        plt.setp(ax_tmp.get_xticklabels(), visible=False)
    if ax_tmp.is_first_col():
        ax_tmp.set_ylabel('Latitude')
    else:
        plt.setp(ax_tmp.get_yticklabels(), visible=False)
    ax_tmp.set_aspect('auto')
    ax_tmp.set_title(subplot_title, loc='left')
    return ax_tmp, map_ax_tmp

def plot_subplot_data(ax_tmp, map_ax_tmp, plot_data, plot_data_lat,
                      plot_data_lon, plot_levels, plot_cmap, py_map_pckg,
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
                py_map_pckg   - string of the python
                                map plotting package
                                to use; either cartopy
                                or basemap
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
    if py_map_pckg == 'cartopy':
        plot_data_cyc, plot_data_lon_cyc = add_cyclic_point(
            plot_data, coord = plot_data_lon
        )
    elif py_map_pckg == 'basemap':
        plot_data_cyc, plot_data_lon_cyc = addcyclic(
            plot_data, plot_data_lon
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
    # Plot model data
    x, y = np.meshgrid(plot_data_lon_cyc, plot_data_lat)
    if np.count_nonzero(~np.isnan(plot_data_cyc)) != 0:
        if py_map_pckg == 'cartopy':
            CF_tmp = ax_tmp.contourf(
                x, y, plot_data_cyc,
                transform=ccrs.PlateCarree(),
                levels=plot_levels, cmap=plot_cmap, extend='both'
            )
        elif py_map_pckg == 'basemap':
            map_ax_tmp_x, map_ax_tmp_y = map_ax_tmp(x, y)
            CF_tmp = map_ax_tmp.contourf(
                map_ax_tmp_x, map_ax_tmp_y, plot_data_cyc,
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
hr_beg = os.environ['hr_beg']
hr_end = os.environ['hr_end']
hr_inc = os.environ['hr_inc']
regrid_to_grid = os.environ['regrid_to_grid']
latlon_area = os.environ['latlon_area'].split(' ')
var_group_name = os.environ['var_group_name']
var_name = os.environ['var_name']
var_levels = os.environ['var_levels'].split(', ')
verif_case_type = os.environ['verif_case_type']
if verif_case_type == 'model2model':
    forecast_anl_diff = os.environ['forecast_anl_diff']
    if forecast_to_plot == 'anl':
        forecast_anl_diff = 'NO'
if verif_case_type == 'model2obs':
   use_monthly_mean = os.environ['use_monthly_mean']

# Set up information
py_map_pckg = os.environ['py_map_pckg']
if py_map_pckg == 'cartopy':
    import cartopy.crs as ccrs
    from cartopy.util import add_cyclic_point
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
elif py_map_pckg == 'basemap':
    from mpl_toolkits.basemap import Basemap, addcyclic
env_var_model_list = []
regex = re.compile(r'model(\d+)$')
for key in os.environ.keys():
    result = regex.match(key)
    if result is not None:
        env_var_model_list.append(result.group(0))
env_var_model_list = sorted(env_var_model_list, key=lambda m: m[-1])
if env_var_model_list[0] == 'model10':
    env_var_model_list.remove(env_var_model_list[0])
    env_var_model_list.append('model10')
nmodels = len(env_var_model_list)
make_met_data_by_hrs = []
hr = int(hr_beg) * 3600
while hr <= int(hr_end)*3600:
    make_met_data_by_hrs.append(str(int(hr/3600)).zfill(2)+'Z')
    hr+=int(hr_inc)
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

# Get input and output directories
series_analysis_file_dir = os.path.join(DATA, RUN, 'metplus_output',
                                        'make_met_data_by_'+make_met_data_by,
                                        'series_analysis', verif_case_type,
                                        var_group_name)
plotting_out_dir_imgs = os.path.join(DATA, RUN, 'metplus_output',
                                     'plot_by_'+plot_by,
                                     verif_case_type, var_group_name,
                                     'imgs')
if not os.path.exists(plotting_out_dir_imgs):
    os.makedirs(plotting_out_dir_imgs)

# Loop of variables levels to create
# indivdual level lat-lon plots
for var_level in var_levels:
    # Do not plot obs. only DSWRF at toa
    if var_name == 'DSWRF' and var_level == 'toa':
        continue
    var_info_title, levels, levels_diff, cmap, var_scale, cbar00_title = (
        maps2d_plot_util.get_maps2d_plot_settings(var_name, var_level) 
    )
    model_num = 0
    subplot_CF_dict = {}
    print("Working on lat-lon error plots for "+var_name+" "+var_level)
    for env_var_model in env_var_model_list:
        model_num+=1
        model = os.environ[env_var_model]
        model_obtype = os.environ[env_var_model+'_obtype']
        model_plot_name = os.environ[env_var_model+'_plot_name']
        model_series_analysis_netcdf_file = os.path.join(
            series_analysis_file_dir, model,
            forecast_to_plot+'_'+var_name+'_'
            +var_level.replace(' ', '')+'.nc'
        )
        # Set up plot
        if model_num == 1:
            if verif_case_type == 'model2obs':
                nsubplots = nmodels + 1
            elif verif_case_type == 'model2model':
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
                cbar00_left_adjust = 0.09
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
                cbar00_left_adjust = 0.09
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
                cbar00_left_adjust = 0.09
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
                cbar00_left_adjust = 0.09
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
                cbar00_left_adjust = 0.09
                cbar_bottom = 0.03
                cbar_height = 0.02
            else:
                logger.error("Too many subplots selected, max. is 10")
                exit(1)
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
            # Set up observation subplot map and title, if needed
            if verif_case_type == 'model2obs':
                obs_subplot_num = 0
                obs_subplot_title = maps2d_plot_util.get_obs_subplot_title(
                    model_obtype, use_monthly_mean
                ) 
                ax_obs, map_ax_obs = draw_subplot_map(
                    obs_subplot_num, obs_subplot_title, nsubplots,
                    py_map_pckg, latlon_area
                )
        # Set up analysis subplot map and title, if needed
        if verif_case_type == 'model2model' and forecast_anl_diff == 'YES':
            anl_subplot_num = (2 * (model_num - 1) + 1)
            anl_subplot_title = model_plot_name+'-'+model_obtype
            ax_anl, map_ax_anl = draw_subplot_map(
                anl_subplot_num, anl_subplot_title, nsubplots, py_map_pckg,
                latlon_area
            )
        # Set up model subplot map and title
        if verif_case_type == 'model2obs':
            subplot_num = model_num
            subplot_title = model_plot_name+'-'+model_obtype
        elif verif_case_type == 'model2model':
            if forecast_anl_diff == 'YES':
                subplot_num = 2 * (model_num - 1)
            else:
                subplot_num =  model_num - 1
            if model_num == 1:
                model1 = model
                model1_plot_name = model_plot_name
                subplot_title = model1_plot_name
            else:
                subplot_title = model_plot_name+'-'+model1_plot_name
        ax, map_ax = draw_subplot_map(
            subplot_num, subplot_title, nsubplots, py_map_pckg, latlon_area
        )
        if verif_case_type == 'model2model' and model_num == 1:
            ax_model1 = ax
        # Read data
        if not os.path.exists(model_series_analysis_netcdf_file):
            print("WARNING: "+model_series_analysis_netcdf_file+" "
                  +"does not exist")
            if verif_case_type == 'model2obs' and nmodel == 1:
                ax_obs.set_title('--', loc='right')
            if verif_case_type == 'model2model' \
                    and forecast_anl_diff == 'YES':
                ax_anl.set_title('--', loc='right')
            ax.set_title('--', loc='right')
        else:
            (model_data_series_cnt_FBAR, model_data_series_cnt_OBAR,
             model_data_lat, model_data_lon) = (
                read_series_analysis_file(model_series_analysis_netcdf_file,
                                          var_scale)
            )
            if verif_case_type == 'model2obs':
                if model_num == 1:
                    print("Plotting "+model_obtype+" observations")
                    ax_obs_subplot_loc = str(ax_obs.rowNum)+','+str(ax_obs.colNum)
                    ax_obs_plot_data = model_data_series_cnt_OBAR
                    ax_obs_plot_data_lat = model_data_lat
                    ax_obs_plot_data_lon = model_data_lon
                    ax_obs_plot_levels = levels
                    ax_obs_plot_cmap = cmap
                    CF_ax_obs = plot_subplot_data(
                        ax_obs, map_ax_obs, ax_obs_plot_data,
                        ax_obs_plot_data_lat, ax_obs_plot_data_lon,
                        ax_obs_plot_levels, ax_obs_plot_cmap,
                        py_map_pckg, latlon_area
                    )
                    subplot_CF_dict[ax_obs_subplot_loc] = CF_ax_obs
                print("Plotting "+model+" - "+model_obtype)
                ax_subplot_loc = str(ax.rowNum)+','+str(ax.colNum)
                ax_plot_data = (
                    model_data_series_cnt_FBAR - model_data_series_cnt_OBAR
                 )
                ax_plot_data_lat = model_data_lat
                ax_plot_data_lon = model_data_lon
                ax_plot_levels = levels_diff
                ax_plot_cmap = cmap_diff
                CF_ax = plot_subplot_data(
                    ax, map_ax, ax_plot_data,
                    ax_plot_data_lat, ax_plot_data_lon,
                    ax_plot_levels, ax_plot_cmap,
                    py_map_pckg, latlon_area
                )
                subplot_CF_dict[ax_subplot_loc] = CF_ax
            elif verif_case_type == 'model2model':
                if model_num == 1:
                    print("Plotting "+model)
                    ax_plot_data = model_data_series_cnt_FBAR
                    ax_plot_levels = levels
                    ax_plot_cmap = cmap
                    model1_data_series_cnt_FBAR = model_data_series_cnt_FBAR
                    model1_data_series_cnt_OBAR = model_data_series_cnt_OBAR
                else:
                    print("Plotting "+model+" - "+model1)
                    ax_plot_data = (
                        model_data_series_cnt_FBAR
                        - model1_data_series_cnt_FBAR
                    )
                    ax_plot_levels = levels_diff
                    ax_plot_cmap = cmap_diff
                ax_subplot_loc = str(ax.rowNum)+','+str(ax.colNum)
                ax_plot_data_lat = model_data_lat
                ax_plot_data_lon = model_data_lon
                CF_ax = plot_subplot_data(
                   ax, map_ax, ax_plot_data,
                   ax_plot_data_lat, ax_plot_data_lon,
                   ax_plot_levels, ax_plot_cmap,
                   py_map_pckg, latlon_area
                )
                subplot_CF_dict[ax_subplot_loc] = CF_ax
                if forecast_anl_diff == 'YES':
                    print("Plotting "+model+" - "+model_obtype)
                    ax_anl_subplot_loc = str(ax_anl.rowNum)+','+str(ax_anl.colNum)
                    ax_anl_plot_data = (
                        model_data_series_cnt_FBAR
                        - model_data_series_cnt_OBAR
                    )
                    ax_anl_plot_data_lat = model_data_lat
                    ax_anl_plot_data_lon = model_data_lon
                    ax_anl_plot_levels = levels_diff
                    ax_anl_plot_cmap = cmap_diff
                    CF_ax_anl = plot_subplot_data(
                        ax_anl, map_ax_anl, ax_anl_plot_data,
                        ax_anl_plot_data_lat, ax_anl_plot_data_lon,
                        ax_anl_plot_levels, ax_anl_plot_cmap,
                        py_map_pckg, latlon_area
                    )
                    subplot_CF_dict[ax_anl_subplot_loc] = CF_ax_anl
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
    plt.subplots_adjust(
        left = noaa_img.get_extent()[1]/(plt.rcParams['figure.dpi']*x_figsize),
        right = nws_img.get_extent()[0]/(plt.rcParams['figure.dpi']*x_figsize)
    )
    # Add colorbars
    if verif_case_type == 'model2obs':
        subplot00_pos = ax_obs.get_position()
    elif verif_case_type == 'model2model':
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
        cbar00.ax.set_ylabel(cbar00_title, labelpad=5)
        cbar00.ax.yaxis.set_tick_params(pad=0)
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
                cbar.ax.set_ylabel('Difference', labelpad = 5)
                cbar.ax.yaxis.set_tick_params(pad=0) 
            else:
                cbar.ax.set_xlabel('Difference', labelpad = 0)
                cbar.ax.xaxis.set_tick_params(pad=0) 
    # Build savefig name
    savefig_name = os.path.join(plotting_out_dir_imgs,
                                verif_case_type+'_'+var_group_name
                                +'_'+var_name+'_'+var_level.replace(' ', '')
                                +'_'+forecast_to_plot+'.png')
    print("Saving image as "+savefig_name)
    plt.savefig(savefig_name)
    plt.close()
