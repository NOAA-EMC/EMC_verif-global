#!/bin/sh
# Program Name: grid2obs_step2
# Author(s)/Contact(s): Mallory Row
# Abstract: Run METplus for global grid-to-observation verification 
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

# Set up directories
mkdir -p $RUN
cd $RUN

# Set up environment variables for initialization, valid, and forecast hours and source them
python $USHverif_global/set_init_valid_fhr_info.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran set_init_valid_fhr_info.py"
echo
. $DATA/$RUN/python_gen_env_vars.sh
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully sourced python_gen_env_vars.sh"
echo

# Link needed data files and set up model information
mkdir -p data
python $USHverif_global/get_data_files.py
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran get_data_files.py"
echo

# Create output directories for METplus
python $USHverif_global/create_METplus_output_dirs.py
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran create_METplus_output_dirs.py"
echo

# Create job scripts to run METplus
python $USHverif_global/create_METplus_job_scripts.py
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran create_METplus_job_scripts.py"

# Run METplus job scripts
chmod u+x metplus_job_scripts/job*
ncount=$(ls -l  metplus_job_scripts/job* |wc -l)
nc=0;iproc=0; node=1; rank=0
while [ $nc -lt $ncount ]; do
    if [ $MPMD = YES ];then
        if [ $iproc -ge $nproc ]; then iproc=0; rank=0; node=$((node+1)); fi
        poe_script=$DATA/$RUN/metplus_job_scripts/poe_jobs${node}
        if [ $iproc -eq 0 ]; then
            rm -f $poe_script; touch $poe_script
        fi
        nc=$((nc+1))
        iproc=$((iproc+1))
        if [ $machine = THEIA -o $machine = HERA ]; then
            echo "$rank $DATA/$RUN/metplus_job_scripts/job${nc}" >>$poe_script
            rank=$((rank+1))
        else
            echo "$DATA/$RUN/metplus_job_scripts/job${nc}" >>$poe_script
        fi
        if [ $iproc -eq $nproc -o $nc -eq $ncount ]; then
            # if at final record and have not reached the
            # final processor then write echo's to
            # poescript for remaining processors
            if [ $nc -eq $ncount ]; then
                while [ $iproc -lt $nproc ]; do
                    nc=$((nc+1))
                    iproc=$((iproc+1))
                    if [ $machine = THEIA -o $machine = HERA ]; then
                        echo "$rank /bin/echo $iproc" >> $poe_script
                        rank=$((rank+1))
                    else
                        echo "/bin/echo $iproc" >> $poe_script
                    fi
                done
            fi
            chmod 775 $poe_script
            export MP_PGMMODEL=mpmd
            export MP_CMDFILE=${poe_script}
            if [ $machine = WCOSS_C ]; then
                launcher="aprun -j 1 -n ${iproc} -N ${iproc} -d 1 cfp"
            elif [ $machine = WCOSS_DELL_P3 ]; then
                launcher="mpirun -n ${iproc} cfp"
            elif [ $machine = THEIA -o $machine = HERA ]; then
                launcher="srun --export=ALL --multi-prog"
            fi
            $launcher $MP_CMDFILE
            export err=$?
            if [ $err -ne 0 ]; then sh +x $poe_script ; fi
        fi
    else
        nc=$((nc+1))
        sh +x $DATA/$RUN/metplus_job_scripts/job${nc}
    fi
done

# Move images to common directory
ln -sf $DATA/$RUN/metplus_output/plot_by_$plot_by/make_plots/*/grid2obs/*/imgs/* $DATA/$RUN/metplus_output/images/.

# Send images to web
if [ $SEND2WEB = YES ] ; then
    python $USHverif_global/build_webpage.py
fi
