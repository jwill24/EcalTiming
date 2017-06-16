EcalTiming
================

1) Install:

    * scram project CMSSW_9_0_0
    * cd CMSSW_9_0_0
    * cmsenv
    * git cms-merge-topic previsualconsent:iRingSubdet804
    * git clone  git@github.com:bmarzocc/EcalTiming.git
    * cd EcalTiming
    * git checkout Run2017
    * cd -
    * scram b -j 5

2) Run:

    * cmsRun test/ecalTime_fromAlcaStream_cfg.py files=root://cms-xrd-global.cern.ch//store/data/Commissioning2017/AlCaPhiSym/RAW/v1/000/293/910/00000/181C8C47-8237-E711-9089-02163E0118FF.root globaltag=90X_dataRun2_HLT_v2
    * NOTE: the output are produced in one step and CANOOT BE MERGED
    
