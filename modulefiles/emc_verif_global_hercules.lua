help([[
Load environment to run EMC_verif-global on Hercules using GNU compiler stack.
]])

prepend_path("MODULEPATH", "/apps/contrib/spack-stack/spack-stack-2.0.0/envs/ue-gcc-12.2.0/modules/Core")

stack_gcc_ver=os.getenv("stack_gcc_ver") or "12.2.0"
load(pathJoin("stack-gcc", stack_gcc_ver))

stack_openmpi_ver=os.getenv("stack_openmpi_ver") or "4.1.4"
load(pathJoin("stack-openmpi", stack_openmpi_ver))

python_ver=os.getenv("python_ver") or "3.11.11"
load(pathJoin("python", python_ver))

prod_util_ver=os.getenv("prod_util_ver") or "2.1.2"
load(pathJoin("prod_util", prod_util_ver))

grib_util_ver=os.getenv("grib_util_ver") or "1.4.0"
load(pathJoin("grib-util", grib_util_ver))

netcdf_c_ver=os.getenv("netcdf_c_ver") or "4.9.2"
load(pathJoin("netcdf-c", netcdf_c_ver))

nco_ver=os.getenv("nco_ver") or "5.3.3"
load(pathJoin("nco", nco_ver))

grads_ver=os.getenv("grads_ver") or "2.2.3"
load(pathJoin("grads", grads_ver))

imagemagick_ver=os.getenv("imagemagick_ver") or "7.1.1-29"
load(pathJoin("imagemagick", imagemagick_ver))

met_ver=os.getenv("met_ver") or "12.0.1"
load(pathJoin("met", met_ver))

metplus_ver=os.getenv("metplus_ver") or "6.0.0"
load(pathJoin("metplus", metplus_ver))

matplotlib_ver=os.getenv("matplotlib_ver") or "3.7.4"
load(pathJoin("py-matplotlib", matplotlib_ver))

cartopy_ver=os.getenv("cartopy_ver") or "0.24.1"
load(pathJoin("py-cartopy", cartopy_ver))
