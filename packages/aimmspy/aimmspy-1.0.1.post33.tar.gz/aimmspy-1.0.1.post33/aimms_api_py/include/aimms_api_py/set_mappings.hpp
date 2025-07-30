#pragma once

#include <functional>
#include <string>

#include "boost/unordered_map.hpp" // IWYU pragma: export

/**
 * @brief A hash function for strings.
 * @details A custom hash function to allow for transparent hashing of strings and string views. which skips the making of a copy.
 * @note This is used to allow for faster lookups in the unordered_map.
 */
struct string_hash {
	using is_transparent = void;

	[[nodiscard]] size_t operator()(const char* txt) const {
		return std::hash<std::string_view>{}(txt);
	}

	[[nodiscard]] size_t operator()(std::string_view txt) const {
		return std::hash<std::string_view>{}(txt);
	}

	[[nodiscard]] size_t operator()(const std::string& txt) const {
		return std::hash<std::string>{}(txt);
	}
};

struct wstring_hash {
	using is_transparent = void;

	[[nodiscard]] size_t operator()(const wchar_t* txt) const {
		return std::hash<std::wstring_view>{}(txt);
	}

	[[nodiscard]] size_t operator()(std::wstring_view txt) const {
		return std::hash<std::wstring_view>{}(txt);
	}

	[[nodiscard]] size_t operator()(const std::wstring& txt) const {
		return std::hash<std::wstring>{}(txt);
	}
};

/**
 * @class mappings
 * @brief A class to manage bidirectional mappings between element numbers and names.
 */
class mappings {

public:

	/**
	 * @brief Adds a mapping between an element number and a name.
	 * @param element_number The integer representing the element number.
	 * @param name The wide string representing the name.
	 */
	void add(int element_number, std::string& name);

	/**
	 * @brief Retrieves the element number corresponding to a given name.
	 * @param name The wide string representing the name.
	 * @return The integer representing the element number.
	 * @throws std::out_of_range if the name is not found.
	 */
	[[nodiscard]] const int& get_element(const std::string_view& name) const;

	/**
	 * @brief Retrieves the name corresponding to a given element number.
	 * @param element_number The integer representing the element number.
	 * @return The wide string representing the name.
	 * @throws std::out_of_range if the element number is not found.
	 */
	[[nodiscard]] const std::string& get_name(int element_number) const;

	/**
	 * @brief Converts the mappings to a string representation.
	 * @return A wide string representing all mappings.
	 */
	std::string to_string();

private:

	/**
	 * @brief A map from names to element numbers.
	 */
	std::unordered_map<std::string, int, string_hash, std::equal_to<>> name_to_element_number;

	/**
	 * @brief A map from element numbers to names.
	 */
	std::unordered_map<int, std::string> element_number_to_name;

}; // class mappings
