import subprocess
import logging
import semver
import json
import sys
import datetime

log = logging.getLogger(__name__)

def parse_to_semver(version) -> semver.Version:
    if semver.Version.is_valid(version):
        return semver.Version.parse(version)

    # remove leading 'cci.' if present
    if version.startswith('cci.'):
        version = version.split('.')[1]

    # add patch version if not present
    if len(version.split('.')) == 2:
        version += '.0'
    elif len(version.split('.')) > 2:
        # remove leading zero's to make sure semver can parse it
        major, minor, patch = version.split('.')
        pre_release = None
        if '-' in patch:
            patch, pre_release = patch.split('-')

        major = int(major)
        minor = int(minor)
        patch = int(patch)

        version = f'{major}.{minor}.{patch}'

        if pre_release:
            version += f'-{pre_release}'

    if semver.Version.is_valid(version):
        return semver.Version.parse(version)

    # If still not semver compatible, then it is most likely a date
    try:
        if version == 'latest':
            date = datetime.datetime.now()
        else:
            date = datetime.datetime.strptime(version, '%Y%m%d')
    except ValueError:
        # if not a date, then it might be an integer version (example: 255)
        if version.isdigit():
            return semver.version.Version(int(version), 0, 0)
        raise ValueError(f'{version} could not be parsed to semver.')
    return semver.version.Version(0, 0, 0, date.strftime('%Y%m%d'))

def append_to_query(query, new_query):
    if query:
        query += f' AND {new_query}'
    else:
        query = new_query

    return query

def get_latest_version_artifactory(package, channel, cmake_preset=None, build_type=None, operating_system=None) -> semver.Version:
    query = ''
    
    if cmake_preset:
        compiler = cmake_preset.split('@')[0]
        # get the compiler version its the numbers after the compiler name so gcc11 becomes 11 msvc193 becomes 193
        compiler_version = ''.join(filter(str.isdigit, compiler))
        compiler_name = ''.join(filter(str.isalpha, compiler))
        
        arch = cmake_preset.split('@')[1]
        query = append_to_query(query, f'arch={arch} AND compiler={compiler_name} AND compiler.version={compiler_version}')
    
    if build_type:
        query = append_to_query(query, f'build_type={build_type}')
    
    if operating_system:
        query = append_to_query(query, f'os={operating_system}')

    args = ['conan', 'list', '-rconan-intra', '-f' , 'json']

    full_package = f'{package}/*@aimms/{channel}'
    if query:
        full_package += ':*'
        args += ['-p', query]
        
    args += [full_package]

    log.info(f'Running: {" ".join(args)}')
    ret = subprocess.run(args, capture_output=True, text=True)

    all_versions = []

    if ret.returncode == 0:
        conan_list = json.loads(ret.stdout)
        conan_intra_list = conan_list['conan-intra']

        if 'error' in conan_intra_list:
            log.warning(f'conan list -rconan-intra failed: {conan_intra_list["error"]}')
            return None

        for reference in conan_intra_list.keys():
            name_and_version  = reference.split('@')[0]
            version = name_and_version.split('/')[1]
            try:
                version = parse_to_semver(version)
            except ValueError:
                log.warning(f'Could not parse version {version} from artifactory to semver')
                continue

            if query:
                for revision in conan_intra_list[reference]['revisions'].keys():
                    if len(conan_intra_list[reference]['revisions'][revision]['packages']) > 0:
                        all_versions.append(version)
            else:
                all_versions.append(version)
    else:
        log.warning(f'conan list failed: {ret.stderr.rstrip()}')

    if len(all_versions) > 0:
        latest_version = max(all_versions)

        log.info(f'{package} has latest version on Artifactory: {latest_version}')
        return latest_version
    else:
        log.info(f'Could not find any versions for {package} with the {channel} channel on Artifactory')
        return None

def quit_job_if_on_artifactory(package_name, version, package_channel, cmake_preset=None, build_type=None, operating_system=None, quit_with_error=True):
    latest_artifactory_version = get_latest_version_artifactory(package_name, package_channel, cmake_preset, build_type, operating_system)

    if latest_artifactory_version and version <= latest_artifactory_version:
        print(f""""
====================================================================================================================================================================================
              
    Trying to build and upload {package_name}/{version}@aimms/{package_channel}, while the latest version in artifactory is already {package_name}/{latest_artifactory_version}@aimms/{package_channel}.    
    It is not allowed to upload a package with the same or lower version as the latest version in artifactory, even if the revision has changed. Please bump the version number.

====================================================================================================================================================================================               
""")
        if quit_with_error:
            sys.exit(1)
        else:
            sys.exit(0)
