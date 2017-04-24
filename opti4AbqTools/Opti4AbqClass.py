class Opti4Abq:
    """Class Opti4Abq
    Opti4Abq(method,data,models)
    Methods:
        setBounds(low,high):
        setOptions(optiOptions):
        setVerbose(verbose=False):
        setResidualAsAbsolute(absolute)

        runScalar()#optimisation for a scalar residuals
        run()#other optimisation
    """
    def __init__(self,initValues,data,models):
        self.p0 = initValues
        self.dataPath = data
        self.modelsPath = models
        self.absDiff = False
        self.bounds = None
        self.options = {}
        self.verbose = False
    #-----------------------------------------------------
    def setResidualsAsAbsolute(self,absolute=False):
        self.absDiff = absolute
    def setBounds(self,low=[-float('Inf')],high=[float('Inf')]):
        assert len(low)==len(high), "lower and higher bounds need to be the same lenght (= number of opti parameters)"
        if len(low) >1:
            newBounds = [[low[i],high[i]] for i in range(len(low))]
        else: newBounds = [low[0],high[0]]
        self.bounds = newBounds
    def setOptions(self,optiOptions={}):
        assert isinstance(optiOptions,dict), "optimisation options need to be defined as a dictionary"
        self.options = optiOptions
    def setVerbose(self,verbose=False):
        self.verbose = verbose
    #-----------------------------------------------------
    def runScalar(self):
        return self.__minimize(scalarResidual = True)
    def run(self,noLBFGS=True):
        return self.__minimize(scalarResidual = False, noLBFGS=noLBFGS)
    #-----------------------------------------------------
    #-----------------------------------------------------
    def __isOneParam(self):
        if isinstance(self.p0,float) or len(self.p0) == 1:
            return True
        else: return False
    #-----------------------------------------------------
    def __minimize(self,scalarResidual=False, noLBFGS=True):
        optiParam = {}
        optiParam['maxIter'] = 10
        optiParam['tol'] = 1e-4
        optiParam['eps'] = 1e-4
        self.options.update(optiParam)
        optiParam['gtol'] = self.options['tol']/10000.
        optiParam['ftol'] = self.options['tol']/10000.
        self.options.update(optiParam)
        if self.__isOneParam():
            return self.__runScalarOpti(scalarResidual, optiParam)
        else:
            return self.__runOpti(scalarResidual, optiParam, noLBFGS)
    #-----------------------------------------------------
    def __runOpti(self, scalarResidual=False, optiParam={}, noLBFGS=True):
        from runAbqTools import callbackF
        import numpy as np
        if scalarResidual:
            from opti4AbqResiduals import residualsScalar
            opts = {'maxiter':optiParam['maxIter'],'disp':self.verbose,'ftol':optiParam['ftol'],'eps':optiParam['eps']}
            from scipy.optimize import minimize
            if self.bounds is None:
                opts['norm'] = 2
                opts['gtol'] = optiParam['gol']
                res = minimize(residualsScalar, self.p0, method='CG', args=(self.modelsPath, self.dataPath, self.absDiff, self.verbose), jac=False, tol=optiParam['tol'], options = opts,callback=callbackF)
            else:
                opts['ftol'] = optiParam['ftol']
                res = minimize(residualsScalar, self.p0, method='L-BFGS-B', args=(self.modelsPath, self.dataPath, self.absDiff, self.verbose), jac=False, bounds=self.bounds, tol=optiParam['tol'], options = opts, callback=callbackF)
            d = {}
            d['funcalls']= res.nfev
            d['task']= res.message
            d['grad'] = res.jac
            if self.verbose: print res.message
            return res.x,res.fun,d
        else:
            from opti4AbqResiduals import residuals
            if self.bounds is None:
                from scipy.optimize import leastsq
                nbParam = len(self.p0)
                pLSQ,covP,info,msg,ier = leastsq(residuals, self.p0, args=(self.modelsPath, self.dataPath, False, self.absDiff, self.verbose), Dfun = None, full_output=True, maxfev=optiParam['maxIter']*nbParam^nbParam, epsfcn=optiParam['eps'], ftol=optiParam['ftol'])
                fVal = info['fvec']
                d = {}
                d['funcalls'] = info['nfev']
                d['grad'] = info['fjac']
                d['task'] = msg
                if self.verbose: print msg
            else:
                if noLBFGS:
                    nbParam = len(self.p0)
                    if nbParam>1:
                        newBounds = [[],[]]
                        for pair in self.bounds:
                            newBounds[0].append(pair[0])
                            newBounds[1].append(pair[1])
                    else:newBounds=self.bounds
                    from scipy.optimize import least_squares #trf method - Trust Region Reflective algorithm, particularly suitable for large sparse problems with bounds. Generally robust method.
                    res = least_squares(residuals, self.p0, args=(self.modelsPath, self.dataPath, True, self.absDiff, self.verbose), bounds=newBounds, ftol=optiParam['ftol'], xtol=optiParam['tol'], gtol=optiParam['gtol'], diff_step=optiParam['eps'], max_nfev=optiParam['maxIter']*nbParam^nbParam, verbose=2)
                    pLSQ = res.x
                    fVal = res.fun
                    if self.verbose: print res.message
                    d = {}
                    import counter
                    d['funcalls'] = res.nfev
                    d['task']= res.message
                    d['grad'] = res.jac
                    if self.verbose: print res.message
                else:
                    from scipy.optimize import fmin_l_bfgs_b
                    factorTol = optiParam['ftol']/np.finfo(float).eps
                    pLSQ,fVal,d = fmin_l_bfgs_b(residuals, self.p0, args=(self.modelsPath, self.dataPath, True, self.absDiff, self.verbose), approx_grad=True, bounds=self.bounds, factr=factorTol, epsilon = optiParam['eps'], disp=True, maxiter=optiParam['maxIter'], callback=callbackF)
                    if d['warnflag'] == 0:d['task'] = "succesfull convergence"
                    elif d['warnflag'] == 1:d['task'] = "too many function evaluations or too many iterations"
                    if self.verbose: print d
            return pLSQ,fVal,d         
    #-----------------------------------------------------
    def __runScalarOpti(self, scalarResidual, optiParam):
        if scalarResidual:
            from opti4AbqResiduals import residualsScalar
            from scipy.optimize import minimize_scalar
            opts = {'maxiter':optiParam['maxIter'],'disp':True}
            if self.bounds is not None:
                res = minimize_scalar(residualsScalar, bounds=self.bounds, args=(self.modelsPath, self.dataPath, self.absDiff, self.verbose), tol=optiParam['tol'], method='bounded', options=opts)
            else:
                res = minimize_scalar(residualsScalar, args=(self.modelsPath, self.dataPath, self.absDiff, self.verbose), tol=optiParam['tol'], method='brent', options=opts)
            d = {}
            d['funcalls']= res.nfev
            d['task']= res.message
            d['grad'] = 'N/A'
            if self.verbose: print res.message
            return res.x,res.fun,d
        else:
            return self.__runOpti(False, optiParam, True)

     