'''
Program Name: check_config_settings.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This does a check on the user's settings in
          the passed config file.
'''

import sys
import os
import datetime
import calendar

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
RUN = os.environ['RUN']
RUN_abbrev = os.environ['RUN_abbrev']

# Do check for all environment variables needed by config
RUN_type_env_vars_dict = {
    'shared': ['model_list', 'model_dir_list', 'model_stat_dir_list',
               'model_file_format_list', 'model_data_run_hpss',
               'model_hpss_dir_list', 'hpss_walltime', 'OUTPUTROOT',
               'start_date', 'end_date', 'spinup_period_start',
               'spinup_period_end', 'make_met_data_by', 'plot_by',
               'SEND2WEB', 'webhost', 'webhostid', 'webdir', 'img_quality',
               'MET_version', 'METplus_version', 'METplus_verbosity',
               'MET_verbosity', 'log_MET_output_to_METplus', 'SENDARCH',
               'SENDMETVIEWER', 'KEEPDATA', 'SENDECF', 'SENDCOM', 'SENDDBN',
               'SENDDBN_NTC'],
    'RUN_GRID2GRID_STEP1': ['g2g1_type_list', 'g2g1_anom_truth_name',
                            'g2g1_anom_truth_file_format_list',
                            'g2g1_anom_fcyc_list', 'g2g1_anom_vhr_list',
                            'g2g1_anom_fhr_min', 'g2g1_anom_fhr_max',
                            'g2g1_anom_grid', 'g2g1_anom_gather_by',
                            'g2g1_pres_truth_name',
                            'g2g1_pres_truth_file_format_list',
                            'g2g1_pres_fcyc_list', 'g2g1_anom_vhr_list',
                            'g2g1_pres_fhr_min', 'g2g1_pres_fhr_max',
                            'g2g1_pres_grid', 'g2g1_pres_gather_by',
                            'g2g1_sfc_truth_name',
                            'g2g1_sfc_truth_file_format_list',
                            'g2g1_sfc_fcyc_list', 'g2g1_anom_vhr_list',
                            'g2g1_sfc_fhr_min', 'g2g1_sfc_fhr_max',
                            'g2g1_sfc_grid', 'g2g1_sfc_gather_by',
                            'g2g1_mv_database_name', 'g2g1_mv_database_group',
                            'g2g1_mv_database_desc'],
    'RUN_GRID2GRID_STEP2': ['g2g2_model_plot_name_list', 'g2g2_type_list',
                            'g2g2_anom_truth_name_list',
                            'g2g2_anom_gather_by_list', 'g2g2_anom_fcyc_list',
                            'g2g2_anom_vhr_list', 'g2g2_anom_fhr_min',
                            'g2g2_anom_fhr_max', 'g2g2_anom_event_eq',
                            'g2g2_anom_grid', 'g2g2_pres_truth_name_list',
                            'g2g2_pres_gather_by_list', 'g2g2_pres_fcyc_list',
                            'g2g2_pres_vhr_list', 'g2g2_pres_fhr_min',
                            'g2g2_pres_fhr_max', 'g2g2_pres_event_eq',
                            'g2g2_pres_grid', 'g2g2_sfc_truth_name_list',
                            'g2g2_sfc_gather_by_list', 'g2g2_sfc_fcyc_list',
                            'g2g2_sfc_vhr_list', 'g2g2_sfc_fhr_min',
                            'g2g2_sfc_fhr_max', 'g2g2_sfc_event_eq',
                            'g2g2_sfc_grid', 'g2g2_make_scorecard'],
    'RUN_GRID2OBS_STEP1': ['g2o1_type_list',
                           'g2o1_upper_air_msg_type_list',
                           'g2o1_upper_air_fcyc_list',
                           'g2o1_upper_air_vhr_list', 'g2o1_upper_air_fhr_min',
                           'g2o1_upper_air_fhr_max', 'g2o1_upper_air_grid',
                           'g2o1_upper_air_gather_by',
                           'g2o1_conus_sfc_msg_type_list',
                           'g2o1_conus_sfc_fcyc_list',
                           'g2o1_conus_sfc_vhr_list', 'g2o1_conus_sfc_fhr_min',
                           'g2o1_conus_sfc_fhr_max', 'g2o1_conus_sfc_grid',
                           'g2o1_conus_sfc_gather_by',
                           'g2o1_polar_sfc_msg_type_list',
                           'g2o1_polar_sfc_fcyc_list',
                           'g2o1_polar_sfc_vhr_list', 'g2o1_polar_sfc_fhr_min',
                           'g2o1_polar_sfc_fhr_max', 'g2o1_polar_sfc_grid',
                           'g2o1_polar_sfc_gather_by',
                           'g2o1_prepbufr_data_run_hpss',
                           'g2o1_mv_database_name', 'g2o1_mv_database_group',
                           'g2o1_mv_database_desc'],
    'RUN_GRID2OBS_STEP2': ['g2o2_model_plot_name_list', 'g2o2_type_list',
                           'g2o2_upper_air_msg_type_list',
                           'g2o2_upper_air_gather_by_list',
                           'g2o2_upper_air_fcyc_list',
                           'g2o2_upper_air_vhr_list', 'g2o2_upper_air_fhr_min',
                           'g2o2_upper_air_fhr_max', 'g2o2_upper_air_event_eq',
                           'g2o2_upper_air_grid',
                           'g2o2_conus_sfc_msg_type_list',
                           'g2o2_conus_sfc_gather_by_list',
                           'g2o2_conus_sfc_fcyc_list',
                           'g2o2_conus_sfc_vhr_list', 'g2o2_conus_sfc_fhr_min',
                           'g2o2_conus_sfc_fhr_max', 'g2o2_conus_sfc_event_eq',
                           'g2o2_conus_sfc_grid',
                           'g2o2_polar_sfc_msg_type_list',
                           'g2o2_polar_sfc_gather_by_list',
                           'g2o2_polar_sfc_fcyc_list',
                           'g2o2_polar_sfc_vhr_list', 'g2o2_polar_sfc_fhr_min',
                           'g2o2_polar_sfc_fhr_max', 'g2o2_polar_sfc_event_eq',
                           'g2o2_polar_sfc_grid'],
    'RUN_PRECIP_STEP1': ['precip1_type_list',
                         'precip1_ccpa_accum24hr_model_bucket_list',
                         'precip1_ccpa_accum24hr_model_var_list',
                         'precip1_ccpa_accum24hr_model_file_format_list',
                         'precip1_ccpa_accum24hr_fcyc_list',
                         'precip1_ccpa_accum24hr_fhr_min',
                         'precip1_ccpa_accum24hr_fhr_max',
                         'precip1_ccpa_accum24hr_grid',
                         'precip1_ccpa_accum24hr_gather_by',
                         'precip1_obs_data_run_hpss',
                         'precip1_mv_database_name',
                         'precip1_mv_database_group',
                         'precip1_mv_database_desc'],
    'RUN_PRECIP_STEP2': ['precip2_model_plot_name_list',
                         'precip2_type_list',
                         'precip2_ccpa_accum24hr_gather_by_list',
                         'precip2_ccpa_accum24hr_fcyc_list',
                         'precip2_ccpa_accum24hr_fhr_min',
                         'precip2_ccpa_accum24hr_fhr_max',
                         'precip2_ccpa_accum24hr_event_eq',
                         'precip2_ccpa_accum24hr_grid'],
    'RUN_SATELLITE_STEP1': ['sat1_type_list',
                            'sat1_ghrsst_ncei_avhrr_anl_fcyc_list',
                            'sat1_ghrsst_ncei_avhrr_anl_fhr_min',
                            'sat1_ghrsst_ncei_avhrr_anl_fhr_max',
                            'sat1_ghrsst_ncei_avhrr_anl_grid',
                            'sat1_ghrsst_ncei_avhrr_anl_gather_by',
                            'sat1_ghrsst_ncei_avhrr_anl_sea_ice_thresh',
                            'sat1_ghrsst_ospo_geopolar_anl_fcyc_list',
                            'sat1_ghrsst_ospo_geopolar_anl_fhr_min',
                            'sat1_ghrsst_ospo_geopolar_anl_fhr_max',
                            'sat1_ghrsst_ospo_geopolar_anl_grid',
                            'sat1_ghrsst_ospo_geopolar_anl_gather_by',
                            'sat1_ghrsst_ncei_avhrr_anl_sea_ice_thresh',
                            'sat1_mv_database_name',
                            'sat1_mv_database_group',
                            'sat1_mv_database_desc'],
    'RUN_SATELLITE_STEP2': ['sat2_model_plot_name_list',
                            'sat2_type_list',
                            'sat2_ghrsst_ncei_avhrr_anl_gather_by_list',
                            'sat2_ghrsst_ospo_geopolar_anl_fcyc_list',
                            'sat2_ghrsst_ncei_avhrr_anl_fhr_min',
                            'sat2_ghrsst_ncei_avhrr_anl_fhr_max',
                            'sat2_ghrsst_ncei_avhrr_anl_sea_ice_thresh',
                            'sat2_ghrsst_ospo_geopolar_anl_event_eq',
                            'sat2_ghrsst_ospo_geopolar_anl_grid',
                            'sat2_ghrsst_ospo_geopolar_anl_gather_by_list',
                            'sat2_ghrsst_ospo_geopolar_anl_fcyc_list',
                            'sat2_ghrsst_ospo_geopolar_anl_fhr_min',
                            'sat2_ghrsst_ospo_geopolar_anl_fhr_max',
                            'sat2_ghrsst_ncei_avhrr_anl_sea_ice_thresh',
                            'sat2_ghrsst_ospo_geopolar_anl_event_eq',
                            'sat2_ghrsst_ospo_geopolar_anl_grid'],
    'RUN_FIT2OBS_PLOTS': ['fit2obs_plots_expnlist', 'fit2obs_plots_expdlist',
                          'fit2obs_plots_endianlist', 'fit2obs_plots_cycle',
                          'fit2obs_plots_oinc', 'fit2obs_plots_finc',
                          'fit2obs_plots_fmax', 'fit2obs_plots_scrdir'],
    'RUN_TROPCYC': ['tropcyc_model_atcf_name_list',
                    'tropcyc_model_plot_name_list',
                    'tropcyc_storm_list', 'tropcyc_fcyc_list',
                    'tropcyc_vhr_list', 'tropcyc_fhr_min',
                    'tropcyc_model_file_format_list',
                    'tropcyc_use_adeck_for_missing_data',
                    'tropcyc_stat_list', 'tropcyc_init_storm_level_list',
                    'tropcyc_valid_storm_level_list', 'tropcyc_plot_CI_bars'],
    'RUN_MAPS2D': ['maps2d_model_plot_name_list', 'maps2d_latlon_area',
                   'maps2d_plot_diff', 'maps2d_anl_file_format_list',
                   'maps2d_type_list',
                   'maps2d_model2model_make_met_data_by',
                   'maps2d_model2model_hour_list',
                   'maps2d_model2model_forecast_to_plot_list',
                   'maps2d_model2model_regrid_to_grid',
                   'maps2d_model2model_forecast_anl_diff',
                   'maps2d_model2obs_make_met_data_by',
                   'maps2d_model2obs_hour_list',
                   'maps2d_model2obs_forecast_to_plot_list',
                   'maps2d_model2obs_regrid_to_grid',
                   'maps2d_model2obs_use_ceres',
                   'maps2d_model2obs_use_monthly_mean'],
    'RUN_MAPSDA': ['mapsda_model_plot_name_list', 'mapsda_latlon_area',
                   'mapsda_plot_diff', 'mapsda_type_list',
                   'mapsda_gdas_make_met_data_by',
                   'mapsda_gdas_hour_list',
                   'mapsda_gdas_guess_hour',
                   'mapsda_gdas_regrid_to_grid',
                   'mapsda_gdas_model_file_format_list',
                   'mapsda_gdas_anl_file_format_list',
                   'mapsda_ens_make_met_data_by',
                   'mapsda_ens_hour_list',
                   'mapsda_ens_guess_hour',
                   'mapsda_ens_regrid_to_grid',
                   'mapsda_ens_model_dir_list',
                   'mapsda_ens_model_file_format_list',
                   'mapsda_ens_model_data_run_hpss']
}
RUN_type_env_check_list = ['shared', 'RUN_'+RUN.upper()]
for RUN_type_env_check in RUN_type_env_check_list:
    RUN_type_env_var_check_list = RUN_type_env_vars_dict[RUN_type_env_check]
    for RUN_type_env_var_check in RUN_type_env_var_check_list:
        if not RUN_type_env_var_check in os.environ:
            print("ERROR: "+RUN_type_env_var_check+" not set in config "
                  +"under "+RUN_type_env_check+" settings")
            sys.exit(1)

if RUN not in ['tropcyc', 'fit2obs_plots']:
    RUN_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')

# Do date check
date_check_name_list = ['start', 'end']
for date_check_name in date_check_name_list:
    date_check = os.environ[date_check_name+'_date']
    if len(date_check) != 8:
        print("ERROR: "+date_check_name+"_date not in YYYYMMDD format")
        sys.exit(1)
    date_check_year = int(date_check[0:4])
    date_check_month = int(date_check[4:6])
    date_check_day = int(date_check[6:])
    if date_check_month > 12 or int(date_check_month) == 0:
        print("ERROR: month "+str(date_check_month)+" in value "
              +date_check+" for "+date_check_name+"_date is not a valid month")
        sys.exit(1)
    if date_check_day \
            > calendar.monthrange(date_check_year, date_check_month)[1]:
        print("ERROR: day "+str(date_check_day)+" in value "
              +date_check+" for "+date_check_name+"_date is not a valid day "
              +"for month")
        sys.exit(1)
if datetime.datetime.strptime(os.environ['end_date'], '%Y%m%d') \
        < datetime.datetime.strptime(os.environ['start_date'], '%Y%m%d'):
    print("ERROR: end_date ("+os.environ['end_date']+") cannot be less than "
          +"start_date ("+os.environ['start_date']+")")
    sys.exit(1)

# Do spinup period check
if os.environ['spinup_period_start'] == 'NA' \
        and os.environ['spinup_period_end'] != 'NA':
    print("ERROR: spinup_period_start is NA, but spinup_period_end is "
          +os.environ['spinup_period_end']+", set spinup_period_end to NA")
    sys.exit(1)
if os.environ['spinup_period_end'] == 'NA' \
        and os.environ['spinup_period_start'] != 'NA':
    print("ERROR: spinup_period_end is NA, but spinup_period_start is "
          +os.environ['spinup_period_start']+", set spinup_period_start to NA")
    sys.exit(1)
if os.environ['spinup_period_start'] != 'NA' \
        and os.environ['spinup_period_end'] != 'NA':
    date_check_name_list = ['start', 'end']
    for date_check_name in date_check_name_list:
        date_check = os.environ['spinup_period_'+date_check_name]
        if len(date_check) != 10:
            print("ERROR: spinup_period_"+date_check_name+" not in "
                  +"YYYYMMDDHH format")
            sys.exit(1)
        date_check_year = int(date_check[0:4])
        date_check_month = int(date_check[4:6])
        date_check_day = int(date_check[6:8])
        date_check_hour = int(date_check[8:])
        if date_check_month > 12 or int(date_check_month) == 0:
            print("ERROR: month "+str(date_check_month)+" in value "
                  +date_check+" for "+date_check_name+"_date is not a "
                  +"valid month")
            sys.exit(1)
        if date_check_day \
                > calendar.monthrange(date_check_year, date_check_month)[1]:
            print("ERROR: day "+str(date_check_day)+" in value "
                  +date_check+" for "+date_check_name+"_date is not a "
                  +"valid day for month")
            sys.exit(1)
    if datetime.datetime.strptime(os.environ['spinup_period_end'],
                                  '%Y%m%d%H') \
            < datetime.datetime.strptime(os.environ['spinup_period_start'],
                                         '%Y%m%d%H'):
        print("ERROR: spinup_period_end ("+os.environ['spinup_period_end']
              +") cannot be less than spinup_period_start ("
              +os.environ['spinup_period_start']+")")
        sys.exit(1)

# Do check for valid RUN_type options
valid_RUN_type_opts_dict = {
    'grid2grid_step1': ['anom', 'pres', 'sfc'],
    'grid2grid_step2': ['anom', 'pres', 'sfc'],
    'grid2obs_step1': ['upper_air', 'conus_sfc', 'polar_sfc'],
    'grid2obs_step2': ['upper_air', 'conus_sfc', 'polar_sfc'],
    'precip_step1': ['ccpa_accum24hr'],
    'precip_step2': ['ccpa_accum24hr'],
    'satellite_step1': ['ghrsst_ncei_avhrr_anl', 'ghrsst_ospo_geopolar_anl'],
    'satellite_step2': ['ghrsst_ncei_avhrr_anl', 'ghrsst_ospo_geopolar_anl'],
    'maps2d': ['model2model', 'model2obs'],
    'mapsda': ['gdas', 'ens']
}
if RUN not in ['tropcyc', 'fit2obs_plots']:
    for RUN_type in RUN_type_list:
        if RUN_type not in valid_RUN_type_opts_dict[RUN]:
            print("ERROR: "+RUN_type+" not a valid option for "
                  +RUN_abbrev+"_type_list. Valid options are "
                  +', '.join(valid_RUN_type_opts_dict[RUN]))
            sys.exit(1)

# Do check for list config variables lengths
check_config_var_len_list = ['model_dir_list', 'model_stat_dir_list',
                             'model_file_format_list', 'model_hpss_dir_list']
if RUN in ['grid2grid_step2', 'grid2obs_step2', 'precip_step2',
           'satellite_step2', 'maps2d', 'mapda']:
    check_config_var_len_list.append(RUN_abbrev+'_model_plot_name_list')
if RUN == 'fit2obs_plots':
    check_config_var_len_list.append(RUN+'_expnlist')
    check_config_var_len_list.append(RUN+'_expdlist')
    check_config_var_len_list.append(RUN+'_endianlist')
elif RUN == 'tropcyc':
    check_config_var_len_list.append(RUN+'_model_atcf_name_list')
    check_config_var_len_list.append(RUN+'_model_plot_name_list')
    check_config_var_len_list.append(RUN+'_model_file_format_list')
elif RUN == 'maps2d':
    check_config_var_len_list.append(RUN+'_anl_file_format_list')
else:
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        if RUN == 'grid2grid_step1':
            if os.environ[RUN_abbrev_type+'_truth_name'] \
                    in ['self_anl', 'self_f00', 'mean_anl', 'mean_f00']:
                check_config_var_len_list.append(
                    RUN_abbrev_type+'_truth_file_format_list'
                )
            elif os.environ[RUN_abbrev_type+'_truth_name'] \
                    in ['gfs_anl', 'gfs_f00', 'gdas_anl', 'gdas_f00',
                        'ecm_f00', 'common_anl', 'common_f00']:
                if 'common' in os.environ[RUN_abbrev_type+'_truth_name']:
                    expected_truth_file_format_list_len = 4
                else:
                    expected_truth_file_format_list_len = 1
                if len(os.environ[RUN_abbrev_type+'_truth_file_format_list']
                       .split(' ')) != expected_truth_file_format_list_len:
                    print("ERROR: length of "+RUN_abbrev_type
                          +"_truth_file_format_list should be "
                          +str(expected_truth_file_format_list_len)+" for "
                          +os.environ[RUN_abbrev_type+'_truth_name'])
                    sys.exit(1)
        elif RUN == 'grid2grid_step2':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_truth_name_list'
            )
            check_config_var_len_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'grid2obs_step2':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'precip_step1':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_model_bucket_list'
            )
            check_config_var_len_list.append(
                RUN_abbrev_type+'_model_var_list'
            )
            check_config_var_len_list.append(
                RUN_abbrev_type+'_model_file_format_list'
            )
        elif RUN == 'precip_step2':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'satellite_step2':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'mapsda':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_model_file_format_list'
            )
            if RUN_type == 'gdas':
                check_config_var_len_list.append(
                    RUN_abbrev_type+'_anl_file_format_list'
                )
            if RUN_type == 'ens':
                check_config_var_len_list.append(
                    RUN_abbrev_type+'_model_dir_list'
                )
for config_var in check_config_var_len_list:
    if len(os.environ[config_var].split(' ')) \
            != len(os.environ['model_list'].split(' ')):
     print("ERROR: length of "+config_var+" (length="
           +str(len(os.environ[config_var].split(' ')))+", values="
           +os.environ[config_var]+") not equal to length of model_list "
           +"(length="+str(len(os.environ['model_list'].split(' ')))+", "
           +"values="+os.environ['model_list']+")")
     sys.exit(1)

# Do check for valid list config variable options
valid_config_var_values_dict = {
    'model_data_run_hpss': ['YES', 'NO'],
    'make_met_data_by': ['VALID', 'INIT'],
    'plot_by': ['VALID', 'INIT'],
    'SEND2WEB': ['YES', 'NO'],
    'img_quality': ['low', 'medium', 'high'],
    'METplus_verbosity': ['DEBUG', 'INFO', 'WARN', 'ERORR'],
    'MET_verbosity': ['0', '1', '2', '3', '4', '5'],
    'log_MET_output_to_METplus': ['yes', 'no'],
    'SENDARCH': ['YES', 'NO'],
    'SENDMETVIEWER': ['YES', 'NO'],
    'KEEPDATA': ['YES', 'NO'],
    'SENDARCH': ['YES', 'NO'],
    'SENDECF': ['YES', 'NO'],
    'SENDCOM': ['YES', 'NO'],
    'SENDDBN': ['YES', 'NO'],
    'SENDDBN_NTC': ['YES', 'NO']
}
if RUN == 'grid2grid_step1':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_truth_name'] = ['self_anl', 'self_f00',
                                                        'gfs_anl', 'gfs_f00',
                                                        'gdas_anl', 'gdas_f00',
                                                        'ecm_f00',
                                                        'common_anl',
                                                        'common_f00',
                                                        'model_mean']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_gather_by'] = ['VALID', 'INIT', 'VSDB']
        if os.environ[RUN_abbrev_type+'_truth_name'] in ['gfs_anl', 'gfs_f00',
                                                         'gdas_anl',
                                                         'gdas_f00',
                                                         'ecm_f00']:
            expected_truth_file_format = (
                'pgb'+os.environ[RUN_abbrev_type+'_truth_name'].split('_')[1]
                +'.'+os.environ[RUN_abbrev_type+'_truth_name'].split('_')[0]
                +'.{valid?fmt=%Y%m%d%H}'
            )
            if os.environ[RUN_abbrev_type+'_truth_file_format_list'] \
                    != expected_truth_file_format:
                print("ERROR: For "+RUN_abbrev_type+"_truth_name set to "
                      +os.environ[RUN_abbrev_type+'_truth_name']+" expected "
                      +expected_truth_file_format+", but got "
                      +os.environ[RUN_abbrev_type+'_truth_file_format_list'])
                sys.exit(1)
        elif os.environ[RUN_abbrev_type+'_truth_name'] in ['common_anl',
                                                           'common_f00']:
            expected_truth_file_format_list = (
                'pgb'+os.environ[RUN_abbrev_type+'_truth_name'].split('_')[1]
                +'.gfs.{valid?fmt=%Y%m%d%H} '
                'pgbf00.ecm.{valid?fmt=%Y%m%d%H} '
                'pgbf00.ukm.{valid?fmt=%Y%m%d%H} '
                'pgbf00.cmc.{valid?fmt=%Y%m%d%H}'
            )
            if os.environ[RUN_abbrev_type+'_truth_file_format_list'] != \
                    expected_truth_file_format_list:
                print("ERROR: For "+RUN_abbrev_type+"_truth_name set to "
                      +os.environ[RUN_abbrev_type+'_truth_name']+" "
                      +"expected "+expected_truth_file_format_list+" "
                      +"but got "
                      +os.environ[RUN_abbrev_type+'_truth_file_format_list'])
                sys.exit(1)
        elif os.environ[RUN_abbrev_type+'_truth_name'] in ['self_anl',
                                                           'self_f00']:
            if 'anl' in os.environ[RUN_abbrev_type+'_truth_name']:
                truth_opt_list = ['anl', 'anal', 'analysis']
            elif 'f00' in os.environ[RUN_abbrev_type+'_truth_name']:
                truth_opt_list = ['f0', 'f00', 'f000']
            if 'anl' in os.environ[RUN_abbrev_type+'_truth_name'] \
                    or 'f00' in os.environ[RUN_abbrev_type+'_truth_name']:
                for truth_file_format \
                        in os.environ[
                            RUN_abbrev_type+'_truth_file_format_list'
                        ].split(' '):
                    if not any(opt in truth_file_format
                               for opt in truth_opt_list):
                        print("ERROR: "+truth_file_format+" in "
                              +RUN_abbrev_type+"_truth_file_format_list does "
                              +"not contain an expected string ("
                              +', '.join(truth_opt_list)+") for "
                              +RUN_abbrev_type+"_truth_name set as "
                              +os.environ[RUN_abbrev_type+'_truth_name'])
                        sys.exit(1)
elif RUN == 'grid2grid_step2':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_truth_name_list'] = ['self_anl',
                                                             'self_f00',
                                                             'gfs_anl',
                                                             'gfs_f00',
                                                             'gdas_anl',
                                                             'gdas_f00',
                                                             'ecm_f00',
                                                             'common_anl',
                                                             'common_f00',
                                                             'model_mean']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_gather_by_list'] = ['VALID', 'INIT',
                                                            'VSDB']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_event_eq'] = ['True', 'False']
elif RUN == 'grid2obs_step1':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        if RUN_type == 'polar_sfc':
            valid_config_var_values_dict[RUN_abbrev_type
                                         +'_msg_type_list'] = ['IABP']
        else:
            valid_config_var_values_dict[RUN_abbrev_type
                                         +'_msg_type_list'] = ['ADPUPA',
                                                               'AIRCAR',
                                                               'AIRCFT',
                                                               'ADPSFC',
                                                               'ERS1DA',
                                                               'GOESND',
                                                               'GPSIPW',
                                                               'MSONET',
                                                               'PROFLR',
                                                               'QKSWND',
                                                               'RASSDA',
                                                               'SATEMP',
                                                               'SATWND',
                                                               'SFCBOG',
                                                               'SFCSHP',
                                                               'SPSSMI',
                                                               'SYNDAT',
                                                               'VADWND',
                                                               'SURFACE',
                                                               'ANYAIR',
                                                               'ANYSFC',
                                                               'ONLYSF']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_gather_by'] = ['VALID', 'INIT', 'VSDB']
    valid_config_var_values_dict[RUN_abbrev
                                 +'_prepbufr_data_run_hpss'] = ['YES', 'NO']
elif RUN == 'grid2obs_step2':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        if RUN_type == 'polar_sfc':
            valid_config_var_values_dict[RUN_abbrev_type
                                         +'_msg_type_list'] = ['IABP']
        else:
            valid_config_var_values_dict[RUN_abbrev_type
                                         +'_msg_type_list'] = ['ADPUPA',
                                                               'AIRCAR',
                                                               'AIRCFT',
                                                               'ADPSFC',
                                                               'ERS1DA',
                                                               'GOESND',
                                                               'GPSIPW',
                                                               'MSONET',
                                                               'PROFLR',
                                                               'QKSWND',
                                                               'RASSDA',
                                                               'SATEMP',
                                                               'SATWND',
                                                               'SFCBOG',
                                                               'SFCSHP',
                                                               'SPSSMI',
                                                               'SYNDAT',
                                                               'VADWND',
                                                               'SURFACE',
                                                               'ANYAIR',
                                                               'ANYSFC',
                                                               'ONLYSF']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_gather_by_list'] = ['VALID', 'INIT',
                                                            'VSDB']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_event_eq'] = ['True', 'False']
elif RUN == 'precip_step1':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_gather_by'] = ['VALID', 'INIT', 'VSDB']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_model_var_list'] = ['APCP', 'PRATE']
        RUN_abbrev_type_accum_length = (
            RUN_type.split('accum')[1].replace('hr','')
        )
        for model_bucket in \
                os.environ[RUN_abbrev_type+'_model_bucket_list'].split(' '):
            if model_bucket != 'continuous':
                if model_bucket.isnumeric():
                    if int(model_bucket) > int(RUN_abbrev_type_accum_length):
                        print("ERROR: value of "+model_bucket+" in "
                              +RUN_abbrev_type+"_model_bucket_list must be "
                              +"<= to "+RUN_abbrev_type+" accumulation length "
                              +"which is "+RUN_abbrev_type_accum_length)
                        sys.exit(1)
                else:
                    print("ERROR: value of "+model_bucket+" in "
                          +RUN_abbrev_type+"_model_bucket_list "
                          +"must be numeric")
                    sys.exit(1)
    valid_config_var_values_dict[RUN_abbrev
                                 +'_obs_data_run_hpss'] = ['YES', 'NO']
elif RUN == 'precip_step2':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_gather_by_list'] = ['VALID', 'INIT',
                                                            'VSDB']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_event_eq'] = ['True', 'False']
elif RUN == 'satellite_step1':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_gather_by'] = ['VALID', 'INIT', 'VSDB']
        if float(os.environ[RUN_abbrev_type+'_sea_ice_thresh']) > 1:
            print("ERROR: value of "+RUN_abbrev_type+"_sea_ice_thresh "
                  +"must be <= 1")
            sys.exit(1)
elif RUN == 'satellite_step2':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_gather_by_list'] = ['VALID', 'INIT',
                                                            'VSDB']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_event_eq'] = ['True', 'False']
        if float(os.environ[RUN_abbrev_type+'_sea_ice_thresh']) > 1:
            print("ERROR: value of "+RUN_abbrev_type+"_sea_ice_thresh "
                  +"must be <= 1")
            sys.exit(1)
elif RUN == 'fit2obs_plots':
    if not os.path.exists(os.environ[RUN+'_scrdir']):
        print("ERROR: "+RUN+"_scrdir ("+os.environ[RUN+'_scrdir']
              +") does not exist")
        sys.exit(1)
    if len(os.environ['model_list'].split(' ')) == 1:
        print("ERROR: To run "+RUN+" length of model_list (length="
              +str(len(os.environ['model_list'].split(' ')))+", values="
              +os.environ['model_list']+") must be > 1")
        sys.exit(1)
    if len(os.environ[RUN+'_cycle'].split(' ')) != 1:
        print("ERROR: length of "+RUN+"_cycle (length="
              +str(len(os.environ[RUN+'_cycle'].split(' ')))+", values="
              +os.environ[RUN+'_cycle']+") must be 1")
        sys.exit(1)
    valid_config_var_values_dict[RUN+'_endianlist'] = ['big', 'little']
elif RUN == 'tropcyc':
    import get_tc_info
    tc_dict = get_tc_info.get_tc_dict()
    valid_basin_list = []
    valid_year_list = []
    for tc in list(tc_dict.keys()):
        valid_basin = tc.split('_')[0]
        if valid_basin not in valid_basin_list:
            valid_basin_list.append(valid_basin)
        valid_year = tc.split('_')[1]
        if valid_year not in valid_year_list:
            valid_year_list.append(valid_year)
    for basin_year_name in os.environ[RUN+'_storm_list'].split(' '):
        basin = basin_year_name.split('_')[0]
        year = basin_year_name.split('_')[1]
        name = basin_year_name.split('_')[2]
        if basin not in valid_basin_list:
            print("ERROR: basin value of "+basin+" in "+basin_year_name+" in "
                  +RUN+"_storm_list not a valid option. Valid options are "
                  +' '.join(valid_basin_list))
            sys.exit(1)
        elif year not in valid_year_list:
            print("ERROR: year value of "+year+" in "+basin_year_name+" in "
                  +RUN+"_storm_list not a valid option. Valid options are "
                  +' '.join(valid_year_list))
            sys.exit(1)
        if name != 'ALLNAMED':
            if basin_year_name not in list(tc_dict.keys()):
                print("ERROR: name value of "+name+" in "+basin_year_name+" "
                      +"in "+basin_year_name+" not supported")
                sys.exit(1)
    valid_config_var_values_dict['tropcyc_use_adeck_for_missing_data'] = [
        'YES', 'NO'
    ]
    for time_type in ['init', 'valid']:
        valid_config_var_values_dict[RUN+'_'+time_type+'_storm_level_list'] = [
            'DB', 'TD', 'TS', 'TY', 'ST', 'TC','HU', 'SD', 'SS',
            'EX', 'IN', 'DS', 'LO', 'WV', 'ET','XX'
        ]
    valid_config_var_values_dict[RUN+'_plot_CI_bars'] = ['YES', 'NO']
elif RUN == 'maps2d':
    valid_config_var_values_dict[RUN_abbrev+'_plot_diff'] = ['YES', 'NO']
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_make_met_data_by'] = ['VALID', 'INIT']
        if RUN_type == 'model2model':
            valid_config_var_values_dict[RUN_abbrev_type
                                         +'_forecast_anl_diff'] = ['YES', 'NO']
        elif RUN_type == 'model2obs':
            valid_config_var_values_dict[RUN_abbrev_type
                                         +'_use_ceres'] = ['YES', 'NO']
            valid_config_var_values_dict[RUN_abbrev_type
                                         +'_use_monthly_mean'] = ['YES', 'NO']
            if os.environ[RUN_abbrev_type+'_use_ceres'] == 'NO' \
                    and os.environ[RUN_abbrev_type+'_use_monthly_mean'] \
                    == 'YES':
                print("ERROR: Cannot set "+RUN_abbrev_type+"_use_ceres to "
                      +"NO and "+RUN_abbrev_type+"_use_monthly_mean to YES. "
                      +"Old observational datasets from VSDB are "
                      +"climatology only. Please set "+RUN_abbrev_type
                      +"_use_monthly_mean to NO.")
                sys.exit(1)
        for forecast_to_plot \
                in os.environ[RUN_abbrev_type
                              +'_forecast_to_plot_list'].split(' '):
            if forecast_to_plot[0] == 'a':
                if forecast_to_plot != 'anl':
                    print("ERROR: value of "+forecast_to_plot+" in "
                          +RUN_abbrev_type+"_forecast_to_plot_list must be "
                          +"anl to use analysis")
                    sys.exit(1)
            elif forecast_to_plot[0] in ['d', 'f']:
                if not forecast_to_plot[1:].isnumeric():
                    print("ERROR: value of "+forecast_to_plot[1:]+" in "
                          +forecast_to_plot+" in "+RUN_abbrev_type
                          +"_forecast_to_plot_list must be numeric")
                    sys.exit(1)
            else:
                print("ERROR: value of "+forecast_to_plot+" in "
                      +RUN_abbrev_type+"_forecast_to_plot_list must be either "
                      +"anl or dX or fX, where X is a number")
                sys.exit(1)
elif RUN == 'mapsda':
    valid_config_var_values_dict[RUN_abbrev+'_plot_diff'] = ['YES', 'NO']
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_make_met_data_by'] = ['VALID', 'INIT']
        if RUN_type == 'ens':
            valid_config_var_values_dict[RUN_abbrev_type
                                         +'_model_data_run_hpss'] = ['YES',
                                                                     'NO']

# Run through and check config variables from dictionary
for config_var in list(valid_config_var_values_dict.keys()):
    if 'list' in config_var:
        for list_item in os.environ[config_var].split(' '):
            if list_item not in valid_config_var_values_dict[config_var]:
                config_var_pass = False
                failed_config_value = list_item
                break
            else:
                config_var_pass = True
    else:
        if os.environ[config_var] \
                not in valid_config_var_values_dict[config_var]:
            config_var_pass = False
            failed_config_value = os.environ[config_var]
        else:
            config_var_pass = True
    if not config_var_pass:
        print("ERROR: value of "+failed_config_value+" for "
              +config_var+" not a valid option. Valid options are "
              +', '.join(valid_config_var_values_dict[config_var]))
        sys.exit(1)

print("END: "+os.path.basename(__file__))
