#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Set up environment based on user configurations
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: set_up_verif_global.sh"

export NET="verif_global"
export RUN_ENVIR="emc"
export envir="dev"

## Output set up
if [ -d "$OUTPUTROOT" ] ; then
   echo "OUTPUTROOT ($OUTPUTROOT) ALREADY EXISTS"
   echo "OVERRIDE CURRENT OUTPUTROOT? [yes/no]"
   read override
   case "$override" in
       yes)
           echo "Removing current OUTPUTROOT and making new directory"
           rm -r $OUTPUTROOT
           mkdir -p $OUTPUTROOT
           ;;
       no)
           echo "Please set new OUTPUTROOT"
           exit
           ;;
       *)
           echo "$override is not a valid choice, please choose [yes or no]"
           exit
           ;;
   esac
else
   mkdir -p ${OUTPUTROOT}
fi
echo "Output will be in: $OUTPUTROOT"
export COMROOT="$OUTPUTROOT/com"
export NWGESROOT="$OUTPUTROOT/nwges"
export DCOMROOT="$OUTPUTROOT/dcom"
export PCOMROOT="$OUTPUTROOT/pcom"
export DATAROOT="$OUTPUTROOT/tmpnw${envir}"
export job=${job:-$LSB_JOBNAME}
export jobid=${jobid:-$$}
export DATA=${DATAROOT}/$NET.$jobid
mkdir -p $COMROOT $NWGESROOT $DCOMROOT $PCOMROOT $DATAROOT $DATA
mkdir -p $COMROOT/$NET/$envir
mkdir -p $COMROOT/logs/jlogfiles
mkdir -p $COMROOT/output/$envir/today
mkdir -p $COMROOT/output/$envir/$(date +%Y%m%d)
export DCOM=${DCOM:-$DCOMROOT/$NET}
export PCOM=${PCOM:-$PCOMROOT/$NET}
export GESIN=${GESIN:-$GESROOT/$envir}
export GESOUT=${GESOUT:-$GESROOT/$envir}
mkdir -p $DCOM $PCOM
cd $DATA
echo

## Get machine
python $HOMEverif_global/ush/get_machine.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran get_machine.py"
echo

if [ -s config.machine ]; then
    . $DATA/config.machine
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Succesfully sourced config.machine"
    echo
fi

## Load modules and set machine specific variables
if [ $machine != "HERA" -a $machine != "WCOSS_C" -a $machine != "WCOSS_DELL_P3" ]; then
    echo "ERROR: $machine is not supported"
    exit 1
fi

. $HOMEverif_global/ush/load_modules.sh $machine $MET_version $METplus_version
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully loaded modules"
echo

## Account and queues for machines
if [ $machine = "HERA" ]; then
    export ACCOUNT="fv3-cpu"
    export QUEUE="batch"
    export QUEUESHARED="batch"
    export QUEUESERV="service"
elif [ $machine = "WCOSS_C" -o $machine = "WCOSS_DELL_P3" ]; then
    export ACCOUNT="GFS-DEV"
    export QUEUE="dev"
    export QUEUESHARED="dev_shared"
    export QUEUESERV="dev_transfer"
fi

## Run settings for machines
if [ $machine = "HERA" ]; then
    export nproc="40"
    export MPMD="YES"
elif [ $machine = "WCOSS_C" ]; then
    export nproc="24"
    export MPMD="YES"
elif [ $machine = "WCOSS_DELL_P3" ]; then
    export nproc="28"
    export MPMD="YES"
fi

## Get fix directory
if [ $machine = "HERA" ]; then
    export FIXverif_global="/scratch1/NCEPDEV/global/glopara/fix/fix_verif"
elif [ $machine = "WCOSS_C" ] ; then
    export FIXverif_global="/gpfs/hps3/emc/global/noscrub/emc.glopara/git/fv3gfs/fix/fix_verif"
elif [ $machine = "WCOSS_DELL_P3" ]; then
    export FIXverif_global="/gpfs/dell2/emc/modeling/noscrub/emc.glopara/git/fv3gfs/fix/fix_verif"
fi

## Installations for verif_global, met, and METplus
export HOMEverif_global=$HOMEverif_global
export PARMverif_global=$HOMEverif_global/parm
export USHverif_global=$HOMEverif_global/ush
export UTILverif_global=$HOMEverif_global/util
export EXECverif_global=$HOMEverif_global/exec
export HOMEMET=$HOMEMET
export HOMEMETplus=$HOMEMETplus
export PARMMETplus=$HOMEMETplus/parm
export USHMETplus=$HOMEMETplus/ush
export PATH="${USHMETplus}:${PATH}"
export PYTHONPATH="${USHMETplus}:${PYTHONPATH}"

## Machine and user specific paths
if [ $machine = "HERA" ]; then
    export NWROOT="/scratch1/NCEPDEV/global/glopara/nwpara"
    export HOMEDIR="/scratch1/NCEPDEV/global/$USER"
    export STMP="/scratch1/NCEPDEV/stmp2/$USER"
    export PTMP="/scratch1/NCEPDEV/stmp4/$USER"
    export NOSCRUB="/scratch1/NCEPDEV/global/$USER"
    export gstat="/scratch1/NCEPDEV/global/Fanglin.Yang/stat"
    export prepbufr_arch_dir="/scratch1/NCEPDEV/global/Fanglin.Yang/stat/prepbufr"
    export ccpa_24hr_arch_dir="/scratch1/NCEPDEV/global/Mallory.Row/obdata/ccpa_accum24hr"
    export WGRIB="/apps/grads/2.0.2/bin/wgrib"
    export WGRIB2="/apps/wgrib2/2.0.8/intel/18.0.3.222/bin/wgrib2"
    export CNVGRIB="/apps/cnvgrib/1.4.0/bin/cnvgrib"
    export trak_arch_dir="/scratch1/NCEPDEV/global/Mallory.Row/trak/abdeck"
elif [ $machine = "WCOSS_C" ]; then
    export NWROOT=${NWROOT:-"/gpfs/hps/nco/ops/nwprod"}
    export HOMEDIR="/gpfs/hps3/emc/global/noscrub/$USER"
    export STMP="/gpfs/hps2/stmp/$USER"
    export PTMP="/gpfs/hps2/ptmp/$USER"
    export NOSCRUB="/gpfs/hps3/emc/global/noscrub/$USER"
    export gstat="/gpfs/hps3/emc/global/noscrub/Fanglin.Yang/stat"
    export prepbufr_arch_dir="/gpfs/hps3/emc/global/noscrub/Fanglin.Yang/prepbufr"
    export ccpa_24hr_arch_dir="/gpfs/hps3/emc/global/noscrub/Mallory.Row/obdata/ccpa_accum24hr"
    export trak_arch_dir="/gpfs/hps3/emc/hwrf/noscrub/emc.hurpara/trak/abdeck"
elif [ $machine = "WCOSS_DELL_P3" ]; then
    export NWROOT=${NWROOT:-"/gpfs/dell1/nco/ops/nwprod"}
    export HOMEDIR="/gpfs/dell2/emc/modeling/noscrub/$USER"
    export STMP="/gpfs/dell3/stmp/$USER"
    export PTMP="/gpfs/dell3/ptmp/$USER"
    export NOSCRUB="/gpfs/dell2/emc/modeling/noscrub/$USER"
    export gstat="/gpfs/dell2/emc/modeling/noscrub/Fanglin.Yang/stat"
    export prepbufr_arch_dir="/gpfs/dell2/emc/modeling/noscrub/Fanglin.Yang/prepbufr"
    export ccpa_24hr_arch_dir="/gpfs/dell2/emc/verification/noscrub/Mallory.Row/obdata/ccpa_accum24hr"
    export trak_arch_dir="/gpfs/hps3/emc/hwrf/noscrub/emc.hurpara/trak/abdeck"
fi

## Some operational directories
export prepbufr_prod_upper_air_dir="/gpfs/dell1/nco/ops/com/gfs/prod" 
export prepbufr_prod_conus_sfc_dir="/gpfs/dell1/nco/ops/com/nam/prod"
export ccpa_24hr_prod_dir="/gpfs/dell1/nco/ops/com/verf/prod"
export nhc_atcfnoaa_bdeck_dir="/gpfs/dell2/nhc/noscrub/data/atcf-noaa/btk"
export nhc_atcfnoaa_adeck_dir="/gpfs/dell2/nhc/noscrub/data/atcf-noaa/aid_nws"
export nhc_atcfnavy_bdeck_dir="/gpfs/dell2/nhc/noscrub/data/atcf-navy/btk"
export nhc_atcfnavy_adeck_dir="/gpfs/dell2/nhc/noscrub/data/atcf-navy/aid"

## Some online sites
export nhc_atcf_bdeck_ftp="ftp://ftp.nhc.noaa.gov/atcf/btk/"
export nhc_atcf_adeck_ftp="ftp://ftp.nhc.noaa.gov/atcf/aid_public/"
export nhc_atfc_arch_ftp="ftp://ftp.nhc.noaa.gov/atcf/archive/"
export navy_atcf_bdeck_ftp="https://www.metoc.navy.mil/jtwc/products/best-tracks/"

echo "END: set_up_verif_global.sh"
