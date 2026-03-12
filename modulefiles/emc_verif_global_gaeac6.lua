help([[
Load environment to run EMC_verif-global on Gaea-C6 using Intel
]])

prepend_path("MODULEPATH", "/ncrc/proj/epic/spack-stack/c6/spack-stack-2.0.0/envs/ue-oneapi-2025.2.1/modules/Core")

stack_oneapi_ver=os.getenv("stack_oneapi_ver") or "2025.2.1"
load(pathJoin("stack-intel-oneapi-compilers", stack_oneapi_ver))

python_ver=os.getenv("python_ver") or "3.11.11"
load(pathJoin("python", python_ver))

Core_ver=os.getenv("Core_ver") or "24.11"
load(pathJoin("Core", Core_ver))

prod_util_ver=os.getenv("prod_util_ver") or "2.1.2"
load(pathJoin("prod_util", prod_util_ver))

stack_cray_mpich_ver=os.getenv("stack_cray_mpich_ver") or "8.1.32"
load(pathJoin("stack-cray-mpich", stack_cray_mpich_ver))

netcdf_c_ver=os.getenv("netcdf_c_ver") or "4.9.2"
load(pathJoin("netcdf-c", netcdf_c_ver))

grads_ver=os.getenv("grads_ver") or "2.2.3"
load(pathJoin("grads", grads_ver))

imagemagick_ver=os.getenv("imagemagick_ver") or "7.1.1-29"
load(pathJoin("imagemagick", imagemagick_ver))

jasper_ver=os.getenv("jasper_ver") or "4.2.4"
load(pathJoin("jasper", jasper_ver))

udunits_ver=os.getenv("udunits_ver") or "2.2.28"
load(pathJoin("udunits", udunits_ver))

grib_util_ver=os.getenv("grib_util_ver") or "1.4.0"
load(pathJoin("grib-util", grib_util_ver))

wgrib2_ver=os.getenv("wgrib2_ver") or "3.6.0"
load(pathJoin("wgrib2", wgrib2_ver))

nco_ver=os.getenv("nco_ver") or "5.3.3"
load(pathJoin("nco", nco_ver))

met_ver=os.getenv("met_ver") or "12.0.1"
load(pathJoin("met", met_ver))

metplus_ver=os.getenv("metplus_ver") or "6.0.0"
load(pathJoin("metplus", metplus_ver))

bufr_ver=os.getenv("bufr_ver") or "12.1.0"
load(pathJoin("bufr", bufr_ver))

cdo_ver=os.getenv("cdo_ver") or "2.5.2"
load(pathJoin("cdo", cdo_ver))

matplotlib_ver=os.getenv("matplotlib_ver") or "3.7.4"
load(pathJoin("py-matplotlib", matplotlib_ver))

cartopy_ver=os.getenv("cartopy_ver") or "0.24.1"
load(pathJoin("py-cartopy", cartopy_ver))
