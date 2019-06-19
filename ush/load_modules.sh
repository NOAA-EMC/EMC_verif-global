#!/bin/sh
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Load necessary modules
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

machine=${1}
MET_version=${2}
METplus_version=${3}

echo "BEGIN: load_modules.sh"

## Check versions are supported in verif_global
if [[ "$MET_version" =~ ^(6.1|7.0|8.0|8.1)$ ]]; then
    echo "Requested MET version: $MET_version"
else
    echo "ERROR: $MET_version is not supported in verif_global"
    exit 1
fi
if [[ "$METplus_version" =~ ^(2.1)$ ]]; then
    echo "Requested METplus version: $METplus_version"
else
    echo "ERROR: $METplus_version is not supported in verif_global"
    exit 1
fi

## Load
#module purge 2>>/dev/null
if [ $machine = WCOSS_C ]; then
    module use /usrx/local/prod/modulefiles
    module use /usrx/local/dev/modulefiles
    module load xt-lsfhpc/9.1.3 2>>/dev/null
    module load alps 2>>/dev/null
    module load cfp-intel-sandybridge/1.1.0 2>>/dev/null
    module load prod_util 2>>/dev/null
    #module load prod_envir 2>>/dev/null
    module load grib_util/1.0.5 2>>/dev/null
    module load util_shared/1.0.7 2>>/dev/null
    module load nco-gnu-sandybridge/4.4.4 2>>/dev/null
    module load NetCDF-intel-sandybridge/4.2 2>>/dev/null
    module load hpss 2>>/dev/null
    module load python/2.7.14 2>>/dev/null
    if [ $MET_version = 6.1 -o $MET_version = 8.1 ]; then
        module load met/$MET_version 2>>/dev/null
        export HOMEMET="/usrx/local/dev/met/${MET_version}"
    elif [ $MET_version = 7.0 -o $MET_version = 8.0 ]; then
        module use /gpfs/hps3/emc/global/noscrub/Julie.Prestopnik/modulefiles 2>>/dev/null
        module load met/$MET_version 2>>/dev/null
        export HOMEMET="/gpfs/hps3/emc/global/noscrub/Julie.Prestopnik/met/${MET_version}"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 2.1 ]; then
        module load metplus/2.1
        export HOMEMETplus="/usrx/local/dev/met/METplus/METplus-$METplus_version"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
elif [ $machine = WCOSS_DELL_P3 ]; then
    module use /usrx/local/prod/modulefiles
    module use /usrx/local/dev/modulefiles
    module load EnvVar/1.0.2 2>>/dev/null
    module load lsf/10.1 2>>/dev/null
    module load ips/18.0.1.163 2>>/dev/null
    module load impi/18.0.1 2>>/dev/null
    module load prod_util/1.1.0 2>>/dev/null
    #module load prod_envir/1.0.2 2>>/dev/null
    module load grib_util/1.0.6 2>>/dev/null
    module load NCO/4.7.0 2>>/dev/null
    module load NetCDF/4.5.0 2>>/dev/null
    module load HPSS/5.0.2.5 2>>/dev/null
    module load python/2.7.14 2>>/dev/null
    module load CFP/2.0.1 2>>/dev/null
    module unload ips 2>>/dev/null
    if [ $MET_version = 8.1 ]; then
        module load met/$MET_version 2>>/dev/null
        export HOMEMET="/usrx/local/dev/met/${MET_version}"
    elif [ $MET_version = 7.0 -o $MET_version = 8.0 ]; then
        module use /gpfs/dell2/emc/verification/noscrub/Julie.Prestopnik/modulefiles 2>>/dev/null
        module load met/$MET_version 2>>/dev/null
        export HOMEMET="/gpfs/dell2/emc/verification/noscrub/Julie.Prestopnik/met/${MET_version}"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 2.1 ]; then
        module load metplus/2.1
        export HOMEMETplus="/usrx/local/dev/packages/met/METplus/METplus-$METplus_version"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
elif [ $machine = THEIA ]; then
    module use /scratch4/NCEPDEV/global/save/glopara/git/NCEPLIBS-prod_util/modulefiles 2>>/dev/null
    module use /contrib/modulefiles 2>>/dev/null
    module load impi/5.1.2.150 2>>/dev/null
    module load prod_util/v1.1.0_slurm 2>>/dev/null
    module load netcdf 2>>/dev/null
    module load nco 2>>/dev/null
    module load wgrib2 2>>/dev/null
    module load hpss/hpss 2>>/dev/null
    module load anaconda/anaconda2-4.4.0 2>>/dev/null
    if [ $MET_version = 6.1 -o $MET_version = 7.0 -o $MET_version = 8.0 -o $MET_version = 8.1 ]; then
        module load met/$MET_version 2>>/dev/null
        export HOMEMET="/contrib/met/${MET_version}"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 2.1 ]; then
        export HOMEMETplus="/contrib/METplus/METplus-$METplus_version"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    module switch anaconda/anaconda2
else
    echo "ERROR: $machine is not supported"
    exit 1
fi
export NCAP2=`which ncap2`
export NCDUMP=`which ncdump`
export HTAR=`which htar`
echo "Using HOMEMET=${HOMEMET}"
echo "Using HOMEMETplus=${HOMEMETplus}"

echo "END: load_modules.sh"
