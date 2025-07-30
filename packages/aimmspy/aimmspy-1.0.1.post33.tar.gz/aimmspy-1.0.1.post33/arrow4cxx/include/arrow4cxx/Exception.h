#pragma once

#pragma once


#ifdef __GNUC__
#define ARROW4CXX_DLLEXPORT     __attribute__ ((visibility("default")))
#define ARROW4CXX_DLLIMPORT     
#define ARROW4CXX_DLLINTERFACE  __attribute__ ((visibility("default")))
#define ARROW4CXX_DLLLOCAL      __attribute__ ((visibility("hidden")))
#endif

#ifdef _MSC_VER
#define ARROW4CXX_DLLEXPORT __declspec(dllexport)
#define ARROW4CXX_DLLIMPORT
#define ARROW4CXX_DLLINTERFACE  
#define ARROW4CXX_DLLLOCAL
#endif


#ifdef ARROW4CXX_EXPORTS
#define ARROW4CXX_API ARROW4CXX_DLLEXPORT
#else
#define ARROW4CXX_API ARROW4CXX_DLLIMPORT
#endif




#include <exception>

#pragma warning( push )
//warning C4275: non dll-interface class 'std::exception' used as base for dll-interface class 'net::Exception' (compiling source file ..\src\RuntimeException.cpp)
#pragma warning( disable: 4275 )

namespace arrow4cxx {

    class ARROW4CXX_API Exception
        : public std::exception 
    {
    public:
        Exception(const char* errMessage, bool logMessage = true);
        Exception(const wchar_t* errMessage, bool logMessage = true);
        virtual ~Exception() throw ();

        virtual const char* what() const throw ();
        virtual const wchar_t* whatW() const throw ();

        Exception(const Exception& otherException);
        Exception& operator =(const Exception& otherException);
    private:
        struct Impl; Impl* pImpl;
    };

} // namespace arrow4cxx

#pragma warning( pop )
