#pragma once

#include "aimmsifc/aimmsifc.h"

#include <codecvt>
#include <iostream>

#ifdef NOT_ANYMORE
static inline aimmsifc::iAimmsW* getAimms(bool usedInExternalAimmsDLL = true , const char* dllNameHint = nullptr)
{
	static aimmsifc::iAimmsW* aimms = aimmsifc::getUnicodeInterface(usedInExternalAimmsDLL, dllNameHint);
	return aimms;
}
#else

class AimmsFactory {
private:
inline
    static std::shared_ptr<aimmsifc::iAimmsW> instance;
    inline static auto& getConvertor() {
        #ifdef _WIN32
            static std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>, wchar_t> s_aioConverter;
        #else
            static std::wstring_convert<std::codecvt_utf8<wchar_t>> s_aioConverter;
        #endif
        return s_aioConverter;
    }
public:

    static std::string ___convert(const std::wstring& txt) {
        // A wide string that contains a code point that is not valid in UTF-16 may throw a range_error.
        // Example: unpaired surrogate (which is invalid in UTF-16), L"\xD800", high surrogate without a low surrogate        
        try {
            return getConvertor().to_bytes(txt);
        } catch (const std::range_error& e) {
            std::wcerr << L"Error converting string '" << txt << L"' to UTF-8" << std::endl;
            throw;
        }
    }
    static std::wstring ___convert(const std::string& txt) {
        // An invalid UTF-8 string (incomplete multibyte sequence) may throw a range_error.
        // Example: "\xC3", incomplete UTF-8 sequence (starts a 2-byte character but ends prematurely)
        try {
            return getConvertor().from_bytes(txt);
        } catch (const std::range_error& e) {
            std::cerr << "Error converting string '" << txt << "' to UTF-16" << std::endl;
            throw;
        }
    }
    static std::shared_ptr<aimmsifc::iAimmsW> getAimms() {
        return instance;
    }
    static void setAimms(std::shared_ptr<aimmsifc::iAimmsW>& aimms) {
        instance = aimms;
    }
};

// create some static methods that are being using in the DEX code
static inline aimmsifc::iAimmsW* getAimms(bool usedInExternalAimmsDLL = true , const char* dllNameHint = nullptr)
{
	return AimmsFactory::getAimms().get();
}
static inline std::wstring ___convert(const std::string& txt) {
    return AimmsFactory::___convert(txt);
}
static inline std::string ___convert(const std::wstring& txt) {
    return AimmsFactory::___convert(txt);
}

#endif
