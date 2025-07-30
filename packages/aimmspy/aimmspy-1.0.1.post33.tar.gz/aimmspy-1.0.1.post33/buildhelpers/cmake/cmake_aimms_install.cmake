# function with argument project name which will be used to install the target
if(${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.31")
    cmake_policy(SET CMP0177 NEW)
endif()
#function for linux to strip a target from debug symbols and make a .debug file
function(aimms_unix_strip)
    set(options)
    set(oneValueArgs NAME )
    set(multiValueArgs)
    cmake_parse_arguments(UNIX_STRIP "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

    if(UNIX)
        add_custom_command(
            TARGET ${UNIX_STRIP_NAME} 
            POST_BUILD
            COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/cmake/strip_linux_debug_symbols.py $<TARGET_FILE:${UNIX_STRIP_NAME}>
        )
    endif()
endfunction(aimms_unix_strip)

function(install_files)
    set(options NO_CONFIG)
    set(oneValueArgs CONFIG DESTINATION_DIR)
    set(multiValueArgs FILE_LIST)
    cmake_parse_arguments(INSTALL_FILES "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    foreach(file ${INSTALL_FILES_FILE_LIST})
        if (NOT INSTALL_FILES_NO_CONFIG)
            install(
                FILES ${file}
                CONFIGURATIONS ${INSTALL_FILES_CONFIG}
                DESTINATION ${INSTALL_FILES_CONFIG}/${INSTALL_FILES_DESTINATION_DIR}
            )
        else()
            install(
                FILES ${file}
                CONFIGURATIONS ${INSTALL_FILES_CONFIG}
                DESTINATION ${INSTALL_FILES_DESTINATION_DIR}
            )
        endif()
    endforeach()
endfunction()

function(install_target_files)
    set(options NO_CONFIG)
    set(oneValueArgs TARGET_NAME CONFIG DESTINATION_FOLDER)
    set(multiValueArgs)
    cmake_parse_arguments(INSTALL_TARGET "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    # if the project is a shared library, install the pdb file in the bin folder
    get_target_property(target_type ${INSTALL_TARGET_TARGET_NAME} TYPE)

    # get target property name
    get_target_property(complete_target_name ${INSTALL_TARGET_TARGET_NAME} OUTPUT_NAME)

    # if target_name not found, use AIMMS_INSTALL_NAME
    if( NOT complete_target_name )
        set(complete_target_name ${INSTALL_TARGET_TARGET_NAME})
    endif()

    # if destination_folder not set, use bin on windows and lib on linux
    if(NOT INSTALL_TARGET_DESTINATION_FOLDER OR INSTALL_TARGET_DESTINATION_FOLDER STREQUAL "")
        if(UNIX)
            if(target_type STREQUAL "EXECUTABLE")
                set(INSTALL_TARGET_DESTINATION_FOLDER bin)
            else()
                set(INSTALL_TARGET_DESTINATION_FOLDER lib)
            endif()
        elseif(WIN32)
            set(INSTALL_TARGET_DESTINATION_FOLDER bin)
        endif()
    endif()

    set_target_properties(${INSTALL_TARGET_TARGET_NAME} PROPERTIES INTERPROCEDURAL_OPTIMIZATION_DEBUG FALSE)
    set_target_properties(${INSTALL_TARGET_TARGET_NAME} PROPERTIES INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO FALSE)

    if (NOT INSTALL_TARGET_NO_CONFIG)
        if (target_type STREQUAL "SHARED_LIBRARY" OR target_type STREQUAL "EXECUTABLE")
            set_target_properties(${INSTALL_TARGET_TARGET_NAME} PROPERTIES INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO TRUE)
            if(UNIX AND NOT INSTALL_TARGET_CONFIG STREQUAL "Release")
                aimms_unix_strip(NAME ${INSTALL_TARGET_TARGET_NAME})

                install(
                    FILES  $<TARGET_FILE_DIR:${INSTALL_TARGET_TARGET_NAME}>/$<TARGET_FILE_PREFIX:${INSTALL_TARGET_TARGET_NAME}>$<TARGET_FILE_BASE_NAME:${INSTALL_TARGET_TARGET_NAME}>.debug
                    CONFIGURATIONS ${INSTALL_TARGET_CONFIG}
                    DESTINATION ${INSTALL_TARGET_CONFIG}/${INSTALL_TARGET_DESTINATION_FOLDER}
                )

            elseif(WIN32)

                install(
                    FILES $<TARGET_FILE_DIR:${INSTALL_TARGET_TARGET_NAME}>/${complete_target_name}.pdb 
                    CONFIGURATIONS ${INSTALL_TARGET_CONFIG}
                    DESTINATION ${INSTALL_TARGET_CONFIG}/${INSTALL_TARGET_DESTINATION_FOLDER}
                )
            endif()
        elseif(target_type STREQUAL "STATIC_LIBRARY")
            if (WIN32)

                # get the property of the pdb file location COMPILE_PDB_OUTPUT_DIRECTORY_<CONFIG>
                get_target_property(pdb_file_location ${INSTALL_TARGET_TARGET_NAME} COMPILE_PDB_OUTPUT_DIRECTORY)
                # message(STATUS "pdb_file_location: ${pdb_file_location}")
                if (pdb_file_location STREQUAL "pdb_file_location-NOTFOUND")
                    install(
                        FILES ${CMAKE_CURRENT_BINARY_DIR}/CmakeFiles/${INSTALL_TARGET_TARGET_NAME}.dir/${INSTALL_TARGET_CONFIG}/${complete_target_name}.pdb
                        CONFIGURATIONS ${INSTALL_TARGET_CONFIG}
                        DESTINATION ${INSTALL_TARGET_CONFIG}/lib
                    )
                else()
                    install(
                        FILES ${pdb_file_location}/${INSTALL_TARGET_CONFIG}/${complete_target_name}.pdb
                        CONFIGURATIONS ${INSTALL_TARGET_CONFIG}
                        DESTINATION ${INSTALL_TARGET_CONFIG}/lib
                    )
                endif()
            endif()
        endif()
    else()
        if (target_type STREQUAL "SHARED_LIBRARY" OR target_type STREQUAL "EXECUTABLE")
            set_target_properties(${INSTALL_TARGET_TARGET_NAME} PROPERTIES INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO TRUE)

            if(UNIX AND NOT INSTALL_TARGET_CONFIG STREQUAL "Release")
                aimms_unix_strip(NAME ${INSTALL_TARGET_TARGET_NAME})

                install(
                    FILES $<TARGET_FILE_DIR:${INSTALL_TARGET_TARGET_NAME}>/$<TARGET_FILE_PREFIX:${INSTALL_TARGET_TARGET_NAME}>$<TARGET_FILE_BASE_NAME:${INSTALL_TARGET_TARGET_NAME}>.debug
                    CONFIGURATIONS ${INSTALL_TARGET_CONFIG}
                    DESTINATION ${INSTALL_TARGET_DESTINATION_FOLDER}
                )

            elseif(WIN32)
                install(
                    FILES $<TARGET_FILE_DIR:${INSTALL_TARGET_TARGET_NAME}>/${complete_target_name}.pdb 
                    CONFIGURATIONS ${INSTALL_TARGET_CONFIG}
                    DESTINATION ${INSTALL_TARGET_DESTINATION_FOLDER}
                )
            endif()
        elseif(target_type STREQUAL "STATIC_LIBRARY")
            if (WIN32)
                # this is a workaround for the fact that the pdb file is not copied to the target folder when using the install command
                # the pdb file is copied to the build folder, so we can copy it from there    
                install(
                    FILES ${CMAKE_CURRENT_BINARY_DIR}/CmakeFiles/${INSTALL_TARGET_TARGET_NAME}.dir/${CONFIG}/${complete_target_name}.pdb
                    CONFIGURATIONS ${INSTALL_TARGET_CONFIG}
                    DESTINATION lib
                )
            endif()
        endif()
    endif()
endfunction()

function(aimms_runtime_install)

    set(options NO_CONFIG NO_INCLUDE_BLOB)
    set(oneValueArgs NAME RUNTIME_FOLDER)
    set(multiValueArgs NO_MULTI INCLUDE_FILES LIB_FILES BIN_FILES)
    cmake_parse_arguments(AIMMS_INSTALL "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

    # if AIMMS_INSTALL RUNTIME_FOLDER is not set, use bin
    if( NOT AIMMS_INSTALL_RUNTIME_FOLDER )
        set(AIMMS_INSTALL_RUNTIME_FOLDER bin)
    endif()

    foreach(CONFIG ${CMAKE_CONFIGURATION_TYPES} )

        if(WIN32)
            install(
                TARGETS ${AIMMS_INSTALL_NAME}
                CONFIGURATIONS ${CONFIG}
                RUNTIME DESTINATION ${CONFIG}/${AIMMS_INSTALL_RUNTIME_FOLDER}
            )
        else()
            install(
                TARGETS ${AIMMS_INSTALL_NAME}
                CONFIGURATIONS ${CONFIG}
                RUNTIME DESTINATION ${CONFIG}/${AIMMS_INSTALL_RUNTIME_FOLDER}
                LIBRARY DESTINATION ${CONFIG}/${AIMMS_INSTALL_RUNTIME_FOLDER}
            )
        endif()
    
        install_files(
            FILE_LIST ${AIMMS_INSTALL_INCLUDE_FILES}
            CONFIG ${CONFIG}
            DESTINATION_DIR include
            NO_CONFIG
        )

        install_files(
            FILE_LIST ${AIMMS_INSTALL_LIB_FILES}
            CONFIG ${CONFIG}
            DESTINATION_DIR lib
            NO_CONFIG
        )

        install_files(
            FILE_LIST ${AIMMS_INSTALL_BIN_FILES}
            CONFIG ${CONFIG}
            DESTINATION_DIR bin
            NO_CONFIG
        )
                
        install_target_files(
            TARGET_NAME ${AIMMS_INSTALL_NAME}
            CONFIG ${CONFIG}
            DESTINATION_FOLDER ${AIMMS_INSTALL_RUNTIME_FOLDER}
        )
    endforeach()
    
endfunction(aimms_runtime_install)


function(aimms_header_install)
    set(options NO_INCLUDE_BLOB)
    set(oneValueArgs NAME)
    cmake_parse_arguments(AIMMS_INSTALL "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

    foreach(CONFIG ${CMAKE_CONFIGURATION_TYPES} )
        install(
            TARGETS ${AIMMS_INSTALL_NAME}
            CONFIGURATIONS ${CONFIG}
            FILE_SET HEADERS DESTINATION ${CONFIG}
        )
    endforeach()	

    if( NOT AIMMS_INSTALL_NO_INCLUDE_BLOB )
        install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/include" # source directory
            DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/$<CONFIG>" # target directory
            FILES_MATCHING # install only matched files
            PATTERN "*.h" # select header files
            PATTERN "*.hpp" # select header files
        )
    endif()
    
endfunction(aimms_header_install)


function(aimms_install)

    set(options NO_CONFIG NO_INCLUDE_BLOB)
    set(oneValueArgs NAME)
    set(multiValueArgs NO_MULTI INCLUDE_FILES LIB_FILES BIN_FILES AUXILARY_DIRS COMPONENTS)
    cmake_parse_arguments(AIMMS_INSTALL "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

    # if AIMMS_INSTALL_COMPONENTS is empty use .
    if( NOT AIMMS_INSTALL_COMPONENTS )
        set(AIMMS_INSTALL_COMPONENTS .)
    endif()

    if( NOT AIMMS_INSTALL_NO_CONFIG AND NOT DEFINED ENV{CONAN_BUILD} )
        foreach(COMPONENT ${AIMMS_INSTALL_COMPONENTS})
            foreach(CONFIG ${CMAKE_CONFIGURATION_TYPES} )
                install(
                    TARGETS ${AIMMS_INSTALL_NAME}
                    CONFIGURATIONS ${CONFIG}
                    RUNTIME DESTINATION ${CONFIG}/${COMPONENT}/bin
                    LIBRARY DESTINATION ${CONFIG}/${COMPONENT}/lib
                    ARCHIVE DESTINATION ${CONFIG}/${COMPONENT}/lib
                    OBJECTS DESTINATION ${CONFIG}/${COMPONENT}/lib
                    FRAMEWORK DESTINATION ${CONFIG}/${COMPONENT}/lib
                    BUNDLE DESTINATION ${CONFIG}/${COMPONENT}/lib
                    FILE_SET HEADERS DESTINATION ${CONFIG}/${COMPONENT}
                )

                install_files(
                    FILE_LIST ${AIMMS_INSTALL_INCLUDE_FILES}
                    CONFIG ${CONFIG}
                    DESTINATION_DIR include
                )

                install_files(
                    FILE_LIST ${AIMMS_INSTALL_BIN_FILES}
                    CONFIG ${CONFIG}
                    DESTINATION_DIR bin
                )

                install_files(
                    FILE_LIST ${AIMMS_INSTALL_LIB_FILES}
                    CONFIG ${CONFIG}
                    DESTINATION_DIR lib
                )

                foreach( DIRECTORY ${AIMMS_INSTALL_AUXILARY_DIRS} )
                    install(
                        DIRECTORY ${DIRECTORY}
                        CONFIGURATIONS ${CONFIG}
                        DESTINATION ${CONFIG}
                    )
                endforeach()
                        
                install_target_files(
                    TARGET_NAME ${AIMMS_INSTALL_NAME}
                    CONFIG ${CONFIG}
                    DESTINATION_FOLDER ${COMPONENT}/$<IF:$<PLATFORM_ID:Linux>,lib,bin>
                )
            endforeach()
        endforeach()

        foreach(COMPONENT ${AIMMS_INSTALL_COMPONENTS})
            if( NOT AIMMS_INSTALL_NO_INCLUDE_BLOB )
                install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/include" # source directory
                    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/$<CONFIG>/${COMPONENT}" # target directory
                    FILES_MATCHING # install only matched files
                    PATTERN "*.h" # select header files
                    PATTERN "*.hpp" # select header files
                )
            endif()
        endforeach()

    else()
        foreach(CONFIG ${CMAKE_CONFIGURATION_TYPES} )
            install(
                TARGETS ${AIMMS_INSTALL_NAME}
                CONFIGURATIONS ${CONFIG}
                RUNTIME DESTINATION bin
                LIBRARY DESTINATION lib
                ARCHIVE DESTINATION lib
                OBJECTS DESTINATION lib
                FRAMEWORK DESTINATION lib
                BUNDLE DESTINATION lib
                FILE_SET HEADERS
            )
        
            install_files(
                FILE_LIST ${AIMMS_INSTALL_INCLUDE_FILES}
                CONFIG ${CONFIG}
                DESTINATION_DIR include
            )

            install_files(
                FILE_LIST ${AIMMS_INSTALL_BIN_FILES}
                CONFIG ${CONFIG}
                DESTINATION_DIR bin
            )

            install_files(
                FILE_LIST ${AIMMS_INSTALL_LIB_FILES}
                CONFIG ${CONFIG}
                DESTINATION_DIR lib
            )

            # loop over all files in the AUXILARY_DIRS list and install them
            foreach( DIRECTORY ${AIMMS_INSTALL_AUXILARY_DIRS} )
                install(
                    DIRECTORY ${DIRECTORY}
                    CONFIGURATIONS ${CONFIG}
                )
            endforeach()

            # get target property name
            get_target_property(target_name ${AIMMS_INSTALL_NAME} ${CONFIG}_OUTPUT_NAME)

            # if target_name not found, use AIMMS_INSTALL_NAME
            if( NOT target_name )
                set(target_name ${AIMMS_INSTALL_NAME})
            endif()

            install_target_files(
                TARGET_NAME ${AIMMS_INSTALL_NAME}
                CONFIG ${CONFIG}
                DESTINATION_FOLDER ""
                NO_CONFIG
            )
        endforeach()

        if( NOT AIMMS_INSTALL_NO_INCLUDE_BLOB )
            if (NOT DEFINED ENV{CONAN_BUILD})
                install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/include" # source directory
                    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/" # target directory
                    FILES_MATCHING # install only matched files
                    PATTERN "*.h" # select header files
                    PATTERN "*.hpp" # select header files
                )
            else ()
                install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/include" # source directory
                    DESTINATION "." # target directory
                    FILES_MATCHING # install only matched files
                    PATTERN "*.h" # select header files
                    PATTERN "*.hpp" # select header files
                )
            endif()
        endif()

    endif()

endfunction(aimms_install)

function(autolib_install)
    set(options IS_SFX IS_PURE_AIMMS)
    set(oneValueArgs NAME AUTOLIB_NAME FOLDER)
    set(multiValueArgs AUXILARY_DIRS)
    cmake_parse_arguments(AUTOLIB_INSTALL "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    string(REGEX MATCH "[^/]+$" PRESET_NAME ${CMAKE_BINARY_DIR})

    if ( AUTOLIB_INSTALL_FOLDER )
        set(DEST ${CMAKE_SOURCE_DIR}/out/upload/${PRESET_NAME}/$<CONFIG>/${AUTOLIB_INSTALL_AUTOLIB_NAME}/${AUTOLIB_INSTALL_FOLDER})
    else()
        if(AUTOLIB_INSTALL_IS_SFX)
            set(DEST ${CMAKE_SOURCE_DIR}/out/upload/${PRESET_NAME}/$<CONFIG>/${AUTOLIB_INSTALL_AUTOLIB_NAME})
        else()
            set(DEST ${CMAKE_SOURCE_DIR}/out/upload/${PRESET_NAME}/$<CONFIG>/${AUTOLIB_INSTALL_AUTOLIB_NAME}/DLL)
        endif()
    endif()

    set_target_properties(${AUTOLIB_INSTALL_NAME} PROPERTIES INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO TRUE)

    
    if(NOT AUTOLIB_INSTALL_IS_PURE_AIMMS)
        if(UNIX)
            aimms_unix_strip(NAME ${AUTOLIB_INSTALL_NAME})
    
            # execute post build running script python set_rpath.py
            if(UNIX)
                add_custom_command(TARGET ${AUTOLIB_INSTALL_NAME} POST_BUILD
                    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/cmake/set_rpath.py $<TARGET_FILE:${AUTOLIB_INSTALL_NAME}>
                )
            endif()
    
        endif()
        add_custom_command(TARGET ${AUTOLIB_INSTALL_NAME} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_FILE:${AUTOLIB_INSTALL_NAME}>
            ${DEST}/$<PATH:GET_FILENAME,$<TARGET_FILE:${AUTOLIB_INSTALL_NAME}>>
        )
        
        foreach(DIRECTORY ${AUTOLIB_INSTALL_AUXILARY_DIRS})
            add_custom_command(TARGET ${AUTOLIB_INSTALL_NAME} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_directory
                ${DIRECTORY}
                ${DEST}/$<PATH:GET_FILENAME,${FOLDER_NAME}>
            )
        endforeach()

        if(WIN32)
            add_custom_command(TARGET ${AUTOLIB_INSTALL_NAME} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different 
                    $<TARGET_PDB_FILE:${AUTOLIB_INSTALL_NAME}>
                    ${DEST}/$<PATH:GET_FILENAME,$<TARGET_PDB_FILE:${AUTOLIB_INSTALL_NAME}>>
            )
        elseif(UNIX)
            # install the debug symbols
            add_custom_command(TARGET ${AUTOLIB_INSTALL_NAME} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different 
                    $<TARGET_FILE_DIR:${AUTOLIB_INSTALL_NAME}>/$<TARGET_FILE_PREFIX:${AUTOLIB_INSTALL_NAME}>$<TARGET_FILE_BASE_NAME:${AUTOLIB_INSTALL_NAME}>.debug
                    ${DEST}/$<TARGET_FILE_PREFIX:${AUTOLIB_INSTALL_NAME}>$<TARGET_FILE_BASE_NAME:${AUTOLIB_INSTALL_NAME}>.debug
            )
        endif()
    endif()
endfunction(autolib_install)
