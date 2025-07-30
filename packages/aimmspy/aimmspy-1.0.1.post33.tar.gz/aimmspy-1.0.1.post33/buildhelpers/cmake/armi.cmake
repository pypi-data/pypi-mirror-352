function(armi_generate)
    set(prefix _)
    set(options)
    set(oneValueArgs GEN_INCLUDE_OUTPUT_DIR GEN_SOURCE_OUTPUT_DIR ARMI_GENERATOR_PATH CPP_NAMESPACE CPP_INCLUDE_PREFIX CPP_TRACER_NAME CLEAR_GEN_FILES_LIST)
    set(multiValueArgs INPUT_FILES)

    cmake_parse_arguments(PARSE_ARGV 0 "${prefix}" "${options}" "${oneValueArgs}" "${multiValueArgs}")

    string(REPLACE ";" " " INPUT_FILES "${__INPUT_FILES}")

    unset(ENV{GEN_SOURCE_FILE_LIST} CACHE)
    unset(ENV{GEN_HEADER_FILE_LIST} CACHE)

    if(DEFINED __CLEAR_GEN_FILES_LIST)
        set(GEN_HEADER_FILE_LIST "")
        set(GEN_SOURCE_FILE_LIST "")
    endif()

    foreach (f ${__INPUT_FILES})
        get_filename_component(FILE_NAME "${f}" NAME_WLE)

        list(APPEND GEN_HEADER_FILE_LIST
                ${__GEN_INCLUDE_OUTPUT_DIR}/${FILE_NAME}.h
                ${__GEN_INCLUDE_OUTPUT_DIR}/${FILE_NAME}.Fwd.h
                ${__GEN_INCLUDE_OUTPUT_DIR}/${FILE_NAME}.Ids.h
                ${__GEN_INCLUDE_OUTPUT_DIR}/${FILE_NAME}.Rec.h
                ${__GEN_INCLUDE_OUTPUT_DIR}/${FILE_NAME}.Stub.h
                ${__GEN_INCLUDE_OUTPUT_DIR}/${FILE_NAME}.Singleton.h
                ${__GEN_INCLUDE_OUTPUT_DIR}/${FILE_NAME}.Skel.h)

        list(APPEND GEN_SOURCE_FILE_LIST
                ${__GEN_SOURCE_OUTPUT_DIR}/${FILE_NAME}.Ids.cpp
                ${__GEN_SOURCE_OUTPUT_DIR}/${FILE_NAME}.Rec.cpp
                ${__GEN_SOURCE_OUTPUT_DIR}/${FILE_NAME}.Stub.cpp
                ${__GEN_SOURCE_OUTPUT_DIR}/${FILE_NAME}.Singleton.cpp
                ${__GEN_SOURCE_OUTPUT_DIR}/${FILE_NAME}.Skel.cpp
                )

    endforeach ()

    message("-- [armi_generate] .h files to: ${__GEN_INCLUDE_OUTPUT_DIR}")
    message("-- [armi_generate] .cpp files to: ${__GEN_SOURCE_OUTPUT_DIR}")

    set(CPP_NAMESPACE_FLAG "")
    set(CPP_NAMESPACE_VALUE "")
    
    if(DEFINED __CPP_NAMESPACE)
        set(CPP_NAMESPACE_FLAG "-cppNamespace")
        set(CPP_NAMESPACE_VALUE "${__CPP_NAMESPACE}")
    endif()

    set(CPP_INCLUDE_PREFIX_FLAG "")
    set(CPP_INCLUDE_PREFIX_VALUE "")
  
    if(DEFINED __CPP_INCLUDE_PREFIX)
        set(CPP_INCLUDE_PREFIX_FLAG "-cppIncPrefix")
        set(CPP_INCLUDE_PREFIX_VALUE "${__CPP_INCLUDE_PREFIX}")
    endif()

    set(CPP_TRACER_NAME_FLAG "")
    set(CPP_TRACER_NAME_VALUE "")
  
    if(DEFINED __CPP_TRACER_NAME)
        set(CPP_TRACER_NAME_FLAG "-cppTracerName")
        set(CPP_TRACER_NAME_VALUE "${__CPP_TRACER_NAME}")
        message("-- [armi_generate] setting tracer-name to: ${__CPP_TRACER_NAME}")
    endif()
    
    # execute_process(
    #     COMMAND echo ${__ARMI_GENERATOR_PATH} -cpp -cppHeaderDir ${__GEN_INCLUDE_OUTPUT_DIR} -cppSourceDir ${__GEN_SOURCE_OUTPUT_DIR} ${CPP_NAMESPACE_FLAG} ${CPP_NAMESPACE_VALUE} ${CPP_INCLUDE_PREFIX_FLAG} ${CPP_INCLUDE_PREFIX_VALUE}  ${CPP_INCLUDE_PREFIX_FLAG} ${CPP_INCLUDE_PREFIX_VALUE} ${__INPUT_FILES}
    #     WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    #     COMMAND_ERROR_IS_FATAL ANY
    # )
    
    execute_process(
        COMMAND java -jar ${__ARMI_GENERATOR_PATH} -cpp -cppHeaderDir ${__GEN_INCLUDE_OUTPUT_DIR} -cppSourceDir ${__GEN_SOURCE_OUTPUT_DIR} ${CPP_NAMESPACE_FLAG} ${CPP_NAMESPACE_VALUE} ${CPP_INCLUDE_PREFIX_FLAG} ${CPP_INCLUDE_PREFIX_VALUE} ${CPP_TRACER_NAME_FLAG} ${CPP_TRACER_NAME_VALUE} ${__INPUT_FILES}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMAND_ERROR_IS_FATAL ANY
    )

    set(GEN_HEADER_FILE_LIST ${GEN_HEADER_FILE_LIST} PARENT_SCOPE)
    set(GEN_SOURCE_FILE_LIST ${GEN_SOURCE_FILE_LIST} PARENT_SCOPE)
endfunction()
