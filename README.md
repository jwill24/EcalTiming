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
    * NOTE: the outputs are produced in one step and CANNOT BE MERGED with other outputs.
    
3) Run on parallel (using LXBATCH):

   * launch:
   
      * voms-proxy-init --voms cms --valid 168:00
      * cd lxbatch
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
   
    
