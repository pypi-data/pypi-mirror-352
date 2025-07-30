#include "ProductVersion/Info.h"
#include "ProductVersion/Version.h"

// the Microsoft compiler
#if defined(_MSC_VER) 
	#define _HOST_COMPILER_MICROSOFT
	#define _HOST_COMPILER_DEFINED
	#define _TARGET_PLATFORM_WINDOWS
	#define _TARGET_PLATFORM_DEFINED
	#if defined(_M_X64)
		#define _TARGET_ARCHITECTURE_X64
		#define _TARGET_ARCHITECTURE_DEFINED
	#endif
	#if defined(_M_IX86)
		#define _TARGET_ARCHITECTURE_X86
		#define _TARGET_ARCHITECTURE_DEFINED
	#endif
#endif

// the gnu compiler
#if defined(__GNUC__)
	#define _HOST_COMPILER_GCC
	#define _HOST_COMPILER_DEFINED
	#define _TARGET_PLATFORM_LINUX
	#define _TARGET_PLATFORM_DEFINED
	#if defined(__x86_64__)
		#define _TARGET_ARCHITECTURE_X64
		#define _TARGET_ARCHITECTURE_DEFINED
	#endif
	#if defined(__i386__)
		#define _TARGET_ARCHITECTURE_X86
		#define _TARGET_ARCHITECTURE_DEFINED
	#endif
#endif


#if !defined(_TARGET_PLATFORM_DEFINED)
#error Unable to determine platform.
#endif

#if !defined(_TARGET_ARCHITECTURE_DEFINED)
#error Unable to determine architecture.
#endif 

namespace ProductVersion{


	Info::Info()
	{
	}

	int Info::getMajor() const
	{
		return PRODUCT_VERSION_MAJOR;
	}

	int Info::getMinor() const
	{
		return PRODUCT_VERSION_MINOR;
	}

	int Info::getRelease() const
	{
		return PRODUCT_VERSION_RELEASE;
	}

	int Info::getPatch() const
	{
		return PRODUCT_VERSION_PATCH;
	}

	const char* Info::getHash() const
	{
		return PRODUCT_VERSION_HASH_STRING;
	}

	const char* Info::getBuildDate() const
	{
		return PRODUCT_VERSION_BUILD_DATE_STRING;
	}

	const char* Info::getBuildHost() const
	{
		return PRODUCT_VERSION_BUILD_HOST_STRING;
	}

	const char* Info::getArchitecture() const
	{
#ifdef _TARGET_ARCHITECTURE_X64
        return "x64";
#endif
#ifdef _TARGET_ARCHITECTURE_X86
        return "x86";
#endif
	}

	const char* Info::getBuildConfig() const
	{
#ifdef _DEBUG
		return "debug";
#else
		return "release";
#endif
	}

     Info::Platform Info::getPlatform() const{
#ifdef _TARGET_PLATFORM_WINDOWS
        return Platform_Windows;
#endif
#ifdef _TARGET_PLATFORM_LINUX
        return Platform_Linux;
#endif
    }




	const Info& Info::instance()
	{
		static const Info g_Info;
		return g_Info;
	}
};
// end namespace TCP

