import os, os.path, sys, stat, errno
import subprocess
import shutil, errno
import glob
import traceback
import zipfile
from subprocess import CalledProcessError
import logging
from .eprint import eprint

debug = True

logger = logging.getLogger("util")
consoleAppender = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s [%(name)s-%(funcName)s()] - %(message)s")
consoleAppender.setFormatter(formatter)
logger.addHandler(consoleAppender)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

# like posix mv, supports globbing
def mv(src, dst):
    entries = glob.glob(src)
    for entry in entries:
        try:
            shutil.move(entry, dst)
        except Exception as e:
            print(e)

def cp_r(src, dst):
    def log():
        if debug:
            print(("Copying %s to %s..." % (src, dst)))
            sys.stdout.flush()
    if(os.path.isdir(src)):
        dst += '/'+os.path.basename(src)
        if(os.path.exists(dst)):
            rm_rf(dst)
        log()
        shutil.copytree(src, dst)
    else:
        log()
        shutil.copy(src, dst)

def rm_rf(path):
    def log():
        if debug:
            print(("Removing %s..." % path))
            sys.stdout.flush()
    # source: http://stackoverflow.com/questions/4829043/
    #           how-to-remove-read-only-attrib-directory-with-python-in-windows#answer-4829285
    def on_rm_error(func, path, exc_info):
        # path contains the path of the file that couldn't be removed
        # let's just assume that it's read-only and unlink it.
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)
    if '*' in path:
        log()
        entries = glob.glob(path)
        for entry in entries:
            try:
                if os.path.isfile(entry):
                    os.unlink(entry)
                elif os.path.isdir(entry):
                    shutil.rmtree(entry, onerror = on_rm_error)
            except Exception as e:
                print(e)
    elif(os.path.isdir(path)):
        log()
        if os.path.exists(path):
            shutil.rmtree(path, onerror = on_rm_error)
    else:
        log()
        if os.path.exists(path):
            os.remove(path)

# new version
def execute2(command, **options):
    if options.get('debug'):
        eprint("Executing: %s in %s" % (command, os.getcwd()))
        sys.stderr.flush()
    try:
        if options.get('get_output', False):
            return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        else:
            return subprocess.call(command, shell=True)
    except CalledProcessError as ex:
        if options.get('checked', True):
            returncode = ex.returncode
            eprint("  %s" % ex.cmd if isinstance(ex.cmd, str) else ' '.join(ex.cmd))
            eprint("  =>  %s" % ex.output.decode('utf-8'))
            eprint("Exception: %s" % ex)
            if (not(returncode == 0)):
                eprint("Command did not exit normally, exit code %d." %returncode )
                sys.exit(returncode)
        else:
            raise ex

# @deprecated version of execute
def execute(command, get_output=False):
    return execute2(command, get_output=get_output,checked=True)

def extract(zfile, dst):
    def log():
        if debug:
            print(("Extracting %s to %s" % (zfile, dst)))
            sys.stdout.flush()
    log()
    fh = open(zfile,'rb')
    z = zipfile.ZipFile(fh)
    z.extractall(dst)
    fh.close()


def rmtreeOnerrorHandler(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat

    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def removeDirRecursive(dirAbsolutePath):
    try:
        shutil.rmtree(dirAbsolutePath, onerror=rmtreeOnerrorHandler)
        logger.debug("removed directory %s and its contents" % dirAbsolutePath)
    except Exception:
        logger.info("directory %s already gone" % dirAbsolutePath)

def checkedCopyTree(sourceDir, targetDir):
    logger.debug("Copying '%s' to '%s'" % (sourceDir, targetDir))
    if os.path.exists(sourceDir):
        shutil.copytree(sourceDir, targetDir)
    else:
        logger.error("Failed to copy '%s' to '%s'" % (sourceDir, targetDir))
        traceback.print_exc()
        sys.exit(1)

# Runs command with immediate output
def runCommand(cmd, checkExitCode = True):
    print(("Executing: %s in %s" % (cmd, os.getcwd())))

    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

    result = []

    while True:
        out = p.stderr.readline().decode('utf-8')
        if out == '' and p.poll() != None:
            break
        print(out)
        result.append(out)

    rc = p.poll()
    if checkExitCode and not (rc == 0):
        print(("Command did not exit normally, exit code %d." % rc))
        sys.exit(rc)

    return "\n".join(result)