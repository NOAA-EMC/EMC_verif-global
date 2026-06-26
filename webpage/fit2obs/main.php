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
The fit files are produced as part of each data assimilation cycle and partial sums are collected and archived. Each set of fit files is grouped by observation types (ADPUPA, ADPSFC, AIRCAR, AIRCFT, and SFCSHP). It is verified for valid times at 00Z, 06Z, 12Z, and 18Z.
</li>
<br>
<li>
Calculation of fits is with respect to  observations from GDAS prepbufr files and interpolated background analysis/forecast products from the atmospheric nemsio files.
</li>
<br>
<li>
Each set of backgrounds within are lagged forecasts all verifying at the valid time.
</li>
<br>
<li>
The calculation of fit files needs backgrounds from analysis (00,06) and forecast (12…126 by 12).
</li>
<br>
<li>
The verification regions used are:
     Global, 
     N.Hemisphere (20N-80N),
     S. Hemisphere (20S-80S),
     Tropics (20S-20N),
     N. America (125W-65W,25N-55N),
     Europe (10W-25E,35N-70N), and 
     Asia (65E-145E,5N-45N).
</li>
</body>
</html>
