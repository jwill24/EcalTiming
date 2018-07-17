import FWCore.ParameterSet.Config as cms

timing = cms.EDFilter("EcalTimingCalibProducer",
                    isSplash = cms.bool(False),
                    makeEventPlots = cms.bool(False),
                    applyAmpThresEB = cms.bool(False),
                    applyAmpThresEE = cms.bool(False),
                    ebUncalibRechits = cms.InputTag("ecalMultiFitUncalibRecHit","EcalUncalibRecHitsEB"),
                    eeUncalibRechits = cms.InputTag("ecalMultiFitUncalibRecHit","EcalUncalibRecHitsEE"),
                    timingCollection = cms.InputTag("EcalTimingEvents"),
                    recHitMinimumN = cms.uint32(2),
                    minRecHitEnergyStep = cms.double(0.5),
                    minRecHitEnergyNStep = cms.double(10),
                    energyThresholdOffsetEE = cms.double(0.0),
                    energyThresholdOffsetEB = cms.double(0.0),
                    ampCut_barrelP = cms.vdouble(16.31759, 18.33355, 18.34853, 18.36281, 18.37667, 18.39011, 18.40334, 18.41657, 18.42994, 18.44359, 18.45759, 18.47222, 18.48748, 18.50358, 18.52052, 18.53844, 18.55755, 18.57778, 18.59934, 18.62216, 18.64645, 18.67221, 18.69951, 18.72849, 18.75894, 18.79121, 18.82502, 18.86058, 18.89796, 18.93695, 18.97783, 19.02025, 19.06442, 19.11041, 19.15787, 19.20708, 19.25783, 19.31026, 19.36409, 19.41932, 19.47602, 19.53384, 19.5932, 19.65347, 19.715, 19.77744, 19.84086, 19.90505, 19.97001, 16.03539, 18.10147, 18.16783, 18.23454, 18.30146, 18.36824, 18.43502, 18.50159, 18.56781, 18.63354, 18.69857, 18.76297, 18.82625, 18.88862, 18.94973, 19.00951, 19.06761, 19.12403, 19.1787, 19.23127, 19.28167, 19.32955, 19.37491, 19.41754, 19.45723, 19.49363, 19.52688, 19.55642, 19.58218, 19.60416, 19.62166, 19.63468, 19.64315, 19.64665, 19.6449, 19.6379),
                    ampCut_barrelM = cms.vdouble(14.31759, 18.33355, 18.34853, 18.36281, 18.37667, 18.39011, 18.40334, 18.41657, 18.42994, 18.44359, 18.45759, 18.47222, 18.48748, 18.50358, 18.52052, 18.53844, 18.55755, 18.57778, 18.59934, 18.62216, 18.64645, 18.67221, 18.69951, 18.72849, 18.75894, 18.79121, 18.82502, 18.86058, 18.89796, 18.93695, 18.97783, 19.02025, 19.06442, 19.11041, 19.15787, 19.20708, 19.25783, 19.31026, 19.36409, 19.41932, 19.47602, 19.53384, 19.5932, 19.65347, 19.715, 19.77744, 19.84086, 19.90505, 19.97001, 16.03539, 18.10147, 18.16783, 18.23454, 18.30146, 18.36824, 18.43502, 18.50159, 18.56781, 18.63354, 18.69857, 18.76297, 18.82625, 18.88862, 18.94973, 19.00951, 19.06761, 19.12403, 19.1787, 19.23127, 19.28167, 19.32955, 19.37491, 19.41754, 19.45723, 19.49363, 19.52688, 19.55642, 19.58218, 19.60416, 19.62166, 19.63468, 19.64315, 19.64665, 19.6449, 19.6379),
                    ampCut_endcapP = cms.vdouble(16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0),
                    ampCut_endcapM = cms.vdouble(16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0),
                    eThresholdsEB = cms.vdouble(
        1.00751, 1.01408, 1.01886, 1.02209, 1.02395, 1.02462, 1.02426, 1.02301, 1.02099, 1.01832,
        1.01508, 1.01139, 1.00731, 1.00292, 0.998285, 0.993462, 0.988504, 0.983455, 0.978355, 0.973239,
        0.968136, 0.963071, 0.958066, 0.953138, 0.948299, 0.943562, 0.938933, 0.934416, 0.930016, 0.925731,
        0.92156, 0.917501, 0.913549, 0.909699, 0.905944, 0.902278, 0.898694, 0.895184, 0.89174, 0.888355,
        0.885023, 0.881736, 0.878489, 0.875276, 0.872093, 0.868936, 0.865802, 0.862691, 0.859601, 0.856534,
        0.853489, 0.850472, 0.847485, 0.844534, 0.841625, 0.838765, 0.835961, 0.833224, 0.830561, 0.827984,
        0.825503, 0.823129, 0.820872, 0.818743, 0.816752, 0.814909, 0.813222, 0.811699, 0.810346, 0.809167,
        0.808164, 0.807336, 0.80668, 0.806189, 0.805852, 0.805656, 0.805582, 0.805606, 0.8057, 0.805828,
        0.805952, 0.806024, 0.80599, 0.805788, 0.805348, 0.805309, 0.80571, 0.805873, 0.805868, 0.805758,
        0.805595, 0.805427, 0.805295, 0.805232, 0.805267, 0.805424, 0.805722, 0.806174, 0.806791, 0.80758,
        0.808543, 0.809683, 0.810995, 0.812478, 0.814124, 0.815926, 0.817876, 0.819964, 0.822179, 0.824511,
        0.82695, 0.829484, 0.832104, 0.834798, 0.837558, 0.840375, 0.84324, 0.846146, 0.849088, 0.852061,
        0.85506, 0.858082, 0.861126, 0.864191, 0.867278, 0.870389, 0.873525, 0.876691, 0.879891, 0.88313,
        0.886414, 0.889751, 0.893146, 0.896607, 0.900142, 0.903758, 0.907462, 0.911262, 0.915162, 0.91917,
        0.923288, 0.92752, 0.931867, 0.936329, 0.940904, 0.945586, 0.950368, 0.95524, 0.960188, 0.965195,
        0.97024, 0.975298, 0.980339, 0.985329, 0.990229, 0.994993, 0.99957, 1.0039, 1.00792, 1.01156,
        1.01474, 1.01737, 1.01934, 1.02054, 1.02085, 1.02014, 1.01824, 1.01499, 1.01018, 1.00359        
                    ), 
                    parAThresholds_endcap = cms.vdouble(10, 0.945), # B + A*ring 2018 thr are defined as two linear cut (one for iring<30 and one above)
                    parBThresholds_endcap = cms.vdouble(150, -21.865),# B + A*ring 2018 thr are defined as two linear cut (one for iring<30 and one above)
                    minEntries = cms.uint32(1),
                    globalOffset = cms.double(0.),
                    storeEvents = cms.bool(False),
                    produceNewCalib = cms.bool(True),
                    outputDumpFile = cms.string('output.dat'),
                    maxSkewnessForDump = cms.double(2),
                    )
