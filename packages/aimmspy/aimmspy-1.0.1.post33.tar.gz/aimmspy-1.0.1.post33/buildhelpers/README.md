# buildhelpers 

To be used as a submodule of a C++ repository  

To get started with cmake/conan in your project, go to the templates folder, copy and adapt: 

addon_for_gitlab-ci.yml:   
extension for you existing gitlab-ci.yml to create some conan cmake jobs 

other files in templates folder:   
copy these to your root folder 

CmakeSettings.json:     
Visual Studio will use this file when opening the project as cmake. It contains settings to build Windows vc141 Release and Debug  and Linux gcc61 with WSL. 

remaining files: see descriptions in the files themselves

src folder:    
Each project will need a CMakeLists.txt, these are examples for the different flavors.


