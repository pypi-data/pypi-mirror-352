#include "ProductVersion/Description.h"

namespace ProductVersion {

    Description::Description()
    {
       
    }

    Description::~Description()
    {
    }

    const char* Description::getDescription(const Info& info){
        std::ostringstream ossTmp;
        getDescription(info, ossTmp);

        m_strDescription = ossTmp.str();
        return m_strDescription.c_str();
    }

    void Description::getDescription(const Info& info,std::ostream& oss) const
    {
        oss << " " << info.getMajor();
        oss << "." << info.getMinor();
        oss << "." << info.getRelease();
        oss << "." << info.getPatch();
        if (isDebug()) {
            oss << "-debug";
        }
        switch (info.getPlatform()){
        case Info::Platform_Windows:
            oss << " windows";
            break;
        case Info::Platform_Linux:
            oss << " linux";
            break;
        }                
        oss << " " << info.getArchitecture();
    }

    bool Description::isDebug() const{
#ifdef _DEBUG
        return true;
#else
        return false;
#endif
    }

   
};
// end namespace ARMI


