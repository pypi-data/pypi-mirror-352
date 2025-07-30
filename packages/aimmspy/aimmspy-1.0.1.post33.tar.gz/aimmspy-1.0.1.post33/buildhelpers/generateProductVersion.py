import sys
import os
import socket
import datetime
from ProductVersionEnvVars import ProductVersionEnvVars
from string import Template
from internal.gitinfo import gitinfo
import argparse


class ProductVersionTemplateGenerator:

    def generate( self, templateFile, resultFile, version):
        with open(templateFile,'r') as file:
            templateString = file.read()
            print("ProductVersionTemplateGenerator: opened template file %s successfully" % file.name)

        rightNow = datetime.datetime.utcnow()
        theMoment = rightNow.strftime("%Y-%m-%d %H:%M:%S (UTC)")
        copyrightYear = "%s" % rightNow.year
        theHostName = socket.gethostname()
        version_class = None
        
        if not version:
            print("ProductVersionTemplateGenerator: no version specified, using gitinfo")
            version_class = gitinfo()
            print ("ProductVersionTemplateGenerator: version = %s" % version_class.getVersion())
        else:
            print ("ProductVersionTemplateGenerator: version = %s" % version)
            version_class = ProductVersionEnvVars()
            
            if '-' in version:
                version, hash = version.split('-')
                version_class.setRevision(hash)
                version = version.split(".")
                version_class.setMajor(version[0])
                version_class.setMinor(version[1])
                version_class.setRelease(version[2])
            else:
                version = version.split(".")
                version_class.setMajor(version[0])
                version_class.setMinor(version[1])
                version_class.setRelease(version[2])
                version_class.setRevision(version[3])
            
        temp_obj = Template(templateString)
        result = temp_obj.substitute(
            ProductVersion_Major=version_class.getMajor(), 
            ProductVersion_Minor=version_class.getMinor(),
            ProductVersion_Release=version_class.getRelease(),
            ProductVersion_Patch=version_class.getRevision(),
            ProductVersion_Hash=version_class.getHash(),
            ProductVersion_BuildDate=theMoment,
            ProductVersion_BuildHost=theHostName,
            ProductVersion_CopyrightYear=copyrightYear)
        
        (resultDir, justTheFile) = os.path.split(resultFile)
        if(len(resultDir) > 0):
            os.makedirs(resultDir, exist_ok=True)
        with open(resultFile,'w') as file:
            file.write(result)
            print("ProductVersionTemplateGenerator: written to file %s successfully" %file.name)
            
if __name__ == "__main__":
    # add a command line parser that retrieves the version
    parser = argparse.ArgumentParser(description='Generate ProductVersion.h')
    # oprional version argument
    parser.add_argument('--template', type=str, help='template file', default=None, required=True)
    parser.add_argument('--result', type=str, help='result file', default=None, required=True)
    parser.add_argument('--version', type=str, help='version', default=None, required=False)
    args = parser.parse_args()
    
    tg = ProductVersionTemplateGenerator()
    
    tg.generate(args.template, args.result, args.version)