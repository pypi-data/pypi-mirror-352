
import os
import subprocess
import platform
import shutil

def runProjectTests(aimms_version, arch, config, project_folder, project, project_root_dir, suites, extra_args, custom_procedure = None):
    
    # if env variable AIMMS_TEST_VERSION_FOLDER is set, use that as the aimms version
    aimms_folder = None
    
    if os.getenv("AIMMS_FOLDER_DEPLOY_VERSION_NAME"):
        aimms_folder = os.path.join(os.getcwd(),"aimms",os.getenv("AIMMS_FOLDER_DEPLOY_VERSION_NAME"), config)
        print (f"Using AIMMS_FOLDER_DEPLOY_VERSION_NAME becoming {aimms_folder}") 
    else:
        aimms_folder = os.path.join(os.getcwd(),"aimms",aimms_version, config)
        
    isLinux = 0
    print("extra args: %s" % extra_args)
    if (platform.system() == 'Linux'):
        isLinux = 1
    if (arch == 'Win32'):
        arch = 'x86'
    
    print ("aimms_folder: %s" % aimms_folder)
    print ("project_folder: %s" % project_folder)
    print ("project: %s" % project)
    print ("project_root_dir: %s" % project_root_dir)
    print ("aimms_version: %s" % aimms_version)
    
    # check if the aimms folder exists
    if not os.path.exists(aimms_folder):
        exit("Aimms folder %s does not exist" % aimms_folder)
    
    # normalise all paths
    aimms_folder = os.path.normpath(aimms_folder)
    project_folder = os.path.normpath(project_folder)
    project_root_dir = os.path.normpath(project_root_dir)

    # remove the log folder if it exists
    if os.path.exists(os.path.join(project_root_dir, project_folder, "log")):
        shutil.rmtree(os.path.join(project_root_dir, project_folder, "log"))

    os.environ["LOG_FILE_PATH"] = os.path.join(project_root_dir, project_folder, "log", "log4cxx.log")
    
    if (isLinux):
        aimmsCmdArgs  = [os.path.join(aimms_folder, "Bin", "AimmsCmd")]
        aimmsCmdArgs += ["--aimms-root-path"]
        aimmsCmdArgs += [os.path.join(project_root_dir, "buildhelpers" , "autolibs", "aimmsroot")]
    else:
        aimmsCmdArgs  = [os.path.join(aimms_folder, "Bin", "AimmsCmd.exe")]
        aimmsCmdArgs += ["--alluser-dir"]
        aimmsCmdArgs += [os.path.join(project_root_dir, "buildhelpers" , "autolibs", "aimmsroot")]
        
    aimmsCmdArgs += ["--logcfg"]

                
    aimmsCmdArgs += [os.path.join(project_root_dir, "buildhelpers", "autolibs" , "AimmsLogConfig.xml")]
    
    if (not custom_procedure):

        if (suites != ""):
            aimmsCmdArgs += ["--aimmsunit::RunTestSuites"]
            aimmsCmdArgs += [suites]
        else:
            aimmsCmdArgs += ["--aimmsunit::RunAllTests"] 
            aimmsCmdArgs += ["1"]

        aimmsCmdArgs += ["--run-only", "aimmsunit::TestRunner"]
        

    else:
        aimmsCmdArgs += ["--run-only"]
        aimmsCmdArgs += [custom_procedure]


    aimmsCmdArgs += ["--as-server"]
    
    aimmsCmdArgs += [os.path.join(os.getcwd(), project_folder, project)]
    
    for arg in extra_args:
        aimmsCmdArgs += [arg]
    
    print (aimmsCmdArgs)
    if (isLinux):
        LD_LIBRARY_PATH = os.environ.get('LD_LIBRARY_PATH')
        LD_LIBRARY_PATH = f'{LD_LIBRARY_PATH}:{os.path.join(aimms_folder, "Bin")}'
        os.environ['LD_LIBRARY_PATH'] = LD_LIBRARY_PATH
   
    ret = subprocess.Popen(aimmsCmdArgs, stdin=subprocess.PIPE, stderr=subprocess.PIPE, cwd=aimms_folder, env=os.environ)
    ret.wait()

    logfile = lambda filename : os.path.join(project_folder, "log", filename)
    logfileExists = lambda filename : os.path.isfile(logfile(filename))

    # print files in project_folder log
    # log_folder = os.path.join(project_folder, "log")
    # print (f'Files in {log_folder}:')
    # for file in os.listdir(log_folder):
    #     print (file)

    if logfileExists("AimmsUnit.xml"):
        print ("\n****************************************************\n")
        file_path = os.path.join(project_folder, "log", "AimmsUnit.xml")
        with open(file_path, 'r') as fin:
            print((fin.read()))
            
    if logfileExists("AimmsUnit.succeeded"):
        # print ("\n****************************************************\n")
        # with open(logfile("AimmsUnit.succeeded"), 'r') as fin:
        #     print((fin.read()))
        return 0
    
    
    # print that the test failed and that the log files are printed in path 
    print ("\n****************************************************\n")
    print("Found failed test, check the log files in the log folder or if on the CI server check the artifacts")
    print (f"{logfile('AimmsUnit.failed')}")
    print (f"{logfile('aimms.err')}")
    print (f"{logfile('log4cxx.log')}")
    print ("\n****************************************************\n")
    
            
    # if (logfileExists("AimmsUnit.failed")):
    #     print ("\n****************************************************\n")
    #     with open(logfile("AimmsUnit.failed"), 'r') as fin:
    #         print((fin.read()))

    # if logfileExists("aimms.err"):
    #     print ("\n****************************************************\n")
    #     with open(logfile("aimms.err"), 'r') as fin:
    #         print((fin.read()))
    
    # if logfileExists("log4cxx.log"):
    #     print ("\n****************************************************\n")
    #     with open(logfile("log4cxx.log"), 'r') as fin:
    #         print((fin.read()))
    
    return 1
