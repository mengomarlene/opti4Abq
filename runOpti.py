# scalar example for the opti4Abq project (multivariables)
# run as "python runScalarOpti_multiVariables"

import opti4AbqMultiVariables
import os

feModelDir = r"D:\myWork\FEModels\stuffIveTried\optimisation"
expDir = r"D:\myWork\FEModels\stuffIveTried\optimisation"

optiParam = {}
optiParam['maxIter'] = 40 # max number of function evaluation in the optimisation process !!there is more than one evalutation per iteration as the jacobian as to be computed!!
optiParam['eps'] = .1 # step taken to compute the jacobian by a finite difference method
optiParam['tol'] = 1e-3 # tolerance on the function value RMS error

p0 = (10.,500.)
bounds = [(1.,100.),(1.,3000.)]

#perform optimisation

p,fVal,info = opti4AbqMultiVariables.main(p0, feModelDir, expDir, pBounds=bounds, options=optiParam, scalarFunction=False)