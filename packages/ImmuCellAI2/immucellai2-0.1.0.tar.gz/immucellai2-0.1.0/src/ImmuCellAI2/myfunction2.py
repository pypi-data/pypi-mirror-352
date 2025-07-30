#!/usr/bin/python3
from immuCellAI2.myclasses import CLASS_FOR_RUN
from immuCellAI2.myfunction3 import ObtainCellTypeCateogry
import pandas
import os
import re
import sys
from multiprocessing import shared_memory
import multiprocessing as mp

def Obtainmyconfigpath():
   return (re.findall("^.*/", os.path.abspath(sys.argv[0])))[0] + "myconfig/"

def SelectGeneForDeconvolution(DFReferenceProfile, FileCoveredGenes = "", Method = "UsedMarker"):
   print("Select the gene for the fellowing deconvlution...")
   GeneUsedForDeconvolution = []
   DFReferenceProfileGenes = DFReferenceProfile.index.values
   if Method == "UsedMarker":   
      if FileCoveredGenes == "":
         #FileCoveredGenes = (re.findall("^.*/", os.path.abspath(sys.argv[0])))[0] + \
         #   "myconfig/MarkerUsedDeconvolution.txt"
         FileCoveredGenes = Obtainmyconfigpath() + "MarkerUsedDeconvolution.txt"
      GeneUsedForDeconvolution0 = (pandas.read_table(FileCoveredGenes, sep= "\t")).iloc[0].to_list()
      GeneUsedForDeconvolution = list(set(GeneUsedForDeconvolution0).intersection(set(DFReferenceProfileGenes)))
      return GeneUsedForDeconvolution
   elif Method == "SelectedFromGtf":
      print("A method seems like Bayesprism's , but under achieved...")
   else:
      pass

def CelltypeCategoryCheck(FileCellTypeCategory = "", celltypelist = [] ):
   print("Check the Celltype covered by configfile")
   if FileCellTypeCategory == "":
      FileCellTypeCategory = Obtainmyconfigpath() + "Celltype.cateogory"
   obtaincontent = ObtainCellTypeCateogry(FileCellTypeCategory)
   Allcelltype = []
   for keyword, oneCellTypeNode in obtaincontent.items():
      Allcelltype += [ keyword ] + oneCellTypeNode["AlsoKnownAs"] + oneCellTypeNode["RelatedNode"]["HisChidNode"]
   for onecelltype in celltypelist:
      if onecelltype not in Allcelltype:
         raise ValueError( "EEROR: reference matrix celltpe'{0}' NOT IN configfile, please CHECK...".format(onecelltype))
   return FileCellTypeCategory
   
def InitialCellTypeRatioCheck(InitialCellTypeRatio, FileInitialCellTypeRatio = "", ncelltype = 0):
   print("Check the celltype ratio initialization method...")
   if InitialCellTypeRatio[1] != "prior":
      return
   if FileInitialCellTypeRatio == "":
      FileInitialCellTypeRatio = Obtainmyconfigpath() + "myCellTypeRatio.initial"
   Expactedcelltypenum = (pandas.read(FileInitialCellTypeRatio, sep = "\t", header = 0, index_col = 0)).shape[1]
   if Expactedcelltypenum <1:
      raise ValueError("FAILED")
   elif Expactedcelltypenum in [ ncelltype, ncelltype -1 ]:
      return FileInitialCellTypeRatio
   else:
      InitialCellTypeRatio = 'randn'     

def PrepareData(FileReferenceProfile , 
   FileSampleExpressionProfile , 
   EnvironmentConfig = ("", "") ,
   FileCoveredGenes = "" ,
   FileCellTypeCategory = "" ,
   FileInitialCellTypeRatio = "" ,
   InitialCellTypeRatio = ('Normone', 'randn')):
   print("prepare for RunObject...")
   DFReferenceProfile0 = pandas.read_table(FileReferenceProfile, sep= "\t", header=0, index_col = 0)
   if DFReferenceProfile0.shape[1] < 2:
      print("warning: When open Reference File, might sep = ' ' not '\t'")
   print("celltype reference raw matrix:\n", DFReferenceProfile0.iloc[0:4, 0:4])
   ReferenceCelltype = {} 
   for oneCellType in DFReferenceProfile0.columns.values.tolist():
      numbertail = re.findall("\.[0-9]*$", oneCellType)
      oneCellType0 = oneCellType
      if numbertail != []: oneCellType = oneCellType[:-len(numbertail)]
      if oneCellType in ReferenceCelltype.keys(): 
         ReferenceCelltype[oneCellType].append(ReferenceCelltype[oneCellType])
      else: ReferenceCelltype[oneCellType] = [oneCellType0]
   DFReferenceProfile = pandas.DataFrame(columns = list(ReferenceCelltype.keys()),
       index = DFReferenceProfile0.index.values)
   for celltype in  DFReferenceProfile.columns.values:
        DFReferenceProfile[celltype] = (  
           DFReferenceProfile0.loc[:, ReferenceCelltype[celltype] ]).mean(axis = 1)
   print("celltype reference matrix:\n", DFReferenceProfile.iloc[0:4, 0:4])
   DFSampleExpressionProfile = pandas.read_table(FileSampleExpressionProfile, sep = "\t", header = 0, index_col = 0)
   print(" initialize a Object For running...") 
   print("environment config(cpus, threads): ", EnvironmentConfig)
   GeneUsedForDeconvolution = SelectGeneForDeconvolution(DFReferenceProfile)
   FileCellTypeCategory = CelltypeCategoryCheck(FileCellTypeCategory, celltypelist = list(ReferenceCelltype.keys()))
   FileInitialCellTypeRatio = InitialCellTypeRatioCheck(InitialCellTypeRatio, FileInitialCellTypeRatio, ncelltype = DFReferenceProfile.shape[1]) 
   DFReferenceProfile0 = DFReferenceProfile.loc[GeneUsedForDeconvolution, ]
   DFReferenceProfile0 = DFReferenceProfile0[DFReferenceProfile0.index.isin(DFSampleExpressionProfile.index)]   
   selected_DFSampleExpressionProfile = DFSampleExpressionProfile.loc[DFReferenceProfile0.index]
   selected_DFSampleExpressionProfile = selected_DFSampleExpressionProfile.transpose() 
   SampleList = list(selected_DFSampleExpressionProfile.index) 
   #DFReferenceProfile0 = DFReferenceProfile0.transpose() 
   return CLASS_FOR_RUN(
      DFReferenceProfile0, 
      selected_DFSampleExpressionProfile, 
      SampleList,
      EnvironmentConfig,
      #InitialCellTypeRatio = DictInitialCellTypeRatio)
      InitialCellTypeRatio = InitialCellTypeRatio,
      FileCellTypeCategory = FileCellTypeCategory,
      FileInitialCellTypeRatio = FileInitialCellTypeRatio,) 
