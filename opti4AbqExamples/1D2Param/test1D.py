"""
example file for opti4Abq toolbox (https://github.com/mengomarlene/opti4Abq)
calibration of cohesive interface parameters (2 parameters) able to represent local displacements
Need to change paths of files  in OneDtools (line 20, 59 and 82)
"""
import sys,inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import exampleTools.OneDtools as tools

def postPro(odbName):
    tools.postPro(odbName)

if __name__ == '__main__':
    import sys
    nbParam = 2
    sys.path.append(sys.argv[-nbParam-1])
    paramToOpti = list()
    for arg in range(nbParam):
        paramToOpti.insert(0,float(sys.argv[-1-arg]))
    p = {}
    p['cohesivePenalties'] = (paramToOpti[0],paramToOpti[1],1.)
    job,mdb = tools.createAnalysis(tools.getParameters(p))
    job.submit()
    job.waitForCompletion()
    mdb.close()