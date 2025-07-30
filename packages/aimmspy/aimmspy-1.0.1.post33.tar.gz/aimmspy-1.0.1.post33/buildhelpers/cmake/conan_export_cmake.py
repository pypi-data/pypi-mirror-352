import os
import json
import argparse
from aimms_common import executeCmd, get_build_types, repo_dirty
from aimms_artifactory import quit_job_if_on_artifactory
import subprocess
import tempfile

def get_installed_presets(install_dir):
    installed_presets = []

    for preset in os.listdir(install_dir):
        preset_path = os.path.join(install_dir, preset)
        
        if os.path.isdir(preset_path):
            installed_presets.append(preset)

    return installed_presets
      
def get_conan_profile(profile, aimms_presets_path):
    with open(aimms_presets_path, 'r') as aimms_preset:
        aimms_presets = json.load(aimms_preset)

    for preset in aimms_presets['configurePresets']:
        if preset['name'] == profile:
            conan_profile = preset['cacheVariables']["CONAN_PROFILE"]

            # Conan profile is saved as ${sourceDir}/..
            # since we are parsing the aimms_presets.json file, ${sourceDir} is not available
            # so we remove it from the string
            return conan_profile.split('/', 1)[1]
    
    raise RuntimeError(f'Could not find conan profile for {profile}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--conan_file_dir", action='store', help='path to conanfile.py')
    parser.add_argument('--name', action='store', help='package name')
    parser.add_argument('--version', action='store', help='package version')
    parser.add_argument('--channel', action='store', help='package channel')
    parser.add_argument('--user', action='store', help='package user')
    parser.add_argument('--install_dir', action='store', help='path to install dir')
    # add option upload_if_different
    parser.add_argument('--upload_if_different', action='store_true', help='upload package if different')

    args = parser.parse_args()
    
    # in channel change all - to _
    args.channel = args.channel.replace('-', '_')

    quit_job_if_on_artifactory(args.name, args.version, args.channel)

    aimms_presets_path = os.path.join('buildhelpers', 'cmake', 'aimms_presets.json')
    conan_profiles_dir = os.path.join('buildhelpers', 'conan-profiles')

    installed_presets = get_installed_presets(args.install_dir)
    configuration_types = get_build_types()

    executeCmd("conan --version")
    executeCmd("conan remote list")

    repo_dirty()
    
    temp_dir = tempfile.gettempdir()

    full_package_name = f'{args.name}/{args.version}@{args.user}/{args.channel}'

    for preset in installed_presets:
        for config in configuration_types:
            profile_install_dir = os.path.join(args.install_dir, preset, config)

            if (os.path.isdir(profile_install_dir)):
                conan_profile = f'{get_conan_profile(preset, aimms_presets_path)}/{config}'
                repo_dirty()
                
                if args.upload_if_different:
                    ret = subprocess.run(['conan', 'export-pkg', '-vtrace', args.conan_file_dir, '--profile', conan_profile, '--name', args.name, '--version', args.version, '--user', args.user, '--channel', args.channel, f'--output-folder={profile_install_dir}', '--format', 'json'], capture_output=True, text=True)
                    
                    #  from ret.stdout make sure to remove everything before the first {  and after the last }
                    ret.stdout = ret.stdout[ret.stdout.find('{'):]
                    ret.stdout = ret.stdout[:ret.stdout.rfind('}')+1]
                    
                    conan_export_pkg_output = json.loads(ret.stdout)
                    
                    package_id = conan_export_pkg_output['graph']['nodes']['0']['package_id']
                    prev = conan_export_pkg_output['graph']['nodes']['0']['prev']
                    rrev = conan_export_pkg_output['graph']['nodes']['0']['rrev']
                        
                        
                    package_ids = []
                    prev_list = []
                    rrev_list = []
                    
                    if args.upload_if_different:
                        ret = subprocess.run(['conan', 'list', args.name + '/*#*:*#*', '-r', 'conan-intra', '--format', 'json'], capture_output=True, text=True)
                        #  from ret.stdout make sure to remove everything before the first {  and after the last }
                        ret.stdout = ret.stdout[ret.stdout.find('{'):]
                        ret.stdout = ret.stdout[:ret.stdout.rfind('}')+1]
                        
                        conan_packages = json.loads(ret.stdout)
                        # print (json.dumps(conan_packages, indent=4, sort_keys=True))
                        for cache in conan_packages.values():
                            for product in cache.values():
                                
                                for revision in product['revisions'].keys():
                                    # append revision key names to package_prev
                                    rrev_list.append(revision)
                                    
                                    for package_id in product['revisions'][revision]['packages'].keys():
                                        # Add the packages keys to package_ids
                                        package_ids.append(package_id)
                                        try:
                                            for prevs in product['revisions'][revision]['packages'][package_id]['revisions'].keys():
                                                prev_list.append(prevs)
                                        except Exception as e:
                                            print (e)

                    
                    print(f"Package prev: {rrev} and package prev: {rrev_list}")
                    print (f"Package ID: {package_id} and package IDS: {package_ids}")
                    print(f"Package revision: {prev} and package revisions: {prev_list}")
                    
                    if prev in prev_list:
                        print(f'Package {prev} looks to be the same as a package already uploaded. Skipping upload.')
                    else:
                        executeCmd(f"conan upload -vtrace {full_package_name} -r conan-intra --confirm")       
                else:
                    executeCmd(f"conan export-pkg -vtrace {args.conan_file_dir} --profile {conan_profile} --name {args.name} --version {args.version} --user {args.user} --channel {args.channel} --output-folder={profile_install_dir}")
                
                repo_dirty()
            else:
                raise RuntimeError(f'Could not find install dir for {preset} and {config}. Use aimms_install to install the package correctly.')

        repo_dirty()
    
    repo_dirty()
    
    if not args.upload_if_different:
        executeCmd(f"conan upload -vtrace {full_package_name} -r conan-intra --confirm")
    