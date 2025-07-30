cmake_minimum_required(VERSION 3.16)

project (prodver)

find_package(Python3 COMPONENTS Interpreter)

if(DEFINED ENV{CONAN_BUILD})
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/include/ProductVersion/Version.h
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/generateProductVersion.py --template ${CMAKE_SOURCE_DIR}/buildhelpers/Version.template --result ${CMAKE_CURRENT_BINARY_DIR}/include/ProductVersion/Version.h --version ${CONAN_BUILD_VERSION}
    DEPENDS ${CMAKE_SOURCE_DIR}/buildhelpers/Version.template
  )
else()
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/include/ProductVersion/Version.h
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/generateProductVersion.py --template ${CMAKE_SOURCE_DIR}/buildhelpers/Version.template --result ${CMAKE_CURRENT_BINARY_DIR}/include/ProductVersion/Version.h
    DEPENDS ${CMAKE_SOURCE_DIR}/buildhelpers/Version.template
  )
endif()

add_library(${PROJECT_NAME} STATIC
            ${CMAKE_CURRENT_BINARY_DIR}/include/ProductVersion/Version.h
            src/Description.cpp
            src/Info.cpp
            )

set_property(TARGET prodver PROPERTY POSITION_INDEPENDENT_CODE ON)

target_include_directories(${PROJECT_NAME} 
        INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include
                  ${CMAKE_CURRENT_BINARY_DIR}/include
        PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include
                ${CMAKE_CURRENT_SOURCE_DIR}/include
)
