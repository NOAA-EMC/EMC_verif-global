#!/bin/sh
# Program Name: fit2obs_plots
# Author(s)/Contact(s): Mallory Row
# Abstract: Plot fit-to-obs data
# History Log:
#   08/2021: Initial version of script
#
# Usage:
#   Parameters:
#       agrument to script
#   Input Files:
#       file
#   Output Files:
#       file
#
# Condition codes:
#       0 - Normal exit
#
# User controllable options: None


set -x

export RUN_abbrev="$RUN"

# Set up directories
mkdir -p $RUN
cd $RUN

# Check user's configuration file
python $USHverif_global/check_config.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran check_config.py"
echo

# Load GrADS
if [ $machine = WCOSS_C ]; then
    module load GrADS/2.0.2 
elif [ $machine = WCOSS_DELL_P3 ]; then
    module load GrADS/2.2.0
elif [ $machine = HERA ]; then
    module load grads/2.2.1
elif [ $machine = ORION ]; then
    module load grads/2.2.1
elif [ $machine = JET ]; then
    module load grads/2.2.1
elif [ $machine = S4 ]; then
    module load grads/2.2.1
elif [ $machine = WCOSS2 ]; then
    module use /apps/test/lmodules/core
    module load GrADS/2.2.1
fi
if [ $machine = "ORION" ]; then
    export GRADS=$(which grads | sed 's/grads is //g')
else
    export GRADS=$(which grads)
fi
export GRADSBIN=$(dirname $GRADS)

# Set directories
export FITS=$(eval "pwd")
export tmpdir=$FITS/fit2obs
mkdir -p $tmpdir
export DATA=$FITS/data
mkdir -p $DATA
export mapdir=$tmpdir/web
mkdir -p $mapdir

# Set dates
DATEST=${start_date}
DATEND=${end_date}

# Set scrdir
export scrdir=${fit2obs_plots_scrdir}

# Misc
export logofile=${scrdir}/grads/nws_logo.png

# Set up
export oinc=${fit2obs_plots_oinc}
export finc=${fit2obs_plots_finc}
export fmax=${fit2obs_plots_fmax}
export endianlist=${fit2obs_plots_endianlist}
export expnlist=${fit2obs_plots_expnlist}
export expdlist=${fit2obs_plots_expdlist}
export cyc=${fit2obs_plots_cycle}
export rundir=$tmpdir/fit
export webmch=${webhost}
export webid=${webhostid}
export ftpdir=${webdir}
export doftp="NO"
export NWPROD=${NWPROD}
export ndate=${NDATE}
export IMGCONVERT=${CONVERT}
n=0 ; for runn in $endianlist ; do n=$((n+1)) ; endianname[n]=$runn ; done
n=0 ; for runn in $expnlist ; do n=$((n+1)) ; expname[n]=$runn ; done
n=0 ; for runn in $expdlist ; do n=$((n+1)) ; exppdir[n]=$runn ; done
n=0 ; for comp in $complist ; do n=$((n+1)) ; compname[n]=$comp  ; done
if [ -s $rundir ];  then rm -r ${rundir}/${expname[2]}; fi
mkdir -p ${rundir}/${expname[2]}
export sdate=${DATEST}${cyc}
export edate=${DATEND}${cyc}
n=1
while [ $n -le 2 ]; do
  fnltype=0
  CLIENT=${compname[n]}
  myclient=$(echo $CLIENT |cut -c 1-1 )
  exp=${expname[$n]}
  export exp$n=$exp                      
  export endian$n=${endianname[$n]}
  export dir$n=${exppdir[$n]}/$exp
n=$(expr $n + 1 )
done
export mctl=1
dotp=1
dovp=1
dohp=1
export tplots=$dotp
export tcplots=$dotp
export vcomp=$dovp
export vplots=$dovp
export vcplots=$dovp
export hcomp=$dohp
export hplots=$dohp
export web=0
export rzdmdir=${ftpdir}
export tmpfit=${rundir}/fits
cd $rundir
export FITDIR=${scrdir}
export tmpdir=${rundir}                 
export MSCRIPTS=$FITDIR/scripts
export PROUT=$tmpdir/$exp2/prout
if [ ! -d $PROUT ] ; then
  mkdir -p $PROUT
fi
export namstr="EMC/NCEP/NWS/NOAA"
export listvar1=exp1,exp2,sdate,edate,dir1,dir2,mctl,tplots,tcplots,vcomp,vplots,vcplots,hcomp,hplots,web,rzdmdir,webmch,webid,namstr,FITDIR,tmpdir,NWPROD,GRADSBIN,IMGCONVERT,mapdir,endian1,endian2
export list="$listvar"
export SCRIPTS=$FITDIR/scripts
export SORC=$FITDIR/sorc
export GSCRIPTS=$FITDIR/grads
export CTLS=$FITDIR/ctls
export ctldir=$tmpdir/$exp2/ctl
export PROUT=$tmpdir/$exp2/prout
export stnmap=${GRADSBIN}/stnmap
if [ ! -d $ctldir ] ; then
  mkdir -p $ctldir
fi
export vt2dir=$tmpdir/$exp2/vert
if [ ! -d $vt2dir ] ; then
  mkdir -p $vt2dir
fi
export vt1dir=$tmpdir/$exp2/vert/$exp1
if [ ! -d $vt1dir ] ; then
  mkdir -p $vt1dir
fi
export hz2dir=$tmpdir/$exp2/horiz
if [ ! -d $hz2dir ] ; then
  mkdir -p $hz2dir
fi
export hz1dir=$tmpdir/$exp2/horiz/$exp1
if [ ! -d $hz1dir ] ; then
  mkdir -p $hz1dir
fi
echo $sdate
export sdate12=$( $NDATE  12 $sdate)
export edate12=$( $NDATE -12 $edate)
yy=$(echo $sdate | cut -c1-4)
mm=$(echo $sdate | cut -c5-6)
dd=$(echo $sdate | cut -c7-8)
hh=$(echo $sdate | cut -c9-10)
mon=$($SCRIPTS/cmon.sh $mm)
hts00=${hh}z${dd}${mon}${yy}
echo "00z horiz plot start date $hts00"
nhours=$( $NHOUR $edate $sdate)
ndays=$(expr $nhours \/ 2)
echo "ndays is $ndays"
export perc=75
echo "perc is $perc"
export minday=$(expr $ndays \* $perc \/ 100)
echo "minday is $minday"
yy=$(echo $sdate12 | cut -c1-4)
mm=$(echo $sdate12 | cut -c5-6)
dd=$(echo $sdate12 | cut -c7-8)
hh=$(echo $sdate12 | cut -c9-10)
mon=$($SCRIPTS/cmon.sh $mm)
hts12=${hh}z${dd}${mon}${yy}
echo "12z horiz plot start date $hts12"
leglist='legf00af06_0z legf00af06_12z legf00af06 legf12af36 legf24af48'
cd $ctldir
exx1=$(echo $exp1|cut -c 1-4)
exx2=$(echo $exp2|cut -c 1-4)
for leg in $leglist
do
ifile=$GSCRIPTS/${leg}_proto
file=$leg
> tmp
/bin/cp $ifile tmp
sed "s/Exp1/$exx1/g" tmp | sed "s/Exp2/$exx2/g" > $file
cat $file
done

# Make vcomp plots
if [[ $vcomp -eq 1 ]] ; then
echo
echo "Running vcomp scripts"
for exp in $exp1 $exp2
do
if [ $exp = $exp1 ]; then
 export expdir=$dir1/fits
 export pvdir=$vt1dir
fi
if [ $exp = $exp2 ]; then
 export expdir=$dir2/fits
 export pvdir=$vt2dir
fi
cd $pvdir
incr=24
fcslist='00 06'
for fcshr in $fcslist
do
for cycle in 00z 12z
do
if [ $cycle = "00z" ] ; then
pss=$sdate
pse=$edate
fi
if [ $cycle = "12z" ] ; then
pss=$sdate12
pse=$edate12
fi
$SCRIPTS/suruplot2_lnx.sh $exp $fcshr $cycle $pss $pse $incr $pvdir $expdir
done
done
fcslist='12 24 36 48'
for fcshr in $fcslist
do
pss=$sdate
pse=$edate
if [ $fcshr = "12" ] ; then
pss=$sdate12
pse=$edate12
fi
if [ $fcshr = "36" ] ; then
pss=$sdate12
pse=$edate12
fi
$SCRIPTS/suruplot_lnx.sh $exp $fcshr $pss $pse $incr $pvdir $expdir
done
done
fi

# Make vplots plots
if [[ $vplots -eq 1 ]] ; then
echo
echo "Running vplots scripts"
for exp in $exp1 $exp2 ;  do
export exp
export ps00=$sdate
export pe00=$edate
export ps12=$sdate12
export pe12=$edate12
export pdir=$tmpdir/$exp2/maps/vert
export idir=$vt2dir
if [ $exp = $exp1 ] ; then
 export pdir=$tmpdir/$exp2/maps/vert/$exp1
 export idir=$vt1dir
fi
if [ ! -d $pdir ] ; then
  mkdir -p $pdir
fi
export webdir=$rzdmdir/fits/vert/$exp
export localdir=$mapdir/fits/vert/$exp
mkdir -p $localdir
echo "exp is $exp"
echo "pdir is $pdir"
echo "webdir is $webdir"
echo "idir is $idir"
$SCRIPTS/vertplot.new
done
fi

# Make vcplots plots
if [[ $vcplots -eq 1 ]] ; then
echo
echo "Running vcplots scripts"
fcstlist='1 2 3 4'
for fcst in $fcstlist
do
export idir1=$vt1dir
export idir2=$vt2dir
if [ $fcst = 1 ] ; then
export fcs1='00.00z'
export fcs2='06.00z'
export sdir=f00af06_0z
export psdate=$sdate
export pedate=$edate
fi
if [ $fcst = 2 ] ; then
export fcs1='00.12z'
export fcs2='06.12z'
export sdir=f00af06_12z
export psdate=$sdate12
export pedate=$edate12
fi
if [ $fcst = 3 ] ; then
export fcs1=12
export fcs2=36
export sdir=f${fcs1}af${fcs2}
export psdate=$sdate12
export pedate=$edate12
fi
if [ $fcst = 4 ] ; then
export fcs1=24
export fcs2=48
export sdir=f${fcs1}af${fcs2}
export psdate=$sdate
export pedate=$edate
fi
export pdir=$tmpdir/$exp2/maps/vert/$sdir
if [ ! -d $pdir ] ; then
  mkdir -p $pdir
fi
export webdir=$rzdmdir/fits/vert/${exp1}-${exp2}
export localdir=$mapdir/fits/vert/${exp1}-${exp2}
mkdir -p $localdir
$SCRIPTS/vertplot.cdas
done
fi

# Make time plots control files
if [[ $mctl -eq 1 ]] ; then
yy=$(echo $sdate | cut -c1-4)
mm=$(echo $sdate | cut -c5-6)
dd=$(echo $sdate | cut -c7-8)
mon=$($SCRIPTS/cmon.sh $mm)
timedate=${dd}${mon}${yy}
echo $timedate
typelist='raob sfc acar acft'
fcslist='00 06 12 24 36 48'
cd $ctldir
for exp in $exp1 $exp2
do
if [ $exp = $exp1 ]; then dir=$dir1/fits; fi
if [ $exp = $exp2 ]; then dir=$dir2/fits; fi
if [ $exp = $exp1 ]; then endian=${endian1:-big}; fi
if [ $exp = $exp2 ]; then endian=${endian2:-big}; fi
endnew=${endian}_endian
for type in $typelist
do
for fcs in $fcslist
do
name=f${fcs}.$type
ifile=$CTLS/${name}_proto.ctl
ofile=${exp}.${name}.ctl
> tmp
sed "s/date/$timedate/g" $ifile | sed "s?dir?$dir?g"  | sed "s?ENDIAN?$endnew?g"  > $ofile
done
cat $ofile
done
done
fi

# Make tplots plots
if [[ $tplots -eq 1 ]] ; then
echo
echo "Running tplots scripts"
for exp in timeout timevrt $exp1 $exp2
do
export exp exp1 exp2
export webdir=$rzdmdir/fits/time/$exp
export localdir=$mapdir/fits/time/$exp; mkdir -p $localdir
export ptdir=$tmpdir/$exp2/maps/time/$exp; mkdir -p $ptdir
if [ $exp = timeout ]; then
 export pdir=$ptdir;  mkdir -p $pdir; echo "exp is $exp"
 $SCRIPTS/timeout.newb
 continue
fi
if [ $exp = timevrt ]; then
 export pdir=$ptdir;  mkdir -p $pdir; echo "exp is $exp"
 $SCRIPTS/timevrt.newb
continue
fi
for var in tmp hgt wnd moi ps
do
export pdir=$ptdir/$var;  mkdir -p $pdir; echo "exp is $exp"
$SCRIPTS/time${var}.newb
done
export pdir=$ptdir/acar; mkdir -p $pdir
$SCRIPTS/timeacar.newb
export pdir=$ptdir/acft;  mkdir -p $pdir
$SCRIPTS/timeacft.newb
done
fi

# Make tcplots plots
if [[ $tcplots -eq 1 ]] ; then
echo
echo "Running tcplots scripts"
fcstlist='1 2 3'
for fcst in $fcstlist
do
if [ $fcst = 1 ] ; then
export fcs1=00
export fcs2=06
fi
if [ $fcst = 2 ] ; then
export fcs1=12
export fcs2=36
fi
if [ $fcst = 3 ] ; then
export fcs1=24
export fcs2=48
fi
export sdir=f${fcs1}af${fcs2}
export webdir=$rzdmdir/fits/time/$sdir
export localdir=$mapdir/fits/time/$sdir
mkdir -p $localdir
varlist='tmp hgt wnd moi ps'
for var in $varlist
do
export pdir=$tmpdir/$exp2/maps/time/$sdir/$var
if [ ! -d $pdir ] ; then
  mkdir -p $pdir
fi
$SCRIPTS/time$var.cdas
done
export pdir=$tmpdir/$exp2/maps/time/$sdir/acar
if [ ! -d $pdir ] ; then
  mkdir -p $pdir
fi
$SCRIPTS/timeacar.cdas
export pdir=$tmpdir/$exp2/maps/time/$sdir/acft
if [ ! -d $pdir ] ; then
  mkdir -p $pdir
fi
$SCRIPTS/timeacft.cdas
done
fi

# Make hcomp plots
if [[ $hcomp -eq 1 ]] ; then
echo
echo "Running hcomp scripts"
incr=24
for exp in $exp1 $exp2
do
##  start 00z-loop
for dir in anl fcs
do
if [ $exp = $exp1 ] ; then
 horizdir=$dir1/horiz/$dir
 outdir=$hz1dir
fi
if [ $exp = $exp2 ] ; then
 horizdir=$dir2/horiz/$dir
 outdir=$hz2dir
fi
cd $outdir
hzname=adpupa.mand
outfile=$outdir/adpupa.$dir.$sdate.$edate
$SCRIPTS/havgfit.sh $sdate $edate $horizdir $hzname $outfile $incr
for name in adpsfc sfcshp
do
hzname=$name
outfile=$outdir/$name.$dir.$sdate.$edate
imas=1
iwnd=0
$SCRIPTS/sfcfit.sh $sdate $edate $horizdir $hzname $outfile $imas $iwnd $incr
done
for dat in adpupa adpsfc sfcshp
do
ofile=${dat}00.$dir.ctl
> $ofile
cp $CTLS/${dat}00_tm.ctl $ofile
> out
#sed "s?date?$hts00?g" $ofile | sed "s?dir?$dir?g" | sed "s?file?$sdate.$edate?g"  | sed "s?ENDIAN?$endnew?g" > out
sed "s?date?$hts00?g" $ofile | sed "s?dir?$dir?g" | sed "s?file?$sdate.$edate?g"   > out
cp out $ofile
cat $ofile
$stnmap -i $ofile
done
done
for dir in fcs
do
hzname=adpupa.mand
outfile=$outdir/adpupa.$dir.$sdate12.$edate12
$SCRIPTS/havgfit.sh $sdate12 $edate12 $horizdir $hzname $outfile $incr
for name in adpsfc sfcshp
do
hzname=$name
outfile=$outdir/$name.$dir.$sdate12.$edate12
imas=1
iwnd=0
$SCRIPTS/sfcfit.sh $sdate12 $edate12 $horizdir $hzname $outfile $imas $iwnd $incr
done
for dat in adpupa adpsfc sfcshp
do
ofile=${dat}12.$dir.ctl
> $ofile
cp $CTLS/${dat}12_tm.ctl $ofile
> out
#sed "s?date?$hts12?g" $ofile | sed "s?dir?$dir?g" | sed "s?file?$sdate12.$edate12?g"  | sed "s?ENDIAN?$endnew?g" > out
sed "s?date?$hts12?g" $ofile | sed "s?dir?$dir?g" | sed "s?file?$sdate12.$edate12?g"  > out
cp out $ofile
cat $ofile
$stnmap -i $ofile
done
done
done
fi

# Make hplots plots
if [[ $hplots -eq 1 ]] ; then
echo
echo "Running hplots scripts"
export exp1dir=$hz1dir
export exp2dir=$hz2dir
export webdir=$rzdmdir/fits/horiz/$exp2
export localdir=$mapdir/fits/horiz/$exp2
mkdir -p $localdir
export pdir=$tmpdir/$exp2/maps/horiz/f00plots
if [ ! -d $pdir ] ; then
  mkdir -p $pdir
fi
$SCRIPTS/f00plots.cdas
export pdir=$tmpdir/$exp2/maps/horiz/f12plots
if [ ! -d $pdir ] ; then
  mkdir -p $pdir
fi
$SCRIPTS/f12plots.cdas
for exp in $exp1 $exp2
do
export exp
export expdir=$hz2dir
if [ $exp = $exp1 ] ; then
 export expdir=$hz1dir
fi
export webdir=$rzdmdir/fits/horiz/$exp
export localdir=$mapdir/fits/horiz/$exp
mkdir -p $localdir
export pdir=$tmpdir/$exp2/maps/horiz/horizab
if [ $exp = $exp1 ] ; then
export pdir=$tmpdir/$exp2/maps/horiz/horizab/$exp1
fi
if [ ! -d $pdir ] ; then
  mkdir -p $pdir
fi
$SCRIPTS/horizab.cdas
export pdir=$tmpdir/$exp2/maps/horiz/horizrab
if [ $exp = $exp1 ] ; then
export pdir=$tmpdir/$exp2/maps/horiz/horizrab/$exp1
fi
if [ ! -d $pdir ] ; then
  mkdir -p $pdir
fi
$SCRIPTS/horizrab.cdas
export pdir=$tmpdir/$exp2/maps/horiz/sfcab
if [ $exp = $exp1 ] ; then
export pdir=$tmpdir/$exp2/maps/horiz/sfcab/$exp1
fi
if [ ! -d $pdir ] ; then
  mkdir -p $pdir
fi
$SCRIPTS/sfcab.cdas
done
fi

# Send images to web
if [ $SEND2WEB = YES ] ; then
    python $USHverif_global/build_webpage.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Succesfully ran build_webpage.py"
    echo
else
    if [ $KEEPDATA = NO ]; then
        cd ..
        rm -rf $RUN
    fi
fi
