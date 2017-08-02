EcalTiming
================

1) Install:

    * scram project CMSSW_9_0_0
    * cd CMSSW_9_0_0
    * cmsenv
    * git cms-merge-topic previsualconsent:iRingSubdet804
    * git cms-addpkg CondTools/Ecal
    * git clone  git@github.com:bmarzocc/EcalTiming.git
    * cd EcalTiming
    * git checkout Run2017
    * cd -
    * cp EcalTiming/EcalTiming/interface/EcalFloatCondObjectContainerXMLTranslator.h CondTools/Ecal/interface/
    * rm EcalTiming/EcalTiming/interface/EcalFloatCondObjectContainerXMLTranslator.h
    * cp EcalTiming/EcalTiming/src/EcalFloatCondObjectContainerXMLTranslator.cc CondTools/Ecal/src/
    * rm EcalTiming/EcalTiming/src/EcalFloatCondObjectContainerXMLTranslator.cc
    * cp EcalTiming/EcalTiming/test/testEcalTimeCalib.py CondTools/Ecal/python/
    * rm EcalTiming/EcalTiming/test/testEcalTimeCalib.py
    * scram b -j 5

2) Run:

    * cd EcalTiming/EcalTiming/
    * cmsRun test/ecalTime_fromAlcaStream_cfg.py files=root://cms-xrd-global.cern.ch//store/data/Commissioning2017/AlCaPhiSym/RAW/v1/000/293/910/00000/181C8C47-8237-E711-9089-02163E0118FF.root globaltag=90X_dataRun2_HLT_v2
    * NOTE: the outputs are produced in one step and CANNOT BE MERGED with other outputs.
    
3) Run on parallel (using LXBATCH):

   * launch:
   
      * cd EcalTiming/EcalTiming/lxbatch/
      * voms-proxy-init --voms cms --valid 168:00
      * perl launchJobs_lxbatch.pl params_lxbatch.CFG
      * sh lancia.sh
      
   * Parameters settings in "params_lxbatch.CFG":
   
      * BASEDir: absolute path of the lxbatch directory
      * X509_USER_PROXY: path of the proxy (before launching better do: export X509_USER_PROXY= /afs/cern.ch/work/X/XXX/x509up_XXX)
      * JOBCfgTemplate: name of the python to launch
      * DATASETName: name of the dataset to be run
      * RUNNumber: run number
      * OUTPUTSAVEPath: path of the output files (EOS directories as default)
      * OUTPUTFILEName: name of the output file.root
      * QUEUE: lxbatch queue
      * JOBdir: directory to store job directories
      * JSONFile: json file
      * GT: gloabl tag
      
   * Final step on one unique final file.root: 
      
      * cd EcalTiming/EcalTiming/
      * EcalTimingCalibration python/EcalTimingCalibration_cfg.py
      * EcalTimingCalibration_cfg.py options:
      
         * inputFile: final file.root
         * inputTree: tree name, by default "/timing/EcalSplashTiming/timingEventsTree"
         * outputDir: output directory, by default "$CMSSW_BASE/src/EcalTiming/EcalTiming/output/" 
         * outputCalib: first calibration output, by default "ecalTiming.dat"
         * outputCalibCorr: second calibration output, by default "ecalTiming-corr.dat"
         * outputFile: output file.root with histograms, by default "ecalTiming.root"

4) Produce the sql tag file:

   * Produce the absolute time calibration (xml file) from the latest IOV:
     
     * cd EcalTiming/EcalTiming/test/
     * python makeTimeCalibConstantsTag_step1.py --tag EcalTimeCalibConstants_v08_offline --calib ../output/ecalTiming-corr.dat --output EcalTimeCalibConstants_IOV.xml
     
   * Produce the sqlite file from EcalTimeCalibConstants_IOV.xml (change the xml input in testEcalTimeCalib.py):
     
     * cd CondTools/Ecal/python/
     * cmsRun testEcalTimeCalib.py 
    

    
