#pragma once
#include "arrow4cxx/IArrowTable.h"
#include "ArrowReadColumns.h"
#include "ArrowWriteColumns.h"

namespace arrow4cxx {

	// schema info can be extended..... Columninfo is derived from this....
	struct ArrowColumnSchema {
		int colno;
		int aimmsType;           // "aimms" type int, double, string
		int arrowType;        // arrow type of data in memory 
		int scale;          // scale for decimal types
		arrow::TimeUnit::type timeunit; // timeunit for timestamp types
		std::string name;

		// rowgroups, stats etc....
		// int index (schema meta) not yet
	};


    class  ArrowTable
        : public IArrowTable
    {
    public:
        ArrowTable() {}
        virtual ~ArrowTable() override{ clear(); }
        virtual void clear() override;

        // info
        virtual std::vector<ColumnInfo> getColumnInfos() override;
        virtual int num_rows() override;

        // reading  
        virtual std::shared_ptr<ReadableColumn> getReadableColumn(int col) override;

        // writing
        virtual std::shared_ptr<WritableColumn> getWritableColumn(const ColumnInfo & ci, ArrowValue rv= ArrowValue()) override;
        virtual void FinishTable(int row) override; // can throw

        // io
        std::shared_ptr<arrow::Table> getTable();
        void setTable(std::shared_ptr<arrow::Table> table);
		std::shared_ptr<arrow::Schema> getSchema();
		void setSchema(std::shared_ptr<arrow::Schema> schema);
        virtual std::shared_ptr<IArrowReader> getReader(ArrowInOutFormat format, char delimiter = ',') override;
        virtual std::shared_ptr<IArrowWriter> getWriter(ArrowInOutFormat format, char delimiter = ',') override;

    private:
		std::shared_ptr<ReadableColumn> makeReadableColumns(int col);
		void parseSchema();
		void makeSchema();

        std::shared_ptr<arrow::Table> m_arrowtable = nullptr;
		std::shared_ptr<arrow::Schema> m_arrowschema = nullptr;
        std::vector<std::shared_ptr<WritableColumn>> m_wcols;

		std::vector<ArrowColumnSchema> m_colschema;
    };

}
