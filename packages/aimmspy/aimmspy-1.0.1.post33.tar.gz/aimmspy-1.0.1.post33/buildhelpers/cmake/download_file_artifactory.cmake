function(download_file_artifactory)
    set(prefix _)
    set(options)
    set(oneValueArgs URL DEST_PATH)
    set(multiValueArgs)

    cmake_parse_arguments(
        PARSE_ARGV 0
        "${prefix}"
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
    )

    if(DEFINED ENV{ARTIFACTORY_GLOBAL_READER_AUTH})
        message(
            "-- [download_file_artifactory] using enviroment variable "
            "ARTIFACTORY_GLOBAL_READER_AUTH"
        )
        set(
            AUTH_HEADER
            "Authorization: Basic $ENV{ARTIFACTORY_GLOBAL_READER_AUTH}"
        )
    elseif(DEFINED ENV{ARTIFACTORY_API_KEY})
        message(
            "-- [download_file_artifactory] using enviroment variable "
            "ARTIFACTORY_API_KEY"
        )
        set(AUTH_HEADER "X-JFrog-Art-Api: $ENV{ARTIFACTORY_API_KEY}")
    else()
        message(
            FATAL_ERROR
            "Neither ARTIFACTORY_GLOBAL_READER_AUTH nor ARTIFACTORY_API_KEY is "
            "set this is required for downloading files from artifactory"
        )
    endif()

    message("-- [download_file_artifactory] ${__URL} to: ${__DEST_PATH}")

    if(NOT EXISTS ${__DEST_PATH})
        file(DOWNLOAD "${__URL}" "${__DEST_PATH}"
                SHOW_PROGRESS
                TLS_VERIFY ON
                STATUS DOWNLOAD_RESULT
                HTTPHEADER "${AUTH_HEADER}"
        )
        list(GET DOWNLOAD_RESULT 0 DOWNLOAD_RESULT_CODE)
        if(NOT DOWNLOAD_RESULT_CODE EQUAL 0)
            # delete file if download failed
            file(REMOVE ${__DEST_PATH})

            # exit with error
            message(
                FATAL_ERROR
                "download failed for: ${__URL} [${DOWNLOAD_RESULT}] "
                "DOWNLOAD_RESULT_CODE: ${DOWNLOAD_RESULT_CODE}")
        endif()
    endif()

endfunction()
