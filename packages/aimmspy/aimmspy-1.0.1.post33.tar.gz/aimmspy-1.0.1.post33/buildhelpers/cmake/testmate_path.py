import argparse
import json
import logging
import platform
import os
import subprocess

logger = logging.getLogger(__name__)

def get_git_url():
    try:
        output = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], stderr=subprocess.STDOUT)
        return output.decode().strip()
    except subprocess.CalledProcessError as e:
        logger.error("Error executing git command: " + str(e))
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", help="paths that should be added for testmate")
    parser.add_argument("--file", help="file where the paths should be stored")
    parser.add_argument("--config", help="the cmake configuration that should be used")
    args = parser.parse_args()

    paths = args.paths
    wrong_config_types = [ config_type for config_type in [ "Debug", "Release", "RelWithDebInfo", "MinSizeRel" ] if not config_type == args.config ]
    for config_type in wrong_config_types:
        paths = paths.replace(config_type, args.config)


    current_path = ""
    data = {}

    ENV_KEYLESS_SERVER_LICENSE = ""
    ENV_TEST_DIR = ""

    if get_git_url() == "git@gitlab.aimms.com:aimms/aimms.git":
        ENV_KEYLESS_SERVER_LICENSE = os.path.dirname(os.path.dirname(args.file)) + "/keylessLicense"
        ENV_TEST_DIR = os.path.dirname(os.path.dirname(args.file)) + "/webui/cube-engine/tests/models"
        
    
    # check if file is already opened by another process
    try:
        with open(args.file, "r") as f:
            pass
    except Exception as e:
        # logger.error(e)
        # traceback.print_exc()
        exit(0)
    
    """
    Opens the file in read mode and loads the JSON data.
    """
    try:
        with open(args.file, "r") as f:
                data = json.load(f)
                
                if platform.system() == "Windows":
                    current_path = data["PATH"]
                    for path in paths.split(";"):
                        if path not in current_path:
                            current_path += (path + ";")
                elif platform.system() == "Linux":
                    current_path = data["LD_LIBRARY_PATH"]
                    for path in paths.split(":"):
                        if path not in current_path:
                            current_path += (path + ":")
                        
    except Exception as e: 
        logger.error("Test viewer might not work completely. Please check the file: " + args.file)


    """
    Opens the file in write mode and dumps the updated JSON data. 
    If the platform is Windows, it updates the PATH variable.
    If the platform is Linux, it updates the LD_LIBRARY_PATH variable.
    """
    try:
        with open(args.file, "w") as f:
                if platform.system() == "Windows":
                    current_path.replace(";;", ";")
                    current_path.replace(" ", ";")
                    data["PATH"] = current_path
                elif platform.system() == "Linux":
                    current_path.replace(";", ":")
                    current_path.replace("::", ":")
                    current_path.replace(" ", ":")
                    current_path.replace("\t", ":")
                    current_path.replace("\n", ":")
                    data["LD_LIBRARY_PATH"] = current_path
                
                if ENV_KEYLESS_SERVER_LICENSE:
                    data["KEYLESS_LICENSE_DIR"] = ENV_KEYLESS_SERVER_LICENSE
                    
                if ENV_TEST_DIR:
                    data["TESTPROJECT_ROOT_DIR"] = ENV_TEST_DIR
                json.dump(data, f, indent=4)
    except Exception as e:
        logger.error("Test viewer might not work completely. Please check the file: " + args.file)

    """
    If the platform is Windows, it creates a .runsettings file with the updated PATH variable.
    """
    try:
        if platform.system() == "Windows":
            file_path = os.path.join(os.path.dirname(args.file), "envfile_" + args.config + ".runsettings")

            xml_file = open(file_path, "w")
            xml_file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
            xml_file.write("<RunSettings>\n")
            xml_file.write("    <RunConfiguration>\n")
            xml_file.write("        <EnvironmentVariables>\n")
            xml_file.write("            <PATH>" + current_path + "</PATH>\n")
            if ENV_KEYLESS_SERVER_LICENSE:
                xml_file.write("            <KEYLESS_LICENSE_DIR>" + ENV_KEYLESS_SERVER_LICENSE + "</KEYLESS_LICENSE_DIR>\n")
            if ENV_TEST_DIR:
                xml_file.write("            <TESTPROJECT_ROOT_DIR>" + ENV_TEST_DIR + "</TESTPROJECT_ROOT_DIR>\n")
            xml_file.write("        </EnvironmentVariables>\n")
            xml_file.write("    </RunConfiguration>\n")
            xml_file.write("</RunSettings>\n")
            xml_file.close()
    except Exception as e:
        logger.error("Test viewer might not work completely. Please check the file: " + file_path)
        
