'''
Program Name: create_job_scripts.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This creates multiple independent job cards. These
          jobs contain all the necessary environment variables
          and METplus commands to needed to run the specific
          METplus verification use case and types (each job
          could be run independenttly on the command line).
'''

import sys
import os
import datetime
import glob

print("BEGIN: "+os.path.basename(__file__))

def init_env_dict():
    """! Initialize dictionary with environment variables
         and their values to write in job scripts with common
         to all METplus job

         Args:

         Returns:
             env_var_dict - dictionary with keys as environment
                            variables names and values as
                            environment variable values
    """
    env_var_list = [
        'machine', 'HOMEverif_global', 'USHverif_global', 'PARMverif_global',
        'FIXverif_global', 'METplus_version', 'HOMEMETplus', 'USHMETplus',
        'MET_version', 'HOMEMET', 'DATA', 'RUN', 'CUT', 'TR', 'CONVERT', 'NCDUMP'
    ]
    env_var_dict = {}
    for env_var in env_var_list:
        env_var_dict[env_var] = os.environ[env_var]
    return env_var_dict

def create_job_scripts_step1(start_date_dt, end_date_dt, case, case_abbrev,
                             case_type_list, run_metplus, machine_conf,
                             conf_dir):
    """! Writes out individual job scripts based on requested verification
         for step 1 RUN

         Args:
             start_date_dt  - datetime object of the verification start
                              date
             end_date_dt    - datetime object of the verification end
                              date
             case           - string of the verification use case
             case_abbrev    - string of case abbrevation
             case_type_list - list of strings of the types of the
                              verification use case
             run_metplus    - string of path to run_metplus.py
             machine_conf   - string of path to machine METplus conf
             conf_dir       - string of path to base METplus conf directory
         Returns:
    """
    njob = 0
    # Initialize environment variable job dictionary
    job_env_dict = init_env_dict()
    job_env_dict['make_met_data_by'] = os.environ['make_met_data_by']
    # Set important METplus paths
    make_met_data_conf_dir = os.path.join(
        conf_dir, case, 'make_met_data'
    )
    gather_conf_dir = os.path.join(
        conf_dir, case, 'gather'
    )
    # Set case
    job_env_dict['RUN_case'] = case
    # Set up model environment variables in dictionary
    for model in os.environ['model_list'].split(' '):
        job_env_dict['model'] = model
        model_idx = os.environ['model_list'].split(' ').index(model)
        # Set up case_type environment variables in dictionary
        for case_type in case_type_list:
            job_env_dict['RUN_type'] = case_type
            case_abbrev_type = case_abbrev+'_'+case_type
            case_type_env_list = ['gather_by', 'grid',
                                  'fhr_list', 'fhr_beg', 'fhr_end',
                                  'valid_hr_list', 'valid_hr_beg',
                                  'valid_hr_end', 'valid_hr_inc',
                                  'init_hr_list', 'init_hr_beg',
                                  'init_hr_end', 'init_hr_inc']
            for case_type_env in case_type_env_list:
                job_env_dict[case_type_env] = (
                    os.environ[case_abbrev_type+'_'+case_type_env]
                )
            if case == 'grid2grid':
                obtype = os.environ[
                    case_abbrev_type+'_truth_name'
                ].replace('self', model)
                job_env_dict['obtype'] = obtype
            elif case == 'grid2obs':
                if case_type == 'upper_air':
                    obtype = 'gdas'
                elif case_type == 'conus_sfc':
                        obtype = 'nam'
                elif case_type == 'polar_sfc':
                    obtype = 'iabp'
                job_env_dict['obtype'] = obtype
                job_env_dict['msg_type_list'] = ', '.join(
                    os.environ[case_abbrev_type+'_msg_type_list'].split(' ')
                )
            elif case == 'precip':
                job_env_dict['obtype'] = case_type
                job_env_dict['model_bucket'] = os.environ[
                    case_abbrev_type+'_model_bucket_list'
                ].split(' ')[model_idx]
                job_env_dict['model_var'] = os.environ[
                    case_abbrev_type+'_model_var_list'
                ].split(' ')[model_idx]
                job_env_dict['model_file_format'] = os.environ[
                    case_abbrev_type+'_model_file_format_list'
                ].split(' ')[model_idx][0:4]
                if job_env_dict['model_bucket'] == 'continuous':
                    job_env_dict['pcp_combine_method'] = 'SUBTRACT'
                else:
                    job_env_dict['pcp_combine_method'] = 'SUM'
            elif case == 'satellite':
                job_env_dict['obtype'] = case_type
                job_env_dict['sea_ice_thresh'] = os.environ[
                    case_abbrev_type+'_sea_ice_thresh'
                ]
            # Set up date environment variables in dictionary
            date_dt = start_date_dt
            while date_dt <= end_date_dt:
                njob+=1
                job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                # Need to do check on grid-to-grid truth file
                # for the date: was requested truth subsituted?
                if case == 'grid2grid':
                    truth_file_list = glob.glob(
                        os.path.join(job_env_dict['DATA'], 'grid2grid_step1',
                                     'data', model, case_type+'.truth.'
                                     +date_dt.strftime('%Y%m%d')+'*')
                    )
                    link_truth_name_list = []
                    if len(truth_file_list) > 0:
                        for truth_file in truth_file_list:
                            if os.path.islink(truth_file):
                                if model in os.readlink(truth_file) \
                                    and 'f000' in os.readlink(truth_file) \
                                    and obtype != model+'_f00':
                                        link_truth_name_list.append(model+'_f00')
                                else:
                                    link_truth_name_list.append(obtype)
                            else:
                                link_truth_name_list.append(obtype)
                    if obtype != model+'_f00':
                        if all(truth == model+'_f00'
                                for truth in link_truth_name_list):
                            job_env_dict['obtype'] = model+'_f00'
                        elif all(truth == link_truth_name_list[0]
                                for truth in link_truth_name_list):
                            job_env_dict['obtype'] = link_truth_name_list[0]
                        else:
                            print("ERROR: mismatched truth types ["
                                  +', '.join(link_truth_name_list)+"] for "
                                  +"files "+', '.join(truth_file_list))
                            sys.exit(1)
                    else:
                        job_env_dict['obtype'] =  model+'_f00'
                # Create job file
                job_filename = os.path.join(job_env_dict['DATA'],
                                            job_env_dict['RUN'],
                                            'metplus_job_scripts',
                                            'job'+str(njob))
                job_file = open(job_filename, 'w')
                job_file.write('#!/bin/sh\n')
                job_file.write('set -x\n')
                # Write environment variables
                for name, value in job_env_dict.items():
                    job_file.write('export '+name+'="'+value+'"\n')
                job_file.write('\n')
                # Write METplus commmands
                metplus_conf_list = [
                    os.path.join(
                        make_met_data_conf_dir,
                        case_type+'_'+job_env_dict['make_met_data_by']+'.conf'
                    )
                ]
                if case == 'grid2grid' and case_type == 'anom':
                    metplus_conf_list.append(
                        os.path.join(
                            make_met_data_conf_dir,
                            case_type+'_height_'
                            +job_env_dict['make_met_data_by']+'.conf'
                        )
                    )
                metplus_conf_list.append(
                    os.path.join(
                        gather_conf_dir, job_env_dict['gather_by']+'.conf'
                    )
                )
                for metplus_conf in metplus_conf_list:
                    job_file.write(
                        run_metplus+' -c '+machine_conf+' '
                        +'-c '+metplus_conf+'\n'
                    )
                job_file.close()
                date_dt = date_dt + datetime.timedelta(days=1)

def create_job_scripts_maps(start_date_dt, end_date_dt, case, case_abbrev,
                            case_type_list, run_metplus, machine_conf,
                            conf_dir):
    """! Writes out individual job scripts based on requested verification
         for maps2d or mapdsda RUN

         Args:
             start_date_dt  - datetime object of the verification start
                              date
             end_date_dt    - datetime object of the verification end
                              date
             case           - string of the verification use case
             case_abbrev    - string of case abbrevation
             case_type_list - list of strings of the types of the
                              verification use case
             run_metplus    - string of path to run_metplus.py
             machine_conf   - string of path to machine METplus conf
             conf_dir       - string of path to base METplus conf directory

         Returns:
    """
    # Set up plotting information dictionary
    plotting_case_case_type_dict = {
        'maps2d_model2model': {
            'preslevs': {'TMP': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                 '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                 '5hPa', '1hPa'],
                         'HGT': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                 '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                 '5hPa', '1hPa'],
                         'UGRD': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                  '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                  '5hPa', '1hPa'],
                         'VGRD': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                  '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                  '5hPa', '1hPa'],
                         'VVEL': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                  '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                  '5hPa', '1hPa'],
                         'RH': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                '5hPa', '1hPa'],
                         'CLMR': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                  '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                  '5hPa', '1hPa'],
                         'O3MR': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                  '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                  '5hPa', '1hPa']},
            'sfc': {'TMP': ['2mAGL', 'sfc'],
                    'TMAX': ['2mAGL_range6hr'],
                    'TMIN': ['2mAGL_range6hr'],
                    'DPT': ['2mAGL'],
                    'RH': ['2mAGL'],
                    'SPFH': ['2mAGL'],
                    'UGRD': ['10mAGL'],
                    'VGRD': ['10mAGL'],
                    'GUST': ['sfc'],
                    'PRES': ['sfc'],
                    'MSLET': ['msl'],
                    'PRMSL': ['msl'],
                    'LFTX': ['sfc'],
                    '4LFTX': ['sfc'],
                    'VIS': ['sfc'],
                    'HGT': ['sfc'],
                    'HINDEX': ['sfc'],
                    'ICEC': ['sfc'],
                    'U-GWD': ['sfc_avg6hr'],
                    'V-GWD': ['sfc_avg6hr'],
                    'UFLX': ['sfc_avg6hr'],
                    'VFLX': ['sfc_avg6hr'],
                    'ALBDO': ['sfc_avg6hr'],
                    'LHTFL': ['sfc_avg6hr'],
                    'SHTFL': ['sfc_avg6hr'],
                    'GFLUX': ['sfc_avg6hr']},
            'totcol': {'PWAT': ['column'],
                       'CWAT': ['column'],
                       'TOZNE': ['column'],
                       'CWORK': ['column_avg6hr'],
                       'RH': ['column']},
            'precip': {'APCP': ['sfc_accum6hr'],
                       'ACPCP': ['sfc_accum6hr'],
                       'SNOD': ['sfc'],
                       'WEASD': ['sfc'],
                       'WATR': ['sfc_accum6hr'],
                       'PRATE': ['sfc_avg6hr'],
                       'CRAIN': ['sfc'],
                       'CSNOW': ['sfc'],
                       'CICEP': ['sfc'],
                       'CFRZR': ['sfc']},
            'cloudsrad': {'DLWRF': ['sfc_avg6hr'],
                          'ULWRF': ['sfc_avg6hr', 'toa_avg6hr'],
                          'DSWRF': ['sfc_avg6hr'],
                          'USWRF': ['sfc_avg6hr', 'toa_avg6hr'],
                          'ALBDO': ['sfc_avg6hr'],
                          'SUNSD': ['sfc'],
                          'TCDC': ['column_avg6hr', 'pbl_avg6hr', 'convective'],
                          'LCDC': ['low_avg6hr'],
                          'MCDC': ['mid_avg6hr'],
                          'HCDC': ['high_avg6hr'],
                          'PRES': ['lowcloudbase_avg6hr',
                                   'midcloudbase_avg6hr',
                                   'highcloudbase_avg6hr',
                                   'convectivecloudbase',
                                   'lowcloudtop_avg6hr', 'midcloudtop_avg6hr',
                                   'highcloudtop_avg6hr',
                                   'convectivecloudtop'],
                          'TMP': ['lowcloudtop_avg6hr', 'midcloudtop_avg6hr',
                                  'highcloudtop_avg6hr'],
                          'CWAT': ['column'],
                          'CWORK': ['column_avg6hr']},
            'capecin': {'CAPE': ['sfc'],
                        'CIN': ['sfc']},
            'pbl': {'HPBL': ['sfc'],
                    'VRATE': ['pbl'],
                    'UGRD': ['pbl'],
                    'VGRD': ['pbl'],
                    'TCDC': ['pbl_avg6hr']},
            'groundsoil': {'TMP': ['sfc'],
                           'TSOIL': ['0-0.1mUGL', '0.1-0.4mUGL',
                                     '0.4-1mUGL', '1-2mUGL'],
                           'SOILW': ['0-0.1mUGL', '0.1-0.4mUGL',
                                     '0.4-1mUGL', '1-2mUGL'],
                           'LHTFL': ['sfc_avg6hr'],
                           'SHTFL': ['sfc_avg6hr'],
                           'GFLUX': ['sfc_avg6hr'],
                           'WATR': ['sfc_accum6hr'],
                           'PEVPR': ['sfc'],
                           'FLDCP': ['sfc'],
                           'WILT': ['sfc']},
            'tropopause': {'HGT': ['tropopause'],
                           'TMP': ['tropopause'],
                           'PRES': ['tropopause'],
                           'UGRD': ['tropopause'],
                           'VGRD': ['tropopause'],
                           'VWSH': ['tropopause'],
                           'ICAHT': ['tropopause']},
            'sigma0995': {'TMP': ['0.995sigma'],
                          'POT': ['0.995sigma'],
                          'UGRD': ['0.995sigma'],
                          'VGRD': ['0.995sigma'],
                          'VVEL': ['0.995sigma'],
                          'RH': ['0.995sigma']},
            'maxwindlev': {'TMP': ['maxwindlev'],
                           'PRES': ['maxwindlev'],
                           'HGT': ['maxwindlev'],
                           'UGRD': ['maxwindlev'],
                           'VGRD': ['maxwindlev'],
                           'ICAHT': ['maxwindlev']},
            'highesttropfrzlev': {'HGT': ['highesttropfrzlev'],
                                  'RH': ['highesttropfrzlev']}
        },
        'maps2d_model2obs': {
            'cloudsrad': {'DLWRF': ['sfc_avg6hr'],
                          'ULWRF': ['sfc_avg6hr', 'toa_avg6hr'],
                          'DSWRF': ['sfc_avg6hr', 'toa_avg6hr'],
                          'USWRF': ['sfc_avg6hr', 'toa_avg6hr'],
                          'TCDC': ['column_avg6hr'],
                          'LCDC': ['low_avg6hr'],
                          'MCDC': ['mid_avg6hr'],
                          'HCDC': ['high_avg6hr']},
            'sfc': {'TMP': ['2mAGL']},
            'totcol': {'PWAT': ['column'],
                       'CWAT': ['column']},
            'precip': {'PRATE': ['sfc_avg6hr']}
        },
        'mapsda_gdas':{
            'preslevs':{'TMP': ['1000hPa', '925hPa', '800hPa', '700hPa',
                                '500hPa', '200hPa', '100hPa', '70hPa',
                                '50hPa', '30hPa', '10hPa', '7hPa', '5hPa',
                                '3hPa', '2hPa', '1hPa'],
                        'UGRD': ['1000hPa', '925hPa', '800hPa', '700hPa',
                                 '500hPa', '200hPa', '100hPa', '70hPa',
                                 '50hPa', '30hPa', '10hPa', '7hPa', '5hPa',
                                 '3hPa', '2hPa', '1hPa'],
                        'VGRD': ['1000hPa', '925hPa', '800hPa', '700hPa',
                                 '500hPa', '200hPa', '100hPa', '70hPa',
                                 '50hPa', '30hPa', '10hPa', '7hPa',
                                 '5hPa', '3hPa', '2hPa', '1hPa'],
                        'RH': ['1000hPa', '925hPa', '800hPa', '700hPa',
                               '500hPa', '200hPa', '100hPa', '70hPa',
                               '50hPa', '30hPa', '10hPa', '7hPa', '5hPa',
                               '3hPa', '2hPa', '1hPa'],
                        'O3MR': ['1000hPa', '925hPa', '800hPa', '700hPa',
                                 '500hPa', '200hPa', '100hPa', '70hPa',
                                 '50hPa', '30hPa', '10hPa', '7hPa', '5hPa',
                                 '3hPa', '2hPa', '1hPa']},
            'sfc': {'MSLET': ['msl']}
        },
        'mapsda_ens': {
            'preslevs': {'TMP': ['1000hPa', '850hPa', '500hPa', '250hPa',
                                 '10hPa', '1hPa'],
                        'UGRD': ['1000hPa', '850hPa', '500hPa', '250hPa',
                                 '10hPa', '1hPa'],
                        'VGRD': ['1000hPa', '850hPa', '500hPa', '250hPa',
                                 '10hPa', '1hPa'],
                        'SPFH': ['1000hPa', '850hPa', '500hPa', '250hPa',
                                 '10hPa', '1hPa'],
                        'O3MR': ['1000hPa', '850hPa', '500hPa', '250hPa',
                                 '10hPa', '1hPa']},
            'sfc': {'PRES': ['sfc']}
        }
    }
    maps2d_model2obs_obs_var_name = {
        'DLWRF': ['lw_sfc_down'],
        'ULWRF': ['lw_sfc_up', 'lw_toa_up'],
        'DSWRF': ['sw_sfc_down', 'sw_toa_down'],
        'USWRF': ['sw_sfc_up', 'sw_toa_up'],
        'TCDC': ['cldt'],
        'LCDC': ['cldl'],
        'MCDC': ['cldm'],
        'HCDC': ['cldh'],
        'TMP': ['air'],
        'PWAT': ['tpw'],
        'CWAT': ['clwp'],
        'PRATE': ['precip']
    }
    njob = 0
    # Initialize environment variable job dictionary
    job_env_dict = init_env_dict()
    job_env_dict['START_DATE'] = start_date_dt.strftime('%Y%m%d')
    job_env_dict['END_DATE'] = end_date_dt.strftime('%Y%m%d')
    job_env_dict['latlon_area'] = os.environ[case_abbrev+'_latlon_area']
    job_env_dict['plot_diff'] = os.environ[case_abbrev+'_plot_diff']
    job_env_dict['img_quality'] = os.environ['img_quality']
    # Set important METplus paths
    case_conf_dir = os.path.join(conf_dir, case)
    # Set up model environment variables in dictionary
    model_list = os.environ['model_list'].split(' ')
    model_plot_name_list = os.environ[
        case_abbrev+'_model_plot_name_list'
    ].split(' ')
    nmodels = len(model_list)
    for model in model_list:
        model_idx = model_list.index(model)
        model_num = model_idx + 1
        job_env_dict['model'+str(model_num)] = model
        job_env_dict['model'+str(model_num)+'_plot_name'] = (
            model_plot_name_list[model_idx]
        )
    # Set up case_type environment variables in dictionary
    for case_type in case_type_list:
        case_abbrev_type = case_abbrev+'_'+case_type
        case_type_env_list = ['make_met_data_by', 'regrid_to_grid',
                              'hour_beg', 'hour_end', 'hour_inc']
        for case_type_env in case_type_env_list:
            job_env_dict[case_type_env] = (
                os.environ[case_abbrev_type+'_'+case_type_env]
            )
        job_env_dict['plot_by'] = job_env_dict['make_met_data_by']
        job_env_dict['RUN_type'] = case_type
        # Check we have enough room on subplots before continuing
        if case == 'maps2d':
            if case_type == 'model2model':
                if os.environ[case_abbrev_type+'_forecast_anl_diff'] == 'YES':
                    nsubplots = nmodels * 2
                    error_msg = (
                        '(number of models in model_list ,'+str(nmodels)+', '
                        +'times 2, for '+case_abbrev_type
                        +'_forecast_anl_diff = YES)'
                    )
                else:
                    nsubplots = nmodels
                    error_msg = (
                        '(number of models in model_list ,'+str(nmodels)+')'
                    )
            elif case_type == 'model2obs':
                nsubplots = nmodels + 1
                error_msg = (
                    '(number of models in model_list ,'+str(nmodels)+', '
                    +'plus 1, for observations)'
                )
        elif case == 'mapsda':
            if case_type == 'gdas':
                nsubplots = nmodels + 1
                error_msg = (
                    '(number of models in model_list ,'+str(nmodels)+', '
                    +'plus 1, for model1 analysis)'
                )
            elif case_type == 'ens':
                nsubplots = nmodels
                error_msg = (
                    '(number of models in model_list ,'+str(nmodels)+')'
                )
        if nsubplots > 8:
            print("ERROR: Requested verification results in "
                  +str(nsubplots)+" subplots "+error_msg
                  +", current maximum is 8")
            sys.exit(1)
        # Set some specific case_type environment variables in own dictionary
        case_type_env_dict = {}
        if case == 'maps2d':
            if case_type == 'model2model':
                case_type_env_dict['forecast_anl_diff'] = (
                    os.environ[case_abbrev_type+'_forecast_anl_diff']
                )
            elif case_type == 'model2obs':
                case_type_env_dict['use_ceres'] = (
                    os.environ[case_abbrev_type+'_use_ceres']
                )
                case_type_env_dict['use_monthly_mean'] = (
                    os.environ[case_abbrev_type+'_use_monthly_mean']
                )
        # Set forecasting plotting list
        if case == 'maps2d':
            forecast_to_plot_list = (
                os.environ[case_abbrev_type+'_forecast_to_plot_list'] \
                .split(' ')
            )
        elif case == 'mapsda':
            forecast_to_plot_list = (
                ('fhr'+os.environ[case_abbrev_type+'_guess_hour']).split(' ')
            )
        # Set up plotting environment variables in dictionary
        plotting_dict = plotting_case_case_type_dict[case+'_'+case_type]
        for var_group in list(plotting_dict.keys()):
            var_group_img_dir = os.path.join(
                job_env_dict['DATA'], job_env_dict['RUN'], 'metplus_output',
                'plot_by_'+job_env_dict['plot_by'], case_type, 'images'
            )
            if not os.path.exists(var_group_img_dir):
                os.makedirs(var_group_img_dir)
            for model in model_list:
                var_group_name_make_met_model_dir = os.path.join(
                    job_env_dict['DATA'], job_env_dict['RUN'],
                    'metplus_output',
                    'make_met_data_by_'+job_env_dict['make_met_data_by'],
                    'series_analysis', case_type, var_group, model
                )
                if not os.path.exists(var_group_name_make_met_model_dir):
                    os.makedirs(var_group_name_make_met_model_dir)
            job_env_dict['var_group'] = var_group
            for var_name, var_levels in plotting_dict[var_group].items():
                job_env_dict['var_name'] = var_name
                job_env_dict['var_levels'] = (
                    ' '.join(var_levels).replace(' ', ', ')
                )
                for model in model_list:
                    model_num = (model_list.index(model)) + 1
                    if case == 'maps2d':
                        if case_type == 'model2model':
                            if case_type_env_dict['forecast_anl_diff'] \
                                    == 'YES':
                                obtype = model+'_anl'
                            else:
                                obtype = model
                        elif case_type == 'model2obs':
                            if var_group in ['cloudsrad', 'totcol']:
                                if case_type_env_dict['use_ceres'] == 'YES':
                                    obtype = 'ceres'
                                else:
                                    if var_name == 'TCDC':
                                        obtype = 'rad_isccp'
                                    elif var_name == 'CWAT':
                                        obtype = 'clwp'
                                    elif var_name == 'PWAT':
                                        obtype = 'nvap'
                                    elif var_name in ['DLWRF', 'ULWRF',
                                                      'DSWRF', 'USWRF']:
                                        obtype = 'rad_srb2'
                            elif var_group == 'sfc':
                                obtype = 'ghcn_cams'
                            elif var_group == 'precip':
                                obtype = 'gpcp'
                            case_type_env_dict['obtype_var_name'] = ' '.join(
                                maps2d_model2obs_obs_var_name[var_name]
                            ).replace(' ', ', ')
                    elif case == 'mapsda':
                        if case_type == 'gdas':
                            obtype = model+'_anl'
                        elif case_type == 'ens':
                            obtype = model
                    job_env_dict['model'+str(model_num)+'_obtype'] = obtype
                for forecast_to_plot in forecast_to_plot_list:
                    job_env_dict['forecast_to_plot'] = forecast_to_plot
                    njob+=1
                    job_env_dict['job_num_id'] = str(njob)
                    # Create job file
                    job_filename = os.path.join(job_env_dict['DATA'],
                                                job_env_dict['RUN'],
                                                'metplus_job_scripts',
                                                'job'+str(njob))
                    job_file = open(job_filename, 'w')
                    job_file.write('#!/bin/sh\n')
                    job_file.write('set -x\n')
                    job_file.write('\n')
                    # Write environment variables
                    for name, value in job_env_dict.items():
                        job_file.write('export '+name+'="'+value+'"\n')
                    for name, value in case_type_env_dict.items():
                        job_file.write('export '+name+'="'+value+'"\n')
                    job_file.write('\n')
                    # Write METplus commands
                    if case == 'maps2d' \
                            or (case == 'mapsda' and case_type == 'gdas'):
                        job_file.write(
                            'python '
                            +os.path.join(
                                job_env_dict['USHverif_global'],
                               'create_MET_series_analysis_jobs.py\n'
                            )
                        )
                        for model in model_list:
                            job_file.write(os.path.join(DATA, RUN,
                                                        'metplus_job_scripts',
                                                        'series_analysis_'
                                                        +'job'+str(njob)+'_'
                                                        +model+'.sh')+'\n')
                        job_file.write('\n')
                    if os.environ['machine'] in ['ORION', 'HERCULES']:
                        job_file.write('echo "WARNING: Cartopy not installed '
                                       +'on '+os.environ['machine'].title()
                                       +', cannot create plots."\n')
                    else:
                        plotting_script_list = []
                        plotting_script_list.append(
                            'plot_'+case+'_lat_lon_errors.py'
                        )
                        if var_group == 'preslevs':
                            plotting_script_list.append(
                                'plot_'+case+'_zonal_mean_errors.py'
                            )
                        for plotting_script in plotting_script_list:
                            job_file.write(
                                'python '
                                 +os.path.join(job_env_dict['USHverif_global'],
                                               'plots', case,
                                                plotting_script)
                                +'\n'
                            )
                        job_file.write('\n')
                        main_img_dir = os.path.join(
                            job_env_dict['DATA'], job_env_dict['RUN'],
                            'metplus_output', 'images'
                        )
                        job_file.write('nimgs=$(ls '+var_group_img_dir
                                       +'/* |wc -l)\n')
                        job_file.write('if [ $nimgs -ne 0 ]; then\n')
                        job_file.write('    ln -sf '+var_group_img_dir
                                       +'/* '+main_img_dir+'/.\n')
                        job_file.write('fi')
                    job_file.close()

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
machine = os.environ['machine']
MPMD = os.environ['MPMD']
nproc = int(os.environ['nproc'])
start_date = os.environ['start_date']
end_date = os.environ['end_date']
RUN_abbrev = os.environ['RUN_abbrev']

# Set up date information
sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]),
                          int(start_date[6:]))
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]),
                          int(end_date[6:]))
# Set important METplus paths
USHMETplus_run_metplus = os.path.join(
    os.environ['USHMETplus'], 'run_metplus.py'
)
PARMverif_global_machine_conf = os.path.join(
    os.environ['PARMverif_global'], 'metplus_config', 'machine.conf'
)
PARMverif_global_METplus_version_conf_dir = os.path.join(
    os.environ['PARMverif_global'], 'metplus_config', 'metplus_use_cases',
    'METplusV'+os.environ['METplus_version']
)

# Run job creation function
if RUN in ['grid2grid_step1', 'grid2obs_step1', 'precip_step1',
           'satellite_step1']:
    create_job_scripts_step1(
        sdate, edate, RUN.split('_')[0], RUN_abbrev,
        os.environ[RUN_abbrev+'_type_list'].split(' '),
        USHMETplus_run_metplus, PARMverif_global_machine_conf,
        PARMverif_global_METplus_version_conf_dir
    )
elif RUN in ['grid2grid_step2', 'grid2obs_step2', 'precip_step2',
             'satellite_step2']:
    create_job_scripts_step2(
        sdate, edate, RUN.split('_')[0], RUN_abbrev,
        os.environ[RUN_abbrev+'_type_list'].split(' '),
        USHMETplus_run_metplus, PARMverif_global_machine_conf,
        PARMverif_global_METplus_version_conf_dir
    )
elif RUN in ['maps2d', 'mapsda']:
    create_job_scripts_maps(
        sdate, edate, RUN, RUN_abbrev,
        os.environ[RUN_abbrev+'_type_list'].split(' '),
        USHMETplus_run_metplus, PARMverif_global_machine_conf,
        PARMverif_global_METplus_version_conf_dir
    )

# If running MPMD, create POE scripts
if MPMD == 'YES':
    job_files = glob.glob(
        os.path.join(DATA, RUN, 'metplus_job_scripts', 'job*')
    )
    njob_files = len(job_files)
    if njob_files == 0:
        print("ERROR: No job files created in "
              +os.path.join(DATA, RUN, 'metplus_job_scripts'))
        sys.exit(1)
    njob, iproc = 1, 0
    node = 1
    while njob <= njob_files:
        job = 'job'+str(njob)
        if machine in ['HERA', 'URSA', 'ORION', 'HERCULES', 'GAEAC6']:
            if iproc >= nproc:
                poe_file.close()
                iproc = 0
                node+=1
        poe_filename = os.path.join(DATA, RUN, 'metplus_job_scripts',
                                        'poe_jobs'+str(node))
        if iproc == 0:
            poe_file = open(poe_filename, 'w')
        iproc+=1
        if machine in ['HERA', 'URSA', 'ORION', 'HERCULES', 'GAEAC6']:
            poe_file.write(
                str(iproc-1)+' '
                +os.path.join(DATA, RUN, 'metplus_job_scripts', job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(DATA, RUN, 'metplus_job_scripts', job)+'\n'
            )
        njob+=1
    poe_file.close()
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_file = open(poe_filename, 'a')
    iproc+=1
    while iproc <= nproc:
        if machine in ['HERA', 'URSA', 'ORION', 'HERCULES', 'GAEAC6']:
            poe_file.write(
                str(iproc-1)+' /bin/echo '+str(iproc)+'\n'
            )
        else:
            poe_file.write(
                '/bin/echo '+str(iproc)+'\n'
            )
        iproc+=1
    poe_file.close()

print("END: "+os.path.basename(__file__))
