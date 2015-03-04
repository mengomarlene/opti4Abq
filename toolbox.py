"""
generic python tools
"""
import os,sys
#-----------------------------------------------------
def fileToModule(file,baseName):
    commonPath = os.path.commonprefix([file,baseName])
    relPath = os.path.relpath(file,commonPath)
    if commonPath not in sys.path:sys.path.append(commonPath)
    return relPath.split('.')[0].replace(os.sep,'.')
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
    return os.path.basename(fileWithExt).split('.')[0]
#-----------------------------------------------------
def getFileExt(fileWithExt):
    return os.path.basename(fileWithExt).split('.')[-1]
#-----------------------------------------------------

