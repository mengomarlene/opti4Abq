import parameterFit1Parr
import os

feModelDir = os.path.join(r"D:\myWork\FEModels\ovineTetsGSFactor\ovineValidation")

optiParam = {}
optiParam['maxEval'] = 40 # max number of function evaluation in the optimisation process !!there is more than one evalutation per iteration as the jacobian as to be computed!!
optiParam['epsfcn'] = .1 # step taken to compute the jacobian by a finite difference method
optiParam['ftol'] = 1e-6 # tolerance on the function value

bounds = (1e-4,0.1)

#perform optimisation
p,fVal,info = parameterFit1Parr.main(feModelDir, feModelDir, pBounds=bounds, options=optiParam)