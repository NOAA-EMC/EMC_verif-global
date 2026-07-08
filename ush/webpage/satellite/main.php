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
Regular partial sums are computed for each model (see <a href="https://met.readthedocs.io/en/latest/Users_Guide/appendixC.html#partial-sums-lines-sl1l2-sal1l2-vl1l2-val1l2" target="_blank">here</a>). Each model's forecast are verified against the given satellite. Information on the GHRSST NCEI AVHRR Analysis dataset can be found <a href="https://podaac.jpl.nasa.gov/dataset/AVHRR_OI-NCEI-L4-GLOB-v2.1?ids=Keywords:Processing%20Levels&values=Oceans:Ocean%20Temperature:Sea%20Surface%20Temperature::4%20-%20Gridded%20Model%20Output" target="_blank">here</a>. Information on the GHRSST OSPO Geo-Polar Analysis dataset can be found <a href="https://podaac.jpl.nasa.gov/dataset/Geo_Polar_Blended-OSPO-L4-GLOB-v1.0?ids=Keywords:Processing%20Levels&values=Oceans:Ocean%20Temperature:Sea%20Surface%20Temperature::4%20-%20Gridded%20Model%20Output" target="_blank"></a>.
</li>
<br>
<li>
Verification statistics are computed from the regular partial sums. The equations used to calculate the verification statistics can be found <a href="https://www.emc.ncep.noaa.gov/users/verification/global/gfs/doc/RMSE_decomposition.pdf" target="_blank">here</a>. Statistical signifance is calculated using a student-t test.
</li>
<br>
<li>
The verification regions used are are:
                     <a href="../images/vx_masks/G002.png" target="_blank">Global</a>,
                     <a href="../images/vx_masks/NH.png" target="_blank">N. Hemisphere</a>: 20N-90N,
                     <a href="../images/vx_masks/SH.png" target="_blank">S. Hemisphere</a>: 20S-90S,
                     <a href="../images/vx_masks/POLAR.png" target="_blank">Polar</a>: 60S-90S and 60N-90N, and
                     <a href="../images/vx_masks/ARCTIC.png" target="_blank">Arctic</a>.
Sea ice and sea ice free regions are determined from the sea ice fraction from the satellite or satellite analysis dataset.
</li>
</body>
</html>
