import platform
import os, os.path
import subprocess
import random
import platform
import time
import random

from multiprocessing.pool import ThreadPool

if platform.system() == "Windows":
    import winreg


# Find signtool.exe

def get_sdk8x_bin_paths(reg_keys=None, reg_path="Software\\Microsoft\\Windows Kits\\Installed Roots"):
    if reg_keys is None:
        reg_keys = ["KitsRoot", "KitsRoot81"]
    ret = []
    hk = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
    for key in reg_keys:
        try:
            p = winreg.QueryValueEx(hk, key)[0]
            p = os.path.join(p, "bin")
            ret.append(p)
        except WindowsError:
            continue
    return ret


def get_sdk10x_bin_paths(reg_key="KitsRoot10", reg_path="Software\\Microsoft\\Windows Kits\\Installed Roots"):
    ret = []
    try:
        hk = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        p10 = winreg.QueryValueEx(hk, reg_key)[0]
        i = 0
        while True:
            try:
                ver = winreg.EnumKey(hk, i)
                p = os.path.join(p10, "bin", ver)
                ret.append(p)
                i += 1
            except:
                break
    except:
        pass
    return ret


def get_signtool_path(arch=None):
    if arch is None:
        arch = platform.architecture()[0]
    ms_arch = {
            "x86": "x86",
            "32bit": "x86",
            "x86_64": "x64",
            "64bit": "x64"
        }.get(str(arch))
    #
    paths = []
    paths += get_sdk8x_bin_paths()
    paths += get_sdk10x_bin_paths()
    paths.reverse()
    for p in paths:
        signtool_path = os.path.join(p, ms_arch, "signtool.exe")
        res = signtool_path.replace("\\", "/")
        if os.path.exists(res):
            if res.count(" ") > 0:
                res = "\"" + res + "\""
            return res
    return None

def getcertsha():
    certsha1 = os.getenv("AIMMS_CODESIGNING_CERTSHA1", "")
    if certsha1 == "":
        raise Exception("No signing certificate found!")
    return certsha1

signServerList = [
    [ "/t", "http://timestamp.verisign.com/scripts/timstamp.dll"],
    [ "/t", "http://timestamp.globalsign.com/scripts/timestamp.dll"],
    [ "/t", "http://tsa.starfieldtech.com"],
    [ "/t", "http://timestamp.comodoca.com/authenticode"],
    [ "/t", "http://timestamp.digicert.com"],
    ];

maxProcesses = 4
maxRandomTime = 16
maxSignAttempts = 8
maxTimeStampAttempts = 8
DEVNULL = open(os.devnull, 'wb')
signtoolWindows = None
debug_mode = os.getenv("SIGN_DEBUG", "False") in ["True", 1, "1", True]

def _timestamp( fileToStamp, flagToUse, serverToUse ):
    if platform.system() == 'Windows':
        signArguments  = [ signToolWindows ]
        signArguments += [ "timestamp" ]
        signArguments += [ flagToUse, serverToUse ]
        signArguments += [ '"%s"' % fileToStamp ]
        cmdLine = " ".join(signArguments)
        return subprocess.call(cmdLine, stdout=DEVNULL, stderr=DEVNULL, shell=True)
    else:
        raise Exception('not supported on linux')


def _sign( fileToSign ):
    signArguments  = [ signToolWindows ]
    signArguments += [ "sign" ]
    if debug_mode:
        signArguments += [ "/debug"]
    signArguments += [ "/fd", "sha256" ]
    signArguments += [ "/sha1", getcertsha() ]
    signArguments += [ '"%s"' % fileToSign ]
    cmdLine = " ".join(signArguments)
    return subprocess.call(cmdLine, shell=True)
    
def _verify( fileToVerify ):
    signArguments  = [ signToolWindows ]
    signArguments += [ "verify" ]
    signArguments += [ "/pa" ]
    signArguments += [ '"%s"' % fileToVerify ]
    cmdLine = " ".join(signArguments)
    return subprocess.call(cmdLine, stdout=DEVNULL, stderr=DEVNULL, shell=True)

def _signAndDescribe( fileToSign, description ):
    signArguments  = [ signToolWindows ]
    signArguments += [ "sign" ]
    signArguments += [ "/sha1", getcertsha() ]
    signArguments += [ "/d", description ]
    signArguments += [ '"%s"' % fileToSign ]
    cmdLine = " ".join(signArguments)
    return subprocess.call(cmdLine, stdout=DEVNULL, stderr=DEVNULL, shell=True)
    
def signAndStamp( fileToProcess ):
    if platform.system() == 'Windows':
        # check if already signed, then don't sign again.
        if (_verify(fileToProcess) == 0): 
            print("'%s' is already signed" % fileToProcess)
            return 0
            
        print("signing '%s'" % fileToProcess)
        for attempt in range(1, maxSignAttempts):
            time.sleep(random.uniform(0,maxRandomTime))
            retCode = _sign( fileToProcess )
            if (retCode == 0):
                break
            print("re-try signing '%s' (attempt %d)" % (fileToProcess,attempt+1))
        
        if (retCode != 0):
           print("Signing of '%s' resulted in exit code %d, exiting" % (fileToProcess,retCode))
           return retCode
        
        retCode = -1
        for attempt in range(0, maxTimeStampAttempts):
            mySignServerList = signServerList
            random.shuffle(mySignServerList)
            for srv in mySignServerList:
                retCode = _timestamp( fileToProcess, srv[0], srv[1] )
                if (retCode == 0):
                    break
            if (retCode == 0):
                break
    else:
        retCode = signAndStampLinux(fileToProcess)
    return retCode

def signAndStampAndDescribe( fileToProcess, description ):
    # check if already signed, then don't sign again.
    if (_verify(fileToProcess) == 0): 
        print("'%s' is already signed" % fileToProcess)
        return 0

    print("signing '%s' with description '%s'" % (fileToProcess, description))
    for attempt in range(1, maxSignAttempts):
        time.sleep(random.uniform(0,maxRandomTime))
        retCode = _signAndDescribe( fileToProcess, description )
        if (retCode == 0):
            break
        print("re-try signing '%s' (attempt %d)" % (fileToProcess,attempt+1))
    
    if (retCode != 0):
        print("Signing of '%s' resulted in exit code %d, exiting" % (fileToProcess,retCode))
        return retCode
    
    retCode = -1
    for attempt in range(0,maxTimeStampAttempts):
        mySignServerList = signServerList
        random.shuffle(mySignServerList)
        for srv in mySignServerList:
            retCode = _timestamp( fileToProcess, srv[0], srv[1] )
            if retCode == 0:
                break
        if retCode == 0:
            break
    return retCode

def signBinaries(targetPath):
    global signToolWindows
    signToolWindows = get_signtool_path()
    binaryFiles = []
    for root, dirs, files in os.walk(targetPath):
        for file in [f for f in files if f.endswith(".exe") or f.endswith(".dll")]:
            binaryFiles.append(os.path.abspath(os.path.join(root, file)))

    pool = ThreadPool(processes=maxProcesses)
    result = pool.map(signAndStamp, binaryFiles)
    pool.close()

    totalFailed = 0
    for r in result:
        totalFailed += r

    if totalFailed > 0:
        raise RuntimeError("%d signing jobs failed" % totalFailed)
