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
$JOBCfgTemplate   = $User_Preferences{"JOBCfgTemplate"} ;
$OUTPUTSAVEPath   = $User_Preferences{"OUTPUTSAVEPath"} ;
$QUEUE            = $User_Preferences{"QUEUE"};
$JOBdir           = $User_Preferences{"JOBdir"};

print "BASEDir = "          .$BASEDir."\n" ;
print "JOBCfgTemplate = "   .$JOBCfgTemplate."\n" ;
print "OUTPUTSAVEPath = "   .$OUTPUTSAVEPath."\n" ;
print "QUEUE  = "           .$QUEUE."\n" ;
print "JOBdir  = "          .$JOBdir."\n" ;

$sampleJobListFile = "./lancia.sh";
open(SAMPLEJOBLISTFILE, ">", $sampleJobListFile);

system ("mkdir ".$JOBdir." \n") ;

$currDir = `pwd` ;
chomp ($currDir) ;

$jobDir = $currDir."/".$JOBdir ;   
$tempBjob = $jobDir."/bjob.sh" ;

$command = "touch ".$tempBjob ;
system ($command) ;
$command = "chmod 777 ".$tempBjob ;
system ($command) ;
$command = "cp EcalTimingCalibration_cfg.py ".$jobDir;
system ($command) ;

$command = "mkdir ".$jobDir."/output";
system ($command) ;

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

$command = "eos mkdir ".$OUTPUTSAVEPath;
print SAMPLEJOBFILE $command."\n";         
        
$command = "cd output" ;
print SAMPLEJOBFILE $command."\n";

$command = "eos cp ecalTiming.dat root://eoscms.cern.ch/".$OUTPUTSAVEPath;
print SAMPLEJOBFILE $command."\n";

$command = "eos cp ecalTiming-corr.dat root://eoscms.cern.ch/".$OUTPUTSAVEPath;
print SAMPLEJOBFILE $command."\n";

$command = "eos cp ecalTiming.root root://eoscms.cern.ch/".$OUTPUTSAVEPath;
print SAMPLEJOBFILE $command."\n";
	
############
# submit job
############
	
$command = "bsub -cwd ".$jobDir." -q ".$QUEUE." ".$tempBjob."\n" ; 
print SAMPLEJOBLISTFILE $command."\n";

