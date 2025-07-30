from internal.gitinfo import gitinfo
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', nargs="?", help='The thing to print [fullbranchname | branchname | branchtype | gitlike | version | commithash]', default="gitlike")
    parser.add_argument('--location', help='The location from which to run')

    args = parser.parse_args()

    gi = gitinfo(args.location)
    if args.action == "fullbranchname":
        
        # check if branch is all lower case
        fullBranchName = gi.getFullBranchName()
        if fullBranchName.islower():
            print((fullBranchName))
        else:
            raise ValueError ("Branch name cannot contain capital letters please change this to lowercase")
        
    elif args.action == "branchname":
        print((gi.getBranchName()))
    elif args.action == "branchtype":
        print((gi.getBranchType()))
    elif args.action == "gitlike":
        print((gi.toString()))
    elif args.action == "version":
        print((gi.getVersion()))
    elif args.action == "commithash":
        print((gi.getHash()))
    elif args.action == "commitmessage":
        print((gi.getMessage()))
    else:
        parser.print_help()
