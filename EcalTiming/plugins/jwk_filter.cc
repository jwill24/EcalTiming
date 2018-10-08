// system include files
#include <memory>
#include <iostream>
#include <sstream>
#include <utility>
#include <string>
#include <vector>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDFilter.h"
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

using namespace std;
using namespace edm;

class jwk_filter : public edm::stream::EDFilter<> {
public:
  explicit jwk_filter(const edm::ParameterSet&);
  ~jwk_filter();

private:
  virtual bool filter(edm::Event&, const edm::EventSetup&) override;

};

  jwk_filter::jwk_filter(const edm::ParameterSet& iConfig){}

  jwk_filter::~jwk_filter() {}


// ------------ method called on each new Event  ------------
bool
jwk_filter::filter(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  
  edm::ESHandle<LHCInfo> lhcInformation;
  iSetup.get<LHCInfoRcd>().get(lhcInformation);

  const LHCInfo* info = lhcInformation.product();

  cout << "LHC LS: " << info->lumiSection() << endl;
  cout << "Crossing angle: " << info->crossingAngle() << endl;
  cout << "Beta Star: " << info->betaStar() << endl;

  cout << "beam1RF size: " << info->beam1RF().size() << endl;  
  cout << "beam2RF size: " << info->beam2RF().size() << endl;

  std::vector<float> ( info->beam1RF() );
  for (vector<float>::const_iterator i = info->beam1RF().begin(); i != info->beam1RF().end(); ++i)
    cout << *i << ' ';

  std::vector<float> ( info->beam2RF() );
  for (vector<float>::const_iterator i = info->beam2RF().begin(); i != info->beam2RF().end(); ++i)
    cout << *i << ' ';



  edm::Wrapper<pat::TriggerEvent> trEv;
  iEvent.getByLabel( triggerEventLabel_,trEv );

  const TriggerObjectCollection* trig = trEv->getObjects();

  //int ls = iEvent.luminosityBlock();
  //int fillNum = trigNames->lhcFill_;
  
  //cout << "LS: " << ls << " Fill number: " << fillNum << endl;
   
  return true;
}

  DEFINE_FWK_MODULE(jwk_filter);
 
