"""
generic python tools
"""
import os,sys
#-----------------------------------------------------
def fileToModule(file,baseName):
    commonPath = os.path.commonprefix([file,baseName])
    relPath = os.path.relpath(file,commonPath)
    return getFileName(relPath).replace(os.sep,'.')
#-----------------------------------------------------
def getWorkspace(file, baseName=os.getcwd(), verb=False):
    wPath = os.path.join(baseName,os.path.join('workspace',fileToModule(file,baseName).replace('.','_')))
    workspace = os.path.abspath(wPath)
    if verb: print "toolbox.getWorkspace returns ",workspace
    return workspace
#-----------------------------------------------------
def modulePath(local_function):
    ''' returns the module path without the use of __file__.  Requires a function defined 
    locally in the module.
    from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module
    '''
    import inspect
    return os.path.abspath(inspect.getsourcefile(local_function))
#-----------------------------------------------------
def getFileName(fileWithExt):
    import os
    return os.path.basename(fileWithExt).split('.')[0]
#-----------------------------------------------------
def getFileExt(fileWithExt):
    import os
    return os.path.basename(fileWithExt).split('.')[-1]
#-----------------------------------------------------
def runPostPro(file,workspace=None):
    baseName = os.path.dirname(os.path.abspath(__file__))
    if workspace is None:workspace =  getWorkspace(file, baseName)
    if not os.path.isdir(workspace): raise Exception("cannot run postPro on empty workspace!")
    else :
        odbName = None
        for name in os.listdir(workspace):
            if name.split('.')[-1] == 'odb':
                odbName = name
                break
        if odbName is None: raise Exception("no odb file in %s!"%(workspace))
        versionInfo = sys.version_info
        assert versionInfo[0]==2,"need to use python 2.x version"
        module = fileToModule(file)
        if versionInfo[1]<7:
            _temp = __import__(module, globals(), locals(), ['postPro'], -1)
        else:# in python 2.7 and above, __import__ should be replaced by importlib.import_module
            import importlib
            _temp = importlib.import_module(module)
        os.chdir(workspace)
        _temp.postPro(odbName)
        os.chdir(baseName)
