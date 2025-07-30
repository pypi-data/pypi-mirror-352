#pragma once

#include <string>

#include <cstdint>
#include <ctime>


//#ifdef _HOST_COMPILER_MICROSOFT
    // // prevent link errors when arrow_static functions aren't being exported
    // #ifndef ARROW_STATIC
    //     #define ARROW_STATIC 
    // #endif
    // #ifndef PARQUET_STATIC
    //     #define PARQUET_STATIC
    // #endif 
//#endif


// below is needed to convert arrow timestamps
// we need to convert between a 64 bit time_t and struct tm
// windows use a function with a non-standard prototype
// linux depends on glibc for 64 support
#include <time.h>
static inline int64_t arrow4cxx_mktime64(struct tm* tm)
{
#ifdef _WIN32
	return (int64_t) _mkgmtime64(tm);
#else
	return (int64_t)timegm(tm);
#endif
}

#include "Exception.h"

# include<vector>
#include <memory>

namespace arrow4cxx {

    /*
    enum AimmsStorageType {
        Handle = 0,
        Double = 1,
        Int = 2,
        Binary = 3,
        String = 4
    };
    */
    // for inits
	const int ARROW4CXX_WRONG_TYPE = -1; // like type not supported
    const int ARROW4CXX_NONE_TYPE = 0;   // means don't know yet

    //  match type numbers in Dex (see AimmsStorageType above)
    const int ARROW4CXX_DOUBLE_TYPE = 1;
    const int ARROW4CXX_INT_TYPE = 2;
	const int ARROW4CXX_BOOL_TYPE = 3;
    const int ARROW4CXX_STRING_TYPE = 4;
	const int ARROW4CXX_CALENDAR_TYPE = 5; // nano is default in pandas datatime64 (micro in numpy :( )
	// binary not supported

	const int ARROW4CXX_LARGE_STRING_TYPE = 6;

    // other int types for reading
    const int ARROW4CXX_INT8_TYPE = 101;
    const int ARROW4CXX_INT16_TYPE = 102;
    const int ARROW4CXX_INT64_TYPE = 103;
    const int ARROW4CXX_UINT8_TYPE = 104;
    const int ARROW4CXX_UINT16_TYPE = 105;
    const int ARROW4CXX_UINT32_TYPE = 106;
    const int ARROW4CXX_UINT64_TYPE = 107;

	// other float types
    const int ARROW4CXX_FLOAT32_TYPE = 110;

	// other date and types from datatime64/timestamp
	const int ARROW4CXX_CALENDARDATE32_TYPE = 124;
	const int ARROW4CXX_CALENDARDATE64_TYPE = 125;
	
	// for timestamp second, milli, micro, nano
	const int timestamp_mulfactors[] = { 1, 1000, 1000000, 1000000000 };
#define DEFAULT_TIMESTAMP_UNIT arrow::TimeUnit::type::MILLI

	const int ARROW4CXX_DECIMAL_TYPE = 130;
	const int ARROW4CXX_DECIMAL128_TYPE = 131;
	
	const int ARROW4CXX_NULL_TYPE = 140;
	
    // for readability (agree with Aimms convention)
    namespace RetVal {
        const int OKAY = 1;
        const int NOT_OKAY = 0;
    }


    // output file type (check IArrowReaderWriter.h)
    enum class ArrowInOutFormat {
        Parquet,
        CSV,// not yet
        None
    };


    // for writing, use addWritableColumn
    struct WritableColumn {
		const bool writedefaults;
        int pos = -1;
        int type = ARROW4CXX_NONE_TYPE;
        int colno;
        std::string name;
        std::string m_LastErrorMsg;

		WritableColumn(const std::string & name,int colno,int type, bool writedefs)
			: name(name), colno(colno),type(type), writedefaults(writedefs)
		{}
        virtual ~WritableColumn() {}
		virtual int finish(int row) = 0;
        virtual int append(int row,int i) {
            m_LastErrorMsg = "Column is not an integer column";
            return RetVal::NOT_OKAY;
        }
        virtual int append(int row,bool b) {
            m_LastErrorMsg = "Column is not an bool column";
            return RetVal::NOT_OKAY;
        }
        virtual int append(int row, double d) {
            m_LastErrorMsg = "Column is not an double column";
            return RetVal::NOT_OKAY;
        }
        virtual int append(int row, const std::string & s) {
            m_LastErrorMsg = "Column is not an string column";
            return RetVal::NOT_OKAY;
        };
		virtual int append(int row, const std::tm & c) {
			m_LastErrorMsg = "Column is not an timestamp column";
			return RetVal::NOT_OKAY;
		}
        virtual std::string getLastError() {
            return m_LastErrorMsg;
        }
		

        virtual int num_rows() {
            return pos;
        }
    };

    // for reading, use getReadableColumn Do we still need this???
    struct ArrowValue {
		ArrowValue()
			: size(0),i(0), type(ARROW4CXX_NONE_TYPE)
		{}
		ArrowValue(double d, int size = 0)
			: size(size),  d(d), type(ARROW4CXX_DOUBLE_TYPE)
		{}
		ArrowValue(int64_t i, int size = 0)
			: size(size), i(i), type(ARROW4CXX_INT_TYPE)
		{}
		ArrowValue(const char * s, int size = 0)
			: size(size), s(s), type(ARROW4CXX_STRING_TYPE)
		{}
		ArrowValue(const char* s, size_t size = 0)
			: size(size), s(s), type(ARROW4CXX_LARGE_STRING_TYPE) 
		{}
		ArrowValue(std::tm* c, int size = 0)
			: size(size), c(c), type(ARROW4CXX_CALENDAR_TYPE)
		{}
        int64_t size = 0; // assume empty
		int type;
        union {
            const char * s;
            double d;
            int64_t i;
			std::tm* c;
        };
    };






    struct ReadableColumn {
		std::string m_LastErrorMsg;
        virtual ~ReadableColumn() {}
		virtual int getValue(int64_t row, int64_t& i) {
			m_LastErrorMsg = "Column is not an integer column";
			return RetVal::NOT_OKAY;
		}
		virtual int getValue(int64_t row, bool& b) {
			m_LastErrorMsg = "Column is not a bool column";
			return RetVal::NOT_OKAY;
		}
		virtual int getValue(int64_t row, double& d) {
			m_LastErrorMsg = "Column is not an double column";
			return RetVal::NOT_OKAY;
		}
		virtual int getValue(int64_t row, const char ** s) {
			m_LastErrorMsg = "Column is not an string column";
			return RetVal::NOT_OKAY;
		};
		virtual int getValue(int64_t row, double & ts, std::tm ** c) {
			m_LastErrorMsg = "Column is not an timestamp column";
			return RetVal::NOT_OKAY;
		}
		virtual std::string getLastError() {
			return m_LastErrorMsg;
		}
    };

  
    // for "schema" in Dex
    struct ColumnInfo {
        int colno;
        int aimmsType;           // "aimms" type int, double, string
        int arrowType;        // arrow type of data in memory 
        std::string name;
        // int index (schema meta) not yet
    };


    // forwards
    class IArrowReader;
    class IArrowWriter;
    

    class IArrowTable 
    {
    public:
        virtual ~IArrowTable() {};

        static ARROW4CXX_API std::shared_ptr<IArrowTable> create();

        virtual std::vector<ColumnInfo> getColumnInfos() = 0;
        virtual int num_rows() = 0;
        virtual void clear() = 0;

        // reading  
        virtual std::shared_ptr<ReadableColumn> getReadableColumn(int col) = 0;

        // writing
        virtual std::shared_ptr<WritableColumn> getWritableColumn(const ColumnInfo & ci, ArrowValue rv= ArrowValue()) = 0;
        virtual void FinishTable(int row=0) = 0; // can throw

        // reader/writer
        virtual std::shared_ptr<IArrowReader> getReader(ArrowInOutFormat format, char delimiter = ',') = 0;
        virtual std::shared_ptr<IArrowWriter> getWriter(ArrowInOutFormat format, char delimiter = ',') = 0;
    };

}


