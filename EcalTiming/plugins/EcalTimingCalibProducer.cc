#include "EcalTiming/EcalTiming/plugins/EcalTimingCalibProducer.h"
/*
*/
//
// Original Author:  Shervin Nourbakhsh
//         Created:  Wed, 01 Apr 2015 10:08:43 GMT
//
//



//
// class declaration
//

using namespace std;
using namespace edm;
using namespace cms;



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
	_maxLoop(iConfig.getParameter<unsigned int>("maxLoop")),
	_isSplash(iConfig.getParameter<bool>("isSplash")),
	_makeEventPlots(iConfig.getParameter<bool>("makeEventPlots")),
	_ecalRecHitsEBTAG(iConfig.getParameter<edm::InputTag>("recHitEBCollection")),
	_ecalRecHitsEETAG(iConfig.getParameter<edm::InputTag>("recHitEECollection")),
	_recHitFlags(iConfig.getParameter<std::vector<int> >("recHitFlags")),
	_recHitMin(iConfig.getParameter<unsigned int>("recHitMinimumN")),

	///\todo the min energy should be in ADC not in energy
	_minRecHitEnergy(iConfig.getParameter<double>("minRecHitEnergy")),
	_minRecHitEnergyStep(iConfig.getParameter<double>("minRecHitEnergyStep")),
	_minEntries(iConfig.getParameter<unsigned int>("minEntries")),
	_globalOffset(iConfig.getParameter<double>("globalOffset")),
	_produceNewCalib(iConfig.getParameter<bool>("produceNewCalib")),
	_outputDumpFileName(iConfig.getParameter<std::string>("outputDumpFile")),
	_maxSkewnessForDump(iConfig.getParameter<double>("maxSkewnessForDump")),
	_ringTools(EcalRingCalibrationTools())
{
	//_ecalRecHitsEBToken = edm::consumes<EcalRecHitCollection>(iConfig.getParameter< edm::InputTag > ("ebRecHitsLabel"));
	//the following line is needed to tell the framework what
	// data is being produced
	if(_produceNewCalib) {
		setWhatProduced(this,  &EcalTimingCalibProducer::produceCalibConstants);
//	setWhatProduced(this, &EcalTimingCalibProducer::produceCalibErrors);
		setWhatProduced(this, &EcalTimingCalibProducer::produceOffsetConstant);
	}
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

	//Get Geometry for Rings
	edm::ESHandle<CaloGeometry> pG;
	iSetup.get<CaloGeometryRecord>().get(pG);
	EcalRingCalibrationTools::setCaloGeometry(&(*pG));
	endcapGeometry_ =  pG->getSubdetectorGeometry(DetId::Ecal, EcalEndcap);
	barrelGeometry_ =  pG->getSubdetectorGeometry(DetId::Ecal, EcalBarrel);

	edm::ESHandle<EcalElectronicsMapping> hElecMap;
	iSetup.get<EcalMappingRcd>().get(hElecMap);
	elecMap_ = hElecMap.product();

}

// ------------ method called at the beginning of a new loop over the event  ------------
// ------------ the argument starts at 0 and increments for each loop        ------------
void EcalTimingCalibProducer::startingNewLoop(unsigned int iIteration)
{
	std::cout << "Starting new loop: " << iIteration << std::endl;
/// save the iteration index
	_iter = iIteration;
#ifdef DEBUG
	auto calib2_itr = _calibConstants->find(RAWIDCRY); //begin();
	std::cout << "index\tcalibConstants\ttimeCalibConstants\n"
	          << calib2_itr - _calibConstants->begin() << "\t" << *calib2_itr << "\t" << *(_timeCalibConstants.find(RAWIDCRY))
	          << std::endl;
#endif

	// Initialize histograms at start of Loop
	char histDirName[100];
	sprintf(histDirName, "EcalSplashTiming_%d", iIteration);
	// Make a new directory for Histograms for each loop
	histDir_ = fileService_->mkdir( histDirName);

	initHists(histDir_);
	initTree(histDir_);

	// reset the calibration
	_timeCalibMap.clear();
}


bool EcalTimingCalibProducer::addRecHit(const EcalRecHit& recHit, EventTimeMap& eventTimeMap_)
{
	//check if rechit is valid
	if(! recHit.checkFlags(_recHitFlags)) return false;
	int iRing = _ringTools.getRingIndexInSubdet(recHit.detid());
	float energyThreshold = recHit.detid().subdetId() == EcalBarrel ? 20 * 0.04 :  20 * (79.29 - 4.148 * iRing + 0.2442 * iRing * iRing ) / 1000 ;

	if( recHit.energy() < (energyThreshold)) return false; // minRecHitEnergy in ADC for EB
	if( recHit.energy() < (energyThreshold + _minRecHitEnergyStep * _iter)) return false;
	//if(recHit.detid().subdetId() == EcalEndcap && recHit.energy() < 2 * (_minRecHitEnergy+_minRecHitEnergyStep*_iter)) return false;

	// add the EcalTimingEvent to the EcalCreateTimeCalibrations
	EcalTimingEvent timeEvent(recHit);
	_eventTimeMap.emplace(recHit.detid(), timeEvent);


	return true;
}

/**
   fills the energy map and timing maps for EB, EE+ and EE-
 */
void EcalTimingCalibProducer::plotRecHit(const EcalTimingEvent& recHit)
{
	if(recHit.detid().subdetId() == EcalBarrel) {
		EBDetId id(recHit.detid());
		// Fill Rechit Energy
		Event_EneMapEB_->Fill(id.ieta(), id.iphi(), recHit.energy()); // 2D energy map
		Event_TimeMapEB_->Fill(id.ieta(), id.iphi(), recHit.time()); // 2D time map
		RechitEnergyTimeEB->Fill(recHit.energy(), recHit.time());
	} else {
		// create EEDetId
		EEDetId id(recHit.detid());
		if(id.zside() < 0) {
			Event_EneMapEEM_->Fill(id.ix(), id.iy(), recHit.energy());
			Event_TimeMapEEM_->Fill(id.ix(), id.iy(), recHit.time());
			RechitEnergyTimeEEM->Fill(recHit.energy(), recHit.time());

		} else {
			Event_EneMapEEP_->Fill(id.ix(), id.iy(), recHit.energy());
			Event_TimeMapEEP_->Fill(id.ix(), id.iy(), recHit.time());
			RechitEnergyTimeEEP->Fill(recHit.energy(), recHit.time());
		}
	}
}

/**
	@param[in] te EcalTimingEvent
	@param[in] splashDir integer indicating the beam direction in splash events
	@param[in] bunchCorr float correction for global event timing
	@param[out] c corrected timing event
*/
EcalTimingEvent EcalTimingCalibProducer::correctGlobalOffset(const EcalTimingEvent& te, int splashDir, float bunchCorr)
{
	DetId id = te.detid();

	const CaloSubdetectorGeometry *geom = (id.subdetId() == EcalBarrel) ? barrelGeometry_ : endcapGeometry_;

	float z = geom->getGeometry(id)->getPosition().z();
	float mag = geom->getGeometry(id)->getPosition().mag();

	float time = te.time() - (splashDir * z - mag) / SPEEDOFLIGHT; // Adjust time by difference in time of flight for halo/splash

	time += bunchCorr;

	time += _globalOffset;

	return 	EcalTimingEvent (EcalRecHit(id, te.energy(), time ));
}

// ------------ called for each event in the loop.  The present event loop can be stopped by return kStop ------------
EcalTimingCalibProducer::Status EcalTimingCalibProducer::duringLoop(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{

	// here the getByToken of the rechits
	edm::Handle<EBRecHitCollection> ebRecHitHandle;
	iEvent.getByLabel(_ecalRecHitsEBTAG, ebRecHitHandle);
	edm::Handle<EERecHitCollection> eeRecHitHandle;
	iEvent.getByLabel(_ecalRecHitsEETAG, eeRecHitHandle);


	_eventTimeMap.clear(); // reset the map of time from recHits for this event

	// the following maps are used to:
	//  - distinguish between beam1 and beam2 in splash events looking at the relative time shift
	//  - adjust the global time offset if required (for splash events for example).
	//  The global time shift is set such that all the time measurements in the event are relative to one ring
	timeEB.clear();  // reset the map for one ring in EB
	timeEEM.clear(); // reset the map for one ring in EE-
	timeEEP.clear(); // reset the map for one ring in EE+

	// loop over the recHits and add those passing the selection to the list of recHits to be used for timing:  eventTimeMap
	// recHit_itr is of type: edm::Handle<EcalRecHitCollection>::const_iterator
	for(auto  recHit_itr = ebRecHitHandle->begin(); recHit_itr != ebRecHitHandle->end(); ++recHit_itr) {
		// add the recHit to the list of recHits used for calibration (with the relative information)
		if(addRecHit(*recHit_itr, _eventTimeMap)) {
			//EBDetId id(recHit.detid());
			// if(id.ieta() == -75 && id.iphi() == 119) {
			// 	std::cout << "RawID\t" << id.rawId() << std::endl;
			// 	return false;
			// }
			timeEB.add(EcalTimingEvent(*recHit_itr), false);
		}
	}

	// same for EE
	for(auto recHit_itr = eeRecHitHandle->begin(); recHit_itr != eeRecHitHandle->end(); ++recHit_itr) {
		// add the recHit to the list of recHits used for calibration (with the relative information)
		if(addRecHit(*recHit_itr, _eventTimeMap)) { // true if the recHit passes the selection and then added to the timeCalibMap
			// create EEDetId
			EEDetId id(recHit_itr->detid());
			if(id.zside() < 0) {
				timeEEM.add(EcalTimingEvent(*recHit_itr), false);
			} else {
				timeEEP.add(EcalTimingEvent(*recHit_itr), false);
			}
		}
	}

#ifdef DEBUG
	std::cout << "[DEBUG]" << "nRecHits passing selection"
	          << "\t" << _eventTimeMap.size()
	          << "\t" << timeEB.num()
	          << "\t" << timeEEM.num()
	          << "\t" << timeEEP.num()
	          << std::endl;
#endif
	// If we got less than the minimum recHits, continue -> this is to select events with enough activity
	if(_eventTimeMap.size() < _recHitMin) return kContinue;
#ifdef DEBUG
	std::cout << "[DUMP]\t" << timeEB << "\t"  << timeEEM << "\t" << timeEEP << std::endl;
#endif
	// Make a new directory for Histograms for each event if you want plots per event
	char eventDirName[100];
	if(_makeEventPlots) {
		sprintf(eventDirName, "Event_%d", int(iEvent.id().event()) );
		TFileDirectory eventDir = histDir_.mkdir(eventDirName);
		initEventHists(eventDir);
	}

	// for splashes you want to distinguish between beam 1 and beam 2
	// you can use the average time over one ring in EE- and one ring in EE+ for that
	int splashDir = (timeEEP.mean() > timeEEM.mean()) ? 1 : -1; // 1 for beam 1, -1 for beam 2
	float bunchCorr = 0.0f;
	if( std::max(timeEEP.mean(), timeEEM.mean()) > 10.0)
		bunchCorr = -25.0f;

	// Add adjusted timeEvents to CorrectionsMap
	for(auto const & it : _eventTimeMap) {
		// if it is a splash event, set a global offset shift such that the time is coherent between different events
		EcalTimingEvent event = _isSplash ? correctGlobalOffset(it.second, splashDir, bunchCorr) : it.second;

		if(_makeEventPlots) plotRecHit(event);
		_timeCalibMap[it.first].add(event);

		//Find the CCU(tower) that this crystal belongs to
		unsigned int elecID = (elecMap_->getElectronicsId(it.first).rawId() >> 6) & 0x3FFF;
		_HWCalibrationMap[elecID].add(event,false);

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
	for (auto it : _HWCalibrationMap)
	{
		if	(abs(it.second.mean()) > HW_UNIT * 1.5) std::cout <<  "HW: " << it.first << ' ' << it.second.mean() << std::endl;
	}
#endif

	// remove the entries OOT (time > n_sigma)
	float n_sigma = 2.; /// \todo remove hard coded number
	for(auto calibRecHit_itr = _timeCalibMap.begin(); calibRecHit_itr != _timeCalibMap.end(); ++calibRecHit_itr) {
		FillCalibrationCorrectionHists(calibRecHit_itr); // histograms with shifts to be corrected at each step
		FillHWCorrectionHists(calibRecHit_itr);
		float correction =  - calibRecHit_itr->second.getMeanWithinNSigma(n_sigma, 10);  // to reject tails
		_timeCalibConstants.setValue(calibRecHit_itr->first.rawId(), (*_calibConstants)[calibRecHit_itr->first.rawId()] + correction);

		unsigned int ds = DS_NONE;
		//TODO: This probably shouldn't be commented out. Move the stat check into the individual functions?
		//if(calibRecHit_itr->second.num() > 50) {
			// check the asymmetry of the distribution: if asymmetric, dump the full set of events for further offline studies
			if(fabs(calibRecHit_itr->second.getSkewnessWithinNSigma(n_sigma, 10)) > _maxSkewnessForDump)  {
				ds |= DS_HIGH_SKEW;

			}

			// check if result is stable as function of energy
			std::vector< std::pair<float, EcalCrystalTimingCalibration*> > energyStability;
			if(! calibRecHit_itr->second.isStableInEnergy(_minRecHitEnergy, _minRecHitEnergy + _minRecHitEnergyStep * N_ENERGY_STEPS, _minRecHitEnergyStep, energyStability)) {
				ds |= DS_UNSTABLE_EN;
			}
			FillEnergyStabilityHists(calibRecHit_itr, energyStability);
		//}

		int elecID = (elecMap_->getElectronicsId(calibRecHit_itr->first).rawId() >> 6) & 0x3FFF;
		if( abs(_HWCalibrationMap[elecID].mean()) > HW_UNIT * 1.5)
		{
			ds |= DS_CCU_OOT;
		}

		if((calibRecHit_itr->first.rawId() == EBCRYex) ||
				(calibRecHit_itr->first.rawId() == EECRYex)) ds |= DS_CRYS;

		int iRing = _ringTools.getRingIndexInSubdet(calibRecHit_itr->first);

		if(calibRecHit_itr->first.subdetId() == EcalBarrel && iRing == EBRING) ds |= DS_RING;
		else if(calibRecHit_itr->first.subdetId() == EcalEndcap && (iRing == EEmRING || iRing == EEpRING )) ds |= DS_RING;

		if(ds != DS_NONE)
		{
			int ix, iy, iz;
			if(calibRecHit_itr->first.subdetId() == EcalBarrel) {
				EBDetId id(calibRecHit_itr->first);
				ix = id.ieta();
				iy = id.iphi();
				iz = 0;
			} else {
				EEDetId id(calibRecHit_itr->first);
				ix = id.ix();
				iy = id.iy();
				iz = id.zside();
			}
			calibRecHit_itr->second.dumpToTree(dumpTree, ix, iy, iz, ds, elecID);
		}

		// add filing Energy hists here
	}

	// save txt
	time_t     now = time(0);
	struct tm  tstruct;
	char       current_time[80];
	tstruct = *localtime(&now);
	strftime(current_time, sizeof(current_time), "%Y-%m-%d.%X", &tstruct);

	char filename[100];
	sprintf(filename, "%s-%d.dat", _outputDumpFileName.substr(0, _outputDumpFileName.find(".root")).c_str(), iLoop_); //text file holding constants
	dumpCalibration(filename);
	sprintf(filename, "%s-corr-%d.dat", _outputDumpFileName.substr(0, _outputDumpFileName.find(".root")).c_str(), iLoop_); //text file holding constants
	dumpCorrections(filename);
	// save the xml

	if(iLoop_ >= _maxLoop - 1) return kStop;
	++iLoop_;
	return kContinue;
}

// ------------ called once each job just before the job ends ------------
void
EcalTimingCalibProducer::endOfJob()
{
}

void EcalTimingCalibProducer::dumpCorrections(std::string filename)
{
	std::ofstream fout(filename);

	// loop over the constants
	// to make more efficient
	for(auto calibRecHit_itr = _timeCalibMap.begin(); calibRecHit_itr != _timeCalibMap.end(); ++calibRecHit_itr) {
		DetId id_ = calibRecHit_itr->first;
		if(id_.subdetId() == EcalBarrel) {
			EBDetId id(id_);
			fout << id.ieta() << "\t" << id.iphi() << "\t" << 0
			     << "\t" << calibRecHit_itr->second.mean() << "\t" << calibRecHit_itr->second.stdDev() << "\t" << calibRecHit_itr->second.num() << "\t" << calibRecHit_itr->second.meanE()
			     << "\t" << id.rawId() << std::endl;
		} else {
			EEDetId id(id_);
			fout << id.ix() << "\t" << id.iy() << "\t" << id.zside()
			     << "\t" << calibRecHit_itr->second.mean() << "\t" << calibRecHit_itr->second.stdDev() << "\t" << calibRecHit_itr->second.num() << "\t" << calibRecHit_itr->second.meanE()
			     << "\t" << id.rawId() << std::endl;
		}
	}
	fout.close();
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
	int ix,iy,iz;
	int rawid = cal_itr->first.rawId();
	if(cal_itr->first.subdetId() == EcalBarrel) {
		EBDetId id(cal_itr->first);
		// Fill Rechit Energy
		EneMapEB_->Fill(id.ieta(), id.iphi(), cal_itr->second.meanE()); // 2D energy map
		TimeMapEB_->Fill(id.ieta(), id.iphi(), cal_itr->second.mean()); // 2D time map
		TimeErrorMapEB_->Fill(id.ieta(), id.iphi(), cal_itr->second.meanError());

		RechitEneEB_->Fill(cal_itr->second.meanE());   // 1D histogram
		RechitTimeEB_->Fill(cal_itr->second.mean()); // 1D histogram

		ix = id.ieta();
		iy = id.iphi();
		iz = 0;

	} else {
		// create EEDetId
		EEDetId id(cal_itr->first);
		if(id.zside() < 0) {
			EneMapEEM_->Fill(id.ix(), id.iy(), cal_itr->second.meanE());
			TimeMapEEM_->Fill(id.ix(), id.iy(), cal_itr->second.mean());
			TimeErrorMapEEM_->Fill(id.ix(), id.iy(), cal_itr->second.meanError());

			RechitEneEEM_->Fill(cal_itr->second.meanE());
			RechitTimeEEM_->Fill(cal_itr->second.mean());
		} else {
			EneMapEEP_->Fill(id.ix(), id.iy(), cal_itr->second.meanE());
			TimeMapEEP_->Fill(id.ix(), id.iy(), cal_itr->second.mean());
			TimeErrorMapEEP_->Fill(id.ix(), id.iy(), cal_itr->second.meanError());

			RechitEneEEP_->Fill(cal_itr->second.meanE());
			RechitTimeEEP_->Fill(cal_itr->second.mean());
		}

		ix = id.ix();
		iy = id.iy();
		iz = id.zside();
	}

	cal_itr->second.dumpCalibToTree(timingTree, rawid, ix, iy, iz);
}

void EcalTimingCalibProducer::FillHWCorrectionHists(EcalTimeCalibrationMap::const_iterator cal_itr)
{
	unsigned int elecID = (elecMap_->getElectronicsId(cal_itr->first).rawId() >> 6) & 0x3FFF;
	float time = _HWCalibrationMap[elecID].mean();
	if(cal_itr->first.subdetId() == EcalBarrel) {
		EBDetId id(cal_itr->first);
		// Fill Rechit Energy
		HWTimeMapEB_->Fill(id.ieta(), id.iphi(), time); // 2D time map
	} else {
		// create EEDetId
		EEDetId id(cal_itr->first);
		if(id.zside() < 0) {
			HWTimeMapEEM_->Fill(id.ix(), id.iy(), time);
		} else {
			HWTimeMapEEP_->Fill(id.ix(), id.iy(), time);
		}
	}

}
void EcalTimingCalibProducer::FillEnergyStabilityHists(EcalTimeCalibrationMap::const_iterator cal_itr, std::vector< std::pair<float, EcalCrystalTimingCalibration*> > energyStability)
{

	std::vector<TProfile2D*> * time_list;
	std::vector<TProfile2D*> * occu_list;
	int ix,iy,iz;
  	int 	rawid = cal_itr->first.rawId();
	//choose which map to store in
	if(cal_itr->first.subdetId() == EcalBarrel) {
		EBDetId id(cal_itr->first);
		time_list = &energyCutMapEB_;
		occu_list = &energyCutOccuMapEB_;
		ix = id.ieta();
		iy = id.iphi();
		iz = 0;
	} else {
		EEDetId id(cal_itr->first);
		ix = id.ix();
		iy = id.iy();
		iz = id.zside();
		if(id.zside() < 0) {
			time_list = &energyCutMapEEM_;
			occu_list = &energyCutOccuMapEEM_;
		} else {
			time_list = &energyCutMapEEP_;
			occu_list = &energyCutOccuMapEEP_;
		}
	}

	auto time_it = time_list->begin();
	auto occu_it = occu_list->begin();
	for(auto it = energyStability.begin(); it!=energyStability.end(); time_it++, occu_it++, it++)
	{
		(*time_it)->Fill(ix, iy, it->second->mean());
		(*occu_it)->Fill(ix, iy, it->second->num());

		// Add min_energy to the tree
		float min_energy = it->first;
		if(energyStabilityTree->GetBranch("min_energy") == NULL) energyStabilityTree->Branch("min_energy", &min_energy, "min_energy/F");
		energyStabilityTree->SetBranchAddress("min_energy", &min_energy);

		it->second->dumpCalibToTree(energyStabilityTree,rawid,ix,iy,iz);
	}

}
void EcalTimingCalibProducer::initEventHists(TFileDirectory fdir)
{
	Event_EneMapEB_   = fdir.make<TProfile2D>("EneMapEB",   "RecHit Energy[GeV] EB map;i#eta; i#phi;E[GeV]", 171, -85, 86, 360, 1., 361.);
	Event_TimeMapEB_  = fdir.make<TProfile2D>("TimeMapEB",  "Time [ns] EB map; i#eta; i#phi;Time[ns]",  	    171, -85, 86, 360, 1., 361.);
	Event_TimeMapEB_OOT  = fdir.make<TProfile2D>("TimeMapEB_OOT",  "Time [ns] EB map; i#eta; i#phi;Time[ns]",  	    171, -85, 86, 360, 1., 361.);

	Event_EneMapEEP_  = fdir.make<TProfile2D>("EneMapEEP",  "RecHit Energy[GeV] map EE+;ix;iy;E[GeV]", 100, 1, 101, 100, 1, 101);
	Event_TimeMapEEP_ = fdir.make<TProfile2D>("TimeMapEEP", "Time[ns] map EE+;ix;iy; Time[ns]", 	    100, 1, 101, 100, 1, 101);
	Event_TimeMapEEP_OOT  = fdir.make<TProfile2D>("TimeMapEEP_OOT", "Time[ns] map EE+;ix;iy; Time[ns]", 	    100, 1, 101, 100, 1, 101);

	Event_EneMapEEM_  = fdir.make<TProfile2D>("EneMapEEM",  "RecHit Energy[GeV] map EE-;ix;iy;E[GeV]", 100, 1, 101, 100, 1, 101);
	Event_TimeMapEEM_ = fdir.make<TProfile2D>("TimeMapEEM", "Time[ns] map EE-;ix;iy; Time[ns]",        100, 1, 101, 100, 1, 101);
	Event_TimeMapEEM_OOT  = fdir.make<TProfile2D>("TimeMapEEM_OOT", "Time[ns] map EE-;ix;iy; Time[ns]",        100, 1, 101, 100, 1, 101);
}

//
void EcalTimingCalibProducer::initHists(TFileDirectory fdir)
{
	EneMapEB_ = fdir.make<TProfile2D>("EneMapEB", "RecHit Energy[GeV] EB profile map;i#eta; i#phi;E[GeV]", 171, -85, 86, 360, 1., 361.);
	TimeMapEB_ = fdir.make<TProfile2D>("TimeMapEB", "Mean Time [ns] EB profile map; i#eta; i#phi;Time[ns]", 171, -85, 86, 360, 1., 361.);

	EneMapEEP_ = fdir.make<TProfile2D>("EneMapEEP", "RecHit Energy[GeV] profile map EE+;ix;iy;E[GeV]", 100, 1, 101, 100, 1, 101);
	TimeMapEEP_ = fdir.make<TProfile2D>("TimeMapEEP", "Mean Time[ns] profile map EE+;ix;iy; Time[ns]", 100, 1, 101, 100, 1, 101);
	EneMapEEM_ = fdir.make<TProfile2D>("EneMapEEM", "RecHit Energy[GeV] profile map EE-;ix;iy;E[GeV]", 100, 1, 101, 100, 1, 101);
	TimeMapEEM_ = fdir.make<TProfile2D>("TimeMapEEM", "Mean Time[ns] profile map EE-;ix;iy; Time[ns]", 100, 1, 101, 100, 1, 101);

	TimeErrorMapEB_ = fdir.make<TProfile2D>("TimeErrorMapEB", "Error Time [ns] EB profile map; i#eta; i#phi;Time[ns]", 171, -85, 86, 360, 1., 361.);

	TimeErrorMapEEP_ = fdir.make<TProfile2D>("TimeErrorMapEEP", "Error Time[ns] profile map EE+;ix;iy; Time[ns]", 100, 1, 101, 100, 1, 101);
	TimeErrorMapEEM_ = fdir.make<TProfile2D>("TimeErrorMapEEM", "Error Time[ns] profile map EE-;ix;iy; Time[ns]", 100, 1, 101, 100, 1, 101);

	RechitTimeEEM_ = fdir.make<TH1F>("RechitTimeEEM", "RecHit Mean Time[ns] EE-;RecHit Time[ns]; Events", 200, -50.0, 50.0);
	RechitTimeEEP_ = fdir.make<TH1F>("RechitTimeEEP", "RecHit Mean Time[ns] EE+;RecHit Time[ns]; Events", 200, -50.0, 50.0);
	RechitTimeEB_ = fdir.make<TH1F>("RechitTimeEB", "RecHit Mean Time[ns] EB;RecHit Time[ns]; Events", 200, -50.0, 50.0);

	RechitEneEEM_ = fdir.make<TH1F>("RechitEneEEM", "RecHit Energy[GeV] EE-;Rechit Energy[GeV]; Events", 200, 0.0, 100.0);
	RechitEneEEP_ = fdir.make<TH1F>("RechitEneEEP", "RecHit Energy[GeV] EE+;Rechit Energy[GeV]; Events", 200, 0.0, 100.0);
	RechitEneEB_ = fdir.make<TH1F>("RechitEneEB", "RecHit Energy[GeV] EB;Rechit Energy[GeV]; Events", 200, 0.0, 100.0);

	RechitEnergyTimeEEM = fdir.make<TH2F>("RechitEnergyTimeEEM", "RecHit Energy vs Time EE-;Rechit Energy[GeV]; Time[ns]; Events", 200, 0.0, 1000.0, 100, -15, 30);
	RechitEnergyTimeEEP = fdir.make<TH2F>("RechitEnergyTimeEEP", "RecHit Energy vs Time EE+;Rechit Energy[GeV]; Time[ns]; Events", 200, 0.0, 1000.0, 100, -15, 30);
	RechitEnergyTimeEB  = fdir.make<TH2F>("RechitEnergyTimeEB",  "RecHit Energy vs Time EB; Rechit Energy[GeV]; Time[ns]; Events", 200, 0.0, 100.0,  100, -15, 30);

	// HW Histograms
	
	HWTimeMapEEP_ = fdir.make<TProfile2D>("HWTimeMapEEP", "Mean HW Time[ns] profile map EE+;ix;iy; Time[ns]", 100, 1, 101, 100, 1, 101);
	HWTimeMapEEM_ = fdir.make<TProfile2D>("HWTimeMapEEM", "Mean HW Time[ns] profile map EE-;ix;iy; Time[ns]", 100, 1, 101, 100, 1, 101);
	HWTimeMapEB_  = fdir.make<TProfile2D>("HWTimeMapEB",  "Mean HW Time[ns] EB profile map; i#eta; i#phi;Time[ns]", 171, -85, 86, 360, 1., 361.);


	TFileDirectory energyCutDir = fdir.mkdir("EnergyCutMaps");

	for(double en_cut = _minRecHitEnergy; en_cut < _minRecHitEnergy + N_ENERGY_STEPS * _minRecHitEnergyStep ; en_cut += _minRecHitEnergyStep) 
	{
		std::string en_cut_str = std::to_string(en_cut);
		energyCutMapEB_ .push_back(energyCutDir.make<TProfile2D>(("EnergyCutMapEB"  + en_cut_str).c_str(), ("Mean Time[ns] E > " + en_cut_str + "GeV EB ; i#eta; i#phi;Time[ns]").c_str(), 171, -85, 86, 360, 1., 361.));
		energyCutMapEEP_.push_back(energyCutDir.make<TProfile2D>(("EnergyCutMapEEP" + en_cut_str).c_str(), ("Mean Time[ns] E > " + en_cut_str + "GeV EE+;ix;iy; Time[ns]").c_str(), 100, 1, 101, 100, 1, 101));
		energyCutMapEEM_.push_back(energyCutDir.make<TProfile2D>(("EnergyCutMapEEM" + en_cut_str).c_str(), ("Mean Time[ns] E > " + en_cut_str + "GeV EE-;ix;iy; Time[ns]").c_str(), 100, 1, 101, 100, 1, 101));

		energyCutOccuMapEB_ .push_back(energyCutDir.make<TProfile2D>(("EnergyCutOccuMapEB"  + en_cut_str).c_str(), ("Occupancy E > " + en_cut_str + "GeV EB ; i#eta; i#phi;Time[ns]").c_str(), 171, -85, 86, 360, 1., 361.));
		energyCutOccuMapEEP_.push_back(energyCutDir.make<TProfile2D>(("EnergyCutOccuMapEEP" + en_cut_str).c_str(), ("Occupancy E > " + en_cut_str + "GeV EE+;ix;iy; Time[ns]").c_str(), 100, 1, 101, 100, 1, 101));
		energyCutOccuMapEEM_.push_back(energyCutDir.make<TProfile2D>(("EnergyCutOccuMapEEM" + en_cut_str).c_str(), ("Occupancy E > " + en_cut_str + "GeV EE-;ix;iy; Time[ns]").c_str(), 100, 1, 101, 100, 1, 101));
	}

}

//
void EcalTimingCalibProducer::initTree(TFileDirectory fdir)
{
	dumpTree = fdir.make<TTree>("dumpTree", "");
	timingTree = fdir.make<TTree>("timingTree", "");
	energyStabilityTree = fdir.make<TTree>("energyStabilityTree", "");
}

//define this as a plug-in
DEFINE_FWK_LOOPER(EcalTimingCalibProducer);
