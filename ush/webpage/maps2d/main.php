<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>Home</title>
<link href="http://fonts.googleapis.com/css?family=Source+Sans+Pro:200,300,400,600,700,900" rel="stylesheet" />
<link href="../main.css" rel="stylesheet" type="text/css" media="all" />
<link href="../fonts.css" rel="stylesheet" type="text/css" media="all" />
<script src="https://d3js.org/d3.v4.min.js"></script>
</head>

<?php
$randomtoken = base64_encode( openssl_random_pseudo_bytes(32));
$_SESSION['csrfToken']=$randomtoken;
?>

<?php include "2dplots_globalvars.php"; ?>

<body>
<li>
The daily average is computed from the 4 model forecast files that comprised the forecast day, ex. day 5 is the average of forecast hours 102, 108, 114, and 120. Then the average of the daily averages over the date span is plotted.
</li>
<br>
<li>
For model-to-model comparison, forecast files from the various models are used. All data are regridded using bilinear interpolation, if needed, to the <a href=http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid002.gif target="_blank">G002</a> (2.5x2.5 degree) grid. Average plotted values in the upper right of each plots are areal averages.
</li>
<br>
<li>
For model-to-obs comparison, forecast files from the various models are used. Different datasets can be used for different variables, and depending on data avaiabilty, monthly means or monthly climatologies are used. For cloud fractions, <a href="https://isccp.giss.nasa.gov/" target="_blank">ISCCP</a> or <a href="https://ceres.larc.nasa.gov/products.php?product=SYN1deg" target="_blank">CERES SYN1deg</a> are used as truth. For radiation, <a herf="https://gewex-srb.larc.nasa.gov/" target="_blank">SRB2</a> or <a href="https://ceres.larc.nasa.gov/products.php?product=SYN1deg" target="_blank">CERES SYN1deg</a> are used as truth. For precipitaion, <a herf="https://www.esrl.noaa.gov/psd/data/gridded/data.gpcp.html" target="_blank">GPCP</a> is used as truth. For precipitable water, <a herf="https://eosweb.larc.nasa.gov/project/nvap/nvap-m_table" target="_blank">NVAP</a> or <a href="https://ceres.larc.nasa.gov/products.php?product=SYN1deg" target="_blank">CERES SYN1deg</a> are used as truth. For cloud liquid water path, <a href="https://climatedataguide.ucar.edu/climate-data/liquid-water-path-lwp-uwisc-climatology">UWisc LWP Climatology</a> or <a href="https://ceres.larc.nasa.gov/products.php?product=SYN1deg" target="_blank">CERES SYN1deg</a> are used as truth. For 2 meter temperature, <a herf="https://climatedataguide.ucar.edu/climate-data/ghcn-global-historical-climatology-network-related-gridded-products" target="_blank">CPC GHCN_CAMS</a> analysis is used. All data are regridded using bilinear interpolation, if needed, to the <a href=http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid002.gif target="_blank">G002</a> (2.5x2.5 degree) grid. Average plotted values in the upper right of each plots are areal averages.
</li>
</body>
</html>
