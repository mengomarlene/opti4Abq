# scalar example for the opti4Abq project
# run as "python runScalarOpti"

import opti4Abq1Variable
import os

feModelDir = r"D:\myWork\FEModels\Sami\calibrationFilesOvine"
expDir = r"C:\Users\menmmen\Documents\othersWork\Sami_GSFactor_ovine\stiffnessData"

optiParam = {}
optiParam['maxEval'] = 40 # max number of function evaluation in the optimisation process !!there is more than one evalutation per iteration as the jacobian as to be computed!!
optiParam['epsfcn'] = .1 # step taken to compute the jacobian by a finite difference method
optiParam['ftol'] = 1e-6 # tolerance on the function value

bounds = (1e-4,0.1)

#perform optimisation
p,fVal,info = opti4Abq1Variable.main(feModelDir, expDir, pBounds=bounds, options=optiParam)