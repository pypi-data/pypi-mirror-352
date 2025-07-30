import os
import sys
import re
from .eprint import eprint
from .util import execute2
from .bash import find_bash

def git_dir_head(target_repo, start_commit_hash, path):
    # Convert target_repo path to something that bash understands
    target_repo = re.sub(r'^([a-zA-Z]):\\', '/\\1/', target_repo)
    target_repo = target_repo.replace("\\", "/")

    # Make sure path is relative to the target_repo
    if os.path.isabs(path):
        path = os.path.relpath(path, target_repo)

    if path != '.' and not path.endswith('/'):
        path = path + '/'

    path = path.replace("\\", "/")

    this_script_dir = os.path.abspath(os.path.dirname(__file__))
    this_script = os.path.join(this_script_dir, "git_dir_head.sh")
    bash = find_bash()

    if(sys.platform == "win32"):
        return execute2([bash, this_script, target_repo, start_commit_hash, path], get_output=True).strip()
    else:
        return execute2('%s %s %s %s %s' %
            (bash, this_script, target_repo, start_commit_hash, path), get_output=True).strip()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        eprint("Usage: git_dir_head.py <target_repo> <start_commit_hash> <path>")
        sys.exit(1)

    target_repo = sys.argv[1]
    start_commit_hash = sys.argv[2]
    path = sys.argv[3]

    print((git_dir_head(target_repo, start_commit_hash, path)))
