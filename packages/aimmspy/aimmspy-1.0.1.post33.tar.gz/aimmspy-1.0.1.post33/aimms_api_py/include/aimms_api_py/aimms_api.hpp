#pragma once

#include <boost/locale/conversion.hpp>
#include <chrono> // IWYU pragma: export
#include <codecvt>
#include <functional>
#include <iostream> // IWYU pragma: export
#include <ranges>	// IWYU pragma: export
#include <string>	// IWYU pragma: export
#include <unordered_map>
#include <utility> // IWYU pragma: export

#define PYBIND11_DETAILED_ERROR_MESSAGES

#include "pybind11/numpy.h"	   // IWYU pragma: export
#include "pybind11/pybind11.h" // IWYU pragma: export
#include "pybind11/stl.h"	   // IWYU pragma: export
#include <pybind11/pytypes.h>
#include <pybind11/stl_bind.h>

#include "arrow/api.h"			  // IWYU pragma: export
#include "arrow/python/pyarrow.h" // IWYU pragma: export

#include "aimmsifc/aimmsifc.h"		  // IWYU pragma: export
#include "aimmsifc/iAimms.h"		  // IWYU pragma: export
#include "aimmsifc/iAimmsCharTypes.h" // IWYU pragma: export

#include "aimms_api_py/aimms_exception.hpp"
#include "aimms_api_py/identifier_info.hpp"
#include "aimms_api_py/set_mappings.hpp"

/**
 * @class AimmsAPI
 * @brief Provides an interface to interact with AIMMS projects and their data.
 */
class AimmsAPI {
public:

	/**
	 * @brief Constructs the AimmsAPI object and initializes AIMMS.
	 * @param aimms_bin_path Path to the AIMMS binary.
	 * @param project_command Command to open the AIMMS project.
	 */
	AimmsAPI(const std::string& aimms_bin_path, const std::wstring& project_command, pybind11::object aimms_project_self, bool with_idex_restriction);

	/**
	 * @brief Destroys the AimmsAPI object and closes the AIMMS project.
	 */
	~AimmsAPI();

	/**
	 * @brief Copy constructor.
	 */
	AimmsAPI(const AimmsAPI&) = delete;
	/**
	 * @brief Copy assignment operator.
	 * @return Reference to the copied AimmsAPI object.
	 */
	AimmsAPI& operator=(const AimmsAPI&) = delete;

	/**
	 * @brief Move constructor.
	 */
	AimmsAPI(AimmsAPI&&) noexcept = delete;

	/**
	 * @brief Move assignment operator.
	 * @return Reference to the moved AimmsAPI object.
	 */
	AimmsAPI& operator=(AimmsAPI&&) noexcept = delete;

	// THE AIMMS ME API FUNCTIONS

	/**
	 * @brief Adds an attribute to a node.
	 * @param meh Node handle.
	 * @param name Name of the attribute.
	 * @param idtype Type of the attribute.
	 */
	void add_attribute(int meh, const std::wstring& name, int idtype);

	/**
	 * @brief Retrieves the value of an attribute from a node.
	 * @param meh Node handle.
	 * @param attr_id Attribute ID.
	 * @return Value of the attribute.
	 */
	std::wstring get_attribute(int meh, int attr_id);

	/**
	 * @brief Retrieves the root node of the AIMMS model.
	 * @param pos Position of the root node (default is 0).
	 * @return Handle to the root node.
	 */
	int get_model_node_root(int pos = 0);

	/**
	 * @brief Retrieves the count of root nodes in the AIMMS model.
	 * @return Number of root nodes.
	 */
	int get_model_root_count();

	/**
	 * @brief Retrieves the first child of a node.
	 * @param pmeh Parent node handle.
	 * @return Handle to the child node.
	 */
	int get_model_node_child(int pmeh);

	/**
	 * @brief Retrieves the next sibling of a node.
	 * @param pmeh Current node handle.
	 * @return Handle to the next sibling node.
	 */
	int get_model_node_next(int pmeh);

	/**
	 * @brief Retrieves the name of a node.
	 * @param meh Node handle.
	 * @return Name of the node.
	 */
	std::wstring get_model_node_name(int meh);

	/**
	 * @brief Retrieves the relative name of a node.
	 * @param meh Node handle.
	 * @param rMEH Reference node handle.
	 * @return Relative name of the node.
	 */
	std::wstring get_model_relative_name(int meh, int rMEH);

	/**
	 * @brief Retrieves the attributes of a node.
	 * @param meh Node handle.
	 * @return A tuple containing a vector of attribute IDs and the number of attributes.
	 */
	std::tuple<std::vector<int>, int> get_model_node_attributes(int meh);

	/**
	 * @brief Retrieves the name of an attribute.
	 * @param attr_id Attribute ID.
	 * @return Name of the attribute.
	 */
	std::wstring get_model_node_attribute_name(int attr_id);

	/**
	 * @brief Retrieves the type name of a node.
	 * @param type Node type.
	 * @return Type name of the node.
	 */
	std::wstring get_model_node_type_name(int type);

	/**
	 * @brief Retrieves a node by its name and parent handle.
	 * @param nmeh Parent node handle.
	 * @param name Name of the node.
	 * @return Handle to the node.
	 */
	int get_model_node(int nmeh, const std::wstring& name);

	/**
	 * @brief Retrieves the type of a node.
	 * @param meh Node handle.
	 * @return Type of the node.
	 */
	int get_model_node_type(int meh);

	// THE AIMMS API FUNCTIONS

	/**
	 * @brief Retrieves the data version of an identifier.
	 * @param handle Identifier handle.
	 * @return Data version.
	 */
	int data_version(const std::wstring& current_identifier_name);

	/**
	 * @brief Retrieves the name of an identifier.
	 * @param identifier_handle Identifier handle.
	 * @return Name of the identifier.
	 */
	std::wstring get_identifier_name(int identifier_handle);

	/**
	 * @brief Retrieves the size of an identifier.
	 * @param identifier_handle Identifier handle.
	 * @return Size of the identifier.
	 */
	int get_identifier_size(int identifier_handle);

	int get_identifier_cardinality(int identifier_handle);

	/**
	 * @brief Compiles an identifier.
	 * @param handle Identifier handle.
	 */
	void compile(int handle);

	/**
	 * @brief Creates a procedure in the AIMMS model.
	 * @param name Name of the procedure.
	 * @return Handle to the created procedure.
	 */
	std::pair<int, std::vector<int>> create_procedure_handle(const std::wstring& name);

	/**
	 * @brief Runs a procedure in the AIMMS model.
	 * @param procedure_handle Handle to the procedure.
	 * @return Result of the procedure execution.
	 */
	int run_procedure(const std::wstring& name, pybind11::kwargs& args);

	/**
	 * @brief Creates an identifier in the AIMMS model.
	 * @param name Name of the identifier.
	 * @return Handle to the created identifier.
	 */
	int create_identifier_handle(const std::wstring& name);

	/**
	 * @brief Resets an identifier to its default state.
	 * @param identifier_handle Identifier handle.
	 */
	void reset_identifier(int identifier_handle);

	/**
	 * @brief Retrieves the type of an identifier.
	 * @param identifier_handle Identifier handle.
	 * @return Type of the identifier.
	 */
	int identifier_storage_type(int identifier_handle);

	/**
	 * @brief Retrieves the type of an identifier.
	 * @param identifier_handle Identifier handle.
	 * @return Type of the identifier.
	 */
	int get_identifier_type(int identifier_handle);

	/**
	 * @brief Retrieves the flags of an identifier.
	 * @param meh Identifier handle.
	 * @return Flags of the identifier.
	 */
	int get_identifier_flags(int meh);

	/**
	 * @brief Deletes an identifier handle.
	 * @param identifier_handle Identifier handle.
	 */
	void delete_handle(int identifier_handle);

	/**
	 * @brief Deletes a procedure handle.
	 * @param procedure_handle Procedure handle.
	 */
	void delete_handle_procedure(int procedure_handle);

	/**
	 * @brief Checks if an identifier is empty.
	 * @param identifier_handle Identifier handle.
	 */
	void identifier_empty(int identifier_handle);

	/**
	 * @brief Adds a value to an identifier.
	 * @param meh Identifier handle.
	 * @param tuple Tuple representing the value's indices.
	 * @param value Value to add.
	 * @param update Flag to update the value if it already exists.
	 */
	void add_value(const std::wstring& current_identifier_name, std::vector<int>& tuple, std::variant<std::wstring, double, int> value, pybind11::dict& options);

	/**
	 * @brief Retrieves a value from an identifier.
	 * @param meh Identifier handle.
	 * @param tuple Tuple representing the value's indices.
	 * @return Retrieved value.
	 */
	 std::variant<std::wstring, double, int> get_value(const std::wstring& current_identifier_name, std::vector<int>& tuple);

	/**
	 * @brief Adds multiple values to an identifier.
	 * @param meh Identifier handle.
	 * @param index_domain_names Names of the index domains.
	 * @param data Dictionary of values to add.
	 * @param update Flag to update the values if they already exist.
	 */
	void add_values(const std::wstring& current_identifier_name, pybind11::dict& data, pybind11::dict& options);

	/**
	 * @brief Adds multiple values to an identifier using an Arrow table.
	 * @param meh Identifier handle.
	 * @param index_domain_names Names of the index domains.
	 * @param data Arrow table of values to add.
	 * @param update Flag to update the values if they already exist.
	 */

	void copyDataframeToAimms(const pybind11::object& data, const pybind11::dict& mapping, const pybind11::dict& options);
	pybind11::object copyAimmsToDataframe(const pybind11::list &identifierList, const pybind11::dict& mapping, const pybind11::dict& options);
	pybind11::dict copyDataFrametoDict(const std::wstring& current_identifier_name,const pybind11::object& data, const pybind11::dict& mapping, const pybind11::dict& options);
	pybind11::object copyDictToDataFrame(const std::wstring& current_identifier_name, const pybind11::dict& data, const pybind11::dict& mapping, const pybind11::dict& options);

	void multi_add_values_dataframe_arrow(const pybind11::object& data, pybind11::dict& options);

	/**
	 * @brief Adds multiple values to an identifier.
	 * @param meh Identifier handle.
	 * @param index_domain_names Names of the index domains.
	 * @param data Arrow table of values to add.
	 * @param update Flag to update the values if they already exist.
	 */
	void add_values_dataframe_arrow(const std::wstring& current_identifier_name, const pybind11::object& data, pybind11::dict& options);

	/**
	 * @brief Retrieves multiple values from an identifier.
	 * @param handle Identifier handle.
	 * @param root_set_names List of root set names.
	 * @return Dictionary of retrieved values.
	 */
	pybind11::dict get_values(const std::wstring& current_identifier_name);

	/**
	 * @brief Retrieves multiple values from an identifier as an Arrow table.
	 * @param handle Identifier handle.
	 * @param root_set_names List of root set names.
	 * @return Arrow table of retrieved values.
	 */
	pybind11::object get_values_dataframe_arrow(
		const std::wstring& current_identifier_name, const std::vector<std::wstring>& column_mapping
	);

	/**
	 * @brief Adds values to a set.
	 * @param meh Set handle.
	 * @param data Set of values to add.
	 * @return Vector of element numbers.
	 */
	std::vector<int> add_set_values(const std::wstring& current_identifier_name, const std::vector<std::wstring>& data);

	/**
	 * @brief Retrieves values from a set.
	 * @param meh Set handle.
	 * @return Set of retrieved values.
	 */
	pybind11::list get_set_values(const std::wstring& current_identifier_name);

	/**
	 * @brief Retrieves the number of a set element.
	 * @param meh Set handle.
	 * @param name Name of the set element.
	 * @return Number of the set element.
	 */
	int get_setelement_number(int meh, const std::wstring& name);

	/**
	 * @brief Retrieves the next identifier and its value.
	 * @param meh Identifier handle.
	 * @return Tuple containing the indices and the value.
	 */
	std::tuple<std::vector<int>, aimmsifc::AimmsValueType<wchar_t>> next_identifier(int meh);

	std::vector<int> get_domain_handles(int data_handle, auto&& domain_function) {
		int dimension{};
		int sliced{};
		auto ret = aimms->AttributeDimension(data_handle, &dimension, &sliced);
		handle_error(ret);

		if (dimension == 0) {
			return std::vector<int>{};
		}

		std::vector<int> domain(dimension, 0);
		ret = domain_function(data_handle, domain.data());
		handle_error(ret);
		data_handles_count += dimension;
		return domain;
	}

	std::vector<std::wstring> get_domain_names(const std::vector<int>& domain) {
		std::vector<std::wstring> domain_names;
		domain_names.reserve(domain.size());
		for (const auto& domain_handle : domain) {
			domain_names.emplace_back(get_identifier_name(domain_handle));
		}

		for (const auto& domain_handle : domain) {
			delete_handle(domain_handle);
		}

		return domain_names;
	}

	auto get_declaration_domain(int data_handle) {
		return get_domain_names(get_domain_handles(data_handle, [this](int data_handle, int* domain) {
			return aimms->AttributeDeclarationDomain(data_handle, domain);
		}));
	}

	/**
	 * @brief Retrieves the exposed identifiers of a set.
	 * @param set_name Name of the set.
	 * @return Vector of exposed identifier names.
	 */
	std::vector<std::wstring> get_exposed_identifiers(const std::wstring& set_name);

	/**
	 * @brief Walks the AIMMS model recursively starting from a node.
	 * @param node Node handle.
	 * @param nodes Map to store the visited nodes.
	 */
	void walk_model_recursive(int node, auto& nodes);

	/**
	 * @brief Walks the entire AIMMS model.
	 * @param root Root node handle (default is 0).
	 * @return Map of all model identifiers.
	 */
	void walk_model(int root = 0);

	identifier_info& get_identifier_info(const std::wstring& name);

	static auto get_current_aimms_api() -> pybind11::object {
		return current_project;
	}

private:

	std::shared_ptr<aimmsifc::iAimmsW> aimms; ///< AIMMS interface.
	int aimms_project_handle{};				  ///< Handle to the AIMMS project.

	std::unordered_map<std::wstring, mappings, wstring_hash, std::equal_to<>> set_mappings; ///< Map of set mappings.
	std::unordered_map<std::wstring, identifier_info> all_model_identifiers_map;			///< Map of all model identifiers.

	void getSharedIndexDomain(const std::vector<std::wstring> &identifierNames, std::vector<std::wstring> &indexNames);
	void createColumnMapping(const std::vector<std::wstring> &identifierNames, std::vector<std::wstring> &indexNames, std::vector<class ColumnMapping> &colMap, std::vector<int> &indexMap, std::vector<int> &idMap);

	int data_handles_count		= 0; ///< Count of data handles.
	int procedure_handles_count = 0; ///< Count of project handles.
	bool m_with_index_restriction = false; ///< Flag to indicate if index restriction is used.
	bool aimms_in_the_lead = false; ///< Flag to indicate if AIMMS is in the lead.

	static inline pybind11::object current_project;

	/**
	 * @brief Handles errors returned by AIMMS functions.
	 * @param ret Return code from an AIMMS function.
	 */
	void handle_error(int ret);

	/**
	 * @brief Initializes the AIMMS interface.
	 * @param aimms_bin_path Path to the AIMMS binary.
	 */
	void init_aimms(const std::string& aimms_bin_path);

	/**
	 * @brief Opens an AIMMS project.
	 * @param command Command to open the project.
	 */
	void open_project(const std::wstring& command);

	/**
	 * @brief Closes the AIMMS project.
	 */
	void close_project();
};
