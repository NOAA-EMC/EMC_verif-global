#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Load necessary modules
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: load_modules.sh"

## Check versions are supported in verif_global
if [[ "$MET_version" =~ ^(9.1)$ ]]; then
    echo "Requested MET version: $MET_version"
else
    echo "ERROR: $MET_version is not supported in verif_global"
    exit 1
fi
if [[ "$METplus_version" =~ ^(3.1)$ ]]; then
    echo "Requested METplus version: $METplus_version"
else
    echo "ERROR: $METplus_version is not supported in verif_global"
    exit 1
fi

## Load
if [ $machine = WCOSS2 ]; then
    source /usr/share/lmod/lmod/init/sh
    module reset
    source ${HOMEverif_global}/versions/run.ver
    export HPC_OPT=/apps/ops/para/libs
    module use ${HOMEverif_global}/modulefiles
    module load emc_verif_global_wcoss2
    if [ $MET_version = 9.1 ]; then
        export HOMEMET="$MET_ROOT"
        export HOMEMET_bin_exec="bin"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
elif [ $machine = HERA ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    module use ${HOMEverif_global}/modulefiles
    module load emc_verif_global_hera
    if [ $MET_version = 9.1 ]; then
        export HOMEMET="/contrib/met/9.1"
        export HOMEMET_bin_exec="bin"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
elif [ $machine = ORION ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    module use ${HOMEverif_global}/modulefiles
    module load emc_verif_global_orion
    if [ $MET_version = 9.1 ]; then
        export HOMEMET="/apps/contrib/MET/9.1"
        export HOMEMET_bin_exec="bin"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    module load python/3.7.5
elif [ $machine = HERCULES ]; then
    "ERROR: EMC_Verif-Global standalone not supported on $machine"
    exit 1
elif [ $machine = S4 ]; then
    source /usr/share/lmod/lmod/init/sh
    module purge
    if [ $MET_version = 9.1 ]; then
        export HOMEMET="/data/prod/glopara/contrib/MET/met-9.1.3"
        export HOMEMET_bin_exec="bin"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        export HOMEMETplus="/data/prod/glopara/contrib/METplus/METplus-3.1.1"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    module use ${HOMEverif_global}/modulefiles
    module load emc_verif_global_s4
elif [ $machine = JET ]; then
    source /apps/lmod/lmod/init/sh
    module use ${HOMEverif_global}/modulefiles
    module load emc_verif_global_jet
    if [ $MET_version = 9.1 ]; then
        export HOMEMET="/contrib/met/9.1"
        export HOMEMET_bin_exec="bin"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
else
    echo "ERROR: $machine is not supported"
    exit 1
fi
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
    elif [ $machine == "JET" -o $machine == "WCOSS2" -o $machine == "HERA" ]; then
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

echo "Using HOMEMET=${HOMEMET}"
echo "Using HOMEMETplus=${HOMEMETplus}"

echo "END: load_modules.sh"

module list
