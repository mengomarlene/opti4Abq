import os
import toolbox
import subprocess
from opti4AbqTools import *

verbose = False
saveIntermediateValues = True
NIter = 0



def residuals(p, modelsDir, expDir):
    ''' residuals(p, modelsDir, expDir) computes the diff (in a least square sense) between experimental data and FE data (function of p)
        p: parameter to optimize
        modelsDir: directory with the computational models, contains python scripts defining and running the FE model. Each script must also contain a function called postPro
        expDir: directory with experimental data to fit, should contains ascii files whose names are the same as the FE model names
    each ascii file is contains one value (the experimental equivalent of the FE output value)
    '''
    feData,modelNames = computeFEData(p,modelsDir)
    #
    import numpy as np
    diff = list()
    print modelsDir
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
    if saveIntermediateValues: saveValues(p, feData, lstSq, NIter)
    return lstSq    

def getOptiParam(modelsDir, expDir, optiParam, pBounds=None):
    global NIter
    from scipy.optimize import minimize_scalar
    opts = {'maxiter':optiParam['maxEval'],'disp':True}
    import numpy as np
    res = minimize_scalar(residuals, bounds=pBounds, args=(modelsDir, expDir), tol=optiParam['ftol'], method='bounded', options=opts)
    d = {}
    d['funcalls']= res.nfev
    d['task']= res.message
    d['nIte']= NIter
    if verbose: print res.message
    return res.x,res.fun,d

def main(expDir, modelsDir, options={}, pBounds=None):
    optiParam = {}
    optiParam['maxEval']=10
    optiParam['ftol']=1e-8
    optiParam.update(options)
    return getOptiParam(modelsDir, expDir, optiParam, pBounds)