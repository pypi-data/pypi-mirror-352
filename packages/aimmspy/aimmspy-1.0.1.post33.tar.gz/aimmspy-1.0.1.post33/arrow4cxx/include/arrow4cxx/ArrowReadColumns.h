#pragma once

#include "arrow4cxx/IArrowTable.h"
#include "arrow/api.h"

#include <time.h>
#include <ctime>
#include <limits>    
#include <iostream>

namespace arrow4cxx {

	template <typename T> struct BaseChunk {
		std::shared_ptr<arrow::Table> table;
		int colno;
		int chunkno;
		std::shared_ptr<T> m_array;
		int64_t chunksize = 0;
		int64_t offset = 0;

		BaseChunk(std::shared_ptr<arrow::Table> table, int colno) : table(table), colno(colno), chunkno(0)
		{
			auto& columns = table->columns();
			if (colno < columns.size() && columns[colno].get() && columns[colno]->chunks().size() > chunkno) {
				m_array = std::static_pointer_cast<T>(table->column(colno)->chunk(chunkno));
				chunksize = m_array->length();
			}
		}

		bool DetermineValidRow(int64_t& row)
		{
			if (chunksize) {
				row -= offset;
				while (chunksize && row >= chunksize) {
					offset += chunksize;
					row -= chunksize;
					chunksize = 0;
					chunkno++;
					if (table->column(colno)->chunks().size() > chunkno) {
						m_array = std::static_pointer_cast<T>(table->column(colno)->chunk(chunkno));
						chunksize = m_array->length();
					}
				}

				if (row < chunksize && m_array.get() && m_array->IsValid(row)) {
					return true;
				}
			}

			return false;
		}
	};
	
    struct ReadableStringChunk : BaseChunk<arrow::StringArray> {
        ReadableStringChunk(std::shared_ptr<arrow::Table > table, int colno)
			: BaseChunk<arrow::StringArray>(table, colno)
		{}
		
		int Data(int64_t row, const char** s) {
			auto offsetrow = m_array->raw_value_offsets()[row];
			*s = (const char*)m_array->raw_data() + offsetrow;
			return m_array->raw_value_offsets()[row + 1] - offsetrow;
		}
		
		bool IsValid(int64_t& row) {
			return DetermineValidRow(row);
		}
    };


     struct ReadableLargeStringChunk : BaseChunk<arrow::LargeStringArray> {
		ReadableLargeStringChunk(std::shared_ptr<arrow::Table> table, int colno)
			: BaseChunk<arrow::LargeStringArray>(table, colno) {}

		int Data(int64_t row, const char** s) {
			auto offsetrow = m_array->raw_value_offsets()[row];
			*s			   = (const char*)m_array->raw_data() + offsetrow;
			return (int)(m_array->raw_value_offsets()[row + 1] - offsetrow);
		}

		bool IsValid(int64_t& row) {
			return DetermineValidRow(row);
		}
	};

	struct ReadableColumnString : ReadableColumn
    {
        ReadableStringChunk m_chunk;
        ReadableColumnString(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(ReadableStringChunk(table, colno))          
        {}
		
		virtual int getValue(int64_t row, const char ** s) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				size = m_chunk.Data(row,s);
			}
			return size;
		}
    };

	struct ReadableColumnLargeString : ReadableColumn {
		ReadableLargeStringChunk m_chunk;

		ReadableColumnLargeString(std::shared_ptr<arrow::Table> table, int colno)
			: m_chunk(ReadableLargeStringChunk(table, colno)) {}

		virtual int getValue(int64_t row, const char** s) override {
			int size = 0;
			if (m_chunk.IsValid(row)) {
				size = m_chunk.Data(row, s);
			}
			return size;
		}
	};

    struct ReadableBoolChunk : BaseChunk<arrow::BooleanArray> {
        ReadableBoolChunk(std::shared_ptr<arrow::Table > table, int colno)
			: BaseChunk<arrow::BooleanArray>(table, colno)
		{}
		
		bool Value(int64_t row) {
			return m_array->Value(row);
		}
		
		bool IsValid(int64_t& row) {
			return DetermineValidRow(row);
		}
    };

	struct ReadableColumnBool : ReadableColumn
    {
        ReadableBoolChunk m_chunk;
        ReadableColumnBool(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(ReadableBoolChunk(table, colno))          
        {}
		
		virtual int getValue(int64_t row, bool &b) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				b = m_chunk.Value(row);
				size = 1;
			}
			return size;
		}
    };

	// numerical chunk
    template <typename Tcol, typename Traw>
    struct ReadableNumChunk : BaseChunk<Tcol> {
        ReadableNumChunk(std::shared_ptr<arrow::Table> table, int colno)
			: BaseChunk<Tcol>(table,colno)
		{}
					
		int Data(int64_t row, Traw& i) {
			i = static_cast<BaseChunk<Tcol>*>(this)->m_array->raw_values()[row];
			return 1;
		}
	
		bool IsValid(int64_t& row) {
			return static_cast<BaseChunk<Tcol>*>(this)->DetermineValidRow(row);
		}
	};


    struct ReadableColumnInt : ReadableColumn
    {
        using chunktype = ReadableNumChunk<arrow::Int32Array, int64_t>;
        chunktype m_chunk;

        ReadableColumnInt(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(chunktype(table, colno))
        {}
		
		virtual int getValue(int64_t row, int64_t & i) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				size = m_chunk.Data(row, i);
			}
			return size;
		}
    };

     struct ReadableColumnDouble : ReadableColumn
    {
        using chunktype = ReadableNumChunk<arrow::DoubleArray, double>;
        chunktype m_chunk;

        ReadableColumnDouble(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(chunktype(table, colno))
        {}
		
		virtual int getValue(int64_t row, double & d) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				size = m_chunk.Data(row, d);
			}
			return size;
		}
    };

	// Base class for time-related columns
	struct ReadableColumnTM : ReadableColumn
	{
		std::tm m_tm{};    // store time object

		// taken from glibc sources to circumvent gmtime problem on MSVC to deal with dates in the year 9999

		#define	SECS_PER_HOUR	(60 * 60)
		#define	SECS_PER_DAY	(SECS_PER_HOUR * 24)
		/* Compute the `struct tm' representation of T,
		   offset OFFSET seconds east of UTC,
		   and store year, yday, mon, mday, wday, hour, min, sec into *TP.
		   Return nonzero if successful.  */

		const unsigned short int __mon_yday[2][13] =
		{
			/* Normal years.  */
			{ 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365 },
			/* Leap years.  */
			{ 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366 }
		};

		int	___offtime(time_t t, long int offset, struct tm* tp)
		{
			time_t days, rem, y;
			const unsigned short int* ip;
			days = t / SECS_PER_DAY;
			rem = t % SECS_PER_DAY;
			rem += offset;
			while (rem < 0)
			{
				rem += SECS_PER_DAY;
				--days;
			}
			while (rem >= SECS_PER_DAY)
			{
				rem -= SECS_PER_DAY;
				++days;
			}
			tp->tm_hour = (int)rem / SECS_PER_HOUR;
			rem %= SECS_PER_HOUR;
			tp->tm_min = (int)rem / 60;
			tp->tm_sec = (int)rem % 60;
			/* January 1, 1970 was a Thursday.  */
			tp->tm_wday = (4 + days) % 7;
			if (tp->tm_wday < 0)
				tp->tm_wday += 7;
			y = 1970;

			#define DIV(a, b) ((a) / (b) - ((a) % (b) < 0))
			#define LEAPS_THRU_END_OF(y) (DIV (y, 4) - DIV (y, 100) + DIV (y, 400))
			#define __isleap(year)	\
			  ((year) % 4 == 0 && ((year) % 100 != 0 || (year) % 400 == 0))

			while (days < 0 || days >= (__isleap(y) ? 366 : 365))
			{
				/* Guess a corrected year, assuming 365 days per year.  */
				time_t yg = y + days / 365 - (days % 365 < 0);
				/* Adjust DAYS and Y to match the guessed year.  */
				days -= ((yg - y) * 365
					+ LEAPS_THRU_END_OF(yg - 1)
					- LEAPS_THRU_END_OF(y - 1));
				y = yg;
			}
			tp->tm_year = int(y - 1900);
			tp->tm_yday = (int)days;
			ip = __mon_yday[__isleap(y)];
			for (y = 11; days < (long int)ip[y]; --y)
				continue;
			days -= ip[y];
			tp->tm_mon = (int)y;
			tp->tm_mday = (int)(days + 1);
			return 1;
		}

		void getTMfromTimestamp(int64_t tval)
		{
			___offtime(tval, 0, &m_tm);
			m_tm.tm_mon += 1;     // because jan=0 => jan=1; 
			m_tm.tm_year += 1900; // 1970-70
		}
	};

	// use TimestampType
	struct ReadableColumnTimestamp : ReadableColumnTM
	{
		const int64_t mulfactor;
		using chunktype = ReadableNumChunk<arrow::TimestampArray, int64_t>;
		chunktype m_chunk;
		
		ReadableColumnTimestamp(std::shared_ptr<arrow::Table> table, int colno, int mulfactor)
			: m_chunk(chunktype(table, colno))
			, mulfactor((int64_t)mulfactor)
		{}
		
		virtual int getValue(int64_t row, double &ts, std::tm **c) override
		{
			int size = 0;
			*c = &m_tm;
			if (m_chunk.IsValid(row)) {
				int64_t t = 0;
				size = m_chunk.Data(row, t);
				t /= mulfactor; // account for multiplication factor in timestamp
				ts = (double)t;
				getTMfromTimestamp(t); // calc m_tm
			}
			return size;
		}
	};

	// use Date32Type
	struct ReadableColumnDate32	: ReadableColumnTM
	{
		using chunktype = ReadableNumChunk<arrow::Date32Array, uint32_t>;
		chunktype m_chunk;

		ReadableColumnDate32(std::shared_ptr<arrow::Table> table, int colno)
			: m_chunk(chunktype(table, colno))
		{}

		virtual int getValue(int64_t row, double& ts, std::tm** c) override
		{
			int size = 0;
			*c = &m_tm;
			if (m_chunk.IsValid(row)) {
				uint32_t t = 0;
				size = m_chunk.Data(row, t);
				int64_t t64 = (uint64_t)t;
				t64 *= 24 * 60 * 60; // days
				ts = (double)t64;
				getTMfromTimestamp(t64); // calc m_tm
			}
			return size;
		}
	};

	// use Date64Type
	struct ReadableColumnDate64	: ReadableColumnTM
	{
		using chunktype = ReadableNumChunk<arrow::Date64Array, uint64_t>;
		chunktype m_chunk;
		std::tm m_tm;    // store time object

		ReadableColumnDate64(std::shared_ptr<arrow::Table> table, int colno)
			: m_chunk(chunktype(table, colno))
		{}

		virtual int getValue(int64_t row, double& ts, std::tm** c) override
		{
			int size = 0;
			*c = &m_tm;
			if (m_chunk.IsValid(row)) {
				uint64_t t = 0;
				size = m_chunk.Data(row, t);
				t /= 1000; // milliseconds
				ts = (double)t;
				getTMfromTimestamp(t); // calc m_tm
			}
			return size;
		}
	};

    // ------------------------- extra ---------------------------------------
    // 
    // note: we could do a nice template thing, but then we have to manually
    //       add extra versions because of the union in ReadValue and 
    //       for int types that could be larger than maxint. So for now
    //       we use the good old copy/paste :)
    //

    struct ReadableColumnInt8 : ReadableColumn
    {
        using chunktype = ReadableNumChunk<arrow::Int8Array, int8_t>;
        chunktype m_chunk;

        ReadableColumnInt8(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(chunktype(table, colno))
        {}
		
		virtual int getValue(int64_t row, int64_t& i) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				int8_t i_;
				size = m_chunk.Data(row, i_);
				i = i_;
			}
			return size;
		}
    };


    struct ReadableColumnUInt8 : ReadableColumn
    {
        using chunktype = ReadableNumChunk<arrow::UInt8Array, uint8_t>;
        chunktype m_chunk;

        ReadableColumnUInt8(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(chunktype(table, colno))
        {}
		
		virtual int getValue(int64_t row, int64_t& i) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				uint8_t i_;
				size = m_chunk.Data(row, i_);
				i = i_;
			}
			return size;
		}
	};


    struct ReadableColumnInt16 : ReadableColumn
    {
        using chunktype = ReadableNumChunk<arrow::Int16Array, int16_t>;
        chunktype m_chunk;

        ReadableColumnInt16(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(chunktype(table, colno))
        {}
		
		virtual int getValue(int64_t row, int64_t& i) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				int16_t i_;
				size = m_chunk.Data(row, i_);
				i = i_;
			}
			return size;
		}
	};


    struct ReadableColumnUInt16 : ReadableColumn
    {
        using chunktype = ReadableNumChunk<arrow::UInt16Array, uint16_t>;
        chunktype m_chunk;

        ReadableColumnUInt16(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(chunktype(table, colno))
        {}
		
		virtual int getValue(int64_t row, int64_t& i) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				uint16_t i_;
				size = m_chunk.Data(row, i_);
				i = i_;
			}
			return size;
		}
	};

    
    struct ReadableColumnUInt32 : ReadableColumn
    {
        // note: i do not know whether this exist, because in python i 
        // see this as int64, but just in case complete it (without testing)
        // it turns out that this is a parquet version 1 issue, if we tell
        // the writer to use version 2 it will support uint32
        // see https://issues.apache.org/jira/browse/ARROW-9215
        // and https://github.com/pandas-dev/pandas/issues/37327
        // or /parquet/type_fwd.h

        using chunktype = ReadableNumChunk<arrow::UInt32Array, uint32_t>;
        chunktype m_chunk;
        uint32_t maxint; // needs check

        ReadableColumnUInt32(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(chunktype(table, colno))
            , maxint((uint32_t)std::numeric_limits<int>::max())
        {}
		
		virtual int getValue(int64_t row, int64_t& i) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				uint32_t i_;
				size = m_chunk.Data(row, i_);
				i = i_;
			}
			return size;
		}
    };


    struct ReadableColumnInt64 : ReadableColumn
    {
        using chunktype = ReadableNumChunk<arrow::Int64Array, int64_t>;
        chunktype m_chunk;
        int64_t maxint; // needs check
        int64_t minint;

        ReadableColumnInt64(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(chunktype(table, colno))
            , maxint((int64_t)std::numeric_limits<int>::max())
            , minint((int64_t)std::numeric_limits<int>::min())
        {}
		
		virtual int getValue(int64_t row, int64_t& i) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				size = m_chunk.Data(row, i);
			}
			return size;
		}
    };


    struct ReadableColumnUInt64 : ReadableColumn
    {
        using chunktype = ReadableNumChunk<arrow::UInt64Array, uint64_t>;
        chunktype m_chunk;
        uint64_t maxint; // needs check

        ReadableColumnUInt64(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(chunktype(table, colno))
            , maxint((uint64_t)std::numeric_limits<int>::max())
        {}
		
		virtual int getValue(int64_t row, int64_t& i) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				uint64_t i_;
				size = m_chunk.Data(row, i_);
				i = i_;
			}
			return size;
		}
    };


    struct ReadableColumnFloat : ReadableColumn
    {
        using chunktype = ReadableNumChunk<arrow::FloatArray, float>;
        chunktype m_chunk;

        ReadableColumnFloat(std::shared_ptr<arrow::Table> table, int colno)
            : m_chunk(chunktype(table, colno))
        {}
		
		virtual int getValue(int64_t row, double& d) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				float d_;
				size = m_chunk.Data(row, d_);
				d = d_;
			}
			return size;
		}
    };

	struct ReadableDecimal128Chunk : BaseChunk<arrow::Decimal128Array> {
		ReadableDecimal128Chunk(std::shared_ptr<arrow::Table > table, int colno) 
			: BaseChunk<arrow::Decimal128Array>(table, colno)
		{}
		
		bool IsValid(int64_t& row) {
			return DetermineValidRow(row);
		}
	};


	struct ReadableColumnDecimal128 : ReadableColumn
	{
		ReadableDecimal128Chunk m_chunk;
		int m_scale;
		ReadableColumnDecimal128(std::shared_ptr<arrow::Table> table, int colno, int scale)
			: m_chunk(ReadableDecimal128Chunk(table, colno)), m_scale(scale)
		{}

		virtual int getValue(int64_t row, int64_t& i) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				size = 1;
				auto status = reinterpret_cast<const arrow::Decimal128*>(m_chunk.m_array->GetValue(row))->ToInteger<int64_t>(&i);
			}
			return size;
		}

		virtual int getValue(int64_t row, double& d) override
		{
			int size = 0;
			if (m_chunk.IsValid(row)) {
				size = 1;
				d = reinterpret_cast<const arrow::Decimal128*>(m_chunk.m_array->GetValue(row))->ToDouble(m_scale);
			}
			return size;
		}
	};

	// more formats...???
}