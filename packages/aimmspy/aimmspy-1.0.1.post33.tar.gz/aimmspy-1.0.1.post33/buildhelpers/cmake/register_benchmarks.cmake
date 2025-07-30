# register benchmark function
function(register_benchmark)

    set(options)	
    set(oneValueArgs NAME BENCHMARK_FILTER TIMEOUT)
    set(multiValueArgs LINKS SOURCES APPEND_PATHS COPY_FILES)
    cmake_parse_arguments(REGISTER_BENCHMARK "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

	set(NAME_EXTRAS "_benchmarks")

	#if target not exists create it
	if (NOT TARGET ${REGISTER_BENCHMARK_NAME}${NAME_EXTRAS})
		add_executable( ${REGISTER_BENCHMARK_NAME}${NAME_EXTRAS}
			$<IF:$<BOOL:${REGISTER_BENCHMARK_SOURCES}>,
				${REGISTER_BENCHMARK_SOURCES},
				${CMAKE_CURRENT_SOURCE_DIR}/benchmark/benchmarks.cpp
			>
		)

		target_link_libraries( ${REGISTER_BENCHMARK_NAME}${NAME_EXTRAS}
			PRIVATE
                benchmark::benchmark_main
				${REGISTER_BENCHMARK_LINKS}
		)

		target_compile_definitions( ${REGISTER_BENCHMARK_NAME}${NAME_EXTRAS}
			PRIVATE
				PROJECT_ROOT_DIR="${CMAKE_SOURCE_DIR}"
				#  _DISABLE_VECTOR_ANNOTATION
		)

		target_compile_features( ${REGISTER_BENCHMARK_NAME}${NAME_EXTRAS}
			PUBLIC
				cxx_std_20
		)

		target_link_options( ${REGISTER_BENCHMARK_NAME}${NAME_EXTRAS}
			PRIVATE
				$<$<CXX_COMPILER_ID:MSVC>:/ignore:4099>
		)

		# turn of link time optimization
		set_target_properties(${REGISTER_BENCHMARK_NAME}${NAME_EXTRAS} PROPERTIES INTERPROCEDURAL_OPTIMIZATION ON)

	else()
		target_sources( ${REGISTER_BENCHMARK_NAME}${NAME_EXTRAS}
			PRIVATE
				$<IF:$<BOOL:${REGISTER_BENCHMARK_SOURCES}>,
					${REGISTER_BENCHMARK_SOURCES},
					${CMAKE_CURRENT_SOURCE_DIR}/benchmark/benchmarks.cpp
				>
		)

		target_link_libraries( ${REGISTER_BENCHMARK_NAME}${NAME_EXTRAS}
			PRIVATE
                benchmark::benchmark_main
				${REGISTER_BENCHMARK_LINKS}
		)
	endif()
endfunction()
