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

// for 20, 25, 30, 35, 40, 45 ns trigger widths

using namespace std;

Double_t fitf_TWNPH(Double_t *x,Double_t *par);

Double_t fitf_TWNPH(Double_t *x,Double_t *par) 
{
  Double_t arg = x[0];
  Double_t fitval_TWNPH = par[0] + TMath::Exp(par[1]*arg + par[2]*arg*arg);
  return fitval_TWNPH;
} 

void FST_Analysis_V1(char* filename, int board);

void FST_Analysis_V1(char* filename, int board)
{

  TFile *_file0 = TFile::Open(filename);
  TTree* tree = (TTree*)_file0->Get("tree");

  const float maxNph = 1.0e6;
  //const float maxPD = 2.0; //was previously set to 2


  char titlename[30];
  sprintf(titlename,"PB%02d",board);

  TCanvas *c1 = new TCanvas("c1", "c1",800,950);
  TPaveLabel* title = new TPaveLabel(0.1,0.96,0.9,0.99,titlename);
  title->Draw();
  gStyle->SetOptFit(kTRUE);
  const int nPoints = 19;   // number of scan points was originally 8

  int nRows = (int)round((float)nPoints / 2.);
  TPad* graphPad = new TPad("Graphs","Graphs",0.01,0.05,0.95,0.95);
  graphPad->Draw();
  graphPad->cd();
  graphPad->Divide(2,nRows);

  //  const int startPoint = 20;  // start trigger width in ns.
  const int startPoint = 11;  // start trigger set //changed from 4

  float nphPMT[nPoints]; //number of photos at PMT
  float ernphPMT[nPoints]; // uncertainties of nphPMT

  float lnphPMT[nPoints]; //number of photos at PMT
  float erlnphPMT[nPoints]; // uncertainties of nphPMT

  float trigW[nPoints]; //trigger width
  float ertrigW[nPoints]; //uncertainties of trigw
  float trigWres[nPoints]; //trigger width calculated residuals

  float pw[nPoints]; //pulse width
  float erpw[nPoints]; // uncertainties of pw
  float pwMax = 0.0; // Max pulse width

  //float pd[nPoints]; //photodiode board output
  //float erpd[nPoints]; // uncertainties of pd

  for (int ipoint = 0; ipoint < nPoints; ipoint++){

    int trigSet = startPoint + ipoint;  // trigger set 1 ~ 5ns

    graphPad->cd(ipoint+1);

    char selection[50];


    if ((board==1 || board==9 || board==17 || board==25) && trigSet > 4){
      sprintf(selection,"widthset==%d&&amp2<-40&&width2<40&&width2>3",trigSet); // widthset is the trigger width set and pulseWidth is the pulse width.
    } 
    else {
      sprintf(selection,"widthset==%d&&amp2<-10&&width2<40&&width2>2",trigSet); // widthset is the trigger width set and pulseWidth is the pulse width.
    }

    //
    TH1F* trwHist = new TH1F("trwHist","",200,0.,200); // values for the trigger width graph
    tree->Draw("width1>>trwHist",selection,""); //trigWidth -> width1
    float nEntries = trwHist->GetEntries();
    if (nEntries < 1) continue;
    float trwMean=trwHist->GetMean();
    float ertrwSigma=trwHist->GetRMS();
    trigW[ipoint] = trwMean;
    ertrigW[ipoint] = ertrwSigma;
    //
    TH1F* pwHist = new TH1F("pwHist","",100,0.,100); // values for the pulse width graph
    tree->Draw("width2>>pwHist",selection,""); //pulseWidth -> width2
    float pwMean=pwHist->GetMean();
    float erpwSigma=pwHist->GetRMS();
    pw[ipoint] = pwMean;
    erpw[ipoint] = erpwSigma;
    if (pwMean > pwMax) pwMax = pwMean;
    //
    TH1F* npHist = new TH1F("npHist","",10000,0.,maxNph); // number of photons in a given scan point
    tree->Draw("nph>>npHist",selection,""); 
    float nphMean=npHist->GetMean();
    //

    /* DON'T HAVE A Photodiode READ BACK ON NEW FIRMWARE/TESTING CODE
    /////////////
    TH1F* pdHist = new TH1F("pdHist","",1000,0.,maxPD); // PD in a given scan point
    tree->Draw("pdReadingCh1>>pdHist",selection,""); //pdReadingCh1 is not a leaf in the new tree
    float pdMean=pdHist->GetMean();
    float pdSigma=pdHist->GetRMS();
    if (pdSigma < 1.0e-5) pdSigma = 1.0e-5;
    pd[ipoint] = pdMean;
    erpd[ipoint] = pdSigma;
    cout << "PD: " << pd[ipoint] << " " << erpd[ipoint] << endl;
    ////////////    
    */

    //
    TH1F* intgHist = new TH1F("intgHist","",10000,0.,maxNph);// integral of the pmt signal which should be ~ to the number of photons but on the pulse-by-pulse basis
    tree->Draw("abs(intg2)>>intgHist",selection,""); //pulseIntg -> intg2
    float intgMean=intgHist->GetMean();
    float intgSigma=intgHist->GetRMS();   // a peak width which will be used to determine the histogram range for a given scan point
    float lb = (intgMean - 4 * intgSigma) * nphMean / intgMean;  // +/- 4sigmas
    float hb = (intgMean + 4 * intgSigma) * nphMean / intgMean;
    std::cout << "intgMean=" << intgMean << "  intgSigma=" << intgSigma << std::endl;
    std::cout << "nphMean=" << nphMean << std::endl;
    std::cout << "lb=" << lb << "  hb=" << hb << std::endl;
    //
    TH1F* npmtHist = new TH1F("npmtHist",titlename,100,lb,hb);
    char ca[50];
    sprintf(ca,"abs(intg2)*%f/%f>>npmtHist",nphMean,intgMean); //pulseIntg -> intg2
    tree->Draw(ca,selection);
    float nPMTMean=npmtHist->GetMean();
    float nPMTSigma=npmtHist->GetRMS();
    nphPMT[ipoint] = nPMTMean;
    ernphPMT[ipoint] = nPMTSigma;
    lnphPMT[ipoint] = TMath::Log(nPMTMean);
    erlnphPMT[ipoint] = nPMTSigma/nPMTMean;
    lnphPMT[ipoint] = (nPMTMean > 0) ? TMath::Log(nPMTMean) : 0.0;
    erlnphPMT[ipoint] = (nPMTMean > 0) ?  nPMTSigma/nPMTMean : 0.0;
    cout << nphPMT[ipoint] << " " << ernphPMT[ipoint] << endl;
    char axname[50];
    sprintf(axname,"Nph for trigger set %d",trigSet);
    npmtHist->GetXaxis()->SetTitle(axname);
    npmtHist->SetTitle("");
    npmtHist->Fit("gaus");
    //
    c1->Update();
    //
  }
  char plotname[30];
  sprintf(plotname,"nphPB%02d.pdf",board);
  c1->Print(plotname);    // a plot with distributions for all the scan points
  //
  sprintf(plotname,"nphPB%02d.png",board);
  c1->Print(plotname);    // a plot with distributions for all the scan points    
  //

  //
  //pulse width VS number of photons
  TGraphErrors* pwVSnph = new TGraphErrors(nPoints,nphPMT,pw,ernphPMT,erpw);
  sprintf(titlename,"PB%02d",board);
  //
  TCanvas *c2 = new TCanvas("c2", "c2",10,65,700,502);
  c2->SetGridy();
  c2->SetLogy(0);
  c2->SetLogx();
  TH2F* tpf = new TH2F("tpf",titlename,10000,1.,maxNph,100,0.,pwMax+5.);
  tpf->SetStats(kFALSE);
  tpf->GetYaxis()->SetTitle("Pulse width (ns)");
  tpf->GetXaxis()->SetTitle("Number of photons per pulse");
  tpf->Draw();
  pwVSnph->SetMarkerStyle(20);
  pwVSnph->Draw("P same");
  //
  sprintf(plotname,"PulseWidthVSnphPB%02d.pdf",board);
  c2->Print(plotname);
  //
  sprintf(plotname,"PulseWidthVSnphPB%02d.png",board);
  c2->Print(plotname);
  //
 
  //Natural Log of nph VS Trigger Width
  TGraphErrors* twVSlnph = new TGraphErrors(nPoints,lnphPMT,trigW,erlnphPMT,ertrigW);
  sprintf(titlename,"PB%02d",board);
  //
  TCanvas *c3 = new TCanvas("c3","c3",10,65,700,500);
  c3->SetGridy();
  //c3->SetLogx();
  //c3->Range(1,0,maxNph,65);
  TH2F* trigWVSlnphPMT = new TH2F("trigWVSnphPMT",titlename,1000,1,TMath::Log(maxNph),65,0,65);
  trigWVSlnphPMT->SetStats(kFALSE);
  trigWVSlnphPMT->GetXaxis()->SetTitle("Log Number of Photons per pulse");
  trigWVSlnphPMT->GetYaxis()->SetTitle("Trigger Width (ns)");
  trigWVSlnphPMT->Draw();
  twVSlnph->SetMarkerStyle(20);
  // 
  TF1 *fitf = new TF1("fitf",fitf_TWNPH,1.,TMath::Log(maxNph),3); 
  fitf->SetParameters(20,0.15,0.008); //(par[0],par[1],par[2]) 
  //
  twVSlnph->Fit(fitf);
  twVSlnph->Draw("P same");
  //
  gStyle->SetStatX(0.55);
  gStyle->SetStatY(0.9);
  //
  c3->Update();
  sprintf(plotname,"TWVSlnphPB%02d.pdf",board);
  c3->Print(plotname);
  //
  sprintf(plotname,"TWVSlnphPB%02d.png",board);
  c3->Print(plotname);
  //

  //
  //Natural Log of nph VS Trigger Width with residuals
  TCanvas *c4 = new TCanvas("c4","c4",10,65,700,500);
  TPad *pad1 = new TPad("pad1", "pad1", 0, 0.3, 1, 1.0);
  pad1->SetBottomMargin(0.1);
  pad1->Draw();
  pad1->cd();

  trigWVSlnphPMT->Draw();
  twVSlnph->Draw("P same");
  pad1->Update();
  pad1->RedrawAxis();

  c4->cd();

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
  for (int iPoints = 0; iPoints <= nPoints; iPoints++) {
    Double_t xval[1];
    xval[iPoints] = lnphPMT[iPoints];
    //    trigWres[iPoints] =  (trigW[iPoints] - fitf_res->Eval(xval[iPoints]) );
    trigWres[iPoints] =  (trigW[iPoints] - fitf->Eval(xval[iPoints]) );
  }
  //
  TGraph* twRes = new TGraph(nPoints,lnphPMT,trigWres);
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
  c4->cd();
  //
  c4->Update();
  //
  sprintf(plotname,"twVSlnph_with_residuals_PB%02d.pdf",board);
  c4->Print(plotname);
  //
  sprintf(plotname,"twVSlnph_with_residuals_PB%02d.png",board);
  c4->Print(plotname);
  //
  



  //
  cout << "Number of Photons" << endl;
  for (int i = 0; i < nPoints; i++){
    cout << i << " " << lnphPMT[i] << endl;
  }
  //
  cout << "Trigger Widths" << endl;
  for (int i = 0; i < nPoints; i++){
    cout << i << " " << trigW[i] << endl;
  }
  //
  cout << "Trigger Width Residuals" << endl;
  for (int i = 0; i < nPoints; i++){
    cout << i << " " << trigWres[i] << endl;
  }


  
}
