import os
import json
import argparse
import platform

def create_launch_json(launch_path):
    launch_json = {
        "version": "0.2.0",
        "configurations": []
    }

    os.makedirs(os.path.dirname(launch_path), exist_ok=True)
    with open(launch_path, "x") as f:
        json.dump(launch_json, f, indent=4)

def update_launch_json(launch_path, name, preset, version, config, working_dir, environment):
    with open(launch_path, 'r') as f:
        data = json.load(f)

    input_found = False
    # Search for the 'inputs' array and the 'PickAimmsVersion' ID
    for input in data.get('inputs', []):
        if input.get('id') == 'PickAimmsVersion':
            # If the new version is not already in the 'options' array, append it
            input_found = True
    
    if not input_found:
        new_config_name = f'Launch {name} with {version} {config } {platform.system()} AIMMS (Generated)'
        if (new_config_name) in [ config['name'] for config in data['configurations'] ]:
            # remove old config
            data['configurations'] = [ config for config in data['configurations'] if not config['name'] == new_config_name ]


        new_config = {}
        
        new_config['name'] = new_config_name
        new_config['request'] = 'launch'
        new_config['cwd'] = working_dir

        if platform.system() == 'Windows':
            new_config['type'] = 'cppvsdbg'
            new_config['program'] = f'${{workspaceFolder}}/aimms/{version}/{config}/Bin/aimms.exe'
            new_config['args'] = [ 
                f'{name}_{preset}_{config}.aimms', 
            ]
            new_config['environment'] = [
                { 'name': 'PATH', 'value': environment}
            ]
        elif platform.system() == 'Linux':
            new_config['type'] = 'cppdbg'
            new_config['program'] = f'${{workspaceFolder}}/aimms/{version}/{config}/Bin/AimmsCmd'
            new_config['args'] = [
                "--logcfg",
                f"${{workspaceFolder}}/buildhelpers/autolibs/AimmsLogConfig.xml",
                "--alluser-dir",
                f"${{workspaceFolder}}/buildhelpers/autolibs/aimmsroot",
                "--aimms-root-path",
                f"${{workspaceFolder}}/buildhelpers/autolibs/aimmsroot", 
                "--aimmsunit::RunAllTests",
                "1",
                f'{name}_{preset}_{config}.aimms', 
            ]
            
            new_config['visualizerFile'] = '${{workspaceFolder}}/buildhelpers/cmake/linux_stl.natvis'
            new_config['showDisplayString'] = True
            new_config['environment'] = [
                { 'name': 'LD_LIBRARY_PATH', 'value': environment}
            ]

        if 'configurations' not in data:
            data['configurations'] = [new_config]
        else:
            data['configurations'].append(new_config)
    else:
        for input in data.get('inputs', []):
            if input.get('id') == 'PickAimmsVersion':
                # If the new version is not already in the 'options' array, append it
                if version not in input.get('options', []):
                    input['options'].append(version)
                    input['default'] = version

    with open(launch_path, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # add an positional argumant that is the path of the aimms project
    parser.add_argument("path", help="Path to the launch.json")
    parser.add_argument("--name", help="Name of the autolibrary")
    parser.add_argument("--preset", help="Preset used for the build")
    parser.add_argument("--version", help="AIMMS version that should be added to launch.json")
    parser.add_argument("--config", help="AIMMS configuration that should be added to launch.json")
    parser.add_argument("--working_dir", help="Working directory for the launch configuration")
    parser.add_argument("--environment", help="Path environment variable for the launch configuration")
    args = parser.parse_args()

    # check if path is a valid path
    if not os.path.exists(args.path):
        create_launch_json(args.path)

    update_launch_json(args.path, args.name, args.preset, args.version, args.config, args.working_dir, args.environment)