import os
from opti4AbqTools import *

verbose = False
        
def getOptiParamVectorial(p0, modelScript, expData, optiParam, pBounds=None):
    from opti4AbqResiduals import residuals
    if pBounds is None:
        from scipy.optimize import leastsq
        nbParam = len(p0)
        pLSQ,covP,info,msg,ier = leastsq(residuals, p0, args=(modelScript, expData), full_output=True, maxfev=optiParam['maxIter']*nbParam*nbParam, epsfcn=optiParam['eps'], ftol=optiParam['tol'])
        if verbose: print msg
        fVal = info['fvec']
        d = {}
        d['funcalls']=info['nfev']
        d['nit'] = None
        d['grad'] = info['fjac']
        if ier in [1,2,3,4]:
            d['warnflag'] = 0
        else:
            d['warnflag'] = 2
        d['task']=msg
    else:
        from scipy.optimize import fmin_l_bfgs_b
        withBounds=True
        import numpy as np
        factorTol = optiParam['tol']/np.finfo(float).eps
        pLSQ,fVal,d = fmin_l_bfgs_b(residuals, p0, args=(modelScript, expData, withBounds), approx_grad=True, bounds=pBounds, factr=factorTol, epsilon = optiParam['eps'], disp=True, maxiter=optiParam['maxIter'],callback=callbackF)
        if verbose: print d
    return pLSQ,fVal,d
    
        
def getOptiParamScalar(p0, modelsDir, expDir, optiParam, pBounds=None):
    from opti4AbqResiduals import residualsScalar
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
    else:
        return getOptiParamVectorial(p0, modelsDir, expDir, optiParam, pBounds)

