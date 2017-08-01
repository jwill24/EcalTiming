#!/usr/bin/env python

import sys, math, os, collections, getopt, subprocess, time, shutil
from array import array

def usage():
    print "Usage: python makeTimeCalibConstantsTag_step1.py --tag=[tag] --calib=[calib] --output=[output]"
    
try:
     opts, args = getopt.getopt(sys.argv[1:], "m:d:r:g:so:", ["tag=","calib=","output="])

except getopt.GetoptError:
     #* print help information and exit:*
     usage()
     sys.exit(2)

for opt, arg in opts:
    
     if opt in ("--tag"):
        tag = arg
     if opt in ("--calib"):
        calib = arg
     if opt in ("--output"):
        output= arg     
     
print "input tag          = ",tag
print "input calibration  = ",calib
print "output IOV         = ",output 

#dump last IOV xml
print "---- Dumping last IOV ----"

#command = os.system("conddb list EcalTimeCalibConstants_validation > IOVs_tmp")
command = os.system("conddb list "+str(tag)+" > IOVs_tmp")
with open('IOVs_tmp') as f_IOVs:
     data_IOVs = f_IOVs.read()

lines_IOVs = data_IOVs.splitlines()
line_IOVs_split = lines_IOVs[len(lines_IOVs)-2].split()
print "Payload: ",line_IOVs_split[5]
command = os.system("conddb dump "+ str(line_IOVs_split[5]) +" > dump_tmp")

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

#with open("/afs/cern.ch/work/b/bmarzocc/ECAL_Timing/CMSSW_9_2_6/src/EcalTiming/EcalTiming/output/ecalTiming-corr_run299481.dat") as f_interCalib:
with open(str(calib)) as f_interCalib:
        data_interCalib = f_interCalib.read()
lines_interCalib = data_interCalib.splitlines() 
for pos,x in enumerate(lines_interCalib):
    lines_interCalib_split = x.split()
    if(pos>=0 and pos<=60496): 
       if(lines_interCalib_split[3] == 'nan' or abs(float(lines_interCalib_split[3]))<=(abs(float(lines_interCalib_split[4]))/math.sqrt(float(lines_interCalib_split[5])))):
          timeIntercalib_EB[lines_interCalib_split[7]]=float(0.) 
          print "WARNING:",lines_interCalib_split[0],lines_interCalib_split[1],lines_interCalib_split[2],"- anomalous crystal, setting calibration to 0"
       else:
          timeIntercalib_EB[lines_interCalib_split[7]]=float(lines_interCalib_split[3])
       crystals_EB[lines_interCalib_split[7]] = bool(True)
    else:  
       if(lines_interCalib_split[3] == 'nan' or abs(float(lines_interCalib_split[3]))<=(abs(float(lines_interCalib_split[4]))/math.sqrt(float(lines_interCalib_split[5])))):
          timeIntercalib_EE[lines_interCalib_split[7]]=float(0.) 
          print "WARNING:",lines_interCalib_split[0],lines_interCalib_split[1],lines_interCalib_split[2],"- anomalous crystal, setting calibration to 0"
       else:
          timeIntercalib_EE[lines_interCalib_split[7]]=float(lines_interCalib_split[3])
       crystals_EE[lines_interCalib_split[7]] = bool(True)

#making the new IOV xml
print "---- Making new IOV xml ----"
 
with open("dump_tmp") as f_dump:
        data_dump = f_dump.read()
lines_dump = data_dump.splitlines()  

#f_tag = open("EcalTimeCalibConstants_new_IOV_299481.xml","w")
f_tag = open(str(output),"w")
for pos,x in enumerate(lines_dump):
    x_intro = str(x)+"\n"
    if(pos<8 or (pos>61207 and pos<61214) or pos>75861):
       x = str(x)+"\n"
       f_tag.write(x)
    elif(pos>=8 and pos<=61207): 
       x = x.replace("<item>", "")
       x = x.replace("</item>", "")
       if(crystals_EB[pos_EB[pos-8]] == True):
          x = float(x)-float(timeIntercalib_EB[pos_EB[pos-8]]) 
       else:
          x = float(x) 
       x = "{:.9e}".format(x)
       x_abs = "			<item>"+str(x)+"</item> \n"
       f_tag.write(x_abs)
    elif(pos>=61214 and pos<=75861):
       x = x.replace("<item>", "")
       x = x.replace("</item>", "")
       if(crystals_EE[pos_EE[pos-61214]] == True):
          x = float(x)-float(timeIntercalib_EE[pos_EE[pos-61214]]) 
       else:
          x = float(x) 
       x = "{:.9e}".format(x)
       x_abs = "			<item>"+str(x)+"</item> \n"
       f_tag.write(x_abs)
f_tag.close()

command = os.system("rm IOVs_tmp")
command = os.system("rm dump_tmp")
