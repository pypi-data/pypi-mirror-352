function(conan2_install)

    set(options AUTO_FIND_PACKAGES CACHE_ONLY)
    set(oneValueArgs CONANFILE)
    set(multiValueArgs NO_MULTI)
    cmake_parse_arguments(CONAN2_INSTALL "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

    if(CONAN2_INSTALL_AUTO_FIND_PACKAGES)
        set(AUTO_FIND_PACKAGES ON)
    endif()

    if(CONAN2_INSTALL_CACHE_ONLY)
        set(CACHE_ONLY_FLAG "--no-remote")
    else()
        set(CACHE_ONLY_FLAG "-rconan-intra")
    endif()

    execute_process(
        COMMAND 
            conan --version && cmake --version
        COMMAND_ERROR_IS_FATAL 
            ANY
    )

    execute_process(
        COMMAND 
            cmake --version
        COMMAND_ERROR_IS_FATAL 
            ANY
    )

    list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR}/conan)
    list(APPEND CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR}/conan)

    set( CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} PARENT_SCOPE )
    set( CMAKE_PREFIX_PATH ${CMAKE_PREFIX_PATH} PARENT_SCOPE )

    if(DEFINED CONAN_BUILD_TYPE)
        set(CMAKE_CONFIGURATION_TYPES ${CONAN_BUILD_TYPE})
        message("CONAN_BUILD_TYPE = ${CONAN_BUILD_TYPE}")
    endif()

    if( DEFINED ENV{build_type} AND NOT DEFINED CONAN_BUILD_TYPE)
        message("ENV{build_type} = $ENV{build_type}")
        set(CMAKE_CONFIGURATION_TYPES $ENV{build_type})
    endif()

    message (" ======== conan install ======== ")

    foreach( CONFIG ${CMAKE_CONFIGURATION_TYPES})
        if (DEFINED ENV{CONAN_BUILD})
            if (DEFINED ENV{CONAN_HOST_PROFILE_PATH} AND DEFINED ENV{CONAN_BUILD_PROFILE_PATH})
                execute_process(
                    COMMAND 
                    conan install ${CONAN2_INSTALL_CONANFILE} --profile:host=$ENV{CONAN_HOST_PROFILE_PATH} --profile:build=$ENV{CONAN_BUILD_PROFILE_PATH} --output-folder=${CMAKE_BINARY_DIR}/conan ${CACHE_ONLY_FLAG} -v --lockfile-out ${CMAKE_BINARY_DIR}/conan/conan_${CONFIG}.lock --lockfile-clean --format=json
                    COMMAND_ERROR_IS_FATAL ANY
                    OUTPUT_VARIABLE CONAN_INSTALL_OUTPUT
                )
            else()
                message(WARNING "CONAN_HOST_PROFILE_PATH and/or CONAN_BUILD_PROFILE_PATH is not defined. Using default profile.")

                execute_process(
                    COMMAND
                    conan install ${CONAN2_INSTALL_CONANFILE} --output-folder=${CMAKE_BINARY_DIR}/conan ${CACHE_ONLY_FLAG} -v --lockfile-out ${CMAKE_BINARY_DIR}/conan/conan_${CONFIG}.lock --lockfile-clean --format=json
                    COMMAND_ERROR_IS_FATAL ANY 
                    OUTPUT_VARIABLE CONAN_INSTALL_OUTPUT
                )
            endif()
        else()
            execute_process(
                COMMAND 
                conan install ${CONAN2_INSTALL_CONANFILE} --profile:host=${CONAN_PROFILE}/${CONFIG} --profile:build=${CONAN_PROFILE}/build --output-folder=${CMAKE_BINARY_DIR}/conan ${CACHE_ONLY_FLAG} -v --lockfile-out ${CMAKE_BINARY_DIR}/conan/conan_${CONFIG}.lock --lockfile-clean --format=json --build=missing
                COMMAND_ERROR_IS_FATAL ANY
                OUTPUT_VARIABLE CONAN_INSTALL_OUTPUT
            )
        endif()

        # save the output of conan install to a file
        file(WRITE ${CMAKE_BINARY_DIR}/conan/conan_install_output_${CONFIG}.json ${CONAN_INSTALL_OUTPUT})

        # execute python script get_cmake_config_files.py --conan_config_dir ${CMAKE_BINARY_DIR}/conan
        execute_process(
            COMMAND
            ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/cmake/conan_cmake_connector.py --conan_config_dir ${CMAKE_BINARY_DIR}/conan --configuration ${CONFIG}
            COMMAND_ERROR_IS_FATAL ANY
        )

        # --------------------------------------------------------------------------------------------------------------
        # ---------------------------------- START OF CONAN INSTALL PROCESSING -----------------------------------------
        # --------------------------------------------------------------------------------------------------------------
    
        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------ PROCESSING cmake_find_package_names ARRAY -------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        if( DEFINED CONAN_BUILD_TYPE OR DEFINED ENV{build_type})
            if(AUTO_FIND_PACKAGES)

            # we only need to do the Debug variant for this case

                message(" ======== Auto find packages enabled ======== ")
                file(READ ${CMAKE_BINARY_DIR}/conan/conan_install_processed_${CONFIG}.json CONAN_INSTALL_OUTPUT)
                
                string(JSON CONAN_GRAPH_INFO_NAMES_LENGTH LENGTH ${CONAN_INSTALL_OUTPUT} "cmake_find_package_names")
            
                if (NOT ${CONAN_GRAPH_INFO_NAMES_LENGTH} EQUAL 0)
                    math(EXPR CONAN_GRAPH_INFO_NAMES_LENGTH "${CONAN_GRAPH_INFO_NAMES_LENGTH} - 1")
                    
                    foreach(INX RANGE 0 ${CONAN_GRAPH_INFO_NAMES_LENGTH})
                        string(JSON CONAN_GRAPH_INFO_NAME GET ${CONAN_INSTALL_OUTPUT} "cmake_find_package_names" ${INX})
                        find_package(${CONAN_GRAPH_INFO_NAME} CONFIG REQUIRED)
                    endforeach()
                endif()
            endif()
        endif()
    endforeach()

    if( NOT DEFINED CONAN_BUILD_TYPE AND NOT DEFINED ENV{build_type})
        if(AUTO_FIND_PACKAGES)
            message(" ======== Auto find packages enabled ======== ")
            file(READ ${CMAKE_BINARY_DIR}/conan/conan_install_processed_Debug.json CONAN_INSTALL_OUTPUT_DEBUG)

            string(JSON CONAN_GRAPH_INFO_NAMES_DEBUGLENGTH LENGTH ${CONAN_INSTALL_OUTPUT_DEBUG} "cmake_find_package_names")

            if (NOT ${CONAN_GRAPH_INFO_NAMES_DEBUGLENGTH} EQUAL 0)
                math(EXPR CONAN_GRAPH_INFO_NAMES_DEBUGLENGTH "${CONAN_GRAPH_INFO_NAMES_DEBUGLENGTH} - 1")

                foreach(INX RANGE 0 ${CONAN_GRAPH_INFO_NAMES_DEBUGLENGTH})
                    string(JSON CONAN_GRAPH_INFO_NAME_DEBUG GET ${CONAN_INSTALL_OUTPUT_DEBUG} "cmake_find_package_names" ${INX})
                    find_package(${CONAN_GRAPH_INFO_NAME_DEBUG} CONFIG REQUIRED)
                endforeach()
            endif()
        endif()
    endif()


    foreach( CONFIG ${CMAKE_CONFIGURATION_TYPES})
        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------ PROCESSING cmake_build_tools_paths ARRAY --------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        file(READ ${CMAKE_BINARY_DIR}/conan/conan_install_processed_${CONFIG}.json CONAN_INSTALL_OUTPUT)

        string(JSON CONAN_GRAPH_INFO_NAMES_LENGTH LENGTH ${CONAN_INSTALL_OUTPUT} "cmake_build_tools_paths")

        if (NOT ${CONAN_GRAPH_INFO_NAMES_LENGTH} EQUAL 0)
            math(EXPR CONAN_GRAPH_INFO_NAMES_LENGTH "${CONAN_GRAPH_INFO_NAMES_LENGTH} - 1")

            foreach(INX RANGE 0 ${CONAN_GRAPH_INFO_NAMES_LENGTH})
                string(JSON CONAN_GRAPH_INFO_NAME_JSON GET ${CONAN_INSTALL_OUTPUT} "cmake_build_tools_paths" ${INX})
                string(JSON CONAN_GRAPH_INFO_PATH GET ${CONAN_GRAPH_INFO_NAME_JSON} "path")
                string(JSON CONAN_GRAPH_INFO_NAME GET ${CONAN_GRAPH_INFO_NAME_JSON} "name")

                # set variable with name of the package in the variable name and path in the variable value
                set(${CONAN_GRAPH_INFO_NAME}_BIN_DIR_${CONFIG} ${CONAN_GRAPH_INFO_PATH} PARENT_SCOPE)
                message(STATUS "Conan: Tool declared ${CONAN_GRAPH_INFO_NAME} '${CONAN_GRAPH_INFO_NAME}_BIN_DIR_${CONFIG}'")

                if(DEFINED CONAN_BUILD_TYPE OR DEFINED ENV{build_type})
                    set(${CONAN_GRAPH_INFO_NAME}_BIN_DIR_RelWithDebInfo ${CONAN_GRAPH_INFO_PATH} PARENT_SCOPE)
                    message(STATUS "Conan: Tool declared ${CONAN_GRAPH_INFO_NAME} '${CONAN_GRAPH_INFO_NAME}_BIN_DIR_RelWithDebInfo'")
                endif()

            endforeach()
        endif()

        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------ PROCESSING cmake_append_conan_paths ARRAY -------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        set( BINARY_LOCATION_${CONFIG} )

        string(JSON CONAN_GRAPH_INFO_NAMES_LENGTH LENGTH ${CONAN_INSTALL_OUTPUT} "cmake_append_conan_paths")

        set (PACKAGE_BINARY_DIRS_${CONFIG} "" )

        if (NOT ${CONAN_GRAPH_INFO_NAMES_LENGTH} EQUAL 0)
            math(EXPR CONAN_GRAPH_INFO_NAMES_LENGTH "${CONAN_GRAPH_INFO_NAMES_LENGTH} - 1")

            foreach(INX RANGE 0 ${CONAN_GRAPH_INFO_NAMES_LENGTH})
                string(JSON CONAN_GRAPH_INFO_NAME_JSON GET ${CONAN_INSTALL_OUTPUT} "cmake_append_conan_paths" ${INX})
                string(JSON CONAN_GRAPH_INFO_PATH GET ${CONAN_GRAPH_INFO_NAME_JSON} "path")
                string(JSON CONAN_GRAPH_INFO_NAME GET ${CONAN_GRAPH_INFO_NAME_JSON} "name")

                # set variable with name of the package in the variable name and path in the variable value
                list (APPEND BINARY_LOCATION_${CONFIG} ${CONAN_GRAPH_INFO_PATH})

            endforeach()

            list(REMOVE_DUPLICATES BINARY_LOCATION_${CONFIG})
            # message(STATUS "BINARY_LOCATION_${CONFIG} = ${BINARY_LOCATION_${CONFIG}}")
            # remove any \n from the string
            string(REPLACE "\n" "" BINARY_LOCATION_${CONFIG} "${BINARY_LOCATION_${CONFIG}}")
            # relpace \\ with /
            string(REPLACE "\\" "/" BINARY_LOCATION_${CONFIG} "${BINARY_LOCATION_${CONFIG}}")
            set (PACKAGE_BINARY_DIRS_${CONFIG} ${BINARY_LOCATION_${CONFIG}})

        endif()

        message("${CONFIG} append paths: ${PACKAGE_BINARY_DIRS_${CONFIG}}")

        # generate a envfile.json containing the environment variables for each config type
        if(WIN32)

            # $ENV{PATH} replace \ with /
            string(REPLACE "\\" "/" ENV_PATH "$ENV{PATH}")
            
            file(WRITE ${CMAKE_SOURCE_DIR}/out/envfile_${CONFIG}.json 
"{
    \"PATH\": \"${ENV_PATH};${PACKAGE_BINARY_DIRS_${CONFIG}};\"
}"
            )
        endif()

        if (UNIX)
            # change ; to : and add $ENV{LD_LIBRARY_PATH}
            string(REPLACE ";" ":" temp_PACKAGE_BINARY_DIRS_${CONFIG} "${PACKAGE_BINARY_DIRS_${CONFIG}}")
            
            file(WRITE ${CMAKE_SOURCE_DIR}/out/envfile_${CONFIG}.json
"{
    \"LD_LIBRARY_PATH\": \"$ENV{LD_LIBRARY_PATH}:${temp_PACKAGE_BINARY_DIRS_${CONFIG}}:\"
}"
            )
        endif()

        set (PACKAGE_BINARY_DIRS_${CONFIG} ${PACKAGE_BINARY_DIRS_${CONFIG}} PARENT_SCOPE)
    endforeach()

    message (" ======== conan install finished  ======== ")
endfunction(conan2_install)
