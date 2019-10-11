#!/bin/sh -xe
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
if [ $machine = WCOSS_C ]; then
    source /opt/modules/default/init/sh
    module use /usrx/local/prod/modulefiles
    module use /usrx/local/dev/modulefiles
    module load xt-lsfhpc/9.1.3 
    module load alps 
    module load cfp-intel-sandybridge/1.1.0 
    module load prod_util 
    #module load prod_envir 
    module load grib_util/1.1.0 
    module load util_shared/1.0.7 
    module load nco-gnu-sandybridge/4.4.4 
    module load NetCDF-intel-sandybridge/4.2 
    module load hpss 
    module load python/2.7.14 
    if [ $MET_version = 6.1 -o $MET_version = 8.1 ]; then
        module load met/$MET_version 
        export HOMEMET="/usrx/local/dev/met/${MET_version}"
    elif [ $MET_version = 7.0 -o $MET_version = 8.0 ]; then
        module use /gpfs/hps3/emc/global/noscrub/Julie.Prestopnik/modulefiles 
        module load met/$MET_version 
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
    source /usrx/local/prod/lmod/lmod/init/sh
    module load EnvVars/1.0.2
    module load lsf/10.1 
    module load ips/18.0.1.163 
    module load impi/18.0.1 
    module load prod_util/1.1.0 
    #module load prod_envir/1.0.2 
    module load grib_util/1.0.6 
    module load NCO/4.7.0 
    module load NetCDF/4.5.0
    module load HPSS/5.0.2.5  
    module load CFP/2.0.1
    module use /usrx/local/dev/modulefiles
    module load python/2.7.14
    module load imagemagick/6.9.9-25 
    if [ $MET_version = 8.1 ]; then
        module load met/$MET_version 
        export HOMEMET="/usrx/local/dev/packages/met/${MET_version}"
    elif [ $MET_version = 7.0 -o $MET_version = 8.0 ]; then
        module use /gpfs/dell2/emc/verification/noscrub/Julie.Prestopnik/modulefiles 
        module load met/$MET_version 
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
    source /apps/lmod/lmod/init/sh
    module use /scratch4/NCEPDEV/global/save/glopara/git/NCEPLIBS-prod_util/modulefiles 
    module use /contrib/modulefiles
    module load intel/16.1.150 
    module load impi/5.1.2.150
    module load contrib 
    module load prod_util/v1.1.0_slurm 
    module load netcdf 
    module load nco 
    module load wgrib2 
    module load hpss/hpss 
    module load anaconda/anaconda2-4.4.0 
    if [ $MET_version = 6.1 -o $MET_version = 7.0 -o $MET_version = 8.0 -o $MET_version = 8.1 ]; then
        module load met/$MET_version 
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
elif [ $machine = HERA ]; then
    source /apps/lmod/lmod/init/sh
    #module use /scratch1/NCEPDEV/global/gwv/l819/lib/modulefiles
    #export NCEPLIBS=/scratch1/NCEPDEV/global/gwv/l819/lib
    #module load prod_util/v1.1.0
    module use /scratch2/NCEPDEV/nwprod/NCEPLIBS/modulefiles
    module use /contrib/modulefiles
    module load intel
    module load impi
    module load contrib
    module load prod_util/1.1.0
    module load netcdf
    module load nco
    module load wgrib2
    module load hpss/hpss
    module load anaconda/anaconda2-4.4.0
    if [ $MET_version = 7.0 -o $MET_version = 8.0 -o $MET_version = 8.1 ]; then
        module load met/$MET_version
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
export CONVERT=`which convert`
echo "Using HOMEMET=${HOMEMET}"
echo "Using HOMEMETplus=${HOMEMETplus}"

echo "END: load_modules.sh"

module list
