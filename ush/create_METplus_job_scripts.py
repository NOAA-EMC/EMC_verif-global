'''
Program Name: create_METplus_job_scripts.py
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

# Read in environment variables
METplus_version = os.environ['METplus_version']
PARMverif_global = os.environ['PARMverif_global']
USHMETplus = os.environ['USHMETplus']
USHverif_global = os.environ['USHverif_global']
DATA = os.environ['DATA']
RUN = os.environ['RUN']
machine = os.environ['machine']
MPMD = os.environ['MPMD']
nproc = int(os.environ['nproc'])

if RUN == 'grid2grid_step1':
    type_list = os.environ['g2g1_type_list'].split(' ')
    case = 'grid2grid'
if RUN == 'grid2grid_step2':
    type_list = os.environ['g2g2_type_list'].split(' ')
    case = 'grid2grid'
elif RUN == 'grid2obs_step1':
    type_list = os.environ['g2o1_type_list'].split(' ')
    case = 'grid2obs'
elif RUN == 'grid2obs_step2':
    type_list = os.environ['g2o2_type_list'].split(' ')
    case = 'grid2obs'
elif RUN == 'precip_step1':
    type_list = os.environ['precip1_type_list'].split(' ')
    case = 'precip'
elif RUN == 'precip_step2':
    type_list = os.environ['precip2_type_list'].split(' ')
    case = 'precip'
model_list = os.environ['model_list'].split(' ')
model_arch_dir_list = os.environ['model_arch_dir_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']

# METplus paths
master_metplus = os.path.join(USHMETplus, 'master_metplus.py')
metplus_machine_conf = os.path.join(PARMverif_global, 'metplus_config',
                                    'machine.conf')
metplus_version_conf_dir = os.path.join(PARMverif_global,
                                        'metplus_config',
                                        'metplus_use_cases',
                                        'METplusV'+METplus_version)

# Set up date information
sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]),
                          int(start_date[6:]))
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]),
                          int(end_date[6:]))

def set_job_common_env(job_file):
    """! Writes out environment variables common
         to all METplus job
        
         Args:
             job_file - string of the path of the
                        METplus job card name
 
         Returns:
    """
    env_var_list = [ 'HOMEverif_global', 'USHverif_global', 'HOMEMETplus',
                     'HOMEMET', 'DATA', 'RUN', 'WGRIB2', 'NCAP2', 'NCDUMP',
                     'CONVERT', 'METplus_verbosity', 'MET_verbosity', 
                     'log_MET_output_to_METplus', 'PARMverif_global',
                     'USHMETplus', 'FIXverif_global', 'METplus_version',
                     'MET_version' ]
    job_file.write('#!/bin/sh\n')
    for env_var in env_var_list:
        job_file.write('export '+env_var+'="'+os.environ[env_var]+'"\n')

def create_job_script_step1(sdate, edate, model_list, type_list, case):
    """! Writes out job cards based on requested verification
        for step 1 jobs
        
         Args:
             sdate      - datetime object of the verification start
                          date
             edate      - datetime object of the verification end
                          date
             model_list - list of strings of model names
             type_list  - list of strings of the types of the
                          verification use case
             case       - string of the verification use case
 
         Returns:
    """
    njob = 0
    date = sdate
    while date <= edate:
        for model in model_list:
            for type in type_list:
                njob+=1
                # Set up information for environment variables
                if case == 'grid2grid':
                    fhr_list = os.environ['g2g1_fhr_list']
                    gather_by = os.environ['g2g1_gather_by']
                    valid_hr_beg = os.environ['g2g1_valid_hr_beg']
                    valid_hr_end = os.environ['g2g1_valid_hr_end']
                    valid_hr_inc = os.environ['g2g1_valid_hr_inc']
                    init_hr_beg = os.environ['g2g1_init_hr_beg']
                    init_hr_end = os.environ['g2g1_init_hr_end']
                    init_hr_inc = os.environ['g2g1_init_hr_inc']
                    extra_env_info = {}
                    if type == 'sfc':
                        obtype = model+'_f00'
                    else:
                        if os.environ['g2g1_anl_name'] == 'self_anl':
                            obtype = model+'_anl'
                        elif os.environ['g2g1_anl_name'] == 'self_f00':
                            obtype = model+'_f00'
                        elif os.environ['g2g1_anl_name'] == 'gfs_anl':
                            obtype = 'gfs_anl'
                        elif os.environ['g2g1_anl_name'] == 'gfs_f00':
                            obtype = 'gfs_f00'
                        anl_file_list = glob.glob(
                            os.path.join(os.environ['DATA'], 
                                         'grid2grid_step1', 'data', model,
                                         'anl.'+date.strftime('%Y%m%d')+'*')
                        )
                        link_anl_type = []
                        if len(anl_file_list) > 0:
                            for anl_file in anl_file_list:
                                if os.path.islink(anl_file):
                                    if (os.readlink(anl_file) ==
                                            anl_file.replace('anl', 'f00')):
                                        link_anl_type.append('f00')
                                    else:
                                        link_anl_type.append('anl')
                                else:
                                    if os.path.exists(anl_file):
                                        link_anl_type.append('anl')
                            if all(anl == 'f00' for anl in link_anl_type):
                                obtype = obtype.replace('anl', 'f00')
                    extra_env_info['verif_grid'] = os.environ['g2g1_grid']
                elif case == 'grid2obs':
                    gather_by = os.environ['g2o1_gather_by']
                    init_hr_beg = os.environ['g2o1_init_hr_beg']
                    init_hr_end = os.environ['g2o1_init_hr_end']
                    init_hr_inc = os.environ['g2o1_init_hr_inc']
                    extra_env_info = {}
                    if type == 'upper_air':
                        fhr_list = os.environ['g2o1_fhr_list_upper_air']
                        obtype = os.environ['g2o1_obtype_upper_air']
                        valid_hr_beg = (
                            os.environ['g2o1_valid_hr_beg_upper_air']
                        )
                        valid_hr_end = (
                            os.environ['g2o1_valid_hr_end_upper_air']
                        )
                        valid_hr_inc = (
                            os.environ['g2o1_valid_hr_inc_upper_air']
                        )
                        extra_env_info['prepbufr'] = 'gdas'
                        extra_env_info['verif_grid'] = (
                            os.environ['g2o1_grid_upper_air']
                        )
                    elif type == 'conus_sfc':
                        fhr_list = os.environ['g2o1_fhr_list_conus_sfc']
                        obtype = os.environ['g2o1_obtype_conus_sfc']
                        valid_hr_beg = (
                            os.environ['g2o1_valid_hr_beg_conus_sfc']
                        )
                        valid_hr_end = (
                            os.environ['g2o1_valid_hr_end_conus_sfc']
                        )
                        valid_hr_inc = (
                            os.environ['g2o1_valid_hr_inc_conus_sfc']
                        )
                        if int(date.strftime('%Y%m%d')) > 20170319:
                            extra_env_info['prepbufr'] = 'nam'
                        else:
                            extra_env_info['prepbufr'] = 'ndas'
                        extra_env_info['verif_grid'] = (
                            os.environ['g2o1_grid_conus_sfc']
                        )
                elif case == 'precip':
                    gather_by = os.environ['precip1_gather_by']
                    fhr_list = os.environ['precip1_fhr_list']
                    obtype = os.environ['precip1_obtype']
                    valid_hr_beg = os.environ['precip1_valid_hr_beg']
                    valid_hr_end = os.environ['precip1_valid_hr_end']
                    valid_hr_inc = os.environ['precip1_valid_hr_inc']
                    init_hr_beg = os.environ['precip1_init_hr_beg']
                    init_hr_end = os.environ['precip1_init_hr_end']
                    init_hr_inc = os.environ['precip1_init_hr_inc']
                    extra_env_info = {}
                    extra_env_info['verif_grid'] = os.environ['precip1_grid']
                    model_bucket_list = (
                        os.environ['precip1_model_bucket_list'].split(' ')
                    )
                    model_varname_list = (
                        os.environ['precip1_model_varname_list'].split(' ')
                    )
                    model_fileformat_list = (
                        os.environ['precip1_model_fileformat_list'].split(' ')
                    )
                    model_index = model_list.index(model)
                    extra_env_info['model_bucket'] = (
                        model_bucket_list[model_index]
                    )
                    extra_env_info['model_varname'] = (
                        model_varname_list[model_index]
                    )
                    extra_env_info['model_filetype'] = (
                        model_fileformat_list[model_index][0:4]
                    )
                # Create job file
                job_filename = os.path.join(DATA, RUN,
                                            'metplus_job_scripts',
                                            'job'+str(njob))
                job_file = open(job_filename, 'w')
                set_job_common_env(job_file)
                job_file.write('export DATE="'+date.strftime('%Y%m%d')+'"\n')
                job_file.write('export model="'+model+'"\n')
                job_file.write('export obtype="'+obtype+'"\n')
                job_file.write('export make_met_data_by="'+make_met_data_by+'"\n')
                job_file.write('export gather_by="'+gather_by+'"\n')
                job_file.write('export fhr_list="'+fhr_list+'"\n')
                job_file.write('export valid_hr_beg="'+valid_hr_beg+'"\n')
                job_file.write('export valid_hr_end="'+valid_hr_end+'"\n')
                job_file.write('export valid_hr_inc="'+valid_hr_inc+'"\n')
                job_file.write('export init_hr_beg="'+init_hr_beg+'"\n')
                job_file.write('export init_hr_end="'+init_hr_end+'"\n')
                job_file.write('export init_hr_inc="'+init_hr_inc+'"\n')
                for name, value in extra_env_info.items():
                    job_file.write('export '+name+'="'+value+'"\n')
                job_file.write('\n')
                metplus_conf_list = [
                    os.path.join(metplus_version_conf_dir, case,
                                 'make_met_data_by_'+make_met_data_by,
                                 type+'.conf')
                ]
                if case == 'grid2grid' and type == 'anom':
                    metplus_conf_list.append(
                        os.path.join(metplus_version_conf_dir, case,
                                     'make_met_data_by_'+make_met_data_by,
                                     type+'_height.conf')
                    )
                metplus_conf_list.append(
                    os.path.join(metplus_version_conf_dir, case,
                                 'gather_by_'+gather_by,
                                 type+'.conf')
                )
                for metplus_conf in metplus_conf_list:
                    job_file.write(
                        master_metplus+' '
                        +'-c '+metplus_machine_conf+' '
                        +'-c '+metplus_conf+'\n'
                    )
                job_file.close()
        date = date + datetime.timedelta(days=1)

def create_job_script_step2(sdate, edate, model_list, type_list, case):
    """! Writes out job cards based on requested verification
        for step 2 jobs
        
         Args:
             sdate      - datetime object of the verification start
                          date
             edate      - datetime object of the verification end
                          date
             model_list - list of strings of model names
             type_list  - list of strings of the types of the
                          verification use case
             case       - string of the verification use case
 
         Returns:
    """
    njob = 0
    for type in type_list:
        # Set up information for environment variables
        if case == 'grid2grid':
            model_plot_name_list = (
                os.environ['g2g2_model_plot_name_list'].split(' ')
            )
            anl_name_list = os.environ['g2g2_anl_name_list'].split(' ')
            if len(model_plot_name_list) != len(model_list):
                print(
                    "model_list and g2g2_model_plot_name_list "
                    +"not of equal length"
                )
                exit(1)
            if len(anl_name_list) != len(model_list):
                print(
                    "model_list and g2g2_anl_name_list not of equal length"
                )
                exit(1)
            fhr_list = os.environ['g2g2_fhr_list']
            valid_hr_beg = os.environ['g2g2_valid_hr_beg']
            valid_hr_end = os.environ['g2g2_valid_hr_end']
            valid_hr_inc = os.environ['g2g2_valid_hr_inc']
            init_hr_beg = os.environ['g2g2_init_hr_beg']
            init_hr_end = os.environ['g2g2_init_hr_end']
            init_hr_inc = os.environ['g2g2_init_hr_inc']
            event_equalization = os.environ['g2g2_event_eq']
            interp = 'NEAREST'
            extra_env_info = {}
            extra_env_info['verif_grid'] = os.environ['g2g2_grid']
            if type == 'anom':
                line_type = 'SAL1L2, VAL1L2'
                plot_stats_list = 'acc'
                vx_mask_list = ['G002', 'NHX', 'SHX', 
                                'PNA', 'TRO']
                vars_and_levels_dict = {
                    'HGT': ['P1000', 'P700', 'P500', 'P250'],
                    'TMP': ['P850', 'P500', 'P250'],
                    'UGRD': ['P850', 'P500', 'P250'],
                    'VGRD': ['P850', 'P500', 'P250'],
                    'UGRD_VGRD': ['P850', 'P500', 'P250'],
                    'PRMSL': ['Z0']
                }
            elif type == 'pres':
                line_type = 'SL1L2, VL1L2'
                plot_stats_list = (
                    'bias, rmse, msess, rsd, rmse_md, rmse_pv'
                )
                vx_mask_list = ['G002', 'NHX', 'SHX',
                                'PNA', 'TRO']
                vars_and_levels_dict = {
                    'HGT': ['P1000', 'P850', 'P700', 
                            'P500', 'P200', 'P100', 
                             'P50', 'P20', 'P10'],
                    'TMP': ['P1000', 'P850', 'P700',
                            'P500', 'P200', 'P100',
                            'P50', 'P20', 'P10'],
                    'UGRD': ['P1000', 'P850', 'P700',
                             'P500', 'P200', 'P100',
                             'P50', 'P20', 'P10'],
                    'VGRD': ['P1000', 'P850', 'P700',
                             'P500', 'P200', 'P100',
                             'P50', 'P20', 'P10'],
                    'UGRD_VGRD': ['P1000', 'P850', 'P700',
                                  'P500', 'P200', 'P100',
                                  'P50', 'P20', 'P10'],
                    'O3MR': ['P100', 'P70', 'P50', 
                             'P30', 'P20', 'P10']
                }
            elif type == 'sfc':
                line_type = 'SL1L2, VL1L2'
                plot_stats_list = 'fbar'
                vx_mask_list = ['G002', 'NHX', 'SHX', 
                                'N60', 'S60', 'TRO',
                                'NPO', 'SPO', 'NAO',
                                'SAO', 'CONUS']
                vars_and_levels_dict = {
                    'TMP': ['Z2', 'Z0', 'L0'],
                    'RH': ['Z2'],
                    'SPFH': ['Z2'],
                    'HPBL': ['L0'],
                    'PRES': ['Z0', 'L0'],
                    'PRMSL': ['Z0'],
                    'UGRD': ['Z10'],
                    'VGRD': ['Z10'],
                    'TSOIL': ['Z10-0'],
                    'SOILW': ['Z10-0'],
                    'WEASD': ['Z0'],
                    'CAPE': ['Z0'],
                    'PWAT': ['L0'],
                    'CWAT': ['L0'],
                    'HGT': ['L0'],
                    'TOZNE': ['L0']
                }
            model_info = {}
            nmodels = int(len(model_list))
            if nmodels > 8:
                print(
                    "Too many models listed in model_list. "
                    +"Current maximum is 8."
                )
                exit(1)
            for model in model_list:
                index = model_list.index(model)
                model_num = index + 1
                model_info['model'+str(model_num)] = model
                model_info['model'+str(model_num)+'_plot_name'] = (
                         model_plot_name_list[index]
                )
                if (len(model_arch_dir_list) != len(model_list) 
                        and len(model_arch_dir_list) > 1):
                    print(
                        "model_arch_dir_list and model_list not of "
                        +"equal length"
                    )
                    exit(1)
                elif (len(model_arch_dir_list) != len(model_list) 
                        and len(model_arch_dir_list) == 1):
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[0]
                    )
                else:
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[index]
                    )
                if type == 'sfc':
                    obtype = model+'_f00'
                else:
                    anl_name = anl_name_list[index]
                    if anl_name == 'self_anl':
                        obtype = model+'_anl'
                    elif anl_name == 'self_f00':
                        obtype = model+'_f00'
                    elif anl_name == 'gfs_anl':
                        obtype = 'gfs_anl'
                    elif anl_name == 'gfs_f00':
                        obtype = 'gfs_f00'
                model_info['model'+str(model_num)+'_obtype'] = obtype
        elif case == 'grid2obs':
            model_plot_name_list = (
                os.environ['g2o2_model_plot_name_list'].split(' ')
            )
            if len(model_plot_name_list) != len(model_list):
                print(
                    "model_list and g2o2_model_plot_name_list "
                    +"are not of equal length"
                )
                exit(1)
            init_hr_beg = os.environ['g2o2_init_hr_beg']
            init_hr_end = os.environ['g2o2_init_hr_end']
            init_hr_inc = os.environ['g2o2_init_hr_inc']
            event_equalization = os.environ['g2o2_event_eq']
            interp = 'BILIN'
            line_type = 'SL1L2, VL1L2'
            plot_stats_list = 'bias, rmse, fbar_obar'
            extra_env_info = {}
            if type == 'upper_air':
                fhr_list = os.environ['g2o2_fhr_list_upper_air']
                obtype = os.environ['g2o2_obtype_upper_air']
                valid_hr_beg = (
                    os.environ['g2o2_valid_hr_beg_upper_air']
                )
                valid_hr_end = (
                    os.environ['g2o2_valid_hr_end_upper_air']
                )
                valid_hr_inc = (
                    os.environ['g2o2_valid_hr_inc_upper_air']
                )
                extra_env_info['verif_grid'] = (
                    os.environ['g2o2_grid_upper_air']
                )
                vx_mask_list = ['G003', 'NH', 'SH', 'TRO', 'G236']
                vars_and_levels_dict = {
                    'TMP': ['P1000', 'P925', 'P850', 'P700', 'P500', 'P400',
                            'P300', 'P250', 'P200', 'P150', 'P100', 'P50'],
                    'RH': ['P1000', 'P925', 'P850', 'P700', 'P500', 'P400',
                           'P300'],
                    'UGRD_VGRD': ['P1000', 'P925', 'P850', 'P700', 'P500',
                                  'P400', 'P300', 'P250', 'P200', 'P150',
                                   'P100', 'P50']
                }
            elif type == 'conus_sfc':
                fhr_list = os.environ['g2o2_fhr_list_conus_sfc']
                obtype = os.environ['g2o2_obtype_conus_sfc']
                valid_hr_beg = (
                    os.environ['g2o2_valid_hr_beg_conus_sfc']
                )
                valid_hr_end = (
                    os.environ['g2o2_valid_hr_end_conus_sfc']
                )
                valid_hr_inc = (
                    os.environ['g2o2_valid_hr_inc_conus_sfc']
                )
                extra_env_info['verif_grid'] = (
                    os.environ['g2o2_grid_conus_sfc']
                )
                vx_mask_list = ['G104', 'WEST', 'EAST', 'MDW', 'NPL', 'SPL',
                                'NEC', 'SEC', 'NWC', 'SWC', 'NMT', 'SMT',
                                'SWD', 'GRB', 'LMV', 'GMC', 'APL', 'NAK',
                                'SAK']
                vars_and_levels_dict = {
                    'TMP': ['Z2'],
                    'RH': ['Z2'],
                    'DPT': ['Z2'],
                    'UGRD_VGRD': ['Z10'],
                    'TCDC': ['L0'],
                    'PRMSL': ['Z0']
                }
            model_info = {}
            nmodels = int(len(model_list))
            if nmodels > 8:
                print(
                    "Too many models listed in model_list. "
                    +"Current maximum is 8."
                )
                exit(1)
            for model in model_list:
                index = model_list.index(model)
                model_num = index + 1
                model_info['model'+str(model_num)] = model
                model_info['model'+str(model_num)+'_plot_name'] = (
                         model_plot_name_list[index]
                )
                if (len(model_arch_dir_list) != len(model_list)
                        and len(model_arch_dir_list) > 1):
                    print(
                        "model_arch_dir_list and model_list not of "
                        +"equal length"
                    )
                    exit(1)
                elif (len(model_arch_dir_list) != len(model_list)
                        and len(model_arch_dir_list) == 1):
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[0]
                    )
                else:
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[index]
                    )
                model_info['model'+str(model_num)+'_obtype'] = obtype
        elif case == 'precip':
            model_plot_name_list = (
                os.environ['precip2_model_plot_name_list'].split(' ')
            )
            if len(model_plot_name_list) != len(model_list):
                print(
                    "model_list and precip2_model_plot_name_list "
                    +"not of equal length"
                )
                exit(1)
            obtype = os.environ['precip2_obtype'] 
            fhr_list = os.environ['precip2_fhr_list']
            valid_hr_beg = os.environ['precip2_valid_hr_beg']
            valid_hr_end = os.environ['precip2_valid_hr_end']
            valid_hr_inc = os.environ['precip2_valid_hr_inc']
            init_hr_beg = os.environ['precip2_init_hr_beg']
            init_hr_end = os.environ['precip2_init_hr_end']
            init_hr_inc = os.environ['precip2_init_hr_inc']
            event_equalization = os.environ['precip2_event_eq']
            interp = 'NEAREST'
            line_type = 'CTC'
            plot_stats_list = 'bias, ets'
            vx_mask_list = ['G211']
            extra_env_info = {}
            extra_env_info['verif_grid'] = os.environ['precip2_grid']
            extra_env_info['var_thresholds'] = (
                'ge0.2, ge2, ge5, ge10, ge15, ge25, ge35, ge50, ge75'
            )
            if type == 'ccpa_accum24hr':
                vars_and_levels_dict = {
                    'APCP_24': ['A24']
                }
            model_info = {}
            nmodels = int(len(model_list))
            if nmodels > 8:
                print(
                    "Too many models listed in model_list. "
                    +"Current maximum is 8."
                )
                exit(1)
            for model in model_list:
                index = model_list.index(model)
                model_num = index + 1
                model_info['model'+str(model_num)] = model
                model_info['model'+str(model_num)+'_plot_name'] = (
                         model_plot_name_list[index]
                )
                if (len(model_arch_dir_list) != len(model_list)
                        and len(model_arch_dir_list) > 1):
                    print(
                        "model_arch_dir_list and model_list not of "
                        +"equal length"
                    )
                    exit(1)
                elif (len(model_arch_dir_list) != len(model_list)
                        and len(model_arch_dir_list) == 1):
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[0]
                    )
                else:
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[index]
                    )
                model_info['model'+str(model_num)+'_obtype'] = obtype
        for var_name, var_levels in vars_and_levels_dict.items():
            for vx_mask in vx_mask_list:
                njob+=1
                # Create job file
                job_filename = os.path.join(DATA, RUN,
                                            'metplus_job_scripts',
                                            'job'+str(njob))
                job_file = open(job_filename, 'w')
                set_job_common_env(job_file)
                job_file.write('export START_DATE="'
                               +sdate.strftime('%Y%m%d')+'"\n')
                job_file.write('export END_DATE="'
                               +edate.strftime('%Y%m%d')+'"\n')
                job_file.write('export plot_by="'+plot_by+'"\n')
                job_file.write('export fhr_list="'+fhr_list+'"\n')
                job_file.write('export valid_hr_beg="'+valid_hr_beg+'"\n')
                job_file.write('export valid_hr_end="'+valid_hr_end+'"\n')
                job_file.write('export valid_hr_inc="'+valid_hr_inc+'"\n')
                job_file.write('export init_hr_beg="'+init_hr_beg+'"\n')
                job_file.write('export init_hr_end="'+init_hr_end+'"\n')
                job_file.write('export init_hr_inc="'+init_hr_inc+'"\n')
                job_file.write('export var_name="'+var_name+'"\n')
                job_file.write('export var_levels="'
                               +' '.join(var_levels).replace(' ', ', ')+'"\n')
                job_file.write('export vx_mask="'+vx_mask+'"\n')
                job_file.write('export line_type="'+line_type+'"\n')
                job_file.write('export plot_stats_list="'
                               +plot_stats_list+'"\n')
                job_file.write('export event_equalization="'
                               +event_equalization+'"\n')
                job_file.write('export interp="'+interp+'"\n')
                job_file.write('export verif_case_type="'+type+'"\n')
                for name, value in model_info.items():
                    job_file.write('export '+name+'="'+value+'"\n')
                for name, value in extra_env_info.items():
                    job_file.write('export '+name+'="'+value+'"\n')
                job_file.write('\n')
                job_file.write('python '
                               +os.path.join(USHverif_global,
                                             'prune_stat_files.py\n\n'))
                if (case == 'grid2grid' and type == 'anom'
                        and var_name == 'HGT'):
                    metplus_conf = os.path.join(metplus_version_conf_dir,
                                                case, 'plot_by_'+plot_by,
                                                type+'_height_nmodels'
                                                +str(nmodels)+'.conf\n')
                else:
                    metplus_conf = os.path.join(metplus_version_conf_dir,
                                                case, 'plot_by_'+plot_by,
                                                type+'_nmodels'
                                                +str(nmodels)+'.conf\n')
                job_file.write(
                    master_metplus+' '
                    +'-c '+metplus_machine_conf+' '
                    +'-c '+metplus_conf+'\n'
                )
                if case == 'precip':
                    job_file.write(
                        os.path.join(USHverif_global, 'plotting_scripts',
                                     'make_plots_wrapper_precip.py')+' '
                        +'-c '+metplus_machine_conf+' '
                        +'-c '+metplus_conf+'\n'
                )
                job_file.write(
                    'ln -sf '
                    +os.path.join(DATA, RUN, 'metplus_output',
                                  'plot_by_'+plot_by, 'make_plots',
                                  var_name+'_'+vx_mask, case, type,
                                  'imgs', '*')+' '
                    +os.path.join(DATA, RUN, 'metplus_output',
                                  'images/.')
                )
                job_file.close()

# Run job creation function
if RUN in ['grid2grid_step1', 'grid2obs_step1', 'precip_step1']:
    create_job_script_step1(sdate, edate, model_list, type_list, case)   
elif RUN in ['grid2grid_step2', 'grid2obs_step2', 'precip_step2']:
    create_job_script_step2(sdate, edate, model_list, type_list, case)

# If running MPMD, create POE scripts
if MPMD == 'YES':
    job_files = glob.glob(
        os.path.join(DATA, RUN, 'metplus_job_scripts', 'job*')
    )
    njob_files = len(job_files)
    njob, iproc = 1, 0
    node, rank = 1, 0
    while njob <= njob_files:
        job = 'job'+str(njob)
        if machine == 'THEIA' or machine == 'HERA':
            if iproc >= nproc:
                poe_file.close()
                iproc = 0
                rank = 0
                node+=1
        poe_filename = os.path.join(DATA, RUN, 'metplus_job_scripts',
                                        'poe_jobs'+str(node))
        if iproc == 0:
            poe_file = open(poe_filename, 'w')
        iproc+=1
        if machine == 'THEIA' or machine == 'HERA':
            poe_file.write(
                rank+' '+os.path.join(DATA, RUN, 'metplus_job_scripts', job)
                +'\n'
            )
            rank+=1
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
    rank+=1
    while iproc <= nproc:
        if machine == 'THEIA' or machine == 'HERA':
            poe_file.write(
                rank+' /bin/echo '+str(iproc)+'\n'
            )
            rank+=1
        else:
            poe_file.write(
                '/bin/echo '+str(iproc)+'\n'
            )
        iproc+=1
poe_file.close()

print("END: "+os.path.basename(__file__))
