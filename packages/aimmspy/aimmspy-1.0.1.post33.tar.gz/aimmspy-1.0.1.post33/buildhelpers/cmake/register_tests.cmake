
include(CMakeParseArguments)
include(GoogleTest)

# if cmake above 3.27 skip this
if (${CMAKE_VERSION} VERSION_LESS "3.27.0")
	include(Dart)
endif()
include(CTest)
#functions to create a gtest executable and register it 

function(set_test name GTEST_FILTER NO_MEMORY_LEAK_CHECK TEST_LIBRARY_NAME TEST_TIMEOUT APPEND_PATHS)

	# The pipeline expects gtest.xml and cppunit.xml to be present in the out directory, even if cppunit/gtest is not used
	file(TOUCH ${CMAKE_SOURCE_DIR}/out/gtest.xml ${CMAKE_SOURCE_DIR}/out/cppunit.xml)

	# enviroment path for windows replace all ; with $<SEMICOLON>
	foreach( CONFIG ${CMAKE_CONFIGURATION_TYPES} )

		if( NOT NO_MEMORY_LEAK_CHECK AND NOT WIN32 )
			add_test(NAME ${name}_${CONFIG}
				COMMAND valgrind --leak-check=full --vgdb=no --gen-suppressions=all --quiet --error-exitcode=1 --error-markers="VALGRIND PROBLEM DETECTED","----------------------------------------------------------" --suppressions=${CMAKE_SOURCE_DIR}/buildhelpers/cmake/valgrind-suppressions.supp ./${name} --gtest_filter=${GTEST_FILTER} --gtest_output=xml:${CMAKE_SOURCE_DIR}/out/${TEST_LIBRARY_NAME}.xml
				WORKING_DIRECTORY $<TARGET_FILE_DIR:${name}>
				CONFIGURATIONS ${CONFIG}
			)

			set_tests_properties(${name}_${CONFIG}
				PROPERTIES	
					FAIL_REGULAR_EXPRESSION "VALGRIND PROBLEM DETECTED"
			)
		else()
			add_test(NAME ${name}_${CONFIG}
				COMMAND ${name} --gtest_filter=${GTEST_FILTER} --gtest_output=xml:${CMAKE_SOURCE_DIR}/out/${TEST_LIBRARY_NAME}.xml
				WORKING_DIRECTORY $<TARGET_FILE_DIR:${name}>
				CONFIGURATIONS ${CONFIG}
			)
		endif()

		if ( ${TEST_TIMEOUT} GREATER 0 )
			set_tests_properties(${name}_${CONFIG}
				PROPERTIES
					TIMEOUT ${TEST_TIMEOUT}
			)
		endif()

		if(WIN32)

			# this will set the enviroment path for windows which uses variables set by conan2_install
			string(REPLACE ";" "\\$<SEMICOLON>" PACKAGE_BINARY_DIRS_${CONFIG}_temp "${PACKAGE_BINARY_DIRS_${CONFIG}}")

			string(REPLACE ";;" "" env_temp "$ENV{PATH}")
			string(REPLACE ";" "\\$<SEMICOLON>" env_temp "${env_temp}")

			if(NOT "${APPEND_PATHS}" MATCHES " ")
				foreach(target IN LISTS APPEND_PATHS)
					list(APPEND GENERATOR_EXPRESSIONS "$<TARGET_FILE_DIR:${target}>")
				endforeach()

				# change all ; to $<SEMICOLON> in generator expressions
				string(REPLACE ";" "\\$<SEMICOLON>" GENERATOR_EXPRESSIONS_PATH_STRING "${GENERATOR_EXPRESSIONS}")
			
				add_custom_command(
					TARGET ${name} POST_BUILD
					COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/cmake/testmate_path.py --paths "${GENERATOR_EXPRESSIONS}" --file ${CMAKE_SOURCE_DIR}/out/envfile_${CONFIG}.json --config ${CONFIG}
				)
			endif()
			
			set_tests_properties(${name}_${CONFIG}
				PROPERTIES
					ENVIRONMENT "PATH=${env_temp}\\$<SEMICOLON>${PACKAGE_BINARY_DIRS_${CONFIG}_temp}\\$<SEMICOLON>${GENERATOR_EXPRESSIONS_PATH_STRING}"
			)
			
			unset(GENERATOR_EXPRESSIONS)
		endif()

		if(UNIX)
			if(NOT "${APPEND_PATHS}" MATCHES " ")
				foreach(target IN LISTS APPEND_PATHS)
					list(APPEND GENERATOR_EXPRESSIONS "$<TARGET_FILE_DIR:${target}>")
				endforeach()

				# change all ; to $<SEMICOLON> in generator expressions
				string(REPLACE ";" ":" GENERATOR_EXPRESSIONS_PATH_STRING "${GENERATOR_EXPRESSIONS}")
				string(REPLACE " " ":" GENERATOR_EXPRESSIONS_PATH_STRING "${GENERATOR_EXPRESSIONS_PATH_STRING}")
			
				add_custom_command(
					TARGET ${name} POST_BUILD
					COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/cmake/testmate_path.py --paths \"${GENERATOR_EXPRESSIONS_PATH_STRING}\" --file \"${CMAKE_SOURCE_DIR}/out/envfile_${CONFIG}.json\" --config \"${CONFIG}\"
				)
			endif()

			string(REPLACE ";" ":" PACKAGE_BINARY_DIRS_${CONFIG}_temp "${PACKAGE_BINARY_DIRS_${CONFIG}}")

			#[[
				We have to set the timezone for the engine because some unit tests use this to properly calculate the time.
			]]

			set_tests_properties(${name}_${CONFIG}
				PROPERTIES
					ENVIRONMENT "LD_LIBRARY_PATH=${PACKAGE_BINARY_DIRS_${CONFIG}_temp}:${GENERATOR_EXPRESSIONS_PATH_STRING}:$ENV{LD_LIBRARY_PATH};TZ=Europe/Amsterdam"
			)
		endif()

	endforeach()

endfunction(set_test )

#[[ 
	# a function to create a gtest executable and register it 
	# name: name of the executable
]]
function ( register_gtest)
	set(options NO_MEMORY_LEAK_CHECK INTEGRATION NEW_INTEGRATION)
	set(oneValueArgs NAME GTEST_FILTER TIMEOUT)
	set(multiValueArgs LINKS SOURCES APPEND_PATHS COPY_FILES)
	cmake_parse_arguments(REGISTER_GTEST "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

	# if ENV{CONAN_BUILD} is set we skip
	if(DEFINED ENV{ENV{CONAN_BUILD}})
		message(STATUS "Skipping gtest registration because ENV{CONAN_BUILD} is set")
		return()
	endif()

	if( NOT REGISTER_GTEST_INTEGRATION )
		set(NAME_EXTRAS "_unittests")
	else()
		set(NAME_EXTRAS "_integrationtests")
	endif()

	#if target not exists create it
	if (NOT TARGET ${REGISTER_GTEST_NAME}${NAME_EXTRAS})
		add_executable( ${REGISTER_GTEST_NAME}${NAME_EXTRAS}
			$<IF:$<BOOL:${REGISTER_GTEST_SOURCES}>,
				${REGISTER_GTEST_SOURCES},
				${CMAKE_CURRENT_SOURCE_DIR}/gtest/gtests.cpp
			>
		)

		target_link_libraries( ${REGISTER_GTEST_NAME}${NAME_EXTRAS}
			PRIVATE
				gtest::gtest
				${REGISTER_GTEST_LINKS}
		)

		target_compile_definitions( ${REGISTER_GTEST_NAME}${NAME_EXTRAS}
			PRIVATE
				PROJECT_ROOT_DIR="${CMAKE_SOURCE_DIR}"
				#  _DISABLE_VECTOR_ANNOTATION
		)
		
		# if(WIN32)
		# 	# Does it help to compile the unit tests specific files without the /GL flag? Does it decrease linking time?
		# 	target_compile_options( ${REGISTER_GTEST_NAME}${NAME_EXTRAS}
		# 		PRIVATE 
		# 			/GL-
		# 	)
		# endif()

		target_link_options( ${REGISTER_GTEST_NAME}${NAME_EXTRAS}
			PRIVATE
				$<$<CXX_COMPILER_ID:MSVC>:/ignore:4099>
		)

		# turn of link time optimization
		set_target_properties(${REGISTER_GTEST_NAME}${NAME_EXTRAS} PROPERTIES INTERPROCEDURAL_OPTIMIZATION FALSE)
		
		# copy files to the build directory
		foreach( COPY_FILE ${REGISTER_GTEST_COPY_FILES} )
			add_custom_command(TARGET ${REGISTER_GTEST_NAME}${NAME_EXTRAS} POST_BUILD 
				COMMAND ${CMAKE_COMMAND} -E copy ${COPY_FILE} $<TARGET_FILE_DIR:${REGISTER_GTEST_NAME}${NAME_EXTRAS}>
			)
		endforeach()

		if (NOT DEFINED REGISTER_GTEST_APPEND_PATHS)
			set(REGISTER_GTEST_APPEND_PATHS " ")
		endif()

		if (NOT DEFINED REGISTER_GTEST_GTEST_FILTER)
			set(REGISTER_GTEST_GTEST_FILTER "*")
		endif()

		if (NOT DEFINED REGISTER_GTEST_TIMEOUT)
			set(REGISTER_GTEST_TIMEOUT 0)
		endif()

		if( NOT REGISTER_GTEST_NEW_INTEGRATION )
			set_test(${REGISTER_GTEST_NAME}${NAME_EXTRAS} ${REGISTER_GTEST_GTEST_FILTER} ${REGISTER_GTEST_NO_MEMORY_LEAK_CHECK} gtest ${REGISTER_GTEST_TIMEOUT} "${REGISTER_GTEST_APPEND_PATHS}" ${REGISTER_GTEST_APPEND_PATH_EXTRA})
		else()
			# copy files to ${CMAKE_SOURCE_DIR}/out/upload/${PRESET_NAME}/${CONFIG}/integrationtests/
			string(REGEX MATCH "[^/]+$" PRESET_NAME ${CMAKE_BINARY_DIR})
			# post build command to copy the file to the integrationtests folder
			# file 

			add_custom_command(TARGET ${REGISTER_GTEST_NAME}${NAME_EXTRAS} POST_BUILD 
				COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${REGISTER_GTEST_NAME}${NAME_EXTRAS}> ${CMAKE_SOURCE_DIR}/out/upload/${PRESET_NAME}/$<CONFIG>/integrationtests/${REGISTER_GTEST_NAME}${NAME_EXTRAS}$<$<PLATFORM_ID:Windows>:.exe>
			)

			# also on windows copy .pdb and on linux the .debug file
			if(WIN32)
				add_custom_command(TARGET ${REGISTER_GTEST_NAME}${NAME_EXTRAS} POST_BUILD 
					COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_PDB_FILE:${REGISTER_GTEST_NAME}${NAME_EXTRAS}> ${CMAKE_SOURCE_DIR}/out/upload/${PRESET_NAME}/$<CONFIG>/integrationtests/${REGISTER_GTEST_NAME}${NAME_EXTRAS}.pdb
				)
			endif()

		endif()
	else()
		target_sources( ${REGISTER_GTEST_NAME}${NAME_EXTRAS}
			PRIVATE
				$<IF:$<BOOL:${REGISTER_GTEST_SOURCES}>,
					${REGISTER_GTEST_SOURCES},
					${CMAKE_CURRENT_SOURCE_DIR}/gtest/gtests.cpp
				>
		)

		target_link_libraries( ${REGISTER_GTEST_NAME}${NAME_EXTRAS}
			PRIVATE
				gtest::gtest
				${REGISTER_GTEST_LINKS}
		)
	endif()

endfunction(register_gtest)

#[[ 
	# a function to create a cppunit with gtest_injector executable and register it 
	# name: name of the executable
]]
function ( register_cppunit)
	set(options NO_MEMORY_LEAK_CHECK)	
	set(oneValueArgs NAME GTEST_FILTER TIMEOUT)
	set(multiValueArgs LINKS SOURCES APPEND_PATHS COPY_FILES)
	cmake_parse_arguments(REGISTER_CPPUNIT "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

	# if ENV{CONAN_BUILD} is set we skip
	if(DEFINED ENV{CONAN_BUILD})
		message(STATUS "Skipping gtest registration because ENV{CONAN_BUILD} is set")
		return()
	endif()

	if (NOT TARGET ${REGISTER_CPPUNIT_NAME}_unittests)
		add_executable(${REGISTER_CPPUNIT_NAME}_unittests
			# $<IF:$<BOOL:${REGISTER_CPPUNIT_SOURCES}>,
				${REGISTER_CPPUNIT_SOURCES}
				${CMAKE_CURRENT_SOURCE_DIR}/cppunit/cppunit.cpp
			# >
		)

		target_link_libraries( ${REGISTER_CPPUNIT_NAME}_unittests
			PRIVATE
				gtest_injector::gtest_injector
				${REGISTER_CPPUNIT_LINKS}
		)

		target_compile_definitions( ${REGISTER_CPPUNIT_NAME}_unittests
			PRIVATE
				PROJECT_ROOT_DIR="${CMAKE_SOURCE_DIR}"
				# _DISABLE_VECTOR_ANNOTATION
		)

		# if(WIN32)
		# 	# Does it help to compile the unit tests specific files without the /GL flag? Does it decrease linking time?
		# 	target_compile_options( ${REGISTER_CPPUNIT_NAME}_unittests
		# 		PRIVATE 
		# 			/GL-
		# 	)
		# endif()
		
		target_link_options( ${REGISTER_CPPUNIT_NAME}_unittests
			PRIVATE
				$<$<CXX_COMPILER_ID:MSVC>:/ignore:4099>
		)

		# turn of link time optimization
		set_target_properties(${REGISTER_CPPUNIT_NAME}_unittests PROPERTIES INTERPROCEDURAL_OPTIMIZATION FALSE)

		# copy files to the build directory
		foreach( COPY_FILE ${REGISTER_CPPUNIT_COPY_FILES} )
			add_custom_command(TARGET ${REGISTER_CPPUNIT_NAME}_unittests POST_BUILD 
				COMMAND ${CMAKE_COMMAND} -E copy ${COPY_FILE} $<TARGET_FILE_DIR:${REGISTER_CPPUNIT_NAME}_unittests>
			)
		endforeach()

		if (NOT DEFINED REGISTER_CPPUNIT_APPEND_PATHS)
			set(REGISTER_CPPUNIT_APPEND_PATHS " ")
		endif()

		if (NOT DEFINED REGISTER_CPPUNIT_GTEST_FILTER)
			set(REGISTER_CPPUNIT_GTEST_FILTER "*")
		endif()

		if (NOT DEFINED REGISTER_CPPUNIT_TIMEOUT)
			set(REGISTER_CPPUNIT_TIMEOUT 0)
		endif()

		set_test(${REGISTER_CPPUNIT_NAME}_unittests ${REGISTER_CPPUNIT_GTEST_FILTER} ${REGISTER_CPPUNIT_NO_MEMORY_LEAK_CHECK} cppunit ${REGISTER_CPPUNIT_TIMEOUT} "${REGISTER_CPPUNIT_APPEND_PATHS}" ${REGISTER_CPPUNIT_APPEND_PATH_EXTRA})

	else()
		target_sources( ${REGISTER_CPPUNIT_NAME}_unittests
			PRIVATE
			# $<IF:$<BOOL:${REGISTER_CPPUNIT_SOURCES}>,
				${REGISTER_CPPUNIT_SOURCES}
				${CMAKE_CURRENT_SOURCE_DIR}/cppunit/cppunit.cpp
			# >
		)

		target_link_libraries( ${REGISTER_CPPUNIT_NAME}_unittests
			PRIVATE
				gtest_injector::gtest_injector
				${REGISTER_CPPUNIT_LINKS}
		)
	endif()

endfunction(register_cppunit)


function(register_aimmsunit)

	set(options NO_DEBUG LOCAL_TEST_ENV IS_PURE_AIMMS IS_SFX)
	set(oneValueArgs PLUGIN_PATH PLUGIN_TEST_PATH NAME ARCHITECTURE BRANCH AUTOLIB_NAME)
	set(multiValueArgs VERSIONS REPOSITORY_LIBRARIES EXTRA_ARGS)
	cmake_parse_arguments(REGISTER_AIMMSUNIT "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

    message("AIMMS_PLUGIN_PATH " ${REGISTER_AIMMSUNIT_PLUGIN_PATH})
    message("AIMMS_PLUGIN_TEST_PATH " ${REGISTER_AIMMSUNIT_PLUGIN_TEST_PATH})
    message("CMAKE_BINARY_DIR: ${CMAKE_BINARY_DIR}")

    # get last part of binary dir 
    string(REGEX MATCH "[^/]+$" PRESET_NAME ${CMAKE_BINARY_DIR})
    message("LIBREPO_AIMMS_TESTPROJECT: ${PRESET_NAME}")

	if (REGISTER_AIMMSUNIT_IS_PURE_AIMMS)
		foreach(CONFIG ${CMAKE_CONFIGURATION_TYPES})
			file(COPY ${REGISTER_AIMMSUNIT_PLUGIN_PATH}/ DESTINATION ${CMAKE_SOURCE_DIR}/out/upload/${PRESET_NAME}/${CONFIG}/${REGISTER_AIMMSUNIT_AUTOLIB_NAME}/)
		endforeach()
	else()
		# copy lib project (note: also makes the dll folder where deps are installed by conan)
		add_custom_command(TARGET ${REGISTER_AIMMSUNIT_NAME} POST_BUILD 
			COMMAND ${CMAKE_COMMAND} -E copy_directory ${REGISTER_AIMMSUNIT_PLUGIN_PATH} ${CMAKE_SOURCE_DIR}/out/upload/${PRESET_NAME}/$<CONFIG>/${REGISTER_AIMMSUNIT_AUTOLIB_NAME}/
		)

		find_package(Python3 COMPONENTS Interpreter)

		add_custom_command(TARGET ${REGISTER_AIMMSUNIT_NAME} POST_BUILD
			COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/autolibs/release_and_publisher.py deploybinaries ${PRESET_NAME} $<CONFIG>
			WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
		)

	endif()

	foreach( CONFIG ${CMAKE_CONFIGURATION_TYPES} )
		install(
			DIRECTORY 
				${CMAKE_SOURCE_DIR}/out/upload/${PRESET_NAME}/${CONFIG}/${REGISTER_AIMMSUNIT_AUTOLIB_NAME}/
			CONFIGURATIONS
				${CONFIG}
			DESTINATION
				${CONFIG}
		)
	endforeach()
	
	if(NOT DEFINED ENV{CI})

		# run python3 buildhelpers/autolibs/autolib_collector.py
		
		add_custom_command(TARGET ${REGISTER_AIMMSUNIT_NAME} POST_BUILD
			COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/autolibs/autolib_collector.py --cmake_preset ${PRESET_NAME} --cmake_build_type $<CONFIG> --quiet --cmake
			WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
		)

		#to get aimms version
		add_custom_command(TARGET ${REGISTER_AIMMSUNIT_NAME} POST_BUILD
			COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/autolibs/aimms_unit_tests2.py --cmake_preset ${PRESET_NAME} --cmake_build_type $<CONFIG> --dry --branch ${REGISTER_AIMMSUNIT_BRANCH} --version ${REGISTER_AIMMSUNIT_VERSIONS}
			WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
		)

		add_custom_command(TARGET ${REGISTER_AIMMSUNIT_NAME} POST_BUILD
			COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/autolibs/release_and_publisher.py createlib
			WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
		)
		
		foreach(CONFIG ${CMAKE_CONFIGURATION_TYPES})
			add_test(NAME ${REGISTER_AIMMSUNIT_NAME}_aimmsunit_tests_${CONFIG}
				COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/autolibs/aimms_unit_tests2.py --cmake_preset ${PRESET_NAME} --cmake_build_type ${CONFIG} --branch ${REGISTER_AIMMSUNIT_BRANCH} --version ${REGISTER_AIMMSUNIT_VERSIONS}
				WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
				CONFIGURATIONS ${CONFIG}
			)
		endforeach()
	endif()


	if(REGISTER_AIMMSUNIT_IS_SFX AND DEFINED ENV{CI})

		# pip install py7zr
		add_custom_command(TARGET ${REGISTER_AIMMSUNIT_NAME} POST_BUILD
			COMMAND pip install py7zr
			WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
		)

		add_custom_command(TARGET ${REGISTER_AIMMSUNIT_NAME} POST_BUILD
			COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/autolibs/autolib_collector.py --cmake_preset ${PRESET_NAME} --cmake_build_type $<CONFIG> --quiet --cmake
			WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
		)

		add_custom_command(TARGET ${REGISTER_AIMMSUNIT_NAME} POST_BUILD
			COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/autolibs/release_and_publisher.py createlib
			WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
		)
	endif()

endfunction(register_aimmsunit)