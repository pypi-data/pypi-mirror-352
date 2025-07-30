#pragma once

#include "AimmsFactory.h"

#include <string>
#include <vector>
#include <cstring>
#include "AimmsVariant.h"
#include "AimmsDomain.h"

#ifndef AIMMSAPI_FLAG_SKIP_NONEXISTING_ELEMENTS
#define AIMMSAPI_FLAG_SKIP_NONEXISTING_ELEMENTS 0x00008000
#endif

#ifdef INCLUDE_LOGGING
#include "log4cxx/logger.h"
extern log4cxx::LoggerPtr g_ioLogger;
#endif

class AimmsHandle {
	int m_handle;
	int m_rangeHandle;
	AimmsRootDomain m_calendarDomain;
	int m_createdHandle;
	STRINGTYPE m_name;
	std::vector<int> m_slicing;
	int m_type;
	size_t m_fullDimension;
	size_t m_dimension;
	AimmsStorageType m_storageType;
	int m_isCalendarValued;

	int CreateHandle(int* domain, int* slicing, int flags)
	{
		// Skip inactive data and communicate data in the units of the identifier
		flags |= aimmsifc::Flag::NoInactiveData | aimmsifc::Flag::Units;

		if (aimmsifc::Success != getAimms()->IdentifierHandleCreate((CHARTYPE*)Name().c_str(), domain, slicing, flags, &m_createdHandle)) {
			CHARTYPE buf[1024];
			int lastError = 0;
			buf[0] = 0;
			getAimms()->APILastError(&lastError, buf);
			if (lastError) {
#ifdef INCLUDE_LOGGING
				if (lastError != aimmsifc::Error::NO_NEXT_ELEMENT) {
					LOG4CXX_WARN(g_ioLogger, STRINGTYPE(buf) << L" (errorcode " << lastError << L")");
				}
#endif
				return 0;
			}
		}

		m_handle = m_createdHandle;
		return 1;
	}

	int DetermineAttributes() {
		int full, dimension;

		getAimms()->AttributeType(m_handle, &m_type);
		getAimms()->AttributeDimension(m_handle, &full, &dimension);
		getAimms()->AttributeSlicing(m_handle, &m_slicing[0]);
		m_fullDimension = full;
		m_dimension = dimension;
		m_storageType = DetermineAimmsStorageType(m_handle);
		if (m_storageType == AimmsStorageType::Binary) {
			m_storageType = AimmsStorageType::Int;
		}

		return 1;
	}
public:
	AimmsHandle(STRINGTYPE name, int* slicing = nullptr, int flags = 0)
		: m_handle(0), m_rangeHandle(0), m_createdHandle(0), m_name(name), m_slicing(aimmsifc::MaxDimension), m_type(0), m_fullDimension(0), m_dimension(0), m_storageType(AimmsStorageType::Handle), m_isCalendarValued(-1)
	{
		CreateHandle(nullptr, slicing, flags);
		DetermineAttributes();
	}

	AimmsHandle(int handle, int* slicing = nullptr, int flags = 0)
		: m_handle(handle), m_rangeHandle(0), m_createdHandle(0), m_slicing(aimmsifc::MaxDimension), m_type(0), m_dimension(0), m_storageType(AimmsStorageType::Handle), m_isCalendarValued(-1)
	{
		if (handle) {
			if (slicing) {
				AimmsCallDomain domain(handle);
				CreateHandle(domain.Domain(), slicing, flags);
			}
			else if (flags) {
				AimmsCallDomain domain(handle);
				getAimms()->AttributeSlicing(m_handle, &m_slicing[0]);
				CreateHandle(domain.Domain(), &m_slicing[0], flags);
			}

			DetermineAttributes();
		}
	}

	int Handle() {
		return m_handle;
	}

	int Type() {
		return m_type;
	}

	size_t FullDimension() {
		return m_fullDimension;
	}

	size_t Dimension() {
		return m_dimension;
	}

	AimmsStorageType StorageType() {
		return m_storageType;
	}

	std::vector<int>& Slicing() {
		return m_slicing;
	}

	const STRINGTYPE& Name() {
		if (m_name.empty() && m_handle) {
			AimmsVariant name;

			if (getAimms()->AttributeName(m_handle, name.resetAsString())) {
				m_name = name.asString();
			}
		}

		return m_name;
	}

	std::vector<STRINGTYPE> Domain() {
		AimmsDeclarationDomain domain(m_handle);
		std::vector<STRINGTYPE> domainNames;

		for (size_t i = 0; i < domain.Dimension(); i++) {
			domainNames.push_back(domain.DomainName(i));
		}

		return domainNames;
	}

	std::vector<STRINGTYPE> RootDomain() {
		AimmsRootDomain domain(m_handle);
		std::vector<STRINGTYPE> domainNames;

		for (size_t i = 0; i < domain.Dimension(); i++) {
			domainNames.push_back(domain.DomainName(i));
		}

		return domainNames;
	}

	const STRINGTYPE ElementRange() {
		if (Type() != aimmsifc::IdentifierType::ParameterElements) return L"";

		if (!m_rangeHandle) {
			getAimms()->AttributeElementRange(m_handle, &m_rangeHandle);
		}
		AimmsVariant name;
		getAimms()->AttributeName(m_rangeHandle, name.resetAsString());

		return name.asString();
	}

	bool IsCalendar()
	{
		if (Type() > aimmsifc::IdentifierType::SimpleSetSubset && Type() != aimmsifc::IdentifierType::Index) return false;

		if (m_isCalendarValued < 0) {
			if (Type() == aimmsifc::IdentifierType::Index || Type() == aimmsifc::IdentifierType::SimpleSetSubset) {
				AimmsRootDomain dom(m_handle);
				m_isCalendarValued = getAimms()->SetIsCalendar(dom[0]);
				if (m_isCalendarValued) {
					m_calendarDomain.SetHandle(m_handle);
				}
			}
			else {
				m_isCalendarValued = getAimms()->SetIsCalendar(m_handle);
			}
		}

		return m_isCalendarValued ? true : false;
	}

	bool IsCalendarValued()
	{
		if (Type() != aimmsifc::IdentifierType::ParameterElements) return false;

		if (m_isCalendarValued < 0) {
			if (!m_rangeHandle) {
				getAimms()->AttributeElementRange(m_handle, &m_rangeHandle);
			}

			AimmsHandle range(m_rangeHandle);
			if (range.Type() == aimmsifc::IdentifierType::SimpleSetSubset) {
				AimmsRootDomain dom(m_rangeHandle);
				m_isCalendarValued = getAimms()->SetIsCalendar(dom[0]);
				if (m_isCalendarValued) {
					m_calendarDomain.SetHandle(m_rangeHandle);
				}
			}
			else {
				m_isCalendarValued = getAimms()->SetIsCalendar(m_rangeHandle);
			}
		}

		return m_isCalendarValued ? true : false;
	}

	int CalendarHandle() {
		return m_calendarDomain[0] ? m_calendarDomain[0] : m_handle;
	}

	int Card() {
		int card = 0;
		getAimms()->ValueCard(m_handle, &card);
		return card;
	}

	int Update() {
		return getAimms()->IdentifierUpdate(m_handle);
	}

	int Empty() {
		return getAimms()->IdentifierEmpty(m_handle);
	}

	AimmsVariant Default() {
		AimmsVariant def(m_storageType);

		switch (m_storageType) {
		case AimmsStorageType::String:
			getAimms()->AttributeDefaultS(m_handle, &def.asAimmsValue());
			break;
		default:
			getAimms()->AttributeDefaultN(m_handle, &def.asAimmsValue());
			break;
		}

		return def;
	}

	~AimmsHandle() {
		if (m_createdHandle) {
			getAimms()->IdentifierHandleDelete(m_createdHandle);
			m_createdHandle = 0;
		}
		if (m_rangeHandle) {
			getAimms()->IdentifierHandleDelete(m_rangeHandle);
			m_rangeHandle = 0;
		}
	}
};
