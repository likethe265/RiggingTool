

import maya.OpenMayaMPx as omMPx
import maya.OpenMaya as om
import maya.cmds as mc
import math
import numpy

 
class RbfBlender(omMPx.MPxNode):
  kPluginNodeId = om.MTypeId(0x00124700)  # unique ID registered to me!
  
  allInputs_compound = om.MObject()
  sampleDimensions = om.MObject()
  numInputGroups = om.MObject()
  deletedIndices = om.MObject()
  
  dataPoint_array = om.MObject()
  sample_array = om.MObject()
  
  lookup_input = om.MObject()
  R_input = om.MObject()

  typeIndex = om.MObject()

  typeDic = {0: 'MQ', 1: 'gaussian', 2: 'thinPlate', 3: 'mcSmoothGaussian', 4: 'shiftedLog'}
  output = om.MObject()
  
  def __init__(self):
    omMPx.MPxNode.__init__(self)

      
  def compute(self, plug, data):
  
    # Begin constructing data points and samples from the user inputs. 
    # The user has specified the number of 'sites' so we need to loop through 
    # the dataBlock to see what's actually there an construct some lists. 
    
    dataPoints = list()
    pyFValues = list()  # the function values are our samples
    
    allInputs_mDataArrayHandle = data.inputArrayValue( RbfBlender.allInputs_compound )
    # numInputs = allInputs_mDataArrayHandle.elementCount()
    numInputs = data.inputValue( RbfBlender.numInputGroups ).asInt()
    sampleDimensions = data.inputValue( RbfBlender.sampleDimensions ).asInt()
    
    # get the deleted indices. this is because we can't differentiate between "optimized" 
    # array indices and deleted indices. 
    deletedIndices_mArrayDataHandle = data.inputArrayValue(RbfBlender.deletedIndices)
    deletedIndices = list()
    numDeletedIndices = deletedIndices_mArrayDataHandle.elementCount()
    
    for i in xrange( numDeletedIndices ):
      deletedIndices_mArrayDataHandle.jumpToArrayElement(i)
      di_i_mDataHandle = deletedIndices_mArrayDataHandle.inputValue()
      deletedIndices.append( di_i_mDataHandle.asInt() )
    
    
    for i in xrange( numInputs + numDeletedIndices ):
      if not i in deletedIndices: 
        # jumpToArrayElement handles the sparse array. 
        # for exmaple, create three inputs, and delete the entry at index 1. 
        #i 0,   array element index 0
        #i 1,   array element index 2
        
        # Just like with the individual attrs, if entire compounds with arrays have zero as their values, 
        # maya will "optimize" by ignoring that whole compound. This is harder to detect than with regular values
        # because the elements still show up in the node editor. Can be checked though with mc.getAttr(<theCompoundAttr>, mi=True)
        # the question becomes: how do you differentiate between an index that has been optimized, with one that 
        # has been deleted by the user? you can't just flatly assume zero, like I do with the others because then you might get
        # multiple "zero compounds" which will break the rbf math. 
        # The only way I can think of, is by storing an array of which indices have been deleted by the user. 
        
        elementOptimized = 0
        thisDataPoint = [0.0, 0.0, 0.0]
        thisSampleSite = list()
        for l in xrange(sampleDimensions): 
          thisSampleSite.append(0.0)
        
        try:  # test for optimized
          allInputs_mDataArrayHandle.jumpToElement(i)
                  
        except: 
          elementOptimized = 1  
          
        if not elementOptimized: 
          
          # So now this is the compound! how do I get the children... ???  you just pass in the object type
          # internally. it must be searching the children of the compound for a "type" 
          currentCompound_i_mDataHandle =  allInputs_mDataArrayHandle.inputValue() 
          dataPoint_mDataHandle = currentCompound_i_mDataHandle.child(RbfBlender.dataPoint_array)
          sample_mDataHandle = currentCompound_i_mDataHandle.child(RbfBlender.sample_array)
          # convert the dataHandle to an daraArrayHandle... you'd think it would know its own type when being 
          # returned eh.  nah. 
          dataPoint_mArrayDataHandle = om.MArrayDataHandle(dataPoint_mDataHandle)
          sample_mArrayDataHandle = om.MArrayDataHandle(sample_mDataHandle)
          
          for j in xrange( 3 ):  # we know this is always 3 for this implemenation
          
            # Maya "optimizes" array attrs with values equal to zero, by removing them.  This causes the 
            # plugin to fail until the attribute editor is opened and the data is reset. Highly annoying. 
            # Work around is to catch the jumpToElement and if it can't find the element, we assume a value
            # of zero. 
            dataPointValue = 0.0
            try:
              dataPoint_mArrayDataHandle.jumpToElement(j)
              dataPointValue = dataPoint_mArrayDataHandle.inputValue().asFloat()
            except:
              pass
              
            thisDataPoint[j] = dataPointValue
          
          for k in xrange( sampleDimensions ):   
            # there shouldn't be a sparse array for the samples because I only add/remove from the end
            sampleValue = 0.0
            try:
              sample_mArrayDataHandle.jumpToElement(k)
              sampleValue = sample_mArrayDataHandle.inputValue().asFloat()
            except:
              pass        
            
            thisSampleSite[k] = sampleValue       
        
        dataPoints.append( thisDataPoint )
        pyFValues.append( thisSampleSite )
      
      # ------------- Done building data points / sample site lists  -------------------------------- #
      
      
    R = data.inputValue(RbfBlender.R_input).asFloat()
    lookup_mDataArrayHandle = data.inputArrayValue( RbfBlender.lookup_input )
    
    lookupValues = list()
    for m in xrange( 3 ): # always gonna be 3.. 
      lookupValue = 0.0
      try: 
        lookup_mDataArrayHandle.jumpToElement(m)
        lookupValue = lookup_mDataArrayHandle.inputValue().asFloat()
      except:  
        pass
      lookupValues.append( lookupValue )
    
    # ----------------- do the math here ---------------- #
    typeIndex = data.inputValue(RbfBlender.typeIndex).asInt()

    outValues = computeWeights( pyFValues, dataPoints, lookupValues, RbfBlender.typeDic[typeIndex], R )
    # ----------------- done doing math ----------------- #   lol
    
    output_mArrayDataHandle = data.outputArrayValue( RbfBlender.output )
    sampleDimensions = data.inputValue( RbfBlender.sampleDimensions ).asInt()


    for n in xrange( sampleDimensions ):   # actually read the sample dimensions here to avoid update issues
      output_mArrayDataHandle.jumpToArrayElement( n )
      output_n_mDataHandle = output_mArrayDataHandle.outputValue()

      if outValues[n] > 1.0:
        outValues[n] = 1.0
      elif outValues[n] < 0.0:
        outValues[n] = 0.0

      output_n_mDataHandle.setFloat(outValues[n])
    
    data.setClean(plug)
  
def creator():
    return omMPx.asMPxPtr( RbfBlender() ) 
 
def initialize():

  
  cAttr = om.MFnCompoundAttribute()
  RbfBlender.allInputs_compound = cAttr.create( "inputsCompound", "ic" )
  cAttr.setArray(True)
  cAttr.setStorable(True)
  cAttr.setKeyable(True)
  cAttr.setIndexMatters(False)
  cAttr.setDisconnectBehavior(om.MFnNumericAttribute.kNothing)
  
  nAttr = om.MFnNumericAttribute()
  nAttr1 = om.MFnNumericAttribute()
  nAttr2 = om.MFnNumericAttribute()
  nAttr3 = om.MFnNumericAttribute()
  nAttr4 = om.MFnNumericAttribute()
  
  RbfBlender.dataPoint_array = nAttr1.create('dataPoint', 'dp', om.MFnNumericData.kFloat, 0.0 )
  nAttr1.setArray(True)
  nAttr1.setStorable(True)
  nAttr1.setKeyable(True)
  nAttr1.setIndexMatters(False)
  nAttr1.setDisconnectBehavior(om.MFnNumericAttribute.kNothing)
  
  RbfBlender.sample_array = nAttr2.create('sample', 's', om.MFnNumericData.kFloat, 0.0 )
  nAttr2.setArray(True)
  nAttr2.setStorable(True)
  nAttr2.setKeyable(True)
  nAttr2.setIndexMatters(False)
  nAttr2.setDisconnectBehavior(om.MFnNumericAttribute.kNothing)
  
  cAttr.addChild( RbfBlender.dataPoint_array )
  cAttr.addChild( RbfBlender.sample_array )
  
  RbfBlender.lookup_input = nAttr3.create("lookup", "lu", om.MFnNumericData.kFloat )
  nAttr3.setArray(True)
  nAttr3.setStorable(True)
  nAttr3.setKeyable(True)
  nAttr3.setIndexMatters(False)
  nAttr3.setDisconnectBehavior(om.MFnNumericAttribute.kNothing)
  
  RbfBlender.R_input = nAttr.create("tuningValue", "tv", om.MFnNumericData.kFloat, 1.0 )
  nAttr.setStorable(True)
  nAttr.setKeyable(True) 
  
  RbfBlender.sampleDimensions = nAttr.create("numSampleDimensions", "nsd", om.MFnNumericData.kInt, 1)
  nAttr.setStorable(True)
  nAttr.setKeyable(False)
  
  RbfBlender.numInputGroups = nAttr.create("numInputGroups", "nig", om.MFnNumericData.kInt, 0)
  nAttr.setStorable(True)
  nAttr.setKeyable(False)
  
  RbfBlender.deletedIndices = nAttr4.create("deletedIndices", "di", om.MFnNumericData.kInt, 999)
  nAttr4.setArray(True)
  nAttr4.setStorable(True)
  nAttr4.setIndexMatters(False)
  nAttr4.setDisconnectBehavior(om.MFnNumericAttribute.kNothing)

  RbfBlender.typeIndex = nAttr.create("typeIndex", "ti", om.MFnNumericData.kInt, 0)
  nAttr.setStorable(True)
  nAttr.setKeyable(True)

  # ------------- initialize output plug      ------------------------------------------------------------- #
  
  nAttrOut = om.MFnNumericAttribute()
  RbfBlender.output = nAttrOut.create('output', 'o', om.MFnNumericData.kFloat )
  nAttrOut.setArray(True)
  nAttrOut.setStorable(True)
  
  RbfBlender.addAttribute( RbfBlender.allInputs_compound )
  RbfBlender.addAttribute( RbfBlender.lookup_input )
  RbfBlender.addAttribute( RbfBlender.R_input )
  RbfBlender.addAttribute( RbfBlender.sampleDimensions )
  RbfBlender.addAttribute( RbfBlender.numInputGroups )
  RbfBlender.addAttribute( RbfBlender.deletedIndices )
  RbfBlender.addAttribute(RbfBlender.typeIndex)
  RbfBlender.addAttribute( RbfBlender.output )  
  
  
  
  # ------------- do attribute effects stuff ------------------------------------------------------------- #
  
  RbfBlender.attributeAffects( RbfBlender.allInputs_compound, RbfBlender.output )
  RbfBlender.attributeAffects( RbfBlender.lookup_input, RbfBlender.output )
  RbfBlender.attributeAffects( RbfBlender.R_input, RbfBlender.output )
  # RbfBlender.attributeAffects( RbfBlender.sampleDimensions, RbfBlender.output )


def constructDistanceMatrix( dataPoints, interpType,  R ): 
  
  pyMatrix = list()
  for i in xrange( len(dataPoints) ): 
    newRow = list()
    for j in xrange( len(dataPoints) ):
      d_squared = distanceSquared( dataPoints[i], dataPoints[j] )
      newRow.append( rbfKernel( interpType, R, d_squared ) )
    pyMatrix.append( newRow )
  
  return numpy.array( pyMatrix )
  

def computeWeights( pyFValues, dataPoints, lookup, interpType, R ):
    
  fValues = numpy.array( pyFValues )  
  G = constructDistanceMatrix( dataPoints, interpType,  R )
  
  numSites = len( dataPoints )  
  
  if numSites == 0:  # catch before user has entered inputs
    return [0.0]
    
  numSamplesPerSite = len( pyFValues[0] )
  
  finalValues = list()
  
  for j in xrange( numSamplesPerSite ):  # M
    finalValues.append( 0.0 )
  
  try: 
    GInv = numpy.linalg.inv(G)
  except: 
    return finalValues  # a zero array at this point
  
  # construct a column vector of the values we look up
  # can dot prod everything in one go!! ( was previously doing this operation 3 times :D )
  weights = numpy.dot( GInv, fValues )
  
  for k in xrange( numSites ):
    distSq = distanceSquared( lookup, dataPoints[k] )
    kernelMult = rbfKernel( interpType, R, distSq )
    for m in xrange( numSamplesPerSite ): 
      finalValues[m] += weights[k][m] * kernelMult
      #finalValue_x += weights[k][0] * rbfKernel( interpType, R, distSq )    
      #finalValue_y += weights[k][1] * rbfKernel( interpType, R, distSq ) 
      #finalValue_z += weights[k][2] * rbfKernel( interpType, R, distSq ) 

  # return [ finalValue_x, finalValue_y, finalValue_z ] 
  return finalValues
  
  
  
def rbfKernel( interpType, R, d_squared ):
    '''
    Description:
    Based on some radial kernel, calculate a value based on a squared distance
    and some constant.

    Accepts:
    interpType - a string to identify which kernel
    R - Some constant float value > 0.  This value is how you tune your results basically.
        It all depends on the scale of the scene, units etc etc.
    d_squared - A float of the squared distance between two objects.

    Returns:
    A float. The result of the operation.

    '''
  
    value = float()
    EPSILON = 10e-1
    # print interpType
    # MQ is the original Hardy method. Good for reconstructing hillsides based
    # on height data samples.
    if interpType == 'MQ':
        value = math.sqrt( R**2 + d_squared )

    # Good general purpose. R values lower than 1.0 produce results. Can become
    # unstable around 0.0001  depending on mesh
    elif interpType== 'gaussian':
        value = math.exp(-R * d_squared )
        # value = math.exp( -d_squared / R**2 )

    elif interpType == 'thinPlate':
        # math.log is the natural log in python
        # print 'd_squared', d_squared
        #value = math.log(math.sqrt(d_squared)+EPSILON)*d_squared
        value = (d_squared) * math.log( d_squared+EPSILON )
    
    # this is Michael Comet's RBF kernel. Not tested much.
    elif interpType == 'mcSmoothGaussian':
        value = 1 - math.exp( -d_squared * 10 / (2.0*R) )
    
    # Good for quite local deformation. So a high influence from near by
    # driver.  A good R value is something like 1.0-10.0 (can't be lower than 1.0 )
    elif interpType=='shiftedLog':
        value = math.sqrt(math.log10(d_squared + R))

    else:
        return None

    return value

def distanceSquared( p1, p2 ): 
    '''
    Description:
    Return the squared distance between two points of n dimension. 
  
    Accepts:
    p1 - the first point (python list, n floats)
    p2 - the first point (python list, n floats)

    Retuns:
    the squared distance - float

    '''
    distSq = float()

    for i in xrange( len(p1) ):
        distSq += (p2[i]-p1[i])**2

    return distSq

def printMatrix( matrix ): 
    '''
    Desc:
    Util to print matrix nicely

    Accepts:
    matrix - A list of lists
  
    '''

    for row in matrix:
        printRow = ''
        for element in row:
            printRow+= '%0.2f\t' % element
            print printRow
    

    
 
def initializePlugin(obj):
    plugin = omMPx.MFnPlugin(obj, 'testNode', '0.1', 'NonLinearVFX')
    try:
        plugin.registerNode( 'rbfBlender', RbfBlender.kPluginNodeId, creator, initialize )
    except:
        raise RuntimeError, 'uh oh, initialization fail'
    '''
    try:
        plugin.registerCommand( 'addDataPoint', testNodeCmd.creator, testNodeCmd.syntaxCreator )
    except:
        raise RuntimeError, 'Failed to register command'
    '''
    
def uninitializePlugin(obj):
    plugin = omMPx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(RbfBlender.kPluginNodeId)
    except:
        raise RuntimeError, 'oh dear, this node does not want to unload'
        
    ''' 
    try:
        plugin.deregisterCommand('addDataPoint')
    except:
        raise RuntimeError, 'Failed to unregister command'    
    '''