'''
Program Name: step2_ccpa_accum24hr_create_job_scripts.py
Contact(s): Shannon Shields (grid2grid)/Binbin Zhou(ccpa_accum24hr)
Abstract: This script is run by exgrid2grdi_step2.sh/exccpa_accum24hr_step2.sh in scripts/.
          This creates multiple independent job cards. These
          jobs contain all the necessary environment variables
          and commands needed to run the specific
          plot verification use case and types (each job
          could be run independently on the command line).
'''

import sys
import os
import datetime
import glob
import itertools
import numpy as np
import subprocess
import copy
import verif_global_util as vfg_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
RUN_CASE = (os.environ['RUN'].split('_')[0])
JOB_GROUP = os.environ['JOB_GROUP']
machine = os.environ['machine']
MPMD = os.environ['MPMD']
ncpus_per_node = int(os.environ['ncpus_per_node'])
start_date = os.environ['start_date']
end_date = os.environ['end_date']
plot_by = os.environ['plot_by']
RUN_abbrev = os.environ['RUN_abbrev']
case_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')

njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, RUN,
                                  'plot_job_scripts', JOB_GROUP)
vfg_util.make_dir(JOB_GROUP_jobs_dir)

# Set up base plotting information dictionary
base_plot_jobs_info_dict = {
    'ccpa_accum24hr': {
        '24hrCCPA': {'vx_masks': ['CONUS', 'EAST', 'WEST'],
                     'fcst_var_dict': {'name': 'APCP',
                                       'levels': ['A24']},
                     #Binbin: 'obs_var_dict': {'name': 'APCP',
                     'obs_var_dict': {'name': 'APCP_24',
                                     'levels': ['A24']},
                     'obs_name': '24hrCCPA'},
    }
}

# condense_stats jobs
condense_stats_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
# ccpa_accum24hr
for ccpa_accum24hr_job in list(condense_stats_jobs_dict['ccpa_accum24hr'].keys()):
    condense_stats_jobs_dict['ccpa_accum24hr']['24hrCCPA']['line_types'] = 'CTC'
    #ccpa_accum24hr_job_line_types = ['CTC']

if JOB_GROUP == 'condense_stats':
    JOB_GROUP_dict = condense_stats_jobs_dict

# filter_stats jobs
filter_stats_jobs_dict = copy.deepcopy(condense_stats_jobs_dict)
# ccpa_accum24hr
for ccpa_accum24hr_job in list(filter_stats_jobs_dict['ccpa_accum24hr'].keys()):
    filter_stats_jobs_dict['ccpa_accum24hr']['24hrCCPA']['line_types'] = 'CTC'
    filter_stats_jobs_dict['ccpa_accum24hr']['24hrCCPA']['fcst_var_dict']['threshs'] = [
        'ge0.2', 'ge2', 'ge5', 'ge10', 'ge15', 'ge25', 'ge35', 'ge50', 'ge75'
    ]
    filter_stats_jobs_dict['ccpa_accum24hr']['24hrCCPA']['obs_var_dict']['threshs'] = [
        'ge0.2', 'ge2', 'ge5', 'ge10', 'ge15', 'ge25', 'ge35', 'ge50', 'ge75'
    ]
    filter_stats_jobs_dict['ccpa_accum24hr']['24hrCCPA']['interps'] = ['NEAREST/1']

if JOB_GROUP == 'filter_stats':
    JOB_GROUP_dict = filter_stats_jobs_dict

# make_plots jobs
make_plots_jobs_dict = copy.deepcopy(filter_stats_jobs_dict)
# ccpa_accum24hr 
for ccpa_accum24hr_job in list(make_plots_jobs_dict['ccpa_accum24hr'].keys()):
    del make_plots_jobs_dict['ccpa_accum24hr'][ccpa_accum24hr_job]['line_types']
    make_plots_jobs_dict['ccpa_accum24hr']['24hrCCPA']['line_type_stats'] = [
        'CTC/ETS', 'CTC/FBIAS'
    ]
    make_plots_jobs_dict['ccpa_accum24hr']['24hrCCPA']['plots'] = [
        'time_series', 'lead_average', 'threshold_average', 'threshold_by_lead'
    ] 

if JOB_GROUP == 'make_plots':
    JOB_GROUP_dict = make_plots_jobs_dict

# Set up model environment variables in dictionary
model_list = os.environ['model_list'].split(' ')
for case_type in case_type_list:
    print("----> Making job scripts for "+RUN+" "
          +case_type+" for job group "+JOB_GROUP)
    RUN_abbrev_type = RUN_abbrev+'_'+case_type
    model_plot_name_list = (
        os.environ[RUN_abbrev+'_model_plot_name_list'].split(' ')
    )
    case_type_plot_jobs_dict = JOB_GROUP_dict[case_type]
    for case_type_job in list(case_type_plot_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = vfg_util.initialize_job_env_dict(
            case_type, JOB_GROUP,
            RUN_abbrev_type, case_type_job
        )
        job_env_dict['start_date'] = start_date
        job_env_dict['end_date'] = end_date
        job_env_dict['plot_by'] = plot_by
        job_env_dict['line_type'] = 'CTC'
        case_type_env_list = ['grid', 'event_eq']
        for case_type_env in case_type_env_list:
            job_env_dict[case_type_env] = (
                os.environ[RUN_abbrev_type+'_'+case_type_env]
            )
        if JOB_GROUP in ['filter_stats', 'make_plots']:
            valid_hr_start = int(job_env_dict['valid_hr_start'])
            valid_hr_end = int(job_env_dict['valid_hr_end'])
            valid_hr_inc = int(job_env_dict['valid_hr_inc'])
            valid_hrs = list(range(valid_hr_start,
                                   valid_hr_end+valid_hr_inc,
                                   valid_hr_inc))
        obs_list = (
            os.environ[RUN_abbrev_type+'_truth_name_list']\
            .split(' ')
        )
        for data_name in ['fcst', 'obs']:
            job_env_dict[data_name+'_var_name'] =  (
                case_type_plot_jobs_dict[case_type_job]\
                [data_name+'_var_dict']['name']
            )
        if JOB_GROUP == 'condense_stats':
            JOB_GROUP_case_type_job_product_loops = list(itertools.product(
                case_type_plot_jobs_dict[case_type_job]['line_types'],
                case_type_plot_jobs_dict[case_type_job]['fcst_var_dict']['levels'],
                case_type_plot_jobs_dict[case_type_job]['vx_masks'],
                model_list
            ))
        elif JOB_GROUP == 'filter_stats':
            JOB_GROUP_case_type_job_product_loops = list(itertools.product(
                case_type_plot_jobs_dict[case_type_job]['line_types'],
                case_type_plot_jobs_dict[case_type_job]['fcst_var_dict']['levels'],
                case_type_plot_jobs_dict[case_type_job]['vx_masks'],
                model_list,
                case_type_plot_jobs_dict[case_type_job]['fcst_var_dict']['threshs'],
                case_type_plot_jobs_dict[case_type_job]['interps'],
                valid_hrs
            ))
        elif JOB_GROUP == 'make_plots':
            JOB_GROUP_case_type_job_product_loops = list(itertools.product(
                case_type_plot_jobs_dict[case_type_job]['line_type_stats'],
                case_type_plot_jobs_dict[case_type_job]['plots'],
                case_type_plot_jobs_dict[case_type_job]['vx_masks'],
                case_type_plot_jobs_dict[case_type_job]['interps']
            ))
        for loop_info in JOB_GROUP_case_type_job_product_loops:
            if JOB_GROUP in ['condense_stats', 'filter_stats']:
                job_env_dict['fcst_var_level'] = loop_info[1]
                job_env_dict['obs_var_level'] = (
                    case_type_plot_jobs_dict[case_type_job]\
                    ['obs_var_dict']['levels'][
                        case_type_plot_jobs_dict[case_type_job]\
                        ['fcst_var_dict']['levels'].index(loop_info[1])
                    ]
                )
                job_env_dict['model_list'] = loop_info[3]
                job_env_dict['model_plot_name_list'] = (
                    model_plot_name_list[model_list.index(loop_info[3])]
                )
                job_env_dict['obs_list'] = (
                    obs_list[model_list.index(loop_info[3])]
                )
                obs_list[model_list.index(loop_info[3])]
                job_env_dict['vx_mask'] = loop_info[2]
                if JOB_GROUP == 'filter_stats':
                    job_env_dict['fcst_var_thresh'] = loop_info[4]
                    job_env_dict['obs_var_thresh'] = (
                        case_type_plot_jobs_dict[case_type_job]\
                        ['obs_var_dict']['threshs'][
                            case_type_plot_jobs_dict[case_type_job]\
                            ['fcst_var_dict']['threshs'].index(loop_info[4])
                        ]
                    )
                    job_env_dict['interp_method'] = loop_info[5].split('/')[0]
                    job_env_dict['interp_points'] = loop_info[5].split('/')[1]
                # Set up output directories
                njobs+=1
                job_env_dict['job_id'] = 'job'+str(njobs)
                job_DATA_dir = os.path.join(DATA, RUN, 'plot_output',
                                            'plot_by_'+plot_by,
                                            JOB_GROUP, case_type)
                job_env_dict['job_DATA_dir'] = job_DATA_dir
                vfg_util.make_dir(job_env_dict['job_DATA_dir'])
                # Create job file
                job_file = os.path.join(JOB_GROUP_jobs_dir,
                                        'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/bash\n')
                job.write('set -x\n')
                job.write('\n')
                # Write environment variables
                for name, value in job_env_dict.items():
                    job.write('export '+name+'="'+value+'"\n')
                job.write('\n')
                job.write(
                    vfg_util.python_command('precip', 'precip_plots.py',[])
                    +'\n'
                )
                job.close()
            elif JOB_GROUP == 'make_plots':
                job_env_dict['model_list'] = ', '.join(model_list)
                job_env_dict['model_plot_name_list'] = (
                    ', '.join(model_plot_name_list)
                )
                job_env_dict['obs_list'] = ', '.join(obs_list)
                job_env_dict['line_type'] = loop_info[0].split('/')[0]
                job_env_dict['stat'] = loop_info[0].split('/')[1]
                job_env_dict['plot'] = loop_info[1]
                job_env_dict['vx_mask'] = loop_info[2]
                job_env_dict['interp_method'] = loop_info[3].split('/')[0]
                job_env_dict['interp_points'] = loop_info[3].split('/')[1]
                if job_env_dict['plot'] == 'valid_hour_average':
                    plot_valid_hrs_loop = [valid_hrs]
                else:
                    plot_valid_hrs_loop = valid_hrs
                if job_env_dict['plot'] in ['threshold_average',
                                            'threshold_by_lead']:
                    plot_fcst_threshs_loop = [
                        case_type_plot_jobs_dict[case_type_job]\
                        ['fcst_var_dict']['threshs']
                    ]

                else:
                    plot_fcst_threshs_loop = (
                        case_type_plot_jobs_dict[case_type_job]\
                        ['fcst_var_dict']['threshs']
                    )
                plot_fcst_levels_loop = (
                    case_type_plot_jobs_dict[case_type_job]\
                    ['fcst_var_dict']['levels']
                )
                for plot_loop_info in list(
                    itertools.product(plot_valid_hrs_loop,
                                      plot_fcst_threshs_loop,
                                      plot_fcst_levels_loop)
                ):
                    job_env_dict['valid_hr_start'] = str(
                        plot_loop_info[0]
                    ).zfill(2)
                    job_env_dict['valid_hr_end'] = str(
                        plot_loop_info[0]
                    ).zfill(2)
                    job_env_dict['valid_hr_inc'] = str(valid_hr_inc)
                    if job_env_dict['plot'] in ['threshold_average',
                                                'threshold_by_lead']:
                        job_env_dict['fcst_var_thresh_list'] = ', '.join(
                            plot_loop_info[1]
                        )
                        job_env_dict['obs_var_thresh_list'] = ', '.join(
                            case_type_plot_jobs_dict[case_type_job]\
                            ['obs_var_dict']['threshs']
                        )
                    else:
                        job_env_dict['fcst_var_thresh_list'] = (
                            plot_loop_info[1]
                        )
                        job_env_dict['obs_var_thresh_list'] = (
                            case_type_plot_jobs_dict[case_type_job]\
                            ['obs_var_dict']['threshs']\
                            [case_type_plot_jobs_dict[case_type_job]\
                             ['fcst_var_dict']['threshs']\
                             .index(plot_loop_info[1])]
                        )
                    job_env_dict['fcst_var_level_list'] = plot_loop_info[2]
                    job_env_dict['obs_var_level_list'] = (
                        case_type_plot_jobs_dict[case_type_job]\
                        ['obs_var_dict']['levels']\
                        [case_type_plot_jobs_dict[case_type_job]\
                         ['fcst_var_dict']['levels']\
                         .index(plot_loop_info[2])]
                    )
                    run_verif_global_g2g_plots = ['plots']
                    for run_verif_global_g2g_plot in run_verif_global_g2g_plots:
                        # Set up output directories
                        njobs+=1
                        job_env_dict['job_id'] = 'job'+str(njobs)
                        job_DATA_dir = os.path.join(DATA, RUN, 'plot_output',
                                                    'plot_by_'+plot_by,
                                                    JOB_GROUP, case_type)
                        job_env_dict['job_DATA_dir'] = job_DATA_dir
                        vfg_util.make_dir(job_env_dict['job_DATA_dir'])
                        # Create job file
                        job_file = os.path.join(JOB_GROUP_jobs_dir,
                                                'job'+str(njobs))
                        print("Creating job script: "+job_file)
                        job = open(job_file, 'w')
                        job.write('#!/bin/bash\n')
                        job.write('set -x\n')
                        job.write('\n')
                        # Write environment variables
                        job_env_dict['job_id'] = 'job'+str(njobs)
                        for name, value in job_env_dict.items():
                            job.write('export '+name+'="'+value+'"\n')
                        job.write('\n')
                        job.write(
                            vfg_util.python_command('precip', 'precip_plots.py',[])
                            +'\n'
                        )
                        job.close()

# If running MPMD, create POE scripts
if MPMD == 'YES':
    job_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("NOTE: No job files created in "+JOB_GROUP_jobs_dir)
    poe_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'poe*'))
    npoe_files = len(poe_files)
    if npoe_files > 0:
        for poe_file in poe_files:
            os.remove(poe_file)
    njob, iproc, node = 1, 0, 1
    while njob <= njob_files:
        job = 'job'+str(njob)
        if machine in ['HERA', 'ORION', 'HERCULES', 'GAEAC6']:
            if iproc >= ncpus_per_node:
                poe_file.close()
                iproc = 0
                node+=1
        poe_filename = os.path.join(JOB_GROUP_jobs_dir,
                                    'poe_jobs'+str(node))
        if iproc == 0:
            poe_file = open(poe_filename, 'w')
        iproc+=1
        if machine in ['HERA', 'ORION', 'HERCULES', 'GAEAC6']:
            poe_file.write(
                os.path.join(JOB_GROUP_jobs_dir,job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(JOB_GROUP_jobs_dir, job)+'\n'
            )
        njob+=1
    poe_file.close()
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(JOB_GROUP_jobs_dir,
                                f"poe_jobs{str(node)}")
    poe_file = open(poe_filename, 'a')
    iproc+=1
    while iproc <= ncpus_per_node:
        if machine in ['HERA', 'ORION', 'HERCULES', 'GAEAC6']:
            poe_file.write(
                '/bin/echo '+str(iproc)+'\n'
            )
        else:
            poe_file.write(
                '/bin/echo '+str(iproc)+'\n'
            )
        iproc+=1
    poe_file.close()

print("END: "+os.path.basename(__file__))
