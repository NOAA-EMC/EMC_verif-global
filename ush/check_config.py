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
if RUN != 'tropcyc':
    RUN_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')

# Do date check
date_check_name_list = ['start', 'end']
for date_check_name in date_check_name_list:
    date_check = os.environ[date_check_name+'_date']
    date_check_year = int(date_check[0:4])
    date_check_month = int(date_check[4:6])
    date_check_day = int(date_check[6:])
    if len(date_check) != 8:
        print("ERROR: "+date_check_name+"_date not in YYYYMMDD format")
        sys.exit(1)
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
if RUN != 'tropcyc':
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
if RUN == 'tropcyc':
    check_config_var_len_list.append(RUN+'_model_atcf_name_list')
    check_config_var_len_list.append(RUN+'_model_plot_name_list')
    check_config_var_len_list.append(RUN+'_model_file_format_list')
elif RUN == 'maps2d':
    check_config_var_len_list.append(RUN+'_anl_file_format_list')
else:
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        if RUN == 'grid2grid_step1':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_truth_file_format_list'
            )
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
                                                        'gfs_anl', 'gfs_f00']
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_gather_by'] = ['VALID', 'INIT', 'VSDB']
        if 'anl' in os.environ[RUN_abbrev_type+'_truth_name']:
            truth_opt_list = ['anl', 'anal', 'analysis']
        elif 'f00' in os.environ[RUN_abbrev_type+'_truth_name']:
            truth_opt_list = ['f0', 'f00', 'f000']
        if 'anl' in os.environ[RUN_abbrev_type+'_truth_name'] \
                or 'f00' in os.environ[RUN_abbrev_type+'_truth_name']:
            for truth_file_format \
                    in os.environ[RUN_abbrev_type+'_truth_file_format_list'] \
                    .split(' '):
                if not any(opt in truth_file_format for opt in truth_opt_list):
                    print("ERROR: "+truth_file_format+" in "+RUN_abbrev_type
                          +"_truth_file_format_list does not contain an "
                          +"expected string ("+', '.join(truth_opt_list)+") "
                          +"for "+RUN_abbrev_type+"_truth_name set as "
                          +os.environ[RUN_abbrev_type+'_truth_name'])
                    sys.exit(1)
elif RUN == 'grid2grid_step2':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type
                                     +'_truth_name_list'] = ['self_anl',
                                                             'self_f00',
                                                             'gfs_anl',
                                                             'gfs_f00']
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
    for atcf_name in os.environ[RUN+'_model_atcf_name_list'].split(' '):
        if len(atcf_name) != 4:
            print("ERROR: length of "+atcf_name+" in "
                  +RUN+"_model_atcf_name_list != to 4")
            sys.exit(1)
    valid_config_var_values_dict[RUN+'_storm_level_list'] = ['DB', 'TD', 'TS',
                                                             'TY', 'ST', 'TC',
                                                             'HU', 'SD', 'SS',
                                                             'EX', 'IN', 'DS',
                                                             'LO', 'WV', 'ET',
                                                             'XX']
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
