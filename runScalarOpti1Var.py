# scalar example for the opti4Abq project
# run as "python runScalarOpti1Var"

import opti4Abq1Variable
import os

feModelDir = r"D:\myWork\FEModels\Sami\ovinePECalibration"
expDir = r"C:\Users\menmmen\Documents\othersWork\Sami_GSFactor_ovine\stiffnessData"

optiParam = {}
optiParam['maxIter'] = 40 # max number of iteration in the optimisation process !!
optiParam['tol'] = 1e-6 # tolerance on the function value (RMS error)

bounds = (1e-4,0.1)

#perform optimisation
p,fVal,info = opti4Abq1Variable.main(feModelDir, expDir, pBounds=bounds, options=optiParam)