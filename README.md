CalibCalorimetry
================

Compiling:

  scram project CMSSW_9_0_0
  cd CMSSW_9_0_0/src
  cmsenv
  git cms-merge-topic previsualconsent:iRingSubdet804
  git clone  git@github.com:bmarzocc/EcalTiming.git
  cd EcalTiming
  git checkout Run2017
  cd - 
  scram b -j16
