// -*- C++ -*-
//
// Package:    CalibCalorimetry/EcalTimingCalibProducer
// Class:      EcalTimingCalibProducer
//
/** \class EcalTimingCalibProducer EcalTimingCalibProducer.cc CalibCalorimetry/EcalTiming/plugins/EcalTimingCalibProducer.cc

 Description: Calculate ecal timing intercalibration

 Implementation:

 \todo Exit condition based on convergence
*/
//
// Original Author:  Shervin Nourbakhsh
//         Created:  Wed, 01 Apr 2015 10:08:43 GMT
//
//

//#define DEBUG
#define RAWIDCRY 838904321
//872415403

// system include files
#include <memory>
#include <iostream>
#include <fstream>

// Make Histograms the way!!
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDConsumerBase.h"

#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
//#include "FWCore/Framework/interface/Handle.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/LooperFactory.h"
#include "FWCore/Framework/interface/ESProducerLooper.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/ESProducts.h"
#include "FWCore/Framework/interface/Event.h"
// input collections
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"

// record to be produced:
#include "CondFormats/DataRecord/interface/EcalTimeCalibConstantsRcd.h"
#include "CondFormats/DataRecord/interface/EcalTimeCalibErrorsRcd.h"
#include "CondFormats/DataRecord/interface/EcalTimeOffsetConstantRcd.h"
#include "CondTools/Ecal/interface/EcalTimeCalibConstantsXMLTranslator.h"
#include "CondTools/Ecal/interface/EcalTimeCalibErrorsXMLTranslator.h"
#include "CondTools/Ecal/interface/EcalTimeOffsetXMLTranslator.h"
#include "CondTools/Ecal/interface/EcalCondHeader.h"

#include "CondFormats/EcalObjects/interface/EcalTimeCalibConstants.h"
#include "CondFormats/EcalObjects/interface/EcalTimeCalibErrors.h"
#include "CondFormats/EcalObjects/interface/EcalTimeOffsetConstant.h"

#include "CalibCalorimetry/EcalTiming/interface/EcalTimingEvent.h"
#include "CalibCalorimetry/EcalTiming/interface/EcalCrystalTimingCalibration.h"

#include "DataFormats/EcalDetId/interface/EBDetId.h"
#include "DataFormats/EcalDetId/interface/EEDetId.h"

#include "TProfile.h"
#include "TProfile2D.h"
#include "TGraphErrors.h"
#include "TGraph.h"
#include "TH1F.h"
#include "TH3F.h"
#include "TH2F.h"

#include <string>
#include <vector>
#include <iostream>
#include <map>
#include <vector>
#include <algorithm>
#include <functional>
#include <set>
#include <assert.h>

#include <TMath.h>
#include <Math/VectorUtil.h>
#include <boost/tokenizer.hpp>


//
// class declaration
//

using namespace std;
using namespace edm;
using namespace cms;

class EcalTimingCalibProducer : public edm::ESProducerLooper
{

public:
	// Map of detId and Crystal time
	typedef std::map<DetId, EcalCrystalTimingCalibration> EcalTimeCalibrationMap;
	EcalTimeCalibrationMap _timeCalibMap;

	EcalTimingCalibProducer(const edm::ParameterSet&);
	~EcalTimingCalibProducer();


	virtual void beginOfJob(const edm::EventSetup&);
	virtual void startingNewLoop(unsigned int ) ;
	virtual Status duringLoop(const edm::Event&, const edm::EventSetup&) ;
	virtual Status endOfLoop(const edm::EventSetup&, unsigned int);
	virtual void endOfJob();
private:
	// ----------member data ---------------------------
	edm::InputTag _ecalRecHitsEBTAG; ///< input collection
	edm::InputTag _ecalRecHitsEETAG;
	std::vector<int> _recHitFlags; ///< vector containing list of valid rec hit flags for calibration

	void dumpCalibration(std::string filename);

// plotting
///fill histograms with the measured shifts (that will become -corrections for the next step)
	void FillCalibrationCorrectionHists(EcalTimeCalibrationMap::const_iterator cal_itr);
	void initHists(TFileDirectory dir);

	// Create calibration container objects -> to be used in beginOfJob
	void createConstants(const edm::EventSetup& iSetup)
	{

		// time calib constants
		edm::ESHandle<EcalTimeCalibConstants> ecalTimeCalibConstantsHandle;
		iSetup.get<EcalTimeCalibConstantsRcd>().get( ecalTimeCalibConstantsHandle);
		_timeCalibConstants = *ecalTimeCalibConstantsHandle;
#ifdef DEBUG
		// why they are 0 when setWhatProduced is uncommented? -> I've not found a way to read the default DB at iter 0
		for(auto t_itr = _timeCalibConstants.begin(); t_itr != _timeCalibConstants.end() && t_itr - _timeCalibConstants.begin() < 10; ++t_itr) {
			std::cout << "t_itr = " << *t_itr << std::endl;
		}
#endif
		produceCalibConstants(iSetup.get<EcalTimeCalibConstantsRcd>());

		// time calib errors
		edm::ESHandle<EcalTimeCalibErrors> ecalTimeCalibErrorsHandle;
		//iSetup.get<EcalTimeCalibErrorsRcd>().get( ecalTimeCalibErrorsHandle);
		//_timeCalibErrors = *ecalTimeCalibErrorsHandle;
		//produceCalibErrors(iSetup.get<EcalTimeCalibErrorsRcd>());

		// time offset constant
		edm::ESHandle<EcalTimeOffsetConstant> ecalTimeOffsetConstantHandle;
		iSetup.get<EcalTimeOffsetConstantRcd>().get( ecalTimeOffsetConstantHandle);
		_timeOffsetConstant = *ecalTimeOffsetConstantHandle;
		produceOffsetConstant(iSetup.get<EcalTimeOffsetConstantRcd>());

	}

	EcalTimeCalibConstants _timeCalibConstants; ///< container of calibrations updated iter by iter
	boost::shared_ptr<EcalTimeCalibConstants> _calibConstants; // corrections used during this iter
	inline boost::shared_ptr<EcalTimeCalibConstants> produceCalibConstants(const EcalTimeCalibConstantsRcd& iRecord)
	{
		// new shared_ptr initialized with previous iter: _timeCalibConstants
		_calibConstants = boost::shared_ptr<EcalTimeCalibConstants>( new EcalTimeCalibConstants(_timeCalibConstants) );
		return  _calibConstants;
	}

	EcalTimeCalibErrors    _timeCalibErrors;
	boost::shared_ptr<EcalTimeCalibErrors> _calibErrors;
	inline boost::shared_ptr<EcalTimeCalibErrors>& produceCalibErrors(const EcalTimeCalibErrorsRcd& iRecord)
	{
		_calibErrors = boost::shared_ptr<EcalTimeCalibErrors>( new EcalTimeCalibErrors(_timeCalibErrors) );
		return _calibErrors;
	}

	EcalTimeOffsetConstant _timeOffsetConstant;
	boost::shared_ptr<EcalTimeOffsetConstant> _offsetConstant;
	inline boost::shared_ptr<EcalTimeOffsetConstant>& produceOffsetConstant(const EcalTimeOffsetConstantRcd& iRecord)
	{
		_offsetConstant = boost::shared_ptr<EcalTimeOffsetConstant>( new EcalTimeOffsetConstant(_timeOffsetConstant) );
		return _offsetConstant;
	}


	bool addRecHit(const EcalRecHit& recHit);

	std::map<DetId, float>  _CrysEnergyMap;

	edm::Service<TFileService> fileService_;
	// Histograms
	TProfile2D* EneProfileMapEEP_;
	TProfile2D* EneProfileMapEEM_;
	//TH2F* EneMapEEP_;
	//TH2F* EneMapEEM_;
	TProfile2D* TimeProfileMapEEP_;
	TProfile2D* TimeProfileMapEEM_;
	//TH2F* TimeMapEEP_;
	//TH2F* TimeMapEEM_;
	TProfile2D* EneProfileMapEB_;
	//TH2F* EneMapEB_;
	TProfile2D* TimeProfileMapEB_;
	//TH2F* TimeMapEB_;
	TH1F* RechitEneEB_;
	TH1F* RechitTimeEB_;
	TH1F* RechitEneEEM_;
	TH1F* RechitTimeEEM_;
	TH1F* RechitEneEEP_;
	TH1F* RechitTimeEEP_;
};


//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
EcalTimingCalibProducer::EcalTimingCalibProducer(const edm::ParameterSet& iConfig) :
	_ecalRecHitsEBTAG(iConfig.getParameter<edm::InputTag>("recHitEBCollection")),
	_ecalRecHitsEETAG(iConfig.getParameter<edm::InputTag>("recHitEECollection")),
	_recHitFlags(iConfig.getParameter<std::vector<int> >("recHitFlags"))
{
	//_ecalRecHitsEBToken = edm::consumes<EcalRecHitCollection>(iConfig.getParameter< edm::InputTag > ("ebRecHitsLabel"));
	//the following line is needed to tell the framework what
	// data is being produced
	setWhatProduced(this,  &EcalTimingCalibProducer::produceCalibConstants);
//	setWhatProduced(this, &EcalTimingCalibProducer::produceCalibErrors);
	//setWhatProduced(this, &EcalTimingCalibProducer::produceOffsetConstant);
	//now do what ever other initialization is needed
}


EcalTimingCalibProducer::~EcalTimingCalibProducer()
{
	// do anything here that needs to be done at desctruction time
	// (e.g. close files, deallocate resources etc.)
}


//
// member functions
//

// ------------ method called to produce the data  ------------
// std::shared_ptr<EcalTimeCalibConstants> EcalTimingCalibProducer::produce(const EcalTimeCalibConstantsRcd& iRecord)
// {
// 	using namespace edm::es;
// 	//std::auto_ptr<EcalTimeCalibConstants> pMyType;
// 	//return products(pMyType);
// 	return NULL;
// }



// ------------ method called once per job just before starting to loop over events  ------------
void EcalTimingCalibProducer::beginOfJob(const edm::EventSetup& iSetup)
{
	std::cout << "Begin job: createConstants" << std::endl;
	createConstants(iSetup);
}

// ------------ method called at the beginning of a new loop over the event  ------------
// ------------ the argument starts at 0 and increments for each loop        ------------
void EcalTimingCalibProducer::startingNewLoop(unsigned int iIteration)
{
	std::cout << "Starting new loop: " << iIteration << std::endl;
#ifdef DEBUG
	auto calib2_itr = _calibConstants->find(RAWIDCRY); //begin();
	std::cout << "index\tcalibConstants\ttimeCalibConstants\n"
	          << calib2_itr - _calibConstants->begin() << "\t" << *calib2_itr << "\t" << *(_timeCalibConstants.find(RAWIDCRY))
	          << std::endl;
#endif

	// Initialize histograms at start of Loop
	char histDir[100];
	sprintf(histDir, "EcalSplashTiming_%d", iIteration);
	// Make a new directory for Histograms for each loop
	TFileDirectory HistDirName = fileService_->mkdir( histDir);

	initHists(HistDirName);
	// reset the calibration

	_timeCalibMap.clear();
	//reset Rechitenergy map
//	_CrysEnergyMap.clear();

}

bool EcalTimingCalibProducer::addRecHit(const EcalRecHit& recHit)
{
	//check if rechit is valid
	if(! recHit.checkFlags(_recHitFlags)) return false;
	if( recHit.energy() < 1) return false;

	//       if( !( (*recHit_itr).checkFlag(EcalRecHit::kGood) || (*recHit_itr).checkFlag(EcalRecHit::kOutOfTime) || (*recHit_itr).checkFlag(EcalRecHit::kPoorCalib)) ) continue;
	// for each recHit create a EcalTimingEvent
	EcalTimingEvent timeEvent(recHit);
	if(fabs(timeEvent.time()) > 25) {
		std::cout << timeEvent << std::endl;
		return false;
	}
#ifdef DEBUG
	//if(recHit.detid().rawId() == RAWIDCRY)
	std::cout << "Debug looping over EB recHits: " << recHit.detid().rawId() << "\t" << timeEvent << "\t <- " << recHit.timeError() << std::endl;
#endif
	// add the EcalTimingEvent to the EcalCreateTimeCalibrations
	assert(_timeCalibMap[recHit.detid()].add(timeEvent));
	// Keep the recHitEventEnergy
//	      	_CrysEnergyMap.insert( std::pair<DetId, float>(recHit.detid(),recHit.energy() ));
	return true;
}

// ------------ called for each event in the loop.  The present event loop can be stopped by return kStop ------------
EcalTimingCalibProducer::Status EcalTimingCalibProducer::duringLoop(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{

	// here the getByToken of the rechits
	edm::Handle<EBRecHitCollection> ebRecHitHandle;
	//iEvent.getByLabel(_ecalRecHitsEBToken, ebRecHitHandle);
	iEvent.getByLabel(_ecalRecHitsEBTAG, ebRecHitHandle);
	edm::Handle<EERecHitCollection> eeRecHitHandle;
	iEvent.getByLabel(_ecalRecHitsEETAG, eeRecHitHandle);


	// loop over the recHits
	// recHit_itr is of type: edm::Handle<EcalRecHitCollection>::const_iterator
	std::cout << "[DEBUG]" << "\t" << ebRecHitHandle->size() << std::endl;
	for(auto  recHit_itr = ebRecHitHandle->begin(); recHit_itr != ebRecHitHandle->end(); ++recHit_itr) {
		addRecHit(*recHit_itr); // add the recHit to the list of recHits used for calibration (with the relative information)
	}

	// same for EE
	for(auto recHit_itr = eeRecHitHandle->begin(); recHit_itr != eeRecHitHandle->end(); ++recHit_itr) {
		addRecHit(*recHit_itr);
	}


	// any etaRing check?
	// any etaRing inter-calibration?
	return kContinue;
}


// ------------ called at the end of each event loop. A new loop will occur if you return kContinue ------------
EcalTimingCalibProducer::Status EcalTimingCalibProducer::endOfLoop(const edm::EventSetup&, unsigned int iLoop_)
{
	std::cout << "EndOfLoop " << std::endl;
	// calculate the calibration constants

	// set the values in _calibConstants, _calibErrors, _offsetConstant
#ifdef DEBUG
	auto calib2_itr = _calibConstants->find(RAWIDCRY); //begin();
	std::cout << "index\tcalibConstants\ttimeCalibConstants: before setValue\n"
	          << calib2_itr - _calibConstants->begin() << "\t" << *calib2_itr << "\t" << *(_timeCalibConstants.find(RAWIDCRY)) << "\t" << _calibConstants->size()
	          << std::endl;
	float debugCorrection;
#endif


	for(auto calibRecHit_itr = _timeCalibMap.begin(); calibRecHit_itr != _timeCalibMap.end(); ++calibRecHit_itr) {
		FillCalibrationCorrectionHists(calibRecHit_itr); // histograms with shifts to be corrected at each step
		float correction =  - calibRecHit_itr->second.mean();
#ifdef DEBUG
		if(calibRecHit_itr->first.rawId() == RAWIDCRY) debugCorrection = correction;
#endif
		_timeCalibConstants.setValue(calibRecHit_itr->first.rawId(), (*_calibConstants)[calibRecHit_itr->first.rawId()] + correction);
		//_calibConstants->setValue(calibRecHit_itr->first.rawId(), *(_calibConstants->find(calibRecHit_itr->first.rawId()))+1);
		//_timeCalibConstants.setValue(calibRecHit_itr->first.rawId(), *(_timeCalibConstants.find(calibRecHit_itr->first.rawId()))+1);

		// add filing Energy hists here
	}

#ifdef DEBUG
	calib2_itr = _calibConstants->find(RAWIDCRY);
	std::cout << "index\tcalibConstants\ttimeCalibConstants: after setValue\n"
	          << calib2_itr - _calibConstants->begin() << "\t" << *calib2_itr << "\t" << *(_timeCalibConstants.find(RAWIDCRY)) << "\t" << debugCorrection
	          << std::endl;
#endif

	// save txt
	char filename[100];
	sprintf(filename, "dumpConstants-%d.dat", iLoop_); //text file holding constants
	dumpCalibration(filename);

	// save the xml

	if(iLoop_ > 1) return kStop;
	++iLoop_;
	return kContinue;
}

// ------------ called once each job just before the job ends ------------
void
EcalTimingCalibProducer::endOfJob()
{
}

void EcalTimingCalibProducer::dumpCalibration(std::string filename)
{
	std::ofstream fout(filename);

	// loop over the constants
	// to make more efficient
#ifdef DEBUG
	DetId findId(RAWIDCRY);
	if(findId.subdetId() == EcalBarrel) {
		EBDetId id(RAWIDCRY);
		fout << "EB: " << id.ieta() << "\t" << id.iphi() << "\t" << id.zside() << "\t" << _timeCalibConstants.barrelItems()[id.denseIndex()] << "\t" << *_timeCalibConstants.find(RAWIDCRY) << "\t" << id.rawId() << std::endl;
	} else {
		EEDetId id(findId);
		fout << "EE: " << id.ix() << "\t" << id.iy() << "\t" << id.zside() << "\t" << _timeCalibConstants.endcapItems()[id.denseIndex()] << "\t" << *_timeCalibConstants.find(RAWIDCRY) << std::endl;
	}
#endif

	for(unsigned int i = 0; i < _timeCalibConstants.barrelItems().size(); ++i) {
		EBDetId id(EBDetId::detIdFromDenseIndex(i)); // this is a stupid thing that I'm obliged to do due to the stupid structure of the ECAL container
		fout << id.ieta() << "\t" << id.iphi() << "\t" << 0 << "\t" << _timeCalibConstants.barrelItems()[i] << "\t" << id.rawId() << std::endl;
	}

	for(unsigned int i = 0; i < _timeCalibConstants.endcapItems().size(); ++i) {
		EEDetId id(EEDetId::detIdFromDenseIndex(i)); // this is a stupid thing that I'm obliged to do due to the stupid structure of the ECAL container
		fout << id.ix() << "\t" << id.iy() << "\t" << id.zside() << "\t" << _timeCalibConstants.endcapItems()[i] << std::endl;
	}
	fout.close();
}



// FillHistograms

void EcalTimingCalibProducer::FillCalibrationCorrectionHists(EcalTimeCalibrationMap::const_iterator cal_itr)
{
	if(cal_itr->first.subdetId() == EcalBarrel) {
		EBDetId id(cal_itr->first);
		// Fill Rechit Energy
		EneProfileMapEB_->Fill(id.ieta(), id.iphi(), cal_itr->second.meanE()); // 2D energy map
		RechitEneEB_->Fill(cal_itr->second.meanE());   // 1D histogram
		TimeProfileMapEB_->Fill(id.ieta(), id.iphi(), cal_itr->second.mean()); // 2D time map
		RechitTimeEB_->Fill(cal_itr->second.mean()); // 1D histogram
	} else {
		// create EEDetId
		EEDetId id(cal_itr->first);
		if(id.zside() < 0) {
			EneProfileMapEEM_->Fill(id.ix(), id.iy(), cal_itr->second.meanE());
			RechitEneEEM_->Fill(cal_itr->second.meanE());
			TimeProfileMapEEM_->Fill(id.ix(), id.iy(), cal_itr->second.mean());
			RechitTimeEEM_->Fill(cal_itr->second.mean());
		} else {
			TimeProfileMapEEP_->Fill(id.ix(), id.iy(), cal_itr->second.mean());
			RechitTimeEEP_->Fill(cal_itr->second.mean());
			EneProfileMapEEP_->Fill(id.ix(), id.iy(), cal_itr->second.meanE());
			RechitEneEEP_->Fill(cal_itr->second.meanE());
		}
	}

}


//
void EcalTimingCalibProducer::initHists(TFileDirectory fdir)
{
	EneProfileMapEB_ = fdir.make<TProfile2D>("EneProfileMapEB_", "RecHit Energy[GeV] EB profile map;i#eta; i#phi;E[GeV]", 171, -85, 86, 360, 1., 361.);
	//EneMapEB_ = fdir.make<TH2F>("EneMapEB_","RecHit Energy  map [GeV]; i#phi; i#eta;E[GeV]",360,1.,361.,171,-85,86);
	TimeProfileMapEB_ = fdir.make<TProfile2D>("TimeProfileMapEB_", "Mean Time [ns] EB profile map; i#eta; i#phi;Time[ns]", 171, -85, 86, 360, 1., 361.);
	//TimeMapEB_ = fdir.make<TH2F>("TimeMapEB_","Mean Time map [ns]; i#phi; i#eta;E[ns]",360,1.,361.,171,-85,86);

	EneProfileMapEEP_ = fdir.make<TProfile2D>("EneProfileMapEEP_", "RecHit Energy[GeV] profile map EE+;ix;iy;E[GeV]", 100, 1, 101, 100, 1, 101);
	//EneMapEEP_ = fdir.make<TH2F>("EneMapEEP_","RecHit Energy  EE+[GeV];ix;iy;E[GeV]",100,1,101,100,1,101);
	TimeProfileMapEEP_ = fdir.make<TProfile2D>("TimeProfileMapEEP_", "Mean Time[ns] profile map EE+;ix;iy; Time[ns]", 100, 1, 101, 100, 1, 101);
	//TimeMapEEP_ = fdir.make<TH2F>("TimeMapEEP_","Mean Time EE+[ns];ix;iy; Time[ns]",100,1,101,100,1,101);
	EneProfileMapEEM_ = fdir.make<TProfile2D>("EneProfileMapEEM_", "RecHit Energy[GeV] profile map EE-;ix;iy;E[GeV]", 100, 1, 101, 100, 1, 101);
	TimeProfileMapEEM_ = fdir.make<TProfile2D>("TimeProfileMapEEM_", "Mean Time[ns] profile map EE-;ix;iy; Time[ns]", 100, 1, 101, 100, 1, 101);
	//TimeMapEEM_ = fdir.make<TH2F>("TimeMapEEM_","Mean Time EE-[ns];ix;iy; Time[ns]",100,1,101,100,1,101);

	RechitTimeEEM_ = fdir.make<TH1F>("RechitTimeEEM_", "RecHit Mean Time[ns] EE-;RecHit Time[ns]; Events", 200, -50.0, 50.0);
	RechitTimeEEP_ = fdir.make<TH1F>("RechitTimeEEP_", "RecHit Mean Time[ns] EE+;RecHit Time[ns]; Events", 200, -50.0, 50.0);
	RechitTimeEB_ = fdir.make<TH1F>("RechitTimeEB_", "RecHit Mean Time[ns] EB;RecHit Time[ns]; Events", 200, -50.0, 50.0);

	RechitEneEEM_ = fdir.make<TH1F>("RechitEneEEM_", "RecHit Energy[GeV] EE-;Rechit Energy[GeV]; Events", 200, 0.0, 100.0);
	RechitEneEEP_ = fdir.make<TH1F>("RechitEneEEP_", "RecHit Energy[GeV] EE+;Rechit Energy[GeV]; Events", 200, 0.0, 100.0);
	RechitEneEB_ = fdir.make<TH1F>("RechitEneEB_", "RecHit Energy[GeV] EB;Rechit Energy[GeV]; Events", 200, 0.0, 100.0);

}

//define this as a plug-in
DEFINE_FWK_LOOPER(EcalTimingCalibProducer);
