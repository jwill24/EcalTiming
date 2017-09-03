#!/usr/bin/perl

# ----------------------------------------------------------------------------
#      MAIN PROGRAM
# ----------------------------------------------------------------------------

use Env;

#PG lettura dei parametri da cfg file
#PG --------------------------------
print "reading ".$ARGV[0]."\n" ;

open (USERCONFIG,$ARGV[0]) ;

while (<USERCONFIG>)
{
    chomp; 
    s/#.*//;                # no comments
    s/^\s+//;               # no leading white
    s/\s+$//;               # no trailing white
#    next unless length;     # anything left?
    my ($var, $value) = split(/\s*=\s*/, $_, 2);
    $User_Preferences{$var} = $value;
}

$BASEDir          = $User_Preferences{"BASEDir"};
$INPUTDir         = $User_Preferences{"INPUTDir"};
$INPUTRuns        = $User_Preferences{"INPUTRuns"};
$JOBCfgTemplate   = $User_Preferences{"JOBCfgTemplate"} ;
$OUTPUTSAVEPath   = $User_Preferences{"OUTPUTSAVEPath"} ;
$QUEUE            = $User_Preferences{"QUEUE"};

print "BASEDir = "          .$BASEDir."\n" ;
print "INPUTDir = "         .$INPUTDir."\n" ;
print "INPUTRuns = "        .$INPUTRuns."\n" ;
print "JOBCfgTemplate = "   .$JOBCfgTemplate."\n" ;
print "OUTPUTSAVEPath = "   .$OUTPUTSAVEPath."\n" ;
print "QUEUE  = "           .$QUEUE."\n" ;

$command = "rm list_files_tmp.txt" ; 
system ($command) ;

$sampleJobListFile = "./lancia.sh";
open(SAMPLEJOBLISTFILE, ">", $sampleJobListFile);

$currDir = `pwd` ;
chomp ($currDir) ;

$JOBdir = $INPUTRuns."_Calib";
$JOBdir =~ s/,/_/g ;

system ("mkdir ".$JOBdir." \n") ;

$jobDir = $currDir."/".$JOBdir ;   
$tempBjob = $jobDir."/bjob.sh" ;

@runs = split /,/, $INPUTRuns;

$LISTOFFiles = "./list_files_tmp.txt" ;
for($index=0;$index<=$#runs;$index++)
{
    system ("eos find -f ".$INPUTDir."/".$runs[$index]."/ | grep .root >> ".$LISTOFFiles."\n") ;
}

$JOBLISTOFFiles;

open (LISTOFFiles,$LISTOFFiles) ;
while (<LISTOFFiles>)
{
    chomp; 
    s/#.*//;                # no comments
    s/^\s+//;               # no leading white
    s/\s+$//;               # no trailing white
    $file = $_ ;
    $remove = "/eos/cms";
    $file  =~ s/$remove// ;
    
    $JOBLISTOFFiles = $JOBLISTOFFiles."root://eoscms.cern.ch/".$file.",";
}

chop $JOBLISTOFFiles;

$tempo1 = "./EcalTimingCalibration_cfg.py" ;   
system ("cat ".$JOBCfgTemplate." | sed -e s%LISTOFFILES%".$JOBLISTOFFiles."%g > ".$tempo1) ;

$command = "touch ".$tempBjob ;
system ($command) ;
$command = "chmod 777 ".$tempBjob ;
system ($command) ;
$command = "cp ".$tempo1." ".$jobDir;
system ($command) ;

$command = "mkdir ".$jobDir."/output";
system ($command) ;

$OUTDir = $OUTPUTSAVEPath."/".$INPUTRuns;
$OUTDir =~ s/,/_/g ;

######################
# make job files
######################    
    
open (SAMPLEJOBFILE, ">", $tempBjob) or die "Can't open file ".$tempBjob;

$command = "#!/bin/tcsh" ;
print SAMPLEJOBFILE $command."\n";

$command = "cd ".$BASEDir."/".$JOBdir;
print SAMPLEJOBFILE $command."\n";

$command = "setenv SCRAM_ARCH slc6_amd64_gcc530" ;
print SAMPLEJOBFILE $command."\n";

$command = "echo $SCRAM_ARCH" ;
print SAMPLEJOBFILE $command."\n";

$command = "eval `scramv1 ru -csh`" ;
print SAMPLEJOBFILE $command."\n";

$command = "EcalTimingCalibration EcalTimingCalibration_cfg.py" ;
print SAMPLEJOBFILE $command."\n";  

$command = "eos mkdir ".$OUTDir;
print SAMPLEJOBFILE $command."\n";         
        
$command = "cd output" ;
print SAMPLEJOBFILE $command."\n";

$command = "eos cp ecalTiming.dat root://eoscms.cern.ch/".$OUTDir."/";
print SAMPLEJOBFILE $command."\n";

$command = "eos cp ecalTiming-corr.dat root://eoscms.cern.ch/".$OUTDir."/";
print SAMPLEJOBFILE $command."\n";

$command = "eos cp ecalTiming.root root://eoscms.cern.ch/".$OUTDir."/";
print SAMPLEJOBFILE $command."\n";
	
############
# submit job
############
	
$command = "bsub -cwd ".$jobDir." -q ".$QUEUE." ".$tempBjob."\n" ; 
print SAMPLEJOBLISTFILE $command."\n";

$command = "rm list_files_tmp.txt" ; 
system ($command) ;
$command = "rm ".$tempo1 ; 
system ($command) ;
