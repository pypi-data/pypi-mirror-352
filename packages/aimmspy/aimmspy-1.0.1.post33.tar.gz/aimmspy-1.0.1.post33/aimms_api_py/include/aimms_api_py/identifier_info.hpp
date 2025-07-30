#pragma once

#include <string>
#include <vector>

/**
 * @struct identifier_info
 * @brief Represents metadata for an identifier in the AIMMS model.
 */
class identifier_info {
public:
	int me_handle{};							  ///< Handle to the model editing node.
	int data_handle = -1;						  ///< Handle to the data associated with the identifier.
	int me_type{};							      ///< Type of the identifier (e.g., parameter, variable, set).
	int aimms_type{};							  ///< AIMMS type of the identifier.
	int dimension{};							  ///< Dimension of the identifier.
	int flags{};								  ///< Flags associated with the identifier.
	int storage_type{};							  ///< Storage type of the identifier.
	int procedure_handle = -1;					  ///< Handle to the procedure associated with the identifier.
	std::vector<int> procedure_args_types;		  ///< Arguments of the procedure.
};
