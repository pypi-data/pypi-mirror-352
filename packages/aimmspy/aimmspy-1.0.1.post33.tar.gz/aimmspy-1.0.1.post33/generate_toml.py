import jinja2
import argparse

import sys
import os
import json

sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers"))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "conan"))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "cmake"))

import buildhelpers.gitinfo as gitinfo

semver_version = gitinfo.gitinfo().getVersion()

# Define the template file and output file paths
template_file = 'pyproject.jinja'
output_file = 'pyproject.toml'

# print all environment variables
# print("Environment Variables:")
# for key, value in os.environ.items():
#     print(f"{key}: {value}")

# Set up argument parser
parser = argparse.ArgumentParser(description='Generate pyproject.toml from a Jinja2 template.')
parser.add_argument('--version', type=str, default=semver_version, help='Version to use in the template')
parser.add_argument('--conan_profile', type=str, default=os.getenv('conan_profiles_path'), help='Conan profile to use in the template')
parser.add_argument('--conan_build_type', type=str, default=os.getenv('build_type'), help='Conan build type to use in the template')
parser.add_argument('--dry', action='store_true', help='Run the command to generate the file')

args = parser.parse_args()

if not args.conan_profile:
    raise ValueError('Conan profile is required')

if not args.conan_build_type:
    raise ValueError('Conan build type is required')

os.environ["CONAN_BUILD"] = "True"
os.environ["CONAN_HOST_PROFILE_PATH"] = os.path.join(args.conan_profile, args.conan_build_type)
os.environ["CONAN_BUILD_PROFILE_PATH"] = os.path.join(args.conan_profile, 'build')

# normalize the conan profile path to /
args.conan_profile = args.conan_profile.replace("\\", "/")

file_path = os.path.join(os.getcwd(), 'buildhelpers', 'cmake', 'aimms_presets.json')
# Read the JSON file
with open(file_path, 'r') as file:
    data = json.load(file)

# Get the value for MINIMUM_CMAKE_VERSION
minimum_cmake_version = data['configurePresets'][0]['cacheVariables']['MINIMUM_CMAKE_VERSION']


# Define the values to be used in the template
context = {
    'version': args.version,
    'conan_profile': args.conan_profile,
    'conan_build_type': args.conan_build_type,
    'minimum_cmake_version': minimum_cmake_version
}

# Load the Jinja2 template
with open(template_file) as file_:
    template = jinja2.Template(file_.read())

# Render the template with the context values
rendered_content = template.render(context)

# Write the rendered content to the output file
with open(output_file, 'w') as file_:
    file_.write(rendered_content)

print(f'{output_file} has been generated successfully.')

