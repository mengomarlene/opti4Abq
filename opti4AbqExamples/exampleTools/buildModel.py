def build(_p={}):
    ## default abaqus modules
    from abaqus import *
    from abaqusConstants import *
    from caeModules import *

    baseInpFile = os.path.join(_p['inpFolder'],_p['inpFile']+'.inp')
    myModel = mdb.ModelFromInputFile(inputFileName=baseInpFile, name=_p['inpFile'])

    ## MATERIALS
    for mat in myModel.materials.keys():
        myMat = myModel.materials[mat]
        if 'DISC' in mat:
            # HOLZAPFEL
            del myMat.hyperelastic
            myMat.Hyperelastic(table=(_p['AFParameters'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL,localDirections=2)
        elif 'NUCLEUS' in mat:
            del myMat.hyperelastic
            myMat.Hyperelastic(materialType=ISOTROPIC, testData=OFF, type=MOONEY_RIVLIN, table=(_p['NPParameters'], ),behaviorType=INCOMPRESSIBLE)
        elif mat.startswith('PMGS'):
            rho = myMat.density.table[0][0]
            E = rho*7.3
            nu = 0.3
            del myMat.elastic
            myMat.Elastic(table=((E, nu), ))
    myJob = mdb.Job(model=myModel.name, name=myModel.name)
    myJob.writeInput(consistencyChecking=OFF)
    
    ## ADD LOCAL FIBRE ORIENTATION
    print "reading inp file - start"
    inpFile = open(myJob.name+'.inp', 'r')
    lines = inpFile.readlines()
    inpFile.close()
    orientationLine = [lineNo for lineNo,line in enumerate(lines) if line.startswith('*Orientation')]#gives the lines of the *ORIENTATION key
    print "reading inp file - done"
    print "writing inp file - start"
    oldLine = lines[orientationLine[0]]
    newLine = oldLine[0:-1]+',local directions=2\n'
    lines[orientationLine[0]] = newLine
    lines[orientationLine[0]+2] += '0.34,0.94,0.\n'
    lines[orientationLine[0]+2] += '-0.34,0.94,0.\n'
    newInputFileName = myJob.name+'.inp'
    newInpFile = open(newInputFileName, 'w')
    newInpFile.writelines(lines)
    newInpFile.close()
    print "writing inp file - done"
    myFibrousJob = mdb.JobFromInputFile(myJob.name,inputFileName=newInputFileName, numCpus=6, numDomains=6, scratch='.')
    return myFibrousJob,mdb


def postPro(odbName):
    odbToolbox = r"D:\myWork\procedures\postPro4Abq_VC"
    import sys
    sys.path.append(odbToolbox)
    print 'running postPro on ',odbName
    import postProTools.odbTools as odbTools
    import postProTools.extractors as ext
    myOdb = odbTools.openOdb(odbName)
    forceExt = ext.getRF_3(myOdb,'TOPRP')
    displExt = ext.getU_3(myOdb,'TOPRP')
    extDiplsList = [abs(displ[0]-displExt[0][0]) for displ in displExt]
    extForceList = [abs(force[0]-forceExt[0][0]) for force in forceExt]
    idx = [ n for n,i in enumerate(extDiplsList) if i>0.2 ]
    try:
        idx = idx[0]#disregard first .2 mm ie about 0.5%
    except:
        idx = -1# if no displacement is higher than 0.2, then output is 0
    odbTools.writeValuesOpti(zip(extDiplsList[idx:],extForceList[idx:]))
    myOdb.close()
   