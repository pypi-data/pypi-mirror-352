#pragma once

#include "AimmsFactory.h"

#include <string>
#include <cstring>
#include "AimmsVariant.h"

class AimmsDomain {
private:
	int m_domain[aimmsifc::MaxDimension];
	size_t m_fullDimension;
	size_t m_dimension;
	size_t m_offset;
	AimmsVariant m_name;
public:
	AimmsDomain() : m_fullDimension(0), m_dimension(0), m_offset(0) {
		memset(m_domain, 0, sizeof(m_domain));
	}

	AimmsDomain(int handle) : m_fullDimension(0), m_dimension(0), m_offset(0) {
		memset(m_domain, 0, sizeof(m_domain));
		SetHandle(handle);
	}

	virtual ~AimmsDomain() {
		for (size_t i = 0; i < m_fullDimension; i++) {
			if (m_domain[i]) getAimms()->IdentifierHandleDelete(m_domain[i]);
		}
	}

	virtual void SetHandle(int handle)
	{
		if (handle) {
			int full = 0, dimension = 0;
			getAimms()->AttributeDimension(handle, &full, &dimension);
			m_fullDimension = full;
			m_dimension = dimension;
			m_offset = full - dimension;

			getAimms()->AttributeName(handle, m_name.resetAsString());
		}
	}

	const wchar_t* Name() {
		return m_name.asString();
	}

	int* Domain() {
		return m_domain;
	}

	size_t& FullDimension() {
		return m_fullDimension;
	}

	size_t& Dimension() {
		return m_dimension;
	}

	size_t& Offset() {
		return m_offset;
	}

	int operator [](size_t i) {
		return (i < m_dimension) ? m_domain[m_offset + i] : 0;
	}

	bool IsIndex(size_t i) {
		if (i >= m_dimension) return false;

		int type = 0;
		getAimms()->AttributeType(m_domain[m_offset + i], &type);
		return (type == aimmsifc::IdentifierType::Index);
	}

	STRINGTYPE DomainName(size_t i) {
		AimmsVariant domainName;
		if (i >= m_dimension) return L"";

		getAimms()->AttributeName(m_domain[m_offset + i], domainName.resetAsString());

		return domainName.asString();
	}

	STRINGTYPE ElementNameAtDim(size_t i, int element) {
		CHARTYPE buf[256];
		AimmsVariant name(buf,256);

		if (i < Dimension() && getAimms()->SetElementToName(m_domain[m_offset + i], element, name.resetAsString()) == aimmsifc::Success) {
			return name.asString();
		}

		return _TEXT_("");
	}

	int ElementOrdinal(size_t i, int element) {
		int ordinal = 0;

		if (i < Dimension() && getAimms()->SetElementToOrdinal(m_domain[m_offset + i], element, &ordinal) == aimmsifc::Success) {
			return ordinal;
		}

		return 0;
	}

	int OrdinalElement(size_t i, int ordinal) {
		int element = 0;

		if (i < Dimension() && getAimms()->SetOrdinalToElement(m_domain[m_offset + i], ordinal, &element) == aimmsifc::Success) {
			return element;
		}

		return 0;
	}

	int FirstElement(size_t i) {
		int element = 0;
		AimmsValueExt value;

		getAimms()->ValueResetHandle(m_domain[m_offset + i]);
		getAimms()->ValueNextN(m_domain[m_offset + i], &element, &value.AimmsVal);

		return element;
	}

	int AddElement(size_t i, const STRINGTYPE& name) {
		int elem = 0;
		if (i < Dimension()) getAimms()->SetAddElementRecursive(m_domain[m_offset + i], (CHARTYPE*)name.c_str(), &elem);
		return elem;
	}
};

class AimmsDeclarationDomain : public AimmsDomain {
public:
	AimmsDeclarationDomain() {}

	AimmsDeclarationDomain(int handle) {
		SetHandle(handle);
	}

	~AimmsDeclarationDomain() {}

	void SetHandle(int handle) override
	{
		AimmsDomain::SetHandle(handle);
		getAimms()->AttributeDeclarationDomain(handle, Domain());
		// Set RAW flag to prevent FirstElement to become slow, because of search for non-existing inactive elements during card call in AIMMS API
		for (int i = 0; i < Dimension(); i++) {
			getAimms()->AttributeFlagsSet(Domain()[i], aimmsifc::Flag::Raw);
		}
	}
};

class AimmsRootDomain : public AimmsDomain {
public:
	AimmsRootDomain() {}

	AimmsRootDomain(int handle) {
		SetHandle(handle);
	}

	~AimmsRootDomain() {}

	void SetHandle(int handle) override
	{
		AimmsDomain::SetHandle(handle);
		getAimms()->AttributeRootDomain(handle, Domain());
		// Set RAW flag to prevent FirstElement to become slow, because of search for non-existing inactive elements during card call in AIMMS API
		for (int i = 0; i < Dimension(); i++) {
			getAimms()->AttributeFlagsSet(Domain()[i], aimmsifc::Flag::Raw);
		}
	}
};

class AimmsCallDomain : public AimmsDomain {
public:
	AimmsCallDomain(int handle) {
		SetHandle(handle);
	}

	~AimmsCallDomain() {}

	void SetHandle(int handle) override
	{
		AimmsDomain::SetHandle(handle);
		getAimms()->AttributeCallDomain(handle, Domain());
		// Set RAW flag to prevent FirstElement to become slow, because of search for non-existing inactive elements during card call in AIMMS API
		for (int i = 0; i < Dimension(); i++) {
			getAimms()->AttributeFlagsSet(Domain()[i], aimmsifc::Flag::Raw);
		}
	}
};

class AimmsRangeDomain : public AimmsDomain {
public:
	AimmsRangeDomain() {}

	AimmsRangeDomain(int handle) : AimmsDomain(handle) {
		SetHandle(handle);
	}

	void SetHandle(int handle) override
	{
		getAimms()->AttributeElementRange(handle, Domain());
		if (Domain()[0]) Dimension() = 1;
	}

	~AimmsRangeDomain() {}
};

class AimmsIntegerDomain : public AimmsDomain {
public:
	AimmsIntegerDomain() {}

	AimmsIntegerDomain(int handle) : AimmsDomain(handle) {
		SetHandle(handle);
	}

	void SetHandle(int handle) override {
		AimmsRootDomain root(handle);
		if (Dimension() == 1 && root.DomainName(0) == L"Integers") {
			int domainHandle = 0;
			getAimms()->IdentifierHandleCreate((CHARTYPE*)Name(), nullptr, nullptr, 0, &domainHandle);
			Domain()[0] = domainHandle;
			for (;;) {
				AimmsDeclarationDomain domain(domainHandle);
				if (domain.DomainName(0) != L"Integers") {
					// Move domain one down, delete domain handle above, prevent current domain from deletion
					getAimms()->IdentifierHandleDelete(Domain()[0]);
					Domain()[0] = domainHandle = domain[0];
					domain.Domain()[0] = 0;
				}
				else {
					// Next domain is Integers, which we don't want
					break;
				}
			}
		}
	}
};