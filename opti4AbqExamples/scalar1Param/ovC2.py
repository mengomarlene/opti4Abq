"""
example file for opti4Abq toolbox (https://github.com/mengomarlene/opti4Abq)
calibration of greyscale-to-modulus mapping (1 parameter: a scale factor) able to represent a specimen stiffness (scalar objective function)
Need to change paths of files (line 12 and 30)
"""
import os

def parametrisedTests(scaleFactor):
    from abaqus import mdb
    backwardCompatibility.setValues(reportDeprecated=False)
    from abaqusConstants import ON,THREADS
    fileName = r'D:/myWork/procedures/opti4Abq_VC/opti4AbqExamples/scalar1Param/ovC2.inp'
    fileName.replace('/',os.sep)
    myModel = mdb.ModelFromInputFile(inputFileName=fileName, name='model')

    for mat in myModel.materials.keys():
        myMat = myModel.materials[mat]
        if mat.startswith('PMGS'):
            rho = myMat.density.table[0][0]
            E = rho*scaleFactor
            nu = 0.3
            del myMat.elastic
            myMat.Elastic(table=((E, nu), ))

    myJob = mdb.Job(model='model', name='scaledJob')
    myJob.writeInput()
    return myJob,mdb
    
def postPro(odbName):
    odbToolbox = r"D:\myWork\procedures\postPro4Abq_VC"
    import sys
    sys.path.append(odbToolbox)
    import postProTools.odbTools as odbTools
    import postProTools.extractors as ext
    myOdb = odbTools.openOdb(odbName)
    refPoint = 'REFERENCE_POINT_PART-2-1        1'
    extDispl = ext.getU_3(myOdb, refPoint)
    extDiplsList = [displ[0] for displ in extDispl]
    outForce = ext.getRF_3(myOdb,refPoint)
    extForceList = [force[0] for force in outForce]
    stiffness = extForceList[-1]/extDiplsList[-1]*1000.
    odbTools.writeValuesOpti(stiffness)
    myOdb.close()
    
if __name__ == '__main__':
    import sys
    optiParam = float(sys.argv[-1])
    job,mdb = parametrisedTests(optiParam)
    job.submit()
    job.waitForCompletion()
    mdb.close()
 