EcalTiming
================

1) Install:

    * scram project CMSSW_10_0_3
    * cd CMSSW_10_0_3
    * cmsenv
    * git cms-addpkg CondTools/Ecal
    * git clone  git@github.com:bmarzocc/EcalTiming.git
    * cd EcalTiming
    * git checkout Run2018
    * cd -
    * cp EcalTiming/EcalTiming/interface/EcalFloatCondObjectContainerXMLTranslator.h CondTools/Ecal/interface/
    * rm EcalTiming/EcalTiming/interface/EcalFloatCondObjectContainerXMLTranslator.h
    * cp EcalTiming/EcalTiming/src/EcalFloatCondObjectContainerXMLTranslator.cc CondTools/Ecal/src/
    * rm EcalTiming/EcalTiming/src/EcalFloatCondObjectContainerXMLTranslator.cc
    * cp EcalTiming/EcalTiming/test/testEcalTimeCalib.py CondTools/Ecal/python/
    * rm EcalTiming/EcalTiming/test/testEcalTimeCalib.py
    * scram b -j 5

2) Run local:

    * cd EcalTiming/EcalTiming/
    * cmsRun test/ecalTime_fromAlcaStream_cfg.py files=root://cms-xrd-global.cern.ch//store/data/Commissioning2017/AlCaPhiSym/RAW/v1/000/293/910/00000/181C8C47-8237-E711-9089-02163E0118FF.root globaltag=90X_dataRun2_HLT_v2
    * NOTE: the outputs are produced in one step and CANNOT BE MERGED with other outputs.
    
3) Run on parallel (using LXBATCH):

   * launch 1st step (ntuple step):
   
      * cd EcalTiming/EcalTiming/lxbatch/
      * voms-proxy-init --voms cms --valid 168:00
      * perl launchJobs_lxbatch.pl params_lxbatch.CFG
      * sh lancia.sh
      
   * Parameters settings in "params_lxbatch.CFG":
   
      * BASEDir: absolute path of the lxbatch directory
      * X509_USER_PROXY: path of the proxy (before launching better do: export X509_USER_PROXY=/afs/cern.ch/work/X/XXX/x509up_XXX)
      * JOBCfgTemplate: name of the python to launch
      * DATASETName: name of the dataset to be run
      * INPUTRuns: input runs
      * OUTPUTSAVEPath: path of the output files (EOS directories as default)
      * OUTPUTFILEName: name of the output file.root
      * QUEUE: lxbatch queue
      * JOBdir: directory to store job directories
      * JSONFile: json file
      * GT: gloabl tag
      
   * launch 2nd step (calibration step):
   
      * cd EcalTiming/EcalTiming/lxbatch/
      * voms-proxy-init --voms cms --valid 168:00
      * perl launchJobs_lxbatch_calibStep.pl params_lxbatch_calibStep.CFG
      * sh lancia.sh
      
   * Parameters settings in "params_lxbatch_calibStep.CFG":
   
      * BASEDir: absolute path of the lxbatch directory
      * JOBCfgTemplate: name of the python to launch
      * INPUTDir: directory of input runs (output of the 1st step)
      * INPUTRuns: input runs
      * OUTPUTSAVEPath: path of the output files (EOS directories as default)
      * QUEUE: lxbatch queue

4) Produce the sql tag file:

   * The output of the calibration needs to have the following name format:

     * eg: ecalTiming-corr.dat -> ecalTiming-corr_2017_09_26.dat

   * Produce the absolute time calibration (xml file) from the latest IOV:
     
     * cd EcalTiming/EcalTiming/test/
     * eg: python makeTimingXML.py --tag=EcalTimeCalibConstants_v01_express --inList=input_List_2017.dat
     * eg: python makeTimingXML.py --tag=EcalTimeCalibConstants_v01_express --calib=/eos/cms/store/group/dpg_ecal/alca_ecalcalib/EcalTiming/Run2017E/Calibration/303948/ecalTiming-corr_2017_09_26.dat
     * eg: python makeTimingXML.py --payload=2cc0da4e6a1ec506d037aa476e76bca8ac9ab9fb --inList=input_List_2017.dat
     * eg: python makeTimingXML.py --payload=2cc0da4e6a1ec506d037aa476e76bca8ac9ab9fb --calib=/eos/cms/store/group/dpg_ecal/alca_ecalcalib/EcalTiming/Run2017E/Calibration/303948/ecalTiming-corr_2017_09_26.dat
     
   * Produce the sqlite file from the absolute timing xml file:
     
     * cd EcalTiming/EcalTiming/test/
     * eg: python makeTimingSqlite.py --calib=/eos/cms/store/group/dpg_ecal/alca_ecalcalib/EcalTiming/Run2017E/Calibration/303948/ecalTiming-abs_2017_09_26.xml --tag=EcalTimeCalibConstants_Legacy2017_v1
     * eg: python makeTimingSqlite.py --inList=input_List_2017_absTiming.dat --tag=EcalTimeCalibConstants_Legacy2017_v1 
     * sh launch_tagCreation.sh
   
5) Make history plot:
   
   * cd EcalTiming/EcalTiming/test/
   * eg: python makeHistoryPlot.py --tag=EcalTimeCalibConstants_v01_express --year=2017
   * eg: python makeHistoryPlot.py --inList=input_List_2017.dat
   * eg: python makeHistoryPlot.py --inList=input_List_2017.dat --runBased
   * eg: python makeHistoryPlot.py --inList=input_List_2017_RunE.dat --epoch=E
   * eg: python makeHistoryPlot.py --inList=input_List_2017_absTiming.dat --absTime 

    

    
