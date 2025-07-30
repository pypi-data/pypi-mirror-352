#include "arrow4cxx/ArrowTable.h"
#ifdef NO_STREAM_SUPPORT
#include "arrow4cxx/ArrowReadersWriters.h"
#endif

namespace arrow4cxx {

	ARROW4CXX_API std::shared_ptr<IArrowTable> IArrowTable::create()
    {
        return std::static_pointer_cast<IArrowTable> (std::make_shared<ArrowTable>());
    }


    void ArrowTable::clear()
    {
        m_arrowtable = nullptr;
        m_wcols.clear();
		m_colschema.clear();
    }

    
    std::vector<ColumnInfo> ArrowTable::getColumnInfos()
    {
        std::vector<ColumnInfo> civec;
		for (auto& it : m_colschema) {
			ColumnInfo ci;
			ci.colno = it.colno;
			ci.name = it.name;
			ci.aimmsType = it.aimmsType;
			ci.arrowType = it.arrowType;
			civec.push_back(ci);
		}
		return civec;
    }

    
    int ArrowTable::num_rows()
    {
		int64_t nr = (m_arrowtable) ? m_arrowtable->num_rows() : 0;
		if (nr > (int64_t)std::numeric_limits<int>::max()) {
			return 0; // ignore data when we have more than we can handle....
		}
        return (int) nr;
    }

    
    std::shared_ptr<ReadableColumn> ArrowTable::getReadableColumn(int col)
    {
		// note: this returns nullptr also for unsuported column types
		return (col < (int)m_colschema.size())
			? makeReadableColumns(col)
			: nullptr;
    }


	std::shared_ptr<WritableColumn> ArrowTable::getWritableColumn(const ColumnInfo & ci, ArrowValue av)
	{

		// for getColInfo we may need to add more to the cols ...... use colinfo :)
		auto colno = (int)m_wcols.size();
		std::shared_ptr<WritableColumn> wc = nullptr;

		if (av.size < 0) {// size negative means no writedefault so fill with nulls
			switch (ci.arrowType) {
			case ARROW4CXX_STRING_TYPE:
			case ARROW4CXX_LARGE_STRING_TYPE:
				wc = std::make_shared<WritableColumnString>(ci.name, colno);
				break;
			case ARROW4CXX_INT_TYPE:
			case ARROW4CXX_UINT32_TYPE:
			case ARROW4CXX_INT8_TYPE:
			case ARROW4CXX_UINT8_TYPE:
			case ARROW4CXX_INT16_TYPE:
			case ARROW4CXX_UINT16_TYPE:
			case ARROW4CXX_INT64_TYPE:
			case ARROW4CXX_UINT64_TYPE:
				wc = std::make_shared<WritableColumnInt>(ci.name, colno);
				break;
			case ARROW4CXX_BOOL_TYPE:
				wc = std::make_shared<WritableColumnBool>(ci.name, colno);
				break;
			case ARROW4CXX_DOUBLE_TYPE:
			case ARROW4CXX_FLOAT32_TYPE:
				wc = std::make_shared<WritableColumnDouble>(ci.name, colno);
				break;
			case ARROW4CXX_CALENDAR_TYPE:
				wc = std::make_shared<WritableColumnTimestamp>(ci.name, colno, DEFAULT_TIMESTAMP_UNIT);
				break;
			case ARROW4CXX_CALENDARDATE32_TYPE:
			case ARROW4CXX_CALENDARDATE64_TYPE:
				wc = std::make_shared<WritableColumnDate64>(ci.name, colno);
				break;
			}
		}
		else {
			switch (ci.arrowType) {
			case ARROW4CXX_STRING_TYPE:
			case ARROW4CXX_LARGE_STRING_TYPE:
				wc = std::make_shared<WritableColumnStringWD>(ci.name, colno, av);
				break;
			case ARROW4CXX_INT_TYPE:
			case ARROW4CXX_UINT32_TYPE:
			case ARROW4CXX_INT8_TYPE:
			case ARROW4CXX_UINT8_TYPE:
			case ARROW4CXX_INT16_TYPE:
			case ARROW4CXX_UINT16_TYPE:
			case ARROW4CXX_INT64_TYPE:
			case ARROW4CXX_UINT64_TYPE:
				wc = std::make_shared<WritableColumnIntWD>(ci.name, colno, av);
				break;
			case ARROW4CXX_BOOL_TYPE:
				wc = std::make_shared<WritableColumnBoolWD>(ci.name, colno, av);
				break;
			case ARROW4CXX_DOUBLE_TYPE:
			case ARROW4CXX_FLOAT32_TYPE:
				wc = std::make_shared<WritableColumnDoubleWD>(ci.name, colno, av);
				break;
			case ARROW4CXX_CALENDAR_TYPE:
				wc = std::make_shared<WritableColumnTimestampWD>(ci.name, colno, DEFAULT_TIMESTAMP_UNIT, av);
				break;
			}
		}
		if (wc) {
			m_wcols.emplace_back(wc); // this will become the schema
		}
		return wc;
	}

  
    void ArrowTable::FinishTable(int row) // row is nrows of final table
    {
		// We need to combine all wcols to make sure they are of equal length and
		// that we can attach the schema to it. That's why the actual finish happens
		// in this table and not in the columns themselves.

        std::vector<std::shared_ptr<arrow::Field>> schema_vector;
        std::vector<std::shared_ptr<arrow::Array>> column_vector;
        arrow::Status st;
        std::string emsg;

        for (auto& it : m_wcols) {// schema is derived from wcols

			it->finish(row);// completes the wcol if needed (writedefaults or null)

            std::shared_ptr<arrow::DataType> dt;
            std::shared_ptr<arrow::Array> ar;

            switch (it->type) {
            case ARROW4CXX_INT_TYPE:
                dt = arrow::int32();
                st = std::static_pointer_cast<WritableColumnInt>(it)->m_array->Finish(&ar); // make arrow::Array
                break;
            case ARROW4CXX_BOOL_TYPE:
                dt = arrow::boolean();
                st = std::static_pointer_cast<WritableColumnBool>(it)->m_array->Finish(&ar); // make arrow::Array
                break;
            case ARROW4CXX_DOUBLE_TYPE:
                dt = arrow::float64();
                st = std::static_pointer_cast<WritableColumnDouble>(it)->m_array->Finish(&ar);
                break;
            case ARROW4CXX_STRING_TYPE:
                dt = arrow::utf8();
                st = std::static_pointer_cast<WritableColumnString>(it)->m_array->Finish(&ar);
                break;
			case ARROW4CXX_CALENDAR_TYPE:
				dt = arrow::timestamp(DEFAULT_TIMESTAMP_UNIT);
				st = std::static_pointer_cast<WritableColumnTimestamp>(it)->m_array->Finish(&ar);
				break;
			case ARROW4CXX_CALENDARDATE64_TYPE:
				dt = arrow::date64();
				st = std::static_pointer_cast<WritableColumnDate64>(it)->m_array->Finish(&ar);
				break;
            default: break;
            }

			if (!st.ok()) {
				emsg = "Cannot finish column "+ it->name;
				throw Exception(emsg.c_str());
			}

            schema_vector.push_back(arrow::field(it->name, dt));
            column_vector.push_back(ar);
        }
        
		// make the table
        if (m_arrowtable == nullptr) {
			m_arrowschema = std::make_shared<arrow::Schema>(schema_vector);
            m_arrowtable = arrow::Table::Make(m_arrowschema, column_vector);
        }
    }


    std::shared_ptr<arrow::Table> ArrowTable::getTable()
    {
        return m_arrowtable;
    }


    void ArrowTable::setTable(std::shared_ptr<arrow::Table> table)
    {
        m_arrowtable = table;
    }

	std::shared_ptr<arrow::Schema> ArrowTable::getSchema()
	{
		return m_arrowschema;
	}


	void ArrowTable::setSchema(std::shared_ptr<arrow::Schema> schema)
	{
		m_arrowschema = schema;
		parseSchema();
		
		/*
		if (schema->HasMetadata()) {
			// still todo....
			auto md = schema->metadata();
		}
		*/
	}


    std::shared_ptr<IArrowReader> ArrowTable::getReader(ArrowInOutFormat format, char delimiter)
    {
        std::shared_ptr<IArrowReader> reader = nullptr;
#ifdef NO_STREAM_SUPPORT		
        switch (format) {
        case ArrowInOutFormat::Parquet:
            reader = std::static_pointer_cast<IArrowReader>(std::make_shared<ArrowParquetReader>(this));
            break;
        case ArrowInOutFormat::CSV:
            reader = std::static_pointer_cast<IArrowReader>(std::make_shared<ArrowCSVReader>(this, delimiter));
            break;
        default: break;
        }
#endif

        return reader;
    }


    std::shared_ptr<IArrowWriter> ArrowTable::getWriter(ArrowInOutFormat format, char delimiter)
    {
        std::shared_ptr<IArrowWriter> writer = nullptr;
#ifdef NO_STREAM_SUPPORT		
        switch (format) {
        case ArrowInOutFormat::Parquet:
            writer = std::static_pointer_cast<IArrowWriter>(std::make_shared<ArrowParquetWriter>(this));
            break;
		case ArrowInOutFormat::CSV:
            writer = std::static_pointer_cast<IArrowWriter>(std::make_shared<ArrowCSVWriter>(this, delimiter));
            break;
        default: break;
        }
#endif

        return writer;
    }


	//-------------------------- priv ---------------------------
	
	std::shared_ptr<ReadableColumn> ArrowTable::makeReadableColumns(int col)// arg colno 
	{
		auto acs = m_colschema[col];
		int colno = acs.colno;

		std::shared_ptr<ReadableColumn> r = nullptr;
		switch (acs.arrowType) {
		case ARROW4CXX_INT_TYPE:
			r = std::make_shared<ReadableColumnInt>(getTable(), colno);
			break;
		case ARROW4CXX_DOUBLE_TYPE:
			r = std::make_shared<ReadableColumnDouble>(getTable(), colno);
			break;
		case ARROW4CXX_STRING_TYPE:
			r = std::make_shared<ReadableColumnString>(getTable(), colno);
			break;
		case ARROW4CXX_LARGE_STRING_TYPE:
			r = std::make_shared<ReadableColumnLargeString>(getTable(), colno);
			break;
		case ARROW4CXX_CALENDAR_TYPE:
			r = std::make_shared<ReadableColumnTimestamp>(getTable(), colno, timestamp_mulfactors[acs.timeunit]);
			break;
			// extra int
		case ARROW4CXX_BOOL_TYPE: 
			r = std::make_shared<ReadableColumnBool>(getTable(), colno);
			break;
		case ARROW4CXX_INT8_TYPE:
			r = std::make_shared<ReadableColumnInt8>(getTable(), colno);
			break;
		case ARROW4CXX_INT16_TYPE:
			r = std::make_shared<ReadableColumnInt16>(getTable(), colno);
			break;
		case ARROW4CXX_INT64_TYPE:
			r = std::make_shared<ReadableColumnInt64>(getTable(), colno);
			break;
		case ARROW4CXX_UINT8_TYPE:
			r = std::make_shared<ReadableColumnUInt8>(getTable(), colno);
			break;
		case ARROW4CXX_UINT16_TYPE:
			r = std::make_shared<ReadableColumnUInt16>(getTable(), colno);
			break;
		case ARROW4CXX_UINT32_TYPE:
			r = std::make_shared<ReadableColumnUInt32>(getTable(), colno); // pyarrow saves as int64 (useless)?
			break;
		case ARROW4CXX_UINT64_TYPE:
			r = std::make_shared<ReadableColumnUInt64>(getTable(), colno);
			break;
			// extra float 
		case ARROW4CXX_FLOAT32_TYPE:
			r = std::make_shared<ReadableColumnFloat>(getTable(), colno);
			break;
		case ARROW4CXX_CALENDARDATE32_TYPE:
			r = std::make_shared<ReadableColumnDate32>(getTable(), colno);
			break;
		case ARROW4CXX_CALENDARDATE64_TYPE:
			r = std::make_shared<ReadableColumnDate64>(getTable(), colno);
			break;
		case ARROW4CXX_DECIMAL128_TYPE:
			r = std::make_shared<ReadableColumnDecimal128>(getTable(), colno, acs.scale);
			break;
		case ARROW4CXX_NULL_TYPE:
			r = std::make_shared<ReadableColumn>();
			break;
		default:
			break;
		}
		return r;
	}


	void ArrowTable::parseSchema() // retval for not found????
	{
		// from m_arrowschema to m_colschema 
		m_colschema.clear();
		auto fields = m_arrowschema->fields();
		int colno = 0;
		for (auto& f : fields) {
			ArrowColumnSchema acs;
			acs.colno = colno;
			acs.name = f->name();

			switch (f->type()->id()) {
				case arrow::Type::INT32:
					acs.aimmsType = ARROW4CXX_INT_TYPE;
					acs.arrowType = ARROW4CXX_INT_TYPE;
					break;
				case arrow::Type::DOUBLE:
					acs.aimmsType = ARROW4CXX_DOUBLE_TYPE;
					acs.arrowType = ARROW4CXX_DOUBLE_TYPE;
					break;
				case arrow::Type::STRING:
					acs.aimmsType	= ARROW4CXX_STRING_TYPE;
					acs.arrowType = ARROW4CXX_STRING_TYPE;
					break;
				case arrow::Type::LARGE_STRING:
					acs.aimmsType	= ARROW4CXX_STRING_TYPE;
					acs.arrowType = ARROW4CXX_LARGE_STRING_TYPE;
					break;
				case arrow::Type::TIMESTAMP:
					acs.aimmsType = ARROW4CXX_CALENDAR_TYPE;
					acs.arrowType = ARROW4CXX_CALENDAR_TYPE;
					acs.timeunit = static_cast<arrow::TimestampType*>(f->type().get())->unit();
					break;
				// ----------- reader only types -------------------------
				case arrow::Type::INT8:
					acs.aimmsType = ARROW4CXX_INT_TYPE;
					acs.arrowType = ARROW4CXX_INT8_TYPE;
					break;
				case arrow::Type::INT16:
					acs.aimmsType = ARROW4CXX_INT_TYPE;
					acs.arrowType = ARROW4CXX_INT16_TYPE;
					break;
				case arrow::Type::INT64:
					acs.aimmsType = ARROW4CXX_INT_TYPE;
					acs.arrowType = ARROW4CXX_INT64_TYPE;
					break;
				case arrow::Type::UINT8:
					acs.aimmsType = ARROW4CXX_INT_TYPE;
					acs.arrowType = ARROW4CXX_UINT8_TYPE;
					break;
				case arrow::Type::UINT16:
					acs.aimmsType = ARROW4CXX_INT_TYPE;
					acs.arrowType = ARROW4CXX_UINT16_TYPE;
					break;
				case arrow::Type::UINT32:
					acs.aimmsType = ARROW4CXX_INT_TYPE;
					acs.arrowType = ARROW4CXX_UINT32_TYPE;
					break;
				case arrow::Type::UINT64:
					acs.aimmsType = ARROW4CXX_INT_TYPE;
					acs.arrowType = ARROW4CXX_UINT64_TYPE;
					break;
				case arrow::Type::FLOAT:
					acs.aimmsType = ARROW4CXX_DOUBLE_TYPE;
					acs.arrowType = ARROW4CXX_FLOAT32_TYPE;
					break;
				case arrow::Type::DATE32:
					acs.aimmsType = ARROW4CXX_CALENDAR_TYPE;
					acs.arrowType = ARROW4CXX_CALENDARDATE32_TYPE;
					break;
				case arrow::Type::DATE64:
					acs.aimmsType = ARROW4CXX_CALENDAR_TYPE;
					acs.arrowType = ARROW4CXX_CALENDARDATE64_TYPE;
					break;
				case arrow::Type::DECIMAL128:
					acs.arrowType = ARROW4CXX_DECIMAL128_TYPE;
					acs.scale = static_cast<arrow::Decimal128Type*>(f->type().get())->scale();
					acs.aimmsType = (acs.scale <= 0) ? ARROW4CXX_INT_TYPE : ARROW4CXX_DOUBLE_TYPE;
					break;
				case arrow::Type::NA:
					acs.aimmsType = ARROW4CXX_DOUBLE_TYPE;
					acs.arrowType = ARROW4CXX_NULL_TYPE;
					break;
				case arrow::Type::BOOL:
					acs.aimmsType = ARROW4CXX_BOOL_TYPE;
					acs.arrowType = ARROW4CXX_BOOL_TYPE;
					break;
				default: // not found, unsupported...
					acs.aimmsType = ARROW4CXX_WRONG_TYPE;
					acs.arrowType = f->type()->id();
					break;
			}
			m_colschema.push_back(acs);
			colno++;
		}

	}

	
	void ArrowTable::makeSchema() 
	{
		// use filled wcols to construct the schema
		// note: we could construct a m_colschema first to agree with parseSchema  (not yet)

		std::vector<std::shared_ptr<arrow::Field>> schema_vector;

		for (auto& it : m_wcols) {
			
			std::shared_ptr<arrow::DataType> dt;
			std::shared_ptr<arrow::Array> ar;

			switch (it->type) {
			case ARROW4CXX_INT_TYPE:
				dt = arrow::int32();
				break;
			case ARROW4CXX_DOUBLE_TYPE:
				dt = arrow::float64();
				break;
			case ARROW4CXX_STRING_TYPE:
				dt = arrow::utf8();
				break;
			case ARROW4CXX_CALENDAR_TYPE:
				dt = arrow::timestamp(DEFAULT_TIMESTAMP_UNIT);
			default: break;
			}

			schema_vector.push_back(arrow::field(it->name, dt));	
		}
		m_arrowschema = std::make_shared<arrow::Schema>(schema_vector);	
	}
	
}

