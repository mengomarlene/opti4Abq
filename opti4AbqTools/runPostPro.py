'''
 ----------------------------------------------------------------
 runPostPro.py - part of the opti4Abq project
 
 runs a abaqus post-processing function defined in a file (fileName) on a odb found in a directory (workspace)
 the file fileName must contain a function called postPro
 WARNING
 This file uses functions defined in toolbox.py (defined in the opti4Abq project):
  --> that module needs to be reachable
 ----------------------------------------------------------------
 author: MENMMEN, 04/03/2015
 ----------------------------------------------------------------
 INSTRUCTION
 run from command line as: "abaqus python runPostPro fileName workspace"
 fileName is the full path of the python file where the postPro function is defined
 workspace is the full path of the directory where the odb file is
 ----------------------------------------------------------------
 KNOWN ISSUE/BUG
 If there are more than one odb file in the workspace, it will run only on the first odb file found
 ----------------------------------------------------------------
'''

import sys,os
fileName = sys.argv[-2]
workspace = sys.argv[-1]
from toolbox import fileToModule

baseName = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(workspace):
    raise Exception("cannot run postPro on empty workspace!")
else :
    odbName = None
    for name in os.listdir(workspace):
        if name.split('.')[-1] == 'odb':
            odbName = name
            break
    if odbName is None: raise Exception("no odb file in %s!"%(workspace))
    versionInfo = sys.version_info
    assert versionInfo[0]==2,"need to use python 2.x version"
    module = fileToModule(fileName, baseName)
    if versionInfo[1]<7:
        _temp = __import__(module, globals(), locals(), ['postPro'], -1)
    else:# in python 2.7 and above, __import__ should be replaced by importlib.import_module
        import importlib
        _temp = importlib.import_module(module)
    os.chdir(workspace)
    _temp.postPro(odbName)
    os.chdir(baseName)
