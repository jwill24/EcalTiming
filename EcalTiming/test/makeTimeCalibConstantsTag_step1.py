#!/usr/bin/env python

import sys, math, os, collections, getopt, subprocess, time, shutil, datetime
from array import array

from historyPlot_utils import makeAbsTimingXML

def usage():
    print "Usage: python makeTimeCalibConstantsTag_step1.py --tag=[tag] --inList=[inList]"
    print "Usage: python makeTimeCalibConstantsTag_step1.py --tag=[tag] --calib=[calib]"
    print "Usage: python makeTimeCalibConstantsTag_step1.py --payload=[payload] --inList=[inList]"
    print "Usage: python makeTimeCalibConstantsTag_step1.py --payload=[payload] --calib=[calib]"
    
try:
     opts, args = getopt.getopt(sys.argv[1:], "t:i:c:p:h", ["tag=","inList=","calib=","payload=","help"])

except getopt.GetoptError:
     #* print help information and exit:*
     usage()
     sys.exit(2)

tag = ""
calib = ""
inList = ""
payload = ""
help = False
for opt, arg in opts:
    
     if opt in ("--tag"):
        tag = arg
     if opt in ("--calib"):
        calib = arg
     if opt in ("--inList"):
        inList = arg 
     if opt in ("--payload"):
        payload = arg    
     if opt in ("--help"):
        help = True     

if(help == True):
   usage()
   sys.exit(2)

goodMode = False

if((tag != "" and inList != "" and payload == "" and calib == "") or (tag != "" and inList == "" and payload == "" and calib != "") or (tag == "" and inList != "" and payload != "" and calib == "") or (tag == "" and inList == "" and payload != "" and calib != "")):
   goodMode = True
if(goodMode == False):
   usage()
   sys.exit(2)

if(tag != ""):
   print "tag          = ",tag
if(payload != ""):
   print "payload      = ",payload
if(inList != ""):
   print "inList       = ",inList 
if(calib != ""):
   print "calib        = ",calib 

IOVs_date = []
IOVs_time = []
IOVs_info = []

#dump IOVs xml
print "---- Dumping IOVs info ----"

if(tag != ""):
   command = os.system("conddb list "+str(tag)+" > IOVs_tmp")
   with open("IOVs_tmp") as f_IOVs:
      data_IOVs = f_IOVs.read()
      lines_IOVs = data_IOVs.splitlines()
      for pos,x in enumerate(lines_IOVs):
         if(pos > 2 and pos < len(lines_IOVs)-1):
            line_IOVs_split = lines_IOVs[pos].split()
            IOV_time = line_IOVs_split[2].split("-")
            date = IOV_time[2]+"/"+IOV_time[1]+"/"+IOV_time[0]
            timeStamp = time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
            IOVs_date.append(date)
            IOVs_time.append(timeStamp)
            IOVs_info.append(x)
            
#make crystal maps
print "---- Making crystal maps ----"

crystals_EB=collections.OrderedDict()
crystals_EE=collections.OrderedDict()
pos_EB=collections.OrderedDict()
pos_EE=collections.OrderedDict()
rawId_EB=collections.OrderedDict()
rawId_EE=collections.OrderedDict()
timeIntercalib_EB=collections.OrderedDict()
timeIntercalib_EE=collections.OrderedDict()

with open("EB_crystals.txt") as f_cryEB:
        data_cryEB = f_cryEB.read()
lines_cryEB = data_cryEB.splitlines() 
for pos,x in enumerate(lines_cryEB):
    lines_cryEB_split = x.split()
    crystals_EB[lines_cryEB_split[0]]=bool(False)
    pos_EB[pos]=lines_cryEB_split[0]
    rawId_EB[lines_cryEB_split[0]]=pos
   
with open("EE_crystals.txt") as f_cryEE:
        data_cryEE = f_cryEE.read()
lines_cryEE = data_cryEE.splitlines() 
for pos,x in enumerate(lines_cryEE):
    lines_cryEE_split = x.split()
    crystals_EE[lines_cryEE_split[0]]=bool(False)
    pos_EE[pos]=lines_cryEE_split[0]
    rawId_EE[lines_cryEE_split[0]]=pos

#Reading the calibration file
print "---- Reading the calibration file ----"

if(inList != ""):
   with open(str(inList)) as f_interCalib:
      data_interCalib = f_interCalib.read()
   lines_interCalib = data_interCalib.splitlines()
   inList_absCalib = inList.replace(".dat", "_absTiming.dat") 

if(payload != ""):
   print "---> Dumping the pyload: ",payload 
   command = os.system("conddb dump "+ str(payload) +" > dump_tmp")

if(calib == ""):
   f_absCalib = open(str(inList_absCalib),"w")
   for pos,x in enumerate(lines_interCalib):
      if(lines_interCalib[pos].find("#") != -1):
         continue
      output_absCalib = x.replace(".dat", ".xml")
      output_absCalib = output_absCalib.replace("-corr_", "-abs_")
      lines_interCalib_split = lines_interCalib[pos].split("/")
      interCalib_time = lines_interCalib_split[len(lines_interCalib_split)-1].split("_")
      if(interCalib_time[3].find(".dat") != -1):
         date = interCalib_time[3].replace(".dat", "")+"/"+interCalib_time[2]+"/"+interCalib_time[1]
         timeStamp = time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
         if(payload == ""):
            icount = 0
            for pos2,x2 in enumerate(IOVs_time):
               if(float(IOVs_time[pos2])>=float(timeStamp)):
                  icount = pos2-1
                  break
               if(float(IOVs_time[pos2])<float(timeStamp) and pos2 == len(IOVs_time)-1):
                  icount = len(IOVs_time)-1
                  break
            print date," ---> ",IOVs_info[icount]
            line_IOVs_split = IOVs_info[icount].split()
            command = os.system("conddb dump "+ str(line_IOVs_split[5]) +" > dump_tmp")
         makeAbsTimingXML(lines_interCalib[pos], timeIntercalib_EB, timeIntercalib_EE, pos_EB, pos_EE, crystals_EB, crystals_EE, str(output_absCalib))
         f_absCalib.write(str(output_absCalib)+"\n")
      else:
         print "WARNING: wrong import format! Skipping this IOV"  
   f_absCalib.close()
else:
   output_absCalib = calib.replace(".dat", ".xml")
   output_absCalib = output_absCalib.replace("-corr_", "-abs_")
   lines_interCalib_split = calib.split("/")
   interCalib_time = lines_interCalib_split[len(lines_interCalib_split)-1].split("_")
   if(interCalib_time[3].find(".dat") != -1):
      date = interCalib_time[3].replace(".dat", "")+"/"+interCalib_time[2]+"/"+interCalib_time[1]
      timeStamp = time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
      if(payload == ""):
         icount = 0
         for pos2,x2 in enumerate(IOVs_time):
            if(float(IOVs_time[pos2])>=float(timeStamp)):
               icount = pos2-1
               break
            if(float(IOVs_time[pos2])<float(timeStamp) and pos2 == len(IOVs_time)-1):
               icount = len(IOVs_time)-1
               break
         print date," ---> ",IOVs_info[icount]
         line_IOVs_split = IOVs_info[icount].split()
         command = os.system("conddb dump "+ str(line_IOVs_split[5]) +" > dump_tmp")
      makeAbsTimingXML(calib, timeIntercalib_EB, timeIntercalib_EE, pos_EB, pos_EE, crystals_EB, crystals_EE, output_absCalib)
      print "---> Absolute Timing file produced: ",output_absCalib
   else:
      print "WARNING: wrong import format! Skipping this IOV"  

command = os.system("rm IOVs_tmp")
command = os.system("rm dump_tmp")
