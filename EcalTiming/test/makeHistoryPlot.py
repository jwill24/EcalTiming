#!/usr/bin/env python

import sys, math, os, collections, getopt, subprocess, time, shutil, datetime
from ROOT import TFile, TH1, TH1F, TLine, TCanvas, TLegend, TGraph, TGraphErrors, gROOT, gPad, TAttText, TText, TGaxis, TMath, TStyle, TColor
from array import array
from historyPlot_utils import calibFromXML
from historyPlot_utils import calibFromDAT

def usage():
    print "Usage: python makeHistoryPlot.py --tag=[tag] --year=[year] (and/or --runBased and/or --noEEForward)"
    print "Usage: python makeHistoryPlot.py --inList=[inList] (--epoch=[epoch] and/or --ix=[ix] and/or --iy=[iy] and/or --iz=[iz] and/or --absTime and/or --runBased and/or --noEEForward)"
    
try:
     opts, args = getopt.getopt(sys.argv[1:], "t:y:i:e:x:y:z:arnh", ["tag=","year=","inList=","epoch=","ix=","iy=","iz=","absTime","runBased","noEEForward","help"])

except getopt.GetoptError:
     #* print help information and exit:*
     usage()
     sys.exit(2)


tag = ""
year = ""
epoch = ""
inList = ""
ix = ""
iy = ""
iz = ""
absTime = False
runBased = False
help = False
noEEForward = False

for opt, arg in opts:
    
     if opt in ("--tag"):
        tag = arg
     if opt in ("--year"):
        year = arg
     if opt in ("--epoch"):
        epoch = arg
     if opt in ("--inList"):
        inList = arg  
     if opt in ("--ix"):
        ix = arg  
     if opt in ("--iy"):
        iy = arg  
     if opt in ("--iz"):
        iz = arg  
     if opt in ("--absTime"):
        absTime = True   
     if opt in ("--runBased"):
        runBased = True 
     if opt in ("--noEEForward"):
        noEEForward = True   
     if opt in ("--help"):
        help = True     

if(help == True):
   usage()
   sys.exit(2)

if((tag == "" and year == "" and epoch == "" and inList == "") or (tag != "" and year == "") or (tag == "" and year != "")):
   usage()
   sys.exit(2)

if(tag != ""):
   print "tag          = ",tag
if(year != ""):
   print "year         = ",year
if(epoch != ""):
   print "epoch        = ",epoch
if(inList != ""):
   print "inList       = ",inList  
if(ix != ""):
   print "ix           = ",ix 
if(iy != ""):
   print "iy           = ",iy 
if(iz != ""):
   print "iz           = ",iz 
if(absTime == True):
   print "absTime      = ",absTime 
if(runBased == True):
   print "runBased     = ",runBased 
if(noEEForward == True):
   print "noEEForward  = ",noEEForward
 

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

g_EBMinus = TGraphErrors()
g_EBPlus = TGraphErrors()
g_EEMinus = TGraphErrors()
g_EEPlus = TGraphErrors()

timeStamp_begin=0
timeStamp_end=0
date_begin=""
date_end=""

timeStamp_list=[]
timeStamp_point=[]
allCalib_list=[]
icount = 0


if(inList != ""):
   with open(str(inList)) as f_interCalib:
      data_interCalib = f_interCalib.read()
      lines_interCalib = data_interCalib.splitlines() 
      for pos,x in enumerate(lines_interCalib):
         lines_interCalib_split = lines_interCalib[pos].split("/")
         interCalib_time = lines_interCalib_split[len(lines_interCalib_split)-1].split("_")
         icount = icount+1
         year = interCalib_time[1]
         if(interCalib_time[3].find(".xml") != -1):
            date = interCalib_time[3].replace(".xml", "")+"/"+interCalib_time[2]+"/"+interCalib_time[1]
            if(runBased == True):
               interCalib_run = lines_interCalib_split[len(lines_interCalib_split)-2].split("_")
               date = float(interCalib_run[0])
            calibFromXML(lines_interCalib[pos], date, icount, timeStamp_list, timeStamp_point, allCalib_list, g_EBMinus, g_EBPlus, g_EEMinus, g_EEPlus, runBased, ringMap, noEEForward, ix, iy, iz, pos_EB, ieta_EB, iphi_EB, pos_EE, ix_EE, iy_EE, iz_EE)
         if(interCalib_time[3].find(".dat") != -1):
            date = interCalib_time[3].replace(".dat", "")+"/"+interCalib_time[2]+"/"+interCalib_time[1]
            if(runBased == True):
               interCalib_run = lines_interCalib_split[len(lines_interCalib_split)-2].split("_")
               date = float(interCalib_run[0])   
            calibFromDAT(lines_interCalib[pos], date, icount, timeStamp_list, timeStamp_point,allCalib_list, g_EBMinus, g_EBPlus, g_EEMinus, g_EEPlus, runBased, ringMap, noEEForward, ix, iy, iz)

else:
   #dump IOVs xml
   print "---- Dumping IOVs ----"

   command = os.system("conddb list "+str(tag)+" > IOVs_tmp")
   with open("IOVs_tmp") as f_IOVs:
      data_IOVs = f_IOVs.read()
      lines_IOVs = data_IOVs.splitlines()
      for pos,x in enumerate(lines_IOVs):
         if(pos > 2 and pos < len(lines_IOVs)-1):
            line_IOVs_split = lines_IOVs[pos].split()
            IOV_time = line_IOVs_split[2].split("-")
            date = IOV_time[2]+"/"+IOV_time[1]+"/"+IOV_time[0]
            if(year == IOV_time[0]):
               print x
               icount = icount+1
               command = os.system("conddb dump "+ str(line_IOVs_split[5]) +" > dump_tmp")
               calibFromXML("dump_tmp", date, icount, timeStamp_list, timeStamp_point, allCalib_list, g_EBMinus, g_EBPlus, g_EEMinus, g_EEPlus, runBased, ringMap, noEEForward)

if(runBased == True):
   timeStamp_begin = timeStamp_point[0]
   timeStamp_end = timeStamp_point[len(timeStamp_point)-1]
else:
   timeStamp_begin = timeStamp_list[0]
   timeStamp_end = timeStamp_list[len(timeStamp_list)-1]

allCalib_list.sort()
y_min = allCalib_list[0]-0.1
y_max = allCalib_list[len(allCalib_list)-1]+0.2
if(absTime == True):
   y_max = allCalib_list[len(allCalib_list)-1]+0.5
if(ix != "" and iy != "" and iz != ""):
   y_min = allCalib_list[0]-1.
   y_max = allCalib_list[len(allCalib_list)-1]+1.

g_EBMinus.SetMarkerColor(600)
g_EBMinus.SetLineColor(600)
g_EBMinus.SetLineWidth(3)
g_EBMinus.SetMarkerStyle(20)
g_EBMinus.SetMarkerSize(0.8)
g_EBMinus.GetXaxis().SetLabelFont(42)
g_EBMinus.GetXaxis().SetLabelOffset(0.007)
g_EBMinus.GetXaxis().SetLabelSize(0.04)
g_EBMinus.GetXaxis().SetTitleSize(0.05)
g_EBMinus.GetXaxis().SetTitleFont(42)
g_EBMinus.GetYaxis().SetLabelFont(42)
g_EBMinus.GetYaxis().SetLabelOffset(0.007)
g_EBMinus.GetYaxis().SetLabelSize(0.05)
g_EBMinus.GetYaxis().SetTitleSize(0.05)
g_EBMinus.GetYaxis().SetTitleOffset(1.1)
g_EBMinus.GetYaxis().SetTitleFont(42)

g_EBPlus.SetMarkerColor(1)
g_EBPlus.SetLineColor(1)
g_EBPlus.SetLineWidth(3)
g_EBPlus.SetMarkerStyle(20)
g_EBPlus.SetMarkerSize(0.8)
g_EBPlus.GetXaxis().SetLabelFont(42)
g_EBPlus.GetXaxis().SetLabelOffset(0.007)
g_EBPlus.GetXaxis().SetLabelSize(0.04)
g_EBPlus.GetXaxis().SetTitleSize(0.05)
g_EBPlus.GetXaxis().SetTitleFont(42)
g_EBPlus.GetYaxis().SetLabelFont(42)
g_EBPlus.GetYaxis().SetLabelOffset(0.007)
g_EBPlus.GetYaxis().SetLabelSize(0.05)
g_EBPlus.GetYaxis().SetTitleSize(0.05)
g_EBPlus.GetYaxis().SetTitleOffset(1.1)
g_EBPlus.GetYaxis().SetTitleFont(42)

g_EEMinus.SetMarkerColor(632)
g_EEMinus.SetLineColor(632)
g_EEMinus.SetLineWidth(3)
g_EEMinus.SetMarkerStyle(20)
g_EEMinus.SetMarkerSize(0.8)
g_EEMinus.GetXaxis().SetLabelFont(42)
g_EEMinus.GetXaxis().SetLabelOffset(0.007)
g_EEMinus.GetXaxis().SetLabelSize(0.04)
g_EEMinus.GetXaxis().SetTitleSize(0.05)
g_EEMinus.GetXaxis().SetTitleFont(42)
g_EEMinus.GetYaxis().SetLabelFont(42)
g_EEMinus.GetYaxis().SetLabelOffset(0.007)
g_EEMinus.GetYaxis().SetLabelSize(0.05)
g_EEMinus.GetYaxis().SetTitleSize(0.05)
g_EEMinus.GetYaxis().SetTitleOffset(1.1)
g_EEMinus.GetYaxis().SetTitleFont(42)
   
g_EEPlus.SetMarkerColor(401)
g_EEPlus.SetLineColor(401)
g_EEPlus.SetLineWidth(3)
g_EEPlus.SetMarkerStyle(20)
g_EEPlus.SetMarkerSize(0.8)
g_EEPlus.GetXaxis().SetLabelFont(42)
g_EEPlus.GetXaxis().SetLabelOffset(0.007)
g_EEPlus.GetXaxis().SetLabelSize(0.04)
g_EEPlus.GetXaxis().SetTitleSize(0.05)
g_EEPlus.GetXaxis().SetTitleFont(42)
g_EEPlus.GetYaxis().SetLabelFont(42)
g_EEPlus.GetYaxis().SetLabelOffset(0.007)
g_EEPlus.GetYaxis().SetLabelSize(0.05)
g_EEPlus.GetYaxis().SetTitleSize(0.05)
g_EEPlus.GetYaxis().SetTitleOffset(1.1)
g_EEPlus.GetYaxis().SetTitleFont(42)

if(runBased == False):
   if(absTime == False):
      test = TH1F("test","Ecal Timing ["+str(year)+str(epoch)+"]",1000,float(timeStamp_begin-172800),float(timeStamp_end+172800))
   else:
      test = TH1F("test","Ecal Absolute Timing ["+str(year)+str(epoch)+"]",1000,float(timeStamp_begin-172800),float(timeStamp_end+172800))
else:
   if(absTime == False):
      test = TH1F("test","Ecal Timing ["+str(year)+str(epoch)+"]",len(timeStamp_point),float(timeStamp_begin-0.5),float(timeStamp_end+0.5))
   else:
      test = TH1F("test","Ecal Absolute Timing ["+str(year)+str(epoch)+"]",len(timeStamp_point),float(timeStamp_begin-0.5),float(timeStamp_end+0.5))
test.SetStats(0)
test.SetFillColor(1)
test.SetFillStyle(3004)
test.SetLineColor(0)
test.SetLineWidth(3)
test.SetMarkerStyle(20)
if(runBased == False):
   test.GetXaxis().SetTitle("date")
   test.GetXaxis().SetTimeDisplay(1)
   test.GetXaxis().SetTimeFormat("%d/%m%F1970-01-01 00:00:00s0")
   test.GetXaxis().SetNdivisions(510)
   test.GetXaxis().SetLabelFont(42)
   test.GetXaxis().SetLabelOffset(0.007)
   test.GetXaxis().SetLabelSize(0.04) 
   test.GetXaxis().SetTitleSize(0.05)
   test.GetXaxis().SetTitleFont(42)
else:
   timeStamp_tmp=[]
   timeStamp_tmp.append("10/10")
   timeStamp_tmp.append("10/10 (15 GeV)")
   timeStamp_tmp.append("10/10 (20 GeV)")
   timeStamp_tmp.append("10/10 (25 GeV)")
   timeStamp_tmp.append("10/10 (30 GeV)")   
   timeStamp_tmp.append("11/10")
   timeStamp_tmp.append("11/10 (10 GeV)")
   timeStamp_tmp.append("11/10 (15 GeV)")
   timeStamp_tmp.append("11/10 (20 GeV)")
   timeStamp_tmp.append("11/10 (25 GeV)")
   timeStamp_tmp.append("11/10 (30 GeV)")
   timeStamp_tmp.append("11/10 (old Ped)")
   timeStamp_tmp.append("11/10 (old PS)")
   timeStamp_tmp.append("11/10 (old Ped&PS)")
   for pos,x in enumerate(timeStamp_tmp):
   #for pos,x in enumerate(timeStamp_list):
      #test.GetXaxis().SetBinLabel(pos+1,str(int(x)));
      test.GetXaxis().SetBinLabel(pos+1,str(x));
      #test.GetXaxis().LabelsOption("v")
      test.GetXaxis().SetLabelFont(42)
      test.GetXaxis().SetLabelOffset(0.005)
      test.GetXaxis().SetLabelSize(0.04)
if(absTime == False):
   test.GetYaxis().SetTitle("Average Time [ns]")
else:
   test.GetYaxis().SetTitle("-(Average DB Hit-Time) [ns]")
test.GetYaxis().SetLabelFont(42)
#test.GetYaxis().SetLabelOffset(0.007)
test.GetYaxis().SetLabelSize(0.05)
test.GetYaxis().SetTitleSize(0.05)
test.GetYaxis().SetTitleOffset(0.8)
test.GetYaxis().SetTitleFont(42)
test.GetYaxis().SetLabelFont(42)
test.GetYaxis().SetRangeUser(float(y_min),float(y_max))

leg = TLegend(0.185,0.8,0.815,0.86,"","brNDC")
#leg.SetFillStyle(0)
leg.SetBorderSize(0)
leg.SetTextSize(0.04)
leg.SetFillColor(0)
leg.SetNColumns(4)
leg.AddEntry(g_EBMinus, "EB-", "P")
leg.AddEntry(g_EBPlus, "EB+", "P")
leg.AddEntry(g_EEMinus, "EE-", "P")
leg.AddEntry(g_EEPlus, "EE+", "P")

#Prompt IOVS
line_IOV1_in = TLine(1524182400,float(y_min),1524182400,float(y_max))
line_IOV1_in.SetLineColor(417)
line_IOV1_in.SetLineStyle(8)
line_IOV1_in.SetLineWidth(2)

line_IOV2_in = TLine(1524906384,float(y_min),1524906384,float(y_max))
line_IOV2_in.SetLineColor(417)
line_IOV2_in.SetLineStyle(8)
line_IOV2_in.SetLineWidth(2)

line_IOV3_in = TLine(1526403946,float(y_min),1526403946,float(y_max))
line_IOV3_in.SetLineColor(417)
line_IOV3_in.SetLineStyle(8)
line_IOV3_in.SetLineWidth(2)

line_IOV4_in = TLine(1526746800,float(y_min),1526746800,float(y_max))
line_IOV4_in.SetLineColor(417)
line_IOV4_in.SetLineStyle(8)
line_IOV4_in.SetLineWidth(2)

line_IOV5_in = TLine(1528243200,float(y_min),1528243200,float(y_max))
line_IOV5_in.SetLineColor(417)
line_IOV5_in.SetLineStyle(8)
line_IOV5_in.SetLineWidth(2)

line_IOV6_in = TLine(1530144000,float(y_min),1530144000,float(y_max))
line_IOV6_in.SetLineColor(417)
line_IOV6_in.SetLineStyle(8)
line_IOV6_in.SetLineWidth(2)

line_IOV7_in = TLine(1531008000,float(y_min),1531008000,float(y_max))
line_IOV7_in.SetLineColor(417)
line_IOV7_in.SetLineStyle(8)
line_IOV7_in.SetLineWidth(2)

line_IOV8_in = TLine(1534916924,float(y_min),1534916924,float(y_max))
line_IOV8_in.SetLineColor(417)
line_IOV8_in.SetLineStyle(8)
line_IOV8_in.SetLineWidth(2)
  
c1 = TCanvas("c1","c1",1)
c1.SetGrid()
test.Draw("H")
if(runBased == False):
   if(float(timeStamp_begin-0.001e+9)<=1524182400. and float(timeStamp_end+0.001e+9)>=1524182400.):
      line_IOV1_in.Draw("same")
   if(float(timeStamp_begin-0.001e+9)<=1524906384. and float(timeStamp_end+0.001e+9)>=1524906384.):
      line_IOV2_in.Draw("same")
   if(float(timeStamp_begin-0.001e+9)<=1526403946. and float(timeStamp_end+0.001e+9)>=1526403946.):
      line_IOV3_in.Draw("same")
   if(float(timeStamp_begin-0.001e+9)<=1526746800. and float(timeStamp_end+0.001e+9)>=1526746800.):
      line_IOV4_in.Draw("same")  
   if(float(timeStamp_begin-0.001e+9)<=1528243200. and float(timeStamp_end+0.001e+9)>=1528243200.):
      line_IOV5_in.Draw("same")  
   if(float(timeStamp_begin-0.001e+9)<=1530144000. and float(timeStamp_end+0.001e+9)>=1530144000.):
      line_IOV6_in.Draw("same")  
   if(float(timeStamp_begin-0.001e+9)<=1531008000. and float(timeStamp_end+0.001e+9)>=1531008000.):
      line_IOV7_in.Draw("same")  
   if(float(timeStamp_begin-0.001e+9)<=1534916924. and float(timeStamp_end+0.001e+9)>=1534916924.):
      line_IOV8_in.Draw("same")  
if(ix != "" and iy != "" and iz != ""):
   g_EBMinus.Draw("P,same")
elif(ix == "" and iy == "" and iz == ""):
   g_EBMinus.Draw("P,same")
   g_EBPlus.Draw("P,same")
   g_EEMinus.Draw("P,same")
   g_EEPlus.Draw("P,same")
   leg.Draw("same")

if(absTime == True):
   if(ix == "" and iy == "" and iz == ""):
      if(noEEForward == True):
         c1.SaveAs("Timing_History_"+str(year)+str(epoch)+"_noEEForward_abs.png","png")
         c1.SaveAs("Timing_History_"+str(year)+str(epoch)+"_noEEForward_abs.pdf","pdf") 
      else:
         c1.SaveAs("Timing_History_"+str(year)+str(epoch)+"_abs.png","png")
         c1.SaveAs("Timing_History_"+str(year)+str(epoch)+"_abs.pdf","pdf") 
   elif(ix != "" and iy != "" and iz != ""):
      c1.SaveAs("Timing_History_"+str(year)+str(epoch)+"_Crystal_"+ix+"_"+iy+"_"+iz+"_abs.png","png")
      c1.SaveAs("Timing_History_"+str(year)+str(epoch)+"_Crystal_"+ix+"_"+iy+"_"+iz+"_abs.pdf","pdf") 
else:
   if(ix == "" and iy == "" and iz == ""):
      if(noEEForward == True):
         c1.SaveAs("Timing_History_"+str(year)+str(epoch)+"_noEEForward.png","png")
         c1.SaveAs("Timing_History_"+str(year)+str(epoch)+"_noEEForward.pdf","pdf") 
      else:
         c1.SaveAs("Timing_History_"+str(year)+str(epoch)+".png","png")
         c1.SaveAs("Timing_History_"+str(year)+str(epoch)+".pdf","pdf") 
   elif(ix != "" and iy != "" and iz != ""):
      c1.SaveAs("Timing_History_"+str(year)+str(epoch)+"_Crystal_"+ix+"_"+iy+"_"+iz+".png","png")
      c1.SaveAs("Timing_History_"+str(year)+str(epoch)+"_Crystal_"+ix+"_"+iy+"_"+iz+".pdf","pdf") 

if(inList == ""): 
   command = os.system("rm IOVs_tmp")
   command = os.system("rm dump_tmp")
