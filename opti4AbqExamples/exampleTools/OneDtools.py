
def deleteDefaultModel():
    from abaqus import mdb
    defaultName = 'Model-1'
    if defaultName in mdb.models.keys():
        del mdb.models[defaultName]
#-----------------------------------------------------
def applyInterpolatedDisplacement(myModel,node,x1,x2,d1,d2,BCName):
    x = node.coordinates
    a = (x[0]-x2[0])/(x1[0]-x2[0])
    b = (x[1]-x2[1])/(x1[1]-x2[1])
    d = (a*d1[0]+(1.-a)*d2[0],b*d1[1]+(1.-b)*d2[1])
    import regionToolset 
    import mesh
    nodeArray = mesh.MeshNodeArray(nodes=(node,))
    nodeRegion = regionToolset.Region(nodes=nodeArray)
    myModel.DisplacementBC(createStepName='displ', localCsys=None, name=BCName, region=nodeRegion, u1=d[0],u2=d[1])   
#-----------------------------------------------------
def postPro(odbName):
    odbToolbox = r"D:\myWork\procedures\postPro4Abq_VC"
    import sys
    sys.path.append(odbToolbox)
    import postProTools.odbTools as odbTools
    import postProTools.extractors as ext
    import math
    myOdb = odbTools.openOdb(odbName)
    myAssembly = myOdb.rootAssembly
    # PRODUCE NODE SET ON THE NODES I EXTRACT COORDINATES FROM.
    newSet = 'extractedDisplacement'.upper()

    myInstances = [myAssembly.instances['SECTIONED3_INSTANCE'],myAssembly.instances['SECTIONED4_INSTANCE'],myAssembly.instances['SECTIONED5_INSTANCE'],
    myAssembly.instances['INPLANE3_INSTANCE'],myAssembly.instances['INPLANE4_INSTANCE']]
    
    expPointsCoord = [[(0.606,1.0208),(0.6956,0.5452),(0.6975,0.10976)],[(0.7466,0.8459),(0.71216,0.4332),(0.7911,0.3266),(0.99157,0.1497)],[(1.1335,0.17328)],
    [(0.606,1.0208),(0.6956,0.5452),(0.6975,0.10976),(0.7466,0.8459),(0.71216,0.4332),(0.7911,0.3266),(0.99157,0.1497)],[(1.1335,0.17328)]]
    
    if newSet not in myAssembly.nodeSets.keys():
        nodeList = list()
        for i,instance in enumerate(myInstances):
            points = {}
            for node in instance.nodes:
                points[node.label] = list(node.coordinates)
            for ptNo in range(len(expPointsCoord[i])):
                shortList = list()
                for key, value in points.iteritems():
                    if (0.95*expPointsCoord[i][ptNo][0] < value[0] < 1.05*expPointsCoord[i][ptNo][0]) and (0.95*expPointsCoord[i][ptNo][1] < value[1] < 1.05*expPointsCoord[i][ptNo][1]):
                        shortList.append((instance.name.replace('instance','Geo'),(key,)))
                nodeList.append(shortList[0])
        myNodes = tuple(nodeList)
        myAssembly.NodeSetFromNodeLabels(name = newSet, nodeLabels = myNodes)
    displ = ext.getFinalU_1(myOdb,newSet)
    
    odbTools.writeValuesOpti(displ)
    myOdb.close()
#-----------------------------------------------------
def getParameters(_p={}):
    param = {}

    fileName = r'D:\myWork\procedures\opti4Abq_VC\opti4AbqExamples\1D2Param\test1D.inp'
    param['sipInpFile'] = fileName
    
    param['modelName'] = 'tt01'

    param['interfaceType'] = 'Cohesive'   #'Rough', 'Friction', 'CohesiveRough', 'Cohesive', 'CohesiveFriction'  
    param['frictionCoef'] = 0.1           #irrelevant if param['interfaceType']!='Friction' or  'CohesiveFriction'
    param['cohesivePenalties'] = (.1,.1,.1)
    param['normalStiffness'] = 1.

    param['timePeriod'] = 1. 
    param['numCpus'] = 1

    param.update(_p)
    return param
#-----------------------------------------------------    
def createAnalysis(param):

    from abaqus import *
    backwardCompatibility.setValues(reportDeprecated=False)
    from abaqusConstants import *
    from caeModules import *    
    import mesh
    Im2MeshToolbox = r"D:\myWork\procedures\2DImage2Mesh_VC"
    import sys
    sys.path.append(Im2MeshToolbox)
    from sipShell2Abq import shellTo2DGeo

    ## IMPORT FILE FROM SCANIP MODEL
    myModel = mdb.ModelFromInputFile(inputFileName=param['sipInpFile'], name=param['modelName'])
    shellTo2DGeo(myModel)
    deleteDefaultModel()

    ## SHORTCUTS
    myAssembly = myModel.rootAssembly
    allMats = myModel.materials

    ## STEP CREATION
    myModel.StaticStep(initialInc=0.01 ,timePeriod=param['timePeriod'], maxInc=.1, minInc=1e-9, name='displ', nlgeom=ON, previous='Initial')
    
    directions = list()
    matNames = list()
    slMaCouples = list()
    for i,myPart in enumerate(myModel.parts.values()):
        myPSet = myPart.sets
        part = myPart.name.split('_')[0]
        if part == 'INPLANE6':
            del myModel.parts['INPLANE6_Geo']
            del myAssembly.features['INPLANE6_instance']
            continue
            
        ## MATERIALS
        cSys = myPart.DatumCsysByThreePoints(coordSysType=CARTESIAN,origin=(0.,0.,0.),point1=(1.,0.,0.),point2=(0.,1.,0.))       
        mat = 'SM_'+part
        if allMats.has_key(mat):
            myMat = myModel.materials[mat]
        else:
            print 'material %s unknown!!!'%mat
            continue
            
        E = 0.06#equivalent GM only as we are perp to fibers!!
        nu = 0.499
        matParam = (E/(4*(1.+nu)),6*(1-2.*nu)/E)
        if matParam[1]==0.:# incompressible
            myMat.Hyperelastic(testData=OFF,table=(matParam,),materialType=ISOTROPIC,type=NEO_HOOKE
            ,behaviorType=INCOMPRESSIBLE)
        else:
            myMat.Hyperelastic(testData=OFF,table=(matParam,),materialType=ISOTROPIC,type=NEO_HOOKE
            ,behaviorType=COMPRESSIBLE)

        ## SECTION
        myModel.HomogeneousSolidSection(name='Section_%s'%part, material=mat, thickness=None)
        myPart.SectionAssignment(region=(myPart.faces[0],), sectionName='Section_%s'%part)
        ## BC'S
        
        myISet = myAssembly.instances['%s_instance'%part].sets
        dMin = 'NS_%s_WITH_XMIN'%part
        dMax = 'NS_%s_WITH_XMAX'%part

        if  myISet.has_key(dMin):
            myModel.PinnedBC(createStepName='displ', localCsys=None, name='fix_%d'%(i), region=myISet[dMin])
        if part == 'INPLANE5':
            x1 = (1.10898,1.29364)
            x2 = (1.29274,0.74189)
            d1 = (0.134,-0.12)
            d2 = (0.18,-0.10)
            for node in myISet['SF_INPLANE5_WITH_SECTIONNED6'].nodes:
                i += 1
                applyInterpolatedDisplacement(myModel,node,x1,x2,d1,d2,'mov_%d'%(i))

        ## Get Master/Slave couples
        oParts = list(myModel.parts.keys())
        oParts.remove(myPart.name)
        for setName in myPSet.keys():
            if setName.startswith('SF_%s_WITH_'%part):
                for oPart in oParts:
                    oPartName = oPart.split('_')[0]
                    if oPartName=='INPLANE6':
                        continue
                    elif oPartName in setName:
                        if [oPartName,part] not in slMaCouples:
                            slMaCouples.append([part,oPartName])

    ## CONSTRAINTS - same for all interfaces!!
    for nbInteraction,slMaCouple in enumerate(slMaCouples):
        masterName = 'SF_%s_WITH_%s'%(slMaCouple[1],slMaCouple[0])
        slaveName = 'SF_%s_WITH_%s'%(slMaCouple[0],slMaCouple[1])
        myMaInstance = myAssembly.instances['%s_instance'%slMaCouple[1]]
        mySlInstance = myAssembly.instances['%s_instance'%slMaCouple[0]]
        from interactions import Interactions
        inter = Interactions(myModel)
        inter.setName('interaction_%i'%nbInteraction)
        if param['interfaceType'] == 'Tie':
            inter.setMasterSlave(myMaInstance.sets[masterName],mySlInstance.sets[slaveName])
            inter.setInteractionToTie()
        else:
            inter.setMasterSlave(myMaInstance.surfaces[masterName],mySlInstance.surfaces[slaveName])
            inter.setNormalStiffness(param['normalStiffness'])
            if param['interfaceType'] == 'Friction':
                inter.setFrictionBehaviour('Friction')
            elif param['interfaceType'] == 'Rough':
                inter.setFrictionBehaviour('Rough')
            elif param['interfaceType'] == 'Cohesive':
                inter.setCohesiveBehaviour(useDefaultBehaviour=False,penalties=param['cohesivePenalties'])
            elif param['interfaceType'] == 'CohesiveRough':
                inter.setCohesiveBehaviour(useDefaultBehaviour=False,penalties=param['cohesivePenalties'])
                inter.setFrictionBehaviour('Rough')
            elif param['interfaceType'] == 'CohesiveFriction':
                inter.setCohesiveBehaviour()
                inter.setFrictionBehaviour('Friction')
        inter.createInteraction()

    ## JOB
    myJob = mdb.Job(model=param['modelName'], name=param['modelName'])
    myJob.writeInput(consistencyChecking=OFF)
    if param['numCpus']>1: 
        myJob.setValues(numCpus=param['numCpus'],numDomains=param['numCpus'],multiprocessingMode=DEFAULT)
    return myJob,mdb
    