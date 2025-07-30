# Helper functions for enabling visual studio static analysis rule sets
# Static analysis is only enabled when -DSTATIC_ANALYSIS:BOOL=TRUE is set
# on the cmake command line.

function(set_static_analysis_rules_directory directory_name)
	if(STATIC_ANALYSIS)
		message("Static analysis: ENABLED")
		message("Static analysis: Setting rulesets directory ${directory_name}")
		string(REPLACE "/" "\\" STATIC_ANALYSIS_RULES_DIRECTORY  "${directory_name}")
		add_compile_options(/analyze /analyze:rulesetdirectory"${STATIC_ANALYSIS_RULES_DIRECTORY}")
	endif()
endfunction()


function(set_static_analysis_rulefile target_name file_name)
	if(STATIC_ANALYSIS)
		message("Static analysis: ${target_name} Using ruleset: ${file_name}")
		target_compile_options(${target_name} PRIVATE /analyze:ruleset ${file_name})
	endif()
endfunction()