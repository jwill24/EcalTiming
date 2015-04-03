// -*- C++ -*-
//
// Package:    CalibCalorimetry/EcalTimingCalibProducer
// Class:      EcalTimingCalibProducer
//
/**\class EcalTimingCalibProducer EcalTimingCalibProducer.cc CalibCalorimetry/EcalTiming/plugins/EcalTimingCalibProducer.cc

 Description: Calculate ecal timing intercalibration

 Implementation:

 \todo Exit condition based on convergence
*/
//
// Original Author:  Shervin Nourbakhsh
//         Created:  Wed, 01 Apr 2015 10:08:43 GMT
//
//

#define DEBUG
#define RAWIDCRY 872415403

// system include files
#include <memory>
#include <iostream>

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
//
// class declaration
//

class EcalTimingCalibProducer : public edm::ESProducerLooper
{
public:
	EcalTimingCalibProducer(const edm::ParameterSet&);
	~EcalTimingCalibProducer();


	virtual void beginOfJob(const edm::EventSetup&);
	virtual void startingNewLoop(unsigned int ) ;
	virtual Status duringLoop(const edm::Event&, const edm::EventSetup&) ;
	virtual Status endOfLoop(const edm::EventSetup&, unsigned int);
	virtual void endOfJob();
private:
	// ----------member data ---------------------------
	edm::InputTag _ecalRecHitsEBTAG;
	edm::InputTag _ecalRecHitsEETAG;

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
	inline boost::shared_ptr<EcalTimeCalibErrors> produceCalibErrors(const EcalTimeCalibErrorsRcd& iRecord)
	{
		_calibErrors = boost::shared_ptr<EcalTimeCalibErrors>( new EcalTimeCalibErrors(_timeCalibErrors) );
		return _calibErrors;
	}

	EcalTimeOffsetConstant _timeOffsetConstant;
	boost::shared_ptr<EcalTimeOffsetConstant> _offsetConstant;
	inline boost::shared_ptr<EcalTimeOffsetConstant> produceOffsetConstant(const EcalTimeOffsetConstantRcd& iRecord)
	{
		_offsetConstant = boost::shared_ptr<EcalTimeOffsetConstant>( new EcalTimeOffsetConstant(_timeOffsetConstant) );
		return _offsetConstant;
	}

	typedef std::map<DetId, EcalCrystalTimingCalibration> EcalTimeCalibrationMap;
	EcalTimeCalibrationMap _timeCalibMap;

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
	_ecalRecHitsEETAG(iConfig.getParameter<edm::InputTag>("recHitEECollection"))
{
	//_ecalRecHitsEBToken = edm::consumes<EcalRecHitCollection>(iConfig.getParameter< edm::InputTag > ("ebRecHitsLabel"));
	//the following line is needed to tell the framework what
	// data is being produced
	setWhatProduced(this,  &EcalTimingCalibProducer::produceCalibConstants);
//	setWhatProduced(this,  &EcalTimingCalibProducer::produceCalibErrors);
	setWhatProduced(this,  &EcalTimingCalibProducer::produceOffsetConstant);
	//now do what ever other initialization is needed
}


EcalTimingCalibProducer::~EcalTimingCalibProducer()
{
	// do anything here that needs to be done at desctruction time
	// (e.g. close files, deallocate resources etc.)
}



// ------------ method called once per job just before starting to loop over events  ------------
void EcalTimingCalibProducer::beginOfJob(const edm::EventSetup& iSetup)
{
//	std::cout << "Begin job: createConstants" << std::endl;
	createConstants(iSetup);
}

// ------------ method called at the beginning of a new loop over the event  ------------
// ------------ the argument starts at 0 and increments for each loop        ------------
void EcalTimingCalibProducer::startingNewLoop(unsigned int iIteration)
{
//	std::cout << "Starting new loop: " << iIteration << std::endl;
#ifdef DEBUG
	auto calib2_itr = _calibConstants->find(RAWIDCRY); //begin();
	std::cout << "index\tcalibConstants\ttimeCalibConstants\n"
	          << calib2_itr - _calibConstants->begin() << "\t" << *calib2_itr << "\t" << *(_timeCalibConstants.find(RAWIDCRY))
	          << std::endl;
#endif

	// reset the calibration
	_timeCalibMap.clear();
}

// ------------ called for each event in the loop.  The present event loop can be stopped by return kStop ------------
EcalTimingCalibProducer::Status EcalTimingCalibProducer::duringLoop(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{

	// here the getByToken of the rechits
	edm::Handle<EBRecHitCollection> ebRecHitHandle;
	//iEvent.getByLabel(_ecalRecHitsEBToken, ebRecHitHandle);
	iEvent.getByLabel(_ecalRecHitsEETAG, ebRecHitHandle);
	edm::Handle<EERecHitCollection> eeRecHitHandle;
	iEvent.getByLabel(_ecalRecHitsEETAG, eeRecHitHandle);


	// loop over the recHits
	// recHit_itr is of type: edm::Handle<EcalRecHitCollection>::const_iterator
	for(auto  recHit_itr = ebRecHitHandle->begin(); recHit_itr != ebRecHitHandle->end(); ++recHit_itr) {
		// for each recHit create a EcalTimingEvent
		EcalTimingEvent timeEvent(recHit_itr->time(), recHit_itr->timeError(), recHit_itr->energy());
#ifdef DEBUG
		if(recHit_itr->detid().rawId() == RAWIDCRY) std::cout << timeEvent << "\t <- " << recHit_itr->timeError() << std::endl;
#endif
		// add the EcalTimingEvent to the EcalCreateTimeCalibrations
		assert(_timeCalibMap[recHit_itr->detid()].add(timeEvent));
	}

	// same for EE
	for(auto recHit_itr = eeRecHitHandle->begin(); recHit_itr != eeRecHitHandle->end(); ++recHit_itr) {
		EcalTimingEvent timeEvent(recHit_itr->time(), recHit_itr->timeError(), recHit_itr->energy());
		assert(_timeCalibMap[recHit_itr->detid()].add(timeEvent));
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
		//_timeCalibConstants.setValue(calibRecHit_itr->first.rawId(), -calibRecHit_itr->second.mean());
		float correction =  - calibRecHit_itr->second.mean();
		if(calibRecHit_itr->first.rawId() == RAWIDCRY) debugCorrection = correction;
		_timeCalibConstants.setValue(calibRecHit_itr->first.rawId(), (*_calibConstants)[calibRecHit_itr->first.rawId()] + correction);
		//_calibConstants->setValue(calibRecHit_itr->first.rawId(), *(_calibConstants->find(calibRecHit_itr->first.rawId()))+1);
		//_timeCalibConstants.setValue(calibRecHit_itr->first.rawId(), *(_timeCalibConstants.find(calibRecHit_itr->first.rawId()))+1);
	}

#ifdef DEBUG
	calib2_itr = _calibConstants->find(RAWIDCRY);
	std::cout << "index\tcalibConstants\ttimeCalibConstants: after setValue\n"
	          << calib2_itr - _calibConstants->begin() << "\t" << *calib2_itr << "\t" << *(_timeCalibConstants.find(RAWIDCRY)) << "\t" << debugCorrection
	          << std::endl;
#endif


	// save the xml

	if(iLoop_ > 2) return kStop;
	++iLoop_;
	return kContinue;
}

// ------------ called once each job just before the job ends ------------
void
EcalTimingCalibProducer::endOfJob()
{
}


//define this as a plug-in
DEFINE_FWK_LOOPER(EcalTimingCalibProducer);
