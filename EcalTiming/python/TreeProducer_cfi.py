import FWCore.ParameterSet.Config as cms

treeProducer = cms.EDAnalyzer('TreeProducer',
    sqrtS = cms.double(13.e3),
    outputFilename = cms.string('output.root'),
)
