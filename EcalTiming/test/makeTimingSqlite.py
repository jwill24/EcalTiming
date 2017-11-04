#!/usr/bin/env python

import sys, math, os, collections, getopt, subprocess, time, shutil, datetime
from ROOT import TFile, TH1, TH1F, TLine, TCanvas, TLegend, TGraph, TGraphErrors, gROOT, gPad, TAttText, TText, TGaxis, TMath, TStyle, TColor
from array import array

def usage():
    print "Usage: python makeTimingSqlite.py --calib=[calib] --tag=[tag]"
    print "Usage: python makeTimingSqlite.py --inList=[inList] --tag=[tag]"
    
try:
     opts, args = getopt.getopt(sys.argv[1:], "c:i:t:h", ["calib=","inList=","tag=","help"])

except getopt.GetoptError:
     #* print help information and exit:*
     usage()
     sys.exit(2)


calib = ""
inList = ""
tag = ""
help = False
for opt, arg in opts:
    
     if opt in ("--calib"):
        calib = arg
     if opt in ("--inList"):
        inList = arg  
     if opt in ("--tag"):
        tag = arg    
     if opt in ("--help"):
        help = True     

if(help == True):
   usage()
   sys.exit(2)

goodMode = False

if((calib != "" and inList == "" and tag!="") or (calib == "" and inList != "" and tag!="")):
   goodMode = True
if(goodMode == False):
   usage()
   sys.exit(2)

if(calib != ""):
   print "calib  = ",calib
if(inList != ""):
   print "inList = ",inList  
if(tag != ""):
   print "tag = ",tag  

f_tag = open("launch_tagCreation.sh","w")
if(inList != ""):
   with open(str(inList)) as f_interCalib:
      data_interCalib = f_interCalib.read()
      lines_interCalib = data_interCalib.splitlines() 
      for pos,x in enumerate(lines_interCalib):
         if(x.find("#") != -1):
            continue
         lines_interCalib_split = lines_interCalib[pos].split("/")
         runs = lines_interCalib_split[len(lines_interCalib_split)-2].split("_")
         firstRun = runs[0]
         output = x.replace(".xml", ".db")
         if os.path.isfile(str(output)):
            print "WARNING: overwriting ",output
            command = os.system("rm "+str(output))
         command=os.system("cmsRun ../../../CondTools/Ecal/python/testEcalTimeCalib.py xmlFile="+str(x)+" sqliteFile="+str(output)+" firstRun="+str(firstRun)+" tag="+str(tag))
         creation_command = "conddb_import -f sqlite_file:"+str(output)+" -i "+str(tag)+" -c sqlite_file:"+str(tag)+"_rereco_calib.db -t "+str(tag)+" -b "+str(firstRun)+"\n"
         f_tag.write(creation_command)
else:
   calib_split = calib.split("/")
   runs = calib_split[len(calib_split)-2].split("_")
   firstRun = runs[0]
   output = calib.replace(".xml", ".db")
   if os.path.isfile(str(output)):
      print "WARNING: overwriting ",output
      command = os.system("rm "+str(output))
   command=os.system("cmsRun ../../../CondTools/Ecal/python/testEcalTimeCalib.py xmlFile="+str(calib)+" sqliteFile="+str(output)+" firstRun="+str(firstRun)+" tag="+str(tag))
   creation_command = "conddb_import -f sqlite_file:"+str(output)+" -i "+str(tag)+" -c sqlite_file:"+str(tag)+"_rereco_calib.db -t "+str(tag)+" -b "+str(firstRun)
   os.system(creation_command)

f_tag.close()
   


