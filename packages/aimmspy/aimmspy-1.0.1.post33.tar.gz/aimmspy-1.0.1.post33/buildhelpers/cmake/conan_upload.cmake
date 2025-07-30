
# function called conan_upload
#   - uploads the package to the conan server
function(git_and_cmake_info)


    if(DEFINED ENV{CONAN_BUILD})
        return()
    endif()

    execute_process(
        COMMAND git describe --tags --abbrev=1 --match "develop*"
    )

    execute_process(
        COMMAND git describe --tags --abbrev=1 --match "release*"
    )

    execute_process(
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/gitinfo-cli.py version
        OUTPUT_VARIABLE conan_version_name
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE exit_code
        ERROR_VARIABLE error_message
        ERROR_STRIP_TRAILING_WHITESPACE
    )

    if(NOT ${exit_code} EQUAL 0 AND DEFINED ENV{CI})
        message(FATAL_ERROR "
        ==============================================================
        ${error_message}
        Possible fix add a more recent annotated tag to the repo if on 
        develop do develop-1.0.10000 and if on master do release-1.0.0
        make sure that the version is higher than the last tag
        ==============================================================
        ")
    endif()

    execute_process(
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/gitinfo-cli.py fullbranchname
        OUTPUT_VARIABLE git_branch_name
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE exit_code
    )

    if(NOT ${exit_code} EQUAL 0 AND DEFINED ENV{CI})
        message(FATAL_ERROR "
        ==============================================================
        ${error_message}
        Possible fix add a more recent annotated tag to the repo if on 
        develop do develop-1.0.10000 and if on master do release-1.0.0
        make sure that the version is higher than the last tag
        ==============================================================
        ")
    endif()

    # replace all / with a _
    string(REPLACE "/" "_" git_branch_name ${git_branch_name})
    string(REPLACE "-" "_" git_branch_name ${git_branch_name})

    execute_process(
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/gitinfo-cli.py commithash
        OUTPUT_VARIABLE git_last_commit_hash
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE exit_code
    )

    if(NOT ${exit_code} EQUAL 0 AND DEFINED ENV{CI})
        message(FATAL_ERROR "
        ==============================================================
        ${error_message}
        Possible fix add a more recent annotated tag to the repo if on 
        develop do develop-1.0.10000 and if on master do release-1.0.0
        make sure that the version is higher than the last tag
        ==============================================================
        ")
    endif()

    set(conan_version_name ${conan_version_name} PARENT_SCOPE)
    set(git_branch_name ${git_branch_name} PARENT_SCOPE)
    

    # get year, build date and build machine which will be used in the Version.h file
    string(TIMESTAMP ProductVersion_CopyrightYear "%Y")
    string(TIMESTAMP ProductVersion_BuildDate "%Y-%m-%dT%H:%M:%SZ")
    cmake_host_system_information(RESULT ProductVersion_BuildHost QUERY HOSTNAME) 

    # print info about what the variables are set to
    message("\n ======== git info ========")
    message("Version        :    ${conan_version_name}")
    message("Branch          :    ${git_branch_name}")
    message("Commit Hash    :    ${git_last_commit_hash}\n")

    message(" ======== build info ========")
    message("Copyright Year :    ${ProductVersion_CopyrightYear}")
    message("Build Date     :    ${ProductVersion_BuildDate}")
    message("Build Host     :    ${ProductVersion_BuildHost}\n")
endfunction(git_and_cmake_info)

function(upload_conan_package package_name conan_file_dir)
    message("Debug info: conan_version_name: ${conan_version_name}, git_branch_name: ${git_branch_name}, git_last_commit_hash: ${git_last_commit_hash}")

    if( UPLOAD_IF_DIFFFERENCE)
        execute_process(
            COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/cmake/conan_export_cmake.py --conan_file_dir ${conan_file_dir} --name ${package_name} --version ${conan_version_name} --user aimms --channel ${git_branch_name} --install_dir ${CMAKE_SOURCE_DIR}/out/install --upload_if_different
            COMMAND_ERROR_IS_FATAL ANY
        )
    else()
        execute_process(
            COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/buildhelpers/cmake/conan_export_cmake.py --conan_file_dir ${conan_file_dir} --name ${package_name} --version ${conan_version_name} --user aimms --channel ${git_branch_name} --install_dir ${CMAKE_SOURCE_DIR}/out/install
            COMMAND_ERROR_IS_FATAL ANY
        )
    endif()
endfunction(upload_conan_package)
