
import os
import platform
import random
import time
import requests

def exportDebugFilesToArtifactory(
        debugFolder,
        product,
        toolset,
        version,
        artifactoryUrl = "https://artifactory.platform.aimms.com:443/artifactory/aimms-linux-debug/"):
    try:
        # Read credentials from environment variables
        username = os.environ.get("ARTIFACTORY_USERNAME")
        password = os.environ.get("ARTIFACTORY_PASSWORD")

        if not (username and password):
            print("Error: ARTIFACTORY_USERNAME and ARTIFACTORY_PASSWORD environment variables are not set.")
            return

        auth = (username, password)

        for root, _, files in os.walk(debugFolder):
            for file in files:
                print(f"Checking {file}")

            for file in [f for f in files if f.endswith(".debug")]:
                debugFile = os.path.abspath(os.path.join(root, file))
                debugFile = os.path.normpath(debugFile).replace("\\", "/")
                debugFileRelative = os.path.relpath(debugFile, debugFolder)
                debugFileRelative = os.path.normpath(debugFileRelative).replace("\\", "/")
                debugFileUrl = artifactoryUrl + product + "-" + toolset + "-" + version + "/" + debugFileRelative
                nMaxAttemps = 9
                sleepSeconds = random.randint(5,15)
                for i in range(1,nMaxAttemps):
                    print("Uploading " + debugFile + " to " + debugFileUrl)
                    with open(debugFile, 'rb') as f:
                        response = requests.put(debugFileUrl, data=f, auth=auth)
                        if response.status_code == 201:
                            break
                    print("Trying again in %d seconds" % sleepSeconds)
                    time.sleep(sleepSeconds)
                else:
                    print("Error: Failed to upload " + debugFile + " to " + debugFileUrl + " (status code " + str(response.status_code) + ")")

    except Exception as e:
        print(f"Error: {e}")

def linux_debug_info_d(debugFolder, product, toolset, version):
    # if platform.system() == "Linux":
        exportDebugFilesToArtifactory(debugFolder, product, toolset, version)
        for root, _, files in os.walk(debugFolder):
            for file in files:
                if file.endswith(".debug"):
                    os.remove(os.path.join(root, file))
                    print("Removed " + file)

     


    