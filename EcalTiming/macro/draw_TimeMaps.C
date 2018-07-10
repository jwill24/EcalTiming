#include "TFile.h"
#include "TStyle.h"
#include "TH1.h"
#include "TH2.h"
#include "TTree.h" 
#include "TCanvas.h"
#include "TLegend.h"
#include "TColor.h"
#include "TLatex.h"
#include "TGraphAsymmErrors.h"
#include "TGaxis.h"
#include "TPaletteAxis.h"
#include "TProfile.h"
#include "TProfile2D.h"

#include<iostream>
#include<string>
#include<fstream>

float getMean(TProfile2D* p2);

void draw_TimeMaps() {
  
  gStyle->SetOptStat(0);
  gROOT->SetBatch(kTRUE);
  // inputs
  TFile* inFile = TFile::Open("/eos/cms/store/group/dpg_ecal/alca_ecalcalib/EcalTiming/Run2018C/Calibration/319349_319437_319439_319444_319449/ecalTiming.root");
  TProfile2D* t2_TimeMap_EB = (TProfile2D*)inFile->Get("TimeMapEB");
  t2_TimeMap_EB->GetZaxis()->SetRangeUser(-1,1);
  
  TProfile2D* t2_TimeMap_EEP = (TProfile2D*)inFile->Get("TimeMapEEP");
  t2_TimeMap_EEP->GetZaxis()->SetRangeUser(-3,3);

  TProfile2D* t2_TimeMap_EEM = (TProfile2D*)inFile->Get("TimeMapEEM");
  t2_TimeMap_EEM->GetZaxis()->SetRangeUser(-3,3);

  TProfile2D* t2_RingTimeMap_EB = (TProfile2D*)inFile->Get("RingTimeMapEB");
  TProfile2D* t2_RingTimeMap_EEP = (TProfile2D*)inFile->Get("RingTimeMapEEP");
  TProfile2D* t2_RingTimeMap_EEM = (TProfile2D*)inFile->Get("RingTimeMapEEM");

  TProfile2D* t2_Occupancy_EB = (TProfile2D*)inFile->Get("OccupancyEB");
  TProfile2D* t2_Occupancy_EEP = (TProfile2D*)inFile->Get("OccupancyEEP");
  TProfile2D* t2_Occupancy_EEM = (TProfile2D*)inFile->Get("OccupancyEEM");

  TProfile2D* t2_TimeErrorMap_EB = (TProfile2D*)inFile->Get("TimeErrorMapEB");
  TProfile2D* t2_TimeErrorMap_EEP = (TProfile2D*)inFile->Get("TimeErrorMapEEP");
  TProfile2D* t2_TimeErrorMap_EEM = (TProfile2D*)inFile->Get("TimeErrorMapEEM");

  TProfile* t1_BXTime_EB = (TProfile*)((TProfile*)inFile->Get("BXTimeEB"))->Clone("t1_BXTime_EB");
  t1_BXTime_EB->GetYaxis()->SetRangeUser(-1,1);

  TProfile* t1_BXTime_EB_zoomed = (TProfile*)((TProfile*)inFile->Get("BXTimeEB"))->Clone("t1_BXTime_EB_zoomed");
  t1_BXTime_EB_zoomed->GetXaxis()->SetRangeUser(0,500);
  t1_BXTime_EB_zoomed->GetYaxis()->SetRangeUser(-1,1);

  TProfile* t1_BXTime_EB_13ADC = (TProfile*)((TProfile*)inFile->Get("BXTimeEB"))->Clone("t1_BXTime_EB_13ADC");
  t1_BXTime_EB_13ADC->SetLineColor(kBlue+1);
  t1_BXTime_EB_13ADC->SetMarkerColor(kBlue+1);

  TProfile* t1_BXTime_EB_3GeV = (TProfile*)((TProfile*)inFile->Get("BXTimeEB_3GeV"))->Clone("t1_BXTime_EB_3GeV");
  t1_BXTime_EB_3GeV->SetLineColor(kRed+1);
  t1_BXTime_EB_3GeV->SetMarkerColor(kRed+1);

  TProfile* t1_BXTime_EB_4GeV = (TProfile*)((TProfile*)inFile->Get("BXTimeEB_4GeV"))->Clone("t1_BXTime_EB_4GeV");
  t1_BXTime_EB_4GeV ->SetLineColor(kGreen+1);
  t1_BXTime_EB_4GeV ->SetMarkerColor(kGreen+1);

  TProfile* t1_BXTime_EB_5GeV = (TProfile*)((TProfile*)inFile->Get("BXTimeEB_5GeV"))->Clone("t1_BXTime_EB_5GeV");
  t1_BXTime_EB_5GeV->SetLineColor(kViolet+1);
  t1_BXTime_EB_5GeV->SetMarkerColor(kViolet+1);
  
  TProfile* t1_BXTime_EEP = (TProfile*)inFile->Get("BXTimeEEP");
  t1_BXTime_EEP->GetYaxis()->SetRangeUser(-1,1.);

  TProfile* t1_BXTime_EEM = (TProfile*)inFile->Get("BXTimeEEM");
  t1_BXTime_EEM->GetYaxis()->SetRangeUser(-1.,1.);

  TProfile* t1_BXTime_EB_Num = (TProfile*)inFile->Get("BXTimeEB_Num");
  TProfile* t1_BXTime_EEP_Num = (TProfile*)inFile->Get("BXTimeEEP_Num");
  TProfile* t1_BXTime_EEM_Num = (TProfile*)inFile->Get("BXTimeEEM_Num");

  TH1F* h1_RechitTimeEB = (TH1F*)inFile->Get("RechitTimeEB");
  TH1F* h1_RechitTimeEEP = (TH1F*)inFile->Get("RechitTimeEEP");
  TH1F* h1_RechitTimeEEM = (TH1F*)inFile->Get("RechitTimeEEM");
  
  std::cout << "EB mean: " << getMean(t2_TimeMap_EB) << std::endl;
  std::cout << "EEP mean: " << getMean(t2_TimeMap_EEP) << std::endl;
  std::cout << "EEM mean: " << getMean(t2_TimeMap_EEM) << std::endl;
  
  
  TCanvas* c1 = new TCanvas("c1","c1",1);
  t2_TimeMap_EB->Draw("COLZ");
  c1->SaveAs("TimeMap_EB.png","png");
  c1->SaveAs("TimeMap_EB.pdf","pdf"); 

  TCanvas* c2 = new TCanvas("c2","c2",1);
  t2_TimeMap_EEP->Draw("COLZ");
  c2->SaveAs("TimeMap_EEP.png","png");
  c2->SaveAs("TimeMap_EEP.pdf","pdf"); 

  TCanvas* c3 = new TCanvas("c3","c3",1);
  t2_TimeMap_EEM->Draw("COLZ");
  c3->SaveAs("TimeMap_EEM.png","png");
  c3->SaveAs("TimeMap_EEM.pdf","pdf"); 

  TCanvas* c4 = new TCanvas("c4","c4",1);
  t2_RingTimeMap_EB->Draw("COLZ");
  c4->SaveAs("TimeMap_Ring_EB.png","png");
  c4->SaveAs("TimeMap_Ring_EB.pdf","pdf"); 

  TCanvas* c5 = new TCanvas("c5","c5",1);
  t2_RingTimeMap_EEP->Draw("COLZ");
  c5->SaveAs("TimeMap_Ring_EEP.png","png");
  c5->SaveAs("TimeMap_Ring_EEP.pdf","pdf"); 

  TCanvas* c6 = new TCanvas("c6","c6",1);
  t2_RingTimeMap_EEM->Draw("COLZ");
  c6->SaveAs("TimeMap_Ring_EEM.png","png");
  c6->SaveAs("TimeMap_Ring_EEM.pdf","pdf"); 

  TCanvas* c7 = new TCanvas("c7","c7",1);
  t2_Occupancy_EB->Draw("COLZ");
  c7->SaveAs("Occupancy_EB.png","png");
  c7->SaveAs("Occupancy_EB.pdf","pdf"); 

  TCanvas* c8 = new TCanvas("c8","c8",1);
  t2_Occupancy_EEP->Draw("COLZ");
  c8->SaveAs("Occupancy_EEP.png","png");
  c8->SaveAs("Occupancy_EEP.pdf","pdf"); 

  TCanvas* c9 = new TCanvas("c9","c9",1);
  t2_Occupancy_EEM->Draw("COLZ");
  c9->SaveAs("Occupancy_EEM.png","png");
  c9->SaveAs("Occupancy_EEM.pdf","pdf"); 

  TCanvas* c10 = new TCanvas("c10","c10",1);
  t2_TimeErrorMap_EB->Draw("COLZ");
  c10->SaveAs("TimeErrorMap_EB.png","png");
  c10->SaveAs("TimeErrorMap_EB.pdf","pdf"); 

  TCanvas* c11 = new TCanvas("c11","c11",1);
  t2_TimeErrorMap_EEP->Draw("COLZ");
  c11->SaveAs("TimeErrorMap_EEP.png","png");
  c11->SaveAs("TimeErrorMap_EEP.pdf","pdf"); 

  TCanvas* c12 = new TCanvas("c12","c12",1);
  t2_TimeErrorMap_EEM->Draw("COLZ");
  c11->SaveAs("TimeErrorMap_EEM.png","png");
  c11->SaveAs("TimeErrorMap_EEM.pdf","pdf"); 

  TCanvas* c13 = new TCanvas("c13","c13",1);
  c13->SetGrid();
  t1_BXTime_EB->Draw();
  c13->SaveAs("Time_BX_EB.png","png");
  c13->SaveAs("Time_BX_EB.pdf","pdf"); 

  TCanvas* c14 = new TCanvas("c14","c14",1);
  t1_BXTime_EEP->Draw();
  c14->SaveAs("Time_BX_EEP.png","png");
  c14->SaveAs("Time_BX_EEP.pdf","pdf"); 

  TCanvas* c15 = new TCanvas("c15","c15",1);
  t1_BXTime_EEM->Draw();
  c15->SaveAs("Time_BX_EEM.png","png");
  c15->SaveAs("Time_BX_EEM.pdf","pdf"); 

  TCanvas* c16 = new TCanvas("c16","c16",1);
  t1_BXTime_EB_Num->Draw();
  c16->SaveAs("Time_BX_Occupancy_EB.png","png");
  c16->SaveAs("Time_BX_Occupancy_EB.pdf","pdf"); 

  TCanvas* c17 = new TCanvas("c17","c17",1);
  t1_BXTime_EEP_Num->Draw();
  c17->SaveAs("Time_BX_Occupancy_EEP.png","png");
  c17->SaveAs("Time_BX_Occupancy_EEP.pdf","pdf"); 

  TCanvas* c18 = new TCanvas("c18","c18",1);
  t1_BXTime_EEM_Num->Draw();
  c18->SaveAs("Time_BX_Occupancy_EEM.png","png");
  c18->SaveAs("Time_BX_Occupancy_EEM.pdf","pdf"); 

  TLegend *leg;
  leg = new TLegend(0.18,0.70,0.38,0.90);
  leg->SetFillStyle(0);
  leg->SetBorderSize(0);
  leg->SetTextSize(0.03);
  leg->SetFillColor(0);
  leg->AddEntry(t1_BXTime_EB_13ADC, "E > 2 GeV", "l");
  leg->AddEntry(t1_BXTime_EB_3GeV, "E > 3 GeV", "l");
  leg->AddEntry(t1_BXTime_EB_4GeV, "E > 4 GeV", "l");
  leg->AddEntry(t1_BXTime_EB_5GeV, "E > 5 GeV", "l");

  TCanvas* c19 = new TCanvas("c19","c19",1);
  c19->SetGrid();
  t1_BXTime_EB->Draw();
  t1_BXTime_EB_3GeV->Draw("same");
  t1_BXTime_EB_4GeV->Draw("same");
  t1_BXTime_EB_5GeV->Draw("same");
  leg->Draw("same");
  c19->SaveAs("Time_BX_EB_thresholds.png","png");
  c19->SaveAs("Time_BX_EB_thresholds.pdf","pdf");

  TCanvas* c20 = new TCanvas("c20","c20",1);
  c20->SetGrid();
  t1_BXTime_EB_zoomed->Draw();
  c20->SaveAs("Time_BX_EB_zoomed.png","png");
  c20->SaveAs("Time_BX_EB_zoomed.pdf","pdf"); 

  t1_BXTime_EB_13ADC->GetXaxis()->SetRangeUser(0,500);
  t1_BXTime_EB_13ADC->GetYaxis()->SetRangeUser(-0.1,0.5);

  TCanvas* c21 = new TCanvas("c21","c21",1);
  c21->SetGrid();
  t1_BXTime_EB_13ADC->Draw();
  t1_BXTime_EB_3GeV->Draw("same");
  t1_BXTime_EB_4GeV->Draw("same");
  t1_BXTime_EB_5GeV->Draw("same");
  leg->Draw("same");
  c21->SaveAs("Time_BX_EB_thresholds_zoomed.png","png");
  c21->SaveAs("Time_BX_EB_thresholds_zoomed.pdf","pdf");

  gStyle->SetOptStat(1);

  h1_RechitTimeEB->Rebin(10);
  h1_RechitTimeEB->GetXaxis()->SetRangeUser(-3.,3.);
  TCanvas* c22 = new TCanvas("c22","c22",1);
  h1_RechitTimeEB->Draw(); 
  c22->SaveAs("Time_EB.png","png");
  c22->SaveAs("Time_EB.pdf","pdf");

  h1_RechitTimeEEP->Rebin(10);
  h1_RechitTimeEEP->GetXaxis()->SetRangeUser(-3.,3.);
  TCanvas* c23 = new TCanvas("c23","c23",1);
  h1_RechitTimeEEP->Draw(); 
  c23->SaveAs("Time_EEP.png","png");
  c23->SaveAs("Time_EEP.pdf","pdf");

  h1_RechitTimeEEM->Rebin(10);
  h1_RechitTimeEEM->GetXaxis()->SetRangeUser(-3.,3.);
  TCanvas* c24 = new TCanvas("c24","c24",1);
  h1_RechitTimeEEM->Draw(); 
  c24->SaveAs("Time_EEM.png","png");
  c24->SaveAs("Time_EEM.pdf","pdf");

}

float getMean(TProfile2D* p2) {

  float mean = 0.;
  int num = 0;
  for(int ii = 1; ii <= p2->GetNbinsX(); ii++)
      for(int jj = 1; jj <= p2->GetNbinsY(); jj++) {

          //std::cout << ii << " " << jj << " " << p2->GetBinContent(ii,jj) << std::endl;
          //if(ii == 19 && jj == 17) continue;
          if(p2->GetBinContent(ii,jj) != 0) num++;
          if(p2->GetBinContent(ii,jj) != 0) mean += p2->GetBinContent(ii,jj);    
      }
   
  //std::cout << mean << " " << num << std::endl;
  return mean/(float)num;       
}
