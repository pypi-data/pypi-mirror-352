
include(buildhelpers/cmake/conan_upload.cmake)
include(buildhelpers/cmake/cmake_aimms_install.cmake)
include(buildhelpers/cmake/cmake_conan2_install.cmake)
include(buildhelpers/cmake/register_tests.cmake)
include(buildhelpers/cmake/register_benchmarks.cmake)
include(buildhelpers/cmake/aimms_common.cmake)
include(buildhelpers/cmake/download_file.cmake)
# make sure that the compile commands are generated for ide support and other tools

find_package(Python3 COMPONENTS Interpreter)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# use, i.e. don't skip the full RPATH for the build tree
set(CMAKE_SKIP_BUILD_RPATH FALSE)

# when building, don't use the install RPATH already
# (but later on when installing)
set(CMAKE_BUILD_WITH_INSTALL_RPATH FALSE)

# the RPATH to be used when installing
# use, i.e. don't skip the full RPATH for the build tree
set(CMAKE_INSTALL_RPATH "\$ORIGIN/.")

# don't add the automatically determined parts of the RPATH
# which point to directories outside the build tree to the install RPATH
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH FALSE)

# CMake defaults on linux for static libraries to not turn on -fPIC (for gcc)
# this results in static libraries that can not be used for creating .so files
# (ie if libX.so depends on libA.a then libA.a should have position
#  independent code)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# gcc defaults to export all symbols, we only want to export symbols that
# are explicitly marked as such
set(CMAKE_CXX_VISIBILITY_PRESET hidden)

# get the folder name of the root cmakelists

cmake_path(GET CMAKE_SOURCE_DIR STEM AIMMS_ROOT_FOLDER_NAME)

# a nice message which repo is being build
message(STATUS "Building ${AIMMS_ROOT_FOLDER_NAME}")


find_program(CCACHE_PROGRAM ccache)

# if found and env ENABLE_CCACHE is set to 1 then enable ccache

# not on windows
if ( NOT WIN32)
    if (CCACHE_PROGRAM)
        message("----- ccache found and enabled: ${CCACHE_PROGRAM} -----")
        set(CMAKE_C_COMPILER_LAUNCHER ${CCACHE_PROGRAM})
        set(CMAKE_CXX_COMPILER_LAUNCHER ${CCACHE_PROGRAM})
        set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ccache)
        set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ccache)
    else()
        message("----- ccache not found or not enabled -----")
    endif()

    # if aimms root folder is aimms ski[ setting link time optimisation for release builds
    if (AIMMS_ROOT_FOLDER_NAME STREQUAL "aimms")
        set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELEASE FALSE)
    else()
        if (UNIX)
            message (STATUS "Setting link time optimisation for release builds")
            set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELEASE TRUE)
        endif()
    endif()
endif()


#if CMAKE_UPLOAD defined skip this part
if(NOT DEFINED CONAN_UPLOAD AND NOT DEFINED ENV{CONAN_BUILD})

    # check if preset is not empty
    if ( NOT DEFINED ENV{preset})
        message (STATUS "CONAN_PROFILE: ${CONAN_PROFILE}")

        # get the arch and compiler from the conan profile by splitting it ont the /
        string(REPLACE "/" ";" CONAN_PROFILE_LIST ${CONAN_PROFILE})
        # the last element is the compiler
        list(GET CONAN_PROFILE_LIST -1 CONAN_COMPILER)
        # the second last element is the arch
        list(GET CONAN_PROFILE_LIST -2 CONAN_ARCH)
    else()
        message (STATUS "CONAN_PROFILE: $ENV{preset}")
        # split the preset at th @
        string(REPLACE "@" ";" CONAN_PROFILE_LIST $ENV{preset})
        # the last element is the compiler
        list(GET CONAN_PROFILE_LIST -2 CONAN_COMPILER)
        # the second last element is the arch
        list(GET CONAN_PROFILE_LIST -1 CONAN_ARCH)
    endif()
    #if x86_64 make it x64 for windows for linux make it linux64 
    if (CONAN_ARCH STREQUAL "x86_64")
        set(CONAN_ARCH "x64")
    endif()

    if (CONAN_ARCH STREQUAL "x86_32")
        set(CONAN_ARCH "x32")
    endif()

    # autolib uses this in its name so we need to make sure that it is set correctly it uses old vc143 instead of the actual compiler
    if (CONAN_COMPILER STREQUAL "msvc193")
        set(CONAN_COMPILER "vc143")
    endif()

    message (STATUS "CONAN_COMPILER: ${CONAN_COMPILER}")
    message (STATUS "CONAN_ARCH: ${CONAN_ARCH}")
endif()

# define the compiler and arch as compile definitions

# an global settings target that can be used to set global settings
# by linking to it the linux define is used in code to turn on or off linux specific code
# and this is not defined by default by the operationg system
add_library(global_aimms INTERFACE)

target_compile_features(global_aimms
    INTERFACE 
        cxx_std_20
)

target_compile_definitions(global_aimms
    INTERFACE
        # define NDEBUG for release builds and RelWithDebInfo builds
        $<$<CONFIG:Release,RelWithDebInfo>:
            NDEBUG
        >

        # define DEBUG for debug builds
        $<$<CONFIG:Debug>:
            DEBUG
        >

        $<$<PLATFORM_ID:Linux>:
            LINUX
            LINUX64
            UNICODE
            _UNICODE
            GCC_HASCLASSVISIBILITY
        >

        # define conan compiler and arch
        CONAN_COMPILER="${CONAN_COMPILER}"
        CONAN_ARCH="${CONAN_ARCH}"
)

target_link_options(global_aimms
    INTERFACE 
        $<$<PLATFORM_ID:Linux>:
            LINKER:--no-undefined
            LINKER:--no-allow-shlib-undefined
        >
		
		# making sure that rounding in printf is as expected 
        $<$<PLATFORM_ID:Windows>:
            LINKER:legacy_stdio_float_rounding.obj
        >

)

# this makes sure that the one .pdb file that gets generated
# for static libraries is updated atomically upon parallel
# builds from Ninja
if(CMAKE_COMPILER_IS_MSVC)
    if(CMAKE_GENERATOR EQUALS "Ninja") 
        if ($<CONFIG:Debug,RelWitDebInfo>)
            set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /FS") 
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /FS") 
        endif()
    endif()
endif()

set_property(
  DIRECTORY 
  PROPERTY CMAKE_CONFIGURE_DEPENDS 
  "${CMAKE_SOURCE_DIR}/conanfile.py" 
)
