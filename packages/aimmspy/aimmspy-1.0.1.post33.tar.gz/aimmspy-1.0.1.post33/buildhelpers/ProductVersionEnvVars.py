import os
from enum import Enum

class _EnvVars(Enum):
    CI_PRODUCTVERSION_MAJOR = 1
    CI_PRODUCTVERSION_MINOR = 2 
    CI_PRODUCTVERSION_RELEASE = 3
    CI_PRODUCTVERSION_REVISION = 4
    CI_PRODUCTVERSION_HASH = 5
    CI_PRODUCTVERSION_BRANCHTYPE = 6
    
# This is a wrapper class around the environment variables
# that are to be used to communicate version information,
# i.e. one single source of truth for the env-var-names.
# Typically at the start of the build these will be set
# by auto-detecting using git describe
class ProductVersionEnvVars:
    __defaultMajor = "4";
    __defaultMinor = "999";
    __defaultRelease = "0";
    __defaultRevision = "1";
    __defaultHash = "0101010101010101010101010101010101010101";
    __defaultBranchType = "local";
    
    def getMajor(self):
        return os.getenv(_EnvVars.CI_PRODUCTVERSION_MAJOR.name, self.__defaultMajor)
    
    def setMajor(self, val):
        os.environ[ _EnvVars.CI_PRODUCTVERSION_MAJOR.name ] = val
        
    def getMinor(self):
        return os.getenv(_EnvVars.CI_PRODUCTVERSION_MINOR.name, self.__defaultMinor)
    
    def setMinor(self, val):
        os.environ[ _EnvVars.CI_PRODUCTVERSION_MINOR.name ] = val
        
    def getRelease(self):
        return os.getenv(_EnvVars.CI_PRODUCTVERSION_RELEASE.name, self.__defaultRelease)
    
    def setRelease(self, val):
        os.environ[ _EnvVars.CI_PRODUCTVERSION_RELEASE.name ] = val
        
    def getRevision(self):
        return os.getenv(_EnvVars.CI_PRODUCTVERSION_REVISION.name, self.__defaultRevision)
    
    def setRevision(self, val):
        os.environ[ _EnvVars.CI_PRODUCTVERSION_REVISION.name ] = val
        
    def getHash(self):
        return os.getenv(_EnvVars.CI_PRODUCTVERSION_HASH.name, self.__defaultHash)
    
    def setHash(self, val):
        os.environ[ _EnvVars.CI_PRODUCTVERSION_HASH.name ] = val
        
    def getBranchType(self):
        return os.getenv(_EnvVars.CI_PRODUCTVERSION_BRANCHTYPE.name, self.__defaultBranchType)
    
    def setBranchType(self, val):
        os.environ[ _EnvVars.CI_PRODUCTVERSION_BRANCHTYPE.name ] = val