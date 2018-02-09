import os
from runAbqTools import *

def interpolateResults(expData,xFE,yFE):
    import scipy.interpolate as interpolate
    import numpy
    interExp = True
    if len(expData[0])>len(xFE):
        xi = xFE
        data = expData
    else:
        xi = expData[0]
        data = [xFE,yFE]
        interExp = False
    f = interpolate.interp1d(data[0],data[1],bounds_error=False)
    if interExp:
        return yFE,numpy.array(f(xi))
    else:
        return numpy.array(f(xi)),expData[1]

def RMS(Data1D):
    RMS = 0
    for value in Data1D: RMS+= value**2
    RMS /= len(Data1D)
    return RMS**0.5   
    
def residuals(p, modelsDir, expDir, withBounds=False, absDiff=False, verbose=False):
    ''' residuals(p, modelsDir, expDir, withBounds=False) computes the diff (in a least square sense) between experimental data and FE data (function of p)
        p: set of parameters to optimize
        modelsDir: directory with the computational models, contains python scripts defining and running the FE model. Each script must also contain a function called postPro
        expDir: directory with experimental data to fit, should contains dat files whose names are the same as the FE model names
    each dat file contains a 2D array (the experimental equivalent of the FE output values)
    '''
    # compute FE data function of parameters only - can return a 2D array (x,y) of floats, a 1D array of floats or 1 float
    # ---------------
    feData,modelNames = computeFEData(p,modelsDir,verbose)
    #
    import numpy as np
    diff = list()
    if len(feData) == 0: 
        diff = [[1],[1]]
    else:
        for data,name in zip(feData,modelNames):
            if len(data)==2:
                xFE = np.array(data[0])
                yFE = np.array(data[1])
                #read data file
                dataFile = os.path.join(expDir,name.split('.')[0]+'.dat')
                with open(dataFile, 'r') as file: expData = zip(*(map(float,line.split()) for line in file))
                #resample experimental data to FE sampling size
                yFE,yExp = interpolateResults(expData,xFE,yFE)
                yFE = yFE[~np.isnan(yExp)]
                yExp = yExp[~np.isnan(yExp)]
            elif len(data)==1:
                if type(data[0]) == float:
                    yFE = [np.array(data[0])]
                else:
                    yFE = np.array(data[0])
                dataFile = os.path.join(expDir,name.split('.')[0]+'.dat')
                with open(dataFile, 'r') as file: yExp = zip(*(map(float,line.split()) for line in file))
                if len(yFE) != len(yExp):
                    raise Exception("FE model (model name: %s) returned a array not the same size as the target data"%(name))
            else:
                yFE = list(data)
                dataFile = os.path.join(expDir,name.split('.')[0]+'.dat')
                with open(dataFile, 'r') as file: yExp = zip(*(map(float,line.split()) for line in file))[0]
            if any(np.isnan(yFE)):
                print "FE model (model name: %s) returned at least 1 NaN value - skipping it"%(name)
                continue# gets to the next feModel in the loop without recording data for this model
            
            #record the (relative) difference between experimental and FE values for each data point
            if absDiff:
                diff.append([abs(fe-exp) for fe,exp in zip(yFE,yExp)])
            else:
                diff.append([abs(fe-exp)/exp for fe,exp in zip(yFE,yExp) if exp])

    if len(diff) == 0:
        try: 
            raise Exception("all your FE models returned NaN values - cannot continue. Current parameters are %s"%(', '.join(map(str, p))))
        except(TypeError):
            raise Exception("all your FE models returned NaN values - cannot continue.")
    allLstSq  = [RMS(diff1D) for diff1D in diff]#RMS error of each model
    lstSq = RMS(allLstSq)#RMS error of (RMS error of each model)
    import counter
    counter.NFeval += 1
    if verbose: saveValues(p, feData, modelNames, lstSq, counter.NFeval)

    if withBounds: return lstSq
    else: return np.resize(allLstSq,len(p))
        
def residualsScalar(p, modelsDir, expDir, absDiff=False, verbose=False):
    ''' residualsScalar(p, modelsDir, expDir) computes the diff (in a least square sense) between experimental data and FE data (function of p)
        p: parameter to optimize
        modelsDir: directory with the computational models, contains python scripts defining and running the FE model. Each script must also contain a function called postPro
        expDir: directory with experimental data to fit, should contains dat files whose names are the same as the FE model names
    each dat file contains one value (the experimental equivalent of the FE output value)
    '''
    feData,modelNames = computeFEData(p,modelsDir,verbose)
    import numpy as np
    #
    diff = list()
    for data,name in zip(feData,modelNames):
        if np.isnan(data):
            print "FE model (model name: %s) returned at least 1 NaN value - skipping it"%(name)
            continue# gets to the next feModel in the loop without recording data for this model
        #read data file
        dataFile = os.path.join(expDir,name.split('.')[0]+'.dat')
        with open(dataFile, 'r') as file: expData =  float(file.readline().split()[0])
        if np.isnan(data[0]):
            print "FE model (model name: %s) returned at least 1 NaN value - skipping it"%(name)
            continue# gets to the next feModel in the loop without recording data for this model
        # add difference in list
        if absDiff or not expData:
            diff.append(expData - data[0])
        elif expData:
            diff.append((expData - data[0])/expData)
    if len(diff) == 0:
        try: 
            raise Exception("all your FE models returned NaN values - cannot continue. Current parameters are %s"%(', '.join(map(str, p))))
        except(TypeError):
            raise Exception("all your FE models returned NaN values - cannot continue.")
    lstSq = RMS(diff)
    import counter
    counter.NFeval += 1
    if verbose: saveValues(p, feData, modelNames, lstSq, counter.NFeval)
    return lstSq