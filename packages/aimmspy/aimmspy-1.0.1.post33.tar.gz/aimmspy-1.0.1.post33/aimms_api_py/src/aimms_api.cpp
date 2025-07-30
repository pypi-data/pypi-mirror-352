#include <algorithm>
#include <pybind11/pytypes.h>
#include <string>

#include "aimms_api_py/aimms_api.hpp"

#include "aimms_api_py/ColumnMapping.hpp"

AimmsAPI::AimmsAPI(const std::string& aimms_bin_path, const std::wstring& project_command, pybind11::object aimms_project_self, bool with_idex_restriction)
	: m_with_index_restriction(with_idex_restriction) {

	init_aimms(aimms_bin_path);

	if (!aimms_bin_path.empty()) {
		open_project(project_command);
	} else {
		aimms_in_the_lead = true;
	}
	current_project = std::move(aimms_project_self);
	current_project.dec_ref();
}

AimmsAPI::~AimmsAPI() {

	try {
		for (auto& [name, info] : all_model_identifiers_map) {
			try {
				if (info.data_handle != -1) {
					delete_handle(info.data_handle);
				}
			} catch (const aimms_exception& e) {
				std::cerr << "Error deleting handle: " << e.what() << '\n';
			}

			try {
				if (info.procedure_handle != -1) {
					delete_handle_procedure(info.procedure_handle);
				}
			} catch (const aimms_exception& e) {
				std::cerr << "Error deleting procedure handle: " << e.what() << '\n';
			}
		}

		if (!aimms_in_the_lead) {
			try {
				close_project();
				aimms.reset();
			} catch (const aimms_exception& e) {
				std::cerr << "Error closing project: " << e.what() << '\n';
			}
		}
	} catch (...) {
		std::cerr << "Error deleting handles\n";
	}

	if (data_handles_count != 0) {
		std::cerr << "Warning: " << data_handles_count << " data handles were not deleted\n";
	}

	if (procedure_handles_count != 0) {
		std::cerr << "Warning: " << procedure_handles_count << " procedure handles were not deleted\n";
	}

	current_project = pybind11::none();
}

void AimmsAPI::add_attribute(int meh, const std::wstring& name, int idtype) {
	const auto ret = aimms->MeSetAttribute(meh, idtype, name.c_str());
	handle_error(ret);
}

std::wstring AimmsAPI::get_attribute(int meh, int attr_id) {
	aimmsifc::AimmsStringType<wchar_t> attribute_string;
	std::wstring attribute_string_buf(512, L'\0');
	attribute_string.buf	= attribute_string_buf.data();
	attribute_string.Length = static_cast<int>(attribute_string_buf.size());

	const auto ret = aimms->MeGetAttribute(meh, attr_id, &attribute_string);
	handle_error(ret);

	// if the attribute string length is larger than the buffer size, resize the buffer and try again
	if (attribute_string.Length > attribute_string_buf.size()) {
		attribute_string_buf.resize(attribute_string.Length);
		attribute_string.buf	= attribute_string_buf.data();
		attribute_string.Length = static_cast<int>(attribute_string_buf.size());
		const auto ret			= aimms->MeGetAttribute(meh, attr_id, &attribute_string);
		handle_error(ret);
	}

	return attribute_string_buf.substr(0, attribute_string.Length - 1);
}

int AimmsAPI::get_model_node_root(int pos) {
	int meh{};
	const auto ret = aimms->MeOpenRoot(pos, &meh);
	handle_error(ret);
	return meh;
}

int AimmsAPI::get_model_root_count() {
	int count{};
	const auto ret = aimms->MeRootCount(&count);
	handle_error(ret);
	return count;
}

int AimmsAPI::get_model_node_child(int pmeh) {
	int meh{};
	const auto ret = aimms->MeFirst(pmeh, &meh);
	handle_error(ret);
	return meh;
}

int AimmsAPI::get_model_node_next(int pmeh) {
	int next_meh{};
	const auto ret = aimms->MeNext(pmeh, &next_meh);
	handle_error(ret);
	return next_meh;
}

std::wstring AimmsAPI::get_model_node_name(int meh) {
	aimmsifc::AimmsStringType<wchar_t> name;
	std::wstring name_buf(256, L'\0');
	name.buf	   = name_buf.data();
	name.Length	   = static_cast<int>(name_buf.size());
	const auto ret = aimms->MeName(meh, &name);
	handle_error(ret);
	return name_buf.substr(0, name.Length - 1);
}

std::wstring AimmsAPI::get_model_relative_name(int meh, int rMEH) {
	aimmsifc::AimmsStringType<wchar_t> name;
	std::wstring name_buf(256, L'\0');
	name.buf	   = name_buf.data();
	name.Length	   = static_cast<int>(name_buf.size());
	const auto ret = aimms->MeRelativeName(meh, rMEH, &name);
	handle_error(ret);
	return name_buf.substr(0, name.Length - 1);
}

std::tuple<std::vector<int>, int> AimmsAPI::get_model_node_attributes(int meh) {
	std::vector<int> attrs_buf(256, 0);
	int max_no_attrs{};
	const auto ret = aimms->MeAttributes(meh, attrs_buf.data(), static_cast<int>(attrs_buf.size()), &max_no_attrs);
	handle_error(ret);
	attrs_buf.resize(max_no_attrs);
	return std::tuple{attrs_buf, max_no_attrs};
}

std::wstring AimmsAPI::get_model_node_attribute_name(int attr_id) {
	aimmsifc::AimmsStringType<wchar_t> name;
	std::wstring name_buf(256, L'\0');
	name.buf	   = name_buf.data();
	name.Length	   = static_cast<int>(name_buf.size());
	const auto ret = aimms->MeAttributeName(attr_id, &name);
	handle_error(ret);
	return name_buf.substr(0, name.Length - 1);
}

std::wstring AimmsAPI::get_model_node_type_name(int type) {
	aimmsifc::AimmsStringType<wchar_t> name;
	std::wstring name_buf(256, L'\0');
	name.buf	   = name_buf.data();
	name.Length	   = static_cast<int>(name_buf.size());
	const auto ret = aimms->MeTypeName(type, &name);
	handle_error(ret);
	return name_buf.substr(0, name.Length - 1);
}

int AimmsAPI::get_model_node(int nmeh, const std::wstring& name) {
	int meh{};
	const auto ret = aimms->MeOpenNode(name.c_str(), nmeh, &meh);
	handle_error(ret);
	return meh;
}

int AimmsAPI::get_model_node_type(int meh) {
	int type{};
	const auto ret = aimms->MeType(meh, &type);
	handle_error(ret);
	return type;
}

/*

	THE AIMMS API FUNCTIONS

*/

int AimmsAPI::data_version(const std::wstring& current_identifier_name) {
	int version{};
	const auto& info = get_identifier_info(current_identifier_name);
	const auto ret	 = aimms->IdentifierDataVersion(info.data_handle, &version);
	handle_error(ret);
	return version;
}

std::wstring AimmsAPI::get_identifier_name(int identifier_handle) {
	aimmsifc::AimmsStringType<wchar_t> name;
	std::wstring name_buf(256, L'\0');
	name.buf	   = name_buf.data();
	name.Length	   = static_cast<int>(name_buf.size());
	const auto ret = aimms->AttributeName(identifier_handle, &name);
	handle_error(ret);
	return name_buf.substr(0, name.Length - 1);
}

int AimmsAPI::get_identifier_size(int identifier_handle) {
	int size{};
	const auto ret = aimms->ValueCard(identifier_handle, &size);
	handle_error(ret);
	return size;
}

int AimmsAPI::get_identifier_cardinality(int identifier_handle) {
	int size{};
	int slice{};
	const auto ret = aimms->AttributeDimension(identifier_handle, &size, &slice);
	handle_error(ret);
	return size;
}

std::pair<int, std::vector<int>> AimmsAPI::create_procedure_handle(const std::wstring& name) {
	int procedure_handle{};
	int args	   = 0;
	std::vector<int> arg_types(32, 0);
	const auto ret = aimms->ProcedureHandleCreate(name.c_str(), &procedure_handle, &args, arg_types.data());
	handle_error(ret);
	arg_types.resize(args);

	procedure_handles_count++;
	return {procedure_handle, arg_types};
}

void AimmsAPI::delete_handle_procedure(int procedure_handle) {
	const auto ret = aimms->ProcedureHandleDelete(procedure_handle);
	handle_error(ret);
	procedure_handles_count--;
}

int AimmsAPI::create_identifier_handle(const std::wstring& name) {
	int handle{};

	auto flags = aimmsifc::Flag::NoInactiveData | aimmsifc::Flag::Units;
	if (m_with_index_restriction) {
		flags |= 0x00002000;
	}

	const auto ret = aimms->IdentifierHandleCreate(name.c_str(), nullptr, nullptr, flags, &handle);
	handle_error(ret);
	data_handles_count++;
	return handle;
}

void AimmsAPI::delete_handle(int identifier_handle) {
	const auto ret = aimms->IdentifierHandleDelete(identifier_handle);
	handle_error(ret);
	data_handles_count--;
}

void AimmsAPI::reset_identifier(int identifier_handle) {
	const auto ret = aimms->ValueResetHandle(identifier_handle);
	handle_error(ret);
}

int AimmsAPI::run_procedure(const std::wstring& name, pybind11::kwargs& args) {
	auto& info = get_identifier_info(name);

	// the type thats is returned is a integer which is a combination of two enums the aimmsifc::Storage and aimmifc::argumenttype

	// struct Storage{
    //     enum{
    //         Handle  = 0x00000000,
    //         Double  = 0x00000001,
    //         Int     = 0x00000002,
    //         Binary  = 0x00000003,
    //         String  = 0x00000004
    //     };
    // };

	// enum{
    //     Input           = 0x00000010,
    //     Output          = 0x00000020,
    //     Input_Output    = 0x00000040,
    //     Optional        = 0x00000080
    // };
	// the storage type is the first hexadecimal number
	std::vector<std::pair<int, int>> arg_types_pairs;
	for (auto& arg_type : info.procedure_args_types) {
		int arg_storage_type  = arg_type & 0x0000000F;
		int arg_argument_type = arg_type & 0x000000F0;
		arg_types_pairs.emplace_back(arg_storage_type, arg_argument_type);
	}

	// check the arguments keep in mind the optional arguments which have a higher hexadecimal value then 0x00000080
	// first filter from arg_type_pairs the ones that are not optional
	size_t required_args_count = 0;
	for (const auto& arg_type_pair : arg_types_pairs) {
		if (arg_type_pair.second < 0x00000080) {
			++required_args_count;
		}
	}
	// check if the number of args is correct
	if (args.size() < required_args_count) {
		throw std::runtime_error("Not enough arguments provided for procedure " + aioConvertString(name) + ". Expected at least " + std::to_string(required_args_count) + " arguments.");
	}

	
	// check if the args match the procedure argument types
	for( size_t i = 0; const auto & [key, value] : args) {
		if ((pybind11::isinstance<pybind11::float_>(value) && arg_types_pairs[i].first == aimmsifc::Storage::Double) ||
			(pybind11::isinstance<pybind11::int_>(value) && arg_types_pairs[i].first == aimmsifc::Storage::Int) ||
			(pybind11::isinstance<pybind11::str>(value) && arg_types_pairs[i].first == aimmsifc::Storage::String)) {
		} else {

			std::string type_name;
			if( arg_types_pairs[i].first == aimmsifc::Storage::Double ) {
				type_name = "Double";
			} else if (arg_types_pairs[i].first == aimmsifc::Storage::Int) {
				type_name = "Int";
			} else if (arg_types_pairs[i].first == aimmsifc::Storage::String) {
				type_name = "String";
			} else {
				type_name = "Unknown";
			}

			throw std::runtime_error("Invalid argument type for procedure " + aioConvertString(name) + " at pos " + std::to_string(i + 1) +
				". Expected type: " + type_name + " but got " + value.get_type().attr("__name__").cast<std::string>());
		}
		++i;
	}
	
	std::vector<aimmsifc::AimmsValueType<wchar_t>> arg_values;
	std::vector<std::wstring> string_pool;
	string_pool.reserve(args.size());
	// we get a kwargs with tuples like so name, (value, type enum)
	for (const auto& [key, value] : args) {
		// first element is a int float/double or string make sure to cast it
		// auto key_str = key.cast<std::wstring>();
		if( pybind11::isinstance<pybind11::str>(value) ) {
			auto& value_str = string_pool.emplace_back(std::move(value.cast<std::wstring>()));
			// make sure the string is null terminated
			if (value_str.back() != L'\0') {
				value_str.push_back(L'\0');
			}
			auto& argument = arg_values.emplace_back();
			argument.String.buf = value_str.data(); // NOLINT(cppcoreguidelines-pro-type-union-access)
			argument.String.Length = static_cast<int>(value_str.size()); // NOLINT(cppcoreguidelines-pro-type-union-access)
		} else if ( pybind11::isinstance<pybind11::int_>(value) ) { 
			arg_values.emplace_back().Int = value.cast<int>(); // NOLINT(cppcoreguidelines-pro-type-union-access)
		} else if ( pybind11::isinstance<pybind11::float_>(value) ) {
			arg_values.emplace_back().Double = value.cast<double>(); // NOLINT(cppcoreguidelines-pro-type-union-access)
		} else {
			throw std::runtime_error("An argument in the kwargs is incorrect expect: name=value where value should be a string, int or double");
		}
	}

	int result{};
	const auto ret = aimms->ProcedureRun(info.procedure_handle, static_cast<int>(args.size()), info.procedure_args_types.data(), arg_values.data(), &result);
	handle_error(ret);
	return result;
}

int AimmsAPI::identifier_storage_type(int identifier_handle) {
	int type{};
	const auto ret = aimms->AttributeStorage(identifier_handle, &type);
	handle_error(ret);
	return type;
}

int AimmsAPI::get_identifier_type(int identifier_handle) {
	int type{};
	const auto ret = aimms->AttributeType(identifier_handle, &type);
	handle_error(ret);
	return type;
}

int AimmsAPI::get_identifier_flags(int meh) {
	int flags{};
	const auto ret = aimms->AttributeFlagsGet(meh, &flags);
	handle_error(ret);
	return flags;
}

void AimmsAPI::identifier_empty(int identifier_handle) {
	int empty{};
	const auto ret = aimms->IdentifierEmpty(identifier_handle);
	handle_error(ret);
}

void AimmsAPI::add_value(const std::wstring& current_identifier_name, std::vector<int>& tuple, std::variant<std::wstring, double, int> value, pybind11::dict& options) {
	const auto& info = get_identifier_info(current_identifier_name);
	
	aimmsifc::AimmsValueType<wchar_t> val;
	if( info.storage_type == aimmsifc::Storage::String ) {
		val.String.buf = std::get<std::wstring>(value).data(); // NOLINT(cppcoreguidelines-pro-type-union-access)
		val.String.Length = static_cast<int>(std::get<std::wstring>(value).size()); // NOLINT(cppcoreguidelines-pro-type-union-access)
	} else if (info.storage_type == aimmsifc::Storage::Double) {
		if( std::holds_alternative<int>(value)) {
			val.Double = static_cast<double>(std::get<int>(value)); // NOLINT(cppcoreguidelines-pro-type-union-access)
		} else {
			val.Double = std::get<double>(value); // NOLINT(cppcoreguidelines-pro-type-union-access)
		}
	} else if (info.storage_type == aimmsifc::Storage::Int) {
		if( std::holds_alternative<double>(value)) {
			val.Int = static_cast<int>(std::get<double>(value)); // NOLINT(cppcoreguidelines-pro-type-union-access)
		} else {
			val.Int = std::get<int>(value); // NOLINT(cppcoreguidelines-pro-type-union-access)
		}
	} else {
		throw std::runtime_error("Invalid type assigned to identifier");
	}

	bool update = options.contains("update") ? options["update"].cast<bool>() : false;
	if (!update) {
		identifier_empty(info.data_handle);
	}

	if ( info.storage_type == aimmsifc::Storage::String ) {
		if (tuple.size() == 0) {
			const auto ret = aimms->ValueAssignS(info.data_handle, nullptr, &val);
			handle_error(ret);
			return;
		}
		const auto ret = aimms->ValueAssignS(info.data_handle, tuple.data(), &val);
		handle_error(ret);
		
	} else {
		if (tuple.size() == 0) {
			const auto ret = aimms->ValueAssignN(info.data_handle, nullptr, &val);
			handle_error(ret);
			return;
		}
		const auto ret = aimms->ValueAssignN(info.data_handle, tuple.data(), &val);
		handle_error(ret);
	}
}

std::variant<std::wstring, double, int> AimmsAPI::get_value(const std::wstring& current_identifier_name, std::vector<int>& tuple) {
	aimmsifc::AimmsValueType<wchar_t> val;
	const auto& info = get_identifier_info(current_identifier_name);
	std::wstring val_buf;

	// make sure to allocate for storage type string
	if( info.storage_type == aimmsifc::Storage::String ) {
		val_buf.resize(512);
		val.String.buf = val_buf.data(); // NOLINT(cppcoreguidelines-pro-type-union-access)
		val.String.Length = static_cast<int>(val_buf.size()); // NOLINT(cppcoreguidelines-pro-type-union-access)
	}

	try {
		if( info.storage_type == aimmsifc::Storage::String ) {
			if (tuple.size() == 0) {
				const auto ret = aimms->ValueRetrieveS(info.data_handle, nullptr, &val);
				handle_error(ret);
			} else {
				const auto ret = aimms->ValueRetrieveS(info.data_handle, tuple.data(), &val);
				handle_error(ret);
			}

			// if the string length is larger than the buffer size, resize the buffer and try again
			if (val.String.Length > val_buf.size()) {
				val_buf.resize(val.String.Length);
				val.String.buf = val_buf.data(); // NOLINT(cppcoreguidelines-pro-type-union-access)
				val.String.Length = static_cast<int>(val_buf.size()); // NOLINT(cppcoreguidelines-pro-type-union-access)
				if (tuple.size() == 0) {
					const auto ret = aimms->ValueRetrieveS(info.data_handle, nullptr, &val);
					handle_error(ret);
				} else {
					const auto ret = aimms->ValueRetrieveS(info.data_handle, tuple.data(), &val);
					handle_error(ret);
				}
			} else {
				val_buf.resize(val.String.Length);
			}


		} else {
			if (tuple.size() == 0) {
				const auto ret = aimms->ValueRetrieveN(info.data_handle, nullptr, &val);
				handle_error(ret);
			} else {
				const auto ret = aimms->ValueRetrieveN(info.data_handle, tuple.data(), &val);
				handle_error(ret);
			}
		}
	} catch (const aimms_exception& e) {
		if (e.error_code() == 124) {
			if( info.storage_type == aimmsifc::Storage::String ) {
				return std::wstring();
			}
			if (info.storage_type == aimmsifc::Storage::Double) {
				return 0.0;
			} 
			if (info.storage_type == aimmsifc::Storage::Int) {
				return 0;
			}
		}
		throw;
	}

	if( info.storage_type == aimmsifc::Storage::String ) {
		return val_buf.substr(0, val.String.Length - 1); // NOLINT(cppcoreguidelines-pro-type-union-access)
	} if (info.storage_type == aimmsifc::Storage::Double) {
		return val.Double;
	} if (info.storage_type == aimmsifc::Storage::Int) {
		return val.Int;
	}  		
	
	throw std::runtime_error("Invalid identifier type");

}

/*
	THESE FUNCTIONS ARE FOR THE DICTIONARY INTERFACE FROM PYTHON TO AIMMS
*/

pybind11::object AimmsAPI::copyDictToDataFrame(const std::wstring& current_identifier_name, const pybind11::dict& data, const pybind11::dict& mapping, const pybind11::dict& options)
{
	std::vector<std::wstring> identifierNames;
    identifierNames.push_back(current_identifier_name);

	std::vector<std::wstring> indexNames;
	getSharedIndexDomain(identifierNames, indexNames);
	
	// add indices to identifier list (if not yet present)
	// use reverse order to keep the order of the identifiers
	for (size_t i=indexNames.size(); i>0;i--) {
		if (std::ranges::find(identifierNames, indexNames[i-1]) == identifierNames.end()) {
			identifierNames.insert(identifierNames.begin(), indexNames[i-1]);
		}
	}

	// create ColumnMapping for each identifier in the list (i.e. including all domain indices)
	std::vector<ColumnMapping> colMap;
    std::vector<int> indexMap;
    std::vector<int> idMap;
	std::vector<std::wstring> indexNames2;
	createColumnMapping(identifierNames, indexNames2, colMap, indexMap, idMap);
	assert(indexNames2 == indexNames);

    arrow4cxx::ArrowTable table;
	{
		int colno = 0;
		
		for (auto &col: colMap) {
			arrow4cxx::ColumnInfo colInfo;
			colInfo.colno = colno++;
			colInfo.name = aioConvertString(col.colName);    
			colInfo.aimmsType = col.aimmsType;
			colInfo.arrowType = col.arrowType;
			arrow4cxx::ArrowValue av((int64_t)0,-1);
			col.colWriter = table.getWritableColumn(colInfo, av);
		}
	}
	
	int row = 0;
	std::vector<int> t(indexMap.size());
	for (const auto& item : data) {
		const auto tuple = item.first.cast<pybind11::tuple>();
		// index columns
		if (indexNames.size() == 1) {
			auto &col = colMap[indexMap[0]];
			const auto &sv = item.first.cast<std::string_view>();
			col.colWriter->append(row, std::string(sv));
		} else {
			for (size_t i=0; i<tuple.size(); i++) {
				auto &col = colMap[indexMap[i]];
				const auto &sv = tuple[i].cast<std::string_view>();
				col.colWriter->append(row, std::string(sv));
			}
		}
		// identifier column
		auto &col = colMap[idMap[0]];
		switch (col.aimmsType) {
		case aimmsifc::IdentifierType::ParameterNumerics:
		case aimmsifc::IdentifierType::Variable:
		{
			double value = item.second.cast<double>();
			col.colWriter->append(row, value);
		}
		break;
		case aimmsifc::IdentifierType::ParameterStrings:
		case aimmsifc::IdentifierType::ParameterElements:
		{
			const auto &sv = item.second.cast<std::string_view>();
			col.colWriter->append(row, std::string(sv));
		}
		break;
		}
		row++;
    }	

    table.FinishTable(row);
	
	const auto& raw_table = table.getTable();
	auto* pyobject = arrow::py::wrap_table(raw_table);
	return pybind11::reinterpret_steal<pybind11::object>(pyobject);
}
	
void AimmsAPI::add_values(const std::wstring& current_identifier_name, pybind11::dict& data, pybind11::dict& options) {
	auto df = copyDictToDataFrame(current_identifier_name, data, pybind11::dict(), options);
	copyDataframeToAimms(df, pybind11::dict(), options);
}

class IdentifierHandles : public std::vector<int> {
private:
	AimmsAPI *m_Api;
public:
	IdentifierHandles(AimmsAPI *api, const std::vector<std::wstring> &names) 
		: m_Api(api) {
		resize(names.size(),0);
		for (size_t i=0; i<this->size(); i++) {
			(*this)[i] = m_Api->create_identifier_handle(names[i]);
		}
	}
	~IdentifierHandles() {
		for (size_t i=0; i<this->size(); i++) {
			if ((*this)[i] != 0) {
				m_Api->delete_handle((*this)[i]);
			}
		}
	}	
};

void AimmsAPI::getSharedIndexDomain(const std::vector<std::wstring> &identifierNames, std::vector<std::wstring> &indexNames) {
	IdentifierHandles identifierHandles(this, identifierNames);
	
	// determine shared index domain
	indexNames.clear();
	bool firstTime = true;
	for (size_t i=0; i<identifierHandles.size(); i++) {
		int type = get_identifier_type(identifierHandles[i]);
		if (type == aimmsifc::IdentifierType::Index || type == aimmsifc::IdentifierType::SimpleSetRoot || type == aimmsifc::IdentifierType::SimpleSetSubset) {
			continue;
		}
		auto indexDomainNames = get_declaration_domain(identifierHandles[i]);
		if (firstTime) {
			indexNames = indexDomainNames;
			firstTime = false;
		} else {
			if (indexDomainNames != indexNames) {
				std::ostringstream os;
				os << "Identifier " << aioConvertString(identifierNames[i]) << " has different index domain than the first identifier";
				throw std::runtime_error(os.str());
			}
		}
	}
}

void AimmsAPI::createColumnMapping(const std::vector<std::wstring> &identifierNames, std::vector<std::wstring> &indexNames, std::vector<ColumnMapping> &colMap, std::vector<int> &indexMap, std::vector<int> &idMap) {
	// check if the identifier names are valid
	// for (size_t i=0; i<identifierNames.size(); i++) {
	// 	if (all_model_identifiers_map.find(identifierNames[i]) == all_model_identifiers_map.end()) {
	// 		throw std::runtime_error("Identifier not found: " + aioConvertString(identifierNames[i]));
	// 	}
	// }

	// determine shared index domain
	getSharedIndexDomain(identifierNames, indexNames);

	// make sure all domain indices are present as part of the identifier names
	for (const auto & indexName : indexNames) {
		if (std::ranges::find(identifierNames, indexName) == identifierNames.end()) {
			throw std::runtime_error("Domain index " + aioConvertString(indexName) + " not present in table");
		}
	}

	// create ColumnMapping
	for (size_t i=0; i<identifierNames.size(); i++) {
		colMap.resize(i + 1);
		ColumnMapping &col = colMap[i];
		col.idName = identifierNames[i];
		col.id = std::make_shared<AimmsIOHandler<>>(identifierNames[i]);
		int type = col.id->Type();
		col.isSet = (type == aimmsifc::IdentifierType::Index || type == aimmsifc::IdentifierType::SimpleSetRoot || type == aimmsifc::IdentifierType::SimpleSetSubset || type == aimmsifc::IdentifierType::ParameterElements);
		if (col.isSet && !col.id->GetAimmsHandle().ElementRange().empty()) {
			col.range = std::make_shared<AimmsIOHandler<>>(col.id->GetAimmsHandle().ElementRange());
		}
		col.isCalendar = (col.id->GetAimmsHandle().IsCalendar() || col.id->GetAimmsHandle().IsCalendarValued());
		col.aimmsType = col.id->Type();
		col.extend = ExtendType::Extend;
		col.colName = col.idName;
		if (col.isCalendar) {
			col.arrowType = arrow4cxx::ARROW4CXX_CALENDAR_TYPE;
			col.transferType = Transfer::Type::TM;
		} else {
			switch (col.aimmsType) {
			case aimmsifc::IdentifierType::Index:
			case aimmsifc::IdentifierType::ParameterElements:
			case aimmsifc::IdentifierType::ParameterStrings:
				col.arrowType = arrow4cxx::ARROW4CXX_STRING_TYPE;
				col.transferType = Transfer::Type::String;
				break;
			case aimmsifc::IdentifierType::ParameterNumerics:
			case aimmsifc::IdentifierType::Variable:
				switch (col.id->StorageType()) {
				case aimmsifc::Storage::Binary:
					col.arrowType = arrow4cxx::ARROW4CXX_BOOL_TYPE;
					col.transferType = Transfer::Type::Bool;
					break;
				case aimmsifc::Storage::Int:
					col.arrowType = arrow4cxx::ARROW4CXX_INT_TYPE;
					col.transferType = Transfer::Type::Int;
					break;
				default:
					col.arrowType = arrow4cxx::ARROW4CXX_DOUBLE_TYPE;
					col.transferType = Transfer::Type::Double;
					break;
				}
				break;
			}
		}
	}

	// make sure no other indices are present
	for (size_t i=0; i<colMap.size(); i++) {
		auto& col = colMap[i];
		if (col.aimmsType == aimmsifc::IdentifierType::Index) {
			if (std::find(indexNames.begin(), indexNames.end(), col.idName) == indexNames.end()) {
				throw std::runtime_error("Index " + aioConvertString(col.idName) + " is not in the index domain of the identifiers");
			}
		}
	}

	// create indexMap and idMap
	indexMap.clear();
	idMap.clear();
	for (size_t i=0; i<colMap.size(); i++) {
		ColumnMapping &col = colMap[i];
		if (col.aimmsType == aimmsifc::IdentifierType::Index) {
			indexMap.push_back(i);
		} else { 
			idMap.push_back(i);
		}
	}

}

void AimmsAPI::copyDataframeToAimms(const pybind11::object& data, const pybind11::dict& mapping, const pybind11::dict& options) {
	bool update = options.contains("update") ? options["update"].cast<bool>() : false;
	bool checking = options.contains("checking") ? options["checking"].cast<bool>() : false;

	auto const& result = arrow::py::unwrap_table(data.ptr());

	std::shared_ptr<arrow4cxx::ArrowTable> table = std::make_shared<arrow4cxx::ArrowTable>();

	auto const& raw_table = result.ValueOrDie();
	table->setTable(raw_table);

	auto schema = raw_table->schema();
	table->setSchema(schema);

	// create identifier list, arrow table already includes index columns
	std::vector<std::wstring> identifierNames;
	auto columnInfos = table->getColumnInfos();
	for (size_t i=0; i<columnInfos.size(); i++) {
		auto& columnInfo = columnInfos[i];
		identifierNames.emplace_back(aioConvertString(mapping.contains(columnInfo.name) ? mapping[columnInfo.name.c_str()].cast<std::string>() : columnInfo.name));
	}

	// create ColumnMapping for each column in the arrow table
	std::vector<std::wstring> indexNames;
	std::vector<ColumnMapping> colMap;
    std::vector<int> indexMap;
    std::vector<int> idMap;
	createColumnMapping(identifierNames, indexNames, colMap, indexMap, idMap);

	if (!update) {
		for (auto &id: idMap) {
       		 auto &col = colMap[id];
			 col.id->Empty();
		}
	}

	auto colInfos = table->getColumnInfos(); 
    for (size_t i = 0; i < colInfos.size(); i++) {
        auto &col = colMap[i];
        col.colReader = table->getReadableColumn(i);
    }

    size_t rows = table->num_rows(); 

    std::vector<int> tuple(indexMap.size());
    for (size_t row = 0; row < rows; row++) {
        for (auto &index: indexMap) {
            auto &col = colMap[index];
            tuple[index] = col.getElementFromRow(row, checking);
        }

        for (auto &id: idMap) {
            auto &col = colMap[id];
            int retval = col.getValueFromRow(row, col.id->Value(), checking);
            if (!retval) continue;
            
            col.id->ValueAssign(tuple.data(), col.id->asValue(), false);
            if (col.id->NeedsCommit()) {
                for (auto &index: indexMap) colMap[index].id->Commit();
                if (col.range.get()) col.range->Commit();

                col.id->Commit();
            }
        }
    }

    // Final commit
    for (auto &index: indexMap) colMap[index].id->Commit();
    for (auto &id: idMap) {
        auto &col = colMap[id];
        if (col.range.get()) col.range->Commit();
        col.id->Commit();
    }
}

pybind11::object AimmsAPI::copyAimmsToDataframe(const pybind11::list &identifierList, const pybind11::dict& mapping, const pybind11::dict& options)
{
	std::vector<std::wstring> identifierNames;
    for (const auto& item : identifierList) {
        identifierNames.emplace_back(aioConvertString(item.cast<std::string>()));
    }
	

	std::vector<std::wstring> indexNames;
	getSharedIndexDomain(identifierNames, indexNames);
	
	// add indices to identifier list (if not yet present)
	// use reverse order to keep the order of the identifiers
	for (size_t i=indexNames.size(); i>0;i--) {
		if (std::find(identifierNames.begin(), identifierNames.end(), indexNames[i-1]) == identifierNames.end()) {
			identifierNames.insert(identifierNames.begin(), indexNames[i-1]);
		}
	}

	// create ColumnMapping for each identifier in the list (i.e. including all domain indices)
	std::vector<ColumnMapping> colMap;
    std::vector<int> indexMap;
    std::vector<int> idMap;
	std::vector<std::wstring> indexNames2;
	createColumnMapping(identifierNames, indexNames2, colMap, indexMap, idMap);
	assert(indexNames2 == indexNames);

    arrow4cxx::ArrowTable table;
	{
		int colno = 0;
	
		for (auto &col: colMap) {
			arrow4cxx::ColumnInfo colInfo;
			colInfo.colno = colno++;
			colInfo.name = aioConvertString(col.colName);    
			colInfo.aimmsType = col.aimmsType;
			colInfo.arrowType = col.arrowType;
			arrow4cxx::ArrowValue av((int64_t)0,-1);
			col.colWriter = table.getWritableColumn(colInfo, av);
		}
	}
	
    std::vector<int> boundElements;

    // Fill the buffers for all identifiers
    for (auto &id: idMap) { 
        colMap[id].dataAvailable = colMap[id].id->ValueNext();
    }

    int row = 0;
    for (;;) {
        AimmsIOHandler<> *current = nullptr;
		boundElements.resize(0);
        for (auto &id: idMap) {
            auto &col = colMap[id];
            if (col.dataAvailable && col.id->comparePartialTupleWithLBVector(current, boundElements) < 0) {
                current = col.id.get();
            }
        }

        if (!current) break;

        for (size_t i = 0; i < indexMap.size(); i++) {
            auto &col = colMap[indexMap[i]];
            col.appendElementToRow(row, current->tuple(i));
            boundElements.push_back(current->tuple(i));
        }

        for (auto &id: idMap) {
            auto &col = colMap[id];
            if (col.dataAvailable && col.id->comparePartialTupleWithLBVector(nullptr, boundElements) <= 0) {
                col.appendValueToRow(row);
                col.dataAvailable = col.id->ValueNext();
            }
        }

        row++;
    }
 
    table.FinishTable(row);
	
	const auto& raw_table = table.getTable();
	auto* pyobject = arrow::py::wrap_table(raw_table);
	return pybind11::reinterpret_steal<pybind11::object>(pyobject);
}

void AimmsAPI::multi_add_values_dataframe_arrow(const pybind11::object& data, pybind11::dict& options) {
	auto const& result = arrow::py::unwrap_table(data.ptr());

	std::shared_ptr<arrow4cxx::ArrowTable> table = std::make_shared<arrow4cxx::ArrowTable>();

	auto const& raw_table = result.ValueOrDie();
	table->setTable(raw_table);

	auto schema = raw_table->schema();
	table->setSchema(schema);

	copyDataframeToAimms(data, pybind11::dict(), options);
}

void AimmsAPI::add_values_dataframe_arrow(	const std::wstring& current_identifier_name, const pybind11::object& data, pybind11::dict& options) {
	auto const& result = arrow::py::unwrap_table(data.ptr());

	std::shared_ptr<arrow4cxx::ArrowTable> table = std::make_shared<arrow4cxx::ArrowTable>();

	auto const& raw_table = result.ValueOrDie();
	table->setTable(raw_table);

	auto schema = raw_table->schema();
	table->setSchema(schema);

	// create identifier list, arrow table already includes index columns
	auto columnInfos = table->getColumnInfos();
	bool identifierFound = false;
	for (size_t i=0; i<columnInfos.size(); i++) {
		auto& columnInfo = columnInfos[i];
		std::wstring columnName = aioConvertString(std::string(columnInfo.name));
		identifierFound = (columnName == current_identifier_name);
		if (identifierFound) {
			break;
		}
	}
	if (!identifierFound) {
		throw std::runtime_error("Identifier " + aioConvertString(current_identifier_name) + " not present in dataframe");
	}

	copyDataframeToAimms(data, pybind11::dict(), options);
}

pybind11::dict AimmsAPI::copyDataFrametoDict(const std::wstring& current_identifier_name, const pybind11::object& data, const pybind11::dict& mapping, const pybind11::dict& options)
{
	// then convert into pybin11:dict
	auto const& result = arrow::py::unwrap_table(data.ptr());

	std::shared_ptr<arrow4cxx::ArrowTable> table = std::make_shared<arrow4cxx::ArrowTable>();

	auto const& raw_table = result.ValueOrDie();
	table->setTable(raw_table);

	auto schema = raw_table->schema();
	table->setSchema(schema);

	// create identifier list, arrow table already includes index columns
	std::vector<std::wstring> identifierNames;
	auto columnInfos = table->getColumnInfos();
	for (size_t i=0; i<columnInfos.size(); i++) {
		auto& columnInfo = columnInfos[i];
		identifierNames.emplace_back(aioConvertString(columnInfo.name));
	}

	// create ColumnMapping for each column in the arrow table
	std::vector<std::wstring> indexNames;
	std::vector<ColumnMapping> colMap;
    std::vector<int> indexMap;
    std::vector<int> idMap;
	createColumnMapping(identifierNames, indexNames, colMap, indexMap, idMap);

	auto colInfos = table->getColumnInfos(); 
    for (size_t i = 0; i < colInfos.size(); i++) {
        auto &col = colMap[i];
        col.colReader = table->getReadableColumn(i);
    }

    size_t rows = table->num_rows(); 
	pybind11::dict dict;

	pybind11::module_ datetime = pybind11::module_::import("datetime");
	pybind11::object datetime_class = datetime.attr("datetime");

	bool checking = options.contains("checking") ? options["checking"].cast<bool>() : false;

    for (size_t row = 0; row < rows; row++) {
		pybind11::tuple tuple(indexMap.size());
        for (auto &index: indexMap) {
            auto &col = colMap[index];
			int element = col.getElementFromRow(row, checking);
			bool datetimeSpecified = false;			
			if (col.id->GetAimmsHandle().IsCalendar()) {
				int year, month, day, hour, minute, second;
				if (col.id->CalendarElementToDate(element, year, month, day, hour, minute, second)) {
					tuple[index] = datetime_class(
						pybind11::int_(year),
						pybind11::int_(month),
						pybind11::int_(day),
						pybind11::int_(hour),
						pybind11::int_(minute),
						pybind11::int_(second)
					);
					datetimeSpecified = true;
				}
			}
			if (!datetimeSpecified) {
				// just use the element name (as a string)
				tuple[index] = col.id->GetSetElementNameA(element, 0, false);
			}
        }
		pybind11::object key = tuple;
		if (indexMap.size() == 1) {
			if (colMap[indexMap[0]].isCalendar) {
				key = tuple[0];
			} else {
				key = pybind11::str(tuple[0].cast<std::string>());
			}
		}
        for (auto &id: idMap) {
            auto &col = colMap[id];
            int retval = col.getValueFromRow(row, col.id->Value(), checking);
            if (retval) {
				switch (col.id->Type()) {
				case aimmsifc::IdentifierType::ParameterNumerics:
				case aimmsifc::IdentifierType::Variable:
					dict[key] = col.id->asDouble();
					break;
				case aimmsifc::IdentifierType::ParameterElements:
					{
						int element = col.getElementFromRow(row, checking);
						std::string elementValueName;
						bool datetimeSpecified = false;		
						if (col.id->GetAimmsHandle().IsCalendarValued()) {
							// TODO
							datetimeSpecified = true;
						}
						if (!datetimeSpecified) {
							elementValueName = aioConvertString(col.id->ElementValueName(element));
							dict[key] = elementValueName;
						}
					}
					break;
				case aimmsifc::IdentifierType::ParameterStrings:
					dict[key] = aioConvertString(col.id->asString());
					break;
				default:
					dict[key] = pybind11::none();
					break;
				}
			} else {
				dict[key] = pybind11::none();
			}
		}   
	}   
	
	return dict;
}

pybind11::dict AimmsAPI::get_values(const std::wstring& current_identifier_name) {
	// first create an arrow table with the data
	pybind11::list identifierList;
	identifierList.append(current_identifier_name);

	auto data = copyAimmsToDataframe(identifierList, pybind11::dict(), pybind11::dict());
	return copyDataFrametoDict(current_identifier_name, data, pybind11::dict(), pybind11::dict());
}

pybind11::object AimmsAPI::get_values_dataframe_arrow(
	const std::wstring& current_identifier_name, const std::vector<std::wstring>& column_mapping
) {
	pybind11::list identifierList;
	identifierList.append(current_identifier_name);

	return copyAimmsToDataframe(identifierList, pybind11::dict(), pybind11::dict());
}

std::vector<int> AimmsAPI::add_set_values(const std::wstring& current_identifier_name, const std::vector<std::wstring>& data) {
	std::vector<int> element_number(data.size(), 0);
	const auto& info = get_identifier_info(current_identifier_name);
	identifier_empty(info.data_handle);
	for (size_t i = 0; const auto& element : data) {
		const auto ret = aimms->SetAddElement(info.data_handle, element.c_str(), &element_number[i++]);
		handle_error(ret);
	}
	return element_number;
}

pybind11::list AimmsAPI::get_set_values(const std::wstring& current_identifier_name) {
	pybind11::list values;
	const auto& info = get_identifier_info(current_identifier_name);

	reset_identifier(info.data_handle);
	const auto size = get_identifier_size(info.data_handle);
	for (int i = 1; i <= size; ++i) {
		aimmsifc::AimmsStringType<wchar_t> name;
		std::wstring name_buf(1024, L'\0');
		name.buf	= name_buf.data();
		name.Length = static_cast<int>(name_buf.size());
		aimms->SetOrdinalToName(info.data_handle, i, &name);
		values.append(name_buf.substr(0, name.Length - 1)); // NOLINT(cppcoreguidelines-pro-type-union-access)
	}

	return values;
}

int AimmsAPI::get_setelement_number(int meh, const std::wstring& name) {
	int number{};
	int is_created{};
	const auto ret = aimms->SetElementNumber(meh, name.c_str(), 0, &number, &is_created);
	handle_error(ret);

	return number;
}

std::tuple<std::vector<int>, aimmsifc::AimmsValueType<wchar_t>> AimmsAPI::next_identifier(int meh) {
	std::vector<int> tuple(aimmsifc::MaxDimension, 0);
	aimmsifc::AimmsValueType<wchar_t> value;
	const auto ret = aimms->ValueNextN(meh, tuple.data(), &value);
	handle_error(ret);
	return std::tuple{tuple, value}; // NOLINT
}

std::vector<std::wstring> AimmsAPI::get_exposed_identifiers(const std::wstring& set_name) {
	const auto handle = create_identifier_handle(set_name);
	const auto size	  = get_identifier_size(handle);
	std::vector<std::wstring> identifiers(size, std::wstring(1024, L'\0'));
	aimmsifc::AimmsStringType<wchar_t> name;

	for (int i = 1; auto& identifier : identifiers) {
		name.buf	= identifier.data();
		name.Length = static_cast<int>(identifier.size());
		aimms->SetOrdinalToName(handle, i++, &name);
		identifier.resize(name.Length - 1);
	}

	delete_handle(handle);

	return identifiers;
}

// loop over the entire model with the me child and next functions
void AimmsAPI::walk_model_recursive(int node, auto& nodes) { // NOLINT
	if (node == 0) {
		return;
	}

	// auto name = get_model_node_name(node);
	auto full_name = get_model_relative_name(node, 0);

	auto& info = nodes[full_name];

	try {
		info.me_handle = node;
		info.me_type = get_model_node_type(node);

		if (info.me_type == aimmsifc::ModelEditing::IdentifierType::Procedure) {
			// stop treewalk (to exclude local symbols)
			return;
		}

	} catch (const aimms_exception& e) {
		if (e.error_code() != 202) {
			throw;
		}
	} catch (const std::exception& e) {
		std::cerr << "Error in walk_model_recursive: " << e.what() << '\n';
		// throw;
	}

	int child = get_model_node_child(node);
	while (child != 0) {
		walk_model_recursive(child, nodes);
		child = get_model_node_next(child);
	}
}

void AimmsAPI::walk_model(int root) {
	if (root == 0) {
		root = get_model_node_root();
	}
	walk_model_recursive(root, all_model_identifiers_map);

	const auto count = get_model_root_count();

	for (int i = 1; i < count; ++i) {
		auto root = get_model_node_root(i);
		walk_model_recursive(root, all_model_identifiers_map);
	}
}

identifier_info& AimmsAPI::get_identifier_info(const std::wstring& name) {
	auto it = all_model_identifiers_map.find(name);
	if (it != all_model_identifiers_map.end()) {
		auto& info = it->second;
		if ((info.data_handle != -1) || (info.procedure_handle != -1)) {
			return info;
		}
		// if type is set parameter or variable also get the dimension and flags
		if (info.me_type == aimmsifc::ModelEditing::IdentifierType::ParameterNumeric || info.me_type == aimmsifc::ModelEditing::IdentifierType::VariableNumeric ||
			info.me_type == aimmsifc::ModelEditing::IdentifierType::Set || info.me_type == aimmsifc::ModelEditing::IdentifierType::ParameterString ||
			info.me_type == aimmsifc::ModelEditing::IdentifierType::ParameterElement) {
			info.data_handle		= create_identifier_handle(name);
			info.dimension			= get_identifier_size(info.data_handle);
			info.flags				= get_identifier_flags(info.data_handle);
			info.aimms_type			= get_identifier_type(info.data_handle);
			info.storage_type		= identifier_storage_type(info.data_handle);
		}
		if (info.me_type == aimmsifc::ModelEditing::IdentifierType::Index) {
			// get the range attribute of this index to check if it has one because if thats not the case it means its an free index and if you try to get some stuff from
			// it aimms does biem
			std::wstring range_attr = get_attribute(info.me_handle, aimmsifc::ModelEditing::AttributeType::Range);

			if (!range_attr.empty()) {
				info.data_handle		= create_identifier_handle(name);
			}
		}
		if (info.me_type == aimmsifc::ModelEditing::IdentifierType::Procedure) {
			// const auto argument_attr = get_attribute(info.me_handle, aimmsifc::ModelEditing::AttributeType::Arguments);
			// if (argument_attr.empty()) {
			//just make the handle because we support most arguments already
				auto [handle, vector] = create_procedure_handle(name);
				info.procedure_handle = handle;
				info.procedure_args_types = vector;
			// }
		}
		return info;
	}
	throw std::runtime_error("Identifier not found: " + ___convert(name));
}

void AimmsAPI::handle_error(int ret) {
	if (ret != aimmsifc::E_ReturnValue::Success) {
		std::wstring error_message(256, L'\0');
		int error_code{};
		auto error_ret = aimms->APILastError(&error_code, error_message.data(), static_cast<int>(error_message.size()));

		if (error_ret == aimmsifc::E_ReturnValue::Success) {
			auto error_message_all = L"Error code: " + std::to_wstring(error_code) + L", message: " + std::wstring(error_message.begin(), error_message.end());
			throw aimms_exception(error_code, error_message_all);
		}
		throw std::runtime_error("Could not get error message");
	}
}

void AimmsAPI::init_aimms(const std::string& aimms_bin_path) {
	aimms = aimmsifc::createUnicodeInterface(true, aimms_bin_path.c_str());
	AimmsFactory::setAimms(aimms);
}

void AimmsAPI::open_project(const std::wstring& command) {
	auto ret = aimms->ProjectOpen(command.c_str(), &aimms_project_handle);
	handle_error(ret);
}

void AimmsAPI::close_project() {
	auto ret = aimms->ProjectClose(aimms_project_handle, 0);
	try {
		handle_error(ret);
	} catch (...) {
		std::cerr << "Could not close aimms project properly\n";
	}
	aimms_project_handle = 0;
}