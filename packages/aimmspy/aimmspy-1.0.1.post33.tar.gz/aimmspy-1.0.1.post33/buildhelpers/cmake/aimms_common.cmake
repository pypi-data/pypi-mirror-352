function(whole_archive_shared_lib)
    set(options NO_WINDOWS NO_LINUX STRIP)	
    set(oneValueArgs NAME)
    set(multiValueArgs NAMES_STATIC)
    cmake_parse_arguments(WHOLE_ARCHIVE "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

    if(WIN32 AND NOT WHOLE_ARCHIVE_NO_WINDOWS)
        foreach(whole_archive_name_static ${WHOLE_ARCHIVE_NAMES_STATIC})
            target_link_options(${WHOLE_ARCHIVE_NAME}
                PRIVATE
                    $<$<PLATFORM_ID:Windows>:
                        /WHOLEARCHIVE:$<TARGET_FILE:${whole_archive_name_static}>
                    >
            )
        endforeach()
    endif()

    if(UNIX AND NOT WHOLE_ARCHIVE_NO_LINUX)
        set(whole_archive_names_static_expanded "")
        list(APPEND whole_archive_names_static_expanded "-Wl,--whole-archive")

        foreach(whole_archive_name_static ${WHOLE_ARCHIVE_NAMES_STATIC})
            list(APPEND whole_archive_names_static_expanded $<TARGET_FILE:${whole_archive_name_static}>)
        endforeach()

        list(APPEND whole_archive_names_static_expanded "-Wl,--no-whole-archive")

        target_link_options(${WHOLE_ARCHIVE_NAME}
            PRIVATE
                $<$<PLATFORM_ID:Linux>:${whole_archive_names_static_expanded}>
        )

        if(WHOLE_ARCHIVE_STRIP)
            # strip unneeded in a custom command post build
            add_custom_command(TARGET ${WHOLE_ARCHIVE_NAME} POST_BUILD
                COMMAND ${CMAKE_STRIP} --strip-unneeded $<TARGET_FILE:${WHOLE_ARCHIVE_NAME}>
            )
        endif()
    endif()
endfunction()