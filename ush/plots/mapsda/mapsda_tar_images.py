'''                     
Program Name: mapsda_tar_images.py
Contact(s): Shannon Shields
Abstract: This script is run by exmapsda.sh in scripts/.
          This creates a tar file of the plots and saves it to an archive directory.
'''

import sys
import os
import datetime
import glob
import itertools
import verif_global_util as vfg_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
plot_by = os.environ['plot_by']
RUN_abbrev = os.environ['RUN_abbrev']
case_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')
arch_dir = os.environ['tar_archive_dir']

for case_type in case_type_list:
    vfg_util.make_dir(arch_dir)
    cwd = os.getcwd()
    job_DATA_dir = os.path.join(DATA, RUN, 'metplus_output',
                                'images')
    tar_file = os.path.join(
        job_DATA_dir,
        'verif_global_'+RUN+'_'+case_type+'.tar')
    archive_tar_file = os.path.join(
        arch_dir,
        'verif_global_'+RUN+'_'+case_type+'.tar')
    plot_by = os.environ[f'mapsda_{case_type}_make_met_data_by']
    job_input_dir = os.path.join(DATA, RUN, 'metplus_output',
                                 'plot_by_'+plot_by,
                                 case_type, 'images')
    if len(glob.glob(job_input_dir+'/*')) != 0:
        print(f"Making tar file {tar_file} "
              +f"from {job_input_dir}")
        os.chdir(job_input_dir)
        vfg_util.run_shell_command(['tar', '-cvf', tar_file, '*'])
        os.chdir(cwd)
    else:
        print(f"No images generated in {job_input_dir}, "
              +"cannot make tar file")
    if os.path.exists(tar_file):
        print(f"Copying {tar_file} to "
              +f"{archive_tar_file}")
        vfg_util.copy_file(tar_file, archive_tar_file)

print("END: "+os.path.basename(__file__))
