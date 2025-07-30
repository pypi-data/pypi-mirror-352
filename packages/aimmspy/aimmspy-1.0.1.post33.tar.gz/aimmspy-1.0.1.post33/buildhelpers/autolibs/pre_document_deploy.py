import os
import sys
import argparse

sys.path.append(os.getcwd() + "/buildhelpers")
import internal.gitinfo as gitinfo

import os
import sys
import gitlab

# Retrieve environment variables for the project ID, default branch, and default file path.
# If these environment variables are not set, use default values.
# PROJECT_ID: The ID of the GitLab project. Default is 982.
# DEFAULT_BRANCH: The name of the default branch in the GitLab project. Default is "develop".
# DEFAULT_FILE_PATH: The path to the release notes file in the GitLab project. Default is "/release-notes/release-notes-scn.rst".
PROJECT_ID = int(os.getenv("PROJECT_ID", "982"))
# DEFAULT_BRANCH = os.getenv("DEFAULT_BRANCH", "develop")
# DEFAULT_FILE_PATH = os.getenv("DEFAULT_FILE_PATH", "/release-notes/release-notes-scn.rst")

def update_release_notes(file_content, file_path, git_version, branch):
    """
    Updates the release notes in a GitLab project.

    Returns:
        None
    """
    # Initialize a GitLab instance using the provided URL and private token.
    # The private token is retrieved from the environment variable "CI_JOB_TOKEN".
    # If the token is not valid or not provided, the script will exit with status code 1.
    try:
        gl = gitlab.Gitlab('https://gitlab.aimms.com', private_token=os.getenv("CI_WEBUI_COMMIT_TOKEN", None))
    except gitlab.GitlabAuthenticationError as e:
        print(e)
        sys.exit(1)

    # Retrieve the GitLab project using the provided project ID.
    # If the project ID is not valid or not provided, the script will exit with status code 1.
    project = gl.projects.get(PROJECT_ID)
    branch = project.branches.get(branch)


    print(f"Updating release notes for testing.")
    # Prepare the data for the commit. This includes the branch name, commit message, and actions.
    # The action is set to 'update' and the file path is set to the default file path.
    # The content of the file is read from the 'release-notes-scn.rst' file in the current working directory.
    data = {
        'branch': branch.name,
        'commit_message': f'[skip ci] Update version in release notes {git_version}',
        'actions': [
            {
                'action': 'update',
                'file_path': file_path,
                'content': file_content,
            }
        ]
    }
    
    try:
        # Try to update the file with the new release notes.
        commit = project.commits.create(data)
        
        # increase the git 3 number version by 1
        git_version = git_version.split(".")
        # should be an array of 4 elements change the third element
        git_version[2] = str(int(git_version[2]) + 1)
        git_version = ".".join(git_version)
        
        print (f"New version tag: {git_version}")
        
        # try adding a tag to the commit
        tag = project.tags.create({'tag_name': f"release-{git_version}", 'ref': commit.id, 'message': f"release-{git_version}"})
    except gitlab.GitlabCreateError as e:
        # If the file does not exist, create a new one with the release notes.
        print (f"Error: {e}")
        exit(1)


def main(args):
    git_version = gitinfo.gitinfo().getVersion().replace("-", ".")
    branch = gitinfo.gitinfo().getFullBranchName()
    # get the line number of the placeholder and insert below it a new version

    print (f"Git version: {git_version}")
    print (f"Branch: {branch}")

    placeholder = "[PLACEHOLDER_NEXT_VERSION]"
    
    if args.check:
        # check if on master main and release manager triggered the job
        if branch in ["master", "main", "feature/cppteam/webui_as_autolib"] and os.environ.get("CI") == "true":
            # get release managers env and person who triggered the job
            release_managers = os.getenv("RELEASE_MANAGER_NAMES", "").split(";")
            gitlab_user_name = os.getenv("GITLAB_USER_NAME", "")
            ci_job_manual = os.getenv("CI_JOB_MANUAL", None)
            print(f"RELEASE_MANAGER_NAMES: {release_managers}")
            print(f"GITLAB_USER_NAME: {gitlab_user_name}")
            print(f"CI_JOB_MANUAL: {ci_job_manual}")
            
            if gitlab_user_name in release_managers and ci_job_manual == "true":
                print(f"Release manager {gitlab_user_name} triggered the job")
            else:
                print("Release manager did not trigger the job")
                sys.exit(1)
        else:
            print("Not on master or main branch so stopping the job")
            sys.exit(1)
    
    if args.pre:
        # check if placeholder is not in the file because than fail the build
        with open(args.release_notes_file, "r") as file:
            data = file.read()
            if placeholder not in data:
                print(f"Error: Placeholder {placeholder} is not in the release notes file {args.release_notes_file}")
                sys.exit(1)

        to_insert = placeholder.replace("[PLACEHOLDER_NEXT_VERSION]", git_version)

        with open(args.release_notes_file, "r") as file:
            data = file.read()
            data = data.replace(placeholder, to_insert)

        with open(args.release_notes_file, "w") as file:
            file.write(data)
            
    if args.post:
        
        # find the last version and append before it the placeholder
        
        # check if placeholder is already in the file because than fail the build
        with open(args.release_notes_file, "r") as file:
            data = file.read()
            if placeholder in data:
                print(f"Error: Placeholder {placeholder} is already in the release notes file {args.release_notes_file}")
                sys.exit(1)
        
        header_copy = ""
        
        with open(args.release_notes_file, "r") as file:
            data = file.readlines()
            for i, line in enumerate(data):
                # if line has string RELEASE NOTES FOR {version} in it than copy line above and below that line and append before it the placeholder
                if f"RELEASE NOTES FOR {git_version}" in line:
                    header_copy = data[i-1] + data[i] + data[i+1]
                    break
                
        with open(args.release_notes_file, "r") as file:
            data = file.read()
            placeholder = header_copy.replace(git_version, placeholder)
            data = data.replace(header_copy, f"{placeholder}\n\n{header_copy}") 
            
        with open(args.release_notes_file, "w") as file:
            file.write(data)
            
        # if on master main or feature/cppteam/webui_as_autolib also commit the file to the repo
        if branch in ["master", "main", "feature/cppteam/webui_as_autolib", "feature/future"] and os.environ.get("CI") == "true":
            # print("DEEEEBBBBUUUUUUGGGGG")
            print(f"Updating release notes in GitLab branch {branch}")
            update_release_notes(data, args.release_notes_file, git_version, branch)
            pass


if __name__ == '__main__':
    
    
    # argparse get release notes file
    parser = argparse.ArgumentParser(description='Inserts the next version in the release notes file')
    parser.add_argument('--release_notes_file', type=str, help='The release notes file to update', required=True)
    # add options for pre and post deploy
    # option pre
    parser.add_argument('--pre', action='store_true', help='Pre deploy')
    # option post
    parser.add_argument('--post', action='store_true', help='Post deploy')
    # option check
    parser.add_argument('--check', action='store_true', help='Check if release manager triggered the job')
    args = parser.parse_args()
    
    # normalize the path
    args.release_notes_file = os.path.normpath(args.release_notes_file)
    
    main(args)
