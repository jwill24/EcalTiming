#!/usr/bin/env python

import sys, math, os, collections, getopt, subprocess, time, shutil, datetime
from ROOT import TFile, TH1, TH1F, TCanvas, TLegend, TGraph, TGraphErrors, gROOT, gPad, TAttText, TText, TGaxis, TMath, TStyle, TColor
from array import array
import os.path

def computeMean (calib, calib_err) :
   mean = 0.
   den = 0.
   for pos,x in enumerate(calib):    
      if(float(calib_err[pos]) == 0.):
         continue
      mean = mean + float(calib[pos])/(float(calib_err[pos])*float(calib_err[pos])) 
      den = den + 1./(float(calib_err[pos])*float(calib_err[pos]))  
   mean = mean/den
   return mean    

def computeError (calib_err) :
   error = 0.
   for pos,x in enumerate(calib_err):  
      if(float(calib_err[pos]) == 0.):
         continue  
      error = error + 1./(float(calib_err[pos])*float(calib_err[pos]))  
   error = 1./math.sqrt(error)
   return error    

def calibFromXML (inFile, date, icount, timeStamp_list, timeStamp_point, allCalib_list, g_EBMinus, g_EBPlus, g_EEMinus, g_EEPlus, runBased, ringMap, noEEForward, ix, iy, iz, pos_EB, ieta_EB, iphi_EB, pos_EE, ix_EE, iy_EE, iz_EE) : 
   if(inFile.find("#") != -1):
      return
   crystal_mean = -999.
   crystal_error = 0.
   with open(inFile) as f_dump:
      data_dump = f_dump.read()
      lines_dump = data_dump.splitlines()  
      EB_plus = []
      EB_minus = []
      EE_plus = []
      EE_minus = []
      for pos2,x2 in enumerate(lines_dump):
         x2 = x2.replace("<item>", "")
         x2 = x2.replace("</item>", "")
         if(pos2>7 and pos2<30608): 
            EB_minus.append(float(x2))
            if(ix != "" and iy != "" and iz != "" and iz == "0" and ieta_EB[pos_EB[pos2-8]] == ix and iphi_EB[pos_EB[pos2-8]] == iy):
               crystal_mean = float(x2)
               crystal_error = 0.
         if(pos2>30607 and pos2<61208): 
            EB_plus.append(float(x2))
            if(ix != "" and iy != "" and iz != "" and iz == "0" and ieta_EB[pos_EB[pos2-8]] == ix and iphi_EB[pos_EB[pos2-8]] == iy):
               crystal_mean = float(x2)
               crystal_error = 0.
         if(pos2>61213 and pos2<68539): 
            zside = 1
            if(int(iz_EE[pos_EE[pos2-61214]]) == -1):
               zside = 0
            ring = 0
            if(noEEForward == True and int(iz_EE[pos_EE[pos2-61214]]) != 0):
               ring = ringMap[zside][int(ix_EE[pos_EE[pos2-61214]])][int(iy_EE[pos_EE[pos2-61214]])]
            if(noEEForward == True and int(iz_EE[pos_EE[pos2-61214]]) != 0 and ring > 28):
               continue
            EE_minus.append(float(x2))
            if(ix != "" and iy != "" and iz != "" and iz != "0" and ix_EE[pos_EE[pos2-61214]] == ix and iy_EE[pos_EE[pos2-61214]] == iy and iz_EE[pos_EE[pos2-61214]] == iz):
               crystal_mean = float(x2)
               crystal_error = 0.
         if(pos2>68538 and pos2<75862): 
            zside = 1
            if(int(iz_EE[pos_EE[pos2-61214]]) == -1):
               zside = 0
            ring = 0
            if(noEEForward == True and int(iz_EE[pos_EE[pos2-61214]]) != 0):
               ring = ringMap[zside][int(ix_EE[pos_EE[pos2-61214]])][int(iy_EE[pos_EE[pos2-61214]])]
            if(noEEForward == True and int(iz_EE[pos_EE[pos2-61214]]) != 0 and ring > 28):
               continue
            EE_plus.append(float(x2)) 
            if(ix != "" and iy != "" and iz != "" and iz != "0" and ix_EE[pos_EE[pos2-61214]] == ix and iy_EE[pos_EE[pos2-61214]] == iy and iz_EE[pos_EE[pos2-61214]] == iz):
               crystal_mean = float(x2)
               crystal_error = 0.

   #fill the graph
   if(ix == "" and iy == "" and iz == ""):
      EB_p_mean = -(float(sum(EB_plus))/len(EB_plus)-9.641680121e-01)
      allCalib_list.append(float(EB_p_mean))
      EB_m_mean = -(float(sum(EB_minus))/len(EB_minus)-9.641680121e-01)
      allCalib_list.append(float(EB_m_mean))
      EE_p_mean = -(float(sum(EE_plus))/len(EE_plus)+3.476650119e-01)
      allCalib_list.append(float(EE_p_mean))
      EE_m_mean = -(float(sum(EE_minus))/len(EE_minus)+3.476650119e-01)
      allCalib_list.append(float(EE_m_mean))
   elif(ix != "" and iy != "" and iz != ""):
      allCalib_list.append(float(crystal_mean))

   if(ix == "" and iy == "" and iz == ""):
      if(runBased == False):
         print date," ---> EB+: ",EB_p_mean,", EB-:",EB_m_mean,", EE+:",EE_p_mean,", EE-:",EE_m_mean,"\n"
         timeStamp = time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
         timeStamp_list.append(float(timeStamp))
         g_EBMinus.SetPoint(icount-1,timeStamp,EB_m_mean)
         g_EBPlus.SetPoint(icount-1,timeStamp,EB_p_mean)
         g_EEMinus.SetPoint(icount-1,timeStamp,EE_m_mean)
         g_EEPlus.SetPoint(icount-1,timeStamp,EE_p_mean) 
      else:
         print int(date)," ---> EB+: ",EB_p_mean,", EB-:",EB_m_mean,", EE+:",EE_p_mean,", EE-:",EE_m_mean,"\n"
         timeStamp_list.append(date)
         timeStamp_point.append(icount-1)
         timeStamp = icount-1
         g_EBMinus.SetPoint(icount-1,timeStamp,EB_m_mean)
         g_EBPlus.SetPoint(icount-1,timeStamp,EB_p_mean)
         g_EEMinus.SetPoint(icount-1,timeStamp,EE_m_mean)
         g_EEPlus.SetPoint(icount-1,timeStamp,EE_p_mean) 
   if(ix != "" and iy != "" and iz != ""):
      if(runBased == False):
         print date," ---> (",ix,iy,iz,"): ",crystal_mean," \n"
         timeStamp = time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
         timeStamp_list.append(float(timeStamp))
         g_EBMinus.SetPoint(icount-1,timeStamp,float(crystal_mean))
      else:
         print int(date)," ---> (",ix,iy,iz,"): ",crystal_mean," \n"
         timeStamp_list.append(date)
         timeStamp_point.append(icount-1)
         timeStamp = icount-1
         g_EBMinus.SetPoint(icount-1,timeStamp,float(crystal_mean))    

def calibFromDAT (inFile, date, icount, timeStamp_list, timeStamp_point, allCalib_list, g_EBMinus, g_EBPlus, g_EEMinus, g_EEPlus, runBased, ringMap, noEEForward, ix, iy, iz) : 
   if(inFile.find("#") != -1):
      return
   crystal_mean = -999.
   crystal_error = 0.
   with open(inFile) as f_dump:
      data_dump = f_dump.read()
      lines_dump = data_dump.splitlines()  
      EB_plus = []
      EB_error_plus = []
      EB_minus = []
      EB_error_minus = []
      EE_plus = []
      EE_error_plus = []
      EE_minus = []
      EE_error_minus = []
      #fill with ICs
      for pos2,x2 in enumerate(lines_dump):
         calib = x2.split()
         if(calib[3] == "nan" or calib[3] == "-nan"):
            continue
         zside = 1
         if(int(calib[2]) == -1):
            zside = 0
         ring = 0
         if(noEEForward == True and int(calib[2]) != 0):
            ring = ringMap[zside][int(calib[1])][int(calib[0])]
         if(noEEForward == True and int(calib[2]) != 0 and ring > 28):
            continue
         if(float(calib[0])<0. and float(calib[2]) == 0.): 
            EB_minus.append(float(calib[3]))
            EB_error_minus.append(float(calib[4])/math.sqrt(int(calib[5])))
         if(float(calib[0])>0. and float(calib[2]) == 0.):
            EB_plus.append(float(calib[3]))
            EB_error_plus.append(float(calib[4])/math.sqrt(int(calib[5])))
         if(calib[2] == "-1"):
            EE_minus.append(float(calib[3]))
            EE_error_minus.append(float(calib[4])/math.sqrt(int(calib[5])))
         if(calib[2] == "1"):
            EE_plus.append(float(calib[3])) 
            EE_error_plus.append(float(calib[4])/math.sqrt(int(calib[5])))
         if(ix != "" and iy != "" and iz != "" and calib[0] == ix and calib[1] == iy and calib[2] == iz):
            crystal_mean = float(calib[3])
            crystal_error = float(calib[4])/math.sqrt(int(calib[5]))

   #fill the graph
   if(ix == "" and iy == "" and iz == ""):
      if(len(EB_plus) != 0):
         #EB_p_mean = computeMean(EB_plus,EB_error_plus)
         EB_p_mean = float(sum(EB_plus))/len(EB_plus)
         EB_p_error = computeError(EB_error_plus)
         allCalib_list.append(float(EB_p_mean))
      else:
         EB_p_mean = -999.
         EB_p_error = 0.
      if(len(EB_minus) != 0):
         #EB_m_mean = computeMean(EB_minus,EB_error_minus)
         EB_m_mean = float(sum(EB_minus))/len(EB_minus)
         EB_m_error = computeError(EB_error_minus)
         allCalib_list.append(float(EB_m_mean))
      else:
         EB_m_mean = -999.
         EB_m_error = 0.
      if(len(EE_plus) != 0):
         #EE_p_mean = computeMean(EE_plus,EE_error_plus)
         EE_p_mean = float(sum(EE_plus))/len(EE_plus)
         EE_p_error = computeError(EE_error_plus)
         allCalib_list.append(float(EE_p_mean))
      else:
         EE_p_mean = -999.
         EE_p_error = 0.
      if(len(EE_minus) != 0):
         #EE_m_mean = computeMean(EE_minus,EE_error_minus)
         EE_m_mean = float(sum(EE_minus))/len(EE_minus)
         EE_m_error = computeError(EE_error_minus)
         allCalib_list.append(float(EE_m_mean))
      else:
         EE_m_mean = -999.
         EE_m_error = 0.
   elif(ix != "" and iy != "" and iz != ""):
      if(crystal_mean != -999.):
         allCalib_list.append(float(crystal_mean))

   if(runBased == False):
      if(ix == "" and iy == "" and iz == ""):
         print date," ---> EB+: ",EB_p_mean,", EB-:",EB_m_mean,", EE+:",EE_p_mean,", EE-:",EE_m_mean,"\n"
         timeStamp = time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
         timeStamp_list.append(float(timeStamp))
         g_EBMinus.SetPoint(icount-1,timeStamp,EB_m_mean)
         #g_EBMinus.SetPointError(icount-1,0.,float(EB_m_error))
         g_EBPlus.SetPoint(icount-1,timeStamp,EB_p_mean)
         #g_EBPlus.SetPointError(icount-1,0.,float(EB_p_error))
         g_EEMinus.SetPoint(icount-1,timeStamp,EE_m_mean)
         #g_EEMinus.SetPointError(icount-1,0.,float(EE_m_error))
         g_EEPlus.SetPoint(icount-1,timeStamp,EE_p_mean)  
         #g_EEPlus.SetPointError(icount-1,0.,float(EE_p_error))
      elif(ix != "" and iy != "" and iz != ""):
         print date," ---> (",ix,iy,iz,"): ",crystal_mean,"+/-",crystal_error," \n"
         timeStamp = time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
         timeStamp_list.append(float(timeStamp))
         g_EBMinus.SetPoint(icount-1,timeStamp,float(crystal_mean))
         g_EBMinus.SetPointError(icount-1,0,float(crystal_error))
   else:
      if(ix == "" and iy == "" and iz == ""):
         print int(date)," ---> EB+: ",EB_p_mean,", EB-:",EB_m_mean,", EE+:",EE_p_mean,", EE-:",EE_m_mean,"\n"
         timeStamp_list.append(date)
         timeStamp_point.append(icount-1)
         timeStamp = icount-1
         g_EBMinus.SetPoint(icount-1,timeStamp,EB_m_mean)
         #g_EBMinus.SetPointError(icount-1,0.,float(EB_m_error))
         g_EBPlus.SetPoint(icount-1,timeStamp,EB_p_mean)
         #g_EBPlus.SetPointError(icount-1,0.,float(EB_p_error))
         g_EEMinus.SetPoint(icount-1,timeStamp,EE_m_mean)
         #g_EEMinus.SetPointError(icount-1,0.,float(EE_m_error))
         g_EEPlus.SetPoint(icount-1,timeStamp,EE_p_mean)  
         #g_EEPlus.SetPointError(icount-1,0.,float(EE_p_error))
      elif(ix != "" and iy != "" and iz != ""):
         print date," ---> (",ix,iy,iz,"): ",crystal_mean,"+/-",crystal_error," \n"
         timeStamp_list.append(date)
         timeStamp_point.append(icount-1)
         timeStamp = icount-1
         g_EBMinus.SetPoint(icount-1,timeStamp,float(crystal_mean))
         g_EBMinus.SetPointError(icount-1,0,float(crystal_error))

def makeAbsTimingXML(calib, timeIntercalib_EB, timeIntercalib_EE, pos_EB, pos_EE, crystals_EB, crystals_EE,ix,iy,iz, output) :
   with open(str(calib)) as f_interCalib:
      data_interCalib = f_interCalib.read()
   lines_interCalib = data_interCalib.splitlines() 
   for pos,x in enumerate(lines_interCalib):
      lines_interCalib_split = x.split()
      if(pos>=0 and pos<=60496): 
         if(lines_interCalib_split[3] == 'nan' or lines_interCalib_split[3] == '-nan' or abs(float(lines_interCalib_split[3]))<=(abs(float(lines_interCalib_split[4]))/math.sqrt(float(lines_interCalib_split[5])))):
            timeIntercalib_EB[lines_interCalib_split[7]]=float(0.) 
            #print "WARNING:",lines_interCalib_split[0],lines_interCalib_split[1],lines_interCalib_split[2],"- anomalous crystal, setting calibration to 0"
         else:
            timeIntercalib_EB[lines_interCalib_split[7]]=float(lines_interCalib_split[3])
         crystals_EB[lines_interCalib_split[7]] = bool(True)
      else:  
         if(lines_interCalib_split[3] == 'nan' or lines_interCalib_split[3] == '-nan' or abs(float(lines_interCalib_split[3]))<=(abs(float(lines_interCalib_split[4]))/math.sqrt(float(lines_interCalib_split[5])))):
            timeIntercalib_EE[lines_interCalib_split[7]]=float(0.) 
            #print "WARNING:",lines_interCalib_split[0],lines_interCalib_split[1],lines_interCalib_split[2],"- anomalous crystal, setting calibration to 0"
         else:
            timeIntercalib_EE[lines_interCalib_split[7]]=float(lines_interCalib_split[3])
         crystals_EE[lines_interCalib_split[7]] = bool(True)

   with open("dump_tmp") as f_dump:
      data_dump = f_dump.read()
   lines_dump = data_dump.splitlines()  

   if os.path.isfile(str(output)):
      print "WARNING: overwriting ",output
      command = os.system("rm "+str(output))
   f_tag = open(str(output),"w")
   for pos,x in enumerate(lines_dump):
       x_intro = str(x)+"\n"
       if(pos<8 or (pos>61207 and pos<61214) or pos>75861):
          x = str(x)+"\n"
          f_tag.write(x)
       elif(pos>=8 and pos<=61207): 
          x = x.replace("<item>", "")
          x = x.replace("</item>", "")
          if(abs(float(x))>10.):
             print "WARNING: ",ix[pos_EB[pos-8]],iy[pos_EB[pos-8]],iz[pos_EB[pos-8]],x,"---> Setting timing to 0!" 
             x = "0."
          else:
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
          if(abs(float(x))>10.):
             print "WARNING: ",ix[pos_EE[pos-61214]],iy[pos_EE[pos-61214]],iz[pos_EE[pos-61214]],x,"---> Setting timing to 0!" 
             x = "0."
          else:
             if(crystals_EE[pos_EE[pos-61214]] == True):
                x = float(x)-float(timeIntercalib_EE[pos_EE[pos-61214]]) 
             else:
                x = float(x) 
             x = "{:.9e}".format(x)
          x_abs = "			<item>"+str(x)+"</item> \n"
          f_tag.write(x_abs)
   f_tag.close()

def calibCompareXML (IOV, inFile1, inFile2, h_diff_EB, h_diff_EE, onlyEB, onlyEE) : 

   EB_1 = []
   EE_1 = []
   EB_2 = []
   EE_2 = []
   EB_diff = []
   EE_diff = []

   with open(inFile1) as f_dump:
      data_dump = f_dump.read()
      lines_dump = data_dump.splitlines()  
      for pos2,x2 in enumerate(lines_dump):
         x2 = x2.replace("<item>", "")
         x2 = x2.replace("</item>", "")
         if(pos2>7 and pos2<61208): 
            EB_1.append(float(x2))
         if(pos2>61213 and pos2<75862): 
            EE_1.append(float(x2))

   with open(inFile2) as f_dump:
      data_dump = f_dump.read()
      lines_dump = data_dump.splitlines()  
      for pos2,x2 in enumerate(lines_dump):
         x2 = x2.replace("<item>", "")
         x2 = x2.replace("</item>", "")
         if(pos2>7 and pos2<61208): 
            EB_2.append(float(x2))
         if(pos2>61213 and pos2<75862): 
            EE_2.append(float(x2))
   
   for pos,x in enumerate(EB_1):
      EB_diff.append(EB_1[pos]-EB_2[pos])
      h_diff_EB.Fill(EB_1[pos]-EB_2[pos])
   for pos,x in enumerate(EE_1):
      EE_diff.append(EE_1[pos]-EE_2[pos])
      h_diff_EE.Fill(EE_1[pos]-EE_2[pos])
   
   EB_mean = float(sum(EB_diff))/len(EB_diff) 
   EE_mean = float(sum(EE_diff))/len(EE_diff) 

   if(onlyEB == False and onlyEE == False):
      print IOV,": <EB diff> = ",EB_mean,", <EE diff> = ",EE_mean  
   elif(onlyEE == False):
      print IOV,": <EB diff> = ",EB_mean 
   elif(onlyEB == False):
      print IOV,": <EE diff> = ",EE_mean 
 
