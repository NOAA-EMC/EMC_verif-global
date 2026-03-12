'''
Program Name: check_config_step2.py
Contact(s): Mallory Row
Abstract: This script is run by step2 scripts in scripts/.
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
    'shared': ['model_list', 'model_stat_dir_list',
               'OUTPUTROOT',
               'start_date', 'end_date', 'spinup_period_start',
               'spinup_period_end', 'make_met_data_by', 'plot_by',
               'SEND2WEB', 'webhost', 'webhostid', 'webdir', 'img_quality',
               'MET_version', 'METplus_version', 'METplus_verbosity',
               'MET_verbosity', 'log_MET_output_to_METplus', 'SENDARCH',
               'KEEPDATA', 'SENDECF', 'SENDCOM', 'SENDDBN', 'SENDDBN_NTC'],
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
    'RUN_PRECIP_STEP2': ['precip2_model_plot_name_list',
                         'precip2_type_list',
                         'precip2_ccpa_accum24hr_gather_by_list',
                         'precip2_ccpa_accum24hr_fcyc_list',
                         'precip2_ccpa_accum24hr_fhr_min',
                         'precip2_ccpa_accum24hr_fhr_max',
                         'precip2_ccpa_accum24hr_event_eq',
                         'precip2_ccpa_accum24hr_grid'],
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
}
RUN_type_env_check_list = ['shared', 'RUN_'+RUN.upper()]
for RUN_type_env_check in RUN_type_env_check_list:
    RUN_type_env_var_check_list = RUN_type_env_vars_dict[RUN_type_env_check]
    for RUN_type_env_var_check in RUN_type_env_var_check_list:
        if not RUN_type_env_var_check in os.environ:
            print("ERROR: "+RUN_type_env_var_check+" not set in config "
                  +"under "+RUN_type_env_check+" settings")
            sys.exit(1)

if RUN not in ['fit2obs_plots']:
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
    'grid2grid_step2': ['anom', 'pres', 'sfc'],
    'grid2obs_step2': ['upper_air', 'conus_sfc', 'polar_sfc'],
    'precip_step2': ['ccpa_accum24hr'],
    'satellite_step2': ['ghrsst_ncei_avhrr_anl', 'ghrsst_ospo_geopolar_anl'],
}
if RUN not in ['fit2obs_plots']:
    for RUN_type in RUN_type_list:
        if RUN_type not in valid_RUN_type_opts_dict[RUN]:
            print("ERROR: "+RUN_type+" not a valid option for "
                  +RUN_abbrev+"_type_list. Valid options are "
                  +', '.join(valid_RUN_type_opts_dict[RUN]))
            sys.exit(1)

# Do check for list config variables lengths
check_config_var_len_list = ['model_stat_dir_list']
if RUN in ['grid2grid_step2', 'grid2obs_step2', 'precip_step2',
           'satellite_step2']:
    check_config_var_len_list.append(RUN_abbrev+'_model_plot_name_list')
if RUN == 'fit2obs_plots':
    check_config_var_len_list.append(RUN+'_expnlist')
    check_config_var_len_list.append(RUN+'_expdlist')
    check_config_var_len_list.append(RUN+'_endianlist')
else:
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        if RUN == 'grid2grid_step2':
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
        elif RUN == 'precip_step2':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_truth_name_list'
            )
            check_config_var_len_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'satellite_step2':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_gather_by_list'
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
    'make_met_data_by': ['VALID', 'INIT'],
    'plot_by': ['VALID', 'INIT'],
    'SEND2WEB': ['YES', 'NO'],
    'img_quality': ['low', 'medium', 'high'],
    'METplus_verbosity': ['DEBUG', 'INFO', 'WARN', 'ERORR'],
    'MET_verbosity': ['0', '1', '2', '3', '4', '5'],
    'log_MET_output_to_METplus': ['yes', 'no'],
    'SENDARCH': ['YES', 'NO'],
    'KEEPDATA': ['YES', 'NO'],
    'SENDARCH': ['YES', 'NO'],
    'SENDECF': ['YES', 'NO'],
    'SENDCOM': ['YES', 'NO'],
    'SENDDBN': ['YES', 'NO'],
    'SENDDBN_NTC': ['YES', 'NO']
}
if RUN == 'grid2grid_step2':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_gather_by_list'] = ['VALID', 'INIT',
                                                            'VSDB']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_event_eq'] = ['True', 'False']
        valid_config_var_values_dict[RUN_abbrev_type+'_truth_name_list'] = [
            'self_anl', 'self_f00', 'gfs_anl', 'gfs_f00', 'gdas_anl', 'gdas_f00',
            'ecm_f00', 'model_mean'
        ]
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
elif RUN == 'precip_step2':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_truth_name_list'] = ['ccpa_accum24hr']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_gather_by_list'] = ['VALID', 'INIT',
                                                            'VSDB']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_event_eq'] = ['True', 'False']
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
