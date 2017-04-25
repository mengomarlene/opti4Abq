# example for the opti4Abq project
# run as "python runOpti"

import opti4AbqTools.Opti4AbqClass as optiTools
import os
thisDir = os.getcwd()
feModelDir = os.path.join(thisDir,r"opti4AbqExamples\1D2Param")
expDir = os.path.join(thisDir,r"opti4AbqExamples\1D2Param")

p0 = [0.1,0.5]
bounds = [(.01,.01),(10.,10.)]

#perform optimisation
myOptiProcess = optiTools.Opti4Abq(p0, expDir, feModelDir)
myOptiProcess.setBounds(low = bounds[0],high = bounds[1])
p,fVal,info = myOptiProcess.run()

print "done"

print p
print fVal
print info