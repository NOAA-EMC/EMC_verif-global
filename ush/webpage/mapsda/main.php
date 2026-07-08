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

<body>
<li>
Analysis plots are created from GDAS analysis and first guess (6-hr forecast from last GDAS cycle). All data are regridded using bilinear interpolation, if needed, to the <a href=http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid002.gif target="_blank">G002</a> (2.5x2.5 degree) grid. Average plotted values in the upper right of each plots are areal averages.
</li>
<br>
<li>
Ensemble plots are created from the model ensemble mean and spread files. All data are regridded using bilinear interpolation, if needed, to the <a href=http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid002.gif target="_blank">G002</a> (2.5x2.5 degree) grid. Average plotted values in the upper right of each plots are areal averages.
</li>
</body>
</html>
