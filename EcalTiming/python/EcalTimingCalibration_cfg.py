import FWCore.ParameterSet.Config as cms

process = cms.PSet()

process.ioFilesOpt = cms.PSet(

    ##input file
    inputFile = cms.string('output/ecalTiming.root'),
    
    ##input tree
    inputTree = cms.string('/timing/EcalSplashTiming/timingEventsTree'),

    ## base output directory: default $CMSSW_BASE/src/EcalTiming/EcalTiming/output/
    outputDir = cms.string(''),

    ## base output: default ecalTiming.dat
    outputCalib = cms.string(''),
     
    ## base output: default ecalTiming-corr.dat
    outputCalibCorr = cms.string(''),

    ## base output: default ecalTiming.root
    outputFile = cms.string('')
)

process.calibOpt = cms.PSet(

    ## nSigma
    nSigma = cms.int32(2),

    ## maxRange
    maxRange = cms.int32(10)
    
)

