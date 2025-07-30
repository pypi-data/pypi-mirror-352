function(download_file)
    set(prefix _)
    set(options)
    set(oneValueArgs URL DEST_PATH)
    set(multiValueArgs)

    cmake_parse_arguments(PARSE_ARGV 0 "${prefix}" "${options}" "${oneValueArgs}" "${multiValueArgs}")

    if (NOT DEFINED ENV{ARTIFACTORY_GLOBAL_READER_AUTH})
        message(FATAL_ERROR "ARTIFACTORY_GLOBAL_READER_AUTH not set this is required for downloading files from artifactory")
    else()
        message("-- [download_file] using enviroment variable ARTIFACTORY_GLOBAL_READER_AUTH")
    endif()

    message("-- [download_file] ${__URL} to: ${__DEST_PATH}")

    if (NOT EXISTS ${__DEST_PATH})
        file(DOWNLOAD "${__URL}" "${__DEST_PATH}"
                SHOW_PROGRESS
                TLS_VERIFY ON
                STATUS DOWNLOAD_RESULT
                HTTPHEADER "Authorization: Basic $ENV{ARTIFACTORY_GLOBAL_READER_AUTH}"
        )
        list(GET DOWNLOAD_RESULT 0 DOWNLOAD_RESULT_CODE)
        if (NOT DOWNLOAD_RESULT_CODE EQUAL 0)
            # message("download failed for: ${__URL} [${DOWNLOAD_RESULT}] DOWNLOAD_RESULT_CODE: ${DOWNLOAD_RESULT_CODE}")
            # delete file if download failed
            file(REMOVE ${__DEST_PATH})
            # exit with error
            message(FATAL_ERROR "download failed for: ${__URL} [${DOWNLOAD_RESULT}] DOWNLOAD_RESULT_CODE: ${DOWNLOAD_RESULT_CODE}")
        endif ()
    endif ()

endfunction()
