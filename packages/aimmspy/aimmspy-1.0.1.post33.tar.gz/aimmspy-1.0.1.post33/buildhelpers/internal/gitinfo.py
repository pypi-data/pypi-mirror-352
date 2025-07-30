import os
import sys
import subprocess
import re
import subprocess
from subprocess import CalledProcessError
from .eprint import eprint
from functools import partial
from .util import execute2
import hashlib

execute = None
from .git_dir_head import git_dir_head
from .git_branch_point import git_branch_point

def executeCmd(command):
    try:
        return subprocess.check_output(command, shell=True).decode('utf-8')
    except CalledProcessError as ex:
        returncode = ex.returncode
        eprint("Exception: %s" % ex)
        if (not(returncode == 0)):
            eprint("Command '%s' did not exit normally, exit code %d." % (command,returncode) )
            sys.exit(returncode)

class NoSuchCommitError(Exception):
    pass


class gitinfo:
    def __init__(self, location = None, **options):
        # print ("gitinfo: location = %s" %location)
        # print ("gitinfo: options = %s" %options)
    # Do not write True below, the crappy web-gui build will break and nobody knows how it works.
        self.verbose = options.get('verbose', False)
        if not 'warnVersion' in options:
            self.warnVersion = location is None
        else:
            self.warnVersion = options.get('warnVersion', True)
        # print ("point 1")
        globals()['execute'] = partial(execute2, get_output=True, debug=self.verbose)

        if (not location and os.getenv("GITINFO_LOCATION")):
            location = os.getenv("GITINFO_LOCATION")

        if (location):
            self.component_location = location
        else:
            self.component_location = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir))
        # print("point 1")
        self.verbose_log("component_location = %s" %self.component_location)
        # print("point 3")
        self.gitLocation = self.determineGit()
        # print ("gitLocation = %s" %self.gitLocation)
        self.fullBranchName = self.priv_determineFullBranchName()

        if self.fullBranchName.startswith('renovate/'):
            # The major number must be 3 or 4, else AIMMS engine unit tests will fail
            # There is a check inside security whether the current AIMMS version is 3 or 4
            # Security\src\Security\src\SecFolders.cpp, line 902
            self.major = 4
            self.minor = 4
            self.release = 44444
            self.revision = 4

            self.hash = "0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad"
            self.message = "Renovating..."
            self.branchType = "renovate"
        else:
            # print ("fullBranchName = %s" %self.fullBranchName)
            self.friendlyBranchName = self.priv_determineFriendlyBranchName()
            # print ("friendlyBranchName = %s" %self.friendlyBranchName)
            self.branchType = self.priv_determineBranchType()
            # print ("branchType = %s" %self.branchType)

            brancheTypeToTagPrefixMap = {
                'master'  : 'release',
                'main'    : 'release',
                'hotfix'  : 'hotfix',
                'feature' : 'feature',
                'renovate': 'renovate',
                'develop' : 'develop',
                'release' : 'release',
                'support' : 'release',
                'other'   : 'other'
            }
            self.verbose_log("prefix : %s" %(brancheTypeToTagPrefixMap[self.branchType]))
            self.priv_determineVersion( brancheTypeToTagPrefixMap[self.branchType] )

    def verbose_log(self,msg):
        if(self.verbose):
            print(msg)

    def determineGit(self):
            gitversion = executeCmd('git --version').strip()
            if gitversion.startswith('git version '):
                gitversion = gitversion[12:]
            if gitversion < '1.8.5':
                if os.name.lower() == 'posix':
                    fileDir = os.path.dirname(os.path.realpath(__file__))
                    extendedPath = os.path.join(fileDir, 'gitexe')
                    #Extending path in order to include .so from the gitexe folder
                    if 'LD_LIBRARY_PATH' in os.environ:
                        os.environ["LD_LIBRARY_PATH"] += ':%s' % extendedPath if os.environ["LD_LIBRARY_PATH"].endswith(':') == False else '%s' % extendedPath
                    else:
                        os.environ["LD_LIBRARY_PATH"] = extendedPath
                    git = os.path.join(extendedPath, 'git')
                    return git
                else:
                    print(("Your Git version (%s) is too old, install the newest git version." %gitversion))
                    sys.exit(1)
            else :
                return "git"

    def gitExec(self, gitArgs, **kwargs):
        self.verbose_log("calling git: %s" %gitArgs)
        return execute('%s %s' % (self.gitLocation, gitArgs), **kwargs).strip()

    def toString(self):
        return "%d.%d.%d-%d-%s" % (self.major, self.minor, self.release, self.revision, self.hash )

    def getMajor(self):
        return self.major

    def getMinor(self):
        return self.minor

    def getRelease(self):
        return self.release

    def getRevision(self):
        return self.revision

    def getVersion(self):
        return "%d.%d.%d-%d" % (self.major, self.minor, self.release, self.revision)

    def getDotVersion(self):
        return f'{self.major}.{self.minor}.{self.release}.{self.revision}'

    def getBranchType(self):
        return self.branchType

    def getBranchName(self):
        return self.friendlyBranchName

    def getFullBranchName(self):
        return self.fullBranchName

    def getHash(self):
        return self.hash
        
    def getMessage(self):
        return self.message

    def priv_determineFullBranchName(self):
        branchName = executeCmd('%s rev-parse --abbrev-ref HEAD' % self.gitLocation).strip()
        # if we're on a detached head, the previous command will nog deliver a proper
        # result, fall back to determining the current branch ourselves
        if branchName=="HEAD":
            self.verbose_log("branchName is 'Head'...")
            # print ("gitinfo: warning: unable to determine branch name; falling back to detached head detection")
            branchName = os.getenv("CI_COMMIT_REF_NAME")
            if not branchName:
                
                # try to get branch name from CI_MERGE_REQUEST_SOURCE_BRANCH_NAME
                branchName = os.getenv("CI_MERGE_REQUEST_SOURCE_BRANCH_NAME")
                if not branchName:
                    branchName = self.priv_determineFullBranchNameDetached()
        return branchName

    def priv_determineFullBranchNameDetached(self):
        # print ("gitinfo: warning: unable to determine branch name; falling back to detached head detection 2")
        currentHash = executeCmd('%s rev-parse HEAD' % self.gitLocation).strip()

        allRawPotentialBranches = executeCmd('%s branch -r --contains %s' % (self.gitLocation, currentHash)).strip().splitlines()
        # print allRawPotentialBranches

        allPotentialBranches = []
        for b in allRawPotentialBranches:
            # print ("potential branch is = %s" %b)
            if not "detached" in b:
                if not "no branch" in b:
                    if not "->" in b:
                        if b.startswith("*"):
                            allPotentialBranches.append(b[1:].strip())
                        else:
                            allPotentialBranches.append(b.strip())
        #print allPotentialBranches

        if len(allPotentialBranches) > 1:
            branchMap = {}
            for b in allPotentialBranches:
                branchMap[ b ] = executeCmd('%s rev-parse %s' % (self.gitLocation, b) ).strip()

            revBranchMap = {}
            for name, hash in list(branchMap.items()):
                if hash not in revBranchMap:
                    revBranchMap[hash] = name
                else:
                    print(("gitinfo: error: unable to determine unique branch name; multiple candidates: %s and %s map to same hash" % (name, revBranchMap[hash])))
                    sys.exit(1)

            #print currentHash
            #print revBranchMap
            if currentHash not in revBranchMap:
                print("gitinfo: error: unable to determine branch name")
                sys.exit(1)
            foundName = revBranchMap[currentHash]
        elif len(allPotentialBranches) == 1 :
            foundName = allPotentialBranches[0]
        else :
            print ("gitinfo: error: unable to determine branch name ( no branches found )")
            sys.exit(1)

        # strip of remote/origin parts
        if foundName.startswith('origin/'):
            foundName = foundName[7:]
        if foundName.startswith('remotes/origin/'):
            foundName = foundName[15:]

        self.verbose_log("priv_determineFullBranchNameDetached foundName = %s" %foundName)
        return foundName

    def priv_determineBranchType(self):
        if self.fullBranchName.startswith(('feature/', 'heads/feature-')):
            return 'feature'
        if self.fullBranchName.startswith(('release/', 'heads/release-')):
            return 'release'
        if self.fullBranchName.startswith('renovate/'):
            return 'renovate'
        if self.fullBranchName.startswith('release/'):
            return 'release'
        if self.fullBranchName.startswith(('support/', 'heads/support-')):
            return 'support'
        if self.fullBranchName.startswith(('hotfix/', 'heads/hotfix-')):
            return 'hotfix'
        if self.fullBranchName == "develop":
            return 'develop'
        if self.fullBranchName == "master":
            return 'master'
        if self.fullBranchName == "main":
            return 'master'

        # other than git-flow branch type
        return 'other'

    def priv_determineFriendlyBranchName(self):
        if self.fullBranchName.startswith('feature/'):
            return self.fullBranchName[8:]
        if self.fullBranchName.startswith('renovate/'):
            return self.fullBranchName[9:]
        if self.fullBranchName.startswith('release/'):
            return self.fullBranchName[8:]
        if self.fullBranchName.startswith('support/'):
            return self.fullBranchName[8:]
        if self.fullBranchName.startswith('hotfix/'):
            return self.fullBranchName[7:]
        if self.fullBranchName == "develop":
            return 'develop'
        if self.fullBranchName == "master":
            return 'master'
        if self.fullBranchName == "main":
            return 'master'

        # return full branchname for non-git-flow branches
        return self.fullBranchName

    # In the mono-repo there are multiple buildtool submodules, git info
    # needs to figure which of the "projects" contains this particular module
    # and get the hash for that path in the git repository.
    # In the non-mono-repos this was always assumed to be the root of the repo;
    # this method will still respect this behaviour.)
    def priv_determineGitHashForVersion(self):
        projectThatOwnsThisBuildTool = self.component_location
        # print ("projectThatOwnsThisBuildTool = %s" %projectThatOwnsThisBuildTool)
        currentCommitHash = self.gitExec('rev-parse HEAD').strip()
        # print ("currentCommitHash = %s" %currentCommitHash)
        gitRepoRoot = self.gitExec('rev-parse --show-toplevel').strip()
        # print ("gitRepoRoot = %s" %gitRepoRoot)
        hashToDescribe = git_dir_head(gitRepoRoot, currentCommitHash, projectThatOwnsThisBuildTool)
        # print ("hashToDescribe = %s" %hashToDescribe)

        return hashToDescribe

    def priv_determineMainOrMaster(self):
        branches = self.gitExec('branch -r').split('\n')
        for branch in branches:
            if branch.strip().endswith('/main'):
                return 'main'
            if branch.strip().endswith('/master'):
                return 'master'
        return None

    def priv_getFirstParentBranch(self):
        if(self.fullBranchName.find('feature/') != -1):
            firstParentBranch = 'develop'
        elif(self.fullBranchName.find('renovate/') != -1):
            firstParentBranch = 'feature'
        elif(self.fullBranchName.find('hotfix/') != -1):
            firstParentBranch = self.priv_determineMainOrMaster()
        elif(self.fullBranchName.find('release/') != -1):
            firstParentBranch = 'develop'
        elif(self.fullBranchName.find('develop') != -1):
            firstParentBranch = self.priv_determineMainOrMaster()
        elif(self.fullBranchName.find('master') != -1):
            firstParentBranch = 'master'
        elif(self.fullBranchName.find('main') != -1):
            firstParentBranch = 'main'
        else:
            raise RuntimeError("Cannot get firstParentBranch for: %s" % self.fullBranchName)

        return firstParentBranch

    def priv_getAllCommitHashesFromOneCommitToAnother(self, a, b):
        output = self.gitExec('log %s..%s --format="%%H" --first-parent' % (a, b)).split('\n')
        allCommitHashes = [x for x in output if len(x)] + [a]
        return allCommitHashes

    def priv_getAllCommitHashesForBranch(self):
        firstParentBranch = 'origin/%s' % self.priv_getFirstParentBranch()
        # print ("firstParentBranch = %s" %firstParentBranch)
        gitRepoRoot = self.gitExec('rev-parse --show-toplevel').strip()
        # print ("gitRepoRoot = %s" %gitRepoRoot)
        remoteFullBranchName = 'origin/%s' % self.fullBranchName
        # print ("remoteFullBranchName = %s" %remoteFullBranchName)
        fromHash = git_branch_point(gitRepoRoot, remoteFullBranchName, firstParentBranch)
        # print ("fromHash = %s" %fromHash)
        if (len(fromHash) != 40):
            fromHash = git_branch_point(gitRepoRoot, self.fullBranchName, firstParentBranch)
            # print ("fromHash = %s" %fromHash)
        toHash = self.gitExec('log -n1 HEAD --format="%H"').strip()
        # print ("toHash = %s" %toHash)
        allCommitHashesForBranch = self.priv_getAllCommitHashesFromOneCommitToAnother(fromHash, toHash)
        # print ("allCommitHashesForBranch = %s" %allCommitHashesForBranch)
        allCommitHashesForBranch.pop()
        allCommitHashesForBranch.reverse()
        return allCommitHashesForBranch

    def priv_getFirstCommitHashOnBranch(self):
        allCommitHashesForBranch = self.priv_getAllCommitHashesForBranch()
        if(len(allCommitHashesForBranch)):
            firstCommitHash = allCommitHashesForBranch[0]
            return firstCommitHash
        else:
            raise RuntimeError("Branch does not have a first commit: %s" % self.fullBranchName)

    # Returns integer array: [major, minor, release, revision]
    def priv_getBranchVersion(self, prefix, hashToDescribe):
        if prefix != 'other':
            regexString = prefix + r'-(?:.*-)*?(\d+\.\d+\.\d+)\-(\d+)-(\w+).*'
            gitDescribe = self.gitExec('describe %s --match "%s-*" --first-parent --long --always' % (hashToDescribe, prefix), checked=False)
        else:
            regexString = r'(\d+\.\d+\.\d+)\-(\d+)-(\w+).*'
            gitDescribe = self.gitExec('describe %s --first-parent --long --always' % (hashToDescribe), checked=False)

        self.verbose_log("priv_getBranchVersion gitDescribe = %s" %gitDescribe)
        if (re.match(regexString, gitDescribe)):
            branchVersionString = re.sub(regexString, '\\1.\\2', gitDescribe).strip()
            branchVersion = list(map(int, re.findall(r'(\d+)', branchVersionString)))
            return branchVersion

        self.verbose_log("priv_getBranchVersion did not match regexString %s" % regexString)
        return None

    # Get the distance in number of commits between fromHash and toHash
    def priv_getDistance(self, prefix, fromHash, toHash):
        fromVersion = self.priv_getBranchVersion(prefix, fromHash)
        toVersion = self.priv_getBranchVersion(prefix, toHash)
        # print ("fromVersion = %s" %fromVersion)
        # print ("toVersion = %s" %toVersion)
        return toVersion[3] - fromVersion[3]

    def priv_getAutomaticBranchVersion(self, allCommitHashesForBranch, hashToDescribe):
        brancheTypeToGitflowParentBranchTagNameMap = {
            'hotfix'  : 'release',
            'feature' : 'develop',
            'renovate' : 'develop',
        }
        gitFlowParentBranchTagName = brancheTypeToGitflowParentBranchTagNameMap[self.branchType]

        if hashToDescribe not in allCommitHashesForBranch:
            # When for the particular hashToDescribe there have been no changes to this branch,
            # we assume the behavior as if we were on the parent branch (i.e. master, develop)
            branchVersion = self.priv_getBranchVersion(gitFlowParentBranchTagName, hashToDescribe)
            
            # print ("branchVersion = %s" %branchVersion)
        else:
            brancheTypeToGitflowParentBranchMap = {
                'hotfix'  : 'master',
                'feature' : 'develop',
                'renovate' : 'develop',
            }
            gitFlowParentBranchName = brancheTypeToGitflowParentBranchMap[self.branchType]
            gitDescribe = self.gitExec('describe --match "%s-*" --first-parent --long' % gitFlowParentBranchTagName)
            regexString = gitFlowParentBranchTagName + r'-(\d+\.\d+)\.\d+\-(\d+)-(\w+).*'
            majorMinorVersion = re.sub(regexString, '\\1', gitDescribe).strip()

            firstCommitHash = allCommitHashesForBranch[0] # Because this is the else, there must be at least one
            # 0xFFFFF is a 20-bit mask, yielding values (0,1048576) which is ~ a multiple of 9999,
            # so the modulo gives a reasonable uniform spread
            m = hashlib.sha256()
            m.update(self.getFullBranchName().encode())
            release = 50001 + (int(firstCommitHash[0:5], 16) ^ int(m.hexdigest()[0:5], 16)) % 9999
            revision = self.priv_getDistance(gitFlowParentBranchTagName, firstCommitHash, hashToDescribe)
            branchVersionString = "%s.%s.%s" % (majorMinorVersion, release, revision)
            branchVersion = list(map(int, re.findall(r'(\d+)', branchVersionString)))

        return branchVersion

    def priv_determineVersion(self, prefix):
        hashToDescribe = self.priv_determineGitHashForVersion()
        # print("determineVersion: hashToDescribe = %s" %hashToDescribe)
        


        if self.branchType in ['hotfix', 'feature']:
            allCommitHashesForBranch = self.priv_getAllCommitHashesForBranch()
            # print ("allCommitHashesForBranch = %s" %allCommitHashesForBranch)

            try:
                branchVersion = self.priv_getBranchVersion(prefix, hashToDescribe)
                # print ("branchVersion = %s" %branchVersion)
                if (not branchVersion):
                    raise NoSuchCommitError
                # Since getBranchVersion may actually return an answer based on a tag that is not on this branch,
                # we check if the tag used for the describe was actually on this branch.
                commitHashUsedForBranchVersion = self.gitExec('log -n 1 --format="%%H" %s-%d.%d.%d' % (prefix, branchVersion[0], branchVersion[1], branchVersion[2]))
                # print ("commitHashUsedForBranchVersion = %s" %commitHashUsedForBranchVersion)
                if commitHashUsedForBranchVersion not in allCommitHashesForBranch:
                    raise NoSuchCommitError
            except (CalledProcessError, NoSuchCommitError) as ex:
                if(self.verbose):
                    eprint("Failed to determine branch version using manual tags, attempt to automatically determine one")
                branchVersion = self.priv_getAutomaticBranchVersion(allCommitHashesForBranch, hashToDescribe)
        else:
            try:
                branchVersion = self.priv_getBranchVersion(prefix, hashToDescribe)
                # print ("branchVersion = %s" %branchVersion)
            except CalledProcessError as ex:
                returncode = ex.returncode
                eprint("Command '%s' did not exit normally, exit code %d: %s" % (ex.cmd,returncode,ex))
                eprint("Failed to determine branch version using manual tags, and automatic versioning not supported for this branch type: %s" % self.branchType)
                sys.exit(returncode)

        if branchVersion:
            if self.warnVersion and self.branchType not in ['master', 'release', 'support'] and  int(branchVersion[2]) < 10000 :
                eprint("The release part of the version number (3rd number) should be at least than 10000 for branch type %s, found %s. \nAdd an annotated tag to fix this." %(self.branchType,branchVersion[2]))
                sys.exit(1)

            self.major = int(branchVersion[0])
            self.minor = int(branchVersion[1])
            self.release = int(branchVersion[2])
            self.revision = int(branchVersion[3])

            self.hash = hashToDescribe
            self.message = self.gitExec('log --format="%s" -n 1')

        else:
            eprint(f"Was not able to determine branch version because branch version is {branchVersion} prefix is {prefix} hashToDescribe is {hashToDescribe}")
            # print all of self
            print(self)
            # print location of current file
            print(os.path.abspath(__file__))
            
            sys.exit(1)
    
    def __str__(self):
        return f"gitinfo: {self.__dict__}"
