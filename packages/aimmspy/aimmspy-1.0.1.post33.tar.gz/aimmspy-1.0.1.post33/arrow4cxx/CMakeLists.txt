project(arrow4cxx)

execute_process(
	COMMAND ${Python_EXECUTABLE} ${CMAKE_SOURCE_DIR}/get_pyarrow_paths.py --path ${CMAKE_BINARY_DIR}
)

file(READ ${CMAKE_BINARY_DIR}/pyarrow_paths.json JSON_FILE)
string(JSON PYARROW_INCLUDE_DIR GET ${JSON_FILE} "includes")
string(JSON PYARROW_LIBRARIES GET ${JSON_FILE} "libraries")
string(JSON PYARROW_LIBRARIES_DIR GET ${JSON_FILE} "library_dirs")
string(JSON TO_COPY_LIST GET ${JSON_FILE} "to_copy_list")

string(REPLACE "@" ";" PYARROW_LIBRARIES ${PYARROW_LIBRARIES})
string(REPLACE "@" ";" TO_COPY_LIST ${TO_COPY_LIST})
string(REPLACE "@" ";" PYARROW_INCLUDE_DIR ${PYARROW_INCLUDE_DIR})

message(STATUS "PYARROW_INCLUDE_DIR: ${PYARROW_INCLUDE_DIR}")
message(STATUS "PYARROW_LIBRARIES_DIR: ${PYARROW_LIBRARIES_DIR}")
message(STATUS "PYARROW_LIBRARIES: ${PYARROW_LIBRARIES}")
message(STATUS "TO_COPY_LIST: ${TO_COPY_LIST}")

# Create a library from the source files
add_library(${PROJECT_NAME} STATIC
    src/ArrowTable.cpp
    src/Exception.cpp
)

target_link_directories( ${PROJECT_NAME}
    PUBLIC
        ${PYARROW_LIBRARIES_DIR}
)

foreach(LIBRARY ${PYARROW_LIBRARIES})
    target_link_libraries(${PROJECT_NAME}
        PUBLIC
        ${LIBRARY}
        )
        endforeach()
        
target_include_directories( ${PROJECT_NAME}
    PUBLIC  
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        ${PYARROW_INCLUDE_DIR}
    )



target_include_directories(${PROJECT_NAME} PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_features(${PROJECT_NAME}
    PUBLIC
        cxx_std_20
)
