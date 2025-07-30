#pragma once
#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable: 4351 4996)
#endif

#ifndef NOMINMAX
#define NOMINMAX
#endif

#include <string>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <cfloat>
#include <vector>
#include <ostream>
#include <sstream>
#include <locale>
#include <codecvt>
#include <cmath>

#ifndef AIMMSAPI_USE_WCHAR
#define AIMMSAPI_USE_WCHAR 1
#endif

template <typename inString, typename outString>
inline outString *___stringncpy(outString *dest, const inString *orig, int n) {
	outString *ret = dest;
	while (*orig && --n) *dest++ = *orig++;
	*dest = 0;
	return ret;
}

inline wchar_t *___wcsncpy(wchar_t *dest, const wchar_t *orig, int n) {
	return ___stringncpy<wchar_t, wchar_t>(dest, orig, n);
}

inline char *___strncpy(char *dest, const char *orig, int n) {
	return ___stringncpy<char, char>(dest, orig, n);
}

#if defined(AIMMSAPI_USE_WCHAR) && AIMMSAPI_USE_WCHAR==1
#define CHARTYPE wchar_t
#define STRINGTYPE std::wstring
#define TO_STRING(txt) ___convert(txt)
#define OSTREAMTYPE std::wostream
#define _STRNCPY ___wcsncpy
#define _STRNCMP wcsncmp
#define _STRLEN wcslen
#ifndef UNICODE
#define UNICODE
#endif
#define ___T(x)   L ## x
#define _TEXT_(x)  ___T(x)
#else
#define CHARTYPE char
#define STRINGTYPE std::string
#define TO_STRING(txt) txt
#define OSTREAMTYPE std::ostream
#define _STRNCPY ___strncpy
#define _STRNCMP strncmp
#define _STRLEN strlen
#undef UNICODE
#define ___T(x)   x
#define _TEXT_(x)  ___T(x)
#endif

#include "AimmsFactory.h"

class NormalizerCLass {
public:
	virtual STRINGTYPE Normalize(const std::string&) = 0;
	virtual STRINGTYPE Normalize(const std::wstring&) = 0;
	virtual std::string NormalizeA(const std::string&) = 0;
};

using NormalizerPtr = NormalizerCLass*;

constexpr int DefaultStringSize = 1024;
constexpr int MediumStringSize	= 8 * 1024;
constexpr int LongStringSize	= 64 * 1024;
constexpr int MaxStringSize		= 1024 * 1024;

inline int GetMaxStringSize() {
	return MaxStringSize;
}

inline int LimitStringSize(int x) {
	return std::min(std::max(x, DefaultStringSize), MaxStringSize);
}

inline int LimitPrecision(int precision) {
	return std::min(std::max(precision, -1), 16);
}

enum AimmsStorageType {
	Handle = aimmsifc::Storage::Handle,
	Double = aimmsifc::Storage::Double,
	Int = aimmsifc::Storage::Int,
	Binary = aimmsifc::Storage::Binary,
	String = aimmsifc::Storage::String
};

typedef aimmsifc::AimmsValueType<wchar_t> AimmsValue;

union AimmsValueTypeExt {
	AimmsValue AimmsVal;
	int64_t	   Int64;
};

typedef AimmsValueTypeExt AimmsValueExt;
typedef aimmsifc::iAimmsW::String AimmsString;



inline AimmsStorageType DetermineAimmsStorageType(int handle) {
	int storage = 0;

	getAimms()->AttributeStorage(handle, &storage);
	return static_cast<AimmsStorageType>(storage);
}

class AimmsVariant {
	int m_tuple[aimmsifc::MaxDimension] = {};
	AimmsValueExt val = {};
	AimmsValueExt convertedVal = {};
	STRINGTYPE m_internalBuf;
	AimmsStorageType m_storage;
	CHARTYPE* m_bufPtr = nullptr;
	int m_bufSize	   = 0;
	size_t m_dimension;
	STRINGTYPE m_normalizedString;
	std::string m_string;

	void Init(CHARTYPE* initBuf = nullptr, int initSize = 0) {
		if (m_storage == AimmsStorageType::String) {
			if (initBuf) {
				m_bufPtr = initBuf;
				m_bufSize = initSize;
				val.AimmsVal.String.buf = m_bufPtr;
				val.AimmsVal.String.Length = m_bufSize;
			}
			else {
				setStringSize(m_bufSize);
			}
		}
	}
public:
	AimmsVariant(AimmsStorageType storage = AimmsStorageType::String, int size = DefaultStringSize, int dimension = 0)
		: m_storage((storage == AimmsStorageType::Binary) ? AimmsStorageType::Int : storage)
		, m_dimension(dimension)
	{
		m_bufSize = LimitStringSize(size);
		Init();
	}

	AimmsVariant(const std::wstring& string, int dimension = 0)
		: m_storage(AimmsStorageType::String)
		, m_dimension(dimension)
	{
		Init();
		setAsString(string);
	}

	AimmsVariant(CHARTYPE* initBuf, int initSize)
		: m_storage(AimmsStorageType::String)
		, m_dimension(0)
	{
		Init(initBuf, initSize);
	}

	AimmsVariant(const int n, int dimension = 0)
		: m_storage(AimmsStorageType::Int)
		, m_dimension(dimension)
	{
		Init();
		setAsInt(n);
	}

	AimmsVariant(const double& d, int dimension = 0)
		: m_storage(AimmsStorageType::Double)
		, m_dimension(dimension)
	{
		Init();
		setAsDouble(d);
	}

	~AimmsVariant() {}

	void setStorageType(AimmsStorageType storage) {
		m_storage = storage;
	}

	void setStringSize(int size) {
		m_bufSize = LimitStringSize(size);
		m_internalBuf.resize(m_bufSize);
		m_bufPtr = (CHARTYPE *)m_internalBuf.data();

		resetAsValue();
	}
	
	int getStringSize() const {
		return m_bufSize;
	}
	
	int* tuple() {
		return m_tuple;
	}

	int& tuple(size_t i) {
		return m_tuple[i];
	}

	int& operator [](size_t i) {
		return m_tuple[i];
	}

	int setTuple(size_t i, int el) {
		return (m_tuple[i] = el);
	}

	bool copyTuple(const AimmsVariant& other) {
		memcpy(m_tuple, other.m_tuple, sizeof(m_tuple));

		return true;
	}

	AimmsStorageType& StorageType() { return m_storage; }
	size_t& Dimension() { return m_dimension; }

	AimmsVariant& reset() {
		resetAsValue();
		return *this;
	}

	AimmsVariant& operator =(const AimmsVariant& other) {
		m_storage = other.m_storage;
		m_dimension = other.m_dimension;

		setAsVariant(other);
		return *this;
	}

	AimmsValue* resetAsValue() {
		if (m_storage == AimmsStorageType::String) {
			val.AimmsVal.String.buf = m_bufPtr;
			m_bufPtr[0] = 0;
			val.AimmsVal.String.Length = m_bufSize;
			m_string.clear();
		}
		else {
			val.AimmsVal.Double = 0;
		}

		return &val.AimmsVal;
	}

	AimmsValueExt* resetAsExtValue() {
		if (m_storage == AimmsStorageType::String) {
			val.AimmsVal.String.buf = m_bufPtr;
			m_bufPtr[0] = 0;
			val.AimmsVal.String.Length = m_bufSize;
			m_string.clear();
		}
		else {
			val.AimmsVal.Double = 0;
		}

		return &val;
	}

	AimmsString* resetAsString() {
		return (AimmsString*)resetAsValue();
	}

	AimmsVariant& setAsString(const std::wstring& s, NormalizerPtr normalizer = nullptr) {
		if (m_storage == AimmsStorageType::String) {
			val.AimmsVal.String.Length = std::min(m_bufSize, (int)s.size());
			_STRNCPY(m_bufPtr, normalizer ? normalizer->Normalize(s).c_str() : s.c_str(), m_bufSize);
			val.AimmsVal.String.buf = m_bufPtr;
		}

		return *this;
	}

	AimmsVariant& setAsString(const std::string& s, NormalizerPtr normalizer = nullptr) {
		if (m_storage == AimmsStorageType::String) {
			m_string = normalizer ? normalizer->NormalizeA(s) : s;
		}

		return *this;
	}

	std::string& GetString() {
		return m_string;
	}

	AimmsVariant& setAsInt(const int64_t n) {
		if (m_storage == AimmsStorageType::Double) {
			val.AimmsVal.Double = (double)n;
		} else {
			val.Int64 = n;
			m_storage = AimmsStorageType::Int;
		}
		return *this;
	}

	int ___convertToInt(const std::wstring& txt) {
		size_t pos = 0;
		int intVal = 0;

		try {
			intVal = std::stoi(txt, &pos);
		} 
		catch (const std::exception&) {
			if (txt == L"true") {
				intVal = 1;
				pos	   = txt.size();
			} else if (txt == L"false") {
				intVal = 0;
				pos	   = txt.size();
			}
		}

		if (pos != txt.size()) {
			std::stringstream errorMessage;
			errorMessage << "String value '" << TO_STRING(txt) << "' contains invalid characters for conversion to int";
			throw std::runtime_error(errorMessage.str().c_str());
		}

		return intVal;
	}

	AimmsVariant& setAsInt(const std::wstring& txt) 
	{
		size_t pos = 0;
		val.Int64 = ___convertToInt(txt);

		return *this;
	}

	AimmsVariant& setAsDouble(const double d) {
		if (m_storage == AimmsStorageType::Int) {
			val.Int64 = std::llround(d);
		}
		else {
			val.AimmsVal.Double = d;
			m_storage = AimmsStorageType::Double;
		}
		return *this;
	}

	double ___convertToDouble(const std::wstring& txt) {
		size_t pos = 0;
		double doubleVal = 0;

		try {
			doubleVal = std::stod(txt, &pos);
		}
		catch (const std::exception&) {
			if (txt == L"true") {
				doubleVal = 1;
				pos	= txt.size();
			} else if (txt == L"false") {
				doubleVal = 0;
				pos	= txt.size();
			}
		}

		if (pos != txt.size()) {
			std::stringstream errorMessage;
			errorMessage << "String value '" << TO_STRING(txt) << "' contains invalid characters for conversion to double";
			throw std::runtime_error(errorMessage.str().c_str());
		}

		return doubleVal;
	}

	AimmsVariant& setAsDouble(const std::wstring& txt)
	{
		size_t pos = 0;
		val.AimmsVal.Double = ___convertToDouble(txt);

		return *this;
	}

	const CHARTYPE* asString(NormalizerPtr normalizer = nullptr) {
		if (normalizer) m_normalizedString = normalizer->Normalize(val.AimmsVal.String.buf);
		return (m_storage == AimmsStorageType::String) ? (normalizer ? m_normalizedString.c_str() : val.AimmsVal.String.buf) : nullptr;
	}

	const std::string& asStringA() {
		static std::string emptyString;
		if (m_storage == AimmsStorageType::String) {
			m_string = ___convert(val.AimmsVal.String.buf);
			return m_string;
		}
		return emptyString;
	}

	AimmsVariant& setAsValue(int64_t n) {
		switch (m_storage) {
		case AimmsStorageType::Double:
			val.AimmsVal.Double = n;
			break;
		case AimmsStorageType::Int:
			val.Int64 = n;
			break;
		case AimmsStorageType::Binary:
			val.Int64 = n ? 1 : 0;
			break;
		case AimmsStorageType::String:
			char buf[32];
			snprintf(buf, 32, "%lld", n);
			val.AimmsVal.String.buf = ___stringncpy<char, wchar_t>(m_bufPtr, buf, 32);
			val.AimmsVal.String.Length = (int)wcslen(val.AimmsVal.String.buf);
			break;
		default:
			break;
		}

		return *this;
	}

	AimmsVariant& setAsValue(double d) {
		switch (m_storage) {
		case AimmsStorageType::Int:
			val.Int64 = std::llround(d);
			break;
		case AimmsStorageType::Double:
			val.AimmsVal.Double = d;
			break;
		case AimmsStorageType::Binary:
			val.Int64 = d ? 1 : 0;
			break;
		case AimmsStorageType::String:
			char buf[64];
			snprintf(buf, 64, "%g", d);
			val.AimmsVal.String.buf = ___stringncpy<char, wchar_t>(m_bufPtr, buf, 64);
			val.AimmsVal.String.Length = (int)wcslen(val.AimmsVal.String.buf);
			break;
		default:
			break;
		}

		return *this;
	}

	AimmsVariant& setAsValue(std::string &s) 	{
		std::wstring ws = ___convert(s);
		switch (m_storage) {
		case AimmsStorageType::Int:
			val.Int64 = ___convertToInt(ws);
			break;
		case AimmsStorageType::Double:
			val.AimmsVal.Double = ___convertToDouble(ws);
			break;
		case AimmsStorageType::Binary:
			val.Int64 = s.empty() ? 0 : 1;
			break;
		case AimmsStorageType::String:
			m_string = s;
			val.AimmsVal.String.buf = ___wcsncpy(m_bufPtr, ws.c_str(), m_bufSize);
			val.AimmsVal.String.Length = ws.size();
			break;
		default:	
			break;
		}
		return *this;
	}
	
	int stringSize() const {
		return (m_storage == AimmsStorageType::String) ? val.AimmsVal.String.Length : 0;
	}

	int asInt() const {
		return (m_storage == AimmsStorageType::Double) ? std::lround(val.AimmsVal.Double) : val.Int64;
	}

	int64_t asConvertedInt() {
		return asConvertedValue(AimmsStorageType::Int).Int64;
	}

	double round(double d, int precision) const {
		static double f[] = {
			1.0,
			10.0,
			100.0,
			1000.0,
			10000.0,
			100000.0,
			1000000.0,
			10000000.0,
			100000000.0,
			1000000000.0,
			10000000000.0,
			100000000000.0,
			1000000000000.0,
			10000000000000.0,
			100000000000000.0,
			1000000000000000.0,
			10000000000000000.0};

		return (precision >= 0 && precision <= 16) ? floor(d * f[precision] + 0.5) / f[precision] : d;
	}

	double asDouble(int precision = -1) {
		double d = (m_storage == AimmsStorageType::Int) ? (double)val.Int64 : val.AimmsVal.Double;
		return round(d, precision);
	}

	double asConvertedDouble() {
		return asConvertedValue(AimmsStorageType::Double).AimmsVal.Double;
	}

	bool isEmpty() const {
		switch (m_storage) {
		case AimmsStorageType::Int:
		case AimmsStorageType::Binary:
			return val.Int64== 0;
		case AimmsStorageType::Double:
			return val.AimmsVal.Double == 0;
		case AimmsStorageType::String:
			return _STRLEN(val.AimmsVal.String.buf) == 0;
		case AimmsStorageType::Handle:
			return true;
		}

		return false;
	}

	AimmsValueExt& asValue() {
		return val;
	}

	AimmsValue& asAimmsValue() {
		return val.AimmsVal;
	}

	AimmsValueExt& asConvertedValue(AimmsStorageType storageType) {
		switch (m_storage) {
		case AimmsStorageType::Int:
		case AimmsStorageType::Binary:
			switch (storageType) {
			case AimmsStorageType::Int:
				convertedVal.Int64 = val.Int64;
				break;
			case AimmsStorageType::Binary:
				convertedVal.Int64 = val.Int64 ? 1 : 0;
				break;
			case AimmsStorageType::Double:
				convertedVal.AimmsVal.Double = val.Int64;
				break;
			case AimmsStorageType::String:
				char buf[32];
				snprintf(buf, 32, "%lld", val.Int64);
				convertedVal.AimmsVal.String.buf = ___stringncpy<char, wchar_t>(m_bufPtr, buf, 32);
				convertedVal.AimmsVal.String.Length = (int)wcslen(convertedVal.AimmsVal.String.buf);
				break;
			}
			break;
		case AimmsStorageType::String:
			switch (storageType) {
			case AimmsStorageType::Int:
				convertedVal.Int64 = ___convertToInt(val.AimmsVal.String.buf);
				break;
			case AimmsStorageType::Binary:
				convertedVal.Int64 = val.AimmsVal.String.buf ? 1 : 0;
				break;
			case AimmsStorageType::Double:
				convertedVal.AimmsVal.Double = ___convertToDouble(val.AimmsVal.String.buf);
				break;
			case AimmsStorageType::String:
				convertedVal.AimmsVal.String.buf = val.AimmsVal.String.buf;
				convertedVal.AimmsVal.String.Length = val.AimmsVal.String.Length;
				break;
			}
			break;
		case AimmsStorageType::Double:
			switch (storageType) {
			case AimmsStorageType::Int:
				convertedVal.Int64 = std::llround(val.AimmsVal.Double);
				break;
			case AimmsStorageType::Binary:
				convertedVal.Int64 = val.AimmsVal.Double ? 1 : 0;
				break;
			case AimmsStorageType::Double:
				convertedVal.AimmsVal.Double = val.AimmsVal.Double;
				break;
			case AimmsStorageType::String:
				char buf[64];
				snprintf(buf, 64, "%g", val.AimmsVal.Double);
				convertedVal.AimmsVal.String.buf = ___stringncpy<char, wchar_t>(m_bufPtr, buf, 64);
				convertedVal.AimmsVal.String.Length = (int)wcslen(convertedVal.AimmsVal.String.buf);
				break;
			}
			break;
		}
		return convertedVal;
	}

	AimmsVariant& setAsValue(AimmsValueExt& value) {
		switch (m_storage) {
		case AimmsStorageType::Int:
		case AimmsStorageType::Binary:
			val.Int64 = value.Int64;
			break;
		case AimmsStorageType::Double:
			val.AimmsVal.Double = value.AimmsVal.Double;
			break;
		case AimmsStorageType::String:
			val.AimmsVal.String.Length = std::min(m_bufSize, value.AimmsVal.String.Length);
			_STRNCPY(val.AimmsVal.String.buf, value.AimmsVal.String.buf, m_bufSize);
			break;
		default:
			break;
		}

		return *this;
	}

	int compareTuple(const AimmsVariant& other) {
		for (int i = 0; i < m_dimension; i++) {
			int diff = m_tuple[i] - other.m_tuple[i];
			if (diff == 0) continue;
			return diff;
		}

		return 0;
	}

	int comparePartialTuplesWithLBVector(const AimmsVariant* other, const std::vector<int>& LBVector)
	{
		// If other exists, than it is guaranteed to be equal to LBVector up to LBVector's size.
		// We're interested in the current value if m_tuple is
		// - not greater than LBVector for the size of LBVector
		// - lower than other (if existing) for any of the remaining dimensions.

		size_t LBDim = LBVector.size();

		for (size_t i = 0; i < m_dimension; i++) {
			if (i < LBDim) {
				if (m_tuple[i] - LBVector[i] > 0) return 1;
			}
			else {
				int diff = other ? (m_tuple[i] - other->m_tuple[i]) : -1;
				if (diff) return diff;
			}
		}

		// If there is no other yet, then we're interested in this value,
		// otherwise only if it is smaller as computed above.
		return other ? 0 : -1;
	}

	int compareDoubleOrSpecial(double d1, double d2, double eps) {
		double a1 = fabs(d1);
		// when comparing with a special number we use true equality, for non-special number comparisons we use a relative and absolute tolerance
		bool equal = ((0 < d1 && d1 < 1024 * DBL_MIN) || (0 < d2 && d2 < 1024 * DBL_MIN)) ? (d1 == d2) : (fabs(d1 - d2) <= eps * std::max(a1, 1.0));
		return equal ? 0 : ((d1 < d2) ? -1 : 1);
	}

	int compare(const AimmsVariant& other, double eps = 1.0e-14) {
		switch (m_storage) {
		case AimmsStorageType::Int:
			if (other.m_storage == AimmsStorageType::Double) {
				return compareDoubleOrSpecial(val.Int64, other.val.AimmsVal.Double, eps);
			}
			else {
				return (val.Int64 == other.val.Int64) ? 0 : ((val.Int64 < other.val.Int64) ? -1 : 1);
			}
		case AimmsStorageType::Double:
			if (other.m_storage == AimmsStorageType::Int) {
				return compareDoubleOrSpecial(val.AimmsVal.Double, other.val.Int64, eps);
			}
			else {
				return compareDoubleOrSpecial(val.AimmsVal.Double, other.val.AimmsVal.Double, eps);
			}
		case AimmsStorageType::String:
			return _STRNCMP(val.AimmsVal.String.buf, other.val.AimmsVal.String.buf, m_bufSize);
		default:
			return 0;
		}
	}

	AimmsVariant& setAsVariant(const AimmsVariant& other) {
		memcpy(m_tuple, other.m_tuple, sizeof(m_tuple));

		switch (m_storage) {
		case AimmsStorageType::Int:
		case AimmsStorageType::Binary:
			if (other.m_storage == AimmsStorageType::Double) {
				val.Int64 = (int64_t)other.val.AimmsVal.Double;
			}
			else {
				val.Int64 = other.val.Int64;
			}
			break;
		case AimmsStorageType::Double:
			if (other.m_storage == AimmsStorageType::Int) {
				val.AimmsVal.Double = other.val.Int64;
			}
			else {
				val.AimmsVal.Double = other.val.AimmsVal.Double;
			}
			break;
		case AimmsStorageType::String:
			val.AimmsVal.String.Length = std::min(m_bufSize, other.val.AimmsVal.String.Length);
			_STRNCPY(val.AimmsVal.String.buf, other.val.AimmsVal.String.buf, m_bufSize);
			break;
		default:
			break;
		}

		return *this;
	}
};

template <int size = DefaultStringSize>
OSTREAMTYPE& operator<<(OSTREAMTYPE& os, AimmsVariant& x) {
	switch (x.StorageType()) {
	case AimmsStorageType::Binary:
	case AimmsStorageType::Int:
		os << x.asInt();
		break;
	case AimmsStorageType::Double:
		os << x.asDouble();
		break;
	case AimmsStorageType::String:
		os << _TEXT_("\"") << x.asString() << _TEXT_("\"");
		break;
	}

	return os;
}

#ifdef _MSC_VER
#pragma warning(pop)
#endif
