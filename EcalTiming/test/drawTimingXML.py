#!/usr/bin/env python

import sys, math, os, collections, getopt, subprocess, time, shutil, datetime
from ROOT import *
from array import array

def fillMaps(ic,h2_EB,h2_EEP,h2_EEM,pos_EB,pos_EE,ieta_EB,iphi_EB,ix_EE,iy_EE,iz_EE):
   with open(ic) as f_dump:
      data_dump = f_dump.read()
      lines_dump = data_dump.splitlines()  
      for pos,x in enumerate(lines_dump):
         x = x.replace("<item>", "")
         x = x.replace("</item>", "")
         if(pos>7 and pos<61208): 
            x = float(x)-9.641680121e-01
            ieta = int(ieta_EB[pos_EB[pos-8]])+86
            iphi = int(iphi_EB[pos_EB[pos-8]])
            h2_EB.SetBinContent(iphi,ieta,x)
         if(pos>61213 and pos<75862): 
            x = float(x)+3.476650119e-01
            ix = int(ix_EE[pos_EE[pos-61214]])
            iy = int(iy_EE[pos_EE[pos-61214]])
            iz = int(iz_EE[pos_EE[pos-61214]])
            if(iz == -1):
               h2_EEM.SetBinContent(ix,iy,x)  
            if(iz == 1):
               h2_EEP.SetBinContent(ix,iy,x)

def drawH2Map(h2,labelx,labely,zmin,zmax,name):
   h2_cl = h2.Clone()
   c = TCanvas("c","c",1)
   h2_cl.GetZaxis().SetRangeUser(float(zmin),float(zmax))
   h2_cl.GetXaxis().SetTitle(str(labelx))
   h2_cl.GetYaxis().SetTitle(str(labely))
   h2_cl.Draw("COLZ")
   c.SaveAs(str(name)+".png","png")
   c.SaveAs(str(name)+".pdf","pdf") 
   h2_cl.Delete()
 
def computeMean2D(h2):
   mean=0.
   nbins=0
   for binx in range(1, h2.GetNbinsX()+1):
      for biny in range(1, h2.GetNbinsY()+1):
         if(h2.GetBinContent(binx,biny)!=0.):
            mean+=h2.GetBinContent(binx,biny)
            nbins+=1
   return mean/nbins

def moveZeros(h2):
   for binx in range(1, h2.GetNbinsX()+1):
      for biny in range(1, h2.GetNbinsY()+1):
         if(h2.GetBinContent(binx,biny)==0.):
            h2.SetBinContent(binx,biny,-999)
    
def usage():
    print "Usage: python drawTimingXML.py --tag=[tag] (--runMin=[runMin] --runMax=[runMax])"
    print "Usage: python drawTimingXML.py --payload=[payload]"
    print "Usage: python drawTimingXML.py --calib=[calib]"

#---------------------------------------------------------- MAIN ----------------------------------------------------------
def main():
    
 try:
     opts, args = getopt.getopt(sys.argv[1:], "", ["tag=","payload=","calib=","runMin=","runMax=","help"])

 except getopt.GetoptError:
     #* print help information and exit:*
     usage()
     sys.exit(2)


 tag = ""
 payload = ""
 calib = ""
 runMin = ""
 runMax = ""
 help = False

 for opt, arg in opts:
    
     if opt in ("--tag"):
        tag = arg
     if opt in ("--payload"):
        payload = arg
     if opt in ("--calib"):
        calib = arg
     if opt in ("--runMin"):
        runMin = arg
     if opt in ("--runMax"):
        runMax = arg
     if opt in ("--help"):
        help = True     

 if(help == True):
   usage()
   sys.exit(2)
 
 if(tag == "" and payload == "" and calib == ""):
   usage()
   sys.exit(2)

 if(tag != ""):
   print "tag     = ",tag
 if(runMin != ""):
   print "runMin  = ",runMin
 if(runMax != ""):
   print "runMax  = ",runMax
 if(payload != ""):
   print "payload = ",payload
 if(calib != ""):
   print "calib = ",calib 

 gROOT.SetBatch(kTRUE)

 #make crystal maps
 print "---- Making crystal maps ----"
 crystals_EB=collections.OrderedDict()
 crystals_EE=collections.OrderedDict()
 pos_EB=collections.OrderedDict()
 pos_EE=collections.OrderedDict()
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
    ieta_EB[lines_cryEB_split[0]] = lines_cryEB_split[4]
    iphi_EB[lines_cryEB_split[0]] = lines_cryEB_split[3]
   
 with open("EE_crystals.txt") as f_cryEE:
        data_cryEE = f_cryEE.read()
 lines_cryEE = data_cryEE.splitlines() 
 for pos,x in enumerate(lines_cryEE):
    lines_cryEE_split = x.split()
    crystals_EE[lines_cryEE_split[0]]=bool(False)
    pos_EE[pos]=lines_cryEE_split[0]
    ix_EE[lines_cryEE_split[0]] = lines_cryEE_split[4]
    iy_EE[lines_cryEE_split[0]] = lines_cryEE_split[5]
    iz_EE[lines_cryEE_split[0]] = lines_cryEE_split[3]
    
 print "---- Reading EE rings ----"
 ringMap={} 
 for iz in range(0,2):
  for binx in range(1,101):
   for biny in range(1,101):
     ringMap.update({(binx,biny,iz):-1}) 

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
    ringMap[(int(lines_EErings_split[0]),int(lines_EErings_split[1]),int(lines_EErings_split[2]))] = int(lines_EErings_split[3])
 
 if(payload != "" and calib == "" and tag == ""):

    print "---> Dumping the pyload: ",payload 
    command = os.system("conddb dump "+ str(payload) +" > dump_tmp")

    h2_time_EB = TH2F("h2_TimeMap_EB_abs","",360,0.5,360.5,171,-85.5,85.5)
    h2_time_EEP = TH2F("h2_TimeMap_EEP_abs","",100,0.5,100.5,100,0.5,100.5)
    h2_time_EEM = TH2F("h2_TimeMap_EEM_abs","",100,0.5,100.5,100,0.5,100.5)
    
    fillMaps("dump_tmp",h2_time_EB,h2_time_EEP,h2_time_EEM,pos_EB,pos_EE,ieta_EB,iphi_EB,ix_EE,iy_EE,iz_EE)
  
    gStyle.SetPalette(55) #55:raibow palette ; 57: kBird (blue to yellow) ; 107 kVisibleSpectrum ; 77 kDarkRainBow 
    gStyle.SetNumberContours(100) #default is 20

    gStyle.SetOptStat(0)

    print "Average timing --->",computeMean2D(h2_time_EB),computeMean2D(h2_time_EEM),computeMean2D(h2_time_EEP)
 
    moveZeros(h2_time_EB)
    drawH2Map(h2_time_EB,"i#phi","i#eta",-5,5,"TimeMap_EB_abs") 
    moveZeros(h2_time_EEP)
    drawH2Map(h2_time_EEP,"ix","iy",-7,7,"TimeMap_EEP_abs") 
    moveZeros(h2_time_EEM)
    drawH2Map(h2_time_EEM,"ix","iy",-7,7,"TimeMap_EEM_abs") 

    command = os.system("rm dump_tmp")
   
 elif(payload == "" and calib != "" and tag == ""):

    h2_time_EB = TH2F("h2_TimeMap_EB_abs","",360,0.5,360.5,171,-85.5,85.5)
    h2_time_EEP = TH2F("h2_TimeMap_EEP_abs","",100,0.5,100.5,100,0.5,100.5)
    h2_time_EEM = TH2F("h2_TimeMap_EEM_abs","",100,0.5,100.5,100,0.5,100.5)
    
    fillMaps(calib,h2_time_EB,h2_time_EEP,h2_time_EEM,pos_EB,pos_EE,ieta_EB,iphi_EB,ix_EE,iy_EE,iz_EE)
  
    gStyle.SetPalette(55) #55:raibow palette ; 57: kBird (blue to yellow) ; 107 kVisibleSpectrum ; 77 kDarkRainBow 
    gStyle.SetNumberContours(100) #default is 20

    gStyle.SetOptStat(0)

    print "Average timing --->",computeMean2D(h2_time_EB),computeMean2D(h2_time_EEM),computeMean2D(h2_time_EEP)
 
    moveZeros(h2_time_EB)
    drawH2Map(h2_time_EB,"i#phi","i#eta",-5,5,"TimeMap_EB_abs") 
    moveZeros(h2_time_EEP)
    drawH2Map(h2_time_EEP,"ix","iy",-7,7,"TimeMap_EEP_abs") 
    moveZeros(h2_time_EEM)
    drawH2Map(h2_time_EEM,"ix","iy",-7,7,"TimeMap_EEM_abs") 

    command = os.system("rm dump_tmp")
    
 elif(payload == "" and calib == "" and tag != ""):

   print "---- Dumping IOVs ----"

   command = os.system("conddb list "+str(tag)+" > IOVs_tmp")
   with open("IOVs_tmp") as f_IOVs:
      data_IOVs = f_IOVs.read()
      lines_IOVs = data_IOVs.splitlines()
      for pos,x in enumerate(lines_IOVs):
         if(pos > 2 and pos < len(lines_IOVs)-1):
            print "\n",x
            line_IOVs_split = lines_IOVs[pos].split()
            IOV_time = line_IOVs_split[2].split("-")
            date = IOV_time[2]+"/"+IOV_time[1]+"/"+IOV_time[0]
            run = line_IOVs_split[0]

            if(run<runMin or run>runMax and (runMin!="" and runMax!="")):
               continue

            command = os.system("conddb dump "+ str(line_IOVs_split[5]) +" > dump_tmp")

            h2_time_EB = TH2F("h2_TimeMap_EB_abs_"+str(run),"",360,0.5,360.5,171,-85.5,85.5)
            h2_time_EEP = TH2F("h2_TimeMap_EEP_abs_"+str(run),"",100,0.5,100.5,100,0.5,100.5)
            h2_time_EEM = TH2F("h2_TimeMap_EEM_abs_"+str(run),"",100,0.5,100.5,100,0.5,100.5)

            fillMaps("dump_tmp",h2_time_EB,h2_time_EEP,h2_time_EEM,pos_EB,pos_EE,ieta_EB,iphi_EB,ix_EE,iy_EE,iz_EE)

            gStyle.SetPalette(55) #55:raibow palette ; 57: kBird (blue to yellow) ; 107 kVisibleSpectrum ; 77 kDarkRainBow 
            gStyle.SetNumberContours(100) #default is 20
            gStyle.SetOptStat(0)

            print "Average timing: ",run,"--->",computeMean2D(h2_time_EB),computeMean2D(h2_time_EEM),computeMean2D(h2_time_EEP)
 
            moveZeros(h2_time_EB)
            drawH2Map(h2_time_EB,"i#phi","i#eta",-5,5,"TimeMap_EB_abs_"+str(run)) 
            moveZeros(h2_time_EEP)
            drawH2Map(h2_time_EEP,"ix","iy",-7,7,"TimeMap_EEP_abs_"+str(run)) 
            moveZeros(h2_time_EEM)
            drawH2Map(h2_time_EEM,"ix","iy",-7,7,"TimeMap_EEM_abs_"+str(run)) 

            #h2_time_EB.delete()
            #h2_time_EEP.delete()
            #h2_time_EEM.delete()

            command = os.system("rm dump_tmp")
  
   command = os.system("rm IOVs_tmp")

if __name__ == "__main__":
    main()



