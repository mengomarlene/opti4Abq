import os
from opti4AbqTools import *

verbose = False
        
def getOptiParamScalar(p0, modelsDir, expDir, optiParam, pBounds=None):
    opts = {'maxiter':optiParam['maxIter'],'disp':True,'ftol':optiParam['tol'],'eps':optiParam['eps']}
    from scipy.optimize import minimize
    res = minimize(residualsScalar, p0, method='L-BFGS-B', args=(modelsDir, expDir), jac=False, bounds=pBounds, tol=optiParam['tol'], options = opts,callback=callbackF)
    d = {}
    d['funcalls']= res.nfev
    d['nIte'] = res.nit
    # d['nIte']= NIter
    #d['grad'] = res.fjac
    d['task']= res.message
    if verbose: print res.message
    return res.x,res.fun,d
    
def main(p0, expDir, modelsDir, options={}, pBounds=None, scalarFunction = True):
    optiParam = {}
    optiParam['maxIter'] = 10
    optiParam['ftol'] = 1e-8
    optiParam.update(options)
    if scalarFunction:
        return getOptiParamScalar(p0, modelsDir, expDir, optiParam, pBounds)
    else:raise NotImplementedError