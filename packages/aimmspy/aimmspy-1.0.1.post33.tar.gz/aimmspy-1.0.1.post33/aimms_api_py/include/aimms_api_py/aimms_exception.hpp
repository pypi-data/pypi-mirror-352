#pragma once

#include <exception>
#include <string>

#include <boost/locale.hpp>
#include <boost/locale/encoding_utf.hpp>

/**
 * @class aimms_exception
 * @brief Represents an exception thrown by the AIMMS API.
 */
class aimms_exception : public std::exception {
public:

	/**
	 * @brief Constructs an aimms_exception object.
	 * @param error_code The error code returned by the AIMMS API.
	 * @param message The error message associated with the exception.
	 */
	aimms_exception(int error_code, const std::wstring& message);

	/**
	 * @brief Retrieves the error code associated with the exception.
	 * @return The error code.
	 */
	[[nodiscard]] int error_code() const;

	/**
	 * @brief Retrieves the error message associated with the exception.
	 * @return A C-style string containing the error message.
	 */
	[[nodiscard]] const char* what() const noexcept override;

private:

	int m_error_code;			 ///< The error code returned by the AIMMS API.
	std::string m_error_message; ///< The error message in UTF-8 format.
};