#pragma once

#include <map>
#include <string>
#include <memory>
#include <ctime>
#include <iostream>
#include <iomanip>

#include "aimms-api-wrapper/AimmsIOHandler.h"
#include "arrow4cxx/ArrowTable.h"
#include "arrow4cxx/ArrowWriteColumns.h"

#ifdef NOT_ANYMORE
std::map<std::wstring, int> aimmsTypes;
std::map<std::wstring, int> arrowTypes;
#endif

namespace Transfer {
    enum Type {
        None = 0,
        String = 1,
        Int = 2,
        Bool = 3,
        Double= 4,
        TM = 5
    };
}

enum ExtendType {
    Extend = 0,
    Filter = 1,
    Error = 2 
};

struct ColumnMapping {
    std::wstring idName;
    int aimmsType = 0;
    std::shared_ptr<AimmsIOHandler<>> id;
    std::shared_ptr<AimmsIOHandler<>> range;
    std::wstring colName;
     int arrowType = 0;
    std::shared_ptr<arrow4cxx::ReadableColumn> colReader;
    std::shared_ptr<arrow4cxx::WritableColumn> colWriter;
    bool dataAvailable = false;
    bool isSet = false;
    bool isCalendar = false;
    Transfer::Type transferType = Transfer::Type::None;
    ExtendType extend = ExtendType::Extend;

    ColumnMapping(){}

    int appendElementToRow(int row, int element) 
    { 
        std::string name;
        std::tm tm = {};
        int el = 0;

        auto set = range.get() ? range.get() : id.get();
        if (isCalendar && transferType == Transfer::Type::TM) {
            set->CalendarElementToDate(element, tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec);
        } else if (isSet && transferType == Transfer::Type::String || transferType == Transfer::Type::Int) {
            name = set->GetSetElementNameA(element, 0, false);
        } else  {
            return 0;
        }
        
        switch (transferType) {
        case Transfer::Type::String:
            return colWriter->append(row, name);
        case Transfer::Type::Int:
            el = std::stoi(name);
            return colWriter->append(row, el);
        case Transfer::Type::TM: 
            return colWriter->append(row, tm);
        default:
            return 0;
        }
    }

    int appendValueToRow(int row) 
    {
        switch (transferType) {
        case Transfer::Type::String:
            if (isSet) {
                return appendElementToRow(row, id->asConvertedInt());
            } else {
                return colWriter->append(row, id->Value().asStringA());
            }
        case Transfer::Type::Int:
            if (isSet) {
                return appendElementToRow(row, id->asConvertedInt());
            } else {
                return colWriter->append(row, (int)id->asConvertedInt());
            }
        case Transfer::Type::Bool:
            return colWriter->append(row, (id->asConvertedInt() ? true : false));
        case Transfer::Type::Double:
            return colWriter->append(row, id->asConvertedDouble());
        case Transfer::Type::TM:
            if (isSet) {
                return appendElementToRow(row, id->asInt());
            } else {
                return colWriter->append(row, id->asConvertedDouble());
            }
        default:
            return 0;
        }
    }

    int getElementFromRow(int row, bool checking)
    {
        int retval = 0;
        const char *elemName = nullptr;
        int64_t elemInt = 0;
        int elem = 0;
        double ts;
        std::tm *tm;

        int addedElement = 0;
        auto set = range.get() ? range.get() : id.get();
        // 'checking' mode implies that the set is not extended
        bool onlyExisting = (!checking && (extend == ExtendType::Extend)) ? false : true;
        switch (transferType) {
            case Transfer::Type::String:
                retval = colReader->getValue(row, &elemName);
                addedElement = retval ? set->AddSetElement(std::string(elemName, retval), onlyExisting, false) : 0;
                if (checking && !addedElement) {
                    throw std::runtime_error("Element '" + std::string(elemName) + "' not found in set with index " + aioConvertString(idName));   
                }   
                return retval ? addedElement : 0;
            case Transfer::Type::Int:
                elemInt = 0;
                retval = colReader->getValue(row, elemInt);
                addedElement = retval ? set->AddSetElement(std::to_string(elemInt).c_str(), onlyExisting, false) : 0;
                if (checking && !addedElement) {
                    throw std::runtime_error("Integer '" + std::to_string(elemInt) + "' not found in set with index " + aioConvertString(idName));   
                }   
                return retval ? addedElement : 0;
            case Transfer::Type::TM:
                retval = colReader->getValue(row, ts, &tm);
                if (retval && set->DateToCalendarElement(tm->tm_year, tm->tm_mon, tm->tm_mday, tm->tm_hour, tm->tm_min, tm->tm_sec, elem)) {
                    if (checking && !elem) {
                        std::stringstream error;
                        error <<  "Date '" << std::put_time(tm, "%Y-%m-%d %H:%M:%S") << "' not found in calendar with index " << aioConvertString(idName);
                        throw std::runtime_error(error.str());   
                    }
                    return elem;
                }
                return 0;
            default:
                return 0;  
        }
            
    }

    int getValueFromRow(int row, AimmsVariant &e, bool checking) 
    {
        switch (transferType) {
        case Transfer::Type::String:
            if (isSet) {
                auto el = getElementFromRow(row, checking);
                e.setAsInt(el);
                return el;
            } else {
                const char *strValue = nullptr;
                auto length = colReader->getValue(row, &strValue);
                std::string s(strValue, length);
                e.setAsValue(s);
                return length;
            }
        case Transfer::Type::Int:
            if (isSet) {
                int el = getElementFromRow(row, checking);
                e.setAsInt(el);
                return el;
            } else {
                int64_t intValue = 0;
                auto retval = colReader->getValue(row, intValue);
                e.setAsValue(intValue);
                return retval;
            }
        case Transfer::Type::Bool:
            {
                bool boolValue = false;
                auto retval = colReader->getValue(row, boolValue);
                int64_t n = boolValue ? 1 : 0;
                e.setAsValue(n);
                return retval;
            }
        case Transfer::Type::Double:
            {
                double doubleValue = 0.0;
                auto retval = colReader->getValue(row, doubleValue);
                e.setAsValue(doubleValue);
                return retval;
            }
        case Transfer::Type::TM:
            if (isSet) {
                auto el = getElementFromRow(row, checking);
                e.setAsInt(el);
                return el;
            } else {
                double ts = 0.0;
                std::tm *tm = nullptr;
                auto retval = colReader->getValue(row, ts, &tm);
                if (retval) {
                    e.setAsValue(ts); 
                }
                return retval;
            }
        default:
            return 0;  
        }
    }
};
