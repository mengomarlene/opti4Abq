"""
example file for opti4Abq toolbox (https://github.com/mengomarlene/opti4Abq)
calibration of material parameters (2 parameters) able to represent full load/displacement data
Need to change path of file  in buildModel (line 52)
"""
import sys,inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import exampleTools.buildModel as tools

def postPro(odbName):tools.postPro(odbName)

if __name__ == '__main__':
    p = {}
    import sys
    nbParam = 2
    paramToOpti = list()
    for arg in range(nbParam):
        paramToOpti.insert(0,float(sys.argv[-1-arg]))
    p['AFParameters'] = ( 0.3, 0.001, paramToOpti[0], paramToOpti[1], 0.)
    p['NPParameters'] = (0.07, 0.02, 0.0)
    p['inpFolder'] = currentdir
    p['inpFile'] = 'T1C1'
    job,mdb = tools.build(p)
    job.submit()
    job.waitForCompletion()
    mdb.close()
