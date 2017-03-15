# example for the opti4Abq project (multivariables)
# run as "python runOpti"

import opti4AbqMultiVariables
import os

feModelDir = r"D:\myWork\Ultrapsine\materialModelCalibration\Control"
expDir = r"D:\myWork\Ultrapsine\expFiles"
#ultrapsine samples calibrated for k1, k2

optiParam = {}
optiParam['maxIter'] = 40 # max number of function evaluation in the optimisation process !!there is more than one evalutation per iteration as the jacobian as to be computed!!
optiParam['eps'] = .1 # step taken to compute the jacobian by a finite difference method
optiParam['tol'] = 10. # tolerance on the function value 

bounds = [(.1,100.),(.5,100.)]
p0 = [0.32,3.85]
#perform optimisation

p,fVal,info = opti4AbqMultiVariables.main(p0, expDir, feModelDir, pBounds=bounds, options=optiParam, scalarFunction=False)