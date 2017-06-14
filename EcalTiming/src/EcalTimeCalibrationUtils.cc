#include "EcalTiming/EcalTiming/interface/EcalTimeCalibrationUtils.h"
#include <cassert>

float EcalTimeCalibrationUtils::getNumWithinNSigma(float n_sigma, float maxRange) const
{

	if(_numWithinNSigma.count(n_sigma) == 0) calcAllWithinNSigma(n_sigma, maxRange);
	return _numWithinNSigma[n_sigma];
}

float EcalTimeCalibrationUtils::getMeanWithinNSigma(float n_sigma, float maxRange) const
{

	if(_numWithinNSigma.count(n_sigma) == 0) calcAllWithinNSigma(n_sigma, maxRange);
	return _sumWithinNSigma[n_sigma] / _numWithinNSigma[n_sigma];
}

float EcalTimeCalibrationUtils::getStdDevWithinNSigma(float n_sigma, float maxRange) const
{

	float mean = getMeanWithinNSigma(n_sigma, maxRange); //variables are calculated by that
	return sqrt(_sum2WithinNSigma[n_sigma] / _numWithinNSigma[n_sigma] - mean * mean);
}

float EcalTimeCalibrationUtils::getMeanErrorWithinNSigma(float n_sigma, float maxRange) const
{

	float stddev = getStdDevWithinNSigma(n_sigma, maxRange); //variables are calculated by that
	return stddev / sqrt(_numWithinNSigma[n_sigma]);
}

float EcalTimeCalibrationUtils::getSkewnessWithinNSigma(float n_sigma, float maxRange) const
{

	float mean = getMeanWithinNSigma(n_sigma, maxRange); //variables are calculated by that
	float stdDev = getStdDevWithinNSigma(n_sigma, maxRange);
	return (_sum3WithinNSigma[n_sigma] / _numWithinNSigma[n_sigma] - 3 * mean * stdDev * stdDev - mean * mean * mean) / (stdDev * stdDev * stdDev);

}


// store the results such that you do only one loop over the events
void EcalTimeCalibrationUtils::calcAllWithinNSigma(float n_sigma, float maxRange) const
{
	
	float range = std::min(maxRange, stdDev() * n_sigma);

	_sumWithinNSigma[n_sigma] = 0.;
	_sum2WithinNSigma[n_sigma] = 0;
	_sum3WithinNSigma[n_sigma] = 0.;
	_numWithinNSigma[n_sigma] = 0.;

	for(auto te : _timingEvents) {
		if(fabs(te - mean()) < range) {
			_sumWithinNSigma[n_sigma] += te;
			_sum2WithinNSigma[n_sigma] += te * te;
			_sum3WithinNSigma[n_sigma] += te * te * te;
			_numWithinNSigma[n_sigma]++;
		}
	}
	return;
}

bool EcalTimeCalibrationUtils::add(std::vector<float>& timingEvents)
{
        _timingEvents = timingEvents;
        _num = _timingEvents.size();
        for(auto te : _timingEvents)
            _sum += te;
        for(auto te : _timingEvents)
            _sum2 += te * te;

        return true;
}

