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
$X509_USER_PROXY  = $User_Preferences{"X509_USER_PROXY"};
$JOBCfgTemplate   = $User_Preferences{"JOBCfgTemplate"} ;
$DATASETName      = $User_Preferences{"DATASETName"} ;
$RUNNumber        = $User_Preferences{"RUNNumber"} ;
$OUTPUTSAVEPath   = $User_Preferences{"OUTPUTSAVEPath"} ;
$OUTPUTFILEName   = $User_Preferences{"OUTPUTFILEName"} ;
$QUEUE            = $User_Preferences{"QUEUE"};
$JSONFile         = $User_Preferences{"JSONFile"};
$GT               = $User_Preferences{"GT"};


print "BASEDir = "          .$BASEDir."\n" ;
print "X509_USER_PROXY = "  .$X509_USER_PROXY."\n" ;
print "JOBCfgTemplate = "   .$JOBCfgTemplate."\n" ;
print "DATASETName = "      .$DATASETName."\n" ;
print "RUNNUmber = "        .$RUNNumber."\n" ;
print "OUTPUTSAVEPath = "   .$OUTPUTSAVEPath."\n" ;
print "OUTPUTFILEName = "   .$OUTPUTFILEName."\n" ;
print "QUEUE  = "           .$QUEUE."\n" ;
print "JSONFile  = "        .$JSONFile."\n" ;
print "GT  = "              .$GT."\n" ;

system("rm fileList.txt") ;

$sampleJobListFile = "./lancia.sh";
open(SAMPLEJOBLISTFILE, ">", $sampleJobListFile);


#####################################################
# PG prepare the array containing the root files list
#####################################################

$totNumber = 0;
$jobNumber = 0;

$JOBdir = $RUNNumber;

$LISTOFSamples = "fileList.txt";
$command = "touch ".$LISTOFSamples ;
system ($command) ;
$command = "python ./das_client.py --query='file dataset=".$DATASETName." run=".$RUNNumber."' --limit=0 >> fileList.txt \n" ;
#print $command ;
system ("python ./das_client.py --query='file dataset=".$DATASETName." run=".$RUNNumber."' --limit=0 >> fileList.txt \n") ;
  
open (LISTOFSamples,$LISTOFSamples) ;
while (<LISTOFSamples>)
{
    ++$totNumber;
}

$JOBModulo = 1;

$jobNumber = int($totNumber/$JOBModulo);
if( $totNumber%$JOBModulo != 0)
{
    $jobNumber = $jobNumber+1;
}

print "NumberOfJobs = ".$jobNumber."\n";
system ("mkdir ".$JOBdir." \n") ;

################
# loop over jobs 
################

$currDir = `pwd` ;
chomp ($currDir) ;

for($jobIt = 1; $jobIt <= $jobNumber; ++$jobIt)
{
    
	$jobDir = $currDir."/".$JOBdir."/JOB_".$jobIt ;
	system ("mkdir ".$jobDir." \n") ;
    
	$tempBjob = $jobDir."/bjob_".$jobIt.".sh" ;
	$command = "touch ".$tempBjob ;
	system ($command) ;
	$command = "chmod 777 ".$tempBjob ;
	system ($command) ;
        $command = "cp  ../test/".$JOBCfgTemplate." ".$jobDir;
	system ($command) ;
        if($JSONFile ne "0"){
           $command = "cp  ../".$JSONFile." ".$jobDir;
	   system ($command) ;
        }
	$it = 0;
        $file = 0;

	open (LISTOFFiles,$LISTOFSamples) ;
	while (<LISTOFFiles>)
	{
	    chomp; 
	    s/#.*//;                # no comments
	    s/^\s+//;               # no leading white
	    s/\s+$//;               # no trailing white
	    #$line = $_.",".$line ;
            #print "1: ".$line."\n";
            
	    if( ($it >= ($jobIt - 1)*$JOBModulo) && ($it < ($jobIt)*$JOBModulo) )
	    { 
                #$line = $_.",".$line ;
                $line = $_;
                $file = $line;
		$line = "";
	    }
	    ++$it;
	}
        #print $file."\n";

        ######################
        # make job files
        ######################    
    
	open (SAMPLEJOBFILE, ">", $tempBjob) or die "Can't open file ".$tempBjob;

	$command = "#!/bin/tcsh" ;
	print SAMPLEJOBFILE $command."\n";

	$command = "cd ".$BASEDir."/".$JOBdir."/JOB_".$jobIt ;
	print SAMPLEJOBFILE $command."\n";

	$command = "setenv SCRAM_ARCH slc6_amd64_gcc530" ;
	print SAMPLEJOBFILE $command."\n";

        $command = "echo $SCRAM_ARCH" ;
        print SAMPLEJOBFILE $command."\n";

	$command = "eval `scramv1 ru -csh`" ;
	print SAMPLEJOBFILE $command."\n";
         
        $command = "setenv X509_USER_PROXY ".$X509_USER_PROXY ;
	print SAMPLEJOBFILE $command."\n";
        
        if($JSONFile eq "0"){
	   $command = "cmsRun ".$JOBCfgTemplate." files=root://cms-xrd-global.cern.ch/".$file." globaltag=".$GT." output=".$OUTPUTFILEName."_".$jobIt;
	   print SAMPLEJOBFILE $command."\n";
        }else{
           $command = "cmsRun ".$JOBCfgTemplate." files=root://cms-xrd-global.cern.ch/".$file." globaltag=".$GT." jsonFile=".$JSONFile." output=".$OUTPUTFILEName."_".$jobIt;
	   print SAMPLEJOBFILE $command."\n";
        }
        
        $command = "eos mkdir ".$OUTPUTSAVEPath."/".$JOBdir;
	print SAMPLEJOBFILE $command."\n";

	$command = "eos cp ".$OUTPUTFILEName."_".$jobIt.".root root://eoscms.cern.ch/".$OUTPUTSAVEPath."/".$JOBdir."/";
	print SAMPLEJOBFILE $command."\n";

        $command = "rm ".$OUTPUTFILEName."_".$jobIt.".root";
	print SAMPLEJOBFILE $command."\n";

	
	############
	# submit job
	############
	
        $command = "bsub -cwd ".$jobDir." -q ".$QUEUE." ".$tempBjob."\n" ; 
	print SAMPLEJOBLISTFILE $command."\n";
}  

system("rm fileList.txt") ;
