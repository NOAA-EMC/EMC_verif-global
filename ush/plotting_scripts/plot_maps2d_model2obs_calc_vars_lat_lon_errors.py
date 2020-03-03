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
import itertools

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

# Exit early if we don't need to run this
# aka not running model2obs
type_list = os.environ['maps2d_type_list'].split(' ')
if 'model2obs' not in type_list:
    print("model2obs verification no requested..."
          +"no need to calculate special variables")
    exit()


# Read in environment variables
machine = os.environ['machine']
DATA = os.environ['DATA']
RUN = os.environ['RUN']
make_met_data_by = os.environ['maps2d_make_met_data_by']
plot_by = os.environ['maps2d_make_met_data_by']
START_DATE = os.environ['start_date']
END_DATE = os.environ['end_date']
forecast_to_plot_list = os.environ['maps2d_forecast_to_plot_list'].split(' ')
regrid_to_grid = os.environ['maps2d_regrid_to_grid']
latlon_area = os.environ['maps2d_latlon_area'].split(' ')
type_list = os.environ['maps2d_type_list'].split(' ')
use_monthly_mean = os.environ['maps2d_model2obs_use_monthly_mean']
use_ceres = os.environ['maps2d_model2obs_use_ceres']
hr_beg = os.environ['maps2d_hr_beg']
hr_end = os.environ['maps2d_hr_end']
hr_inc = os.environ['maps2d_hr_inc']
model_list = os.environ['model_list'].split(' ')
model_plot_name_list = os.environ['maps2d_model_plot_name_list'].split(' ')

# Set up information
verif_case_type = 'model2obs'
var_group_name = 'cloudsrad'
if machine == 'WCOSS_C' or machine == 'WCOSS_DELL_P3':
    py_map_pckg = 'cartopy'
else:
    py_map_pckg = 'basemap' 
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
nmodels = int(len(model_list))

# Plot title information
START_DATE_dt = datetime.datetime.strptime(START_DATE, '%Y%m%d')
END_DATE_dt = datetime.datetime.strptime(END_DATE, '%Y%m%d')
dates_title = (make_met_data_by.lower()+' '
               +START_DATE_dt.strftime('%d%b%Y')+'-'
               +END_DATE_dt.strftime('%d%b%Y'))
make_met_data_by_hrs = []
hr = int(hr_beg) * 3600
while hr <= int(hr_end)*3600:
    make_met_data_by_hrs.append(str(int(hr/3600)).zfill(2)+'Z')
    hr+=int(hr_inc)
make_met_data_by_hrs_title = ', '.join(make_met_data_by_hrs)
forecase_to_plot_title_list = []
    
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

# Loop of variables lat-lon plots
var_info_forcast_to_plot_list = itertools.product(
    ['SWABSORB_atm', 'LWEMIT_atm', 'SWALBDO_sfc'], forecast_to_plot_list
)
for var_info_forcast_to_plot in var_info_forcast_to_plot_list:
    var_name = var_info_forcast_to_plot[0].split('_')[0]
    var_level = var_info_forcast_to_plot[0].split('_')[1]
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
        files_needed_list = [
           forecast_to_plot+'_DSWRF_toa_obsonly.nc',
           forecast_to_plot+'_DSWRF_sfc.nc', 
           forecast_to_plot+'_USWRF_toa.nc',
           forecast_to_plot+'_USWRF_sfc.nc',
        ]
    elif var_name == 'LWEMIT': #longwave emitted
        var_info_title = (
            'Atmospheric Emitted Longwave (W 'r'$\mathregular{m^{-2}}$'')'
        )
        levels = np.array([100,120,140,160,180,200,220,240])
        levels_diff = np.array([-60,-40,-30,-20,-10,0,10,20,30,40,60])
        cmap = plt.cm.cool
        var_scale = 1
        files_needed_list = [
           forecast_to_plot+'_DLWRF_sfc.nc',        
           forecast_to_plot+'_ULWRF_toa.nc',
           forecast_to_plot+'_ULWRF_sfc.nc',
        ]
    elif var_name == 'SWALBDO': #shortwave surface albedo
        var_info_title = 'Shortwave Surface Albedo (fraction)'
        levels = np.array([0.1,0.2,0.4,0.6,0.8,1.0])
        levels_diff = np.array(
            [-0.06,-0.04,-0.03,-0.02,-0.01,0,0.01,0.02,0.03,0.04,0.06]
        )
        cmap = plt.cm.cubehelix_r
        var_scale = 1
        files_needed_list = [
           forecast_to_plot+'_DSWRF_sfc.nc',        
           forecast_to_plot+'_USWRF_sfc.nc',
        ]
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
            # Set up observation subplot map and title
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
                lon_formatter = LongitudeFormatter(zero_direction_label=True)
                lat_formatter = LatitudeFormatter()
                ax_obs.xaxis.set_major_formatter(lon_formatter)
                ax_obs.yaxis.set_major_formatter(lat_formatter)
            elif py_map_pckg == 'basemap':
                ax_obs = plt.subplot(gs[subplot_num])
                mo = Basemap(projection='cyl', llcrnrlat=llcrnrlat_val,
                             urcrnrlat=urcrnrlat_val, llcrnrlon=llcrnrlon_val,
                             urcrnrlon=urcrnrlon_val, resolution='c', lon_0=180,
                             ax=ax_obs)
                mo.drawcoastlines(linewidth=1.5, color='k', zorder=6)
                mo.drawmapboundary
                ax_obs.set_xlabel('Longitude')
                ax_obs.set_ylabel('Latitude')
                mo.drawmeridians(lon_ticks, labels=[False,False,False,True],
                                 fontsize=15)
                mo.drawparallels(lat_ticks, labels=[True,False,False,False],
                                 fontsize=15)
            obtype_subtitle = maps2d_plot_util.get_obs_subplot_title(
                model_obtype, use_monthly_mean
            )
            ax_obs.set_title(obtype_subtitle, loc='left')
        # Set up model subplot map
        subplot_num = model_num
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
        ax.set_title(model_plot_name+'-'+model_obtype, loc='left')
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
            if nmodel == 1:
                ax_obs.set_title(str(np.nan), loc='right')
            ax.set_title(str(np.nan), loc='right')    
        else:
            if var_name == 'SWABSORB': #shortwave absorption
                # DWSRF toa
                DSWRF_toa_obsonly_file  = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_DSWRF_toa_obsonly.nc'
                )
                DSWRF_toa_obsonly_data = netcdf.Dataset(
                    DSWRF_toa_obsonly_file
                )
                DSWRF_toa_obsonly_data_lat = (
                    DSWRF_toa_obsonly_data.variables['lat'][:]
                )
                DSWRF_toa_obsonly_data_lon = (
                    DSWRF_toa_obsonly_data.variables['lon'][:]
                )
                lat = DSWRF_toa_obsonly_data_lat
                lon = DSWRF_toa_obsonly_data_lon
                DSWRF_toa_obsonly_data_variable_names = []
                for var in DSWRF_toa_obsonly_data.variables:
                    DSWRF_toa_obsonly_data_variable_names.append(str(var))
                if 'series_cnt_FBAR' in DSWRF_toa_obsonly_data_variable_names:
                    DSWRF_toa_obsonly_data_series_cnt_FBAR =  (
                        DSWRF_toa_obsonly_data.variables['series_cnt_FBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: FBAR values for "+model+" "
                          +"not in file "+DSWRF_toa_obsonly_file
                          +"...setting to NaN")
                    DSWRF_toa_obsonly_data_series_cnt_FBAR = np.full(
                        (len(DSWRF_toa_obsonly_data_lat),
                         len(DSWRF_toa_obsonly_data_lon)), np.nan
                    )
                if 'series_cnt_OBAR' in DSWRF_toa_obsonly_data_variable_names:
                    DSWRF_toa_obsonly_data_series_cnt_OBAR =  (
                        DSWRF_toa_obsonly_data.variables['series_cnt_OBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: OBAR values for "+model+" "
                          +"not in file "+DSWRF_toa_obsonly_file
                          +"...setting to NaN")
                    DSWRF_toa_obsonly_data_series_cnt_OBAR = np.full(
                        (len(DSWRF_toa_obsonly_data_lat),
                         len(DSWRF_toa_obsonly_data_lon)), np.nan
                    )
                # DSWRF sfc
                DSWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_DSWRF_sfc.nc'
                )
                DSWRF_sfc_data = netcdf.Dataset(
                    DSWRF_sfc_file
                )
                DSWRF_sfc_data_lat = (
                    DSWRF_sfc_data.variables['lat'][:]
                )
                DSWRF_sfc_data_lon = (
                    DSWRF_sfc_data.variables['lon'][:]
                )
                DSWRF_sfc_data_variable_names = []
                for var in DSWRF_sfc_data.variables:
                    DSWRF_sfc_data_variable_names.append(str(var))
                if 'series_cnt_FBAR' in DSWRF_sfc_data_variable_names:
                    DSWRF_sfc_data_series_cnt_FBAR =  (
                        DSWRF_sfc_data.variables['series_cnt_FBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: FBAR values for "+model+" "
                          +"not in file "+DSWRF_sfc_file
                          +"...setting to NaN")
                    DSWRF_sfc_data_series_cnt_FBAR = np.full(
                        (len(DSWRF_sfc_data_lat),
                         len(DSWRF_sfc_data_lon)), np.nan
                    )
                if 'series_cnt_OBAR' in DSWRF_sfc_data_variable_names:
                    DSWRF_sfc_data_series_cnt_OBAR =  (
                        DSWRF_sfc_data.variables['series_cnt_OBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: OBAR values for "+model+" "
                          +"not in file "+DSWRF_sfc_file
                          +"...setting to NaN")
                    DSWRF_sfc_data_series_cnt_OBAR = np.full(
                        (len(DSWRF_sfc_data_lat),
                         len(DSWRF_sfc_data_lon)), np.nan
                    )
                # USWRF toa
                USWRF_toa_file  = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_USWRF_toa.nc'
                )
                USWRF_toa_data = netcdf.Dataset(
                    USWRF_toa_file
                )
                USWRF_toa_data_lat = (
                    USWRF_toa_data.variables['lat'][:]
                )
                USWRF_toa_data_lon = (
                    USWRF_toa_data.variables['lon'][:]
                )
                USWRF_toa_data_variable_names = []
                for var in USWRF_toa_data.variables:
                    USWRF_toa_data_variable_names.append(str(var))
                if 'series_cnt_FBAR' in USWRF_toa_data_variable_names:
                    USWRF_toa_data_series_cnt_FBAR =  (
                        USWRF_toa_data.variables['series_cnt_FBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: FBAR values for "+model+" "
                          +"not in file "+USWRF_toa_file
                          +"...setting to NaN")
                    USWRF_toa_data_series_cnt_FBAR = np.full(
                        (len(USWRF_toa_data_lat),
                         len(USWRF_toa_data_lon)), np.nan
                    )
                if 'series_cnt_OBAR' in USWRF_toa_data_variable_names:
                    USWRF_toa_data_series_cnt_OBAR =  (
                        USWRF_toa_data.variables['series_cnt_OBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: OBAR values for "+model+" "
                          +"not in file "+USWRF_toa_file
                          +"...setting to NaN")
                    USWRF_toa_data_series_cnt_OBAR = np.full(
                        (len(USWRF_toa_data_lat),
                         len(USWRF_toa_data_lon)), np.nan
                    )
                # USWRF sfc
                USWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_USWRF_sfc.nc'
                )
                USWRF_sfc_data = netcdf.Dataset(
                    USWRF_sfc_file
                )
                USWRF_sfc_data_lat = (
                    USWRF_sfc_data.variables['lat'][:]
                )
                USWRF_sfc_data_lon = (
                    USWRF_sfc_data.variables['lon'][:]
                )
                USWRF_sfc_data_variable_names = []
                for var in USWRF_sfc_data.variables:
                    USWRF_sfc_data_variable_names.append(str(var))
                if 'series_cnt_FBAR' in USWRF_sfc_data_variable_names:
                    USWRF_sfc_data_series_cnt_FBAR =  (
                        USWRF_sfc_data.variables['series_cnt_FBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: FBAR values for "+model+" "
                          +"not in file "+USWRF_sfc_file
                          +"...setting to NaN")
                    USWRF_sfc_data_series_cnt_FBAR = np.full(
                        (len(USWRF_sfc_data_lat),
                         len(USWRF_sfc_data_lon)), np.nan
                    )
                if 'series_cnt_OBAR' in USWRF_sfc_data_variable_names:
                    USWRF_sfc_data_series_cnt_OBAR =  (
                        USWRF_sfc_data.variables['series_cnt_OBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: OBAR values for "+model+" "
                          +"not in file "+USWRF_sfc_file
                          +"...setting to NaN")
                    USWRF_sfc_data_series_cnt_OBAR = np.full(
                        (len(USWRF_sfc_data_lat),
                         len(USWRF_sfc_data_lon)), np.nan
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
            elif var_name == 'LWEMIT': #longwave emitted
                # DLWRF sfc
                DLWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_DLWRF_sfc.nc'
                )
                DLWRF_sfc_data = netcdf.Dataset(
                    DLWRF_sfc_file
                )
                DLWRF_sfc_data_lat = (
                    DLWRF_sfc_data.variables['lat'][:]
                )
                DLWRF_sfc_data_lon = (
                    DLWRF_sfc_data.variables['lon'][:]
                )
                lat = DLWRF_sfc_data_lat
                lon = DLWRF_sfc_data_lon
                DLWRF_sfc_data_variable_names = []
                for var in DLWRF_sfc_data.variables:
                    DLWRF_sfc_data_variable_names.append(str(var))
                if 'series_cnt_FBAR' in DLWRF_sfc_data_variable_names:
                    DLWRF_sfc_data_series_cnt_FBAR =  (
                        DLWRF_sfc_data.variables['series_cnt_FBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: FBAR values for "+model+" "
                          +"not in file "+DLWRF_sfc_file
                          +"...setting to NaN")
                    DLWRF_sfc_data_series_cnt_FBAR = np.full(
                        (len(DLWRF_sfc_data_lat),
                         len(DLWRF_sfc_data_lon)), np.nan
                    )
                if 'series_cnt_OBAR' in DLWRF_sfc_data_variable_names:
                    DLWRF_sfc_data_series_cnt_OBAR =  (
                        DLWRF_sfc_data.variables['series_cnt_OBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: OBAR values for "+model+" "
                          +"not in file "+DLWRF_sfc_file
                          +"...setting to NaN")
                    DLWRF_sfc_data_series_cnt_OBAR = np.full(
                        (len(DLWRF_sfc_data_lat),
                         len(DLWRF_sfc_data_lon)), np.nan
                    )
                # ULWRF toa
                ULWRF_toa_file  = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_ULWRF_toa.nc'
                )
                ULWRF_toa_data = netcdf.Dataset(
                    ULWRF_toa_file
                )
                ULWRF_toa_data_lat = (
                    ULWRF_toa_data.variables['lat'][:]
                )   
                ULWRF_toa_data_lon = (
                    ULWRF_toa_data.variables['lon'][:]
                )
                ULWRF_toa_data_variable_names = []
                for var in ULWRF_toa_data.variables:
                    ULWRF_toa_data_variable_names.append(str(var))
                if 'series_cnt_FBAR' in ULWRF_toa_data_variable_names:
                    ULWRF_toa_data_series_cnt_FBAR =  (
                        ULWRF_toa_data.variables['series_cnt_FBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: FBAR values for "+model+" "
                          +"not in file "+ULWRF_toa_file
                          +"...setting to NaN")
                    ULWRF_toa_data_series_cnt_FBAR = np.full(
                        (len(ULWRF_toa_data_lat),
                         len(ULWRF_toa_data_lon)), np.nan
                    )
                if 'series_cnt_OBAR' in ULWRF_toa_data_variable_names:
                    ULWRF_toa_data_series_cnt_OBAR =  (
                        ULWRF_toa_data.variables['series_cnt_OBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: OBAR values for "+model+" "
                          +"not in file "+ULWRF_toa_file
                          +"...setting to NaN")
                    ULWRF_toa_data_series_cnt_OBAR = np.full(
                        (len(ULWRF_toa_data_lat),
                         len(ULWRF_toa_data_lon)), np.nan
                    )
                # ULWRF sfc
                ULWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_ULWRF_sfc.nc'
                )
                ULWRF_sfc_data = netcdf.Dataset(
                    ULWRF_sfc_file
                )
                ULWRF_sfc_data_lat = (
                    ULWRF_sfc_data.variables['lat'][:]
                )
                ULWRF_sfc_data_lon = (
                    ULWRF_sfc_data.variables['lon'][:]
                )
                ULWRF_sfc_data_variable_names = []
                for var in ULWRF_sfc_data.variables:
                    ULWRF_sfc_data_variable_names.append(str(var))
                if 'series_cnt_FBAR' in ULWRF_sfc_data_variable_names:
                    ULWRF_sfc_data_series_cnt_FBAR =  (
                        ULWRF_sfc_data.variables['series_cnt_FBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: FBAR values for "+model+" "
                          +"not in file "+ULWRF_sfc_file
                          +"...setting to NaN")
                    ULWRF_sfc_data_series_cnt_FBAR = np.full(
                        (len(ULWRF_sfc_data_lat),
                         len(ULWRF_sfc_data_lon)), np.nan
                    )
                if 'series_cnt_OBAR' in ULWRF_sfc_data_variable_names:
                    ULWRF_sfc_data_series_cnt_OBAR =  (
                        ULWRF_sfc_data.variables['series_cnt_OBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: OBAR values for "+model+" "
                          +"not in file "+ULWRF_sfc_file
                          +"...setting to NaN")
                    ULWRF_sfc_data_series_cnt_OBAR = np.full(
                        (len(ULWRF_sfc_data_lat),
                         len(ULWRF_sfc_data_lon)), np.nan
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
            elif var_name == 'SWALBDO': #shortwave surface albedo
                # DSWRF sfc
                DSWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_DSWRF_sfc.nc'
                )
                DSWRF_sfc_data = netcdf.Dataset(
                    DSWRF_sfc_file
                )
                DSWRF_sfc_data_lat = (
                    DSWRF_sfc_data.variables['lat'][:]
                )
                DSWRF_sfc_data_lon = (
                    DSWRF_sfc_data.variables['lon'][:]
                )
                lat = DSWRF_sfc_data_lat
                lon = DSWRF_sfc_data_lon
                DSWRF_sfc_data_variable_names = []
                for var in DSWRF_sfc_data.variables:
                    DSWRF_sfc_data_variable_names.append(str(var))
                if 'series_cnt_FBAR' in DSWRF_sfc_data_variable_names:
                    DSWRF_sfc_data_series_cnt_FBAR =  (
                        DSWRF_sfc_data.variables['series_cnt_FBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: FBAR values for "+model+" "
                          +"not in file "+DSWRF_sfc_file
                          +"...setting to NaN")
                    DSWRF_sfc_data_series_cnt_FBAR = np.full(
                        (len(DSWRF_sfc_data_lat),
                         len(DSWRF_sfc_data_lon)), np.nan
                    )
                if 'series_cnt_OBAR' in DSWRF_sfc_data_variable_names:
                    DSWRF_sfc_data_series_cnt_OBAR =  (
                        DSWRF_sfc_data.variables['series_cnt_OBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: OBAR values for "+model+" "
                          +"not in file "+DSWRF_sfc_file
                          +"...setting to NaN")
                    DSWRF_sfc_data_series_cnt_OBAR = np.full(
                        (len(DSWRF_sfc_data_lat),
                         len(DSWRF_sfc_data_lon)), np.nan
                    )
                # USWRF sfc
                USWRF_sfc_file = os.path.join(
                    series_analysis_file_dir, model,
                    forecast_to_plot+'_USWRF_sfc.nc'
                )
                USWRF_sfc_data = netcdf.Dataset(
                    USWRF_sfc_file
                )
                USWRF_sfc_data_lat = (
                    USWRF_sfc_data.variables['lat'][:]
                )
                USWRF_sfc_data_lon = (
                    USWRF_sfc_data.variables['lon'][:]
                )
                USWRF_sfc_data_variable_names = []
                for var in USWRF_sfc_data.variables:
                    USWRF_sfc_data_variable_names.append(str(var))
                if 'series_cnt_FBAR' in USWRF_sfc_data_variable_names:
                    USWRF_sfc_data_series_cnt_FBAR =  (
                        USWRF_sfc_data.variables['series_cnt_FBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: FBAR values for "+model+" "
                          +"not in file "+USWRF_sfc_file
                          +"...setting to NaN")
                    USWRF_sfc_data_series_cnt_FBAR = np.full(
                        (len(USWRF_sfc_data_lat),
                         len(USWRF_sfc_data_lon)), np.nan
                    )
                if 'series_cnt_OBAR' in USWRF_sfc_data_variable_names:
                    USWRF_sfc_data_series_cnt_OBAR =  (
                        USWRF_sfc_data.variables['series_cnt_OBAR'][:]
                        * var_scale
                    )
                else:
                    print("WARNING: OBAR values for "+model+" "
                          +"not in file "+USWRF_sfc_file
                          +"...setting to NaN")
                    USWRF_sfc_data_series_cnt_OBAR = np.full(
                        (len(USWRF_sfc_data_lat),
                         len(USWRF_sfc_data_lon)), np.nan
                    )
                obs_calc_var = (
                    USWRF_sfc_data_series_cnt_OBAR 
                    / DSWRF_sfc_data_series_cnt_OBAR
                )
                model_calc_var = (
                    USWRF_sfc_data_series_cnt_FBAR
                    / DSWRF_sfc_data_series_cnt_FBAR
                )
            if np.ma.is_masked(obs_calc_var):
                np.ma.set_fill_value(obs_calc_var, np.nan)
                obs_calc_var = obs_calc_var.filled()
            if np.ma.is_masked(model_calc_var):
                np.ma.set_fill_value(model_calc_var, np.nan)
                model_calc_var = model_calc_var.filled()
            # Plot observations
            if model_num == 1:
                print("Plotting "+model_obtype+" observations")
                # Add cyclic point for obs data 
                if py_map_pckg == 'cartopy':
                    obs_calc_var_cyc, lon_cyc = (
                        add_cyclic_point(obs_calc_var,
                                         coord=lon)
                    )
                elif py_map_pckg == 'basemap':
                    obs_calc_var_cyc, lon_cyc = addcyclic(
                        obs_calc_var, lon
                    )
                xo, yo = np.meshgrid(lon_cyc, lat)
                obs_area_avg = maps2d_plot_util.calculate_area_average(
                    obs_calc_var, lat, lon,
                    llcrnrlat_val, urcrnrlat_val, llcrnrlon_val, urcrnrlon_val
                )
                ax_obs.set_title(round(obs_area_avg, 3), loc='right')
                if np.all(np.isnan(levels)):
                    if np.isnan(np.nanmax(obs_calc_var)):
                        levels_max = 1
                    else:
                        levels_max = int(
                            np.nanmax(obs_calc_var)
                        ) + 1
                    if np.isnan(np.nanmin(obs_calc_var)):
                        levels_min = -1
                    else:
                        levels_min = int(
                            np.nanmin(obs_calc_var)
                        ) - 1
                    levels = np.linspace(levels_min, levels_max, 11,
                                         endpoint=True)
                if np.count_nonzero(
                        ~np.isnan(obs_calc_var)) != 0:
                    if py_map_pckg == 'cartopy':
                        CF1 = ax_obs.contourf(xo, yo,
                                              obs_calc_var_cyc,
                                              transform=ccrs.PlateCarree(),
                                              levels=levels, cmap=cmap,
                                              extend='both')
                        # matplotlib/cartopy tries to close contour when
                        # using cylic point, so need to plot contours
                        # set contour labels, remove contour lines, and then
                        # replot contour lines
                        C1 = ax_obs.contour(xo, yo,
                                            obs_calc_var_cyc,
                                            transform=ccrs.PlateCarree(),
                                            levels=levels, colors='k',
                                            linewidths=1.0, extend='both')
                        C1labels = ax_obs.clabel(C1, C1.levels,
                                                 fmt='%g', colors='k')
                        for c in C1.collections:
                            c.set_visible(False)
                        C1 = ax_obs.contour(xo, yo,
                                            obs_calc_var_cyc,
                                            transform=ccrs.PlateCarree(),
                                            levels=levels, colors='k',
                                            linewidths=1.0, extend='both')
                    elif py_map_pckg == 'basemap':
                        mox, moy = mo(xo, yo)
                        CF1 = mo.contourf(mox, moy,
                                          obs_calc_var_cyc,
                                          levels=levels, cmap=cmap,
                                          extend='both')
                        C1 = mo.contour(mox, moy,
                                        obs_calc_var_cyc,
                                        levels=levels, colors='k',
                                        linewidths=1.0, extend='both')
                        C1labels = ax_obs.clabel(C1, C1.levels,
                                                 fmt='%g', colors='k')
            # Plot model - obs
            print("Plotting "+model+" - "+model_obtype)
            # Add cyclic point for model data
            if py_map_pckg == 'cartopy':
                model_calc_var_cyc, lon_cyc = (
                    add_cyclic_point(model_calc_var,
                                     coord=lon)
                )
            elif py_map_pckg == 'basemap':
                model_calc_var_cyc, lon_cyc = addcyclic(
                    model_calc_var, lon
                )
            model_obs_diff_calc_var = (
                model_calc_var - obs_calc_var
            )
            model_obs_diff_calc_var_cyc = (
                model_calc_var_cyc - obs_calc_var_cyc
            )
            x, y = np.meshgrid(lon_cyc, lat)
            model_obs_diff_area_avg = maps2d_plot_util.calculate_area_average(
                model_calc_var - obs_calc_var, lat, lon,
                llcrnrlat_val, urcrnrlat_val, llcrnrlon_val, urcrnrlon_val
            )
            ax.set_title(round(model_obs_diff_area_avg, 3), loc='right')
            if np.count_nonzero(
                        ~np.isnan(model_calc_var - obs_calc_var)) != 0:
                    if py_map_pckg == 'cartopy':
                        CF = ax.contourf(x, y,
                                         model_obs_diff_calc_var_cyc,
                                         transform=ccrs.PlateCarree(),
                                         levels=levels_diff, cmap=cmap_diff,
                                         extend='both')
                    elif py_map_pckg == 'basemap':
                        mx, my = m(x, y)
                        CF = m.contourf(mx, my,
                                        model_obs_diff_calc_var_cyc,
                                        levels=levels_diff, cmap=cmap_diff,
                                        extend='both')
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
                                +'_'+var_name+'_'+var_level
                                +'_'+forecast_to_plot+'.png')
    print("Saving image as "+savefig_name)
    plt.savefig(savefig_name, bbox_inches='tight')
    link_image_dir = os.path.join(
        DATA, RUN, 'metplus_output', 'images/.'
    )
    print("Linking image to "+link_image_dir)
    os.system('ln -sf '+savefig_name+' '+link_image_dir)
    plt.close()
