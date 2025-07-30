project(aimms-api-wrapper)

# Create a library from the source files
add_library(${PROJECT_NAME} INTERFACE)

target_compile_definitions( ${PROJECT_NAME} 
    INTERFACE
        UNICODE
        _UNICODE
        SA_UNICODE
        RAPIDJSON_HAS_STDSTRING=1
        RAPIDJSON_HAS_CXX11_RVALUE_REFS=1
        BOOST_CONFIG_SUPPRESS_OUTDATED_MESSAGE
        _SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING
        SHA2_USE_INTTYPES_H
        _CRT_SECURE_NO_WARNINGS
        CMAKE_CONAN_BUILD=1
        INCLUDE_STRING_CONVERT
        PUGIXML_WCHAR_MODE
        $<$<CONFIG:Release>:
            NDEBUG
        >
        $<$<CONFIG:Debug>:
            DEBUG
            _DEBUG
        >
        $<$<PLATFORM_ID:Windows>:WIN32
            _WINDOWS
            _USRDLL
            WIN32_LEAN_AND_MEAN
            NOMINMAX
            _DISABLE_CONSTEXPR_MUTEX_CONSTRUCTOR
        >
        $<$<PLATFORM_ID:Linux>:
            GCC_HASCLASSVISIBILITY
        >
)

target_include_directories(${PROJECT_NAME} INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/include 
)

target_compile_features(${PROJECT_NAME}
    INTERFACE
        cxx_std_20
)