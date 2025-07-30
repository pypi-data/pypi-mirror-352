#include "aimms_api_py/set_mappings.hpp"

void mappings::add(int element_number, std::string& name) {
	name_to_element_number[name]		   = element_number;
	element_number_to_name[element_number] = name;
}

const int& mappings::get_element(const std::string_view& name) const {
	return name_to_element_number.find(name)->second;
}

const std::string& mappings::get_name(int element_number) const {
	return element_number_to_name.at(element_number);
}

std::string mappings::to_string() {
	std::string result;
	for (const auto& [name, element_number] : name_to_element_number) {
		result += name + " : " + std::to_string(element_number) + "\n";
	}
	return result;
}