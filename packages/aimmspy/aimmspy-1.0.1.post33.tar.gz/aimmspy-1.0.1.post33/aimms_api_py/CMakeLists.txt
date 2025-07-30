#if not defined SKBUILD_PROJECT_NAME
if (NOT DEFINED SKBUILD_PROJECT_NAME)
    set(THE_PROJECT_NAME aimmspy)
    # pip install arrowpy
    execute_process(
        COMMAND ${Python_EXECUTABLE} -m pip install pyarrow natsort pandas polars
    )
else()
    set(THE_PROJECT_NAME ${SKBUILD_PROJECT_NAME})
endif()

project(${THE_PROJECT_NAME})

add_library(${PROJECT_NAME}_interface INTERFACE)

#disable optimization when compiling 'RelWithDebInfo' locally
if(NOT DEFINED ENV{CI})
	string(REPLACE "/O2" "/Od" CMAKE_CXX_FLAGS_RELWITHDEBINFO ${CMAKE_CXX_FLAGS_RELWITHDEBINFO})
endif()


execute_process(
	COMMAND ${Python_EXECUTABLE} ${CMAKE_SOURCE_DIR}/get_pyarrow_paths.py --path ${CMAKE_BINARY_DIR}
)

file(READ ${CMAKE_BINARY_DIR}/pyarrow_paths.json JSON_FILE)
string(JSON PYARROW_INCLUDE_DIR GET ${JSON_FILE} "includes")
string(JSON PYARROW_LIBRARIES GET ${JSON_FILE} "libraries")
string(JSON PYARROW_LIBRARIES_DIR GET ${JSON_FILE} "library_dirs")
string(JSON TO_COPY_LIST GET ${JSON_FILE} "to_copy_list")

string(REPLACE "@" ";" PYARROW_LIBRARIES ${PYARROW_LIBRARIES})
string(REPLACE "@" ";" PYARROW_LIBRARIES_DIR ${PYARROW_LIBRARIES_DIR})
string(REPLACE "@" ";" TO_COPY_LIST ${TO_COPY_LIST})
string(REPLACE "@" ";" PYARROW_INCLUDE_DIR ${PYARROW_INCLUDE_DIR})

message(STATUS "PYARROW_INCLUDE_DIR: ${PYARROW_INCLUDE_DIR}")
message(STATUS "PYARROW_LIBRARIES_DIR: ${PYARROW_LIBRARIES_DIR}")
message(STATUS "PYARROW_LIBRARIES: ${PYARROW_LIBRARIES}")
message(STATUS "TO_COPY_LIST: ${TO_COPY_LIST}")

target_include_directories( ${PROJECT_NAME}_interface
    INTERFACE  
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        # ${PYARROW_INCLUDE_DIR}
        )

foreach(LIBRARY_DIR ${PYARROW_LIBRARIES_DIR})
    target_link_directories(${PROJECT_NAME}_interface
        INTERFACE
            ${LIBRARY_DIR}
    )
endforeach()

target_link_libraries(${PROJECT_NAME}_interface
    INTERFACE
        aimmsifc::aimmsifc
        pybind11::headers
        boost::boost
        aimms-api-wrapper
        arrow4cxx

        prodver
        $<$<PLATFORM_ID:Linux>:
            dl
            m
            pthread
        >
)

target_compile_definitions(${PROJECT_NAME}_interface
    INTERFACE
        _SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING
        $<$<PLATFORM_ID:Windows>:
            NOMINMAX
            WIN32_LEAN_AND_MEAN
            WINDOWS
        >
        $<$<PLATFORM_ID:Linux>:
            LINUX
        >
        VERSION_INFO=${PROJECT_VERSION}
)

target_compile_features(${PROJECT_NAME}_interface
    INTERFACE
        cxx_std_20
)

set_property(TARGET ${PROJECT_NAME}_interface PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)

pybind11_add_module(${PROJECT_NAME}
    src/aimms_api.cpp
    src/set_mappings.cpp
    src/aimms_exception.cpp
    src/python_module.cpp
)

target_link_libraries(${PROJECT_NAME}
    PUBLIC
        ${PROJECT_NAME}_interface
)

if ( DEFINED SKBUILD_PROJECT_NAME)
    install(
        TARGETS
            ${PROJECT_NAME}
        RUNTIME           # Following options apply to runtime artifacts.
            COMPONENT Runtime
        LIBRARY           # Following options apply to library artifacts.
            COMPONENT Runtime
            DESTINATION .
    )
    
    install(
        DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/python/aimms
        DESTINATION .
    )
else()

    aimms_install(
        NAME
            ${PROJECT_NAME}
        AUXILARY_DIRS
            ${CMAKE_CURRENT_SOURCE_DIR}/python/aimms
    )
endif()

#copy the target file to the cmake source directory
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${PROJECT_NAME}> ${CMAKE_CURRENT_SOURCE_DIR}/python
)

# on windows also copy the pdb file
if(WIN32)
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_PDB_FILE:${PROJECT_NAME}> ${CMAKE_CURRENT_SOURCE_DIR}/python
    )
endif()
