from .myfunction1 import MainRun # MainRun
from .myfunction2 import PrepareData # PrepareDate
from .myfunction3 import ExtractResult, SummaryCellRatio # ExtractResult()
from .myfunction4 import DrawPlotFunction1, DrawPlotFunction2 # visualization()

def main():
   import argparse
   import time
   import multiprocessing as mp
   import numpy as np
   import random
   seed = 43
   np.random.seed(seed) 
   random.seed(seed)
   
   start_time = time.time()  
   mp.set_start_method('fork', force=True) 
   parser = argparse.ArgumentParser(description='Process some integers.')
   parser.add_argument('-f', '--reference', dest = 'ReferenceMatrix', required = True, default="", help = 'celltype reference experession matrix')
   parser.add_argument('-g', '--genes', dest = 'CoveredGenes', action = 'store_const', help = 'The genes used in the following deconvolution process selected by BayesPrism, temporary variance')
   parser.add_argument('-s', '--sample', dest = 'SampleExpressionProfile', required = True, help = 'the samples gene expression profile')
   parser.add_argument('-t', '--thread', dest = 'ThreadNum', type=int, default = 16, help = "threading numbers for deconvalution")
   parser.add_argument('-c', '--cores', dest="CpuCores", type=int, default = 8, help = "cpus cores numrs for deconvalution")
   parser.add_argument('-o', '--output', dest = "FileResult", default = "myresult/ResultDeconvolution.xlsx", help = " the path/filename to save the deconvaluted result.")
   parser.add_argument('--seed', type=int, default=42, help='Random seed')  
   args = parser.parse_args() 
   print("### Begin run deconvolution tools, wait....") 
   RunObject = PrepareData(
      FileReferenceProfile = args.ReferenceMatrix, 
      FileSampleExpressionProfile = args.SampleExpressionProfile,
      EnvironmentConfig = (args.CpuCores, args.ThreadNum),
      InitialCellTypeRatio = ('Normone', 'randn'), #randn, prior, # randn, uniform, prior, default ='prior'
   ) 
   ResultObject = MainRun(RunObject, seed=args.seed)
   ExtractResult(ResultObject, args.FileResult, ResultIndex = 0)
   end_time=time.time()
   total_time = end_time - start_time
   print(f"\n### Total execution time: {total_time:.2f} seconds ###")
   
if __name__ == "__main__":
   main() 
