#!/usr/bin/python3
import numpy
import pandas
from numba import jit
from .shared_memory_manager import SharedMemoryManager
import multiprocessing as mp

class CLASS_FOR_RUN(object):
   def __init__(self, 
      CelltypesReferenceMatrix, 
      SamplesBulkRNAseqExpression, 
      sample_names_list,
      EnvironmentRun = (),
      EmceeParameterPosition = None,
      EmceeParameterNsteps = 1000 , # default: 10000
      EmceeParameterNwalkers = 1 , # default: 30
      EmceeParameterNdims = 0,
      EmceeParameterDiscard = 500,
      EmceeParameterThin = 1,
      #ModelRestrictCellTypeRatio = 'Minus',
      InitialCellTypeRatio = ("",""),
      MAPorMLE = 'MAP',
      FileCellTypeCategory = "",
      FileInitialCellTypeRatio = ""
      ):  
      manager = mp.Manager() 
      CelltypesReferenceMatrix_array = numpy.array(CelltypesReferenceMatrix)
      self.CelltypesReferenceMatrixManager = SharedMemoryManager(CelltypesReferenceMatrix_array.shape, dtype=CelltypesReferenceMatrix_array.dtype)
      numpy.copyto(self.CelltypesReferenceMatrixManager.get_shared_array(), CelltypesReferenceMatrix_array)
      self.CelltypesReferenceMatrix = self.CelltypesReferenceMatrixManager.get_shared_array()
      # Convert SamplesBulkRNAseqExpression to numpy array
      SamplesBulkRNAseqExpression_array = numpy.array(SamplesBulkRNAseqExpression)
      self.SamplesBulkRNAseqExpressionManager = SharedMemoryManager(SamplesBulkRNAseqExpression_array.shape, dtype=SamplesBulkRNAseqExpression_array.dtype)
      numpy.copyto(self.SamplesBulkRNAseqExpressionManager.get_shared_array(), SamplesBulkRNAseqExpression_array)
      self.SamplesBulkRNAseqExpression = self.SamplesBulkRNAseqExpressionManager.get_shared_array()
      self.SampleList = sample_names_list
      self.EnvironmentRun = CLASS_ENVIRONMENT_CONFIG(EnvironmentRun) 
      self.CellType = manager.list(CelltypesReferenceMatrix.columns.values) 
      self.MAPorMLE = MAPorMLE 
      self.FileCellTypeCategory = FileCellTypeCategory
      self.EmceeParameterlist = ( 
         EmceeParameterPosition, 
         EmceeParameterNsteps, 
         EmceeParameterNwalkers, 
         EmceeParameterNdims if EmceeParameterNdims >0 else len(self.CellType), 
         EmceeParameterDiscard,
         EmceeParameterThin, 
         InitialCellTypeRatio,
         FileInitialCellTypeRatio 
      )
      self.ShowInitialRunObject()
   def ShowInitialRunObject(self):
      print("Initilize RunObject completed with parameter ( CellType, SampleList,etc..)!!")
      if len(self.CellType) <3: ShowCellType = self.CellType
      else: ShowCellType = self.CellType[:3]
      if len(self.SampleList) <3: ShowSample = self.SampleList
      else: ShowSample = self.SampleList[:3]
      print("Celltype used for deconvoluation: %s..."%(', '.join(ShowCellType) ))
      print("Sample under the following analysis: %s ..."%(', '.join(ShowSample) ))  
   @property
   def EmceeParameter(self):
      return CLASS_FOR_EMCEEPARAMETER(
         position = self.EmceeParameterlist[0],
         CellType = self.CellType,
         nsteps = self.EmceeParameterlist[1], 
         nwalkers = self.EmceeParameterlist[2],
         ndims = self.EmceeParameterlist[3],
         discard = self.EmceeParameterlist[4],
         thin = self.EmceeParameterlist[5],
         InitialCellTypeRatio = self.EmceeParameterlist[6],
         FileInitialCellTypeRatio = self.EmceeParameterlist[7] 
      )

class CLASS_FOR_RUNRESULT(object):
   def __init__(self,
      #nnn = 44, 
      #CellTypeRatio = pandas.DataFrame([['celltype1'],[0]], columns=['celltype1',], index = ['celltype','sample1']), 
      #OtherResult1 = pandas.DataFrame([]), 
      #OtherResult2 = pandas.DataFrame([])
      SampleNameList = list(),
      CellTypeList = list(),
      FileCellTypeCategory = "",
      McmcSamplingResultList = numpy.array([[[[None]]]]),
      FlatSamplingResultList = numpy.array([[[None]]]),
      CellTypeRatioResult = None,
      CellTypeRatioResultFinal = None,
      SumCellTypeRatio = pandas.DataFrame([])
      ):
      #self.nnn = nnn
      #self.CellTypeRatio = CellTypeRatio
      self.CellType = CellTypeList
      self.SampleName = SampleNameList
      self.FileCellTypeCategory = FileCellTypeCategory
      self.McmcSamplingResult = self.EmceeFunction1( McmcSamplingResultList )
      self.FlatSamplingResult = self.EmceeFunction2( FlatSamplingResultList )
      #self.CellTypeRatioResult = self.CalculateRatio() if CellTypeRatioResult is None else CellTypeRatioResult
      self.CellTypeRatioResult, self.CellTypeRatioResultFinal = self.CalculateCellTypeRatio() \
         if CellTypeRatioResult is None else (CellTypeRatioResult, CellTypeRatioResultFinal)
      self.SumCellTypeRatio = SumCellTypeRatio
      self.OtherResult1 = self.OtherResult1Function()
      self.OtherResult2 = self.OtherResult2Function()
   def OtherResult1Function(self):
      print("OtherResult1 Have not achieved, return null,")
      return pandas.DataFrame([['']])
   def OtherResult2Function(self):
      print("OtherResult2 Have not achieved, return null,")
      return pandas.DataFrame([['']])
   def EmceeFunction1(self, McSamplingResultList ):
      mshape = McSamplingResultList.shape
      nCellType = len(self.CellType)
      NewMcSamplingResultList = numpy.zeros(( mshape[0], mshape[1], mshape[2], nCellType ))
      for sampleii in range(mshape[0]):
         #for iterationjj in range(mshape[1]):
         #print( numpy.mean( McSamplingResultList[sampleii, -1, :, :], axis = 0 ))
         NewMcSamplingResultList[sampleii, :, :, :] = \
            self.EmceeFunction2( McSamplingResultList[sampleii, :, :, :] )
      return  NewMcSamplingResultList
   def optimized_calculation(self, FlatSamplingResultOne, nCellType):
       if FlatSamplingResultOne.shape[1] == nCellType:
           return FlatSamplingResultOne / FlatSamplingResultOne.sum(axis=1)[:, None]
       elif FlatSamplingResultOne.shape[1] + 1 == nCellType:
           return numpy.column_stack((FlatSamplingResultOne, 1 - FlatSamplingResultOne.sum(axis=1)))
   def EmceeFunction2(self, FlatSamplingResultList):
       fshape = FlatSamplingResultList.shape
       nCellType = len(self.CellType)
       NewFlatSamplingResultList = numpy.zeros((fshape[0], fshape[1], nCellType))
       for sampleii in range(fshape[0]):
           FlatSamplingResultOne = FlatSamplingResultList[sampleii, :, :]
           NewFlatSamplingResultOne = self.optimized_calculation(FlatSamplingResultOne, nCellType)
           NewFlatSamplingResultList[sampleii, :, :] = NewFlatSamplingResultOne
       return NewFlatSamplingResultList
   def CalculateCellTypeRatio(self):
      CellTypeRatioResult = pandas.DataFrame(numpy.zeros(( len(self.SampleName),
                                                           len(self.CellType) )),
                               columns = self.CellType, index = self.SampleName )
      CellTypeRatioResultFinal = pandas.DataFrame(numpy.zeros(( len(self.SampleName),
                                                                len(self.CellType) )),
                                    columns = self.CellType, index = self.SampleName )
      for Oneii in range(len(self.SampleName)):
         SampleNameOne = self.SampleName[Oneii]
         FlatSamplingOne = self.FlatSamplingResult[Oneii, :, :]
         FlatSamplingOne = FlatSamplingOne / FlatSamplingOne.sum(axis =1)[:, None]
         FlatSamplingAverageOne = numpy.mean(FlatSamplingOne, axis=0 )
         CellTypeRatioResult.loc[SampleNameOne, ] = FlatSamplingAverageOne
         FinalSampling = self.McmcSamplingResult[Oneii, -1, :, :]
         CellTypeRatioResultFinal.loc[SampleNameOne, ] = numpy.mean(FinalSampling, axis = 0)
      return CellTypeRatioResult, CellTypeRatioResultFinal 
   def CalculateRatioOld(self):
      CellTypeRatioResult = pandas.DataFrame([[]], columns = self.CellType, index = self.SampleName )
      for Oneii in range(len(self.FlatSamplingResult)):
         FlatSamplingOne = self.FlatSamplingResult[Oneii]
         SampleNameOne = self.SampleName[Oneii]
         CellTypeRatioOne = list()
         for ii in range(len(self.Celltype)):
             CellTypeRatioOne.append((FlatSamplingOne[:, :, ii].sum(axis =1))[1])
         CellTypeRatioResult.loc[SampleNameOne,] = CellTypeRatioOne
      return CellTypeRatioResult
   def save_result(self, FilenameToSave, ResultIndex = 0):
      DataCelltypeRatio = self.get_result( ResultIndex = ResultIndex )
      (DataCelltypeRatio.T).to_excel(FilenameToSave, index = True, header = True)
      #DataCelltypeRatio.to_excel(FilenameToSave, index = False, header = True)
   def get_result(self, ResultIndex = 0):
     if ResultIndex == 0:
        return self.CellTypeRatioResult
     elif ResultIndex  == 1:
        return self.CellTypeRatioResultFinal
     else:
        pass
   @property
   def CellTypeCateogryContent(self):
      return self._CellTypeCateogryContent
   @CellTypeCateogryContent.setter
   def CellTypeCateogryContent(self, CellTypeCateogryContent ):
      self._CellTypeCateogryContent = CellTypeCateogryContent
      del self.FileCellTypeCategory


class CLASS_FOR_EMCEEPARAMETER(object):
   def __init__(self, position, CellType = list(), nsteps = 1000, 
      nwalkers = 1, 
      ndims = 0,
      discard = 500,
      thin = 1,
      #ModelRestrictCellTypeRatio = 'Minus',
      InitialCellTypeRatio = (('Minus','Normone'), ('randn', 'prior')), #(('Minus','Normone'), ('uniform', 'randn', 'prior'))
      FileInitialCellTypeRatio = "",
      CheckPosition = True):

      #self.position = position
      self.nsteps = nsteps
      self.CellType = CellType
      # mathceil = lambda x : int(x)+1
      self.nwalkers = nwalkers # if len(CellType) * 2 <= nwalkers else mathceil(len(CellType) *2 / 10 ) * 10
      #self.ModelRestrictCellTypeRatio = ModelRestrictCellTypeRatio
      self.InitialCellTypeRatioFunction( InitialCellTypeRatio )
      self.ndims = ndims
      self.discard, self.thin = discard, thin
      self.position = self.PositionInitilize(position, FileInitialCellTypeRatio) if CheckPosition is True else position
      #self.ShowInitialEmceeState()
   
   def ShowInitialEmceeState(self):
      print("initialize the emcee sampler completed!!")

   def InitialCellTypeRatioFunction(self, InitialCellTypeRatio):
      if isinstance(InitialCellTypeRatio, dict):
         self.InitialCellTypeRatio = InitialCellTypeRatio
         return 
      param1 = 'Minus' if InitialCellTypeRatio[0] == "" else InitialCellTypeRatio[0]
      param2 = 'prior' if InitialCellTypeRatio[1] == "" else InitialCellTypeRatio[1]
      self.InitialCellTypeRatio = {'ModelRestrictCellTypeRatio': param1, 'ValuesFromNORMorUNIFORM': param2 }

   def PositionInitilize(self, position, FileInitialCellTypeRatio):
     
      #colSums(CellTypeRatioMatrix)=1
      nCellType = len(self.CellType)
      position = numpy.unique(position)
      CellTypeRatioMatrix = numpy.zeros((self.nwalkers, nCellType))
      
      ###     remember to repair the bugs ~~~
      pshape = position.shape
      if pshape in [(self.nwalkers, nCellType), (self.nwalkers, nCellType -1 )]:
         print("Check emcee orginal parameters over, and then initialize succesfully...")
         if pshape[1] == nCellType:
            CellTypeRationMatrix = position
            CellTypeRationMatrix = CellTypeRationMatrix / CellTypeRationMatrix.sum(axis=1)[:, None]
         else:
            CellTypeRationMatrix = numpy.column_stack((position, 1 - position.sum(axis = 1)))
         #return CellTypeRationMatrix/CellTypeRationMatrix.sum(axis=1) 
      elif pshape in [(1, nCellType), (1, nCellType -1)]:
         print("Will initialize emcee by the only first invalid one row")
         if pshape[1] == nCelltype: CellTypeRatioGuess = position
         else: CellTypeRatioGuess = numpy.append(position, [ 1- position.sum()], axis=0)
            
      else:
         print("default by avergaed with randn / uniform ...")
         CellTypeRatioGuess = numpy.full((self.nwalkers,nCellType), 1/nCellType)
      if numpy.all(CellTypeRatioMatrix == 0 ):
         #NORMorUNIFORM = 'randn'
         #NORMorUNIFORM = 'uniform' # uniform, randn, prior
         #NORMorUNIFORM = 'prior'
         NORMorUNIFORM = self.InitialCellTypeRatio["ValuesFromNORMorUNIFORM"]
         if NORMorUNIFORM == 'randn':
            #CellTypeRatioMatrix = CellTypeRatioGuess + \
            #   1*(1 / nCellType )*1e-1*numpy.random.randn(self.nwalkers, nCellType)
            CellTypeRatioMatrix = CellTypeRatioGuess
            # CellTypeRatioMatrix = [1e-4 if x <= 0 else x for x in CellTypeRatioMatrix]
 	    
            print("~~condition number", numpy.linalg.cond(CellTypeRatioMatrix) )
         #elif NORMorUNIFORM == 'uniform':
         #   for rowii in range(CellTypeRatioMatrix.shape[0]):
         #      randvalue = numpy.array([ numpy.random.uniform(1, 1000) for i in range(nCellType) ])
         #      CellTypeRatioMatrix[rowii, ] = randvalue / randvalue.sum()
         elif NORMorUNIFORM == 'prior' :
            #print( os.getcwd() )
            #ScriptPath = ( re.findall('^.*/', os.path.abspath(sys.argv[0])) )[0]
            #
            #MyCellTypeRatioInitialMatrix = (pandas.read_table(ScriptPath+'myconfig/myCellTypeRatio.initial', 
            #   header=0,index_col=0, sep= "\t")).to_numpy()
            MyCellTypeRatioInitialMatrix = (pandas.read_table(FileInitialCellTypeRatio, 
               header=0,index_col=0, sep= "\t")).to_numpy()
            if CellTypeRatioMatrix.shape[1] == MyCellTypeRatioInitialMatrix.shape[1]:
               CellTypeRatioMatrix = MyCellTypeRatioInitialMatrix
            elif CellTypeRatioMatrix.shape[1] == MyCellTypeRatioInitialMatrix.shape[1] +1:
               CellTypeRatioMatrix = numpy.column_stack((MyCellTypeRatioInitialMatrix, 
                  1 - MyCellTypeRatioInitialMatrix.sum(axis=1)[:,None]))
            else: raise ValueError("format error...")

      #if self.ModelRestrictCellTypeRatio == 'Minus':
      if self.InitialCellTypeRatio["ModelRestrictCellTypeRatio"] == 'Minus':
         if nCellType == self.ndims: self.ndims -= 1
         if nCellType == CellTypeRatioMatrix.shape[1]:
            CellTypeRatioMatrix = CellTypeRatioMatrix / CellTypeRatioMatrix.sum(axis=1)[:, None]
            CellTypeRatioMatrix = CellTypeRatioMatrix[:, :-1]
      elif self.InitialCellTypeRatio["ModelRestrictCellTypeRatio"] == 'Normone':
         #CellTypeRatioMatrix = CellTypeRatioMatrix / CellTypeRatioMatrix.sum(axis=1)[:, None]
         pass
      Mshape = CellTypeRatioMatrix.shape
      print("total Celltype number %d\n...CellType Initial Ratio: shape(%d, %d)\n"%(nCellType, \
         Mshape[0], Mshape[1]), CellTypeRatioMatrix)
      self.ShowInitialEmceeState()
      # print("~~condition number", numpy.linalg.cond(CellTypeRatioMatrix) )
      return CellTypeRatioMatrix

   def mycopy( self ):
      return CLASS_FOR_EMCEEPARAMETER(
         nsteps = self.nsteps,
         CellType = self.CellType,
         nwalkers = self.nwalkers,
         ndims = self.ndims,
         InitialCellTypeRatio = self.InitialCellTypeRatio.copy(),
         #ModelRestrictCellTypeRatio = self.ModelRestrictCellTypeRatio,
         position = (self.position).copy(),
         CheckPosition = False
      )
    

class CLASS_ENVIRONMENT_CONFIG(object):
   def __init__(self, Environment):
      self.CpusCore, self.ThreadNum =  Environment

  

#exmaples1 = CLASSONE(111)
