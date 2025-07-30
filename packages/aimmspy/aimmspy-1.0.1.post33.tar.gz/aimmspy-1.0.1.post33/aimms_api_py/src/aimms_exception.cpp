#include "aimms_api_py/aimms_exception.hpp"

aimms_exception::aimms_exception(int error_code, const std::wstring& message)
	: m_error_code(error_code)
	, m_error_message(boost::locale::conv::utf_to_utf<char>(message)) {}

[[nodiscard]] int aimms_exception::error_code() const {
	return m_error_code;
}

[[nodiscard]] const char* aimms_exception::what() const noexcept {
	return m_error_message.c_str();
}
