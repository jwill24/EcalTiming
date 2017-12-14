#!/usr/bin/env python

import sys, math, os, collections, getopt, subprocess, time, shutil, datetime
from ROOT import *
from array import array
from historyPlot_utils import calibCompareXML

def usage():
    print "Usage: python makeTagComparison.py --tag1=[tag1] --tag2=[tag2] (--since=[since] --eb --ee)"
    
try:
     opts, args = getopt.getopt(sys.argv[1:], "", ["tag1=","tag2=","since=","eb","ee","help"])

except getopt.GetoptError:
     #* print help information and exit:*
     usage()
     sys.exit(2)


tag1 = ""
tag2 = ""
since = ""
onlyEB = False
onlyEE = False
help = False

for opt, arg in opts:
    
     if opt in ("--tag1"):
        tag1 = arg
     if opt in ("--tag2"):
        tag2 = arg
     if opt in ("--since"):
        since = arg
     if opt in ("--eb"):
        onlyEB = True   
     if opt in ("--eb"):
        onlyEE = True   
     if opt in ("--help"):
        help = True     

if(help == True):
   usage()
   sys.exit(2)

if(tag1 == "" or tag2 == ""):
   usage()
   sys.exit(2)

if(tag1 != ""):
   print "tag1    = ",tag1
if(tag2 != ""):
   print "tag2    = ",tag2
if(since != ""):
   print "since    = ",since
if(onlyEB == True):
   print "onlyEB  = ",onlyEB
if(onlyEE == True):
   print "onlyEE  = ",onlyEE
 

#gStyle.SetOptStat(0)

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
ieta_EB=collections.OrderedDict()
iphi_EB=collections.OrderedDict()
ix_EE=collections.OrderedDict()
iy_EE=collections.OrderedDict()
iz_EE=collections.OrderedDict()

with open("EB_crystals.txt") as f_cryEB:
        data_cryEB = f_cryEB.read()
lines_cryEB = data_cryEB.splitlines() 
for pos,x in enumerate(lines_cryEB):
    lines_cryEB_split = x.split()
    crystals_EB[lines_cryEB_split[0]]=bool(False)
    pos_EB[pos]=lines_cryEB_split[0]
    rawId_EB[lines_cryEB_split[0]]=pos
    ieta_EB[lines_cryEB_split[0]] = lines_cryEB_split[4]
    iphi_EB[lines_cryEB_split[0]] = lines_cryEB_split[3]
   
with open("EE_crystals.txt") as f_cryEE:
        data_cryEE = f_cryEE.read()
lines_cryEE = data_cryEE.splitlines() 
for pos,x in enumerate(lines_cryEE):
    lines_cryEE_split = x.split()
    crystals_EE[lines_cryEE_split[0]]=bool(False)
    pos_EE[pos]=lines_cryEE_split[0]
    rawId_EE[lines_cryEE_split[0]]=pos
    ix_EE[lines_cryEE_split[0]] = lines_cryEE_split[4]
    iy_EE[lines_cryEE_split[0]] = lines_cryEE_split[5]
    iz_EE[lines_cryEE_split[0]] = lines_cryEE_split[3]

print "---- Reading EE rings ----"

ringMap = [[[0 for k in xrange(101)] for j in xrange(101)] for i in xrange(2)]

with open("eerings.dat") as f_EErings:
        data_EErings = f_EErings.read()
lines_EErings = data_EErings.splitlines() 
for pos,x in enumerate(lines_EErings):
    if(x == ""): 
       continue
    lines_EErings_split = x.split()
    lines_EErings_split[0] = lines_EErings_split[0].replace("(", "")
    lines_EErings_split[0] = lines_EErings_split[0].replace(",", "")
    lines_EErings_split[1] = lines_EErings_split[1].replace(",", "")
    lines_EErings_split[2] = lines_EErings_split[2].replace(")", "")
    lines_EErings_split[2] = lines_EErings_split[2].replace(",", "")
    if(int(int(lines_EErings_split[2]))<0):
       lines_EErings_split[2] = "0"
    ringMap[int(lines_EErings_split[2])][int(lines_EErings_split[1])][int(lines_EErings_split[0])] = int(lines_EErings_split[3])

IOV_runs1=[]
IOV_runs2=[]
IOV_payload1=[]
IOV_payload2=[]

h_diff_EB = TH1F("h_diff_EB","",1000,-5,5)
h_diff_EE = TH1F("h_diff_EE","",1000,-5,5)

command = os.system("conddb list "+str(tag1)+" > tag1_list_tmp")
command = os.system("conddb --db dev list "+str(tag2)+" > tag2_list_tmp")

with open("tag1_list_tmp") as f_IOVs:
   data_IOVs = f_IOVs.read()
   lines_IOVs = data_IOVs.splitlines()
   for pos,x in enumerate(lines_IOVs):
      if(pos > 2 and pos < len(lines_IOVs)-1):
         line_IOVs_split = lines_IOVs[pos].split()
         if(int(line_IOVs_split[0]) >= int(since)):
            print line_IOVs_split[0]
            IOV_payload1.append(line_IOVs_split[5])
            IOV_runs1.append(line_IOVs_split[0])

with open("tag2_list_tmp") as f_IOVs:
   data_IOVs = f_IOVs.read()
   lines_IOVs = data_IOVs.splitlines()
   for pos,x in enumerate(lines_IOVs):
      if(pos > 2 and pos < len(lines_IOVs)-1):
         line_IOVs_split = lines_IOVs[pos].split()
         if(int(line_IOVs_split[0]) >= int(since)):
            print line_IOVs_split[0]
            IOV_payload2.append(line_IOVs_split[5])
            IOV_runs2.append(line_IOVs_split[0])

if(len(IOV_runs1) != len(IOV_runs2)):
   print "WARNING: different number of IOVs!"
   sys.exit(2)

for pos,x in enumerate(IOV_runs1):
   if(IOV_runs1[pos] != IOV_runs2[pos]):
      print "WARNING:",IOV_runs1[pos]," - ",IOV_runs2[pos]," different IOV run number ----> SKIP"
   else:
      print "IOV:",IOV_runs1[pos],IOV_runs2[pos] 
      command = os.system("conddb dump "+str(IOV_payload1[pos])+" >> dump1_tmp.xml")
      command = os.system("conddb --db dev dump "+str(IOV_payload2[pos])+" >> dump2_tmp.xml")
      calibCompareXML (IOV_runs1[pos], 'dump1_tmp.xml', 'dump2_tmp.xml', h_diff_EB, h_diff_EE, onlyEB, onlyEE)
      command = os.system("rm dump1_tmp.xml")
      command = os.system("rm dump2_tmp.xml")

c1 = TCanvas("c1","c1",1)
h_diff_EB.Draw("H")
c1.SaveAs("h_diff_EB.png","png")
c1.SaveAs("h_diff_EB.pdf","pdf") 

c2 = TCanvas("c2","c2",1)
h_diff_EE.Draw("H")
c2.SaveAs("h_diff_EE.png","png")
c2.SaveAs("h_diff_EE.pdf","pdf") 

#command = os.system("rm tag1_list_tmp")
#command = os.system("rm tag2_list_tmp")
