#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Used to run the verif_global package in the Global Workflow.
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

export SDATE_GFS=${SDATE_GFS:-$SDATE}
export EDATE_GFS=${EDATE_GFS:-$EDATE}
export VDATE=${VDATE:-$(date --utc +%Y%m%d%H -d "${PDY} ${cyc} - ${VRFYBACK_HRS} hours")}
export vPDY=${VDATE:0:8}
cyc2run="${cyc}"

# Check if we are on the first YMD
if [[ ${SDATE_GFS} == ${VDATE} ]]; then
    start_cyc=${SDATE_GFS:8:2}
else
    start_cyc=0
fi

# Check if we are on the last YMD
if [[ ${EDATE_GFS} == ${VDATE} ]]; then
    cyc2run=${EDATE_GFS:8:2}
fi

#Determine which cycles to run
export fcyc_list="$(seq -s ' ' -f '%02g' ${start_cyc} ${INTERVAL_GFS:-24} ${cyc2run} )"
export vhr_list="$(seq -s ' ' -f '%02g' ${start_cyc} ${INTERVAL_GFS:-24} ${cyc2run} )"

# Map the global workflow environment variables to EMC_verif-global variables
export RUN_GRID2GRID_STEP1=${RUN_GRID2GRID_STEP1:-NO}
export RUN_GRID2OBS_STEP1=${RUN_GRID2OBS_STEP1:-NO}
export RUN_PRECIP_STEP1=${RUN_PRECIP_STEP1:-NO}
export RUN_SATELLITE_STEP1=${RUN_SATELLITE_STEP1:-NO}
export HOMEverif_global=${HOMEverif_global:-${HOMEglobal}/sorc/verif-global.fd}
## INPUT DATA SETTINGS
export model_list=${model:-$PSLOT}
export model_dir_list=${model_dir:-${NOSCRUB}/archive/${PSLOT}}
export model_stat_dir_list=${model_stat_dir:-${NOSCRUB}/archive}
export model_file_format_list=${model_file_format:-"pgbf{lead?fmt=%2H}.${RUN}.{init?fmt=%Y%m%d%H}.grib2"}
## Get machine
#### Need upper case machine name defined
machine=$(echo $machine | tr '[a-z]' '[A-Z]')
export model_hpss_dir_list=${model_hpss_dir:-/NCEPDEV/$HPSS_PROJECT/1year/$USER/$machine/scratch}
export model_data_run_hpss=${get_data_from_hpss:-"NO"}
export hpss_walltime=${hpss_walltime:-10}
## DATE SETTINGS
export start_date="${vPDY}"
export end_date="${vPDY}"
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
export MET_version="12.0.1"
export METplus_version="6.0.0"
## DATA DIRECTIVE SETTINGS
export SENDARCH=${SENDARCH:-"YES"}
export KEEPDATA=${KEEPDATA:-"NO"}
export SENDECF=${SENDECF:-"NO"}
export SENDCOM=${SENDCOM:-"NO"}
export SENDDBN=${SENDDBN:-"NO"}
export SENDDBN_NTC=${SENDDBN_NTC:-"NO"}
# GRID2GRID STEP 1
export g2g1_type_list=${g2g1_type_list:-"anom pres sfc"}
export g2g1_anom_truth_name=${g2g1_anom_truth_name:-"self_anl"}
export g2g1_anom_truth_file_format_list=${g2g1_anom_truth_file_format:-"pgbanl.${RUN}.{valid?fmt=%Y%m%d%H}.grib2"}
export g2g1_anom_fcyc_list=${fcyc_list}
export g2g1_anom_vhr_list=${vhr_list}
export g2g1_anom_fhr_min=${g2g1_anom_fhr_min:-$FHMIN_GFS}
export g2g1_anom_fhr_max=${g2g1_anom_fhr_max:-$FHMAX_GFS}
export g2g1_anom_grid=${g2g1_anom_grid:-"G002"}
export g2g1_anom_gather_by=${g2g1_anom_gather_by:-"VALID"}
export g2g1_pres_truth_name=${g2g1_pres_truth_name:-"self_anl"}
export g2g1_pres_truth_file_format_list=${g2g1_pres_truth_file_format:-"pgbanl.${RUN}.{valid?fmt=%Y%m%d%H}.grib2"}
export g2g1_pres_fcyc_list=${fcyc_list}
export g2g1_pres_vhr_list=${vhr_list}
export g2g1_pres_fhr_min=${g2g1_pres_fhr_min:-$FHMIN_GFS}
export g2g1_pres_fhr_max=${g2g1_pres_fhr_max:-$FHMAX_GFS}
export g2g1_pres_grid=${g2g1_pres_grid:-"G002"}
export g2g1_pres_gather_by=${g2g1_pres_gather_by:-"VALID"}
export g2g1_sfc_truth_name=${g2g1_sfc_truth_name:-"self_f00"}
export g2g1_sfc_truth_file_format_list=${g2g1_sfc_truth_file_format:-"pgbf00.${RUN}.{valid?fmt=%Y%m%d%H}.grib2"}
export g2g1_sfc_fcyc_list=${fcyc_list}
export g2g1_sfc_vhr_list=${vhr_list}
export g2g1_sfc_fhr_min=${g2g1_sfc_fhr_min:-$FHMIN_GFS}
export g2g1_sfc_fhr_max=${g2g1_sfc_fhr_max:-$FHMAX_GFS}
export g2g1_sfc_grid=${g2g1_sfc_grid:-"G002"}
export g2g1_sfc_gather_by=${g2g1_sfc_gather_by:-"VALID"}
# GRID2OBS STEP 1
export g2o1_type_list=${g2o1_type_list:-"upper_air conus_sfc"}
export g2o1_upper_air_msg_type_list=${g2o1_upper_air_msg_type_list:-"ADPUPA"}
export g2o1_upper_air_fcyc_list=${fcyc_list}
export g2o1_upper_air_vhr_list=${g2o1_upper_air_vhr_list:-"00 06 12 18"}
export g2o1_upper_air_fhr_min=${g2o1_upper_air_fhr_min:-$FHMIN_GFS}
export g2o1_upper_air_fhr_max=${g2o1_upper_air_fhr_max:-$FHMAX_GFS}
export g2o1_upper_air_grid=${g2o1_upper_air_grid:-"G003"}
export g2o1_upper_air_gather_by=${g2o1_upper_air_gather_by:-"VALID"}
export g2o1_conus_sfc_msg_type_list=${g2o1_conus_sfc_msg_type_list:-"ONLYSF ADPUPA"}
export g2o1_conus_sfc_fcyc_list=${fcyc_list}
export g2o1_conus_sfc_vhr_list=${g2o1_conus_sfc_vhr_list:-"00 03 06 09 12 15 18 21"}
export g2o1_conus_sfc_fhr_min=${g2o1_conus_sfc_fhr_min:-$FHMIN_GFS}
export g2o1_conus_sfc_fhr_max=${g2o1_conus_sfc_fhr_max:-$FHMAX_GFS}
export g2o1_conus_sfc_grid=${g2o1_conus_sfc_grid:-"G104"}
export g2o1_conus_sfc_gather_by=${g2o1_conus_sfc_gather_by:-"VALID"}
export g2o1_polar_sfc_msg_type_list=${g2o1_polar_sfc_msg_type_list:-"IABP"}
export g2o1_polar_sfc_fcyc_list=${fcyc_list}
export g2o1_polar_sfc_vhr_list=${g2o1_polar_sfc_vhr_list:-"00 03 06 09 12 15 18 21"}
export g2o1_polar_sfc_fhr_min=${g2o1_polar_sfc_fhr_min:-$FHMIN_GFS}
export g2o1_polar_sfc_fhr_max=${g2o1_polar_sfc_fhr_max:-$FHMAX_GFS}
export g2o1_polar_sfc_grid=${g2o1_polar_sfc_grid:-"G219"}
export g2o1_polar_sfc_gather_by=${g2o1_polar_sfc_gather_by:-"VALID"}
export g2o1_prepbufr_data_run_hpss=${g2o1_prepbufr_data_run_hpss:-"NO"}
# PRECIP STEP 1
export precip1_type_list=${precip1_type_list:-"ccpa_accum24hr"}
export precip1_ccpa_accum24hr_model_bucket_list=${precip1_ccpa_accum24hr_model_bucket:-"06"}
export precip1_ccpa_accum24hr_model_var_list=${precip1_ccpa_accum24hr_model_var:-"APCP"}
export precip1_ccpa_accum24hr_model_file_format_list=${precip1_ccpa_accum24hr_model_file_format:-"pgbf{lead?fmt=%2H}.${RUN}.{init?fmt=%Y%m%d%H}.grib2"}
export precip1_ccpa_accum24hr_fcyc_list=${fcyc_list}
export precip1_ccpa_accum24hr_fhr_min=${precip1_ccpa_accum24hr_fhr_min:-$FHMIN_GFS}
export precip1_ccpa_accum24hr_fhr_max=${precip1_ccpa_accum24hr_fhr_max:-$FHMAX_GFS}
export precip1_ccpa_accum24hr_grid=${precip1_ccpa_accum24hr_grid:-"G211"}
export precip1_ccpa_accum24hr_gather_by=${precip1_ccpa_accum24hr_gather_by:-"VALID"}
export precip1_obs_data_run_hpss=${precip1_obs_data_run_hpss:-"YES"}
# SATELLITE STEP 1
export sat1_type_list=${sat1_type_list:-"ghrsst_ncei_avhrr_anl ghrsst_ospo_geopolar_anl"}
export sat1_ghrsst_ncei_avhrr_anl_fcyc_list=${sat1_ghrsst_ncei_avhrr_anl_fcyc_list:-${fcyc_list}}
export sat1_ghrsst_ncei_avhrr_anl_fhr_min=${sat1_ghrsst_ncei_avhrr_anl_fhr_min:-${FHMIN_GFS}}
export sat1_ghrsst_ncei_avhrr_anl_fhr_max=${sat1_ghrsst_ncei_avhrr_anl_fhr_max:-${FHMAX_GFS}}
export sat1_ghrsst_ncei_avhrr_anl_grid=${sat1_ghrsst_ncei_avhrr_anl_grid:-"G219"}
export sat1_ghrsst_ncei_avhrr_anl_gather_by=${sat1_ghrsst_ncei_avhrr_anl_gather_by:-"VALID"}
export sat1_ghrsst_ncei_avhrr_anl_sea_ice_thresh=${sat1_ghrsst_ncei_avhrr_anl_sea_ice_thresh:-"0.15"}
export sat1_ghrsst_ospo_geopolar_anl_fcyc_list=${sat1_ghrsst_ospo_geopolar_anl_fcyc_list:-${fcyc_list}}
export sat1_ghrsst_ospo_geopolar_anl_fhr_min=${sat1_ghrsst_ospo_geopolar_anl_fhr_min:-${FHMIN_GFS}}
export sat1_ghrsst_ospo_geopolar_anl_fhr_max=${sat1_ghrsst_ospo_geopolar_anl_fhr_max:-${FHMAX_GFS}}
export sat1_ghrsst_ospo_geopolar_anl_grid=${sat1_ghrsst_ospo_geopolar_anl_grid:-"G219"}
export sat1_ghrsst_ospo_geopolar_anl_gather_by=${sat1_ghrsst_ospo_geopolar_anl_gather_by:-"VALID"}
export sat1_ghrsst_ospo_geopolar_anl_sea_ice_thresh=${sat1_ghrsst_ospo_geopolar_anl_sea_ice_thresh:-"0.15"}
export sat1_obs_dir=${sat1_obs_dir:-"/gpfs/f6/drsa-precip3/world-shared/Ho-Chun.Huang/obs_archive/"}

echo

# Check forecast max hours, adjust if before experiment SDATE_GFS
SDATE_GFS_YYYYMMDDHH=$(echo $SDATE_GFS | cut -c1-10)
g2g1_anom_check_vhour="${g2g1_anom_vhr_list: -2}"
g2g1_anom_fhr_max_idate="$($NDATE -${g2g1_anom_fhr_max} ${vPDY}${g2g1_anom_check_vhour})"
if [ $g2g1_anom_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2g1_anom_fhr_max="$(echo $($NHOUR ${vPDY}${g2g1_anom_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2g1_pres_check_vhour="${g2g1_pres_vhr_list: -2}"
g2g1_pres_fhr_max_idate="$($NDATE -${g2g1_pres_fhr_max} ${vPDY}${g2g1_pres_check_vhour})"
if [ $g2g1_pres_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2g1_pres_fhr_max="$(echo $($NHOUR ${vPDY}${g2g1_pres_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2g1_sfc_check_vhour="${g2g1_sfc_vhr_list: -2}"
g2g1_sfc_fhr_max_idate="$($NDATE -${g2g1_sfc_fhr_max} ${vPDY}${g2g1_sfc_check_vhour})"
if [ $g2g1_sfc_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2g1_sfc_fhr_max="$(echo $($NHOUR ${vPDY}${g2g1_sfc_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2o1_upper_air_check_vhour="${g2o1_upper_air_vhr_list: -2}"
g2o1_upper_air_fhr_max_idate="$($NDATE -${g2o1_upper_air_fhr_max} ${vPDY}${g2o1_upper_air_check_vhour})"
if [ $g2o1_upper_air_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2o1_upper_air_fhr_max="$(echo $($NHOUR ${vPDY}${g2o1_upper_air_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2o1_conus_sfc_check_vhour="${g2o1_conus_sfc_vhr_list: -2}"
g2o1_conus_sfc_fhr_max_idate="$($NDATE -${g2o1_conus_sfc_fhr_max} ${vPDY}${g2o1_conus_sfc_check_vhour})"
if [ $g2o1_conus_sfc_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2o1_conus_sfc_fhr_max="$(echo $($NHOUR ${vPDY}${g2o1_conus_sfc_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2o1_polar_sfc_check_vhour="${g2o1_polar_sfc_vhr_list: -2}"
g2o1_polar_sfc_fhr_max_idate="$($NDATE -${g2o1_polar_sfc_fhr_max} ${vPDY}${g2o1_polar_sfc_check_vhour})"
if [ $g2o1_polar_sfc_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2o1_polar_sfc_fhr_max="$(echo $($NHOUR ${vPDY}${g2o1_polar_sfc_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
precip1_ccpa_accum24hr_check_vhour="12"
precip1_ccpa_accum24hr_fhr_max_idate="$($NDATE -${precip1_ccpa_accum24hr_fhr_max} ${vPDY}${precip1_ccpa_accum24hr_check_vhour})"
if [ $precip1_ccpa_accum24hr_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export precip1_ccpa_accum24hr_fhr_max="$(echo $($NHOUR ${vPDY}${precip1_ccpa_accum24hr_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
sat1_ghrsst_ncei_avhrr_anl_check_vhour="00"
sat1_ghrsst_ncei_avhrr_anl_fhr_max_idate="$($NDATE -${sat1_ghrsst_ncei_avhrr_anl_fhr_max} ${vPDY}${sat1_ghrsst_ncei_avhrr_anl_check_vhour})"
if [ $sat1_ghrsst_ncei_avhrr_anl_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export sat1_ghrsst_ncei_avhrr_anl_fhr_max="$(echo $($NHOUR ${vPDY}${sat1_ghrsst_ncei_avhrr_anl_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
sat1_ghrsst_ospo_geopolar_anl_check_vhour="00"
sat1_ghrsst_ospo_geopolar_anl_fhr_max_idate="$($NDATE -${sat1_ghrsst_ospo_geopolar_anl_fhr_max} ${vPDY}${sat1_ghrsst_ospo_geopolar_anl_check_vhour})"
if [ $sat1_ghrsst_ospo_geopolar_anl_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export sat1_ghrsst_ospo_geopolar_anl_fhr_max="$(echo $($NHOUR ${vPDY}${sat1_ghrsst_ospo_geopolar_anl_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi

echo

## Output set up
export jobid=${jobid:-${job}.${pid}}
export OUTPUTROOT=${DATA}
mkdir -p $DATA
cd $DATA

if [[ "$machine" =~ ^(URSA|HERA|ORION|WCOSS2|HERCULES|GAEAC6)$ ]]; then
   echo
else
    echo "ERROR: $machine is not a supported machine"
    exit 1
fi

## Environment variables
if [ $machine = "ORION" ]; then
    export CUT=$(which cut | sed 's/cut is //g')
    export TR=$(which tr | sed 's/tr is //g')
    export CONVERT=$(which convert | sed 's/convert is //g')
    export NCDUMP=$(which ncdump | sed 's/ncdump is //g')
    export NCEA=$(which ncea | sed 's/ncea is //g')
    export HTAR="/null/htar"
else
    export CUT=$(which cut)
    export TR=$(which tr)
    export CONVERT=$(which convert)
    export NCDUMP=$(which ncdump)
    export NCEA=$(which ncea)
    export HTAR=$(which htar)
fi
export HOMEMET_bin_exec="bin"
export HOMEMET=${met_ROOT:-${MET_ROOT:?met_ROOT is undefined!}}
export HOMEMETplus=${metplus_ROOT:-${METPLUS_ROOT:?metplus_ROOT is undefined!}}
echo "Using HOMEMET=${HOMEMET}"
echo "Using HOMEMETplus=${HOMEMETplus}"

## Account and queues for machines
export ACCOUNT=${ACCOUNT:-"GFS-DEV"}
export QUEUE=${QUEUE:-"dev"}
export QUEUESHARED=${QUEUE_SHARED:-"dev_shared"}
export QUEUESERV=${QUEUE_SERVICE:-"dev_transfer"}
export PARTITION_BATCH=${PARTITION_BATCH:-""}
export CLUSTERS_DTN=${CLUSTERS_DTN:-""}
export PARTITION_DTN=${PARTITION_DTN:-""}

## Run settings for machines
export MPMD="YES"
export nproc=${nproc:-1}

## Set paths for verif_global, MET, and METplus
export HOMEverif_global=$HOMEverif_global
export PARMverif_global=$HOMEverif_global/parm
export FIXverif_global=$FIXglobal/verif
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
if [[ ${machine} == "HERA" || ${machine} == "URSA" ]]; then
    export global_archive="/scratch3/NCEPDEV/global/role.glopara/data/metplus.data/archive"
    export prepbufr_arch_dir="/scratch3/NCEPDEV/global/role.glopara/data/metplus.data/prepbufr"
    export ccpa_24hr_arch_dir="/scratch3/NCEPDEV/global/role.glopara/data/metplus.data/obdata/ccpa_accum24hr"
elif [ $machine = "ORION" -o $machine = "HERCULES" ]; then
    export global_archive="/work2/noaa/global/role-global/data/metplus.data/archive"
    export prepbufr_arch_dir="/work2/noaa/global/role-global/data/metplus.data/prepbufr"
    export ccpa_24hr_arch_dir="/work2/noaa/global/role-global/data/metplus.data/obdata/ccpa_accum24hr"
elif [ $machine = "WCOSS2" ]; then
    export global_archive="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/model_data"
    export prepbufr_arch_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data/prepbufr"
    export ccpa_24hr_arch_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data/ccpa_accum24hr"
elif [ $machine = "GAEAC6" ]; then
    export global_archive="/gpfs/f6/drsa-precip3/world-shared/role.glopara/data/metplus.data/archive"
    export prepbufr_arch_dir="/gpfs/f6/drsa-precip3/world-shared/role.glopara/data/metplus.data/prepbufr"
    export ccpa_24hr_arch_dir="/gpfs/f6/drsa-precip3/world-shared/role.glopara/data/metplus.data/obdata/ccpa_accum24hr"
fi

## Set operational directories
export prepbufr_prod_upper_air_dir="/lfs/h1/ops/prod/com/obsproc/${obsproc_ver}"
export prepbufr_prod_conus_sfc_dir="/lfs/h1/ops/prod/com/obsproc/${obsproc_ver}"
export ccpa_24hr_prod_dir="/lfs/h1/ops/prod/com/verf_precip/${verf_precip_ver}"

## Some online sites
export iabp_ftp="http://iabp.apl.washington.edu/Data_Products/Daily_Full_Res_Data"
export ghrsst_ncei_avhrr_anl_ftp="https://www.ncei.noaa.gov/data/oceans/ghrsst/L4/GLOB/NCEI/AVHRR_OI"
export ghrsst_ospo_geopolar_anl_ftp="https://www.ncei.noaa.gov/data/oceans/ghrsst/L4/GLOB/OSPO/Geo_Polar_Blended"

## Do checks on switches to run verification for
if [ $METPCASE = g2g1 ]; then
    RUN_GRID2OBS_STEP1=NO
    RUN_PRECIP_STEP1=NO
    RUN_SATELLITE_STEP1=NO
    emc_verif_switch_name="RUN_GRID2GRID_STEP1"
    export emc_verif_name="g2g1"
fi
if [ $METPCASE = g2o1 ]; then
    RUN_GRID2GRID_STEP1=NO
    RUN_PRECIP_STEP1=NO
    RUN_SATELLITE_STEP1=NO
    emc_verif_switch_name="RUN_GRID2OBS_STEP1"
    export emc_verif_name="g2o1"
fi
if [ $METPCASE = pcp1 ]; then
    RUN_GRID2GRID_STEP1=NO
    RUN_GRID2OBS_STEP1=NO
    RUN_SATELLITE_STEP1=NO
    emc_verif_switch_name="RUN_PRECIP_STEP1"
    export emc_verif_name="precip1"
fi
if [ $METPCASE = sat1 ]; then
    RUN_GRID2GRID_STEP1=NO
    RUN_GRID2OBS_STEP1=NO
    RUN_PRECIP_STEP1=NO
    emc_verif_switch_name="RUN_SATELLITE_STEP1"
    export emc_verif_name="sat1"
fi
if [ ${start_date}${cyc2run} -lt $SDATE_GFS_YYYYMMDDHH ]; then
    RUN_GRID2GRID_STEP1=NO
    RUN_GRID2OBS_STEP1=NO
    RUN_PRECIP_STEP1=NO
    RUN_SATELLITE_STEP1=NO
fi
# Cycle through forecast cycles. If any are valid, exit loop and do not change steps to run.
change_steps="NO"
for fcyc in $fcyc_list; do
    if [ ${start_date}${fcyc} -lt $SDATE_GFS_YYYYMMDDHH ]; then
        change_steps="YES"
    else
        change_steps="NO"
        break
    fi
done
if [ $change_steps = "YES" ] ; then
    RUN_GRID2GRID_STEP1=NO
    RUN_GRID2OBS_STEP1=NO
    RUN_PRECIP_STEP1=NO
    RUN_SATELLITE_STEP1=NO
fi
for precip1_type in $precip1_type_list; do
    precip1_accum_length=$(echo $precip1_type | sed 's/[^0-9]*//g')
    precip_back_hours=$((VRFYBACK_HRS + precip1_accum_length))
    precip_check_date="$(date --utc +%Y%m%d%H -d "${PDY} ${cyc} - ${precip_back_hours} hours")"
    if [ ${precip_check_date:0:8}${cyc2run} -lt $SDATE_GFS_YYYYMMDDHH ]; then
        RUN_PRECIP_STEP1=NO
    fi
    for fcyc in $fcyc_list; do
        if [ ${precip_check_date:0:8}${fcyc} -lt $SDATE_GFS_YYYYMMDDHH ]; then
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
if [ $RUN_SATELLITE_STEP1 = YES ] ; then
    echo
    echo "===== RUNNING SATELLITE STEP 1 VERIFICATION  ====="
    echo "===== creating partial sum data for satellite verifcation using METplus ====="
    export RUN="satellite_step1"
    $HOMEverif_global/scripts/exsatellite_step1.sh
fi
