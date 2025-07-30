
if(UNIX)
  add_compile_options(
    "-Wno-write-strings"
    "-funsigned-char"
    "-fexceptions"
    "-fpermissive"
    "-fnon-call-exceptions"
    "-fvisibility=hidden"
  )
    
  add_compile_definitions(
     LINUX
     LINUX64
    _FILE_OFFSET_BITS=64
    AIMMS_PTHREAD_STACKSIZE=524288
    GCC_HASCLASSVISIBILITY
  )

  add_link_options(
	  "LINKER:--no-undefined" # Ensure that the linker informs us of missing symbols
  )
elseif(WIN32)
  add_compile_definitions(
    WIN32
    _WINDOWS
    __WIN32__
    _CRT_SECURE_NO_WARNINGS
  )
endif()

add_compile_definitions(
  UNICODE
  _UNICODE

  # $<$<CONFIG:Debug>:DEBUG>
  # $<$<CONFIG:RelWithDebInfo>:_DEBUG>
  # $<$<CONFIG:RelWithDebInfo>:NDEBUG>
  # $<$<CONFIG:Release>:NDEBUG>
  # $<$<CONFIG:Release>:_DEBUG>
)