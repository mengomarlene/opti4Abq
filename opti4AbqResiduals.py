import os
from opti4AbqTools import *

def interpolateResults(data,xi):
    import scipy.interpolate as interpolate
    import numpy
    f = interpolate.interp1d(data[0],data[1],bounds_error=False)
    return numpy.array(f(xi))

def RMS(Data1D):
    RMS = 0
    for value in Data1D: RMS+= value**2
    RMS /= len(Data1D)
    return RMS**0.5   
    
def residuals(p, modelsDir, expDir, withBounds=False):
    ''' residuals(p, modelsDir, expDir, withBounds=False) computes the diff (in a least square sense) between experimental data and FE data (function of p)
        p: set of parameters to optimize
        modelsDir: directory with the computational models, contains python scripts defining and running the FE model. Each script must also contain a function called postPro
        expDir: directory with experimental data to fit, should contains ascii files whose names are the same as the FE model names
    each ascii file contains a 2D array (the experimental equivalent of the FE output values)
    '''
    # compute FE data function of parameters only - should return a 2D array (x,y) of floats
    # ---------------
    feData,modelNames = computeFEData(p,modelsDir)
    #
    import numpy as np
    diff = list()
    for data,name in zip(feData,modelNames):
        xFE = np.array(data[0])
        yFE = np.array(data[1])
        #read data file
        dataFile = os.path.join(expDir,name.split('.')[0]+'.ascii')
        with open(dataFile, 'r') as file: expData = zip(*(map(float,line.split()) for line in file))
        #resample experimental data to FE sampling size
        yExp = interpolateResults(expData,xFE)
        yFE = yFE[~np.isnan(yExp)]
        yExp = yExp[~np.isnan(yExp)]
        #record the relative difference between experimental and FE values for each data point, if non zero
        diff.append([abs(x-y)/y for x,y in zip(yFE,yExp) if y])
    if not len(feData): 
        diff = [[1],[1]]
        print "at least one model did not complete"
    allLstSq  = [RMS(diff1D) for diff1D in diff]#RMS error of each model
    lstSq = RMS(allLstSq)#RMS error of (RMS error of each model)
    import counter
    counter.NFeval += 1
    if saveIntermediateValues: saveValues(p, feData, modelNames, lstSq, counter.NFeval)
    if withBounds: return lstSq
    else: return np.resize(allLstSq,len(p))
        
        
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
    lstSq = RMS(diff)
    import counter
    counter.NFeval += 1
    if saveIntermediateValues: saveValues(p, feData, modelNames, lstSq, counter.NFeval)
    return lstSq