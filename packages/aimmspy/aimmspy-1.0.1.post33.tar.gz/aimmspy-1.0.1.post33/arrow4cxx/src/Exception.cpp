#include "arrow4cxx/Exception.h"

#include <locale>
#include <codecvt>
#include <string>

// note: cuurently no logging (maybe later)

//#include <log4cxx/logger.h>

namespace arrow4cxx {
    //namespace {
    //    static log4cxx::LoggerPtr g_Logger = log4cxx::Logger::getLogger("autolib.Exception");

    //}

    struct Exception::Impl {

        mutable std::string m_MessageA;
        mutable std::wstring m_MessageW;

        Impl(const char* errMessage, bool logMessage)
            : m_MessageA(errMessage)
        {
            if (logMessage) {
              //  LOG4CXX_WARN(g_Logger, szErrorMessage); // not yet
            }
        }

        Impl(const wchar_t* errMessage, bool logMessage)
            : m_MessageW(errMessage)
        {
            if (logMessage) {
              //  LOG4CXX_WARN(g_Logger, szErrorMessage); // not yet
            }
        }

        const char* what() const throw()
        {
            if (m_MessageA.empty()) {
                m_MessageA = (std::wstring_convert<std::codecvt_utf8<wchar_t>>()).to_bytes(m_MessageW);
            }
            return m_MessageA.c_str();
        }

        const wchar_t* whatW() const throw()
        {
            if (m_MessageW.empty()) {
                m_MessageW = (std::wstring_convert<std::codecvt_utf8<wchar_t>>()).from_bytes(m_MessageA);
            }
            return m_MessageW.c_str();
        }
    };


    Exception::Exception(const char* errMessage, bool logMessage)
        : pImpl(new Impl(errMessage, logMessage))
    {
    }


    Exception::Exception(const wchar_t* errMessage, bool logMessage)
        : pImpl(new Impl(errMessage, logMessage))
    {
    }


    Exception::~Exception() throw () {
        delete pImpl;
    }


    const char*  Exception::what() const throw()
    {
        return pImpl->what();
    }


    const wchar_t* Exception::whatW() const throw()
    {
        return pImpl->whatW();
    }


    Exception::Exception(const Exception& otherException) 
        : pImpl(new Impl(*otherException.pImpl))
    {
    }


    Exception& Exception::operator =(const Exception& otherException)
    {
        *pImpl = *otherException.pImpl;
        return *this;
    }

};


