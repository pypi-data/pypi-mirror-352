import os
import platform
import subprocess

from buildhelpers import gitinfo

def upload_wheel():
    # Add /home/gitlab-runner/.local/bin to PATH only on Linux
    if platform.system() == "Linux":
        os.environ["PATH"] = f"/home/gitlab-runner/.local/bin:{os.environ.get('PATH', '')}"
    
    compiler, arch = os.getenv("preset").split('@')
    build_type = os.getenv("build_type")
    
    # Skip uploading if build_type is Debug
    if build_type == "Debug":
        print("Skipping upload as the build type is Debug.")
        return
    
    dist_folder = os.path.join(os.getcwd(), 'dist')
    if not os.path.exists(dist_folder):
        raise FileNotFoundError("The 'dist' folder does not exist. Please ensure the build was successful and the wheel is present.")
    
    os.chdir(dist_folder)

    try:
        branch = gitinfo.gitinfo().fullBranchName
        print (f"Branch: {branch}")
        print (f"Dist folder: {dist_folder}")
        if branch == 'master' or branch == 'main':
            print("Uploading to PyPI...")
            subprocess.check_call(['twine', 'upload', os.path.join(dist_folder, '*'), '--verbose'])

        print("Uploading to Artifactory...")
        if not os.getenv("ARTIFACTORY_USERNAME") or not os.getenv("ARTIFACTORY_PASSWORD"):
            raise EnvironmentError("ARTIFACTORY_USERNAME and ARTIFACTORY_PASSWORD must be set for uploading to Artifactory.")
        
        os.environ["TWINE_USERNAME"] = os.getenv("ARTIFACTORY_USERNAME")
        os.environ["TWINE_PASSWORD"] = os.getenv("ARTIFACTORY_PASSWORD")
        subprocess.check_call(['twine', 'upload', '*', '--verbose', '--repository-url', 'https://artifactory.platform.aimms.com/artifactory/api/pypi/pypi-local'])
    except subprocess.CalledProcessError as e:
        print(f"Error uploading the wheel: {e}")
        raise

if __name__ == "__main__":
    upload_wheel()
