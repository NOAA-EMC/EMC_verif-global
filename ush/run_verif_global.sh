#!/bin/sh -e
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Used to run the verif_global package in a stand alone mode.
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

export HOMEverif_global=`eval "cd ../;pwd"`  # Home base of verif_global

echo "=============== SOURCING CONFIGS ==============="
passed_config=$1
passed_config_strlength=$(echo -n $passed_config | wc -m)
if [ $passed_config_strlength = 0 ]; then
    echo "No config passed, using default: $HOMEverif_global/parm/config/config.vrfy"
    config=$HOMEverif_global/parm/config/config.vrfy
else
    config=$(readlink -f $passed_config)
    if [ ! -e $config ]; then
        echo "The passed config $config does not exist"
        exit 1
    else
        echo "Using passed config: $config"
    fi
fi
. $config
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully sourced ${config}"
echo
 
echo "=============== SETTING UP ==============="
. $HOMEverif_global/ush/set_up_verif_global.sh
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran set_up_verif_global.sh"

echo "=============== RUNNING METPLUS ==============="
if [ $RUN_GRID2GRID_STEP1 = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-GRID STEP 1 VERIFICATION  ====="
    echo "===== creating partial sum data for grid-to-grid verifcation using METplus ====="
    export RUN="grid2grid_step1"
    python $HOMEverif_global/ush/run_batch.py $machine $HOMEverif_global/scripts/exgrid2grid_step1.sh
fi 

if [ $RUN_GRID2GRID_STEP2 = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-GRID STEP 2 VERIFICATION  ====="
    echo "===== calculating statistics and creating plots for grid-to-grid verifcation using METplus ====="
    export RUN="grid2grid_step2"
    python $HOMEverif_global/ush/run_batch.py $machine $HOMEverif_global/scripts/exgrid2grid_step2.sh
fi

if [ $RUN_GRID2OBS_STEP1 = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-OBSERVATIONS STEP 1 VERIFICATION  ====="
    echo "===== creating partial sum data for grid-to-observations verifcation using METplus ====="
    export RUN="grid2obs_step1"
    python $HOMEverif_global/ush/run_batch.py $machine $HOMEverif_global/scripts/exgrid2obs_step1.sh
fi  

if [ $RUN_GRID2OBS_STEP2 = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-OBSERBATIONS STEP 2 VERIFICATION  ====="
    echo "===== calculating statistics and creating plots for grid-to-observations verifcation using METplus ====="
    export RUN="grid2obs_step2"
    python $HOMEverif_global/ush/run_batch.py $machine $HOMEverif_global/scripts/exgrid2obs_step2.sh
fi 

if [ $RUN_PRECIP_STEP1 = YES ] ; then
    echo
    echo "===== RUNNING PRECIPITATION STEP 1 VERIFICATION  ====="
    echo "===== creating partial sum data for precipitation verifcation using METplus ====="
    export RUN="precip_step1"
    python $HOMEverif_global/ush/run_batch.py $machine $HOMEverif_global/scripts/exprecip_step1.sh
fi

if [ $RUN_PRECIP_STEP2 = YES ] ; then
    echo
    echo "===== PRECIPITATION VERIFICATION PLOTTING IS NOT SUPPORTED AT THIS TIME ====="
    export RUN="precip_step2"
fi

if [ $RUN_TROPCYC = YES ] ; then
    echo
    echo "===== TROPICAL CYCLONE VERIFICATION IS NOT SUPPORTED AT THIS TIME ====="
    export RUN="tropcyc"
fi

if [ $RUN_MAPS2D = YES ] ; then
    echo
    echo "===== 2D MAP PLOTTING VERIFICATION IS NOT SUPPORTED AT THIS TIME ====="
    export RUN="maps2d"
fi

if [ $RUN_MAPSGDAS = YES ] ; then
    echo
    echo "===== GDAS MAP PLOTTING VERIFICATION IS NOT SUPPORTED AT THIS TIME ====="
    export RUN="mapsgdas"
fi

if [ $RUN_MAPSENKF = YES ] ; then
    echo
    echo "===== ENKF MAP PLOTTING VERIFICATION IS NOT SUPPORTED AT THIS TIME ====="
    export RUN="mapsenkf"
fi
