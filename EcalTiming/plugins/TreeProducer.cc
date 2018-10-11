// system include files
#include <memory>
#include <iostream>
#include <sstream>
#include <utility>
#include <string>
#include <vector>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/EventSetupRecordIntervalFinder.h"

#include "CondFormats/DataRecord/interface/LHCInfoRcd.h"
#include "CondFormats/RunInfo/interface/LHCInfo.h"
#include "CondTools/RunInfo/interface/LHCInfoPopConSourceHandler.h"
#include "DataFormats/PatCandidates/interface/TriggerEvent.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "FWCore/Common/interface/TriggerNames.h"

#include "FWCore/Utilities/interface/InputTag.h"

#include "TFile.h"
#include "TTree.h"
#include "TLorentzVector.h"

#define BUNCHES 3564

using namespace std;
using namespace edm;

class TreeProducer : public edm::one::EDAnalyzer<edm::one::SharedResources>
{
public:
  explicit TreeProducer( const edm::ParameterSet& );
  ~TreeProducer();

private:
  virtual void beginJob() override;
  virtual void analyze( const edm::Event&, const edm::EventSetup& ) override;
  virtual void endJob() override;

  // ----------member data --------------------------- 

  void clearTree();

  double sqrtS_;
  std::string filename_;
  TFile* file_;
  TTree* tree_;

  // --- tree components --- 

  unsigned int fBX, fRun, fLumiSection;
  unsigned long long fEventNum;

  unsigned int fBunchNum;
  float fBeam1VC[BUNCHES], fBeam2VC[BUNCHES], fBeam1RF[BUNCHES], fBeam2RF[BUNCHES], fBeamDelay[BUNCHES];
  float fBetaStar;
  unsigned int fXangle, fBunch1, fBunch2, fCollBunch, fTarBunch;
  

};


TreeProducer::TreeProducer( const edm::ParameterSet& iConfig ) :
  filename_ ( iConfig.getParameter<std::string>( "outputFilename" ) ),
  file_( 0 ), tree_( 0 )
  
{
  file_ = new TFile( filename_.c_str(), "recreate" );
  file_->cd();
  
  tree_ = new TTree( "ntp", "ecal ntuple" );
}


TreeProducer::~TreeProducer() {
  if ( file_ ) {
    file_->Write();
    file_->Close();
    delete file_;
  }
  if ( tree_ ) delete tree_;
}

void
TreeProducer::clearTree()
{

  fXangle = 0.;
  fBetaStar = 0.;
  fBunch1 = 0.;
  fBunch2 = 0.;
  fCollBunch = 0.;
  fTarBunch = 0.;

  for ( unsigned int i=0; i<BUNCHES; i++ ) {
    fBeam1VC[i] = 0.;
    fBeam2VC[i] = 0.;
    fBeam1RF[i] = 0.;
    fBeam2RF[i] = 0.;
    fBeamDelay[i] = 0.;
  }
}

// ------------ method called on each new Event  ------------
void
TreeProducer::analyze( const edm::Event& iEvent, const edm::EventSetup& iSetup )
{


  clearTree();

  // Run and BX information
  fBX = iEvent.bunchCrossing();
  fRun = iEvent.id().run();
  fLumiSection = iEvent.luminosityBlock();
  fEventNum = iEvent.id().event();

  edm::ESHandle<LHCInfo> lhcInformation;
  iSetup.get<LHCInfoRcd>().get(lhcInformation);

  const LHCInfo* info = lhcInformation.product();

  fXangle = info->crossingAngle();
  fBetaStar = info->betaStar();
  fBunch1 = info->bunchesInBeam1();
  fBunch2 = info->bunchesInBeam2();
  fCollBunch = info->collidingBunches();
  fTarBunch = info->targetBunches();


  fBunchNum = 0;
  std::vector<float> ( info->beam1VC() );
  for (vector<float>::const_iterator i = info->beam1VC().begin(); i != info->beam1VC().end(); ++i) {
    fBeam1VC[fBunchNum] = *i;
    fBunchNum++;
  }


  fBunchNum = 0;
  std::vector<float> ( info->beam2VC() );
  for (vector<float>::const_iterator i = info->beam2VC().begin(); i != info->beam2VC().end(); ++i) {
    fBeam2VC[fBunchNum] = *i;
    fBunchNum++;
  }

  
  fBunchNum = 0;
  std::vector<float> ( info->beam1RF() );
  for (vector<float>::const_iterator i = info->beam1RF().begin(); i != info->beam1RF().end(); ++i) {
    fBeam1RF[fBunchNum] = *i;
    fBunchNum++;
  }


  fBunchNum = 0;
  std::vector<float> ( info->beam2RF() );
  for (vector<float>::const_iterator i = info->beam2RF().begin(); i != info->beam2RF().end(); ++i) {
    fBeam2RF[fBunchNum] = *i;
    fBunchNum++;
  }


  for ( unsigned int i=0; i < BUNCHES; i++) {
    fBeamDelay[i] = ( fBeam1VC[i] + fBeam2VC[i] ) * ( 2 * 2.5 ) / 360;
  }
  
  tree_->Fill();

}

void
TreeProducer::beginJob()
{

  tree_->Branch( "run_id", &fRun, "run_id/i");
  tree_->Branch( "lumisection", &fLumiSection, "lumisection/i");
  tree_->Branch( "bunch_crossing", &fBX, "bunch_crossing/i");
  tree_->Branch( "event_number", &fEventNum, "event_number/l");

  tree_->Branch( "crossing_angle", &fXangle, "crossing_angle/i");
  tree_->Branch( "beta_star", &fBetaStar, "beta_star/F");
  tree_->Branch( "bunch1", &fBunch1, "bunch1/i");
  tree_->Branch( "bunch2", &fBunch2, "bunch2/i");
  tree_->Branch( "collision_bunches", &fCollBunch, "collision_bunches/i");
  tree_->Branch( "target_bunches", &fTarBunch, "target_bunches/i");

  tree_->Branch( "num_bunch", &fBunchNum, "num_bunch/i");
  tree_->Branch( "beam1_VC", fBeam1VC, "beam1_VC[num_bunch]/F");
  tree_->Branch( "beam2_VC", fBeam2VC, "beam2_VC[num_bunch]/F");
  tree_->Branch( "beam1_RF", fBeam1RF, "beam1_RF[num_bunch]/F");
  tree_->Branch( "beam2_RF", fBeam2RF, "beam2_RF[num_bunch]/F");
  tree_->Branch( "beam_delay", fBeamDelay, "beam_delay[num_bunch]/F");
  

}

void
TreeProducer::endJob()
{
}


  DEFINE_FWK_MODULE(TreeProducer);
 
