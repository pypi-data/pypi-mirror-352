#include "aimms_api_py/aimms_api.hpp"

PYBIND11_MAKE_OPAQUE(std::vector<int>);
// PYBIND11_MAKE_OPAQUE(mappings);
// PYBIND11_MAKE_OPAQUE(identifier_info);
// PYBIND11_MAKE_OPAQUE(std::vector<std::wstring>);
// PYBIND11_MAKE_OPAQUE(std::wstring);
// PYBIND11_MAKE_OPAQUE(std::string);
// PYBIND11_MAKE_OPAQUE(std::tuple<std::vector<int>, int>);
PYBIND11_MAKE_OPAQUE(std::unordered_map<std::wstring, mappings>);
PYBIND11_MAKE_OPAQUE(std::unordered_map<std::wstring, identifier_info>);

PYBIND11_MODULE(aimmspy, m) {

	// for performance reasons, we bind the vector of integers as an opaque type
	pybind11::bind_vector<std::vector<int>>(m, "int_vector");
	pybind11::bind_map<std::unordered_map<std::wstring, mappings>>(m, "set_mappings");
	pybind11::bind_map<std::unordered_map<std::wstring, identifier_info>>(m, "all_model_identifiers_map");

	// for walking the aimms model we need to bind the identifier_info struct which is mapped to a identifier full name
	pybind11::class_<identifier_info>(m, "identifier_info")
		.def_readonly("me_handle", &identifier_info::me_handle)
		.def_readonly("me_type", &identifier_info::me_type)
		.def_readonly("data_handle", &identifier_info::data_handle)
		.def_readonly("aimms_type", &identifier_info::aimms_type)
		.def_readonly("dimension", &identifier_info::dimension)
		.def_readonly("flags", &identifier_info::flags)
		.def_readonly("storage_type", &identifier_info::storage_type)
		.def_readonly("procedure_handle", &identifier_info::procedure_handle)
		.def_readonly("procedure_args_types", &identifier_info::procedure_args_types)
		;

	// mappings need for the data assigning and data retrieval we have to go from string tuples to element number tuples and back
	// therefore we keep track of the element number for each string tuple in the mappings class
	pybind11::class_<mappings>(m, "mappings")
		.def(pybind11::init<>())
		.def("add", &mappings::add)
		.def("get_element", &mappings::get_element)
		.def("get_name", &mappings::get_name)
		.def("to_string", &mappings::to_string);

	// all the aimms api functions that we expose to python
	pybind11::class_<AimmsAPI>(m, "AimmsAPI")
		.def(pybind11::init<const std::string&, const std::wstring&, pybind11::object, bool>())
		.def("add_attribute", &AimmsAPI::add_attribute)
		.def("get_attribute", &AimmsAPI::get_attribute)
		.def("create_procedure", &AimmsAPI::create_procedure_handle)
		.def("run_procedure", &AimmsAPI::run_procedure)
		.def("create_identifier", &AimmsAPI::create_identifier_handle)
		.def("data_version", &AimmsAPI::data_version)

		// for single value assignments and retrievals
		.def("get_value", &AimmsAPI::get_value)
		.def("add_value", &AimmsAPI::add_value)

		// special functions for set values
		.def("get_set_values", &AimmsAPI::get_set_values)
		.def("add_set_values", &AimmsAPI::add_set_values)

		// for multiple value assignments and retrievals
		.def("get_values", &AimmsAPI::get_values)
		.def("get_values_dataframe_arrow", &AimmsAPI::get_values_dataframe_arrow)
		.def("add_values_dataframe_arrow", &AimmsAPI::add_values_dataframe_arrow)
		.def("multi_add_values_dataframe_arrow", &AimmsAPI::multi_add_values_dataframe_arrow)
		.def("add_values", &AimmsAPI::add_values)
		.def("identifier_empty", &AimmsAPI::identifier_empty)
		.def("get_identifier_cardinality", &AimmsAPI::get_identifier_cardinality)

		// these functions execute multiple aimms api calls and return the results
		.def("get_exposed_identifiers", &AimmsAPI::get_exposed_identifiers)
		.def("walk_model", &AimmsAPI::walk_model)
		.def("get_identifier_info", &AimmsAPI::get_identifier_info)

		.def_static("get_current_aimms_api", &AimmsAPI::get_current_aimms_api)

		;
}