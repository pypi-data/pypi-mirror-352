import argparse
import os
import json
import platform

def main(args):
        
    #read json file conan_install_output_Debug.json
    conan_install_output_Debug = os.path.join(args.conan_config_dir, f"conan_install_output_{args.configuration}.json")
    
    # read file and purge everything before first { and after last }
    json_string = ''
    with open(conan_install_output_Debug, 'rb') as f:
        string = f.read()
        
        # find first occurrence of { 
        start = string.find(b'{')
        last = string.rfind(b'}')
        
        # remove everything before first { and after last }
        json_string = string[start:last+1]
        
    # parse json
    data = json.loads(json_string)
    
    node0 = data['graph']['nodes']['0']
    node0_deps = node0['dependencies']
    node0_deps_numbers = []
    node0_direct_deps_numbers = []
    node0_cmake_append_path_nums = []
    node0_cmake_append_build_path_nums = []
    cmake_find_package_names = []
    cmake_append_conan_paths = []
    cmake_build_tools_paths = []
    
    for dep in node0_deps:
        node0_deps_numbers.append(dep)
    
    for node0_deps_number in node0_deps:
        
        if node0_deps[node0_deps_number]['direct'] and not node0_deps[node0_deps_number]['skip'] and (not node0_deps[node0_deps_number]['build'] or node0_deps[node0_deps_number]['test']):
            node0_direct_deps_numbers.append(node0_deps_number)
        
        if not node0_deps[node0_deps_number]['skip'] and (not node0_deps[node0_deps_number]['build']):
            node0_cmake_append_path_nums.append(node0_deps_number)
            
        if node0_deps[node0_deps_number]['build']:
            node0_cmake_append_build_path_nums.append(node0_deps_number)
            
    # print (node0_direct_deps_numbers)
    # print (node0_cmake_append_path_nums)
    # print (node0_cmake_append_build_path_nums)
            
    for node0_direct_deps_number in node0_direct_deps_numbers:
        node_info = data['graph']['nodes'][node0_direct_deps_number].get('cpp_info')
        name = ''
        if node_info:
            root_info = node_info.get('root')
            if root_info:
                properties = root_info.get('properties')
                if properties:
                    cmake_file_name = properties.get('cmake_file_name')
                    if cmake_file_name:
                        name = cmake_file_name
        if not name:
            name = data['graph']['nodes'][node0_direct_deps_number]['name']
            
        if name:
            cmake_find_package_names.append(name)
                    
    for node0_cmake_append_path_num in node0_cmake_append_path_nums:
        
        # get package_type and continue if shared-library and application
        package_type = data['graph']['nodes'][node0_cmake_append_path_num].get('package_type')
        path = ''
        if  package_type == 'shared-library' or package_type == 'application':
            node_info = data['graph']['nodes'][node0_cmake_append_path_num].get('cpp_info')
            if node_info:
                root_info = node_info.get('root')
                if root_info: 
                    if platform.system() == 'Windows':
                        bindirs = root_info.get('bindirs')
                        if bindirs:
                            path = bindirs[0]
                    else:
                        libdirs = root_info.get('libdirs')
                        if libdirs:
                            path = libdirs[0]
                    
            if not path:
                package_folder_dir = data['graph']['nodes'][node0_cmake_append_path_num].get('package_folder')
                if package_folder_dir:
                    path = package_folder_dir
                    
        if path:
            cmake_append_conan_paths.append({ 'path': path, 'name': data['graph']['nodes'][node0_cmake_append_path_num]['name'] })
    
    for node0_cmake_append_build_path_num in node0_cmake_append_build_path_nums:
        node_info = data['graph']['nodes'][node0_cmake_append_build_path_num].get('cpp_info')
        path = ''
        if node_info:
            root_info = node_info.get('root')
            if root_info:
                bindirs = root_info.get('bindirs')
                if bindirs:
                    path = bindirs[0]
        
        if not path:
            package_folder_dir = data['graph']['nodes'][node0_cmake_append_build_path_num].get('package_folder')
            if package_folder_dir:
                path = package_folder_dir
                
        cmake_build_tools_paths.append({ 'path': path, 'name': data['graph']['nodes'][node0_cmake_append_build_path_num]['name'] })
    
    # make a json file with cmake_find_package_names and cmake_append_conan_paths
    cmake_config_file = os.path.join(args.conan_config_dir, f"conan_install_processed_{args.configuration}.json")
    with open(cmake_config_file, 'w') as f:
        json.dump({'cmake_find_package_names': cmake_find_package_names, 'cmake_append_conan_paths': cmake_append_conan_paths, 'cmake_build_tools_paths': cmake_build_tools_paths}, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get CMake config files")
    parser.add_argument("--conan_config_dir", type=str, help="Conan config directory")
    parser.add_argument("--configuration", type=str, help="CMake configuration")
    args = parser.parse_args()
    
    main(args)