'''
Name: verif_global_util.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This contains many functions used across verif_global.
'''

import os
import datetime
import numpy as np
import subprocess
import shutil
import sys
import netCDF4 as netcdf
import glob
import pandas as pd
import logging
import copy
import itertools
import copy
from time import sleep

def run_shell_command(command):
    """! Run shell command

         Args:
             command - list of agrument entries (string)

         Returns:

    """
    print("Running  "+' '.join(command))
    if any(mark in ' '.join(command) for mark in ['"', "'", '|', '*', '>',
                                                  '-']):
        run_command = subprocess.run(
            ' '.join(command), shell=True
        )
    else:
        run_command = subprocess.run(command)
    if run_command.returncode != 0:
        print("FATAL ERROR: "+' '.join(run_command.args)+" gave return code "
              +str(run_command.returncode))
        sys.exit(run_command.returncode)

def make_dir(dir_path):
    """! Make a directory

         Args:
             dir_path - path of the directory (string)

         Returns:

    """
    if not os.path.exists(dir_path):
        print(f"Making directory {dir_path}")
        os.makedirs(dir_path, mode=0o755, exist_ok=True)

def python_command(python_script_name, script_arg_list):
    """! Write out full call to python

         Args:
             python_script_name - python script name (string)
             script_arg_list    - list of script arguments (strings)

         Returns:
             python_cmd - full call to python (string)

    """
    python_script = os.path.join(os.environ['USHverif_global'],
                                 python_script_name)
    if not os.path.exists(python_script):
        print("FATAL ERROR: "+python_script+" DOES NOT EXIST")
        sys.exit(1)
    python_cmd = 'python '+python_script
    for script_arg in script_arg_list:
        python_cmd = python_cmd+' '+script_arg
    return python_cmd

def python_g2g_command(python_script_name, script_arg_list):
    """! Write out full call to python for ush/plots/grid2grid

         Args:
             python_script_name - python script name (string)
             script_arg_list    - list of script arguments (strings)

         Returns:
             python_cmd - full call to python (string)
    """
    python_script = os.path.join(os.environ['USHverif_global'],
                                 'plots', 'grid2grid',
                                 python_script_name)
    if not os.path.exists(python_script):
        print("FATAL ERROR: "+python_script+" DOES NOT EXIST")
        sys.exit(1)
    python_cmd = 'python '+python_script
    for script_arg in script_arg_list:
        python_cmd = python_cmd+' '+script_arg
    return python_cmd

def check_file_exists_size(file_name):
    """! Checks to see if file exists and has size greater than 0

         Args:
             file_name - file path (string)

         Returns:
             file_good - boolean
                       - True: file exists,file size >0
                       - False: file doesn't exist
                                OR file size = 0
    """
    if '/com/' in file_name or '/dcom/' in file_name:
        alert_word = 'WARNING'
    else:
        alert_word = 'NOTE'
    if os.path.exists(file_name):
        if os.path.getsize(file_name) > 0:
            file_good = True
        else:
            print(f"{alert_word}: {file_name} empty, 0 sized")
            file_good = False
    else:
        print(f"{alert_word}: {file_name} does not exist")
        file_good = False
    return file_good

def copy_file(source_file, dest_file):
    """! This copies a file from one location to another

         Args:
             source_file - source file path (string)
             dest_file   - destination file path (string)

         Returns:
    """
    if check_file_exists_size(source_file):
        print("Copying "+source_file+" to "+dest_file)
        shutil.copy(source_file, dest_file)

def convert_grib1_grib2(grib1_file, grib2_file):
    """! Converts GRIB1 data to GRIB2

         Args:
             grib1_file - string of the path to
                          the GRIB1 file to
                          convert (string)
             grib2_file - string of the path to
                          save the converted GRIB2
                          file (string)
         Returns:
    """
    print(f"Converting GRIB1 file {grib1_file} to GRIB2 file {grib2_file}")
    cnvgrib = os.environ['CNVGRIB']
    run_shell_command(
        [cnvgrib, '-g12', grib1_file, grib2_file, '>', '/dev/null', '2>&1']
    )

def convert_grib2_grib1(grib2_file, grib1_file):
    """! Converts GRIB2 data to GRIB1

         Args:
             grib2_file - string of the path to
                          the GRIB2 file to
                          convert
             grib1_file - string of the path to
                          save the converted GRIB1
                          file
         Returns:
    """
    print(f"Converting GRIB2 file {grib2_file} to GRIB1 file {grib1_file}")
    cnvgrib = os.environ['CNVGRIB']
    run_shell_command(
        [cnvgrib, '-g21', grib2_file, grib1_file, '>', '/dev/null', '2>&1']
    )

def convert_grib2_grib2(grib2_fileA, grib2_fileB):
    """! Converts GRIB2 data to GRIB2

         Args:
             grib2_fileA - string of the path to
                           the GRIB2 file to
                           convert
             grib2_fileB - string of the path to
                           save the converted GRIB2
                           file
         Returns:
    """
    print(f"Converting GRIB2 file {grib2_fileA} to GRIB2 file {grib2_fileB}")
    cnvgrib = os.environ['CNVGRIB']
    run_shell_command(
        [cnvgrib, '-g22', grib2_fileA, grib2_fileB, '>', '/dev/null', '2>&1']
    )

def check_grib1_file_corrupt(grib1_file):
    """! Checks if GRIB1 file is corrupt

         Args:
             grib1_file - string of the path to
                          the GRIB1 file to
                          convert
         Returns:
             file_is_corrupt - True means file is corrupt
                               False means file is not corrupt
    """
    WGRIB = os.environ['WGRIB']
    chk_corrupt = subprocess.run(
        f"{WGRIB} {grib1_file}  1> /dev/null 2>&1", shell=True
    )
    if chk_corrupt.returncode != 0:
        print(f"WARNING: {grib1_file} is corrupt")
        file_is_corrupt = True
    else:
        file_is_corrupt = False
    return file_is_corrupt

def check_grib2_file_corrupt(grib2_file):
    """! Checks if GRIB2 file is corrupt

         Args:
             grib2_file - string of the path to
                          the GRIB2 file to
                          convert
         Returns:
             file_is_corrupt - True means file is corrupt
                               False means file is not corrupt
    """
    WGRIB2 = os.environ['WGRIB2']
    chk_corrupt = subprocess.run(
        f"{WGRIB2} {grib2_file}  1> /dev/null 2>&1", shell=True
    )
    if chk_corrupt.returncode != 0:
        print(f"WARNING: {grib2_file} is corrupt")
        file_is_corrupt = True
    else:
        file_is_corrupt = False
    return file_is_corrupt

def check_netcdf_file_corrupt(netcdf_file):
    """! Checks if netCDF file is corrupt
                
         Args:
             netcdf_file - string of the path to
                           the netCDF file to 
                           convert
         Returns:
             file_is_corrupt - True means file is corrupt
                               False means file is not corrupt
    """
    chk_corrupt = subprocess.run(
        f"ncks -H {netcdf_file}  1> /dev/null 2>&1", shell=True
    )
    if chk_corrupt.returncode != 0:
        print(f"WARNING: {netcdf_file} is corrupt")
        file_is_corrupt = True
    else:
        file_is_corrupt = False
    return file_is_corrupt


def get_time_info(date_start, date_end, plot_by, init_hr_list, valid_hr_list,
                  fhr_list):
    """! Creates a list of dictionaries containing information
         on the valid dates and times, the initialization dates
         and times, and forecast hour pairings

         Args:
             date_start     - verification start date
                              (string, format:YYYYmmdd)
             date_end       - verification end_date
                              (string, format:YYYYmmdd)
             plot_by        - how to treat date_start and
                              date_end (string, values:VALID or INIT)
             init_hr_list   - list of initialization hours
                              (string)
             valid_hr_list  - list of valid hours (string)
             fhr_list       - list of forecasts hours (string)

         Returns:
             time_info - list of dictionaries with the valid,
                         initialization, and forecast hour
                         pairings
    """
    valid_hr_zfill2_list = [hr.zfill(2) for hr in valid_hr_list]
    init_hr_zfill2_list = [hr.zfill(2) for hr in init_hr_list]
    if plot_by == 'VALID':
        plot_by_hr_list = valid_hr_zfill2_list
    elif plot_by == 'INIT':
        plot_by_hr_list = init_hr_zfill2_list
    plot_by_hr_start = plot_by_hr_list[0]
    plot_by_hr_end = plot_by_hr_list[-1]
    if len(plot_by_hr_list) > 1:
        plot_by_hr_inc = np.min(
            np.diff(np.array(plot_by_hr_list, dtype=int))
        )
    else:
        plot_by_hr_inc = 24
    date_start_dt = datetime.datetime.strptime(date_start+plot_by_hr_start,
                                               '%Y%m%d%H')
    date_end_dt = datetime.datetime.strptime(date_end+plot_by_hr_end,
                                             '%Y%m%d%H')
    time_info = []
    date_dt = date_start_dt
    while date_dt <= date_end_dt:
        if plot_by == 'VALID':
            valid_time_dt = date_dt
        elif plot_by == 'INIT':
            init_time_dt = date_dt
        for fhr in fhr_list:
            if fhr == 'anl':
                forecast_hour = 0
            else:
                forecast_hour = int(fhr)
            if plot_by == 'VALID':
                init_time_dt = (valid_time_dt
                                - datetime.timedelta(hours=forecast_hour))
            elif plot_by == 'INIT':
                valid_time_dt = (init_time_dt
                                 + datetime.timedelta(hours=forecast_hour))
            if valid_time_dt.strftime('%H') in valid_hr_zfill2_list \
                    and init_time_dt.strftime('%H') in init_hr_zfill2_list:
                t = {}
                t['valid_time'] = valid_time_dt
                t['init_time'] = init_time_dt
                t['forecast_hour'] = str(forecast_hour)
                time_info.append(t)
        date_dt = date_dt + datetime.timedelta(hours=int(plot_by_hr_inc))
    return time_info

def get_init_hour(valid_hour, forecast_hour):
    """! Get a initialization hour

         Args:
             valid_hour    - valid hour (integer)
             forecast_hour - forecast hour (integer)
    """
    init_hour = 24 + (valid_hour - (forecast_hour%24))
    if forecast_hour % 24 == 0:
        init_hour = valid_hour
    else:
        init_hour = 24 + (valid_hour - (forecast_hour%24))
    if init_hour >= 24:
        init_hour = init_hour - 24
    return init_hour

def get_valid_hour(init_hour, forecast_hour):
    """! Get a valid hour

         Args:
             init_hour    - init hour (integer)
             forecast_hour - forecast hour (integer)
    """
    valid_hour = (init_hour + (forecast_hour%24))
    if forecast_hour % 24 == 0:
        valid_hour = init_hour
    else:
        valid_hour = (init_hour + (forecast_hour%24))
    if valid_hour >= 24:
        valid_hour = valid_hour - 24
    return valid_hour


def format_filler(unfilled_file_format, valid_time_dt, init_time_dt,
                  forecast_hour, str_sub_dict):
    """! Creates a filled file path from a format

         Args:
             unfilled_file_format - file naming convention (string)
             valid_time_dt        - valid time (datetime)
             init_time_dt         - initialization time (datetime)
             forecast_hour        - forecast hour (string)
             str_sub_dict         - other strings to substitue (dictionary)
         Returns:
             filled_file_format - file_format filled in with verifying
                                  time information (string)
    """
    filled_file_format = '/'
    format_opt_list = ['lead', 'lead_shift', 'valid', 'valid_shift',
                       'init', 'init_shift']
    if len(list(str_sub_dict.keys())) != 0:
        format_opt_list = format_opt_list+list(str_sub_dict.keys())
    for filled_file_format_chunk in unfilled_file_format.split('/'):
        for format_opt in format_opt_list:
            nformat_opt = (
                filled_file_format_chunk.count('{'+format_opt+'?fmt=')
            )
            if nformat_opt > 0:
               format_opt_count = 1
               while format_opt_count <= nformat_opt:
                   if format_opt in ['lead_shift', 'valid_shift',
                                     'init_shift']:
                       shift = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0].partition('shift=')[2]
                       )
                       format_opt_count_fmt = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0].partition('?')[0]
                       )
                   else:
                       format_opt_count_fmt = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0]
                       )
                   if format_opt == 'valid':
                       replace_format_opt_count = valid_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'lead':
                       if format_opt_count_fmt == '%1H':
                           if int(forecast_hour) < 10:
                               replace_format_opt_count = forecast_hour[1]
                           else:
                               replace_format_opt_count = forecast_hour
                       elif format_opt_count_fmt == '%2H':
                           replace_format_opt_count = forecast_hour.zfill(2)
                       elif format_opt_count_fmt == '%3H':
                           replace_format_opt_count = forecast_hour.zfill(3)
                       else:
                           replace_format_opt_count = forecast_hour
                   elif format_opt == 'init':
                       replace_format_opt_count = init_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'lead_shift':
                       shift = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0].partition('shift=')[2]
                       )
                       forecast_hour_shift = str(int(forecast_hour)
                                                 + int(shift))
                       if format_opt_count_fmt == '%1H':
                           if int(forecast_hour_shift) < 10:
                               replace_format_opt_count = (
                                   forecast_hour_shift[1]
                               )
                           else:
                               replace_format_opt_count = forecast_hour_shift
                       elif format_opt_count_fmt == '%2H':
                           replace_format_opt_count = (
                               forecast_hour_shift.zfill(2)
                           )
                       elif format_opt_count_fmt == '%3H':
                           replace_format_opt_count = (
                               forecast_hour_shift.zfill(3)
                           )
                       else:
                           replace_format_opt_count = forecast_hour_shift
                   elif format_opt == 'init_shift':
                       shift = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0].partition('shift=')[2]
                       )
                       init_shift_time_dt = (
                           init_time_dt + datetime.timedelta(hours=int(shift))
                       )
                       replace_format_opt_count = init_shift_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'valid_shift':
                       shift = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0].partition('shift=')[2]
                       )
                       valid_shift_time_dt = (
                           valid_time_dt + datetime.timedelta(hours=int(shift))
                       )
                       replace_format_opt_count = valid_shift_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   else:
                       replace_format_opt_count = str_sub_dict[format_opt]
                   if format_opt in ['lead_shift', 'valid_shift', 'init_shift']:
                       filled_file_format_chunk = (
                           filled_file_format_chunk.replace(
                               '{'+format_opt+'?fmt='
                               +format_opt_count_fmt
                               +'?shift='+shift+'}',
                               replace_format_opt_count
                           )
                       )
                   else:
                       filled_file_format_chunk = (
                           filled_file_format_chunk.replace(
                               '{'+format_opt+'?fmt='
                               +format_opt_count_fmt+'}',
                               replace_format_opt_count
                           )
                       )
                   format_opt_count+=1
        filled_file_format = os.path.join(filled_file_format,
                                          filled_file_format_chunk)
    return filled_file_format

def get_obs_valid_hrs(obs):
    """! This returns the valid hour start, end, and increment
         information for a given observation

         Args:
             obs - observation name (string)

         Returns:
             valid_hr_start - starting valid hour (integer)
             valid_hr_end   - ending valid hour (integer)
             valid_hr_inc   - valid hour increment (integer)
    """
    obs_valid_hr_dict = {
        '24hrCCPA': {'valid_hr_start': 12,
                     'valid_hr_end': 12,
                     'valid_hr_inc': 24},
        '3hrCCPA': {'valid_hr_start': 0,
                    'valid_hr_end': 21,
                    'valid_hr_inc': 3},
        '24hrNOHRSC': {'valid_hr_start': 12,
                       'valid_hr_end': 12,
                       'valid_hr_inc': 24},
        'OSI-SAF': {'valid_hr_start': 00,
                    'valid_hr_end': 00,
                    'valid_hr_inc': 24},
        'GHRSST-OSPO': {'valid_hr_start': 00,
                        'valid_hr_end': 00,
                        'valid_hr_inc': 24},
    }
    if obs in list(obs_valid_hr_dict.keys()):
        valid_hr_start = obs_valid_hr_dict[obs]['valid_hr_start']
        valid_hr_end = obs_valid_hr_dict[obs]['valid_hr_end']
        valid_hr_inc = obs_valid_hr_dict[obs]['valid_hr_inc']
    else:
        print(f"FATAL ERROR: Cannot get {obs} valid hour information")
        sys.exit(1)
    return valid_hr_start, valid_hr_end, valid_hr_inc

def get_off_machine_data(job_file, job_name, job_output, machine, user, queue,
                         account):
    """! This submits a job to the transfer queue
         to get data that does not reside on current machine
         Args:
             job_file   - path to job submission file (string)
             job_name   - job submission name (string)
             job_output - path to write job output (string)
             machine    - machine name (string)
             user       - user name (string)
             queue      - submission queue name (string)
             account    - submission account name (string)
         Returns:
    """
    # Set up job wall time information
    walltime = '60'
    walltime_seconds = (
        datetime.timedelta(minutes=int(walltime)).total_seconds()
    )
    walltime = (datetime.datetime.min
                + datetime.timedelta(minutes=int(walltime))).time()
    # Submit job
    print(f"Submitting {job_file} to {queue}")
    print(f"Output sent to {job_output}")
    os.chmod(job_file, 0o755)
    if machine == 'WCOSS2':
        job_submit_cmd = (
            f"qsub -V -l walltime={walltime:%H:%M:%S} -q {queue} -A {account} "
            +f"-o {job_output} -e {job_output} -N {job_name} "
            +f"-l select=1:ncpus=1 {job_file}"
        )
        job_check_cmd = (
            f"qselect -s QR -u {user} -N {job_name} | wc -l"
        )
    elif machine in ['HERA', 'ORION', 'GAEAC6']:
        job_submit_cmd = (
            f"sbatch --ntasks=1 --time={walltime:%H:%M:%S} "
            +f"--partition={queue} --account={account} --output={job_output} "
            +f"--job-name={job_name} {job_file}"
        )
        job_check_cmd = (
            f"squeue -u {user} -n {job_name} -t R,PD -h | wc -l"
        )
    job_submit = subprocess.run(job_submit_cmd, shell=True)
    sleep_counter, sleep_checker = 1, 10
    while (sleep_counter*sleep_checker) <= walltime_seconds:
        sleep(sleep_checker)
        print(f"Walltime checker: {str(sleep_counter*sleep_checker)} "
              +f"out of {str(int(walltime_seconds))} seconds")
        job_check = subprocess.run(job_check_cmd, shell=True,
                                   capture_output=True, encoding="utf8")
        if job_check.stdout[0] == '0':
            break
        sleep_counter+=1

def initialize_job_env_dict(case_type, group,
                           run_abbrev_type, job):
    """! This initializes a dictionary of environment variables and their
         values to be set for the job pulling from environment variables
         already set previously
         Args:
             case_type                   - string of the use case name
             group                       - string of the group name
             run_abbrev_type             - string of reference name in config
                                           and environment variables
             job                         - string of job name
         Returns:
             job_env_dict - dictionary of job settings
    """
    job_env_var_list = [
        'machine', 'HOMEverif_global', 'FIXverif_global', 'USHverif_global', 'DATA',
        'NET', 'RUN'
    ]
    if group in ['condense_stats', 'filter_stats', 'scorecard_avg_ci', 'make_plots']:
        job_env_var_list.extend(['HOMEMET', 'MET_version'])
    job_env_dict = {}
    for env_var in job_env_var_list:
        job_env_dict[env_var] = os.environ[env_var]
    if group in ['condense_stats', 'filter_stats', 'scorecard_avg_ci', 'make_plots']:
        job_env_dict['plot_verbosity'] = 'DEBUG'
    job_env_dict['CASE_TYPE'] = case_type
    job_env_dict['JOB_GROUP'] = group
    job_env_dict['job_name'] = job
    if group in ['filter_stats', 'make_plots']:
        if run_abbrev_type+'_fhr_list' in list(os.environ.keys()):
            fhr_list = (
                os.environ[run_abbrev_type+'_fhr_list'].split(' ')
            )
        else:
            fhr_range = range(
                int(os.environ[run_abbrev_type+'_fhr_min']),
                int(os.environ[run_abbrev_type+'_fhr_max'])
                +int(os.environ[run_abbrev_type+'_fhr_inc']),
                int(os.environ[run_abbrev_type+'_fhr_inc'])
            )
            fhr_list = [str(i) for i in fhr_range]
        job_env_dict['fhr_list'] = ', '.join(fhr_list)
        if case_type in ['pres', 'anom', 'sfc', 'ptype']:
            case_type_valid_hr_list = (
                os.environ[run_abbrev_type+'_valid_hr_list']\
                .split(' ')
            )
            job_env_dict['valid_hr_start'] = (
                case_type_valid_hr_list[0].zfill(2)
            )
            job_env_dict['valid_hr_end'] = (
                case_type_valid_hr_list[-1].zfill(2)
            )
            if len(case_type_valid_hr_list) > 1:
                case_type_valid_hr_inc = np.min(
                    np.diff(np.array(case_type_valid_hr_list, dtype=int))
                )
            else:
                case_type_valid_hr_inc = 24
            job_env_dict['valid_hr_inc'] = str(case_type_valid_hr_inc)
        else:
            if case_type == 'precip_accum24hr':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('24hrCCPA')
                )
            elif case_type == 'precip_accum3hr':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('3hrCCPA')
                )
            elif case_type == 'snow':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('24hrNOHRSC')
                )
            elif case_type == 'sea_ice':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('OSI-SAF')
                )
            elif case_type == 'sst':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('GHRSST-OSPO')
                )
            else:
                 valid_hr_start, valid_hr_end, valid_hr_inc = 12, 12, 23
            job_env_dict['valid_hr_start'] = str(valid_hr_start).zfill(2)
            job_env_dict['valid_hr_end'] = str(valid_hr_end).zfill(2)
            job_env_dict['valid_hr_inc'] = str(valid_hr_inc)
        case_type_init_hr_list = (
            os.environ[run_abbrev_type+'_init_hr_list']\
            .split(' ')
        )
        job_env_dict['init_hr_start'] = (
            case_type_init_hr_list[0].zfill(2)
        )
        job_env_dict['init_hr_end'] = (
            case_type_init_hr_list[-1].zfill(2)
        )
        if len(case_type_init_hr_list) > 1:
            case_type_init_hr_inc = np.min(
                np.diff(np.array(case_type_init_hr_list, dtype=int))
            )
        else:
            case_type_init_hr_inc = 24
        job_env_dict['init_hr_inc'] = str(case_type_init_hr_inc)
    return job_env_dict

def get_logger(log_file):
    """! Get logger
         Args:
             log_file - full path to log file (string)
         Returns:
             logger - logger object
    """
    log_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
        + '%(message)s',
        '%m/%d %H:%M:%S'
    )
    logger = logging.getLogger(log_file)
    logger.setLevel('DEBUG')
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    logger_info = f"Log file: {log_file}"
    print(logger_info)
    logger.info(logger_info)
    return logger

def get_plot_dates(logger, plot_by, start_date, end_date,
                   valid_hr_start, valid_hr_end, valid_hr_inc,
                   init_hr_start, init_hr_end, init_hr_inc,
                   forecast_hour):
    """! This builds the dates to include in plotting based on user
         configurations
         Args:
             logger         - logger object
             plot_by        - type of date to plot (string: VALID or INIT)
             start_date     - plotting start date (string, format: YYYYmmdd)
             end_date       - plotting end date (string, format: YYYYmmdd)
             valid_hr_start - starting valid hour (string)
             valid_hr_end   - ending valid hour (string)
             valid_hr_inc   - valid hour increment (string)
             init_hr_start  - starting initialization hour (string)
             init_hr_end    - ending initialization hour (string)
             init_hr_inc    - initialization hour incrrement (string)
             forecast_hour  - forecast hour (string)
         Returns:
             valid_dates - array of valid dates (datetime)
             init_dates  - array of initialization dates (datetime)
    """
    # Build date_type date array
    if plot_by == 'VALID':
        start_date_dt = datetime.datetime.strptime(start_date+valid_hr_start,
                                                   '%Y%m%d%H')
        end_date_dt = datetime.datetime.strptime(end_date+valid_hr_end,
                                                 '%Y%m%d%H')
        dt_inc = datetime.timedelta(hours=int(valid_hr_inc))
    elif plot_by == 'INIT':
        start_date_dt = datetime.datetime.strptime(start_date+init_hr_start,
                                                   '%Y%m%d%H')
        end_date_dt = datetime.datetime.strptime(end_date+init_hr_end,
                                                 '%Y%m%d%H')
        dt_inc = datetime.timedelta(hours=int(init_hr_inc))
    plot_by_dates = (np.arange(start_date_dt, end_date_dt+dt_inc, dt_inc)\
                       .astype(datetime.datetime))
    # Build valid and init date arrays
    if plot_by == 'VALID':
        valid_dates = plot_by_dates
        init_dates = (valid_dates
                      - datetime.timedelta(hours=(int(forecast_hour))))
    elif plot_by == 'INIT':
        init_dates = plot_by_dates
        valid_dates = (init_dates
                      + datetime.timedelta(hours=(int(forecast_hour))))
    # Check if unrequested hours exist in arrays, and remove
    valid_remove_idx_list = []
    valid_hr_list = [
        str(hr).zfill(2) for hr in range(int(valid_hr_start),
                                         int(valid_hr_end)+int(valid_hr_inc),
                                         int(valid_hr_inc))
    ]
    for d in range(len(valid_dates)):
        if valid_dates[d].strftime('%H') \
                not in valid_hr_list:
            valid_remove_idx_list.append(d)
    valid_dates = np.delete(valid_dates, valid_remove_idx_list)
    init_dates = np.delete(init_dates, valid_remove_idx_list)
    init_remove_idx_list = []
    init_hr_list = [
        str(hr).zfill(2) for hr in range(int(init_hr_start),
                                         int(init_hr_end)+int(init_hr_inc),
                                         int(init_hr_inc))
    ]
    for d in range(len(init_dates)):
        if init_dates[d].strftime('%H') \
                not in init_hr_list:
            init_remove_idx_list.append(d)
    valid_dates = np.delete(valid_dates, init_remove_idx_list)
    init_dates = np.delete(init_dates, init_remove_idx_list)
    return valid_dates, init_dates

def get_met_line_type_cols(logger, met_root, met_version, met_line_type):
    """! Get the MET columns for a specific line type and MET
         version

         Args:
             logger        - logger object
             met_root      - path to MET (string)
             met_version   - MET version number (string)
             met_line_type - MET line type (string)
         Returns:
             met_version_line_type_col_list - list of MET version
                                              line type columns (strings)
    """
    if met_version.count('.') == 2:
        met_minor_version = met_version.rpartition('.')[0]
    elif met_version.count('.') == 1:
        met_minor_version = met_version
    met_minor_version_col_file = os.path.join(
        met_root, 'share', 'met', 'table_files',
        'met_header_columns_V'+met_minor_version+'.txt'
    )
    if os.path.exists(met_minor_version_col_file):
        with open(met_minor_version_col_file) as f:
            for line in f:
                if met_line_type in line:
                    line_type_cols = line.split(' : ')[-1]
                    break
    else:
        logger.error(f"{met_minor_version_col_file} does not exist, "
                     +"cannot determine MET data column structure")
        sys.exit(1)
    met_version_line_type_col_list = (
        line_type_cols.replace('\n', '').split(' ')
    )
    return met_version_line_type_col_list

def format_thresh(thresh):
   """! Format threshold with letter and symbol options

      Args:
         thresh         - the threshold (string)

      Return:
         thresh_symbol  - threshold with symbols (string)
         thresh_letters - treshold with letters (string)
   """
   thresh_symbol = (
       thresh.replace('ge', '>=').replace('gt', '>')\
       .replace('eq', '==').replace('ne', '!=')\
       .replace('le', '<=').replace('lt', '<')
   )
   thresh_letter = (
       thresh.replace('>=', 'ge').replace('>', 'gt')\
       .replace('==', 'eq').replace('!=', 'ne')\
       .replace('<=', 'le').replace('<', 'lt')
   )
   return thresh_symbol, thresh_letter

def get_plot_job_dirs(DATA_base_dir, COMOUT_base_dir, job_group,
                      plot_job_env_dict):
    """! Get directories for the plotting job
         Args:
             DATA_base_dir     - path to DATA directory
                                 (string)
             COMOUT_base_dir   - path to COMOUT directory
                                 (string)
             job_group         - plotting job group:
                                 condense_stats, filter_stats,
                                 make_plots (string)
             plot_job_env_dict - dictionary with plotting job
                                 environment variables to be
                                 set

         Returns:
             job_work_dir    - path to plotting job's
                               working directory
             job_DATA_dir    - path to plotting job's
                               DATA directory
             job_COMOUT_dir  - path to plotting job's
                               COMOUT directory
    """
    region_savefig_dict = {
        'Alaska': 'alaska',
        'alaska': 'alaska',
        'Appalachia': 'buk_apl',
        'ANTARCTIC': 'antarctic',
        'ARCTIC': 'arctic',
        'ATL_MDR': 'al_mdr',
        'conus': 'conus',
        'CONUS': 'buk_conus',
        'CONUS_East': 'buk_conus_e',
        'CONUS_Central': 'buk_conus_c',
        'CONUS_South': 'buk_conus_s',
        'CONUS_West': 'buk_conus_w',
        'CPlains': 'buk_cpl',
        'DeepSouth': 'buk_ds',
        'EPAC_MDR': 'ep_mdr',
        'GLOBAL': 'glb',
        'GreatBasin': 'buk_grb',
        'GreatLakes': 'buk_grlk',
        'hawaii': 'hawaii',
        'Mezqutial': 'buk_mez',
        'MidAtlantic': 'buk_matl',
        'N60N90': 'n60',
        'NAO': 'nao',
        'NHEM': 'nhem',
        'NorthAtlantic': 'buk_ne',
        'NPlains': 'buk_npl',
        'NPO': 'npo',
        'NRockies': 'buk_nrk',
        'PacificNW': 'buk_npw',
        'PacificSW': 'buk_psw',
        'Prairie': 'buk_pra',
        'prico': 'prico',
        'S60S90': 's60',
        'SAO': 'sao',
        'SHEM': 'shem',
        'Southeast': 'buk_se',
        'Southwest': 'buk_sw',
        'SPlains': 'buk_spl',
        'SPO': 'spo',
        'SRockies': 'buk_srk',
        'TROPICS': 'tropics'
    }
    dir_step = plot_job_env_dict['STEP'].lower()
    dir_verif_case = plot_job_env_dict['VERIF_CASE'].lower()
    dir_verif_type = plot_job_env_dict['VERIF_TYPE'].lower()
    dir_ndays = ('last'+plot_job_env_dict['NDAYS']+'days').lower()
    dir_line_type = plot_job_env_dict['line_type'].lower()
    dir_parameter = plot_job_env_dict['fcst_var_name'].lower()
    if job_group == 'make_plots':
        if plot_job_env_dict['plot'] in ['stat_by_level', 'lead_by_level']:
            dir_level = plot_job_env_dict['vert_profile'].lower()
        else:
            dir_level = (plot_job_env_dict['fcst_var_level_list'].lower()\
                         .replace('.','p').replace('-', '_'))
    else:
        dir_level = (plot_job_env_dict['fcst_var_level'].lower()\
                     .replace('.','p').replace('-', '_'))
    if plot_job_env_dict['fcst_var_name'] == 'CAPE':
        dir_level = dir_level.replace('z0', 'l0').replace('p90_0', 'l90')
    dir_region = region_savefig_dict[plot_job_env_dict['vx_mask']]
    if job_group in ['condense_stats', 'filter_stats']:
        job_work_dir = os.path.join(
            DATA_base_dir, f"{dir_verif_case}_{dir_step}", 'plot_output',
            'job_work_dir', job_group, f"{plot_job_env_dict['job_id']}",
            f"{plot_job_env_dict['RUN']}.{plot_job_env_dict['end_date']}",
            f"{dir_verif_case}_{dir_verif_type}",
            dir_ndays, dir_line_type,
            f"{dir_parameter}_{dir_level}",
            dir_region
        )
    elif job_group == 'make_plots':
        dir_stat = plot_job_env_dict['stat'].lower()
        job_work_dir = os.path.join(
            DATA_base_dir, f"{dir_verif_case}_{dir_step}", 'plot_output',
            'job_work_dir', job_group, f"{plot_job_env_dict['job_id']}",
            f"{plot_job_env_dict['RUN']}.{plot_job_env_dict['end_date']}",
            f"{dir_verif_case}_{dir_verif_type}",
            dir_ndays, dir_line_type,
            f"{dir_parameter}_{dir_level}",
            dir_region, dir_stat
        )
    job_COMOUT_dir = job_work_dir.replace(
        os.path.join(DATA_base_dir,
                     f"{dir_verif_case}_{dir_step}",
                     'plot_output', 'job_work_dir', job_group,
                     f"{plot_job_env_dict['job_id']}",
                     f"{plot_job_env_dict['RUN']}."
                     +f"{plot_job_env_dict['end_date']}"),
        COMOUT_base_dir
    )
    job_DATA_dir = job_COMOUT_dir.replace(
        COMOUT_base_dir,
        os.path.join(DATA_base_dir, f"{dir_verif_case}_{dir_step}",
                     'plot_output', f"{plot_job_env_dict['RUN']}."
                     +f"{plot_job_env_dict['end_date']}")
    )
    return job_work_dir, job_DATA_dir, job_COMOUT_dir

def get_daily_stat_file(model_name, source_stats_base_dir,
                        dest_model_name_stats_dir,
                        verif_case, start_date_dt, end_date_dt):
    """! Link model daily stat files
         Args:
             model_name                - name of model (string)
             source_stats_base_dir     - full path to stats/global_det
                                         source directory (string)
             dest_model_name_stats_dir - full path to model
                                         destintion directory (string)
             verif_case                - grid2grid or grid2obs (string)
             start_date_dt             - month start date (datetime obj)
             end_date_dt               - month end date (datetime obj)
         Returns:
    """
    date_dt = start_date_dt
    while date_dt <= end_date_dt:
        source_model_date_stat_file = os.path.join(
            source_stats_base_dir,
            model_name+'.'+date_dt.strftime('%Y%m%d'),
            'evs.stats.'+model_name+'.atmos.'+verif_case+'.'
            +'v'+date_dt.strftime('%Y%m%d')+'.stat'
        )
        dest_model_date_stat_file = os.path.join(
            dest_model_name_stats_dir,
            model_name+'_atmos_'+verif_case+'_v'
            +date_dt.strftime('%Y%m%d')+'.stat'
        )
        if not os.path.exists(dest_model_date_stat_file):
            if check_file_exists_size(source_model_date_stat_file):
                print(f"Linking {source_model_date_stat_file} to "
                      +f"{dest_model_date_stat_file}")
                os.symlink(source_model_date_stat_file,
                           dest_model_date_stat_file)
        date_dt = date_dt + datetime.timedelta(days=1)

def condense_model_stat_files(logger, input_dir, output_dir, model, obs,
                              vx_mask, fcst_var_name, fcst_var_level,
                              obs_var_name, obs_var_level, line_type):
    """! Condense the individual date model stat file and
         thin out unneeded data

         Args:
             logger         - logger object
             input_dir      - path to input directory (string)
             output_dir     - path to output directory (string)
             model          - model name (string)
             obs            - observation name (string)
             vx_mask        - verification masking region (string)
             fcst_var_name  - forecast variable name (string)
             fcst_var_level - forecast variable level (string)
             obs_var_name   - observation variable name (string)
             obs_var_leve   - observation variable level (string)
             line_type      - MET line type (string)

         Returns:
    """
    model_stat_files_wildcard = os.path.join(input_dir, model+'_*.stat')
    model_stat_files = glob.glob(model_stat_files_wildcard, recursive=True)
    make_dir(output_dir)
    output_file = os.path.join(
        output_dir, f"condensed_stats_{model.lower()}_{line_type.lower()}_"
        +f"{fcst_var_name.lower()}_"
        +f"{fcst_var_level.lower().replace('.','p').replace('-', '_')}_"
        +f"{vx_mask.lower()}.stat"
    )
    if len(model_stat_files) == 0:
        logger.debug(f"No stat files matching "
                     +f"{model_stat_files_wildcard}")
    else:
        if not os.path.exists(output_file):
            logger.info(f"Condensing down stat files matching "
                        +f"{model_stat_files_wildcard}")
            with open(model_stat_files[0]) as msf:
                met_header_cols = msf.readline()
            additional_grep_list = [obs, vx_mask, fcst_var_name,
                                    fcst_var_level, obs_var_name,
                                    line_type]
            additional_grep = ''
            for item in additional_grep_list:
                additional_grep = (additional_grep
                                   +f' | grep "{item} "')
            all_grep_output = ''
            for model_stat_file in model_stat_files:
                logger.info(f"Grep'ing {model_stat_file} for "
                            +f"{model}, {', '.join(additional_grep_list)}")
                grep = subprocess.run(
                    'grep -R "'+model+' " '+model_stat_file+additional_grep,
                    shell=True, capture_output=True, encoding="utf8"
                )
                logger.debug(f"Ran {grep.args}")
                all_grep_output = all_grep_output+grep.stdout
            logger.info(f"Condensed {model} stat files at "
                        +f"{output_file}")
            with open(output_file, 'w') as f:
                f.write(met_header_cols+all_grep_output)
        else:
            logger.info(f"{output_file} exists")

def build_df(job_group, logger, input_dir, output_dir, model_info_dict,
             met_info_dict, fcst_var_name, fcst_var_level, fcst_var_thresh,
             obs_var_name, obs_var_level, obs_var_thresh, line_type,
             grid, vx_mask, interp_method, interp_points, plot_by, dates,
             met_format_valid_dates, fhr):
    """! Build the data frame for all model stats,
         Read the model's filtered file, and if it doesn't exist
         filter the model file for needed information and write file

         Args:
             job_group              - either filter_stats or make_plots
                                      (string)
             logger                 - logger object
             input_dir              - path to input directory (string)
             output_dir             - path to output directory (string)
             model_info_dict        - model infomation dictionary (strings)
             met_info_dict          - MET information dictionary (strings)
             fcst_var_name          - forecast variable name (string)
             fcst_var_level         - forecast variable level (string)
             fcst_var_tresh         - forecast variable treshold (string)
             obs_var_name           - observation variable name (string)
             obs_var_level          - observation variable level (string)
             obs_var_tresh          - observation variable treshold (string)
             line_type              - MET line type (string)
             grid                   - verification grid (string)
             vx_mask                - verification masking region (string)
             interp_method          - interpolation method (string)
             interp_points          - interpolation points (string)
             plot_by                - type of date (string, VALID or INIT)
             dates                  - array of dates (datetime)
             met_format_valid_dates - list of valid dates formatted
                                      like they are in MET stat files
             fhr                    - forecast hour (string)

         Returns:
             all_model_df                - dataframe of all the information
    """
    met_version_line_type_col_list = get_met_line_type_cols(
        logger, met_info_dict['root'], met_info_dict['version'], line_type
    )
    for model_num in list(model_info_dict.keys()):
        model_num_name = (
            model_num+'/'+model_info_dict[model_num]['name']
            +'/'+model_info_dict[model_num]['plot_name']
        )
        model_num_df_index = pd.MultiIndex.from_product(
            [[model_num_name], met_format_valid_dates],
            names=['model', 'valid_dates']
        )
        model_dict = model_info_dict[model_num]
        condensed_model_file = os.path.join(
            input_dir, 'condensed_stats_'
            +f"{model_info_dict[model_num]['name'].lower()}_"
            +f"{line_type.lower()}_"
            +f"{fcst_var_name.lower()}_"
            +f"{fcst_var_level.lower().replace('.','p').replace('-', '_')}_"
            +f"{vx_mask.lower()}.stat"
        )
        if len(dates) != 0:
            filtered_model_stat_file_name = (
                'fcst'+model_dict['name']+'_'
                +fcst_var_name+fcst_var_level+fcst_var_thresh+'_'
                +'obs'+model_dict['obs_name']+'_'
                +obs_var_name+obs_var_level+obs_var_thresh+'_'
                +'linetype'+line_type+'_'
                +'grid'+grid+'_'+'vxmask'+vx_mask+'_'
                +'interp'+interp_method+interp_points+'_'
                +plot_by.lower()
                +dates[0].strftime('%Y%m%d%H%M%S')+'to'
                +dates[-1].strftime('%Y%m%d%H%M%S')+'_'
                +'fhr'+fhr.zfill(3)
            ).lower().replace('.','p').replace('-', '_')\
            .replace('&&', 'and').replace('||', 'or')\
            .replace('0,*,*', '').replace('*,*', '')+'.stat'
            input_filtered_model_stat_file = os.path.join(
                input_dir, filtered_model_stat_file_name
            )
            output_filtered_model_stat_file = os.path.join(
                output_dir, filtered_model_stat_file_name
            )
            if os.path.exists(input_filtered_model_stat_file):
                filtered_model_stat_file = input_filtered_model_stat_file
            else:
                filtered_model_stat_file = output_filtered_model_stat_file
            if not os.path.exists(filtered_model_stat_file):
                write_filtered_stat_file = True
                read_filtered_stat_file = True
            else:
                write_filtered_stat_file = False
                read_filtered_stat_file = True
            if job_group == 'filter_stats':
                read_filtered_stat_file = False
        else:
            write_filtered_stat_file = False
            read_filtered_stat_file = False
        if os.path.exists(condensed_model_file) and line_type == 'MCTC':
            tmp_df = pd.read_csv(
                condensed_model_file, sep=" ", skiprows=1,
                skipinitialspace=True,
                keep_default_na=False, dtype='str', header=None
            )
            if len(tmp_df) > 0:
                ncat = int(tmp_df[25][0])
                new_met_version_line_type_col_list = []
                for col in met_version_line_type_col_list:
                    if col == '(N_CAT)':
                        new_met_version_line_type_col_list.append('N_CAT')
                    elif col == 'F[0-9]*_O[0-9]*':
                        fcount = 1
                        ocount = 1
                        totcount = 1
                        while totcount <= ncat*ncat:
                            new_met_version_line_type_col_list.append(
                                'F'+str(fcount)+'_'+'O'+str(ocount)
                            )
                            if ocount < ncat:
                                ocount+=1
                            elif ocount == ncat:
                                ocount = 1
                                fcount+=1
                            totcount+=1
                    else:
                        new_met_version_line_type_col_list.append(col)
                met_version_line_type_col_list = (
                    new_met_version_line_type_col_list
                )
        if write_filtered_stat_file:
            if fcst_var_thresh != 'NA':
                fcst_var_thresh_symbol, fcst_var_thresh_letter = (
                    format_thresh(fcst_var_thresh)
                )
            else:
                fcst_var_thresh_symbol = fcst_var_thresh
                fcst_vat_thresh_letter = fcst_var_thresh
            if obs_var_thresh != 'NA':
                obs_var_thresh_symbol, obs_var_thresh_letter = (
                    format_thresh(obs_var_thresh)
                )
            else:
                obs_var_thresh_symbol = obs_var_thresh
                obs_vat_thresh_letter = obs_var_thresh
            if os.path.exists(condensed_model_file):
                condensed_model_df = pd.read_csv(
                    condensed_model_file, sep=" ", skiprows=1,
                    skipinitialspace=True, names=met_version_line_type_col_list,
                    keep_default_na=False, dtype='str', header=None
                )
                filtered_model_df = condensed_model_df[
                    (condensed_model_df['MODEL'] == model_dict['name'])
                     & (condensed_model_df['DESC'] == 'on_'+grid)
                     & (condensed_model_df['FCST_LEAD'] \
                        == fhr.zfill(2)+'0000')
                     & (condensed_model_df['FCST_VAR'] \
                        == fcst_var_name)
                     & (condensed_model_df['FCST_LEV'] \
                        == fcst_var_level)
                     & (condensed_model_df['OBS_VAR'] \
                        == obs_var_name)
                     & (condensed_model_df['OBS_LEV'] \
                        == obs_var_level)
                     & (condensed_model_df['OBTYPE'] == model_dict['obs_name'])
                     & (condensed_model_df['VX_MASK'] \
                        == vx_mask)
                     & (condensed_model_df['INTERP_MTHD'] \
                        == interp_method)
                     & (condensed_model_df['INTERP_PNTS'] \
                        == interp_points)
                     & (condensed_model_df['FCST_THRESH'] \
                        == fcst_var_thresh_symbol)
                     & (condensed_model_df['OBS_THRESH'] \
                        == obs_var_thresh_symbol)
                     & (condensed_model_df['LINE_TYPE'] \
                        == line_type)
                ]
                filtered_model_df = filtered_model_df[
                    filtered_model_df['FCST_VALID_BEG'].isin(met_format_valid_dates)
                ]
                filtered_model_df['FCST_VALID_BEG'] = pd.to_datetime(
                    filtered_model_df['FCST_VALID_BEG'], format='%Y%m%d_%H%M%S'
                )
                filtered_model_df = filtered_model_df.sort_values(by='FCST_VALID_BEG')
                filtered_model_df['FCST_VALID_BEG'] = (
                    filtered_model_df['FCST_VALID_BEG'].dt.strftime('%Y%m%d_%H%M%S')
                )
                filtered_model_df.to_csv(
                    filtered_model_stat_file, header=met_version_line_type_col_list,
                    index=None, sep=' ', mode='w'
                )
            else:
                logger.debug(f"{condensed_model_file} does not exist")
            if os.path.exists(filtered_model_stat_file):
                logger.info(f"Filtered {model_dict['name']} file "
                            +f"at {filtered_model_stat_file}")
            else:
                logger.debug(f"Could not create {filtered_model_stat_file}")
        model_num_df = pd.DataFrame(np.nan, index=model_num_df_index,
                                    columns=met_version_line_type_col_list)
        if read_filtered_stat_file:
            if os.path.exists(filtered_model_stat_file):
                logger.info(f"Reading {filtered_model_stat_file} for "
                            +f"{model_dict['name']}")
                model_stat_file_df = pd.read_csv(
                    filtered_model_stat_file, sep=" ", skiprows=1,
                    skipinitialspace=True, names=met_version_line_type_col_list,
                    na_values=['NA'], header=None
                )
                df_dtype_dict = {}
                float_idx = met_version_line_type_col_list.index('TOTAL')
                for col in met_version_line_type_col_list:
                    col_idx = met_version_line_type_col_list.index(col)
                    if col_idx < float_idx:
                        df_dtype_dict[col] = str
                    else:
                        df_dtype_dict[col] = np.float64
                model_stat_file_df = model_stat_file_df.astype(df_dtype_dict)
                for valid_date in met_format_valid_dates:
                    model_stat_file_df_valid_date_idx_list = (
                        model_stat_file_df.index[
                            model_stat_file_df['FCST_VALID_BEG'] == valid_date
                        ]
                    ).tolist()
                    if len(model_stat_file_df_valid_date_idx_list) == 0:
                        continue
                    model_num_df.loc[(model_num_name, valid_date)] = (
                        model_stat_file_df.loc\
                        [model_stat_file_df_valid_date_idx_list[0]]\
                        [:]
                    )
            else:
                logger.debug(f"{filtered_model_stat_file} does not exist")
        if model_num == 'model1':
            all_model_df = model_num_df
        else:
            all_model_df = pd.concat([all_model_df, model_num_df])
    return all_model_df

def calculate_stat(logger, data_df, line_type, stat):
   """! Calculate the statistic from the data from the
        read in MET .stat file(s)
        Args:
           data_df        - dataframe containing the model(s)
                            information from the MET .stat
                            files
           line_type      - MET line type (string)
           stat           - statistic to calculate (string)

        Returns:
           stat_df       - dataframe of the statistic
           stat_array    - array of the statistic
   """
   if line_type == 'SL1L2':
       FBAR = data_df.loc[:]['FBAR']
       OBAR = data_df.loc[:]['OBAR']
       FOBAR = data_df.loc[:]['FOBAR']
       FFBAR = data_df.loc[:]['FFBAR']
       OOBAR = data_df.loc[:]['OOBAR']
   elif line_type == 'SAL1L2':
       FABAR = data_df.loc[:]['FABAR']
       OABAR = data_df.loc[:]['OABAR']
       FOABAR = data_df.loc[:]['FOABAR']
       FFABAR = data_df.loc[:]['FFABAR']
       OOABAR = data_df.loc[:]['OOABAR']
   elif line_type == 'CNT':
       FBAR = data_df.loc[:]['FBAR']
       FBAR_NCL = data_df.loc[:]['FBAR_NCL']
       FBAR_NCU = data_df.loc[:]['FBAR_NCU']
       FBAR_BCL = data_df.loc[:]['FBAR_BCL']
       FBAR_BCU = data_df.loc[:]['FBAR_BCU']
       FSTDEV = data_df.loc[:]['FSTDEV']
       FSTDEV_NCL = data_df.loc[:]['FSTDEV_NCL']
       FSTDEV_NCU = data_df.loc[:]['FSTDEV_NCU']
       FSTDEV_BCL = data_df.loc[:]['FSTDEV_BCL']
       FSTDEV_BCU = data_df.loc[:]['FSTDEV_BCU']
       OBAR = data_df.loc[:]['OBAR']
       OBAR_NCL = data_df.loc[:]['OBAR_NCL']
       OBAR_NCU = data_df.loc[:]['OBAR_NCU']
       OBAR_BCL = data_df.loc[:]['OBAR_BCL']
       OBAR_BCU = data_df.loc[:]['OBAR_BCU']
       OSTDEV = data_df.loc[:]['OSTDEV']
       OSTDEV_NCL = data_df.loc[:]['OSTDEV_NCL']
       OSTDEV_NCU = data_df.loc[:]['OSTDEV_NCU']
       OSTDEV_BCL = data_df.loc[:]['OSTDEV_BCL']
       OSTDEV_BCU = data_df.loc[:]['OSTDEV_BCU']
       PR_CORR = data_df.loc[:]['PR_CORR']
       PR_CORR_NCL = data_df.loc[:]['PR_CORR_NCL']
       PR_CORR_NCU = data_df.loc[:]['PR_CORR_NCU']
       PR_CORR_BCL = data_df.loc[:]['PR_CORR_BCL']
       PR_CORR_BCU = data_df.loc[:]['PR_CORR_BCU']
       SP_CORR = data_df.loc[:]['SP_CORR']
       KT_CORR = data_df.loc[:]['KT_CORR']
       RANKS = data_df.loc[:]['RANKS']
       FRANKS_TIES = data_df.loc[:]['FRANKS_TIES']
       ORANKS_TIES = data_df.loc[:]['ORANKS_TIES']
       ME = data_df.loc[:]['ME']
       ME_NCL = data_df.loc[:]['ME_NCL']
       ME_NCU = data_df.loc[:]['ME_NCU']
       ME_BCL = data_df.loc[:]['ME_BCL']
       ME_BCU = data_df.loc[:]['ME_BCU']
       ESTDEV = data_df.loc[:]['ESTDEV']
       ESTDEV_NCL = data_df.loc[:]['ESTDEV_NCL']
       ESTDEV_NCU = data_df.loc[:]['ESTDEV_NCU']
       ESTDEV_BCL = data_df.loc[:]['ESTDEV_BCL']
       ESTDEV_BCU = data_df.loc[:]['ESTDEV_BCU']
       MBIAS = data_df.loc[:]['MBIAS']
       MBIAS_BCL = data_df.loc[:]['MBIAS_BCL']
       MBIAS_BCU = data_df.loc[:]['MBIAS_BCU']
       MAE = data_df.loc[:]['MAE']
       MAE_BCL = data_df.loc[:]['MAE_BCL']
       MAE_BCU = data_df.loc[:]['MAE_BCU']
       MSE = data_df.loc[:]['MSE']
       MSE_BCL = data_df.loc[:]['MSE_BCL']
       MSE_BCU = data_df.loc[:]['MSE_BCU']
       BCRMSE = data_df.loc[:]['BCRMSE']
       BCRMSE_BCL = data_df.loc[:]['BCRMSE_BCL']
       BCRMSE_BCU = data_df.loc[:]['BCRMSE_BCU']
       RMSE = data_df.loc[:]['RMSE']
       RMSE_BCL = data_df.loc[:]['RMSE_BCL']
       RMSE_BCU = data_df.loc[:]['RMSE_BCU']
       E10 = data_df.loc[:]['E10']
       E10_BCL = data_df.loc[:]['E10_BCL']
       E10_BCU = data_df.loc[:]['E10_BCU']
       E25 = data_df.loc[:]['E25']
       E25_BCL = data_df.loc[:]['E25_BCL']
       E25_BCU = data_df.loc[:]['E25_BCU']
       E50 = data_df.loc[:]['E50']
       E50_BCL = data_df.loc[:]['E50_BCL']
       E50_BCU = data_df.loc[:]['E50_BCU']
       E75 = data_df.loc[:]['E75']
       E75_BCL = data_df.loc[:]['E75_BCL']
       E75_BCU = data_df.loc[:]['E75_BCU']
       E90 = data_df.loc[:]['E90']
       E90_BCL = data_df.loc[:]['E90_BCL']
       E90_BCU = data_df.loc[:]['E90_BCU']
       IQR = data_df.loc[:]['IQR']
       IQR_BCL = data_df.loc[:]['IQR_BCL']
       IQR_BCU = data_df.loc[:]['IQR_BCU']
       MAD = data_df.loc[:]['MAD']
       MAD_BCL = data_df.loc[:]['MAD_BCL']
       MAD_BCU = data_df.loc[:]['MAD_BCU']
       ANOM_CORR_NCL = data_df.loc[:]['ANOM_CORR_NCL']
       ANOM_CORR_NCU = data_df.loc[:]['ANOM_CORR_NCU']
       ANOM_CORR_BCL = data_df.loc[:]['ANOM_CORR_BCL']
       ANOM_CORR_BCU = data_df.loc[:]['ANOM_CORR_BCU']
       ME2 = data_df.loc[:]['ME2']
       ME2_BCL = data_df.loc[:]['ME2_BCL']
       ME2_BCU = data_df.loc[:]['ME2_BCU']
       MSESS = data_df.loc[:]['MSESS']
       MSESS_BCL = data_df.loc[:]['MSESS_BCL']
       MSESS_BCU = data_df.loc[:]['MSESS_BCU']
       RMSFA = data_df.loc[:]['RMSFA']
       RMSFA_BCL = data_df.loc[:]['RMSFA_BCL']
       RMSFA_BCU = data_df.loc[:]['RMSFA_BCU']
       RMSOA = data_df.loc[:]['RMSOA']
       RMSOA_BCL = data_df.loc[:]['RMSOA_BCL']
       RMSOA_BCU = data_df.loc[:]['RMSOA_BCU']
       ANOM_CORR_UNCNTR = data_df.loc[:]['ANOM_CORR_UNCNTR']
       ANOM_CORR_UNCNTR_BCL = data_df.loc[:]['ANOM_CORR_UNCNTR_BCL']
       ANOM_CORR_UNCNTR_BCU = data_df.loc[:]['ANOM_CORR_UNCNTR_BCU']
       SI = data_df.loc[:]['SI']
       SI_BCL = data_df.loc[:]['SI_BCL']
       SI_BCU = data_df.loc[:]['SI_BCU']
   elif line_type == 'GRAD':
       FGBAR = data_df.loc[:]['FGBAR']
       OGBAR = data_df.loc[:]['OGBAR']
       MGBAR = data_df.loc[:]['MGBAR']
       EGBAR = data_df.loc[:]['EGBAR']
       S1 = data_df.loc[:]['S1']
       S1_OG = data_df.loc[:]['S1_OG']
       FGOG_RATIO = data_df.loc[:]['FGOG_RATIO']
       DX = data_df.loc[:]['DX']
       DY = data_df.loc[:]['DY']
   elif line_type == 'FHO':
       F_RATE = data_df.loc[:]['F_RATE']
       H_RATE = data_df.loc[:]['H_RATE']
       O_RATE = data_df.loc[:]['O_RATE']
   elif line_type in ['CTC', 'NBRCTC']:
       FY_OY = data_df.loc[:]['FY_OY']
       FY_ON = data_df.loc[:]['FY_ON']
       FN_OY = data_df.loc[:]['FN_OY']
       FN_ON = data_df.loc[:]['FN_ON']
       if line_type == 'CTC':
           EC_VALUE = data_df.loc[:]['EC_VALUE']
   elif line_type in ['CTS', 'NBRCTS']:
       BASER = data_df.loc[:]['BASER']
       BASER_NCL = data_df.loc[:]['BASER_NCL']
       BASER_NCU = data_df.loc[:]['BASER_NCU']
       BASER_BCL = data_df.loc[:]['BASER_BCL']
       BASER_BCU = data_df.loc[:]['BASER_BCU']
       FMEAN = data_df.loc[:]['FMEAN']
       FMEAN_NCL = data_df.loc[:]['FMEAN_NCL']
       FMEAN_NCU = data_df.loc[:]['FMEAN_NCU']
       FMEAN_BCL = data_df.loc[:]['FMEAN_BCL']
       FMEAN_BCU = data_df.loc[:]['FMEAN_BCU']
       ACC = data_df.loc[:]['ACC']
       ACC_NCL = data_df.loc[:]['ACC_NCL']
       ACC_NCU = data_df.loc[:]['ACC_NCU']
       ACC_BCL = data_df.loc[:]['ACC_BCL']
       ACC_BCU = data_df.loc[:]['ACC_BCU']
       FBIAS = data_df.loc[:]['FBIAS']
       FBIAS_BCL = data_df.loc[:]['FBIAS_BCL']
       FBIAS_BCU = data_df.loc[:]['FBIAS_BCU']
       PODY = data_df.loc[:]['PODY']
       PODY_NCL = data_df.loc[:]['PODY_NCL']
       PODY_NCU = data_df.loc[:]['PODY_NCU']
       PODY_BCL = data_df.loc[:]['PODY_BCL']
       PODY_BCU = data_df.loc[:]['PODY_BCU']
       PODN = data_df.loc[:]['PODN']
       PODN_NCL = data_df.loc[:]['PODN_NCL']
       PODN_NCU = data_df.loc[:]['PODN_NCU']
       PODN_BCL = data_df.loc[:]['PODN_BCL']
       PODN_BCU = data_df.loc[:]['PODN_BCU']
       POFD = data_df.loc[:]['POFD']
       POFD_NCL = data_df.loc[:]['POFD_NCL']
       POFD_NCU = data_df.loc[:]['POFD_NCU']
       POFD_BCL = data_df.loc[:]['POFD_BCL']
       POFD_BCU = data_df.loc[:]['POFD_BCU']
       FAR = data_df.loc[:]['FAR']
       FAR_NCL = data_df.loc[:]['FAR_NCL']
       FAR_NCU = data_df.loc[:]['FAR_NCU']
       FAR_BCL = data_df.loc[:]['FAR_BCL']
       FAR_BCU = data_df.loc[:]['FAR_BCU']
       CSI = data_df.loc[:]['CSI']
       CSI_NCL = data_df.loc[:]['CSI_NCL']
       CSI_NCU = data_df.loc[:]['CSI_NCU']
       CSI_BCL = data_df.loc[:]['CSI_BCL']
       CSI_BCU = data_df.loc[:]['CSI_BCU']
       GSS = data_df.loc[:]['GSS']
       GSS_BCL = data_df.loc[:]['GSS_BCL']
       GSS_BCU = data_df.loc[:]['GSS_BCU']
       HK = data_df.loc[:]['HK']
       HK_NCL = data_df.loc[:]['HK_NCL']
       HK_NCU = data_df.loc[:]['HK_NCU']
       HK_BCL = data_df.loc[:]['HK_BCL']
       HK_BCU = data_df.loc[:]['HK_BCU']
       HSS = data_df.loc[:]['HSS']
       HSS_BCL = data_df.loc[:]['HSS_BCL']
       HSS_BCU = data_df.loc[:]['HSS_BCU']
       ODDS = data_df.loc[:]['ODDS']
       ODDS_NCL = data_df.loc[:]['ODDS_NCL']
       ODDS_NCU = data_df.loc[:]['ODDS_NCU']
       ODDS_BCL = data_df.loc[:]['ODDS_BCL']
       ODDS_BCU = data_df.loc[:]['ODDS_BCU']
       LODDS = data_df.loc[:]['LODDS']
       LODDS_NCL = data_df.loc[:]['LODDS_NCL']
       LODDS_NCU = data_df.loc[:]['LODDS_NCU']
       LODDS_BCL = data_df.loc[:]['LODDS_BCL']
       LODDS_BCU = data_df.loc[:]['LODDS_BCU']
       ORSS = data_df.loc[:]['ORSS']
       ORSS_NCL = data_df.loc[:]['ORSS_NCL']
       ORSS_NCU = data_df.loc[:]['ORSS_NCU']
       ORSS_BCL = data_df.loc[:]['ORSS_BCL']
       ORSS_BCU = data_df.loc[:]['ORSS_BCU']
       EDS = data_df.loc[:]['EDS']
       EDS_NCL = data_df.loc[:]['EDS_NCL']
       EDS_NCU = data_df.loc[:]['EDS_NCU']
       EDS_BCL = data_df.loc[:]['EDS_BCL']
       EDS_BCU = data_df.loc[:]['EDS_BCU']
       SEDS = data_df.loc[:]['SEDS']
       SEDS_NCL = data_df.loc[:]['SEDS_NCL']
       SEDS_NCU = data_df.loc[:]['SEDS_NCU']
       SEDS_BCL = data_df.loc[:]['SEDS_BCL']
       SEDS_BCU = data_df.loc[:]['SEDS_BCU']
       EDI = data_df.loc[:]['EDI']
       EDI_NCL = data_df.loc[:]['EDI_NCL']
       EDI_NCU = data_df.loc[:]['EDI_NCU']
       EDI_BCL = data_df.loc[:]['EDI_BCL']
       EDI_BCU = data_df.loc[:]['EDI_BCU']
       SEDI = data_df.loc[:]['SEDI']
       SEDI_NCL = data_df.loc[:]['SEDI_NCL']
       SEDI_NCU = data_df.loc[:]['SEDI_NCU']
       SEDI_BCL = data_df.loc[:]['SEDI_BCL']
       SEDI_BCU = data_df.loc[:]['SEDI_BCU']
       BAGSS = data_df.loc[:]['BAGSS']
       BAGSS_BCL = data_df.loc[:]['BAGSS_BCL']
       BAGSS_BCU = data_df.loc[:]['BAGSS_BCU']
       if line_type == 'CTS':
           EC_VALUE = data_df.loc[:]['EC_VALUE']
   elif line_type == 'MCTC':
       F1_O1 = data_df.loc[:]['F1_O1']
   elif line_type == 'NBRCNT':
       FBS = data_df.loc[:]['FBS']
       FBS_BCL = data_df.loc[:]['FBS_BCL']
       FBS_BCU = data_df.loc[:]['FBS_BCU']
       FSS = data_df.loc[:]['FSS']
       FSS_BCL = data_df.loc[:]['FSS_BCL']
       FSS_BCU = data_df.loc[:]['FSS_BCU']
       AFSS = data_df.loc[:]['AFSS']
       AFSS_BCL = data_df.loc[:]['AFSS_BCL']
       AFSS_BCU = data_df.loc[:]['AFSS_BCU']
       UFSS = data_df.loc[:]['UFSS']
       UFSS_BCL = data_df.loc[:]['UFSS_BCL']
       UFSS_BCU = data_df.loc[:]['UFSS_BCU']
       F_RATE = data_df.loc[:]['F_RATE']
       F_RATE_BCL = data_df.loc[:]['F_RATE_BCL']
       F_RATE_BCU = data_df.loc[:]['F_RATE_BCU']
       O_RATE = data_df.loc[:]['O_RATE']
       O_RATE_BCL = data_df.loc[:]['O_RATE_BCL']
       O_RATE_BCU = data_df.loc[:]['O_RATE_BCU']
   elif line_type == 'VL1L2':
       UFBAR = data_df.loc[:]['UFBAR']
       VFBAR = data_df.loc[:]['VFBAR']
       UOBAR = data_df.loc[:]['UOBAR']
       VOBAR = data_df.loc[:]['VOBAR']
       UVFOBAR = data_df.loc[:]['UVFOBAR']
       UVFFBAR = data_df.loc[:]['UVFFBAR']
       UVOOBAR = data_df.loc[:]['UVOOBAR']
       F_SPEED_BAR = data_df.loc[:]['F_SPEED_BAR']
       O_SPEED_BAR = data_df.loc[:]['O_SPEED_BAR']
       TOTAL_DIR = data_df.loc[:]['TOTAL_DIR']
       DIR_ME = data_df.loc[:]['DIR_ME']
       DIR_MAE = data_df.loc[:]['DIR_MAE']
       DIR_MSE = data_df.loc[:]['DIR_MSE']
   elif line_type == 'VAL1L2':
       UFABAR = data_df.loc[:]['UFABAR']
       VFABAR = data_df.loc[:]['VFABAR']
       UOABAR = data_df.loc[:]['UOABAR']
       VOABAR = data_df.loc[:]['VOABAR']
       UVFOABAR = data_df.loc[:]['UVFOABAR']
       UVFFABAR = data_df.loc[:]['UVFFABAR']
       UVOOABAR = data_df.loc[:]['UVOOABAR']
       FA_SPEED_BAR = data_df.loc[:]['FA_SPEED_BAR']
       OA_SPEED_BAR = data_df.loc[:]['OA_SPEED_BAR']
       TOTAL_DIR = data_df.loc[:]['TOTAL_DIR']
       DIRA_ME = data_df.loc[:]['DIRA_ME']
       DIRA_MAE = data_df.loc[:]['DIRA_MAE']
       DIRA_MSE = data_df.loc[:]['DIRA_MSE']
   elif line_type == 'VCNT':
       FBAR = data_df.loc[:]['FBAR']
       OBAR = data_df.loc[:]['OBAR']
       FS_RMS = data_df.loc[:]['FS_RMS']
       OS_RMS = data_df.loc[:]['OS_RMS']
       MSVE = data_df.loc[:]['MSVE']
       RMSVE = data_df.loc[:]['RMSVE']
       FSTDEV = data_df.loc[:]['FSTDEV']
       OSTDEV = data_df.loc[:]['OSTDEV']
       FDIR = data_df.loc[:]['FDIR']
       ORDIR = data_df.loc[:]['ODIR']
       FBAR_SPEED = data_df.loc[:]['FBAR_SPEED']
       OBAR_SPEED = data_df.loc[:]['OBAR_SPEED']
       VDIFF_SPEED = data_df.loc[:]['VDIFF_SPEED']
       VDIFF_DIR = data_df.loc[:]['VDIFF_DIR']
       SPEED_ERR = data_df.loc[:]['SPEED_ERR']
       SPEED_ABSERR = data_df.loc[:]['SPEED_ABSERR']
       DIR_ERR = data_df.loc[:]['DIR_ERR']
       DIR_ABSERR = data_df.loc[:]['DIR_ABSERR']
       ANOM_CORR = data_df.loc[:]['ANOM_CORR']
       ANOM_CORR_NCL = data_df.loc[:]['ANOM_CORR_NCL']
       ANOM_CORR_NCU = data_df.loc[:]['ANOM_CORR_NCU']
       ANOM_CORR_BCL = data_df.loc[:]['ANOM_CORR_BCL']
       ANOM_CORR_BCU = data_df.loc[:]['ANOM_CORR_BCU']
       ANOM_CORR_UNCNTR = data_df.loc[:]['ANOM_CORR_UNCNTR']
       ANOM_CORR_UNCNTR_BCL = data_df.loc[:]['ANOM_CORR_UNCNTR_BCL']
       ANOM_CORR_UNCNTR_BCU = data_df.loc[:]['ANOM_CORR_UNCNTR_BCU']
       TOTAL_DIR = data_df.loc[:]['TOTAL_DIR']
       DIR_ME = data_df.loc[:]['DIR_ME']
       DIR_ME_BCL = data_df.loc[:]['DIR_ME_BCL']
       DIR_ME_BCU = data_df.loc[:]['DIR_ME_BCU']
       DIR_MAE = data_df.loc[:]['DIR_MAE']
       DIR_MAE_BCL = data_df.loc[:]['DIR_MAE_BCL']
       DIR_MAE_BCU = data_df.loc[:]['DIR_MAE_BCU']
       DIR_MSE = data_df.loc[:]['DIR_MSE']
       DIR_MSE_BCL = data_df.loc[:]['DIR_MSE_BCL']
       DIR_MSE_BCU = data_df.loc[:]['DIR_MSE_BCU']
       DIR_RMSE = data_df.loc[:]['DIR_RMSE']
       DIR_RMSE_BCL = data_df.loc[:]['DIR_RMSE_BCL']
       DIR_RMSE_BCU = data_df.loc[:]['DIR_RMSE_BCU']
   if stat == 'ACC': # Anomaly Correlation Coefficient
       if line_type == 'SAL1L2':
           radicand = (FFABAR - FABAR*FABAR)*(OOABAR - OABAR*OABAR)
           radicand[radicand<0] = np.nan
           stat_df = (FOABAR - FABAR*OABAR) \
                     /np.sqrt(radicand)
       elif line_type in ['CNT', 'VCNT']:
           stat_df = ANOM_CORR
       elif line_type == 'VAL1L2':
           radicand = UVFFABAR*UVOOABAR
           radicand[radicand<0] = np.nan
           stat_df = UVFOABAR/np.sqrt(radicand)
   elif stat in ['BIAS', 'ME']: # Bias/Mean Error
       if line_type == 'SL1L2':
           stat_df = FBAR - OBAR
       elif line_type == 'CNT':
           stat_df = ME
       elif line_type == 'VL1L2':
           radicand1 = UVFFBAR
           radicand1[radicand1<0] = np.nan
           radicand2 = UVOOBAR
           radicand2[radicand2<0] = np.nan
           stat_df = np.sqrt(radicand1) - np.sqrt(radicand2)
   elif stat == 'CORR': # Pearson Correlation Coefficient
       if line_type == 'SL1L2':
           var_f = FFBAR - FBAR*FBAR
           var_o = OOBAR - OBAR*OBAR
           radicand = var_f*var_o
           radicand[radicand<0] = np.nan
           stat_df = (FOBAR - (FBAR*OBAR))/np.sqrt(radicand)
   elif stat == 'CSI': # Critical Success Index'
       if line_type == 'CTC':
           stat_df = FY_OY/(FY_OY + FY_ON + FN_OY)
   elif stat == 'F1_O1': # Count of forecast category 1 and observation category 1
       if line_type == 'MCTC':
           stat_df = F1_O1
   elif stat in ['ETS', 'GSS']: # Equitable Threat Score/Gilbert Skill Score
       if line_type == 'CTC':
           TOTAL = FY_OY + FY_ON + FN_OY + FN_ON
           C = ((FY_OY + FY_ON)*(FY_OY + FN_OY))/TOTAL
           stat_df = (FY_OY - C)/(FY_OY + FY_ON + FN_OY - C)
       elif line_type == 'CTS':
           stat_df = GSS
   elif stat == 'FBAR': # Forecast Mean
       if line_type == 'SL1L2':
           stat_df = FBAR
   elif stat == 'FBIAS': # Frequency Bias
       if line_type == 'CTC':
           stat_df = (FY_OY + FY_ON)/(FY_OY + FN_OY)
       elif line_type == 'CTS':
           stat_df = FBIAS
   elif stat == 'FSS': # Fraction Skill Score
       if line_type == 'NBRCNT':
           stat_df = FSS
   elif stat == 'FY_OY': # Forecast Yes/Obs Yes
       if line_type == 'CTC':
           stat_df = FY_OY
   elif stat == 'HSS': # Heidke Skill Score
       if line_type == 'CTC':
           TOTAL = FY_OY + FY_ON + FN_OY + FN_ON
           CA = (FY_OY+FY_ON)*(FY_OY+FN_OY)
           CB = (FN_OY+FN_ON)*(FY_ON+FN_ON)
           C = (CA + CB)/TOTAL
           stat_df = (FY_OY + FN_ON - C)/(TOTAL - C)
   elif stat == 'OBAR': # Observation Mean
       if line_type == 'SL1L2':
           stat_df = OBAR
   elif stat == 'POD': # Probability of Detection
       if line_type == 'CTC':
           stat_df = FY_OY/(FY_OY + FN_OY)
   elif stat == 'RMSE': # Root Mean Square Error
       if line_type == 'SL1L2':
           radicand = FFBAR + OOBAR - 2*FOBAR
           radicand[radicand<0] = np.nan
           stat_df = np.sqrt(radicand)
       elif line_type == 'CNT':
           stat_df = RMSE
       elif line_type == 'VL1L2':
           radicand = UVFFBAR + UVOOBAR - 2*UVFOBAR
           radicand[radicand<0] = np.nan
           stat_df = np.sqrt(radicand)
   elif stat == 'S1': # S1
       if line_type == 'GRAD':
           stat_df = S1
   elif stat == 'SRATIO': # Success Ratio
       if line_type == 'CTC':
           stat_df = 1 - (FY_ON/(FY_ON + FY_OY))
   elif stat == 'STDEV_ERR': # Standard Deviation of Error
       if line_type == 'SL1L2':
           radicand = (
               FFBAR + OOBAR - FBAR*FBAR - OBAR*OBAR - 2*FOBAR + 2*FBAR*OBAR
           )
           radicand[radicand<0] = np.nan
           stat_df = np.sqrt(radicand)
   elif stat == 'MSESS': # Murphy's Mean Square Error Skill Score
       if line_type == 'SL1L2':
           mse = FFBAR + OOBAR - 2*FOBAR
           var_o = OOBAR - OBAR*OBAR
           stat_df = 1 - mse/var_o
       elif line_type == 'VL1L2':
           mse = UVFFBAR + UVOOBAR - 2*UVFOBAR
           var_o = UVOOBAR - UOBAR*UOBAR - VOBAR*VOBAR
           stat_df = 1 - mse/var_o
   elif stat == 'RSD': # Ratio of Standard Deviation
       if line_type == 'SL1L2':
           var_f = FFBAR - FBAR*FBAR
           var_o = OOBAR - OBAR*OBAR
           stat_df = np.sqrt(var_f)/np.sqrt(var_o)
       elif line_type == 'VL1L2':
           var_f = UVFFBAR - UFBAR*UFBAR - VFBAR*VFBAR
           var_o = UVOOBAR - UOBAR*UOBAR - VOBAR*VOBAR
           stat_df = np.sqrt(var_f)/np.sqrt(var_o)
       elif line_type == 'VCNT':
           stat_df = FSTDEV/OSTDEV
   elif stat == 'RMSE_MD': # Root Mean Square Error from Mean Error
       if line_type == 'SL1L2':
           stat_df = np.sqrt((FBAR-OBAR)**2)
       elif line_type == 'VL1L2':
           stat_df = np.sqrt((UFBAR - UOBAR)**2 + (VFBAR - VOBAR)**2)
   elif stat == 'RMSE_PV': # Root Mean Square Error from Pattern Variation
       if line_type == 'SL1L2':
           var_f = FFBAR - FBAR**2
           var_o = OOBAR - OBAR**2
           R = (FOBAR - (FBAR*OBAR))/(np.sqrt(var_f*var_o))
           stat_df = np.sqrt(var_f + var_o - 2*np.sqrt(var_f*var_o)*R)
       elif line_type == 'VL1L2':
           var_f = UVFFBAR - UFBAR*UFBAR - VFBAR*VFBAR
           var_o = UVOOBAR - UOBAR*UOBAR - VOBAR*VOBAR
           R = (UVFOBAR - UFBAR*UOBAR - VFBAR*VOBAR)/(np.sqrt(var_f*var_o))
           stat_df = np.sqrt(var_f + var_o - 2*np.sqrt(var_f*var_o)*R)
   else:
        logger.error(stat+" is not an option")
        sys.exit(1)
   idx = 0
   idx_dict = {}
   while idx < stat_df.index.nlevels:
       idx_dict['index'+str(idx)] = len(
           stat_df.index.get_level_values(idx).unique()
       )
       idx+=1
   if stat_df.index.nlevels == 1:
       stat_array = stat_df.values.reshape(
           idx_dict['index0']
       )
   elif stat_df.index.nlevels == 2:
       stat_array = stat_df.values.reshape(
           idx_dict['index0'], idx_dict['index1']
       )
   return stat_df, stat_array

def calculate_average(logger, average_method, line_type, stat, df):
    """! Calculate average of dataset

         Args:
             logger                 - logger object
             average_method         - method to use to
                                      calculate the
                                      average (string:
                                      mean, aggregation)
             line_type              - line type to calculate
                                      stat from
             stat                   - statistic to calculate
                                      (string)
             df                     - dataframe of values
         Returns:
    """
    average_value = np.nan
    if average_method == 'mean':
        average_value = np.ma.masked_invalid(df).mean()
    elif average_method == 'aggregation':
        if not df.isnull().values.all():
            ndays = (
                len(df.loc[:,'TOTAL'])
                -np.ma.count_masked(np.ma.masked_invalid(df.loc[:,'TOTAL']))
            )
            avg_df, avg_array = calculate_stat(
                logger, df.loc[:,'TOTAL':].agg(['sum'])/ndays,
                line_type, stat
            )
            average_value = avg_array[0]
    else:
        logger.warning(f"{average_method} not recognized..."
                       +"use mean, or aggregation...returning NaN")
    return average_value

def calculate_scorecard_stat(logger, model_data, stat):
    """! Calculate the statistic from the data from the
         read in MET .stat file(s)

             Args:
                 model_data        - Dataframe containing the model(s)
                                     information from the MET .stat
                                     files
                 stat              - string of the simple statistic
                                     name being plotted

             Returns:
                 stat_values       - Dataframe of the statistic values
                 stat_values_array - array of the statistic values
                 stat_plot_name    - string of the formal statistic
                                     name being plotted
    """
    model_data_columns = model_data.columns.values.tolist()
    if model_data_columns == [ 'TOTAL' ]:
        logger.warning("Empty model_data dataframe")
        line_type = 'NULL'
        if (stat == 'fbar_obar' or stat == 'orate_frate'
                or stat == 'baser_frate'):
            stat_values = model_data.loc[:][['TOTAL']]
            stat_values_fbar = model_data.loc[:]['TOTAL']
            stat_values_obar = model_data.loc[:]['TOTAL']
        else:
            stat_values = model_data.loc[:]['TOTAL']
    else:
        if all(elem in model_data_columns for elem in
               ['FBAR', 'OBAR', 'MAE']):
            line_type = 'SL1L2'
            fbar = model_data.loc[:]['FBAR']
            obar = model_data.loc[:]['OBAR']
            fobar = model_data.loc[:]['FOBAR']
            ffbar = model_data.loc[:]['FFBAR']
            oobar = model_data.loc[:]['OOBAR']
        elif all(elem in model_data_columns for elem in
                 ['FABAR', 'OABAR', 'MAE']):
            line_type = 'SAL1L2'
            fabar = model_data.loc[:]['FABAR']
            oabar = model_data.loc[:]['OABAR']
            foabar = model_data.loc[:]['FOABAR']
            ffabar = model_data.loc[:]['FFABAR']
            ooabar = model_data.loc[:]['OOABAR']
        elif all(elem in model_data_columns for elem in
                 ['UFBAR', 'VFBAR']):
            line_type = 'VL1L2'
            ufbar = model_data.loc[:]['UFBAR']
            vfbar = model_data.loc[:]['VFBAR']
            uobar = model_data.loc[:]['UOBAR']
            vobar = model_data.loc[:]['VOBAR']
            uvfobar = model_data.loc[:]['UVFOBAR']
            uvffbar = model_data.loc[:]['UVFFBAR']
            uvoobar = model_data.loc[:]['UVOOBAR']
        elif all(elem in model_data_columns for elem in
                 ['UFABAR', 'VFABAR']):
            line_type = 'VAL1L2'
            ufabar = model_data.loc[:]['UFABAR']
            vfabar = model_data.loc[:]['VFABAR']
            uoabar = model_data.loc[:]['UOABAR']
            voabar = model_data.loc[:]['VOABAR']
            uvfoabar = model_data.loc[:]['UVFOABAR']
            uvffabar = model_data.loc[:]['UVFFABAR']
            uvooabar = model_data.loc[:]['UVOOABAR']
        elif all(elem in model_data_columns for elem in
                 ['VDIFF_SPEED', 'VDIFF_DIR']):
            line_type = 'VCNT'
            fbar = model_data.loc[:]['FBAR']
            obar = model_data.loc[:]['OBAR']
            fs_rms = model_data.loc[:]['FS_RMS']
            os_rms = model_data.loc[:]['OS_RMS']
            msve = model_data.loc[:]['MSVE']
            rmsve = model_data.loc[:]['RMSVE']
            fstdev = model_data.loc[:]['FSTDEV']
            ostdev = model_data.loc[:]['OSTDEV']
            fdir = model_data.loc[:]['FDIR']
            odir = model_data.loc[:]['ODIR']
            fbar_speed = model_data.loc[:]['FBAR_SPEED']
            obar_speed = model_data.loc[:]['OBAR_SPEED']
            vdiff_speed = model_data.loc[:]['VDIFF_SPEED']
            vdiff_dir =  model_data.loc[:]['VDIFF_DIR']
            speed_err = model_data.loc[:]['SPEED_ERR']
            dir_err = model_data.loc[:]['DIR_ERR']
        elif all(elem in model_data_columns for elem in
                 ['FY_OY', 'FN_ON']):
            line_type = 'CTC'
            total = model_data.loc[:]['TOTAL']
            fy_oy = model_data.loc[:]['FY_OY']
            fy_on = model_data.loc[:]['FY_ON']
            fn_oy = model_data.loc[:]['FN_OY']
            fn_on = model_data.loc[:]['FN_ON']
        else:
            logger.error("Could not recognize line type from columns")
            exit(1)
    if stat == 'bias':
        stat_plot_name = 'Bias'
        if line_type == 'SL1L2':
            stat_values = fbar - obar
        elif line_type == 'VL1L2':
            stat_values = np.sqrt(uvffbar) - np.sqrt(uvoobar)
        elif line_type == 'VCNT':
            stat_values = fbar - obar
        elif line_type == 'CTC':
            stat_values = (fy_oy + fy_on)/(fy_oy + fn_oy)
    elif stat == 'rmse':
        stat_plot_name = 'Root Mean Square Error'
        if line_type == 'SL1L2':
            stat_values = np.sqrt(ffbar + oobar - 2*fobar)
        elif line_type == 'VL1L2':
            stat_values = np.sqrt(uvffbar + uvoobar - 2*uvfobar)
    elif stat == 'msess':
        stat_plot_name = "Murphy's Mean Square Error Skill Score"
        if line_type == 'SL1L2':
            mse = ffbar + oobar - 2*fobar
            var_o = oobar - obar*obar
            stat_values = 1 - mse/var_o
        elif line_type == 'VL1L2':
            mse = uvffbar + uvoobar - 2*uvfobar
            var_o = uvoobar - uobar*uobar - vobar*vobar
            stat_values = 1 - mse/var_o
    elif stat == 'rsd':
        stat_plot_name = 'Ratio of Standard Deviation'
        if line_type == 'SL1L2':
            var_f = ffbar - fbar*fbar
            var_o = oobar - obar*obar
            stat_values = np.sqrt(var_f)/np.sqrt(var_o)
        elif line_type == 'VL1L2':
            var_f = uvffbar - ufbar*ufbar - vfbar*vfbar
            var_o = uvoobar - uobar*uobar - vobar*vobar
            stat_values = np.sqrt(var_f)/np.sqrt(var_o)
        elif line_type == 'VCNT':
            stat_values = fstdev/ostdev
    elif stat == 'rmse_md':
        stat_plot_name = 'Root Mean Square Error from Mean Error'
        if line_type == 'SL1L2':
            stat_values = np.sqrt((fbar-obar)**2)
        elif line_type == 'VL1L2':
            stat_values = np.sqrt((ufbar - uobar)**2 + (vfbar - vobar)**2)
    elif stat == 'rmse_pv':
        stat_plot_name = 'Root Mean Square Error from Pattern Variation'
        if line_type == 'SL1L2':
            var_f = ffbar - fbar**2
            var_o = oobar - obar**2
            R = (fobar - (fbar*obar))/(np.sqrt(var_f*var_o))
            stat_values = np.sqrt(var_f + var_o - 2*np.sqrt(var_f*var_o)*R)
        elif line_type == 'VL1L2':
            var_f = uvffbar - ufbar*ufbar - vfbar*vfbar
            var_o = uvoobar - uobar*uobar - vobar*vobar
            R = (uvfobar - ufbar*uobar - vfbar*vobar)/(np.sqrt(var_f*var_o))
            stat_values = np.sqrt(var_f + var_o - 2*np.sqrt(var_f*var_o)*R)
    elif stat == 'pcor':
        stat_plot_name = 'Pattern Correlation'
        if line_type == 'SL1L2':
            var_f = ffbar - fbar*fbar
            var_o = oobar - obar*obar
            stat_values = (fobar - fbar*obar)/(np.sqrt(var_f*var_o))
        elif line_type == 'VL1L2':
            var_f = uvffbar - ufbar*ufbar - vfbar*vfbar
            var_o = uvoobar - uobar*uobar - vobar*vobar
            stat_values = (uvfobar - ufbar*uobar - vfbar*vobar)/(np.sqrt(
                              var_f*var_o))
    elif stat == 'acc':
        stat_plot_name = 'Anomaly Correlation Coefficient'
        if line_type == 'SAL1L2':
            stat_values = \
                (foabar - fabar*oabar)/(np.sqrt(
                (ffabar - fabar*fabar)*(ooabar - oabar*oabar)))
        elif line_type == 'VAL1L2':
            stat_values = (uvfoabar)/(np.sqrt(uvffabar*uvooabar))
    elif stat == 'fbar':
        stat_plot_name = 'Forecast Averages'
        if line_type == 'SL1L2':
            stat_values = fbar
        elif line_type == 'VL1L2':
            stat_values = np.sqrt(uvffbar)
        elif line_type == 'VCNT':
            stat_values = fbar
    elif stat == 'fbar_obar':
        stat_plot_name = 'Forecast and Observation Averages'
        if line_type == 'SL1L2':
            stat_values = model_data.loc[:][['FBAR', 'OBAR']]
            stat_values_fbar = model_data.loc[:]['FBAR']
            stat_values_obar = model_data.loc[:]['OBAR']
        elif line_type == 'VL1L2':
            stat_values = model_data.loc[:][['UVFFBAR', 'UVOOBAR']]
            stat_values_fbar = np.sqrt(model_data.loc[:]['UVFFBAR'])
            stat_values_obar = np.sqrt(model_data.loc[:]['UVOOBAR'])
        elif line_type == 'VCNT':
            stat_values = model_data.loc[:][['FBAR', 'OBAR']]
            stat_values_fbar = model_data.loc[:]['FBAR']
            stat_values_obar = model_data.loc[:]['OBAR']
    elif stat == 'speed_err':
        stat_plot_name = (
            'Difference in Average FCST and OBS Wind Vector Speeds'
        )
        if line_type == 'VCNT':
            stat_values = speed_err
    elif stat == 'dir_err':
        stat_plot_name = (
            'Difference in Average FCST and OBS Wind Vector Direction'
        )
        if line_type == 'VCNT':
           stat_values = dir_err
    elif stat == 'rmsve':
        stat_plot_name = 'Root Mean Square Difference Vector Error'
        if line_type == 'VCNT':
           stat_values = rmsve
    elif stat == 'vdiff_speed':
        stat_plot_name = 'Difference Vector Speed'
        if line_type == 'VCNT':
            stat_values = vdiff_speed
    elif stat == 'vdiff_dir':
        stat_plot_name = 'Difference Vector Direction'
        if line_type == 'VCNT':
           stat_values = vdiff_dir
    elif stat == 'fbar_obar_speed':
        stat_plot_name = 'Average Wind Vector Speed'
        if line_type == 'VCNT':
            stat_values = model_data.loc[:][('FBAR_SPEED', 'OBAR_SPEED')]
    elif stat == 'fbar_obar_dir':
        stat_plot_name = 'Average Wind Vector Direction'
        if line_type == 'VCNT':
           stat_values = model_data.loc[:][('FDIR', 'ODIR')]
    elif stat == 'fbar_speed':
        stat_plot_name = 'Average Forecast Wind Vector Speed'
        if line_type == 'VCNT':
            stat_values = fbar_speed
    elif stat == 'fbar_dir':
        stat_plot_name = 'Average Forecast Wind Vector Direction'
        if line_type == 'VCNT':
            stat_values = fdir
    elif stat == 'orate' or stat == 'baser':
        if stat == 'orate':
            stat_plot_name = 'Observation Rate'
        elif stat == 'baser':
            stat_plot_name = 'Base Rate'
        if line_type == 'CTC':
            stat_values = (fy_oy + fn_oy)/total
    elif stat == 'frate':
        stat_plot_name = 'Forecast Rate'
        if line_type == 'CTC':
            stat_values = (fy_oy + fy_on)/total
    elif stat == 'orate_frate' or stat == 'baser_frate':
        if stat == 'orate_frate':
            stat_plot_name = 'Observation and Forecast Rates'
        elif stat == 'baser_frate':
            stat_plot_name = 'Base and Forecast Rates'
        if line_type == 'CTC':
            stat_values_fbar = (fy_oy + fy_on)/total
            stat_values_obar = (fy_oy + fn_oy)/total
            stat_values = pd.concat([stat_values_fbar, stat_values_obar],
                                    axis=1)
    elif stat == 'accuracy':
        stat_plot_name = 'Accuracy'
        if line_type == 'CTC':
            stat_values = (fy_oy + fn_on)/total
    elif stat == 'fbias':
        stat_plot_name = 'Frequency Bias'
        if line_type == 'CTC':
            stat_values = (fy_oy + fy_on)/(fy_oy + fn_oy)
    elif stat == 'pod' or stat == 'hrate':
        if stat == 'pod':
            stat_plot_name = 'Probability of Detection'
        elif stat == 'hrate':
            stat_plot_name = 'Hit Rate'
        if line_type == 'CTC':
            stat_values = fy_oy/(fy_oy + fn_oy)
    elif stat == 'pofd' or stat == 'farate':
        if stat == 'pofd':
            stat_plot_name = 'Probability of False Detection'
        elif stat == 'farate':
            stat_plot_name = 'False Alarm Rate'
        if line_type == 'CTC':
            stat_values = fy_on/(fy_on + fn_on)
    elif stat == 'podn':
        stat_plot_name = 'Probability of Detection of the Non-Event'
        if line_type == 'CTC':
            stat_values = fn_on/(fy_on + fn_on)
    elif stat == 'faratio':
        stat_plot_name = 'False Alarm Ratio'
        if line_type == 'CTC':
            stat_values = fy_on/(fy_on + fy_oy)
    elif stat == 'csi' or stat == 'ts':
        if stat == 'csi':
            stat_plot_name = 'Critical Success Index'
        elif stat == 'ts':
            stat_plot_name = 'Threat Score'
        if line_type == 'CTC':
            stat_values = fy_oy/(fy_oy + fy_on + fn_oy)
    elif stat == 'gss' or stat == 'ets':
        if stat == 'gss':
            stat_plot_name = 'Gilbert Skill Score'
        elif stat == 'ets':
            stat_plot_name = 'Equitable Threat Score'
        if line_type == 'CTC':
            C = ((fy_oy + fy_on)*(fy_oy + fn_oy))/total
            stat_values = (fy_oy - C)/(fy_oy + fy_on+ fn_oy - C)
    elif stat == 'hk' or stat == 'tss' or stat == 'pss':
        if stat == 'hk':
            stat_plot_name = 'Hanssen-Kuipers Discriminant'
        elif stat == 'tss':
            stat_plot_name = 'True Skill Score'
        elif stat == 'pss':
            stat_plot_name = 'Peirce Skill Score'
        if line_type == 'CTC':
            stat_values = (
                ((fy_oy*fn_on)-(fy_on*fn_oy))/((fy_oy+fn_oy)*(fy_on+fn_on))
            )
    elif stat == 'hss':
        stat_plot_name = 'Heidke Skill Score'
        if line_type == 'CTC':
            Ca = (fy_oy+fy_on)*(fy_oy+fn_oy)
            Cb = (fn_oy+fn_on)*(fy_on+fn_on)
            C = (Ca + Cb)/total
            stat_values = (fy_oy + fn_on - C)/(total - C)
    else:
        logger.error(stat+" is not a valid option")
        exit(1)
    nindex = stat_values.index.nlevels
    if stat == 'fbar_obar' or stat == 'orate_frate' or stat == 'baser_frate':
        if nindex == 1:
            index0 = len(stat_values_fbar.index.get_level_values(0).unique())
            stat_values_array_fbar = (
                np.ma.masked_invalid(
                    stat_values_fbar.values.reshape(index0)
                )
            )
            index0 = len(stat_values_obar.index.get_level_values(0).unique())
            stat_values_array_obar = (
                np.ma.masked_invalid(
                    stat_values_obar.values.reshape(index0)
                )
            )
        elif nindex == 2:
            index0 = len(stat_values_fbar.index.get_level_values(0).unique())
            index1 = len(stat_values_fbar.index.get_level_values(1).unique())
            stat_values_array_fbar = (
                np.ma.masked_invalid(
                    stat_values_fbar.values.reshape(index0,index1)
                )
            )
            index0 = len(stat_values_obar.index.get_level_values(0).unique())
            index1 = len(stat_values_obar.index.get_level_values(1).unique())
            stat_values_array_obar = (
                np.ma.masked_invalid(
                    stat_values_obar.values.reshape(index0,index1)
                )
            )
        elif nindex == 3:
            index0 = len(stat_values_fbar.index.get_level_values(0).unique())
            index1 = len(stat_values_fbar.index.get_level_values(1).unique())
            index2 = len(stat_values_fbar.index.get_level_values(2).unique())
            stat_values_array_fbar = (
                np.ma.masked_invalid(
                    stat_values_fbar.values.reshape(index0,index1,index2)
                )
            )
            index0 = len(stat_values_obar.index.get_level_values(0).unique())
            index1 = len(stat_values_obar.index.get_level_values(1).unique())
            index2 = len(stat_values_obar.index.get_level_values(2).unique())
            stat_values_array_obar = (
                np.ma.masked_invalid(
                    stat_values_obar.values.reshape(index0,index1,index2)
                )
            )
        stat_values_array = np.ma.array([stat_values_array_fbar,
                                         stat_values_array_obar])
    else:
        if nindex == 1:
            index0 = len(stat_values.index.get_level_values(0).unique())
            stat_values_array = (
                np.ma.masked_invalid(
                    stat_values.values.reshape(1,index0)
                )
            )
        elif nindex == 2:
            index0 = len(stat_values.index.get_level_values(0).unique())
            index1 = len(stat_values.index.get_level_values(1).unique())
            stat_values_array = (
                np.ma.masked_invalid(
                    stat_values.values.reshape(1,index0,index1)
                )
            )
        elif nindex == 3:
            index0 = len(stat_values.index.get_level_values(0).unique())
            index1 = len(stat_values.index.get_level_values(1).unique())
            index2 = len(stat_values.index.get_level_values(2).unique())
            stat_values_array = (
                np.ma.masked_invalid(
                    stat_values.values.reshape(1,index0,index1,index2)
                )
            )
    return stat_values, stat_values_array, stat_plot_name

def calculate_scorecard_average(logger, average_method, stat, model_dataframe,
                      model_stat_values):
    """! Calculate average of dataset

             Args:
                 logger               - logging file
                 average_method       - string of the method to
                                        use to calculate the
                                        average
                 stat                 - string of the statistic the
                                        average is being taken for
                 model_dataframe      - dataframe of model .stat
                                        columns
                 model_stat_values    - array of statistic values

             Returns:
                 average_array        - array of average value(s)
    """
    average_array = np.empty_like(model_stat_values[:,0])
    if average_method == 'MEAN':
        for l in range(len(model_stat_values[:,0])):
            average_array[l] = np.ma.mean(model_stat_values[l,:])
    elif average_method == 'MEDIAN':
        for l in range(len(model_stat_values[:,0])):
            logger.info(np.ma.median(model_stat_values[l,:]))
            average_array[l] = np.ma.median(model_stat_values[l,:])
    elif average_method == 'AGGREGATION':
         ndays = model_dataframe.shape[0]
         model_dataframe_aggsum = (
             model_dataframe.groupby('model_plot_name').agg(['sum'])
         )
         model_dataframe_aggsum.columns = (
             model_dataframe_aggsum.columns.droplevel(1)
         )
         avg_values, avg_array, stat_plot_name = (
             calculate_scorecard_stat(logger, model_dataframe_aggsum/ndays, stat)
         )
         for l in range(len(avg_array[:,0])):
             average_array[l] = avg_array[l]
    else:
        logger.error("Invalid entry for MEAN_METHOD, "
                     +"use MEAN, MEDIAN, or AGGREGATION")
        exit(1)
    return average_array

def calculate_ci(logger, ci_method, modelB_values, modelA_values, total_days,
                 stat, average_method, randx):
    """! Calculate confidence intervals between two sets of data

             Args:
                 logger         - logging file
                 ci_method      - string of the method to use to
                                  calculate the confidence intervals
                 modelB_values  - array of values
                 modelA_values  - array of values
                 total_days     - float of total number of days
                                  being considered, sample size
                 stat           - string of the statistic the
                                  confidence intervals are being
                                  calculated for
                 average_method - string of the method to
                                  use to calculate the
                                  average
                 randx          - 2D array of random numbers [0,1)

             Returns:
                 intvl          - float of the confidence interval
    """
    if ci_method == 'EMC':
        modelB_modelA_diff = modelB_values - modelA_values
        ndays = total_days - np.ma.count_masked(modelB_modelA_diff)
        modelB_modelA_diff_mean = modelB_modelA_diff.mean()
        modelB_modelA_std = np.sqrt(
            ((modelB_modelA_diff - modelB_modelA_diff_mean)**2).mean()
        )
        if ndays >= 80:
            intvl = 1.960*modelB_modelA_std/np.sqrt(ndays-1)
        elif ndays >= 40 and ndays < 80:
            intvl = 2.000*modelB_modelA_std/np.sqrt(ndays-1)
        elif ndays >= 20 and ndays < 40:
            intvl = 2.042*modelB_modelA_std/np.sqrt(ndays-1)
        elif ndays < 20 and ndays > 0:
            intvl = 2.228*modelB_modelA_std/np.sqrt(ndays-1)
        elif ndays == 0:
            intvl = '--'
    elif ci_method == 'EMC_MONTE_CARLO':
        ntest, ntests = 1, 10000
        dates = []
        for idx_val in modelB_values.index.values:
            dates.append(idx_val[1])
        ndays = len(dates)
        rand1_data_index = pd.MultiIndex.from_product(
            [['rand1'], np.arange(1, ntests+1, dtype=int), dates],
            names=['model_plot_name', 'ntest', 'dates']
        )
        rand2_data_index = pd.MultiIndex.from_product(
            [['rand2'], np.arange(1, ntests+1, dtype=int), dates],
            names=['model_plot_name', 'ntest', 'dates']
        )
        rand1_data = pd.DataFrame(
            np.nan, index=rand1_data_index,
            columns=modelB_values.columns
        )
        rand2_data = pd.DataFrame(
            np.nan, index=rand2_data_index,
            columns=modelB_values.columns
        )
        ncolumns = len(modelB_values.columns)
        rand1_data_values = np.empty([ntests, ndays, ncolumns])
        rand2_data_values = np.empty([ntests, ndays, ncolumns])
        randx_ge0_idx = np.where(randx - 0.5 >= 0)
        randx_lt0_idx = np.where(randx - 0.5 < 0)
        rand1_data_values[randx_ge0_idx[0], randx_ge0_idx[1],:] = (
            modelA_values.iloc[randx_ge0_idx[1],:]
        )
        rand2_data_values[randx_ge0_idx[0], randx_ge0_idx[1],:] = (
           modelB_values.iloc[randx_ge0_idx[1],:]
        )
        rand1_data_values[randx_lt0_idx[0], randx_lt0_idx[1],:] = (
          modelB_values.iloc[randx_lt0_idx[1],:]
        )
        rand2_data_values[randx_lt0_idx[0], randx_lt0_idx[1],:] = (
            modelA_values.iloc[randx_lt0_idx[1],:]
        )
        ntest = 1
        while ntest <= ntests:
            rand1_data.loc[('rand1', ntest)] = rand1_data_values[ntest-1,:,:]
            rand2_data.loc[('rand2', ntest)] = rand2_data_values[ntest-1,:,:]
            ntest+=1
        intvl = np.nan
        rand1_stat_values, rand1_stat_values_array, stat_plot_name = (
            calculate_scorecard_stat(logger, rand1_data, stat)
        )
        rand2_stat_values, rand2_stat_values_array, stat_plot_name = (
            calculate_scorecard_stat(logger, rand2_data, stat)
        )
        rand1_average_array = (
            calculate_scorecard_average(logger, average_method, stat, rand1_data,
                              rand1_stat_values_array[0,0,:,:])
        )
        rand2_average_array = (
            calculate_scorecard_average(logger, average_method, stat, rand2_data,
                              rand2_stat_values_array[0,0,:,:])
        )
        scores_diff = rand2_average_array - rand1_average_array
        scores_diff_mean = np.sum(scores_diff)/ntests
        scores_diff_var = np.sum((scores_diff-scores_diff_mean)**2)
        scores_diff_std = np.sqrt(scores_diff_var/(ntests-1))
        intvl = 1.96*scores_diff_std
    else:
        logger.error("Invalid entry for MAKE_CI_METHOD, "
                     +"use EMC, EMC_MONTE_CARLO")
        exit(1)
    return intvl

def get_lead_avg_file(stat, input_filename, fcst_lead, output_base_dir):
    lead_avg_filename = stat + '_' + os.path.basename(input_filename) \
                        .replace('_dump_row.stat', '')
    # if fcst_leadX is in filename, replace it with fcst_lead_avgs
    # and add .txt to end of filename
    if f'fhr{fcst_lead}' in lead_avg_filename:
        lead_avg_filename = (
            lead_avg_filename.replace(f'fhr{fcst_lead}',
                                      'fcst_lead_avgs')
        )
        lead_avg_filename += '.txt'

    # if not, remove mention of forecast lead and
    # add fcst_lead_avgs.txt to end of filename
    elif 'fcst_lead_avgs' not in input_filename:
        lead_avg_filename = lead_avg_filename.replace(f'fhr{fcst_lead}',
                                                      '')
        lead_avg_filename += '_fcst_lead_avgs.txt'

    lead_avg_file = os.path.join(output_base_dir, 'data',
                                 lead_avg_filename)
    return lead_avg_file

def get_ci_file(stat, input_filename, fcst_lead, output_base_dir, ci_method):
    CI_filename = stat + '_' + os.path.basename(input_filename) \
                  .replace('_dump_row.stat', '')
    # if fcst_leadX is in filename, replace it with fcst_lead_avgs
    # and add .txt to end of filename
    if f'fhr{fcst_lead}' in CI_filename:
        CI_filename = CI_filename.replace(f'fhr{fcst_lead}',
                                          'fcst_lead_avgs')

    # if not and fcst_lead_avgs isn't already in filename,
    # remove mention of forecast lead and
    # add fcst_lead_avgs.txt to end of filename
    elif 'fcst_lead_avgs' not in CI_filename:
        CI_filename = CI_filename.replace(f'fhr{fcst_lead}',
                                          '')
        CI_filename += '_fcst_lead_avgs'

    CI_filename += '_CI_' + ci_method + '.txt'

    CI_file = os.path.join(output_base_dir, 'data',
                           CI_filename)
    return CI_file
