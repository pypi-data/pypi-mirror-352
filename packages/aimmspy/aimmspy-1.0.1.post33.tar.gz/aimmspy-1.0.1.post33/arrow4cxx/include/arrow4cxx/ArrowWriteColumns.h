#pragma once

#include "arrow4cxx/IArrowTable.h"
#include "arrow/api.h"
#include <iostream>
#include <sstream>
#include <cmath>

namespace arrow4cxx {

	const int ARROW4CXX_RESERVE = 1024 * 128;

	static inline int64_t getTimestampFromTM(const std::tm & tm, long long mulfactor)
	{
		std::tm t = tm;
		t.tm_year -= 1900;
		t.tm_mon -= 1;
	
		int64_t tval = arrow4cxx_mktime64(&t);
		return tval * mulfactor;
	}

    struct WritableColumnString : WritableColumn
    {
        std::shared_ptr<arrow::StringBuilder> m_array;

        WritableColumnString(const std::string& colname, int cn=0)
            : WritableColumn(colname,cn, ARROW4CXX_STRING_TYPE, false)
			, m_array(std::make_shared<arrow::StringBuilder>())
        {
            auto status = m_array->Reserve(ARROW4CXX_RESERVE);
        }
		
		int writedefault(int row)
		{
			int nskipped = row - pos - 1;
			if (nskipped) {
				auto st = m_array->AppendNulls(nskipped);
				if (!st.ok()) {
					m_LastErrorMsg = st.message();
					return RetVal::NOT_OKAY;
				}
			}
			pos = row;
			return RetVal::OKAY;
		}

        virtual int append(int row, const std::string & s) override
        {
			if (!writedefault(row)) return RetVal::NOT_OKAY;

            auto st=m_array->Append((const uint8_t*)s.c_str(),(int)s.size());
            if (!st.ok()) {
                m_LastErrorMsg = st.message();
                return RetVal::NOT_OKAY;
            }
            return RetVal::OKAY;
        }

		virtual int finish(int row) override
		{
			return writedefault(row);
		}

    };


    struct WritableColumnDouble : WritableColumn
    {
        std::shared_ptr<arrow::NumericBuilder<arrow::DoubleType>> m_array;

        WritableColumnDouble(const std::string& colname, int cn = 0)
            : WritableColumn(colname, cn, ARROW4CXX_DOUBLE_TYPE, false)
			, m_array(std::make_shared<arrow::NumericBuilder<arrow::DoubleType>>())
        {
            auto status = m_array->Reserve(ARROW4CXX_RESERVE);
        }

		int writedefault(int row)
		{
			int nskipped = row - pos - 1;
			if (nskipped) {
				auto st = m_array->AppendNulls(nskipped);
				if (!st.ok()) {
					m_LastErrorMsg = st.message();
					return RetVal::NOT_OKAY;
				}
			}
			pos = row;
			return RetVal::OKAY;
		}

        virtual int append(int row, double d) override
        {           
			if (!writedefault(row)) return RetVal::NOT_OKAY;

            auto st=m_array->Append(d);
            if (!st.ok()) {
                m_LastErrorMsg = st.message();
                return RetVal::NOT_OKAY;
            }
            return RetVal::OKAY;
        }

		virtual int finish(int row) override
		{
			return writedefault(row);
		}
    };


    struct WritableColumnInt : WritableColumn
    {
        std::shared_ptr<arrow::NumericBuilder<arrow::Int32Type>> m_array;

        WritableColumnInt(const std::string& colname, int cn = 0)
            : WritableColumn(colname, cn, ARROW4CXX_INT_TYPE, false)
			, m_array(std::make_shared<arrow::NumericBuilder<arrow::Int32Type>>())
        {
            auto status = m_array->Reserve(ARROW4CXX_RESERVE);
        }
		
		int writedefault(int row)
		{
			int nskipped = row - pos - 1;
			if (nskipped) {
				auto st = m_array->AppendNulls(nskipped);
				if (!st.ok()) {
					m_LastErrorMsg = st.message();
					return RetVal::NOT_OKAY;
				}
			}
			pos = row;
			return RetVal::OKAY;
		}

        virtual int append(int row, int i) override
        {
			if (!writedefault(row)) return RetVal::NOT_OKAY;

            auto st=m_array->Append(i);
            if (!st.ok()) {
                m_LastErrorMsg = st.message();
                return RetVal::NOT_OKAY;
            }
            return RetVal::OKAY;
        }

		virtual int finish(int row) override
		{
			return writedefault(row);
		}
    };


    struct WritableColumnBool : WritableColumn
    {
        std::shared_ptr<arrow::BooleanBuilder> m_array;

        WritableColumnBool(const std::string& colname, int cn = 0)
            : WritableColumn(colname, cn, ARROW4CXX_BOOL_TYPE, false)
			, m_array(std::make_shared<arrow::BooleanBuilder>())
        {
            auto status = m_array->Reserve(ARROW4CXX_RESERVE);
        }
		
		int writedefault(int row)
		{
			int nskipped = row - pos - 1;
			if (nskipped) {
				auto st = m_array->AppendNulls(nskipped);
				if (!st.ok()) {
					m_LastErrorMsg = st.message();
					return RetVal::NOT_OKAY;
				}
			}
			pos = row;
			return RetVal::OKAY;
		}

        virtual int append(int row, bool b) override
        {
			if (!writedefault(row)) return RetVal::NOT_OKAY;

            auto st=m_array->Append(b);
            if (!st.ok()) {
                m_LastErrorMsg = st.message();
                return RetVal::NOT_OKAY;
            }
            return RetVal::OKAY;
        }

		virtual int finish(int row) override
		{
			return writedefault(row);
		}
    };

	// for calendar
	struct WritableColumnTimestamp : WritableColumn
	{
		const long long mulfactor;
		std::shared_ptr<arrow::TimestampType> tst_tu;// for ctor builder....
		std::shared_ptr<arrow::TimestampBuilder> m_array;

		WritableColumnTimestamp(const std::string& colname, int cn, arrow::TimeUnit::type tu)
			: WritableColumn(colname, cn, ARROW4CXX_CALENDAR_TYPE, false)
			, mulfactor((long long) timestamp_mulfactors[tu])
			, tst_tu(std::make_shared<arrow::TimestampType>(tu))
			, m_array(std::make_shared<arrow::TimestampBuilder>(tst_tu, arrow::default_memory_pool()))
		{
			auto status = m_array->Reserve(ARROW4CXX_RESERVE);
		}
		
		int writedefault(int row)
		{
			int nskipped = row - pos - 1;
			if (nskipped) {
				auto st = m_array->AppendNulls(nskipped);
				if (!st.ok()) {
					m_LastErrorMsg = st.message();
					return RetVal::NOT_OKAY;
				}
			}
			pos = row;
			return RetVal::OKAY;
		}

		virtual int append(int row, const std::tm & c) override
		{
			if (!writedefault(row)) return RetVal::NOT_OKAY;
			
			auto st = m_array->Append(getTimestampFromTM(c,mulfactor));
			if (!st.ok()) {
				m_LastErrorMsg = st.message();
				return RetVal::NOT_OKAY;
			}
			return RetVal::OKAY;
		}
		
		virtual int finish(int row) override
		{
			return writedefault(row);
		}

	};
	
	struct WritableColumnDate64 : WritableColumn
	{
		std::shared_ptr<arrow::Date64Builder> m_array;

		WritableColumnDate64(const std::string& colname, int cn)
			: WritableColumn(colname, cn, ARROW4CXX_CALENDARDATE64_TYPE, false)
			, m_array(std::make_shared<arrow::Date64Builder>())
		{
			auto status = m_array->Reserve(ARROW4CXX_RESERVE);
		}
		
		int writedefault(int row)
		{
			int nskipped = row - pos - 1;
			if (nskipped) {
				auto st = m_array->AppendNulls(nskipped);
				if (!st.ok()) {
					m_LastErrorMsg = st.message();
					return RetVal::NOT_OKAY;
				}
			}
			pos = row;
			return RetVal::OKAY;
		}

		virtual int append(int row, const std::tm & c) override
		{
			if (!writedefault(row)) return RetVal::NOT_OKAY;
			
			auto st = m_array->Append(getTimestampFromTM(c,1000));
			if (!st.ok()) {
				m_LastErrorMsg = st.message();
				return RetVal::NOT_OKAY;
			}
			return RetVal::OKAY;
		}
		
		virtual int append(int row, const double ts) override
		{
			if (!writedefault(row)) return RetVal::NOT_OKAY;
			
			auto st = m_array->Append(std::llround(ts) * 1000);
			if (!st.ok()) {
				m_LastErrorMsg = st.message();
				return RetVal::NOT_OKAY;
			}
			return RetVal::OKAY;
		}

		virtual int finish(int row) override
		{
			return writedefault(row);
		}

	};
	

//------------------- write defaults ----------------------------------------

	struct WritableColumnStringWD : WritableColumn
	{
		std::shared_ptr<arrow::StringBuilder> m_array;
		std::string def;

		WritableColumnStringWD(const std::string& colname, int cn , ArrowValue av)
			: WritableColumn(colname, cn, ARROW4CXX_STRING_TYPE, false)
			, m_array(std::make_shared<arrow::StringBuilder>())
			, def(std::string(av.s,av.size))
		{
			auto status = m_array->Reserve(ARROW4CXX_RESERVE);
		}
		
		int writedefault(int row)
		{
			int nskipped = row - pos - 1;
			for (int i = 0; i < nskipped; i++) {
				auto st = m_array->Append((const uint8_t*)def.c_str(), (int)def.size());
				if (!st.ok()) {
					m_LastErrorMsg = st.message();
					return RetVal::NOT_OKAY;
				}
			}
			pos = row;
			return RetVal::OKAY;
		}

		virtual int append(int row, const std::string & s) override
		{
			if (!writedefault(row)) return RetVal::NOT_OKAY;

			auto st = m_array->Append((const uint8_t*)s.c_str(), (int)s.size());
			if (!st.ok()) {
				m_LastErrorMsg = st.message();
				return RetVal::NOT_OKAY;
			}
			return RetVal::OKAY;
		}

		virtual int finish(int row) override
		{
			return writedefault(row);
		}
	};


	struct WritableColumnDoubleWD : WritableColumn
	{
		std::shared_ptr<arrow::NumericBuilder<arrow::DoubleType>> m_array;
		double def;

		WritableColumnDoubleWD(const std::string& colname, int cn , ArrowValue av)
			: WritableColumn(colname, cn, ARROW4CXX_DOUBLE_TYPE, false)
			, m_array(std::make_shared<arrow::NumericBuilder<arrow::DoubleType>>())
			, def(av.d)
		{
			auto status = m_array->Reserve(ARROW4CXX_RESERVE);
		}
		
		int writedefault(int row)
		{
			int nskipped = row - pos - 1;
			for (int i = 0; i < nskipped;i++) {
				auto st = m_array->Append(def);
				if (!st.ok()) {
					m_LastErrorMsg = st.message();
					return RetVal::NOT_OKAY;
				}
			}
			pos = row;
			return RetVal::OKAY;
		}

		virtual int append(int row, double d) override
		{
			if (!writedefault(row)) return RetVal::NOT_OKAY;

			auto st = m_array->Append(d);
			if (!st.ok()) {
				m_LastErrorMsg = st.message();
				return RetVal::NOT_OKAY;
			}
			return RetVal::OKAY;
		}

		virtual int finish(int row) override
		{
			return writedefault(row);
		}
	};


	struct WritableColumnIntWD : WritableColumn
	{
		std::shared_ptr<arrow::NumericBuilder<arrow::Int32Type>> m_array;
		int def;

		WritableColumnIntWD(const std::string& colname, int cn , ArrowValue av)
			: WritableColumn(colname, cn, ARROW4CXX_INT_TYPE, false)
			, m_array(std::make_shared<arrow::NumericBuilder<arrow::Int32Type>>())
			, def((int)av.i)
		{
			auto status = m_array->Reserve(ARROW4CXX_RESERVE);
		}
		
		int writedefault(int row)
		{
			int nskipped = row - pos - 1;
			for (int i = 0; i < nskipped; i++) {
				auto st = m_array->Append(def);
				if (!st.ok()) {
					m_LastErrorMsg = st.message();
					return RetVal::NOT_OKAY;
				}
			}
			pos = row;
			return RetVal::OKAY;
		}

		virtual int append(int row, int i) override
		{
			if (!writedefault(row)) return RetVal::NOT_OKAY;

			auto st = m_array->Append(i);
			if (!st.ok()) {
				m_LastErrorMsg = st.message();
				return RetVal::NOT_OKAY;
			}
			return RetVal::OKAY;
		}

		virtual int finish(int row) override
		{
			return writedefault(row);
		}
	};

	struct WritableColumnBoolWD : WritableColumn
	{
		std::shared_ptr<arrow::BooleanBuilder> m_array;
		bool def;

		WritableColumnBoolWD(const std::string& colname, int cn , ArrowValue av)
			: WritableColumn(colname, cn, ARROW4CXX_BOOL_TYPE, false)
			, m_array(std::make_shared<arrow::BooleanBuilder>())
			, def((bool)av.i)
		{
			auto status = m_array->Reserve(ARROW4CXX_RESERVE);
		}
		
		int writedefault(int row)
		{
			int nskipped = row - pos - 1;
			for (int i = 0; i < nskipped; i++) {
				auto st = m_array->Append(def);
				if (!st.ok()) {
					m_LastErrorMsg = st.message();
					return RetVal::NOT_OKAY;
				}
			}
			pos = row;
			return RetVal::OKAY;
		}

		virtual int append(int row, bool b) override
		{
			if (!writedefault(row)) return RetVal::NOT_OKAY;

			auto st = m_array->Append(b);
			if (!st.ok()) {
				m_LastErrorMsg = st.message();
				return RetVal::NOT_OKAY;
			}
			return RetVal::OKAY;
		}

		virtual int finish(int row) override
		{
			return writedefault(row);
		}
	};

	// for calendar
	struct WritableColumnTimestampWD : WritableColumn
	{
		const long long mulfactor;
		std::shared_ptr<arrow::TimestampType> tst_dummy;// for ctor builder....
		std::shared_ptr<arrow::TimestampBuilder> m_array;
		int64_t def;

		WritableColumnTimestampWD(const std::string& colname, int cn, arrow::TimeUnit::type tu, ArrowValue av)
			: WritableColumn(colname, cn, ARROW4CXX_CALENDAR_TYPE, false)
			, mulfactor((long long)timestamp_mulfactors[tu])
			, tst_dummy(std::make_shared<arrow::TimestampType>(tu))
			, m_array(std::make_shared<arrow::TimestampBuilder>(tst_dummy, arrow::default_memory_pool()))
			, def(getTimestampFromTM(*(av.c), mulfactor))
		{
			auto status = m_array->Reserve(ARROW4CXX_RESERVE);
			
		}
		
		int writedefault(int row)
		{
			int nskipped = row - pos - 1;
			for (int i = 0; i < nskipped; i++) {
				auto st = m_array->Append(def);
				if (!st.ok()) {
					m_LastErrorMsg = st.message();
					return RetVal::NOT_OKAY;
				}
			}
			pos = row;
			return RetVal::OKAY;
		}

		virtual int append(int row, const std::tm & c) override
		{
			if (!writedefault(row)) return RetVal::NOT_OKAY;
			auto st = m_array->Append(getTimestampFromTM(c,mulfactor));
			if (!st.ok()) {
				m_LastErrorMsg = st.message();
				return RetVal::NOT_OKAY;
			}
			return RetVal::OKAY;
		}
		
		virtual int finish(int row) override
		{
			return writedefault(row);
		}
	};





    /* NOT YET (maybe never) 


    // in case we want to allow other possible columns for writing we could do this
    // nope, we do not need *int64 and uint32, they are pointless.

    template<typename Tcol,typename Traw, typename Tdex> 
    struct WritableColumnNum : WritableColumn
    {
        std::shared_ptr<arrow::NumericBuilder<Tcol>> m_array;
        const Tdex max; 
        const Tdex min;
        WritableColumnNum()
            : m_array(std::make_shared<arrow::NumericBuilder<Tcol>>())
            // hmm, max and min dont work for float....and max not for uint64 :(
            , max((int64_t)std::numeric_limits<Traw>::max() > (int64_t)std::numeric_limits<Tdex>::max()
                ? std::numeric_limits<Tdex>::max() : (Tdex)std::numeric_limits<Traw>::max())
            , min((int64_t)std::numeric_limits<Traw>::min() < (int64_t)std::numeric_limits<Tdex>::min()
                ? std::numeric_limits<Tdex>::min() : (Tdex)std::numeric_limits<Traw>::min())
        {
            m_array->Reserve(1024 * 128);
        }
        virtual int append() override
        {
            pos++;
            auto st = m_array->AppendNull();
            if (!st.ok()) {
                m_LastErrorMsg = st.message();
                return RetVal::NOT_OKAY;
            }
            return RetVal::OKAY;
        }

        virtual int append(Tdex numval) override
        {
            pos++;
            if (numval > max || numval < min) {
                m_array->AppendNull();
                m_LastErrorMsg = "Value " + std::to_string(numval) + " does not fit in this column";
                return RetVal::NOT_OKAY;
            }
            auto st = m_array->Append((Traw) numval);
            if (!st.ok()) {
                m_LastErrorMsg = st.message();
                return RetVal::NOT_OKAY;
            }
            return RetVal::OKAY;
        }
    };

    // now we can do this :), but we need error checks for the casting :(
    using WritableColumnInt8 = WritableColumnNum<arrow::Int32Type, int8_t, int>;
    */


}



