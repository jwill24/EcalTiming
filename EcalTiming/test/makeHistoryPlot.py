#!/usr/bin/env python

import sys, math, os, collections, getopt, subprocess, time, shutil, datetime
from ROOT import TFile, TH1, TH1F, TLine, TCanvas, TLegend, TGraph, TGraphErrors, gROOT, gPad, TAttText, TText, TGaxis, TMath, TStyle, TColor
from array import array
from historyPlot_utils import calibFromXML
from historyPlot_utils import calibFromDAT

def usage():
    print "Usage: python makeHistoryPlot.py --tag=[tag] --year=[year] (--run=[run] --absTime)"
    print "Usage: python makeHistoryPlot.py --inList=[inList] (--run=[run] --absTime)"
    
try:
     opts, args = getopt.getopt(sys.argv[1:], "t:y:i:r:ah", ["tag=","year=","inList=","run=","absTime","help"])

except getopt.GetoptError:
     #* print help information and exit:*
     usage()
     sys.exit(2)


tag = ""
year = ""
run = ""
inList = ""
absTime = False
help = False
for opt, arg in opts:
    
     if opt in ("--tag"):
        tag = arg
     if opt in ("--year"):
        year = arg
     if opt in ("--run"):
        run = arg
     if opt in ("--inList"):
        inList = arg  
     if opt in ("--absTime"):
        absTime = True    
     if opt in ("--help"):
        help = True     

if(help == True):
   usage()
   sys.exit(2)

if((tag == "" and year == "" and run == "" and inList == "") or (tag != "" and year == "") or (tag == "" and year != "")):
   usage()
   sys.exit(2)

if(tag != ""):
   print "tag          = ",tag
if(year != ""):
   print "year         = ",year
if(run != ""):
   print "run          = ",run
if(inList != ""):
   print "inList       = ",inList  
if(absTime == True):
   print "absTime      = ",absTime  

#gStyle.SetOptStat(0)

g_EBMinus = TGraphErrors()
g_EBPlus = TGraphErrors()
g_EEMinus = TGraphErrors()
g_EEPlus = TGraphErrors()

timeStamp_begin=0
timeStamp_end=0
date_begin=""
date_end=""

timeStamp_list=[]
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
            calibFromXML(lines_interCalib[pos], date, icount, timeStamp_list, allCalib_list, g_EBMinus, g_EBPlus, g_EEMinus, g_EEPlus)
         if(interCalib_time[3].find(".dat") != -1):
            date = interCalib_time[3].replace(".dat", "")+"/"+interCalib_time[2]+"/"+interCalib_time[1]
            calibFromDAT(lines_interCalib[pos], date, icount, timeStamp_list, allCalib_list, g_EBMinus, g_EBPlus, g_EEMinus, g_EEPlus)

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
               calibFromXML("dump_tmp", date, icount, timeStamp_list, allCalib_list, g_EBMinus, g_EBPlus, g_EEMinus, g_EEPlus)

timeStamp_begin = timeStamp_list[0]
timeStamp_end = timeStamp_list[len(timeStamp_list)-1]

allCalib_list.sort()
y_min = allCalib_list[0]-0.05
y_max = allCalib_list[len(allCalib_list)-1]+0.3

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

if(absTime == False):
   test = TH1F("test","Ecal Timing ["+str(year)+str(run)+"]",1000,float(timeStamp_begin-172800),float(timeStamp_end+172800))
else:
   test = TH1F("test","Ecal Absolute Timing ["+str(year)+str(run)+"]",1000,float(timeStamp_begin-172800),float(timeStamp_end+172800))
test.SetStats(0)
test.SetFillColor(1)
test.SetFillStyle(3004)
test.SetLineColor(0)
test.SetLineWidth(3)
test.SetMarkerStyle(20)
test.GetXaxis().SetTitle("date")
test.GetXaxis().SetTimeDisplay(1)
test.GetXaxis().SetTimeFormat("%d/%m%F1970-01-01 00:00:00s0")
test.GetXaxis().SetNdivisions(512)
test.GetXaxis().SetLabelFont(42)
test.GetXaxis().SetLabelOffset(0.007)
test.GetXaxis().SetLabelSize(0.04)
test.GetXaxis().SetTitleSize(0.05)
test.GetXaxis().SetTitleFont(42)
if(absTime == False):
   test.GetYaxis().SetTitle("Average Time [ns]")
else:
   test.GetYaxis().SetTitle("Absolute Time [ns]")
test.GetYaxis().SetLabelFont(42)
test.GetYaxis().SetLabelOffset(0.007)
test.GetYaxis().SetLabelSize(0.05)
test.GetYaxis().SetTitleSize(0.05)
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
line_IOV1_calib = TLine(1494460800,float(y_min),1494460800,float(y_max))
line_IOV1_calib.SetLineColor(633)
line_IOV1_calib.SetLineStyle(8)
line_IOV1_calib.SetLineWidth(2)

line_IOV1_inBad = TLine(1494806400,float(y_min),1494806400,float(y_max))
line_IOV1_inBad.SetLineColor(880)
line_IOV1_inBad.SetLineStyle(8)
line_IOV1_inBad.SetLineWidth(2)

line_IOV1_in = TLine(1496880000,float(y_min),1496880000,float(y_max))
line_IOV1_in.SetLineColor(417)
line_IOV1_in.SetLineStyle(8)
line_IOV1_in.SetLineWidth(2)

line_IOV2_calib = TLine(1497744000,float(y_min),1497744000,float(y_max))
line_IOV2_calib.SetLineColor(633)
line_IOV2_calib.SetLineStyle(8)
line_IOV2_calib.SetLineWidth(2)

line_IOV2_in = TLine(1498780800,float(y_min),1498780800,float(y_max))
line_IOV2_in.SetLineColor(417)
line_IOV2_in.SetLineStyle(8)
line_IOV2_in.SetLineWidth(2)

line_IOV3_calib = TLine(1500508800,float(y_min),1500508800,float(y_max))
line_IOV3_calib.SetLineColor(633)
line_IOV3_calib.SetLineStyle(8)
line_IOV3_calib.SetLineWidth(2)

line_IOV3_in = TLine(1501459200,float(y_min),1501459200,float(y_max))
line_IOV3_in.SetLineColor(417)
line_IOV3_in.SetLineStyle(8)
line_IOV3_in.SetLineWidth(2)

line_IOV4_calib = TLine(1502064000,float(y_min),1502064000,float(y_max))
line_IOV4_calib.SetLineColor(633)
line_IOV4_calib.SetLineStyle(8)
line_IOV4_calib.SetLineWidth(2)

line_IOV4_in = TLine(1503273600,float(y_min),1503273600,float(y_max))
line_IOV4_in.SetLineColor(417)
line_IOV4_in.SetLineStyle(8)
line_IOV4_in.SetLineWidth(2)
  
c1 = TCanvas("c1","c1",1)
c1.SetGrid()
test.Draw("H")
if(float(timeStamp_begin-0.001e+9)<=1494460800. and float(timeStamp_end+0.001e+9)>=1494460800.):
   line_IOV1_calib.Draw("same")
if(float(timeStamp_begin-0.001e+9)<=1494806400. and float(timeStamp_end+0.001e+9)>=1494806400.):
   line_IOV1_inBad.Draw("same")
if(float(timeStamp_begin-0.001e+9)<=1496880000. and float(timeStamp_end+0.001e+9)>=1496880000.):
   line_IOV1_in.Draw("same")
if(float(timeStamp_begin-0.001e+9)<=1497744000. and float(timeStamp_end+0.001e+9)>=1497744000.):
   line_IOV2_calib.Draw("same")
if(float(timeStamp_begin-0.001e+9)<=1498780800. and float(timeStamp_end+0.001e+9)>=1498780800.):
   line_IOV2_in.Draw("same")
if(float(timeStamp_begin-0.001e+9)<=1500508800. and float(timeStamp_end+0.001e+9)>=1500508800.):
   line_IOV3_calib.Draw("same")
if(float(timeStamp_begin-0.001e+9)<=1501459200. and float(timeStamp_end+0.001e+9)>=1501459200.):
   line_IOV3_in.Draw("same")
if(float(timeStamp_begin-0.001e+9)<=1502064000. and float(timeStamp_end+0.001e+9)>=1502064000.):
   line_IOV4_calib.Draw("same")
if(float(timeStamp_begin-0.001e+9)<=1503273600. and float(timeStamp_end+0.001e+9)>=1503273600.):
   line_IOV4_in.Draw("same")
g_EBMinus.Draw("P,same")
g_EBPlus.Draw("P,same")
g_EEMinus.Draw("P,same")
g_EEPlus.Draw("P,same")
leg.Draw("same")
c1.SaveAs("Timing_History_"+str(year)+str(run)+".png","png")
c1.SaveAs("Timing_History_"+str(year)+str(run)+".pdf","pdf") 

if(inList == ""): 
   command = os.system("rm IOVs_tmp")
   command = os.system("rm dump_tmp")
