cmake_minimum_required(VERSION ${MINIMUM_CMAKE_VERSION})

project (toplevel)

if (WIN32)
	string (REPLACE "/Ob1" "/Ob2 " CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO}")
endif()

find_package(Python REQUIRED COMPONENTS Interpreter Development)

include(buildhelpers/cmake/aimms_conan.cmake)

git_and_cmake_info()

if( DEFINED CONAN_UPLOAD)
	upload_conan_package("aimms_api_py" ${CMAKE_SOURCE_DIR}/conanfile.py)
else()

	conan2_install(
		CONANFILE
			${CMAKE_SOURCE_DIR}/conanfile.py
		AUTO_FIND_PACKAGES
	)

	enable_testing()
	add_subdirectory(buildhelpers/cmake/prodver)
	add_subdirectory(aimms_api_py)
	add_subdirectory(aimms-api-wrapper)
	add_subdirectory(arrow4cxx)

	# if(NOT DEFINED ENV{CI})
    # 	find_package(Doxygen)
	# 	if(DOXYGEN_FOUND)
	# 		include(FetchContent)
	# 		FetchContent_Declare(
	# 			doxygen-awesome-css
	# 			URL https://github.com/jothepro/doxygen-awesome-css/archive/refs/heads/main.zip
	# 		)
	# 		FetchContent_MakeAvailable(doxygen-awesome-css)
	# 		FetchContent_GetProperties(doxygen-awesome-css SOURCE_DIR AWESOME_CSS_DIR)

	# 		set(DOXYFILE_IN ${CMAKE_SOURCE_DIR}/doxyfile.in)
	# 		set(DOXYFILE_OUT ${CMAKE_BINARY_DIR}/doxyfile)
	# 		configure_file(${DOXYFILE_IN} ${DOXYFILE_OUT} @ONLY)

	# 		# Add a custom target to run Doxygen when ever the project is built
	# 		add_custom_target( doc_doxygen ALL
	# 			COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYFILE_OUT}
	# 			WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
	# 			COMMENT "Generating API documentation with Doxygen"
	# 		)

	# 	endif()
	# endif()

endif()
