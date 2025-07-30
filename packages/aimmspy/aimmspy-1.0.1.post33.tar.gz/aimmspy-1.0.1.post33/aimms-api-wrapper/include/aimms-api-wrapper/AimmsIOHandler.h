#pragma once
#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable: 4996 26451)
#endif

#include "AimmsHandle.h"
#include "AimmsVariant.h"
#include "AimmsDomain.h"
#include <vector>
#include <memory>
#ifdef USE_ROBIN_MAP
#include <tsl/robin_map.h>
#define aimmsIOMap tsl::robin_map
#else
#include <unordered_map>
#define aimmsIOMap std::unordered_map
#endif
#include <list>
#include <sstream>

#ifdef INCLUDE_LOGGING
#include "log4cxx/logger.h"
extern log4cxx::LoggerPtr g_ioLogger;
#endif

#ifdef INCLUDE_STRING_CONVERT
#define aioConvertString ___convert
#endif

namespace {
	constexpr int DefaultIOSize = 1024;
}

class AimmsLock {
	bool m_locked;
public:
	AimmsLock(int timeout = aimmsifc::WaitInfinite) : m_locked(false) {
		m_locked = (getAimms()->ControlGet(timeout) == aimmsifc::Success);
#ifdef INCLUDE_LOGGING
		if (m_locked) {
			LOG4CXX_DEBUG(g_ioLogger, L"Acquired AIMMS lock");
		}
#endif
	}

	~AimmsLock() {
		if (m_locked) {
			getAimms()->ControlRelease();
#ifdef INCLUDE_LOGGING
			LOG4CXX_DEBUG(g_ioLogger, L"Released AIMMS lock");
#endif
		}
	}

	bool Locked() {
		return m_locked;
	}
};

class AimmsUnlock {
public:
	AimmsUnlock() {
		getAimms()->ControlRelease();
	}

	~AimmsUnlock() {
		getAimms()->ControlGet(aimmsifc::WaitInfinite);
	}
};

template <int size = DefaultIOSize, int strSize = DefaultStringSize> class AimmsIOHandler {
	AimmsHandle m_handle;
	bool m_init;
	AimmsDeclarationDomain m_domain;
	AimmsRangeDomain m_rangeDomain;
	int m_realStrSize = strSize;
	int m_realReadSize = size;
	int m_setReadSize = size;
	int m_realWriteSize = size;

	struct ArrayData {
		int m_elements[size] = {};
		int m_tuples[size * aimmsifc::MaxDimension] = {};
		AimmsValueExt m_values[size] = {};
		CHARTYPE m_buf[size * strSize] = {};

		static ArrayData* GetOrReleaseArrayData(ArrayData* data = 0) {
			static std::list<ArrayData*> s_arrayData;
			ArrayData* ret = 0;

			if (data) {
				s_arrayData.push_back(data);
			}
			else if (!s_arrayData.empty()) {
				ret = s_arrayData.back();
				s_arrayData.pop_back();
			}
			else {
				ret = new ArrayData();
			}

			return ret;
		}

		~ArrayData() {
			if (m_buf) {
				delete[] m_buf;
			}
		}

	private:
		ArrayData() {}
	} *m_data;

	int m_read;
	int m_next;
	int m_elemWritten;
	int m_written;
	int m_totalWritten;
	bool m_isChar;
	STRINGTYPE m_errorMessage;
	int m_lastError;
	AimmsVariant m_value;
	bool m_continuableError;

	aimmsIOMap<std::wstring, int> m_addedElements;
	aimmsIOMap<std::wstring, int> m_addedElementsDisplay;
	aimmsIOMap<int, std::wstring> m_knownElements;
	aimmsIOMap<int, std::wstring> m_knownElementsDisplay;
	aimmsIOMap<int, int> m_addedElementsByOrdinal;
	aimmsIOMap<std::wstring, int> m_elementDisplayNames;
	aimmsIOMap<int, std::wstring> m_displayNames;

#ifdef INCLUDE_STRING_CONVERT
	aimmsIOMap<std::string, int> m_addedElementsA;
	aimmsIOMap<std::string, int> m_addedElementsDisplayA;
	aimmsIOMap<int, std::string> m_knownElementsA;
	aimmsIOMap<int, std::string> m_knownElementsDisplayA;
#endif
	std::wstring m_displayNameIdentifier;
	std::shared_ptr<AimmsHandle> m_displayNameHandle;
	int m_displayNamesVersion = 0;

public:
	AimmsHandle& GetAimmsHandle() {
		return m_handle;
	}

	int GetHandle()
	{
		return m_handle.Handle();
	}

	int GetCalendarHandle() {
		return m_handle.CalendarHandle();
	}

	const std::wstring& Name()
	{
		return m_handle.Name();
	}

	int Type()
	{
		return m_handle.Type();
	}

	AimmsStorageType StorageType() {
		return m_handle.StorageType();
	}

	size_t Dimension() {
		return m_handle.Dimension();
	}

	AimmsIOHandler(const STRINGTYPE& identifier, int strSize_ = strSize, bool init = true, int flags = 0) : m_handle(identifier, nullptr, flags), m_init(init)
		, m_realStrSize(LimitStringSize(strSize_)), m_data(0), m_read(0), m_next(0)
		, m_elemWritten(0), m_written(0), m_totalWritten(0), m_isChar(false), m_lastError(0), m_continuableError(true)
	{
		if (GetHandle()) {
			FillMembers(true);
		}
	}

	AimmsIOHandler(int handle = 0, bool reset = true) : m_handle(handle), m_init(true), m_data(0)
		, m_read(0), m_next(0), m_elemWritten(0), m_written(0), m_totalWritten(0), m_isChar(false), m_lastError(0), m_continuableError(true)
	{
		FillMembers(reset);
	}

	AimmsIOHandler(int handle, int strSize_) : m_handle(handle), m_init(true), m_data(0), m_realStrSize(LimitStringSize(strSize_))
		, m_read(0), m_next(0), m_elemWritten(0), m_written(0), m_totalWritten(0), m_isChar(false), m_lastError(0), m_continuableError(true)
	{
		FillMembers(true);
	}

	void FillMembers(bool reset)
	{
		m_isChar = (StorageType() == AimmsStorageType::String);
		if (m_isChar) {
			m_realWriteSize = (size * strSize) / m_realStrSize;
			m_realReadSize = (size * strSize) / std::max(16 * strSize, m_realStrSize);
			m_setReadSize = m_realReadSize;
			m_value.setStringSize(m_realStrSize);
		}

		if (m_init) {
			m_data = ArrayData::GetOrReleaseArrayData();
		}

		m_value.StorageType() = StorageType();
		m_value.Dimension() = Dimension();
		if (reset && Dimension() > 0) {
			Reset();
		}
	}
	 
	void Attach() {
		if (!m_data) {
			m_data = ArrayData::GetOrReleaseArrayData();
		}
	}

	void Detach() {
		if (m_data) {
			ArrayData::GetOrReleaseArrayData(m_data);
			m_data = 0;
		}
	}

	void SetReadSize(int _size) 
	{
		m_setReadSize = std::min(std::max(_size,1), m_realReadSize);
	}
	
	void DoubleReadSize() {
		m_setReadSize = std::min(m_setReadSize * 2, m_realReadSize);
	}
	
	~AimmsIOHandler() {
		if (m_data) {
			Commit();

			ArrayData::GetOrReleaseArrayData(m_data);
			m_data = 0;
		}
	}

	void Reset() {
		getAimms()->ValueResetHandle(GetHandle());
		m_read = 0;
		m_next = 0;
		ResetErrorState();
	}

	void CachedElementsReset() {
		m_addedElements.clear();
		m_addedElementsDisplay.clear();
		m_knownElements.clear();
		m_knownElementsDisplay.clear();
		m_addedElementsByOrdinal.clear();
#ifdef INCLUDE_STRING_CONVERT
		m_addedElementsA.clear();
		m_addedElementsDisplayA.clear();
		m_knownElementsA.clear();
		m_knownElementsDisplayA.clear();
#endif
	}

	void ResetErrorState() {
		m_lastError = 0;
		m_errorMessage.clear();
	}

	void ReadAimmsError() {
		ResetErrorState();

		CHARTYPE buf[1024];
		getAimms()->APILastError(&m_lastError, buf);

		// No data left, not really an error, so do as little as possible
		if (m_lastError == aimmsifc::Error::NO_NON_DEFAULT_ELEMENT_LEFT || m_lastError == aimmsifc::Error::NO_NEXT_ELEMENT) {
			m_continuableError = true;
			m_errorMessage.clear();
			return;
		}

		if (m_lastError) {
			m_continuableError &= (
				m_lastError == aimmsifc::Error::CHANGE_DEFINED_SUPERSET || m_lastError == aimmsifc::Error::CHANGE_DEFINED_IDENTIFIER
			);

			std::wstringstream errorMessage;
			errorMessage << Name() << L": " << buf << L" (error " << m_lastError << L")";
			m_errorMessage = errorMessage.str();
		}
	}

	bool ContinuableError() const {
		return m_continuableError;
	}

	const STRINGTYPE& ErrorMessage() const {
		return m_errorMessage;
	}

	int LastError() const {
		return m_lastError;
	}

	void ResetValues(int n) {
		if (StorageType() == AimmsStorageType::String) {
			for (int i = 0; i < n; i++) {
				m_data->m_values[i].AimmsVal.String.buf = &m_data->m_buf[i * m_realStrSize];
				m_data->m_values[i].AimmsVal.String.Length = m_realStrSize;
			}
		} 
		else if (StorageType() == AimmsStorageType::Int) {
			memset(m_data->m_values, 0, n * sizeof(AimmsValueExt));
		}
	}

	bool IsSimpleSet() {
		return (Type() == aimmsifc::IdentifierType::SimpleSetRoot|| Type() == aimmsifc::IdentifierType::SimpleSetSubset|| Type() == aimmsifc::IdentifierType::Index) ? true : false;
	}

	bool IsSimpleSubSet() {
		return (Type() == aimmsifc::IdentifierType::SimpleSetSubset) ? true : false;
	}

	bool IsRootSet() {
		return (Type() == aimmsifc::IdentifierType::SimpleSetRoot) ? true : false;
	}

	int Empty() {
		return getAimms()->IdentifierEmpty(GetHandle());
	}

	int Cleanup() {
		return getAimms()->IdentifierCleanup(GetHandle());
	}

	int Update() {
		return getAimms()->IdentifierUpdate(GetHandle());
	}

	int DataVersion() {
		int dataVersion;
		getAimms()->IdentifierDataVersion(GetHandle(), &dataVersion);
		return dataVersion;
	}

	int Card() {
		int card = 0;
		getAimms()->ValueCard(GetHandle(), &card);
		return card;
	}

	void CopyTupleValue(int* toTuple, AimmsValueExt* toValue, int toSize, int* fromTuple, AimmsValueExt* fromValue)
	{
		memcpy(toTuple, fromTuple, Dimension() * sizeof(int));
		if (m_isChar) {
			toValue->AimmsVal.String.Length = std::min(fromValue->AimmsVal.String.Length, toSize);
			_STRNCPY(toValue->AimmsVal.String.buf, fromValue->AimmsVal.String.buf, toSize);
		}
		else {
			memcpy(toValue, fromValue, sizeof(AimmsValueExt));
		}
	}

	AimmsVariant& Value() {
		return m_value;
	}

	void CopyCurrentToVariant(AimmsVariant& variant) {
		CopyTupleValue(variant.tuple(), &variant.asValue(), m_realStrSize, m_value.tuple(), &m_value.asValue());
	}

	void CopyCurrentFromVariant(AimmsVariant& variant) {
		CopyTupleValue(m_value.tuple(), &m_value.asValue(), m_realStrSize, variant.tuple(), &variant.asValue());
	}

	void SetEnd() {
		m_read = -1;
	}
	
	void CopyVariant(AimmsVariant& to, AimmsVariant& from) {
		CopyTupleValue(to.tuple(), &to.asValue(), m_realStrSize, from.tuple(), &from.asValue());
	}

	bool ValueNext(AimmsVariant& value, int* searchTuple = nullptr) {
		int ret;

		if (m_read < 0) return false;

		if (Dimension() == 0) {
			ScalarValue(value);
			m_read = -1;
			return true;
		}

		if (m_next == m_read) {
			m_next = 0;

			if (searchTuple) {
				getAimms()->ValueResetHandle(GetHandle());
				for (int i = 0; i < Dimension(); i++) m_data->m_tuples[i] = searchTuple[i];
				// without checking storage type, call the Numeric variant, because it only needs
				// to do string conversions for ancient AIMMS versions 
				ResetValues(1);
				ret = getAimms()->ValueSearchN(GetHandle(), m_data->m_tuples, (AimmsValue *)m_data->m_values);
				m_read = 1;
			}
			else {
				m_read = m_setReadSize;
				DoubleReadSize();
				// without checking storage type, call the Numeric variant, because it only needs
				// to do string conversions for ancient AIMMS versions 
				ResetValues(m_read);
				ret = getAimms()->ValueNextMultiN(GetHandle(), &m_read, m_data->m_tuples, (AimmsValue *)m_data->m_values);
			}
			if (m_read == 0 || ret == aimmsifc::Failure) {
				ReadAimmsError();
				m_read = -1;
				return false;
			}
		}

		CopyTupleValue(value.tuple(), &value.asValue(), m_realStrSize, &m_data->m_tuples[m_next * Dimension()], &m_data->m_values[m_next]);
		m_next++;

		return true;
	}

	bool ValueNext(int* searchTuple = nullptr) {
		return ValueNext(m_value.reset(), searchTuple);
	}

	AimmsVariant& setAsInt(int n) {
		return m_value.setAsInt(n);
	}

	int asInt() {
		return m_value.asInt();
	}

	int64_t asConvertedInt() {
		return m_value.asConvertedInt();
	}

	AimmsVariant& setAsDouble(double d) {
		return m_value.setAsDouble(d);
	}

	double asDouble(int precision = -1) {
		return m_value.asDouble(precision);
	}

	double asConvertedDouble() {
		return m_value.asConvertedDouble();
	}

	AimmsVariant& setAsString(const STRINGTYPE& s, NormalizerPtr normalizer = nullptr) {
		return m_value.setAsString(s, normalizer);
	}

	AimmsVariant& setAsVariant(const AimmsVariant& other) {
		return m_value.setAsVariant(other);
	}

	const CHARTYPE* asString(NormalizerPtr normalizer = nullptr) {
		return m_value.asString(normalizer);
	}

	AimmsValueExt& asValue() {
		return m_value.asValue();
	}

	AimmsValue& asAimmsValue() {
		return m_value.asAimmsValue();
	}

	int compare(const AimmsVariant& otherValue, double eps = 1.0e-14)
	{
		int compare = m_value.compare(otherValue, eps);
		if (compare) {
			if (Type() != aimmsifc::IdentifierType::ParameterElements) return compare;

			// Check for comparing the empty element against an inactive element value
			int ord = RangeDomain().ElementOrdinal(0, m_value.asInt());
			int otherOrd = RangeDomain().ElementOrdinal(0, otherValue.asInt());

			return ord - otherOrd;
		}

		return 0;
	}

	int compare(const AimmsIOHandler<size, strSize>& other, double eps = 1.0e-14) {
		return compare(other.m_value, eps);
	}

	int compareTuple(const AimmsIOHandler<size, strSize>& other) {
		return m_value.compareTuple(other.m_value);
	}

	int comparePartialTupleWithLBVector(const AimmsIOHandler<size, strSize>* other, const std::vector<int>& LBVector) {
		return m_value.comparePartialTuplesWithLBVector((other ? &other->m_value : 0), LBVector);
	}

	int& operator [](size_t i) {
		return m_value[i];
	}

	int tuple(size_t i) {
		return m_value[i];
	}

	int setTuple(size_t i, int el) {
		return m_value.setTuple(i, el);
	}

	AimmsDeclarationDomain& Domain() {
		if (!m_domain.Dimension()) m_domain.SetHandle(GetHandle());

		return m_domain;
	}

	STRINGTYPE CurrentElementNameAtDim(size_t i, NormalizerPtr normalizer = nullptr) {
		if (!m_domain.Dimension()) m_domain.SetHandle(GetHandle());

		auto elName = m_domain.ElementNameAtDim(i, m_value[i]);
		if (normalizer) elName = normalizer->Normalize(elName);
		return elName;
	}

	int ElementOrdinal(size_t i) {
		if (!m_domain.Dimension()) m_domain.SetHandle(GetHandle());

		return m_domain.ElementOrdinal(i, m_value[i]);
	}

	AimmsRangeDomain& RangeDomain() {
		if (!m_rangeDomain.Dimension()) m_rangeDomain.SetHandle(GetHandle());

		return m_rangeDomain;
	}

	STRINGTYPE ElementValueName(int el) {
		if (!m_rangeDomain.Dimension()) m_rangeDomain.SetHandle(GetHandle());

		return m_rangeDomain.ElementNameAtDim(0, el);
	}

	int* tuple() {
		return m_value.tuple();
	}

	bool ScalarValue(AimmsVariant& value) {
		int ret = 0;
		// withouth checking storage type, call the Numeric variant, because it only needs
		// to do string conversions for ancient AIMMS versions 
		ret = getAimms()->ValueRetrieveN(GetHandle(), 0, value.resetAsValue());
		
		if (ret == aimmsifc::Failure){
			ReadAimmsError();
			return false;
		}

		return true;
	}

	bool ScalarValue() {
		return ScalarValue(m_value.reset());
	}

	bool ValueAssign(int* tuple, AimmsValueExt& val, bool autoCommit = true) {
		if (Dimension() == 0) return ScalarAssign(val);

		int ret = aimmsifc::Success;

		if (m_written == 0) {
			ResetValues(m_realWriteSize);
		}

		if (IsSimpleSet() && val.Int64 == 1) {
			m_data->m_elements[m_elemWritten] = tuple[0];
			m_elemWritten++;
			m_totalWritten++;
		}
		else {
			CopyTupleValue(&m_data->m_tuples[m_written * Dimension()], &m_data->m_values[m_written], m_realStrSize, tuple, &val);
			m_written++;
			m_totalWritten++;
		}

		if (autoCommit && m_totalWritten == m_realWriteSize) {
			if (m_elemWritten) {
#ifdef INCLUDE_LOGGING
				LOG4CXX_TRACE(g_ioLogger, L"Assigning " << m_elemWritten << L" elements to set " << Name());
#endif
				ret = getAimms()->SetAddElementRecursiveMulti(GetHandle(), m_elemWritten, m_data->m_elements);
				m_elemWritten = 0;
			}

			if (ret && m_written) {
#ifdef INCLUDE_LOGGING
				LOG4CXX_TRACE(g_ioLogger, L"Assigning " << m_written << L" tuples to identifier " << Name());
#endif
				// withouth checking storage type, call the Numeric variant, because it only needs
				// to do string conversions for ancient AIMMS versions
				ret &= getAimms()->ValueAssignMultiN(GetHandle(), m_written, m_data->m_tuples, (AimmsValue *)m_data->m_values);
				m_written = 0;
			}
			m_totalWritten = 0;
		}

		if (!ret) ReadAimmsError();
		return (ret == aimmsifc::Success);
	}

	bool NeedsCommit() {
		return (m_totalWritten == m_realWriteSize);
	}

	bool Commit() {
		int ret = aimmsifc::Success;

		if (m_elemWritten) {
#ifdef INCLUDE_LOGGING
			LOG4CXX_TRACE(g_ioLogger, L"Assigning " << m_elemWritten << L" elements to set " << Name());
#endif
			ret = getAimms()->SetAddElementRecursiveMulti(GetHandle(), m_elemWritten, m_data->m_elements);
			m_elemWritten = 0;
		}

		if (ret && m_written) {
#ifdef INCLUDE_LOGGING
			LOG4CXX_TRACE(g_ioLogger, L"Assigning " << m_written << L" tuples to identifier " << Name());
#endif
			if (Dimension() == 0) {
				// withouth checking storage type, call the Numeric variant, because it only needs
				// to do string conversions for ancient AIMMS versions
				ret &= getAimms()->ValueAssignN(GetHandle(), 0, (AimmsValue *)m_data->m_values);
			}
			else {
				// withouth checking storage type, call the Numeric variant, because it only needs
				// to do string conversions for ancient AIMMS versions
				ret &= getAimms()->ValueAssignMultiN(GetHandle(), m_written, m_data->m_tuples, (AimmsValue *)m_data->m_values);
			}

			m_written = 0;
		}

		m_totalWritten = 0;
		if (!ret) ReadAimmsError();
		return (m_lastError == aimmsifc::Error::None);
	}

	bool ValueAssign(AimmsVariant& value, bool autoCommit = true) {
		return (Dimension() == 0) ? ScalarAssign(value) : ValueAssign(value.tuple(), value.asConvertedValue(StorageType()), autoCommit);
	}

	bool ValueAssign(AimmsIOHandler<size, strSize>& other, bool autoCommit = true) {
		return (Dimension() == 0) ? ScalarAssign(other.m_value) : ValueAssign(other.m_value, autoCommit);
	}

	bool ValueAssign(bool autoCommit = true) {
		return (Dimension() == 0) ? ScalarAssign(m_value) : ValueAssign(m_value, autoCommit);
	}

	bool ScalarAssign(AimmsValueExt& val) {
		int ret = 0;
		// withouth checking storage type, call the Numeric variant, because it only needs
		// to do string conversions for ancient AIMMS versions
		ret = getAimms()->ValueAssignN(GetHandle(), 0, &val.AimmsVal);
		if (!ret) ReadAimmsError();

		return (ret == aimmsifc::Success);
	}

	bool ScalarAssign(AimmsVariant& value) {
		return ScalarAssign(value.asConvertedValue(StorageType()));
	}

	bool ScalarAssign(AimmsIOHandler<size, strSize>& other) {
		return ScalarAssign(other.m_value);
	}

	bool ScalarAssign() {
		return ScalarAssign(m_value);
	}

	bool ValueRetrieve() {
		if (getAimms()->ValueRetrieveN(GetHandle(), m_value.tuple(), m_value.resetAsValue()) == aimmsifc::Success) {
			return true;
		}

		ReadAimmsError();
		return false;
	}

	bool SetDisplayNames(std::wstring& identifier) {
		if (!m_displayNameIdentifier.empty() && m_displayNameIdentifier != identifier) {
			return false;
		}

		m_displayNameIdentifier = identifier;
		m_displayNameHandle		= std::make_shared<AimmsHandle>(identifier);

		return true;
	}

	void UpdateDisplayNames() {
		if (!m_displayNameHandle || !m_displayNameHandle->Handle()) return;
		
		int dataVersion = 0;
		getAimms()->IdentifierDataVersion(m_displayNameHandle->Handle(), &dataVersion);
		if (dataVersion == m_displayNamesVersion) return;

		AimmsIOHandler<> displayNames(m_displayNameIdentifier);

		m_elementDisplayNames.clear();
		m_displayNames.clear();
		
		displayNames.Reset();
		while (displayNames.ValueNext()) {
			auto& value	= displayNames.Value();

			m_elementDisplayNames[value.asString()] = value[0];
			m_displayNames[value[0]]				= value.asString();
		}

		m_displayNamesVersion = dataVersion;
	}

#ifdef INCLUDE_STRING_CONVERT
	int AddSetElement(const std::string& elName, bool onlyExisting, bool useDisplayNames) {
		// If already added to map, return value;
		auto& addedElement = useDisplayNames ? m_addedElementsDisplayA[elName] : m_addedElementsA[elName];
		if (addedElement) return addedElement;
		std::wstring elname_ = aioConvertString(elName);

		addedElement = AddSetElement(elname_, onlyExisting, useDisplayNames);
		return addedElement;
	}
#endif

	// trim from left and right (including FEFF BOM chars), truncate to 255 chars (max label size)
	inline std::wstring& trim255(std::wstring& s, const wchar_t* t = L" \t\n\r\f\v\ufeff") {
		s.erase(0, s.find_first_not_of(t));
		s.erase(s.find_last_not_of(t) + 1);

		if (s.size() > 255) {
			s.erase(255);
		}

		std::transform(s.cbegin(), s.cend(), s.begin(), [](wchar_t c) {
			return (c < 32) ? ' ' : c;
		});

		return s;
	}

	int AddSetElement(std::wstring& elName, bool onlyExisting, bool useDisplayNames, bool isConst = false) {
		if (!IsSimpleSet() || elName.empty()) {
			return 0;
		}

		// If already added to map, return value;
		auto& addedElement = useDisplayNames ? m_addedElementsDisplay[elName] : m_addedElements[elName];
		if (addedElement) return addedElement;

		if (!isConst) trim255(elName);

		if (useDisplayNames) {
			auto it = m_elementDisplayNames.find(elName);
			if (it != m_elementDisplayNames.end()) {
				addedElement = it->second;
				return addedElement;
			}
		}

		if (onlyExisting) {
			getAimms()->SetNameToElement(GetHandle(), elName.c_str(), &addedElement);
			return addedElement;
		}
		if (!addedElement) {
			int isCreated = 0;
			if (getAimms()->SetElementNumber(GetHandle(), elName.c_str(), 1, &addedElement, &isCreated) == aimmsifc::Success) {
				m_value[0] = addedElement;
				m_value.setAsInt(1);
				ValueAssign();
			} else {
				ReadAimmsError();
			}
		}
		return addedElement;
	}

	int AddSetElementConst(const std::wstring& elName, bool onlyExisting = false, bool useDisplayNames = false) {
		return AddSetElement(const_cast<std::wstring&>(elName), onlyExisting, useDisplayNames, true);
	}

	int GetSetElementByOrdinal(int ordinal) {
		if (!IsSimpleSet() || ordinal <= 0) {
			return 0;
		}

		int& element = m_addedElementsByOrdinal[ordinal];
		if (!element) {
			if (getAimms()->SetOrdinalToElement(GetHandle(), ordinal, &element) != aimmsifc::Success) {
				element = 0;
			}
			else {
				ReadAimmsError();
			}
		}

		return element;
	}

	std::wstring& GetSetElementName(int elNo, NormalizerPtr normalizer, bool useDisplayNames) {
		bool isDisplayName = false;
		return GetSetElementName(elNo, normalizer, useDisplayNames, isDisplayName);
	}

	std::wstring& GetSetElementName(int elNo, NormalizerPtr normalizer, bool useDisplayNames, bool &isDisplayName) {
		static std::wstring noElement;

		if (!elNo || !IsSimpleSet()) {
			return noElement;
		}

		auto& elName = useDisplayNames ? m_knownElementsDisplay[elNo] : m_knownElements[elNo];

		if (useDisplayNames) {
			auto it = m_displayNames.find(elNo);
			if (it != m_displayNames.end()) {
				elName = it->second;
				isDisplayName = true;
				return elName;
			}
		}

		if (elName.empty()) {
			setTuple(0, elNo);
			elName = CurrentElementNameAtDim(0, normalizer);
			isDisplayName = false;
		}

		return elName;
	}

#ifdef INCLUDE_STRING_CONVERT
	std::string& GetSetElementNameA(int elNo, NormalizerPtr normalizer, bool useDisplayNames) {
		static std::string noElement;

		if (!elNo || !IsSimpleSet()) {
			return noElement;
		}

		auto& elName = useDisplayNames ? m_knownElementsDisplayA[elNo] : m_knownElementsA[elNo];

		if (useDisplayNames) {
			auto it = m_displayNames.find(elNo);
			if (it != m_displayNames.end()) {
				elName = aioConvertString(it->second);
				return elName;
			}
		}

		if (elName.empty()) {
			setTuple(0, elNo);
			elName = aioConvertString(CurrentElementNameAtDim(0, normalizer));
		}

		return elName;
	}
#endif

	int StringSize() {
		return m_realStrSize;
	}

	int CalendarElementToDate(const int el, int& year, int& month, int& day, int& hour, int& minute, int& second)
	{
		if (!GetAimmsHandle().IsCalendar()) return 0;
		return getAimms()->SetElementToDate(GetCalendarHandle(), el, &year, &month, &day, &hour, &minute, &second);
	}

	int DateToCalendarElement(const int& year, const int& month, const int& day, const int& hour, const int& minute, const int& second, int& el)
	{
		if (!GetAimmsHandle().IsCalendar()) return 0;
		return getAimms()->SetDateToElement(GetCalendarHandle(), year, month, day, hour, minute, second, &el);
	}
};

template <int size = DefaultIOSize, int strSize = DefaultStringSize>
OSTREAMTYPE& operator<<(OSTREAMTYPE& os, AimmsIOHandler<size, strSize>& x) {
	os << _TEXT_("[") << x.Name();
	if (x.Dimension()) {
		os << _TEXT_("(");
		for (int i = 0; i < x.Dimension(); i++) {
			if (i) os << _TEXT_(",");
			os << _TEXT_("\'") << x.CurrentElementNameAtDim(i) << _TEXT_("\'");
		}
		os << _TEXT_(")");
	}
	os << _TEXT_(" = ");
	if (x.Type() == aimmsifc::IdentifierType::ParameterElements) {
		os << _TEXT_("\'") << x.ElementValueName(x.Value().asInt()) << _TEXT_("\'");
	}
	else {
		os << x.Value();
	}
	os << _TEXT_("]");

	return os;
}

#ifdef _MSC_VER
#pragma warning(pop)
#endif
