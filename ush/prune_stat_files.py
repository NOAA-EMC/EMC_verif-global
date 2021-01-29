'''
Program Name: prune_stat_files.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This prunes the MET .stat files for the
          specific plotting job to help decrease
          wall time.
'''

import glob
import subprocess
import os
import datetime
import re

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
verif_case_type = os.environ['verif_case_type']
var_name = os.environ['var_name']
fcst_var_name = os.environ['fcst_var_name']
vx_mask = os.environ['vx_mask']

# Get list of models and loop through
env_var_model_list = []
regex = re.compile(r'model(\d+)$')
for key in os.environ.keys():
    result = regex.match(key)
    if result is not None:
        env_var_model_list.append(result.group(0))
for env_var_model in env_var_model_list:
    model = os.environ[env_var_model]
    # Get input and output data
    data_dir = os.path.join(DATA, RUN, 'data', model, verif_case_type)
    met_stat_files = glob.glob(os.path.join(data_dir, model+'_*'))
    pruned_data_dir = os.path.join(DATA, RUN, 'data', model,
                                   verif_case_type,
                                   var_name+'_'+vx_mask)
    if not os.path.exists(pruned_data_dir):
       os.makedirs(pruned_data_dir)
    print("Pruning "+data_dir+" for "+fcst_var_name+" and "+vx_mask)
    # Prune the MET .stat files and write to new file
    for met_stat_file in met_stat_files:
        met_stat_filename = met_stat_file.rpartition('/')[2]
        with open(met_stat_file) as msf:
            first_line = msf.readline()
            second_line = msf.readline()
        filter_cmd = (
            ' | grep "'+vx_mask+'" | grep "'+fcst_var_name+'" | grep -v "VCNT"'
        )
        ps = subprocess.Popen('grep -R "'+model+'" '+met_stat_file+filter_cmd,
                              shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        pruned_met_stat_file = os.path.join(pruned_data_dir,
                                            met_stat_filename)
        with open(pruned_met_stat_file, 'w') as pmsf:
            pmsf.write(first_line+output)
        if '/contrib' in os.environ['HOMEMET']:
            if 'V'+os.environ['MET_version'] != second_line.split(' ')[0]:
                print('V'+os.environ['MET_version']+' '+second_line.split(' ')[0])
                import pandas as pd
                met_columns = first_line.split()
                pruned_met_stat_file_data = pd.read_csv(
                    pruned_met_stat_file, sep=" ", skiprows=1,
                    skipinitialspace=True, header=None, dtype=str,
                    keep_default_na=False
                )
                pruned_met_stat_file_data.rename(
                    columns=dict(
                        zip(
                            pruned_met_stat_file_data.columns[
                                :len(met_columns)
                            ],
                            met_columns
                        )
                    ), inplace=True
                )
                pruned_met_stat_file_data_drop = (
                    pruned_met_stat_file_data.drop(
                        ['FCST_UNITS', 'OBS_UNITS'],
                        axis=1
                    )
                )
                new_first_line = first_line.replace('FCST_UNITS', '').replace('OBS_UNITS', '')
                new_output = pruned_met_stat_file_data_drop.to_string(header=False, index=False).replace(second_line.split(' ')[0], 'V'+os.environ['MET_version'])
                new_pruned_met_stat_file = os.path.join(pruned_data_dir, 'test_'+met_stat_filename)
                print(new_pruned_met_stat_file)
                with open(new_pruned_met_stat_file, 'w') as npmsf:
                    npmsf.write(new_first_line+new_output)
                os.rename(new_pruned_met_stat_file, pruned_met_stat_file)

print("END: "+os.path.basename(__file__))
