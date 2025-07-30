import os
import sys
import re
from .eprint import eprint
from .util import execute2
from .bash import find_bash

def git_branch_point(target_repo, branch_name, parent_branch_name):
    # Convert target_repo path to something that bash understands
    target_repo = re.sub(r'^([a-zA-Z]):\\', '/\\1/', target_repo)
    target_repo = target_repo.replace("\\", "/")

    this_script_dir = os.path.abspath(os.path.dirname(__file__))
    this_script = os.path.join(this_script_dir, "git_branch_point.sh")
    bash = find_bash()

    if(sys.platform == "win32"):
        return execute2([bash, this_script, target_repo, branch_name, parent_branch_name], get_output=True).strip()
    else:
        return execute2('%s %s %s %s %s' %
            (bash, this_script, target_repo, branch_name, parent_branch_name), get_output=True).strip()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        eprint("Usage: git_dir_head.py <target_repo> <branch_name> <parent_branch_name>")
        sys.exit(1)

    target_repo = sys.argv[1]
    branch_name = sys.argv[2]
    parent_branch_name = sys.argv[3]

    print((git_branch_point(target_repo, branch_name, parent_branch_name)))


# import os
# import sys
# import re
# from .eprint import eprint
# from .util import execute2
# from .bash import find_bash

# def git_branch_point(target_repo, branch_name, parent_branch_name):
#     # Convert target_repo path to something that bash understands
#     target_repo = re.sub(r'^([a-zA-Z]):\\', '/\\1/', target_repo)
#     target_repo = target_repo.replace("\\", "/")

#     this_script_dir = os.path.abspath(os.path.dirname(__file__))
#     this_script = os.path.join(this_script_dir, "git_branch_point.sh")
#     bash = find_bash()
#     print (" found bash at %s" % bash)

#     if(sys.platform == "win32"):
#         print ("branch_name: %s" % branch_name)
#         print ("parent_branch_name: %s" % parent_branch_name)
        
#         # ret = execute2([bash, this_script, target_repo, branch_name, parent_branch_name], get_output=True).strip()
#         # # execute command git rev-list --first-parent ${parent_branch_name} and get the last line
#         # subproccess = subprocess.Popen(["git", "rev-list", "--first-parent", parent_branch_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
#         # # get last line
#         # # subproccess = subproccess[len(subproccess) - 1].decode("utf-8").strip()
#         # print ("subprocess: %s" % subproccess)
        
#         # # same as above but with branch_name
#         # subproccess2 = subprocess.Popen(["git", "rev-list", "--first-parent", branch_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
#         # # subproccess2 = subproccess2[len(subproccess2) - 1].decode("utf-8").strip()
#         # print ("subprocess2: %s" % subproccess2)
        
#         # subproccess3 = subprocess.Popen(["git", "rev-list", "--first-parent", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
#         # print ("subprocess3: %s" % subproccess3)
        
#         # subproccess4 = subprocess.Popen(["git", "rev-list", "--first-parent", "develop"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
#         # print ("subprocess4: %s" % subproccess4)
        
#         # git checkout parent_branch_name and run git rev-list --first-parent ${parent_branch_name} and get the last line
#         # subproccess5 = subprocess.Popen(["git", "checkout", parent_branch_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
#         subproccess5 = subprocess.Popen(["git", "rev-list", parent_branch_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
#         print ("subprocess5: %s" % subproccess5)
        
#         # git checkout branch_name and run git rev-list --first-parent ${branch_name} and get the last line
#         # subproccess6 = subprocess.Popen(["git", "checkout", branch_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
#         subproccess6 = subprocess.Popen(["git", "rev-list", branch_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
#         print ("subprocess6: %s" % subproccess6)
        
#         # find all common values in both lists
#         ret2 = []
#         for i in subproccess5: 
#             for j in subproccess6:
#                 if i.decode("utf-8").strip() == j.decode("utf-8").strip():
#                     ret2.append(i.decode("utf-8").strip())
         
        
#         # get first of ret2
#         first_common_commit = ret2[0]
#         print ("first common commit: %s" % first_common_commit)
        
        
#         # print ("ret: %s" % ret)
#         return first_common_commit
#     else:
#         return execute2('%s %s %s %s %s' %
#             (bash, this_script, target_repo, branch_name, parent_branch_name), get_output=True).strip()

# if __name__ == "__main__":
#     if len(sys.argv) != 4:
#         eprint("Usage: git_dir_head.py <target_repo> <branch_name> <parent_branch_name>")
#         sys.exit(1)

#     target_repo = sys.argv[1]
#     branch_name = sys.argv[2]
#     parent_branch_name = sys.argv[3]

#     print((git_branch_point(target_repo, branch_name, parent_branch_name)))
