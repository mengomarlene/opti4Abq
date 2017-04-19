"""
abaqus python tools - part of the opti4Abq project
"""
import os
import subprocess
import toolbox
    
def callbackF(p):
    import counter
    counter.NIter += 1
    baseName = os.path.dirname(os.path.abspath(__file__))
    resultFolder = os.path.join(baseName,'..','results')
    if not os.path.exists(resultFolder): os.makedirs(resultFolder)
    callbackFile = os.path.join(resultFolder,'callbackValues_%i.dat'%counter.NIter)
    with open(callbackFile, 'w') as file:
        file.write('Iteration Nb: %i\n'%(counter.NIter))
        file.write('Nb Function Evaluation: %i\n'%(counter.NFeval))
        file.write('Parameters Input: %s\n'%(p))
#-----------------------------------------------------
def computeFEData(p,modelsDir,verbose):
    files = os.listdir(modelsDir)
    files.sort()
    '''
    populates a list of model names found in modelsDir and a list of model outputs after they have run with parameter p
    '''
    modelList = list()
    for modelScript in files:
        if (modelScript.endswith('.py')) and ('__init__' not in modelScript):
            modelList.append(modelScript)
    else:#no break
        output = list()
        for model in modelList:
            out1job = runModel(p,model,modelsDir,verbose)
            if len(out1job)>1:output.append(out1job)
            elif len(out1job)== 1:output.append(out1job[0])               
    return output,modelList
#-----------------------------------------------------
def runModel(p,modelScript,modelsDir,verbose):
    '''
    run abaqus models:
    1/ create a working directory for abaqus (in workspace\name_of_modelsDir_from_common_path_with_current_directory)
    2/ runs an abaqus cae analysis in the working directory (all abaqus files written in that directory): abaqus cae noGUI=path_to_modelScript -- p
    3/ runs an abaqus post-processing analysis by looking for the postPro function defined in the modelScript with argument the odb file of the previously run model
    '''
    #1/ create working directory
    baseName = os.getcwd()
    import sys
    if baseName not in sys.path:sys.path.append(baseName)
    filePath = os.path.join(modelsDir,modelScript)
    workspace = toolbox.getWorkspace(filePath,baseName=baseName)
    if not(os.path.isdir(workspace)):
        try: os.makedirs(workspace)
        except WindowsError: print("file(s) probably locked!\n")

    #2/ runs abaqus cae
    # run abaqus analysis (function of parameters p) in workspace
    os.chdir(workspace)
    if verbose: print "running abaqus cae on %s"%(toolbox.getFileName(filePath))
    cmd = 'abaqus cae noGUI=%s'%(filePath)
    try:#multiparam opti
        paramString = ' '.join(map(str,p))
    except(TypeError):#scalar opti
        paramString = str(p)
    cmd += ' -- %s > %s 2>&1'%(paramString,'exeCalls.txt')
    if verbose: print 'cmd= ',cmd
    pCall1 = subprocess.call(cmd, shell=True)
    with open('exeCalls.txt', 'r') as file:
        lastLine = file.readlines()[-1]
    os.chdir(baseName)

    #3/ run abaqus postPro -- needs to be called with abaqus python as abaqus-specific modules are needed!!
    # solution: run in a new subprocess the file runPostPro.py called with the appropriate modelScript and working directory
    cmd = r"abaqus python opti4AbqTools\runPostPro.py %s %s"%(filePath,workspace)
    pCall2 = subprocess.call(cmd, shell=True)
    if pCall2:#the post pro function has not run properly --> writes an error file
        writeErrorFile(workspace,modelScript,p,pCall1,pCall2)
        raise Exception("!! something has gone wrong, check notRun.txt")
    else:# reads the written output of the post-processing function as a float
        feOutputFile = os.path.join(workspace,'output.dat')#could be generalised to allow the user to input a fileName!
        with open(feOutputFile, 'r') as file:   
            output = zip(*(map(float,line.split()) for line in file))
        return output
#-----------------------------------------------------
def writeErrorFile(workspace,modelScript,p,pCall1,pCall2='not run yet'):
    feErrorFile = os.path.join(workspace,'notRun.txt')
    import counter
    with open(feErrorFile, 'w') as file:
        file.write('running abaqus cae on %s returned %s\n'%(toolbox.getFileName(modelScript), pCall1))
        file.write('running post pro on %s returned %s\n'%(toolbox.getFileName(modelScript), pCall2))
        file.write('parameter inputs: %s\n'%(p))
        file.write('run number: %s\n'%(counter.NFeval))
#-----------------------------------------------------
def plotValues(fittedValues, modelScript, expData):
    baseName = os.path.dirname(os.path.abspath(__file__))
    workspace = getWorkspace(modelScript,baseName)
    os.chdir(workspace)
    figFilePng = os.path.join(workspace,'fittedResults2.png')
    figFilePdf = os.path.join(workspace,'fittedResults2.pdf')
    import matplotlib.pyplot as plt
    plt.plot(expData[0],expData[1],'o',fittedValues[0],fittedValues[1],'x')
    plt.legend(['Data', 'Fit'])
    plt.title('Least-squares fit to data')
    plt.savefig(figFilePng, bbox_inches='tight')
    plt.savefig(figFilePdf, bbox_inches='tight')
    if not verbose:plt.show()
    return fittedValues
#-----------------------------------------------------
def plotIntermediateValues(feData, expData, no='final'):
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(expData[0],expData[1],'o',feData[0],feData[1],'x')
    plt.legend(['Data', 'Fit'])
    plt.title('Least-squares fit to data - function evaluation nb %i'%no)
    plt.savefig('fit_%i.png'%no, bbox_inches='tight')
    plt.savefig('fit_%i.pdf'%no, bbox_inches='tight')
#-----------------------------------------------------
def saveValues(p, feData, names, value, no='final'):
    baseName = os.path.dirname(os.path.abspath(__file__))
    resultFolder = os.path.join(baseName,'results')
    if not os.path.exists(resultFolder): os.makedirs(resultFolder)
    feDataFile = os.path.join(resultFolder,'intermediateValues_%i.dat'%no)
    with open(feDataFile, 'w') as file:
        file.write('run number (nb function evaluation): %s\n'%(no))
        file.write('parameter inputs: %s\n'%(p))
        file.write('least square error %s\n'%value)
        try:file.write('\n'.join('%s: %f ' %(name,data[0]) for data,name in zip(feData,names)))
        except(TypeError):
            file.write('\n'.join('%s (last FE x and y Values): %f %f' %(name,data[0][-1],data[1][-1]) for data,name in zip(feData,names)))
            # for data,name in zip(feData,names):
                # file.write('%s\n' %name)    
                # file.write('\n'.join('%f ' %values for values in data[1]))
#-----------------------------------------------------       
