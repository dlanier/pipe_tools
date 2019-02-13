##############################################################

###       This WDL script calls the CutAdapt WDL Task       ##

##############################################################

import "MayomicsVC/src/wdl/Alignment/Tasks/trim_sequences.wdl" as TRIMSEQ

workflow RunTrimSequencesTask {

   Array[Array[File]] InputReads   # One lane per subarray with one or two input reads
   Boolean PairedEnd               # Variable to check if single ended or not

   Array[String] SampleName        # Name of the Sample

   Array[Int] Index = range(length(InputReads))


   scatter (idx in Index) {
   
      # If PairedEnd=False, set InputRead2="null"
      if(PairedEnd) {
         call TRIMSEQ.trimsequencesTask as TRIMSEQ_paired {
            input:
               SampleName=SampleName[idx],
               InputRead1=InputReads[idx][0],
               InputRead2=InputReads[idx][1]
         }
      }
   
      if(!PairedEnd) {
         call TRIMSEQ.trimsequencesTask as TRIMSEQ_single {
            input:
               SampleName=SampleName[idx],
               InputRead1=InputReads[idx][0],
               InputRead2="null"
         }
      }
   }
   
   output {
      # Unify outputs from scatter and filter out null entries 
      Array[Array[File]] Outputs = select_all(flatten([TRIMSEQ_paired.Outputs,TRIMSEQ_single.Outputs]))
   }
} 
