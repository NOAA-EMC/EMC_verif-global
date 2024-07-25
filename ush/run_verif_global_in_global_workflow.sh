#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Used to run the verif_global package in the Global Workflow.
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

# Set information based on gfs_cyc
if [ $gfs_cyc = 1 ]; then
    export fcyc_list="$cyc"
    export vhr_list="$cyc"
    export cyc2run="$cyc"
elif [ $gfs_cyc = 2 ]; then
    export fcyc_list="00 12"
    export vhr_list="00 12"
    export cyc2run=12
elif [ $gfs_cyc = 4 ]; then
    export fcyc_list="00 06 12 18"
    export vhr_list="00 06 12 18"
    export cyc2run=18
else
    echo "EXIT ERROR: gfs_cyc must be 1, 2 or 4." 
    exit 1
fi

export SDATE_GFS=${SDATE_GFS:-$SDATE}
export EDATE_GFS=${EDATE_GFS:-$EDATE}
export VDATE="${VDATE:-$(echo $($NDATE -${VRFYBACK_HRS} $CDATE) | cut -c1-8)}"

# Handle cases where SDATE_GFS is not on 00Z and gfs_cyc=2 or 4
if [[ ${SDATE_GFS} == "${CDATE}" && "${cyc}" != "00" ]]; then
    if [[ ${gfs_cyc} == 2 ]]; then
        export fcyc_list="${cyc}"
        export vhr_list="${cyc}"
    elif [[ ${gfs_cyc} == 4 ]]; then
        # e.g. cyc=6, fcyc_list="6 12 18"
        export fcyc_list="$(seq -f '%02g' ${cyc} 6 18)"
        export vhr_list="$(seq -f '%02g' ${cyc} 6 18)"
    fi
fi

# Check if EDATE_GFS is before 18Z
if [[ ${EDATE_GFS: -2} != "18" && ${VDATE} == ${EDATE_GFS:0:8} && ${gfs_cyc} != 1 && ${SDATE_GFS} != ${EDATE_GFS} ]]; then
    last_cycle=${EDATE_GFS: -2}
    export cyc2run=${last_cycle}
    if [[ ${SDATE_GFS: -2} != ${CDATE} ]]; then
        start_cycle=0
    else
        start_cycle=${SDATE_GFS: -2}
    fi

    if [[ ${gfs_cyc} == 2 ]]; then
        export fcyc_list="$(seq -f '%02g' ${start_cycle} 12 ${last_cycle} )"
        export vhr_list="$(seq -f '%02g' ${start_cycle} 12 ${last_cycle} )"
    elif [[ ${gfs_cyc} == 4 ]]; then
        export fcyc_list="$(seq -f '%02g' ${start_cycle}  6 ${last_cycle} )"
        export vhr_list="$(seq -f '%02g' ${start_cycle}  6 ${last_cycle} )"
    fi
fi

if [[ ${cyc2run} != ${cyc} ]]; then
    echo "Skipping ${METPCASE} for ${cyc}"
    exit 0
fi

# Map the global workflow environment variables to EMC_verif-global variables
export RUN_GRID2GRID_STEP1=${RUN_GRID2GRID_STEP1:-NO}
export RUN_GRID2OBS_STEP1=${RUN_GRID2OBS_STEP1:-NO}
export RUN_PRECIP_STEP1=${RUN_PRECIP_STEP1:-NO}
export HOMEverif_global=${HOMEverif_global:-${HOMEgfs}/sorc/verif-global.fd}
## INPUT DATA SETTINGS
export model_list=${model:-$PSLOT}
export model_dir_list=${model_dir:-${NOSCRUB}/archive}
export model_stat_dir_list=${model_stat_dir:-${NOSCRUB}/archive}
export model_file_format_list=${model_file_format:-"pgbf{lead?fmt=%2H}.${CDUMP}.{init?fmt=%Y%m%d%H}.grib2"}
export model_hpss_dir_list=${model_hpss_dir:-/NCEPDEV/$HPSS_PROJECT/1year/$USER/$machine/scratch}
export model_data_run_hpss=${get_data_from_hpss:-"NO"}
export hpss_walltime=${hpss_walltime:-10}
## DATE SETTINGS
export start_date="$VDATE"
export end_date="$VDATE"
export spinup_period_start=${spinup_period_start:-"NA"}
export spinup_period_end=${spinup_period_end:-"NA"}
export make_met_data_by=${make_met_data_by:-VALID}
export plot_by="VALID"
## WEB SETTINGS
export SEND2WEB="NO"
export webhost="emcrzdm.ncep.noaa.gov"
export webhostid="$USER"
export webdir="/home/people/emc/www/htdocs/gmb/${webhostid}/METplus_${PSLOT}"
export img_quality="low"
## METPLUS SETTINGS
export MET_version="9.1"
export METplus_version="3.1"
export METplus_verbosity=${METplus_verbosity:-INFO}
export MET_verbosity=${MET_verbosity:-2}
export log_MET_output_to_METplus=${log_MET_output_to_METplus:-yes}
## DATA DIRECTIVE SETTINGS
export SENDARCH=${SENDARCH:-"YES"}
export SENDMETVIEWER=${SENDMETVIEWER:-"NO"}
export KEEPDATA=${KEEPDATA:-"NO"}
export SENDECF=${SENDECF:-"NO"}
export SENDCOM=${SENDCOM:-"NO"}
export SENDDBN=${SENDDBN:-"NO"}
export SENDDBN_NTC=${SENDDBN_NTC:-"NO"}
# GRID2GRID STEP 1
export g2g1_type_list=${g2g1_type_list:-"anom pres sfc"}
export g2g1_anom_truth_name=${g2g1_anom_truth_name:-"self_anl"}
export g2g1_anom_truth_file_format_list=${g2g1_anom_truth_file_format:-"pgbanl.${CDUMP}.{valid?fmt=%Y%m%d%H}.grib2"}
export g2g1_anom_fcyc_list=${fcyc_list}
export g2g1_anom_vhr_list=${vhr_list}
export g2g1_anom_fhr_min=${g2g1_anom_fhr_min:-$FHMIN_GFS}
export g2g1_anom_fhr_max=${g2g1_anom_fhr_max:-$FHMAX_GFS}
export g2g1_anom_grid=${g2g1_anom_grid:-"G002"}
export g2g1_anom_gather_by=${g2g1_anom_gather_by:-"VSDB"}
export g2g1_pres_truth_name=${g2g1_pres_truth_name:-"self_anl"}
export g2g1_pres_truth_file_format_list=${g2g1_pres_truth_file_format:-"pgbanl.${CDUMP}.{valid?fmt=%Y%m%d%H}.grib2"}
export g2g1_pres_fcyc_list=${fcyc_list}
export g2g1_pres_vhr_list=${vhr_list}
export g2g1_pres_fhr_min=${g2g1_pres_fhr_min:-$FHMIN_GFS}
export g2g1_pres_fhr_max=${g2g1_pres_fhr_max:-$FHMAX_GFS}
export g2g1_pres_grid=${g2g1_pres_grid:-"G002"}
export g2g1_pres_gather_by=${g2g1_pres_gather_by:-"VSDB"}
export g2g1_sfc_truth_name=${g2g1_sfc_truth_name:-"self_f00"}
export g2g1_sfc_truth_file_format_list=${g2g1_sfc_truth_file_format:-"pgbf00.${CDUMP}.{valid?fmt=%Y%m%d%H}.grib2"}
export g2g1_sfc_fcyc_list=${fcyc_list}
export g2g1_sfc_vhr_list=${vhr_list}
export g2g1_sfc_fhr_min=${g2g1_sfc_fhr_min:-$FHMIN_GFS}
export g2g1_sfc_fhr_max=${g2g1_sfc_fhr_max:-$FHMAX_GFS}
export g2g1_sfc_grid=${g2g1_sfc_grid:-"G002"}
export g2g1_sfc_gather_by=${g2g1_sfc_gather_by:-"VSDB"}
export g2g1_mv_database_name=${g2g1_mv_database_name:-"mv_${PSLOT}_grid2grid_metplus"}
export g2g1_mv_database_group=${g2g1_mv_database_group:-"NOAA-NCEP"}
export g2g1_mv_database_desc=${g2g1_mv_database_desc:-"Grid-to-grid METplus data for global workflow experiment ${PSLOT}"}
# GRID2OBS STEP 1
export g2o1_type_list=${g2o1_type_list:-"upper_air conus_sfc"}
export g2o1_upper_air_msg_type_list=${g2o1_upper_air_msg_type_list:-"ADPUPA"}
export g2o1_upper_air_fcyc_list=${fcyc_list}
export g2o1_upper_air_vhr_list=${g2o1_upper_air_vhr_list:-"00 06 12 18"}
export g2o1_upper_air_fhr_min=${g2o1_upper_air_fhr_min:-$FHMIN_GFS}
export g2o1_upper_air_fhr_max=${g2o1_upper_air_fhr_max:-$FHMAX_GFS}
export g2o1_upper_air_grid=${g2o1_upper_air_grid:-"G003"}
export g2o1_upper_air_gather_by=${g2o1_upper_air_gather_by:-"VSDB"}
export g2o1_conus_sfc_msg_type_list=${g2o1_conus_sfc_msg_type_list:-"ONLYSF ADPUPA"}
export g2o1_conus_sfc_fcyc_list=${fcyc_list}
export g2o1_conus_sfc_vhr_list=${g2o1_conus_sfc_vhr_list:-"00 03 06 09 12 15 18 21"}
export g2o1_conus_sfc_fhr_min=${g2o1_conus_sfc_fhr_min:-$FHMIN_GFS}
export g2o1_conus_sfc_fhr_max=${g2o1_cnous_sfc_fhr_max:-$FHMAX_GFS}
export g2o1_conus_sfc_grid=${g2o1_conus_sfc_grid:-"G104"}
export g2o1_conus_sfc_gather_by=${g2o1_conus_sfc_gather_by:-"VSDB"}
export g2o1_polar_sfc_msg_type_list=${g2o1_polar_sfc_msg_type_list:-"IABP"}
export g2o1_polar_sfc_fcyc_list=${fcyc_list}
export g2o1_polar_sfc_vhr_list=${g2o1_polar_sfc_vhr_list:-"00 03 06 09 12 15 18 21"}
export g2o1_polar_sfc_fhr_min=${g2o1_polar_sfc_fhr_min:-$FHMIN_GFS}
export g2o1_polar_sfc_fhr_max=${g2o1_polar_sfc_fhr_max:-$FHMAX_GFS}
export g2o1_polar_sfc_grid=${g2o1_polar_sfc_grid:-"G219"}
export g2o1_polar_sfc_gather_by=${g2o1_polar_sfc_gather_by:-"VSDB"}
export g2o1_prepbufr_data_run_hpss=${g2o1_prepbufr_data_run_hpss:-"NO"}
export g2o1_mv_database_name=${g2o1_mv_database_name:-"mv_${PSLOT}_grid2grid_metplus"}
export g2o1_mv_database_group=${g2o1_mv_database_group:-"NOAA-NCEP"}
export g2o1_mv_database_desc=${g2o1_mv_database_desc:-"Grid-to-obs METplus data for global workflow experiment ${PSLOT}"}
# PRECIP STEP 1
export precip1_type_list=${precip1_type_list:-"ccpa_accum24hr"}
export precip1_ccpa_accum24hr_model_bucket_list=${precip1_ccpa_accum24hr_model_bucket:-"06"}
export precip1_ccpa_accum24hr_model_var_list=${precip1_ccpa_accum24hr_model_var:-"APCP"}
export precip1_ccpa_accum24hr_model_file_format_list=${precip1_ccpa_accum24hr_model_file_format:-"pgbf{lead?fmt=%2H}.${CDUMP}.{init?fmt=%Y%m%d%H}.grib2"}
export precip1_ccpa_accum24hr_fcyc_list=${fcyc_list}
export precip1_ccpa_accum24hr_fhr_min=${precip1_ccpa_accum24hr_fhr_min:-$FHMIN_GFS}
export precip1_ccpa_accum24hr_fhr_max=${precip1_ccpa_accum24hr_fhr_max:-$FHMAX_GFS}
export precip1_ccpa_accum24hr_grid=${precip1_ccpa_accum24hr_grid:-"G211"}
export precip1_ccpa_accum24hr_gather_by=${precip1_ccpa_accum24hr_gather_by:-"VSDB"}
export precip1_obs_data_run_hpss=${precip1_obs_data_run_hpss:-"YES"}
export precip1_mv_database_name=${precip1_mv_database_name:-"mv_${PSLOT}_precip_metplus"}
export precip1_mv_database_group=${precip1_mv_database_group:-"NOAA-NCEP"}
export precip1_mv_database_desc=${precip1_mv_database_desc:-"Precip METplus data for global workflow experiment ${PSLOT}"}

echo

# Check forecast max hours, adjust if before experiment SDATE_GFS
SDATE_GFS_YYYYMMDDHH=$(echo $SDATE_GFS | cut -c1-10)
g2g1_anom_check_vhour="${g2g1_anom_vhr_list: -2}"
g2g1_anom_fhr_max_idate="$($NDATE -${g2g1_anom_fhr_max} ${VDATE}${g2g1_anom_check_vhour})"
if [ $g2g1_anom_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2g1_anom_fhr_max="$(echo $($NHOUR ${VDATE}${g2g1_anom_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2g1_pres_check_vhour="${g2g1_pres_vhr_list: -2}"
g2g1_pres_fhr_max_idate="$($NDATE -${g2g1_pres_fhr_max} ${VDATE}${g2g1_pres_check_vhour})"
if [ $g2g1_pres_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2g1_pres_fhr_max="$(echo $($NHOUR ${VDATE}${g2g1_pres_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2g1_sfc_check_vhour="${g2g1_sfc_vhr_list: -2}"
g2g1_sfc_fhr_max_idate="$($NDATE -${g2g1_sfc_fhr_max} ${VDATE}${g2g1_sfc_check_vhour})"
if [ $g2g1_sfc_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2g1_sfc_fhr_max="$(echo $($NHOUR ${VDATE}${g2g1_sfc_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2o1_upper_air_check_vhour="${g2o1_upper_air_vhr_list: -2}"
g2o1_upper_air_fhr_max_idate="$($NDATE -${g2o1_upper_air_fhr_max} ${VDATE}${g2o1_upper_air_check_vhour})"
if [ $g2o1_upper_air_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2o1_upper_air_fhr_max="$(echo $($NHOUR ${VDATE}${g2o1_upper_air_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2o1_conus_sfc_check_vhour="${g2o1_conus_sfc_vhr_list: -2}"
g2o1_conus_sfc_fhr_max_idate="$($NDATE -${g2o1_conus_sfc_fhr_max} ${VDATE}${g2o1_conus_sfc_check_vhour})"
if [ $g2o1_conus_sfc_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2o1_conus_sfc_fhr_max="$(echo $($NHOUR ${VDATE}${g2o1_conus_sfc_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2o1_polar_sfc_check_vhour="${g2o1_polar_sfc_vhr_list: -2}"
g2o1_polar_sfc_fhr_max_idate="$($NDATE -${g2o1_polar_sfc_fhr_max} ${VDATE}${g2o1_polar_sfc_check_vhour})"
if [ $g2o1_polar_sfc_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2o1_polar_sfc_fhr_max="$(echo $($NHOUR ${VDATE}${g2o1_polar_sfc_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
precip1_ccpa_accum24hr_check_vhour="12"
precip1_ccpa_accum24hr_fhr_max_idate="$($NDATE -${precip1_ccpa_accum24hr_fhr_max} ${VDATE}${precip1_ccpa_accum24hr_check_vhour})"
if [ $precip1_ccpa_accum24hr_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export precip1_ccpa_accum24hr_fhr_max="$(echo $($NHOUR ${VDATE}${precip1_ccpa_accum24hr_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi

echo

## Output set up
export jobid=${jobid:-${job}.${pid}}
export OUTPUTROOT=${DATA}
mkdir -p $DATA
cd $DATA

## Get machine
#### Need upper case machine name defined
machine=$(echo $machine | tr '[a-z]' '[A-Z]')
if [[ "$machine" =~ ^(HERA|ORION|S4|JET|WCOSS2|HERCULES)$ ]]; then
   echo
else
    echo "ERROR: $machine is not a supported machine"
    exit 1
fi

## Environment variables
if [ $machine != "ORION" ]; then
    export RM=$(which rm)
    export CUT=$(which cut)
    export TR=$(which tr)
    export CONVERT=$(which convert)
    export NCDUMP=$(which ncdump)
    export NCEA=$(which ncea)
    if [ $machine == "S4" ]; then
        export HTAR="/null/htar"
        export NCAP2="/null/ncap2"
    elif [ $machine == "JET" -o $machine == "WCOSS2" ]; then
        export HTAR=$(which htar)
        export NCAP2="/null/ncap2"
    else
        export HTAR=$(which htar)
        export NCAP2=$(which ncap2)
    fi
fi
if [ $machine = "ORION" ]; then
    export RM=$(which rm | sed 's/rm is //g')
    export CUT=$(which cut | sed 's/cut is //g')
    export TR=$(which tr | sed 's/tr is //g')
    export NCAP2=$(which ncap2 | sed 's/ncap2 is //g')
    export CONVERT=$(which convert | sed 's/convert is //g')
    export NCDUMP=$(which ncdump | sed 's/ncdump is //g')
    export NCEA=$(which ncea | sed 's/ncea is //g')
    export HTAR="/null/htar"
fi
export HOMEMET_bin_exec="bin"
if [ $machine = WCOSS2 ]; then
    export HOMEMET="/apps/ops/para/libs/intel/19.1.3.304/met/9.1.3"
    export HOMEMETplus="/apps/ops/para/libs/intel/19.1.3.304/metplus/3.1.1"
    export MET_BASE="$HOMEMET/share/met"
    export HOMEMET_bin_exec="bin"
    export LD_LIBRARY_PATH=/apps/prod/hpc-stack/intel-19.1.3.304/netcdf/4.7.4/lib:${LD_LIBRARY_PATH}
else
    export HOMEMET=$met_ROOT
    export HOMEMETplus=$metplus_ROOT
fi
echo "Using HOMEMET=${HOMEMET}"
echo "Using HOMEMETplus=${HOMEMETplus}"

## Account and queues for machines
export ACCOUNT=${ACCOUNT:-"GFS-DEV"}
export QUEUE=${QUEUE:-"dev"}
export QUEUESHARED=${QUEUE_SHARED:-"dev_shared"}
export QUEUESERV=${QUEUE_SERVICE:-"dev_transfer"}
export PARTITION_BATCH=${PARTITION_BATCH:-""}

## Run settings for machines
export MPMD="YES"
export nproc=${nproc:-1}

## Set paths for verif_global, MET, and METplus
export HOMEverif_global=$HOMEverif_global
export PARMverif_global=$HOMEverif_global/parm
export FIXverif_global=$FIXgfs/verif
export USHverif_global=$HOMEverif_global/ush
export UTILverif_global=$HOMEverif_global/util
export EXECverif_global=$HOMEverif_global/exec
export HOMEMET=$HOMEMET
export HOMEMETplus=$HOMEMETplus
export PARMMETplus=$HOMEMETplus/parm
export USHMETplus=$HOMEMETplus/ush
export PATH="${USHMETplus}:${PATH}"
export PYTHONPATH="${USHMETplus}:${PYTHONPATH}"

## Set machine and user specific directories
if [ $machine = "HERA" ]; then
    export global_archive="/scratch1/NCEPDEV/global/Mallory.Row/archive"
    export prepbufr_arch_dir="/scratch1/NCEPDEV/global/Mallory.Row/prepbufr"
    export ccpa_24hr_arch_dir="/scratch1/NCEPDEV/global/Mallory.Row/obdata/ccpa_accum24hr"
elif [ $machine = "ORION" -o $machine = "HERCULES" ]; then
    export global_archive="/work/noaa/ovp/mrow/archive"
    export prepbufr_arch_dir="/work/noaa/ovp/mrow/prepbufr"
    export ccpa_24hr_arch_dir="/work/noaa/ovp/mrow/obdata/ccpa_accum24hr"
elif [ $machine = "S4" ]; then
    export global_archive="/data/prod/glopara/MET_data/archive"
    export prepbufr_arch_dir="/data/prod/glopara/MET_data/prepbufr"
    export ccpa_24hr_arch_dir="/data/prod/glopara/MET_data/obdata/ccpa_accum24hr"
elif [ $machine = "JET" ]; then
    export global_archive="/lfs4/HFIP/hfv3gfs/Mallory.Row/archive"
    export prepbufr_arch_dir="/lfs4/HFIP/hfv3gfs/Mallory.Row/prepbufr"
    export ccpa_24hr_arch_dir="/lfs4/HFIP/hfv3gfs/Mallory.Row/obdata/ccpa_accum24hr"
elif [ $machine = "WCOSS2" ]; then
    export global_archive="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/model_data"
    export prepbufr_arch_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data/prepbufr"
    export ccpa_24hr_arch_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data/ccpa_accum24hr"
fi

## Set operational directories
export prepbufr_prod_upper_air_dir="/lfs/h1/ops/prod/com/obsproc/v1.1"
export prepbufr_prod_conus_sfc_dir="/lfs/h1/ops/prod/com/obsproc/v1.1"
export ccpa_24hr_prod_dir="/lfs/h1/ops/prod/com/verf_precip/v4.5"

## Some online sites
export iabp_ftp="http://iabp.apl.washington.edu/Data_Products/Daily_Full_Res_Data"

## Do checks on switches to run verification for
if [ $METPCASE = g2g1 ]; then
    RUN_GRID2OBS_STEP1=NO
    RUN_PRECIP_STEP1=NO
    emc_verif_switch_name="RUN_GRID2GRID_STEP1"
    export emc_verif_name="g2g1"
fi
if [ $METPCASE = g2o1 ]; then
    RUN_GRID2GRID_STEP1=NO
    RUN_PRECIP_STEP1=NO
    emc_verif_switch_name="RUN_GRID2OBS_STEP1"
    export emc_verif_name="g2o1"
fi
if [ $METPCASE = pcp1 ]; then
    RUN_GRID2GRID_STEP1=NO
    RUN_GRID2OBS_STEP1=NO
    emc_verif_switch_name="RUN_PRECIP_STEP1"
    export emc_verif_name="precip1"
fi
if [ ${start_date}${cyc2run} -lt $SDATE_GFS_YYYYMMDDHH ]; then
    RUN_GRID2GRID_STEP1=NO
    RUN_GRID2OBS_STEP1=NO
    RUN_PRECIP_STEP1=NO
fi
for fcyc in $fcyc_list; do
    if [ ${start_date}${fcyc} -lt $SDATE_GFS_YYYYMMDDHH ]; then
         RUN_GRID2GRID_STEP1=NO
         RUN_GRID2OBS_STEP1=NO
         RUN_PRECIP_STEP1=NO
    fi
done
for precip1_type in $precip1_type_list; do
    precip1_accum_length=$(echo $precip1_type | sed 's/[^0-9]*//g')
    precip_back_hours=$((VRFYBACK_HRS + precip1_accum_length))
    precip_check_date="$(echo $($NDATE -${precip_back_hours} $CDATE) | cut -c1-8)"
    if [ ${precip_check_date}${cyc2run} -lt $SDATE_GFS_YYYYMMDDHH ]; then
        RUN_PRECIP_STEP1=NO
    fi
    for fcyc in $fcyc_list; do
        if [ ${precip_check_date}${fcyc} -lt $SDATE_GFS_YYYYMMDDHH ]; then
            RUN_PRECIP_STEP1=NO
        fi
    done
done
RUN_METPCASE=${!emc_verif_switch_name}
export METPCASE_type_list=$(eval echo \${${emc_verif_name}_type_list})

## Run METplus
echo "=============== RUNNING METPLUS ==============="
if [ $RUN_GRID2GRID_STEP1 = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-GRID STEP 1 VERIFICATION  ====="
    echo "===== creating partial sum data for grid-to-grid verifcation using METplus ====="
    export RUN="grid2grid_step1"
    $HOMEverif_global/scripts/exgrid2grid_step1.sh
fi

if [ $RUN_GRID2OBS_STEP1 = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-OBSERVATIONS STEP 1 VERIFICATION  ====="
    echo "===== creating partial sum data for grid-to-observations verifcation using METplus ====="
    export RUN="grid2obs_step1"
    $HOMEverif_global/scripts/exgrid2obs_step1.sh
fi

if [ $RUN_PRECIP_STEP1 = YES ] ; then
    echo
    echo "===== RUNNING PRECIPITATION STEP 1 VERIFICATION  ====="
    echo "===== creating partial sum data for precipitation verifcation using METplus ====="
    export RUN="precip_step1"
    $HOMEverif_global/scripts/exprecip_step1.sh
fi
