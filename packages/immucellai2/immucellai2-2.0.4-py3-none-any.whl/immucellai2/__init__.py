from .myfunction1 import MainRun # MainRun
from .myfunction2 import PrepareData # PrepareDate
from .myfunction3 import ExtractResult, SummaryCellRatio # ExtractResult()
from .myfunction4 import DrawPlotFunction1, DrawPlotFunction2 # visualization()

def run_ImmuCellAI2(reference_file, sample_file, output_file, thread_num=16, cpu_cores=8, seed=42):
    try:
        if not os.path.exists(reference_file):
            raise FileNotFoundError(f"Reference file not found: {reference_file}")
        run_obj = PrepareData(
            FileReferenceProfile=reference_file,
            FileSampleExpressionProfile=sample_file,
            EnvironmentConfig=(cpu_cores, thread_num),
            InitialCellTypeRatio=('Normone', 'randn')
        )
        result_obj = MainRun(run_obj, seed=seed)
        ExtractResult(result_obj, output_file, ResultIndex=0)
        return result_obj
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

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
   parser = argparse.ArgumentParser(description='ImmuCellAI2 deconvolution tool')
   parser.add_argument('-f', '--reference', dest = 'reference', required = True, default="", help = 'celltype reference experession matrix')
   parser.add_argument('-g', '--genes', dest = 'CoveredGenes', action = 'store_const', help = 'The genes used in the following deconvolution process selected by BayesPrism, temporary variance')
   parser.add_argument('-s', '--sample', dest = 'SampleExpressionProfile', required = True, help = 'the samples gene expression profile')
   parser.add_argument('-t', '--thread', dest = 'ThreadNum', type=int, default = 16, help = "threading numbers for deconvalution")
   parser.add_argument('-c', '--cores', dest="CpuCores", type=int, default = 8, help = "cpus cores numrs for deconvalution")
   parser.add_argument('-o', '--output', dest = "FileResult", default = "myresult/ResultDeconvolution.xlsx", help = " the path/filename to save the deconvaluted result.")
   parser.add_argument('--seed', type=int, default=42, help='Random seed')  
   args = parser.parse_args() 
   print("### Begin run deconvolution tools, wait....") 
   return run_ImmuCellAI2(
        reference_file=args.reference,
        sample_file=args.sample,
        output_file=args.output,
        thread_num=args.thread,
        cpu_cores=args.cores,
        seed=args.seed
    )
 
if __name__ == "__main__":
   main() 
