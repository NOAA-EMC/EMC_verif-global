#!/bin/sh
# Program Name: precip_step2
# Author(s)/Contact(s): Mallory Row
# Abstract: Run METplus for global precipitation verification
#           to create plots from step 1
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

export RUN_abbrev="precip2"

# Set up directories
mkdir -p $RUN
cd $RUN

# WCOSS2: Remove cray-mpich, proj if loaded
if [ $machine = "WCOSS2" ]; then
    if [[ "$_LMFILES_" == *"/cray-mpich/"* ]]; then
        module unload cray-mpich
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

# Create output directories for plots
python $USHverif_global/create_output_dirs.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran create_output_dirs.py"
echo

# Create and run job scripts for condense_stats, filter_stats, and make_plots
for group in condense_stats filter_stats make_plots; do
    export JOB_GROUP=$group
    echo "Creating and running jobs for precip plots: ${JOB_GROUP}"
    python $USHverif_global/plots/precip/step2_precip_create_job_scripts.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Succesfully ran step2_precip_create_job_scripts.py"
    chmod u+x plot_job_scripts/$group/*
    group_ncount_poe=$(ls -l  plot_job_scripts/$group/poe* |wc -l)
    group_ncount_job=$(ls -l  plot_job_scripts/$group/job* |wc -l)
    if [ $MPMD = YES ]; then
        nc=0
        while [ $nc -lt $group_ncount_poe ]; do
            nc=$((nc+1))
            poe_script=$DATA/$RUN/plot_job_scripts/$group/poe_jobs${nc}
            chmod 775 $poe_script
            export MP_PGMMODEL=mpmd
            export MP_CMDFILE=${poe_script}
            if [ $machine = WCOSS2 ]; then
                export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
                launcher="mpiexec -np ${nproc} -ppn ${ncpus_per_node} --cpu-bind verbose,depth cfp"
            else
                launcher="srun --export=ALL --multi-prog"
            fi
            $launcher $MP_CMDFILE
        done
    else
        nc=0
        while [ $nc -lt $group_ncount_job ]; do
            nc=$((nc+1))
            #sh +x $DATA/$RUN/plot_job_scripts/$group/job${nc}
            echo" $DATA/$RUN/plot_job_scripts/$group/job${nc}"
        done
    fi

done

# Tar up plots
python $USHverif_global/plots/tar_images.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran tar_images.py"

# Send images to web
if [ $SEND2WEB = YES ] ; then
    python $USHverif_global/build_webpage.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Succesfully ran build_webpage.py"
    echo
else
    if [ $KEEPDATA = NO ]; then
        cd ..
        rm -rf $RUN
    fi
fi
