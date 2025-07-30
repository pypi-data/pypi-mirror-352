#pragma once


#include <string>
#include <sstream>
#include "ProductVersion/Info.h"

namespace ProductVersion{

    class Description 
    {
    public:
        Description();
        virtual ~Description();

        const char* getDescription(const Info& info);
        void getDescription(const Info& info,std::ostream& oss) const;

    private:
        bool isDebug() const;
        

    private:
        std::string m_strDescription;
    };

};
// end namespace ProductVersion
