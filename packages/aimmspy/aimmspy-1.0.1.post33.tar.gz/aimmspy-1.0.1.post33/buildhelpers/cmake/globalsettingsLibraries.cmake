message( "-- Setting common compilation flags" )
if(UNIX)
  add_compile_options(
    "-Wno-write-strings"
    "-fexceptions"
    "-fpermissive"
    "-fnon-call-exceptions"
    "-fvisibility=hidden"
  )
  set(CMAKE_POSITION_INDEPENDENT_CODE ON) # add -fPIC compiler option
    
  add_compile_definitions(
     LINUX
     LINUX64
    UNICODE
    _UNICODE
    GCC_HASCLASSVISIBILITY
  )

  add_link_options(
	"LINKER:--no-undefined" # Ensure that the linker informs us of missing symbols
  )
endif()

# Enable ccache if it is available
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    message("----- ccache found and enabled: ${CCACHE_PROGRAM} -----")
    set(CMAKE_CXX_COMPILER_LAUNCHER ${CCACHE_PROGRAM})
else()
	message("----- ccache disabled! -----")
endif()