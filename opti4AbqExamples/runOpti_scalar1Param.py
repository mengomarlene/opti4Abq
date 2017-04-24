# example for the opti4Abq project
# run as "python runOpti"

import opti4AbqTools.Opti4AbqClass as optiTools
import os
thisDir = os.getcwd()
feModelDir = os.path.join(thisDir,r"opti4AbqExamples\scalar1Param")
expDir = os.path.join(thisDir,r"opti4AbqExamples\scalar1Param")

optiParam = {}
optiParam['maxIter'] = 40 # max number of function evaluation in the optimisation process !!there is more than one evalutation per iteration as the jacobian as to be computed!!
optiParam['eps'] = .01 # step taken to compute the jacobian by a finite difference method
optiParam['ftol'] = .1 # tolerance on the function value 
optiParam['tol'] = 1e-5 # tolerance on the parameter value 

p0 = [0.32]
bounds = [[.0001],[.1]]

#perform optimisation
myOptiProcess = optiTools.Opti4Abq(p0, expDir, feModelDir)
myOptiProcess.setResidualsAsAbsolute(False)
myOptiProcess.setBounds(low = bounds[0],high = bounds[1])
myOptiProcess.setOptions(optiParam)
myOptiProcess.setVerbose(False)
p,fVal,info = myOptiProcess.runScalar()

print "done"

print p
print fVal
print info