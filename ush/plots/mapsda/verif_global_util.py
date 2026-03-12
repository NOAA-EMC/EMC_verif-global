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
