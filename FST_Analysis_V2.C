////////////////////////////////////
// This is 2nd Version of the Full System Test Analysis script, update 24/04/19.
// Harvey Birch 
// harveyjohnbirch@gmail.com 
//
// To run the analysis, use the following terminal command:
// $ root -l FST_Analysis_V2.C+(\"PB##file.root\",##);
// REPLACE ## with respective pulser board number in file name.
////////////////////////////////////

#include "TH2F.h"
#include "TH1F.h"
#include "TCanvas.h"
#include "TTree.h"
#include <iostream>
#include "TProfile.h"
#include "TGraphErrors.h"
#include <cmath>
#include <cstdio>
#include "TROOT.h"
#include "TStyle.h"
#include "TPaveText.h"
#include "TPaveLabel.h"
#include "TPad.h"
#include "TFile.h"
#include "TF1.h"
#include "TAxis.h"
#include "TMath.h"
#include "TPaveStats.h"
#include "TObject.h"
#include "TString.h"
#include "TGraph.h"
#include "TH1.h"
#include "TRandom.h"
#include "TLine.h"

using namespace std;

Double_t fitf_TWNPH(Double_t *x,Double_t *par);

Double_t fitf_TWNPH(Double_t *x,Double_t *par) 
{
  Double_t arg = x[0];
  Double_t fitval_TWNPH = par[0] + TMath::Exp(par[1]*arg + par[2]*arg*arg);
  return fitval_TWNPH;
} 

void FST_Analysis_V2(char* filename, int board);

void FST_Analysis_V2(char* filename, int board)
{

  TFile *_file0 = TFile::Open(filename);
  TTree* tree = (TTree*)_file0->Get("tree");

  char titlename[30];
  sprintf(titlename,"PB%02d",board);

  const float maxNph = 300.e3;

  const int nPointsLarge = 19;   // number of scan points was originally 8
  const int nPointsSmall = 64;   // number of scan points was originally 8
  const int nPointsTot = nPointsLarge * nPointsSmall;
  const int startPointLarge = 10;
  const int startPointSmall = 1;
  
  TCanvas *c1 = new TCanvas("c1", "c1",800,1500);
  TPaveLabel* title = new TPaveLabel(0.1,0.96,0.9,0.99,titlename);
  title->Draw();
  gStyle->SetOptFit(kTRUE);

  int nRows = (int)round((float)(nPointsLarge-startPointLarge) / 2.);
  TPad* graphPad = new TPad("Graphs","Graphs",0.01,0.05,0.95,0.95);
  graphPad->Draw();
  graphPad->cd();
  graphPad->Divide(2,nRows);

  float nphPMT[nPointsTot]; //number of photos at PMT
  float ernphPMT[nPointsTot]; // uncertainties of nphPMT

  float lnphPMT[nPointsTot]; //number of photos at PMT
  float erlnphPMT[nPointsTot]; // uncertainties of nphPMT

  float trigW[nPointsTot]; //trigger width
  float ertrigW[nPointsTot]; //uncertainties of trigw
  float trigWres[nPointsTot]; //trigger width calculated residuals

  float pw[nPointsTot]; //pulse width
  float erpw[nPointsTot]; // uncertainties of pw
  float pwMax = 0.0; // Max pulse width

  float widthsetlarge[nPointsTot];
  float widthsetsmall[nPointsTot];
  float widthsetdec[nPointsTot];

  float vref[nPointsTot];


  //const float maxPD = 2.0; //was previously set to 2
  //float pd[nPointsTot]; //photodiode board output
  //float erpd[nPointsTot]; // uncertainties of pd

  int i_looped = 0;

  for (int ipoint = 0; ipoint < nPointsLarge; ipoint++){
    for (int jpoint = 0; jpoint < nPointsSmall; jpoint++){
      

      int trigSetLarge = startPointLarge + ipoint;  // trigger set 1 ~ 5ns
      int trigSetSmall = startPointSmall + jpoint;

      graphPad->cd(ipoint+1);
      
      char selection[70];

      if ((board==1 || board==9 || board==17 || board==25) && trigSetLarge > 4){
	sprintf(selection,"widthsetLarge==%d&&widthsetSmall==%d&&amp2<-40&&width2<40&&width2>3",trigSetLarge, trigSetSmall); // widthset is the trigger width set and pulseWidth is the pulse width.
      } 
      else {
	sprintf(selection,"widthsetLarge==%d&&widthsetSmall==%d&&amp2<-10&&width2<40&&width2>2",trigSetLarge, trigSetSmall); // widthset is the trigger width set and pulseWidth is the pulse width.
      }

      TH1F* trwHist = new TH1F("trwHist","",200,0.,200); // values for the trigger width graph
      tree->Draw("width1>>trwHist",selection,""); //trigWidth -> width1
      float nEntries = trwHist->GetEntries();
      if (nEntries < 1) continue;
      float trwMean=trwHist->GetMean();
      float ertrwSigma=trwHist->GetRMS();
      trigW[i_looped] = trwMean;
      ertrigW[i_looped] = ertrwSigma;
      std::cout << "trigW=" << trwMean << std::endl;

      TH1F* pwHist = new TH1F("pwHist","",100,0.,100); // values for the pulse width graph
      tree->Draw("width2>>pwHist",selection,""); //pulseWidth -> width2
      float pwMean=pwHist->GetMean();
      float erpwSigma=pwHist->GetRMS();
      pw[i_looped] = pwMean;
      erpw[i_looped] = erpwSigma;
      if (pwMean > pwMax) pwMax = pwMean;
      std::cout << "pwMean=" << pwMean << std::endl;

      TH1F* LargeWHist = new TH1F("LargeWHist","",20,0.,20.);
      tree->Draw("widthsetLarge>>LargeWHist",selection,""); 
      float LargeWval = trigSetLarge;
      widthsetlarge[i_looped] = LargeWval;
      std::cout << "Large Width: " <<  LargeWval << endl;      

      TH1F* SmallWHist = new TH1F("SmallWHist","",20,0.,20.);
      tree->Draw("widthsetSmall>>SmallWHist",selection,""); 
      float trigSetSmallf = trigSetSmall; 
      float SmallWval = (trigSetSmallf/64);
      widthsetsmall[i_looped] = SmallWval;
      std::cout << "Small Width: " <<  SmallWval << endl;

      float widthsetdecVal = LargeWval + SmallWval;
      widthsetdec[i_looped] = widthsetdecVal;
      std::cout << "Calc Width: " <<  widthsetdecVal << endl;

      /*
      TH1F* vrefHist = new TH1F("vrefHist","",1000,0.,1.);
      tree->Draw("vref>>vrefHist",selection,""); 
      float vrefval=vrefHist->GetMean();
      vref[i_looped] = vrefval;
      std::cout << "vref: " <<  vrefval << endl;      
      */    
      TH1F* npHist = new TH1F("npHist","",10000,0.,maxNph); // number of photons in a given scan point
      tree->Draw("nph>>npHist",selection,""); 
      float nphMean=npHist->GetMean();
      /* 
	 DON'T HAVE A Photodiode READ BACK ON NEW FIRMWARE/TESTING CODE
	 TH1F* pdHist = new TH1F("pdHist","",1000,0.,maxPD); // PD in a given scan point
	 tree->Draw("pdReadingCh1>>pdHist",selection,""); //pdReadingCh1 is not a leaf in the new tree
	 float pdMean=pdHist->GetMean();
	 float pdSigma=pdHist->GetRMS();
	 if (pdSigma < 1.0e-5) pdSigma = 1.0e-5;
	 pd[ipoint] = pdMean;
	 erpd[ipoint] = pdSigma;
	 cout << "PD: " << pd[ipoint] << " " << erpd[ipoint] << endl;
      */
      
      TH1F* intgHist = new TH1F("intgHist","",10000,0.,maxNph);// integral of the pmt signal which should be ~ to the number of photons but on the pulse-by-pulse basis
      tree->Draw("abs(intg2)>>intgHist",selection,""); //pulseIntg -> intg2
      float intgMean=intgHist->GetMean();
      float intgSigma=intgHist->GetRMS();   // a peak width which will be used to determine the histogram range for a given scan point
      float lb = (intgMean - 4 * intgSigma) * nphMean / intgMean;  // +/- 4sigmas
      float hb = (intgMean + 4 * intgSigma) * nphMean / intgMean;
      std::cout << "intgMean=" << intgMean << "  intgSigma=" << intgSigma << std::endl;
      std::cout << "nphMean=" << nphMean << std::endl;
      std::cout << "lb=" << lb << "  hb=" << hb << std::endl;

      TH1F* npmtHist = new TH1F("npmtHist",titlename,100,lb,hb);
      char ca[50];
      sprintf(ca,"abs(intg2)*%f/%f>>npmtHist",nphMean,intgMean); //pulseIntg -> intg2
      tree->Draw(ca,selection);
      float nPMTMean=npmtHist->GetMean();
      float nPMTSigma=npmtHist->GetRMS();
      nphPMT[i_looped] = nPMTMean;
      ernphPMT[i_looped] = nPMTSigma;
      lnphPMT[i_looped] = TMath::Log(nPMTMean);
      erlnphPMT[i_looped] = nPMTSigma/nPMTMean;
      lnphPMT[i_looped] = (nPMTMean > 0) ? TMath::Log(nPMTMean) : 0.0;
      erlnphPMT[i_looped] = (nPMTMean > 0) ?  nPMTSigma/nPMTMean : 0.0;
      std::cout << "nph: " << nphPMT[i_looped] << " " << "enph: " << ernphPMT[i_looped] << endl;

      char axname[50];
      sprintf(axname,"Nph for trigger set %d.%d",trigSetLarge,trigSetSmall);
      npmtHist->GetXaxis()->SetTitle(axname);
      npmtHist->SetTitle("");
      npmtHist->Fit("gaus");
      
      c1->Update();
    
      i_looped = i_looped+1;
    }
  }
  char plotname[30];  
  sprintf(plotname,"nphPB%02d.png",board);
  c1->Print(plotname);    // a plot with distributions for all large width sets    
  /*
  float nph = nphPMT[0]; //nphPMT max value loop 
  for(int i = 1; i < nPointsTot; i++)
  if ( nphPMT[i] > nph )
      nph = nphPMT[i];
  cout << "Max nph in the nphPMT array is: " << nph << endl; 
  float maxNph = 1.1*nph;
  */

  TGraphErrors* nphVSpw = new TGraphErrors(nPointsTot,nphPMT,pw,ernphPMT,erpw); //Nph VS pulse width: R-160606
  sprintf(titlename,"PB%02d",board);
  TCanvas *c2 = new TCanvas("c2", "c2",10,65,700,500);
  c2->SetGridy();
  //c2->SetLogy(0);
  //c2->SetLogx();
  TH2F* NPHvsPW = new TH2F("NPHvsPW",titlename,100,2.,pwMax+2.,1000,1,maxNph);
  NPHvsPW->SetStats(kFALSE);
  NPHvsPW->GetYaxis()->SetTitle("Log number of photons per pulse");
  NPHvsPW->GetXaxis()->SetTitle("Pulse width (ns)");
  NPHvsPW->Draw();
  nphVSpw->SetMarkerStyle(20);
  nphVSpw->Draw("P same");
  c2->Update();  
  sprintf(plotname,"NphVSPulseWidthPB%02d.png",board);
  c2->Print(plotname);
    

  TGraphErrors* nphVStw = new TGraphErrors(nPointsTot,nphPMT,trigW,ernphPMT,ertrigW);  //Nph VS Trigger Width: R-160601
  sprintf(titlename,"PB%02d",board);
  TCanvas *c3 = new TCanvas("c3","c3",10,65,700,500);
  c3->SetGridy();
  //c3->SetLogx();
  //c3->Range(1,0,maxNph,65);
  TH2F* NPHvsTW = new TH2F("NPHvsTW",titlename,35,15,50,1000,1,maxNph);
  NPHvsTW->SetStats(kFALSE);
  NPHvsTW->GetXaxis()->SetTitle("Trigger width (ns)");
  NPHvsTW->GetYaxis()->SetTitle("Number of photons per pulse");
  NPHvsTW->Draw();
  nphVStw->SetMarkerStyle(20);
  nphVStw->Draw("P same");
  c3->Update();
  sprintf(plotname,"NphvsTriggerWidthPB%02d.png",board);
  c3->Print(plotname);
  
  TGraphErrors* twVSlnph = new TGraphErrors(nPointsTot,lnphPMT,trigW,erlnphPMT,ertrigW); //ln(Nph) VS Trigger Width: R-160605
  sprintf(titlename,"PB%02d",board);
  TCanvas *c4 = new TCanvas("c4","c4",10,65,700,500);
  c4->SetGridy();
  TH2F* trigWVSlnphPMT = new TH2F("trigWVSlnphPMT",titlename,1000,1,TMath::Log(maxNph),65,0,65);
  trigWVSlnphPMT->SetStats(kFALSE);
  trigWVSlnphPMT->GetXaxis()->SetTitle("Natural log number of photons per pulse");
  trigWVSlnphPMT->GetYaxis()->SetTitle("Trigger width (ns)");
  trigWVSlnphPMT->Draw();
  twVSlnph->SetMarkerStyle(20);
  TF1 *fitf = new TF1("fitf",fitf_TWNPH,1.,TMath::Log(maxNph),3); 
  fitf->SetParameters(22,0.15,0.001); //(par[0],par[1],par[2]) 
  twVSlnph->Fit(fitf);
  twVSlnph->Draw("P same");
  gStyle->SetStatX(0.55);
  gStyle->SetStatY(0.9);
  c4->Update();
  sprintf(plotname,"ln(Nph)VSTriggerWidthPB%02d.png",board);
  c4->Print(plotname);
    
  
  TCanvas *c5 = new TCanvas("c5","c5",10,65,700,500);  //ln(Nph) VS Trigger Width: R-160605
  TPad *pad1 = new TPad("pad1", "pad1", 0, 0.3, 1, 1.0);
  pad1->SetBottomMargin(0.1);
  pad1->Draw();
  pad1->cd();

  trigWVSlnphPMT->Draw();
  twVSlnph->Draw("P same");
  pad1->Update();
  pad1->RedrawAxis();

  c5->cd();

  TPad *pad2 = new TPad("pad2", "pad2", 0.02, 0, 1, 0.3);
  pad2->Draw();
  pad2->cd();
  pad2->SetLeftMargin(0.08);
  pad2->SetTopMargin(0.035);
  pad2->SetBottomMargin(0.19);
  pad2->Range(-0.2586662,-7.368421,15.41745,5.438596);
  pad2->SetGridy();
  //
  //  TF1 *fitf_res = new TF1("fitf_res",fitf_TWNPH,1.,TMath::Log(maxNph),3);
  // fitf_res->SetParameters(20.,0.15,0.008);
  //
  for (int iPoints = 0; iPoints <= nPointsTot; iPoints++) {
    Double_t xval[1];
    xval[iPoints] = lnphPMT[iPoints];
    //    trigWres[iPoints] =  (trigW[iPoints] - fitf_res->Eval(xval[iPoints]) );
    trigWres[iPoints] =  (trigW[iPoints] - fitf->Eval(xval[iPoints]) );
  }
  //
  TGraph* twRes = new TGraph(nPointsTot,lnphPMT,trigWres);
  //
  twRes->SetTitle("");
  twRes->GetXaxis()->SetTitle("Log Number of Photons per pulse");
  twRes->GetXaxis()->SetTitleSize(0.08);
  twRes->GetXaxis()->SetTitleOffset(1);
  twRes->GetXaxis()->SetLabelSize(0.085);
  twRes->GetYaxis()->SetTitle("Trigger Width Residual");
  twRes->GetYaxis()->SetLabelSize(0.085);
  twRes->GetYaxis()->SetTitleSize(0.085);
  twRes->GetYaxis()->SetTitleOffset(0.35);
  twRes->GetYaxis()->CenterTitle(true);
  twRes->GetXaxis()->SetLimits(1,TMath::Log(maxNph));
  twRes->SetMinimum(-3);
  twRes->SetMaximum(3);
  twRes->SetMarkerColor(1);
  twRes->SetMarkerSize(1);
  twRes->SetMarkerStyle(8);
  twRes->Draw("AP");
  TLine *line = new TLine(1,0,TMath::Log(maxNph),0);
  line->SetLineColor(kBlack);
  line->Draw();
  //
  c5->cd();
  //
  c5->Update();
  //
  //sprintf(plotname,"twVSlnph_with_residuals_PB%02d.pdf",board);
  //c5->Print(plotname);
  //
  //sprintf(plotname,"twVSlnph_with_residuals_PB%02d.png",board);
  //c5->Print(plotname);
  //
  
  /*
  cout << "Number of Photons" << endl;
  for (int i = 0; i < nPointsTot; i++){
  cout << i << " " << lnphPMT[i] << endl;
  }
  //
  cout << "Trigger Widths" << endl;
  for (int i = 0; i < nPointsTot; i++){
  cout << i << " " << trigW[i] << endl;
  }
  //
  cout << "Trigger Width Residuals" << endl;
  for (int i = 0; i < nPointsTot; i++){
  cout << i << " " << trigWres[i] << endl;
  }

  */
}




/*
  CODE DUMP 
  TGraphErrors* pwVSnph = new TGraphErrors(nPointsTot,nphPMT,pw,ernphPMT,erpw); //pulse width VS number of photons /////////////////////////////////////////////////////
  sprintf(titlename,"PB%02d",board);
  TCanvas *c2 = new TCanvas("c2", "c2",10,65,700,500);
  c2->SetGridy();
  //c2->SetLogy(0);
  c2->SetLogx();
  TH2F* PWvsNPH = new TH2F("PWvsNPH",titlename,1000,1,maxNph,100,2.,pwMax+2.);
  PWvsNPH->SetStats(kFALSE);
  PWvsNPH->GetYaxis()->SetTitle("Pulse width (ns)");
  PWvsNPH->GetXaxis()->SetTitle("Number of photons per pulse");
  PWvsNPH->Draw();
  pwVSnph->SetMarkerStyle(20);
  pwVSnph->Draw("P same");
  //sprintf(plotname,"PulseWidthVSnphPB%02d.root",board);
  //c2->Print(plotname);
  sprintf(plotname,"log(Nph)VSPulseWidthPB%02d.png",board);  
  c2->Print(plotname);

  TGraphErrors* twVSnph = new TGraphErrors(nPointsTot,nphPMT,trigW,ernphPMT,ertrigW);  //Trigger Width VS nph
  sprintf(titlename,"PB%02d",board);
  TCanvas *c4 = new TCanvas("c4","c4",10,65,700,500);
  c4->SetGridy();
  //c4->SetLogx();
  //c4->Range(1,0,maxNph,65);
  TH2F* TWvsNPH = new TH2F("TWvsNPH",titlename,1000,1,maxNph,35,15,50);
  TWvsNPH->SetStats(kFALSE);
  TWvsNPH->GetXaxis()->SetTitle("Number of Photons per pulse");
  TWvsNPH->GetYaxis()->SetTitle("Trigger Width (ns)");
  TWvsNPH->Draw();
  twVSnph->SetMarkerStyle(20);
  twVSnph->Draw("P same");
  //sprintf(plotname,"TriggerWidthVSnphPB%02d.png",board);
  //c4->Print(plotname);
  //sprintf(plotname,"TriggerWidthVSnphPB%02d.root",board);
  //c4->Print(plotname);


  TGraphErrors* nphVSwidthsetL = new TGraphErrors(nPointsTot,widthsetlarge,nphPMT,0,ernphPMT);  //nph VS width set large 
  sprintf(titlename,"PB%02d",board);
  TCanvas *c7 = new TCanvas("c7","c7",10,65,700,500);
  c7->SetGridy();
  //c7->SetLog();
  //c7->Range(1,0,maxNph,65);
  TH2F* NPHvsWIDTHSETL = new TH2F("NPHvsWIDTHSETL",titlename,12,9,21,1000,1,maxNph);
  NPHvsWIDTHSETL->SetStats(kFALSE);
  NPHvsWIDTHSETL->GetXaxis()->SetTitle("Large Width Set");
  NPHvsWIDTHSETL->GetYaxis()->SetTitle("nph");
  NPHvsWIDTHSETL->Draw();
  nphVSwidthsetL->SetMarkerStyle(20);
  nphVSwidthsetL->Draw("P same");
  //sprintf(plotname,"TriggerWidthVSnphPB%02d.png",board);
  //c7->Print(plotname);
  //sprintf(plotname,"TriggerWidthVSnphPB%02d.root",board);
  //c7->Print(plotname);
  
  TGraphErrors* nphVSwidthsetS = new TGraphErrors(nPointsTot,widthsetsmall,nphPMT,0,ernphPMT);  //nph VS width set small 
  sprintf(titlename,"PB%02d",board);
  TCanvas *c8 = new TCanvas("c8","c8",10,65,700,500);
  c8->SetGridy();
  //c8->SetLog();
  //c8->Range(1,0,maxNph,65);
  TH2F* NPHvsWIDTHSETS = new TH2F("NPHvsWIDTHSETS",titlename,120,9,21,1000,1,maxNph);
  NPHvsWIDTHSETS->SetStats(kFALSE);
  NPHvsWIDTHSETS->GetXaxis()->SetTitle("Small Width Set");
  NPHvsWIDTHSETS->GetYaxis()->SetTitle("nph");
  NPHvsWIDTHSETS->Draw();
  nphVSwidthsetS->SetMarkerStyle(20);
  nphVSwidthsetS->Draw("P same");
  //sprintf(plotname,"TriggerWidthVSnphPB%02d.png",board);
  //c8->Print(plotname);
  //sprintf(plotname,"TriggerWidthVSnphPB%02d.root",board);
  //c8->Print(plotname);
  
  TGraphErrors* nphVSwidthsetD = new TGraphErrors(nPointsTot,widthsetdec,nphPMT,0,ernphPMT);  //nph VS combined widthset ////////////////////////////////////////////////////////////
  sprintf(titlename,"PB%02d",board);
  TCanvas *c9 = new TCanvas("c9","c9",10,65,700,500);
  c9->SetGridy();
  //c9->SetLog();
  //c9->Range(1,0,maxNph,65);
  TH2F* NPHvsWIDTHSETD = new TH2F("NPHvsWIDTHSETD",titlename,640,9,21,1000,1,maxNph);
  NPHvsWIDTHSETD->SetStats(kFALSE);
  NPHvsWIDTHSETD->GetXaxis()->SetTitle("Width set");
  NPHvsWIDTHSETD->GetYaxis()->SetTitle("Number of photons");
  NPHvsWIDTHSETD->Draw();
  nphVSwidthsetD->SetMarkerStyle(20);
  nphVSwidthsetD->Draw("P same");
  sprintf(plotname,"nphVSWidthSetPB%02d.png",board);
  c9->Print(plotname);


  TGraphErrors* vrefVSnph = new TGraphErrors(nPointsTot,vref,nphPMT,0,ernphPMT);  //nph VS combined widthset 
  sprintf(titlename,"PB%02d",board);
  TCanvas *c5 = new TCanvas("c5","c5",10,65,700,500);
  c5->SetGridy();
  //c5->SetLog();
  //c5->Range(1,0,maxNph,65);
  TH2F* VREFvsNPH = new TH2F("VREFvsNPH",titlename,1000,0.5,1.,1000,1,maxNph);
  VREFvsNPH->SetStats(kFALSE);
  VREFvsNPH->GetXaxis()->SetTitle("vref");
  VREFvsNPH->GetYaxis()->SetTitle("nph");
  VREFvsNPH->Draw();
  vrefVSnph->SetMarkerStyle(20);
  vrefVSnph->Draw("P same");
  sprintf(plotname,"nphVSvrefPB%02d.png",board);
  c5->Print(plotname);
*/
