#!/bin/sh
# Program Name: grid2obs_step1
# Author(s)/Contact(s): Mallory Row
# Abstract: Run METplus for global grid-to-observation verification
#           to produce SL1L2 and VL1L2 stats
# History Log:
#   2/2019: Initial version of script
#
# Usage:
#   Parameters:
#       agrument to script
#   Input Files:
#       file
#   Output Files:
#       file
#
# Condition codes:
#       0 - Normal exit
#
# User controllable options: None

set -x

export RUN_abbrev="g2o1"

# Set up directories
mkdir -p $RUN
cd $RUN

# Check machine to be sure we can get the data
if [[ "$machine" =~ ^(HERA|ORION|WCOSS_C)$ ]]; then
    if grep -q "polar_sfc" <<< "$g2o1_type_list"; then
        echo "WARNING: Cannot run ${RUN} polar_sfc on ${machine}, cannot retrieve data from web in queue ${QUEUE}"
        export g2o1_type_list=`echo $g2o1_type_list | sed 's/ polar_sfc //'`
        export g2o1_type_list=`echo $g2o1_type_list | sed 's/ polar_sfc//'`
        export g2o1_type_list=`echo $g2o1_type_list | sed 's/polar_sfc //'`
    fi
fi

# Check user's configuration file
python $USHverif_global/check_config.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran check_config.py"
echo

# Set up environment variables for initialization, valid, and forecast hours and source them
python $USHverif_global/set_init_valid_fhr_info.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran set_init_valid_fhr_info.py"
echo
. $DATA/$RUN/python_gen_env_vars.sh
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully sourced python_gen_env_vars.sh"
echo

# Link needed data files and set up model information
mkdir -p data
python $USHverif_global/get_data_files.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran get_data_files.py"
echo

# Create output directories for METplus
python $USHverif_global/create_METplus_output_dirs.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran create_METplus_output_dirs.py"
echo

# Create job scripts to run METplus
python $USHverif_global/create_METplus_job_scripts.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran create_METplus_job_scripts.py"

# Run METplus job scripts
chmod u+x metplus_job_scripts/job*
if [ $MPMD = YES ]; then
    ncount=$(ls -l  metplus_job_scripts/poe* |wc -l)
    nc=0
    while [ $nc -lt $ncount ]; do
        nc=$((nc+1))
        poe_script=$DATA/$RUN/metplus_job_scripts/poe_jobs${nc}
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        if [ $machine = WCOSS_C ]; then
            launcher="aprun -j 1 -n 1 -N 1 -d 1 cfp"
        elif [ $machine = WCOSS_DELL_P3 ]; then
            launcher="mpirun -n ${nproc} cfp"
        elif [ $machine = HERA -o $machine = ORION ]; then
            launcher="srun --export=ALL --multi-prog"
        fi
        $launcher $MP_CMDFILE
    done
else
    ncount=$(ls -l  metplus_job_scripts/job* |wc -l)
    nc=0
    while [ $nc -lt $ncount ]; do
        nc=$((nc+1))
        sh +x $DATA/$RUN/metplus_job_scripts/job${nc}
    done
fi

# Copy stat files to desired location
python $USHverif_global/copy_stat_files.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran copy_stat_files.py"
echo

# Send data to METviewer AWS server and clean up
if [ $SENDMETVIEWER = YES ]; then
    python $USHverif_global/load_to_METviewer_AWS.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Succesfully ran load_to_METviewer_AWS.py"
    echo
else
    if [ $KEEPDATA = NO ]; then
        cd ..
        rm -rf $RUN
    fi
fi
