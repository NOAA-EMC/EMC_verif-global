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
plt.rcParams['axes.labelsize'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.formatter.useoffset'] = False
###import cmocean
###cmap_diff = cmocean.cm.balance
cmap_diff = plt.cm.coolwarm
noaa_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'noaa.png')
)

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
llcrnrlat_val = float(latlon_area[0])
urcrnrlat_val = float(latlon_area[1])
llcrnrlon_val = float(latlon_area[2])
urcrnrlon_val = float(latlon_area[3])
lat_ticks = np.linspace(llcrnrlat_val, urcrnrlat_val, 7, endpoint=True)
lon_ticks = np.linspace(llcrnrlon_val, urcrnrlon_val, 7, endpoint=True)
env_var_model_list = []
regex = re.compile(r'model(\d+)$')
for key in os.environ.keys():
    result = regex.match(key)
    if result is not None:
        env_var_model_list.append(result.group(0))
env_var_model_list = sorted(env_var_model_list, key=lambda m: m[-1])
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
    var_info_title, levels, levels_diff, cmap, var_scale = (
        maps2d_plot_util.get_maps2d_plot_settings(var_name, var_level) 
    )
    model_num = 0
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
            if nsubplots > 8:
                print("Too many subplots requested. Current maximum is 8.")
                exit(1)
            if nsubplots == 1:
                fig = plt.figure(figsize=(10,12))
                gs = gridspec.GridSpec(1,1)
            elif nsubplots == 2:
                fig = plt.figure(figsize=(10,12))
                gs = gridspec.GridSpec(2,1)
                gs.update(hspace=0.2)
            elif nsubplots > 2 and nsubplots <= 4:
                fig = plt.figure(figsize=(20,12))
                gs = gridspec.GridSpec(2,2)
                gs.update(wspace=0.2, hspace=0.2)
            elif nsubplots > 4 and nsubplots <= 6:
                fig = plt.figure(figsize=(30,12))
                gs = gridspec.GridSpec(2,3)
                gs.update(wspace=0.2, hspace=0.2)
            elif nsubplots > 6 and nsubplots <= 9:
                fig = plt.figure(figsize=(30,18))
                gs = gridspec.GridSpec(3,3)
                gs.update(wspace=0.2, hspace=0.2)
            # Set up observation subplot map and title, if needed
            if verif_case_type == 'model2obs':
                if py_map_pckg == 'cartopy':
                    ax_obs = plt.subplot(gs[0],
                                         projection=ccrs.PlateCarree(
                                             central_longitude=180
                                         ))
                    if urcrnrlon_val == 360:
                        urcrnrlon_val_adjust = 359.9
                    else:
                        urcrnrlon_val_adjust = urcrnrlon_val
                    ax_obs.set_extent(
                        [llcrnrlon_val, urcrnrlon_val_adjust,
                         llcrnrlat_val, urcrnrlat_val],
                        ccrs.PlateCarree()
                    )
                    ax_obs.set_global()
                    ax_obs.coastlines()
                    ax_obs.set_xlabel('Longitude')
                    ax_obs.set_xticks(lon_ticks, crs=ccrs.PlateCarree())
                    ax_obs.set_ylabel('Latitude')
                    ax_obs.set_yticks(lat_ticks, crs=ccrs.PlateCarree())
                    lon_formatter = LongitudeFormatter(
                        zero_direction_label=True
                    )
                    lat_formatter = LatitudeFormatter()
                    ax_obs.xaxis.set_major_formatter(lon_formatter)
                    ax_obs.yaxis.set_major_formatter(lat_formatter)
                elif py_map_pckg == 'basemap':
                    ax_obs = plt.subplot(gs[0])
                    mo = Basemap(projection='cyl',
                                 llcrnrlat=llcrnrlat_val,
                                 urcrnrlat=urcrnrlat_val,
                                 llcrnrlon=llcrnrlon_val,
                                 urcrnrlon=urcrnrlon_val,
                                 resolution='c', lon_0=180, ax=ax_obs)
                    mo.drawcoastlines(linewidth=1.5, color='k', zorder=6)
                    mo.drawmapboundary
                    ax_obs.set_xlabel('Longitude')
                    ax_obs.set_ylabel('Latitude')
                    mo.drawmeridians(lon_ticks,
                                     labels=[False,False,False,True],
                                     fontsize=15)
                    mo.drawparallels(lat_ticks,
                                     labels=[True,False,False,False],
                                     fontsize=15)
                obtype_subtitle = maps2d_plot_util.get_obs_subplot_title(
                    model_obtype, use_monthly_mean
                )
                ax_obs.set_title(obtype_subtitle, loc='left')
        # Set up analysis subplot map and title, if needed
        if verif_case_type == 'model2model' and forecast_anl_diff == 'YES':
            if py_map_pckg == 'cartopy':
                ax_anl = plt.subplot(gs[(2 * (model_num - 1) + 1)],
                                     projection=ccrs.PlateCarree(
                                         central_longitude=180
                                     ))
                if urcrnrlon_val == 360:
                    urcrnrlon_val_adjust = 359.9
                else:
                    urcrnrlon_val_adjust = urcrnrlon_val
                ax_anl.set_extent(
                    [llcrnrlon_val, urcrnrlon_val_adjust,
                     llcrnrlat_val, urcrnrlat_val],
                    ccrs.PlateCarree()
                )
                ax_anl.set_global()
                ax_anl.coastlines()
                ax_anl.set_xlabel('Longitude')
                ax_anl.set_xticks(lon_ticks, crs=ccrs.PlateCarree())
                ax_anl.set_ylabel('Latitude')
                ax_anl.set_yticks(lat_ticks, crs=ccrs.PlateCarree())
                lon_formatter = LongitudeFormatter(
                    zero_direction_label=True
                )
                lat_formatter = LatitudeFormatter()
                ax_anl.xaxis.set_major_formatter(lon_formatter)
                ax_anl.yaxis.set_major_formatter(lat_formatter)
            elif py_map_pckg == 'basemap':
                ax_anl = plt.subplot(gs[(2 * (model_num - 1) + 1)])
                ma = Basemap(projection='cyl',
                             llcrnrlat=llcrnrlat_val,
                             urcrnrlat=urcrnrlat_val,
                             llcrnrlon=llcrnrlon_val,
                             urcrnrlon=urcrnrlon_val,
                             resolution='c', lon_0=180, ax=ax_anl)
                ma.drawcoastlines(linewidth=1.5, color='k', zorder=6)
                ma.drawmapboundary
                ax_anl.set_xlabel('Longitude')
                ax_anl.set_ylabel('Latitude')
                ma.drawmeridians(lon_ticks,
                                 labels=[False,False,False,True],
                                 fontsize=15)
                ma.drawparallels(lat_ticks,
                                 labels=[True,False,False,False],
                                 fontsize=15)
            ax_anl.set_title(model_plot_name+'-'+model_obtype, loc='left') 
        # Set up model subplot map and title
        if verif_case_type == 'model2obs':
            subplot_num = model_num
        elif verif_case_type == 'model2model': 
            if forecast_anl_diff == 'YES':
                subplot_num = 2 * (model_num - 1)
            else:
                subplot_num =  model_num - 1
        if py_map_pckg == 'cartopy':
            ax = plt.subplot(gs[subplot_num], 
                             projection=ccrs.PlateCarree(
                                 central_longitude=180
                             ))
            if urcrnrlon_val == 360:
                urcrnrlon_val_adjust = 359.9
            else:
                urcrnrlon_val_adjust = urcrnrlon_val
            ax.set_extent(
                [llcrnrlon_val, urcrnrlon_val_adjust,
                 llcrnrlat_val, urcrnrlat_val],
                ccrs.PlateCarree()
            )
            ax.set_global()
            ax.coastlines()
            ax.set_xlabel('Longitude')
            ax.set_xticks(lon_ticks, crs=ccrs.PlateCarree())
            ax.set_ylabel('Latitude')
            ax.set_yticks(lat_ticks, crs=ccrs.PlateCarree())
            lon_formatter = LongitudeFormatter(zero_direction_label=True)
            lat_formatter = LatitudeFormatter()
            ax.xaxis.set_major_formatter(lon_formatter)
            ax.yaxis.set_major_formatter(lat_formatter)
        elif py_map_pckg == 'basemap':
            ax = plt.subplot(gs[subplot_num])
            m = Basemap(projection='cyl', llcrnrlat=llcrnrlat_val,
                        urcrnrlat=urcrnrlat_val, llcrnrlon=llcrnrlon_val,
                        urcrnrlon=urcrnrlon_val, resolution='c', lon_0=180,
                        ax=ax)
            m.drawcoastlines(linewidth=1.5, color='k', zorder=6)
            m.drawmapboundary
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            m.drawmeridians(lon_ticks, labels=[False,False,False,True],
                            fontsize=15)
            m.drawparallels(lat_ticks, labels=[True,False,False,False],
                            fontsize=15)
        if verif_case_type == 'model2obs':
            ax.set_title(model_plot_name+'-'+model_obtype, loc='left')
        elif verif_case_type == 'model2model':
            if model_num == 1:
                model1 = model
                model1_plot_name = model_plot_name
                ax.set_title(model1_plot_name, loc='left')
            else:
                ax.set_title(model_plot_name+'-'+model1_plot_name, loc='left')
        # Read data
        if not os.path.exists(model_series_analysis_netcdf_file):
            print("WARNING: "+model_series_analysis_netcdf_file+" "
                  +"does not exist")
            if nmodel == 1:
                ax_obs.set_title(str(np.nan), loc='left') 
            ax.set_title(str(np.nan), loc='left')
        else:
            print(model_series_analysis_netcdf_file+" exists")
            model_data = netcdf.Dataset(model_series_analysis_netcdf_file)
            model_data_lat = model_data.variables['lat'][:]
            model_data_lon = model_data.variables['lon'][:]
            model_data_variable_names = []
            for var in model_data.variables:
                model_data_variable_names.append(str(var))
            if 'series_cnt_FBAR' in model_data_variable_names:
                model_data_series_cnt_FBAR =  (
                    model_data.variables['series_cnt_FBAR'][:] * var_scale
                )
            else:
                print("WARNING: FBAR values for "+model+" "
                      +"not in file "+model_series_analysis_netcdf_file
                      +"...setting to NaN")
                model_data_series_cnt_FBAR = np.full(
                    (len(model_data_lat), len(model_data_lon)), np.nan
                )
            if 'series_cnt_OBAR' in model_data_variable_names:
                model_data_series_cnt_OBAR =  (
                    model_data.variables['series_cnt_OBAR'][:] * var_scale
                )
            else:
                print("WARNING: OBAR values for "+model+" "
                      +"not in file "+model_series_analysis_netcdf_file
                      +"...setting to NaN")
                model_data_series_cnt_OBAR = np.full(
                    (len(model_data_lat), len(model_data_lon)), np.nan
                )
            if np.ma.is_masked(model_data_series_cnt_FBAR):
                np.ma.set_fill_value(model_data_series_cnt_FBAR, np.nan)
                model_data_series_cnt_FBAR = (
                    model_data_series_cnt_FBAR.filled()
                )
            if np.ma.is_masked(model_data_series_cnt_OBAR):
                np.ma.set_fill_value(model_data_series_cnt_OBAR, np.nan)
                model_data_series_cnt_OBAR = (
                    model_data_series_cnt_OBAR.filled()
                )
            # Add cyclic point for model data
            if py_map_pckg == 'cartopy':
                model_data_series_cnt_FBAR_cyc, model_data_lon_cyc = (
                    add_cyclic_point(model_data_series_cnt_FBAR,
                                     coord=model_data_lon)
                )
                model_data_series_cnt_OBAR_cyc, model_data_lon_cyc = (
                    add_cyclic_point(model_data_series_cnt_OBAR,
                                     coord=model_data_lon)
                )
            elif py_map_pckg == 'basemap':
                model_data_series_cnt_FBAR_cyc, model_data_lon_cyc = addcyclic(
                    model_data_series_cnt_FBAR, model_data_lon
                )
                model_data_series_cnt_OBAR_cyc, model_data_lon_cyc = addcyclic(
                    model_data_series_cnt_OBAR, model_data_lon
                )
            # Plot model data
            x, y = np.meshgrid(model_data_lon_cyc, model_data_lat)
            if verif_case_type == 'model2obs':
                if model_num == 1:
                    print("Plotting "+model_obtype+" observations")
                    obs_area_avg = maps2d_plot_util.calculate_area_average(
                        model_data_series_cnt_OBAR, model_data_lat,
                        model_data_lon, llcrnrlat_val, urcrnrlat_val,
                        llcrnrlon_val, urcrnrlon_val
                    )
                    ax_obs.set_title(round(obs_area_avg, 3), loc='right')
                    if np.all(np.isnan(levels)):
                        if np.isnan(np.nanmax(model_data_series_cnt_OBAR)):
                            levels_max = 1
                        else:
                            levels_max = int(
                                np.nanmax(model_data_series_cnt_OBAR)
                             ) + 1
                        if np.isnan(np.nanmin(model_data_series_cnt_OBAR)):
                            levels_min = -1
                        else:
                            levels_min = int(
                                np.nanmin(model_data_series_cnt_OBAR)
                            ) - 1
                        levels = np.linspace(levels_min, levels_max, 11,
                                             endpoint=True)
                    if np.count_nonzero(~np.isnan(
                            model_data_series_cnt_OBAR_cyc
                            )) != 0:
                        if py_map_pckg == 'cartopy':
                            CF1 = ax_obs.contourf(
                                x, y, model_data_series_cnt_OBAR_cyc,
                                transform=ccrs.PlateCarree(),
                                levels=levels, cmap=cmap, extend='both'
                            )
                            # matplotlib/cartopy tries to close contour when
                            # using cylic point, so need to plot contours
                            # set contour labels, remove contour lines, and
                            # then replot contour lines
                            C1 = ax_obs.contour(
                                x, y, model_data_series_cnt_OBAR_cyc,
                                transform=ccrs.PlateCarree(),
                                levels=levels, colors='k',
                                linewidths=1.0, extend='both'
                            )
                            C1labels = ax_obs.clabel(
                                C1, C1.levels, fmt='%g', colors='k'
                            )
                            for c in C1.collections:
                                 c.set_visible(False)
                            C1 = ax_obs.contour(
                                x, y, model_data_series_cnt_OBAR_cyc,
                                transform=ccrs.PlateCarree(),
                                levels=levels, colors='k',
                                linewidths=1.0, extend='both'
                            )
                        elif py_map_pckg == 'basemap':
                            mox, moy = mo(x, y)
                            CF1 = mo.contourf(
                                mox, moy, model_data_series_cnt_OBAR_cyc,
                                levels=levels, cmap=cmap, extend='both'
                            )
                            C1 = mo.contour(
                                mox, moy, model_data_series_cnt_OBAR_cyc,
                                levels=levels, colors='k',
                                linewidths=1.0, extend='both'
                            )
                            C1labels = ax_obs.clabel(
                                C1, C1.levels, fmt='%g', colors='k'
                            )
                print("Plotting "+model+" - "+model_obtype)
                model_data_series_cnt_FBAR_OBAR_diff = (
                    model_data_series_cnt_FBAR
                    - model_data_series_cnt_OBAR
                 )
                model_FBAR_OBAR_diff_area_avg = (
                    maps2d_plot_util.calculate_area_average(
                        model_data_series_cnt_FBAR_OBAR_diff, model_data_lat,
                        model_data_lon, llcrnrlat_val, urcrnrlat_val,
                        llcrnrlon_val, urcrnrlon_val
                    )
                )
                ax.set_title(round(model_FBAR_OBAR_diff_area_avg, 3),
                             loc='right')
                model_data_series_cnt_FBAR_OBAR_diff_cyc = (
                    model_data_series_cnt_FBAR_cyc
                    - model_data_series_cnt_OBAR_cyc
                )
                if np.count_nonzero(~np.isnan(
                        model_data_series_cnt_FBAR_OBAR_diff_cyc
                        )) != 0:
                    if py_map_pckg == 'cartopy':
                        CF = ax.contourf(
                            x, y, model_data_series_cnt_FBAR_OBAR_diff_cyc,
                            transform=ccrs.PlateCarree(),
                            levels=levels_diff, cmap=cmap_diff, extend='both'
                        )
                    elif py_map_pckg == 'basemap':
                        mx, my = m(x, y)
                        CF = ma.contourf(
                             mx, my, model_data_series_cnt_FBAR_OBAR_diff_cyc,
                             levels=levels_diff, cmap=cmap_diff, extend='both'
                        )
            elif verif_case_type == 'model2model':
                if model_num == 1:
                    print("Plotting "+model)
                    model1_area_avg = maps2d_plot_util.calculate_area_average(
                        model_data_series_cnt_FBAR, model_data_lat,
                        model_data_lon, llcrnrlat_val, urcrnrlat_val,
                        llcrnrlon_val, urcrnrlon_val
                    )
                    ax.set_title(round(model1_area_avg, 3), loc='right')
                    if np.all(np.isnan(levels)):
                        if np.isnan(np.nanmax(model_data_series_cnt_FBAR)):
                            levels_max = 1
                        else:
                            levels_max = int(
                                np.nanmax(model_data_series_cnt_FBAR)
                            ) + 1
                        if np.isnan(np.nanmin(model_data_series_cnt_FBAR)):
                            levels_min = -1
                        else: 
                            levels_min = int(
                                 np.nanmin(model_data_series_cnt_FBAR)
                            ) - 1
                        levels = np.linspace(levels_min, levels_max, 11,
                                             endpoint=True)
                    if np.count_nonzero(~np.isnan(
                            model_data_series_cnt_FBAR_cyc
                            )) != 0:
                        if py_map_pckg == 'cartopy':
                            CF1 = ax.contourf(
                                 x, y, model_data_series_cnt_FBAR_cyc,
                                 transform=ccrs.PlateCarree(),
                                 levels=levels, cmap=cmap, extend='both'
                            )
                            # matplotlib/cartopy tries to close contour when
                            # using cylic point, so need to plot contours
                            # set contour labels, remove contour lines, and
                            # then replot contour lines
                            C1 = ax.contour(
                                x, y, model_data_series_cnt_FBAR_cyc,
                                transform=ccrs.PlateCarree(),
                                levels=levels, colors='k',
                                linewidths=1.0, extend='both'
                            )
                            C1labels = ax.clabel(
                                C1, C1.levels, fmt='%g', colors='k'
                            )
                            for c in C1.collections:
                                c.set_visible(False)
                            C1 = ax.contour(
                                x, y, model_data_series_cnt_FBAR_cyc,
                                transform=ccrs.PlateCarree(),
                                levels=levels, colors='k',
                                linewidths=1.0, extend='both'
                            )
                        elif py_map_pckg == 'basemap':
                            mx, my = m(x, y)
                            CF1 = m.contourf(
                                mx, my, model_data_series_cnt_FBAR_cyc,
                                levels=levels, cmap=cmap, extend='both'
                            )
                            C1 = m.contour(
                                mx, my, model_data_series_cnt_FBAR_cyc,
                                levels=levels, colors='k',
                                linewidths=1.0, extend='both'
                            )
                            C1labels = ax.clabel(
                                 C1, C1.levels, fmt='%g', colors='k'
                            )
                    model1_data_series_cnt_FBAR = model_data_series_cnt_FBAR
                    model1_data_series_cnt_FBAR_cyc = (
                        model_data_series_cnt_FBAR_cyc
                     )
                    model1_data_series_cnt_OBAR_cyc = (
                        model_data_series_cnt_OBAR_cyc
                    )
                else:
                    print("Plotting "+model+" - "+model1)
                    model_model1_data_series_cnt_FBAR_diff = (
                        model_data_series_cnt_FBAR
                        - model1_data_series_cnt_FBAR
                    )
                    model_model1_diff_area_avg = (
                        maps2d_plot_util.calculate_area_average(
                            model_model1_data_series_cnt_FBAR_diff,
                            model_data_lat, model_data_lon,
                            llcrnrlat_val, urcrnrlat_val,
                            llcrnrlon_val, urcrnrlon_val
                        )
                    )
                    ax.set_title(round(model_model1_diff_area_avg, 3),
                                 loc='right')
                    model_model1_data_series_cnt_FBAR_diff_cyc = (
                        model_data_series_cnt_FBAR_cyc
                        - model1_data_series_cnt_FBAR_cyc
                    )
                    if np.count_nonzero(~np.isnan(
                           model_model1_data_series_cnt_FBAR_diff_cyc
                          )) != 0:
                       if py_map_pckg == 'cartopy':
                            CF = ax.contourf(
                                x, y,
                                model_model1_data_series_cnt_FBAR_diff_cyc,
                                transform=ccrs.PlateCarree(),
                                levels=levels_diff, cmap=cmap_diff,
                                extend='both'
                            )
                       elif py_map_pckg == 'basemap':
                            mx, my = m(x, y)
                            CF = m.contourf(
                                mx, my,
                                model_model1_data_series_cnt_FBAR_diff_cyc,
                                levels=levels_diff, cmap=cmap_diff,
                                extend='both'
                            )
                if forecast_anl_diff == 'YES':
                    print("Plotting "+model+" - "+model_obtype)
                    model_data_series_cnt_FBAR_OBAR_diff = (
                        model_data_series_cnt_FBAR
                        - model_data_series_cnt_OBAR
                    )
                    model_FBAR_OBAR_diff_area_avg = (
                        maps2d_plot_util.calculate_area_average(
                            model_data_series_cnt_FBAR_OBAR_diff,
                            model_data_lat, model_data_lon,
                            llcrnrlat_val, urcrnrlat_val,
                            llcrnrlon_val, urcrnrlon_val
                        )
                    )
                    ax_anl.set_title(round(model_FBAR_OBAR_diff_area_avg, 3),
                                     loc='right')
                    model_data_series_cnt_FBAR_OBAR_diff_cyc = (
                        model_data_series_cnt_FBAR_cyc
                       - model_data_series_cnt_OBAR_cyc
                    )
                    if np.count_nonzero(~np.isnan(
                            model_data_series_cnt_FBAR_OBAR_diff_cyc
                            )) != 0:
                        if py_map_pckg == 'cartopy':
                            CF = ax_anl.contourf(
                                 x, y, model_data_series_cnt_FBAR_OBAR_cyc,
                                 transform=ccrs.PlateCarree(),
                                 levels=levels_diff, cmap=cmap_diff,
                                 extend='both'
                            )
                        elif py_map_pckg == 'basemap':
                            max, may = ma(x, y)
                            CF = ma.contourf(
                                max, may,
                                model_data_series_cnt_FBAR_OBAR_cyc,
                                levels=levels_diff, cmap=cmap_diff,
                                extend='both'
                            )
    # Final touches and save plot
    if nmodels > 1 or \
            (nmodels == 1 and forecast_anl_diff == 'YES') or \
            (nmodels == 1 and verif_case_type == 'model2obs'):
        cax = fig.add_axes([0.1, 0.0, 0.8, 0.05])
        cbar = fig.colorbar(CF, cax=cax, orientation='horizontal',
                            ticks=levels_diff)
        cbar.ax.set_xlabel('Difference')
    full_title = (
        var_info_title+' Mean Error\n'
        +dates_title+' '+make_met_data_by_hrs_title+', '
        +forecast_to_plot_title
    )
    fig.suptitle(full_title, fontsize=18, fontweight='bold')
    noaa_img_axes = fig.add_axes([-0.01, 0.0, 0.01, 0.01])
    noaa_img_axes.axes.get_xaxis().set_visible(False)
    noaa_img_axes.axes.get_yaxis().set_visible(False)
    noaa_img_axes.axis('off')
    fig.figimage(noaa_logo_img_array, 1, 1, zorder=1, alpha=0.5)
    savefig_name = os.path.join(plotting_out_dir_imgs,
                                verif_case_type+'_'+var_group_name
                                +'_'+var_name+'_'+var_level.replace(' ', '')
                                +'_'+forecast_to_plot+'.png')
    print("Saving image as "+savefig_name)
    plt.savefig(savefig_name, bbox_inches='tight')
    plt.close()
