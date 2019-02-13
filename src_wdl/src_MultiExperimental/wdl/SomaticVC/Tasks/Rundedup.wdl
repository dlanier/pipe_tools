#########################################################################

#       This WDL script calls the Marking Duplicates WDL Task     ##

#########################################################################

import "MayomicsVC/src/wdl/Alignment/Tasks/dedup.wdl" as DEDUP

workflow CalldedupTask {

   Array[File] InputBams          # Array of Aligned Bams
   Array[File] InputBais     
   
   Array[String] SampleName       # Name of Sample

   Array[Int] Index = range(length(InputBams))

   scatter (idx in Index) {
   
      call DEDUP.dedupTask as DEDUP_MultiSample {
         input:
            SampleName = SampleName[idx],
            InputBams = InputBams[idx],
            InputBais = InputBais[idx]
   
      }
   
   }

   output {
      
      Array[File] OutputBams = DEDUP_MultiSample.OutputBams
      Array[File] OutputBais = DEDUP_MultiSample.OutputBais
   }
}

