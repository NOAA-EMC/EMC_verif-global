#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: David Huber, david.huber@noaa.gov, NOAA/NWS/NCEP/EMC
## PURPOSE: Load necessary modules
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: load_modules.sh"

## Check versions are supported in verif_global
if [[ "$MET_version" =~ ^(12.0.1)$ ]]; then
    echo "Requested MET version: $MET_version"
else
    echo "ERROR: $MET_version is not supported in verif_global"
    exit 1
fi

if [[ "$METplus_version" =~ ^(6.0.0)$ ]]; then
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
elif [ $machine = HERA ]; then
    source /apps/lmod/lmod/init/sh
    module purge
elif [ $machine = URSA ]; then
    source /apps/lmod/lmod/init/sh
    module purge
elif [ $machine = ORION ]; then
    source /apps/other/lmod/lmod/init/sh
    module purge
elif [ $machine = HERCULES ]; then
    source /apps/other/lmod/lmod/init/sh
    module purge
elif [ $machine = GAEAC6 ]; then
    module reset
else
    echo "ERROR: $machine is not supported"
    exit 1
fi

_machine=${machine,,}

module use "${HOMEverif_global}/modulefiles"
module load "emc_verif_global_${_machine}"

# spack-stack 2.0.0 uses these env vars
MET_ROOT=${MET_ROOT:-${met_ROOT}}
METPLUS_PATH=${METPLUS_PATH:-${metplus_ROOT}}

export HOMEMET="$MET_ROOT"
export HOMEMET_bin_exec="bin"
export HOMEMETplus="${METPLUS_PATH}"

for cmd in rm cut tr ncap2 convert ncdump ncea htar; do
    # Check if the command exists. If not, set ${cmd^^} to /null/${cmd}
    if ! command -v $cmd &> /dev/null; then
        export ${cmd^^}="/null/$cmd"
    else
        export ${cmd^^}=$(which $cmd)
    fi
done

echo "Using HOMEMET=${HOMEMET}"
echo "Using HOMEMETplus=${HOMEMETplus}"

echo "END: load_modules.sh"

module list
