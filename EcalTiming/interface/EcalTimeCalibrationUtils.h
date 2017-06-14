#include <fstream>
#include <string>
#include <vector>
#include <iostream>
#include <map>
#include <vector>
#include <algorithm>
#include <functional>
#include <set>
#include <assert.h>
#include <time.h>

#include <TMath.h>
#include <Math/VectorUtil.h>


class EcalTimeCalibrationUtils
{

private:

	float _sum; ///< scalar sum of the time of each timingEvent
	float _sum2; ///< scalar sum of the square of the time of each timingEvent
	unsigned long int _num; ///< number of timingEvents;

	mutable std::map<float, float> _sumWithinNSigma, _sum2WithinNSigma, _sum3WithinNSigma, _sumEWithinNSigma; ///< variables for calculation of mean, stdDev within n-times the origina stdDev (to remove tails)
	mutable std::map<float, unsigned int> _numWithinNSigma; ///< variables for calculation of mean, stdDev within n-times the origina stdDev (to remove tails)
        std::vector<float> _timingEvents;
public:
	/// default constructor
	EcalTimeCalibrationUtils() :
		_sum(0), _sum2(0), _num(0)
	{
	}

        bool add(std::vector<float>& timingEvents);

	inline unsigned int num() const
	{
		return _num;
	};
        inline float sum() const
	{
		return _sum;
	};
	inline float mean() const
	{
		if(!_num) return -999.f;
		return _sum / _num;
	}; 
	inline float stdDev() const  
	{
		float mean_ = mean();
		return sqrt(_sum2 / _num - mean_ * mean_);
	};
	inline float meanError() const
	{
		return stdDev() / sqrt(_num);
	};
	
	float getMeanWithinNSigma(float sigma, float maxRange) const; ///< returns the mean time within abs(mean+ n * stdDev) to reject tails
	float getStdDevWithinNSigma(float sigma, float maxRange) const; ///< returns the stdDev calculated within abs(mean+ n * stdDev) to reject tails
	float getNumWithinNSigma(float sigma, float maxRange) const; ///< returns the num calculated within abs(mean+ n * stdDev) to reject tails
	float getMeanErrorWithinNSigma(float sigma, float maxRange) const; ///< returns the error on the mean calculated within abs(mean+ n * stdDev) to reject tails
	float getSkewnessWithinNSigma(float sigma, float maxRange) const; ///< returns the skewness calculated within abs(mean+ n * stdDev) to reject tails

	inline void clear()
	{
		_sum = 0.0f;
		_sum2 = 0.0f;
		_num = 0;
		_sumWithinNSigma.clear();
		_sum2WithinNSigma.clear();
		_sum3WithinNSigma.clear();
		_numWithinNSigma.clear();
	}

private:
	void calcAllWithinNSigma(float n_sigma, float maxRange = 10) const; ///< calculate sum, sum2, sum3, n for time if time within n x stdDev and store the result
	// since the values are stored, the calculation is done only once with only one loop over the events

};
