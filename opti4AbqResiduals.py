import os
from opti4AbqTools import *

def residuals(p, modelScript, expData, withBounds=False):
    ''' residuals(p, expData) computes the diff (in a least square sense) between experimental data and FE data (function of p)
        p: set of parameters to optimize
        expData: experimental data to fit, should be a 2D array (x,y)
    '''
    # compute FE data function of parameters only - should return a 2D array (x,y) of floats
    # ---------------
    feData = computeFEData(p,modelScript)
    #
    import numpy as np
    #try to get next four lines in one with zip??
    diff = list()
    for n in range(len(feData)):
        for m in range(len(feData[n])):
            diff.append(expData[n][m] - feData[n][m])
    lstSq = 0
    for value in diff:
        lstSq+= value**2
    lstSq /= (len(feData[0])*len(feData))
    lstSq = lstSq**0.5
    global NIter
    NIter += 1
    if saveIntermediateValues: 
        saveValues(p, feData, lstSq, NIter)
    if withBounds:
        return lstSq
    else:
        return np.resize(diff,len(p))
        
        
def residualsScalar(p, modelsDir, expDir):
    ''' residuals(p, modelsDir, expDir) computes the diff (in a least square sense) between experimental data and FE data (function of p)
        p: parameter to optimize
        modelsDir: directory with the computational models, contains python scripts defining and running the FE model. Each script must also contain a function called postPro
        expDir: directory with experimental data to fit, should contains ascii files whose names are the same as the FE model names
    each ascii file contains one value (the experimental equivalent of the FE output value)
    '''
    feData,modelNames = computeFEData(p,modelsDir)
    #
    diff = list()
    for data,name in zip(feData,modelNames):
        #read data file
        dataFile = os.path.join(expDir,name.split('.')[0]+'.ascii')
        with open(dataFile, 'r') as file: expData =  float(file.readline().split()[0])
        # add difference in list
        if data[0]: diff.append((expData - data[0])/expData)
    lstSq = 0
    for value in diff: lstSq+= value**2
    lstSq /= len(diff)
    lstSq = lstSq**0.5
    global NIter
    NIter += 1
    if saveIntermediateValues: saveValues(p, feData, modelNames, lstSq, NIter)
    return lstSq