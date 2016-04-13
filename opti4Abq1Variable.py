from opti4AbqTools import *

verbose = False

def getOptiParamScalar(modelsDir, expDir, optiParam, pBounds=None):
    from opti4AbqResiduals import residualsScalar
    from scipy.optimize import minimize_scalar
    opts = {'maxiter':optiParam['maxIter'],'disp':True}
    import numpy as np
    if pBounds:
        res = minimize_scalar(residualsScalar, bounds=pBounds, args=(modelsDir, expDir), tol=optiParam['tol'], method='bounded', options=opts)
    else:
        res = minimize_scalar(residualsScalar, args=(modelsDir, expDir), tol=optiParam['tol'], method='brent', options=opts)
    d = {}
    d['funcalls']= res.nfev
    d['task']= res.message
    d['nIte']= NIter
    if verbose: print res.message
    return res.x,res.fun,d

def main(modelsDir, expDir, options={}, pBounds=None, scalarFunction = True):
    optiParam = {}
    optiParam['maxIter'] = 10
    optiParam['tol'] = 1e-4
    optiParam.update(options)
    if scalarFunction: return getOptiParamScalar(modelsDir, expDir, optiParam, pBounds)
    else:raise NotImplementedError