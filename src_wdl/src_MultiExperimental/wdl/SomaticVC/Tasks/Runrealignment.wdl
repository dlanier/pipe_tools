#########################################################################################################

###                This WDL script is performs Realignment on Input sorted Deduped BAM                 ##

#########################################################################################################

import "MayomicsVC/src/wdl/HaplotyperVC/Tasks/realignment.wdl" as REALIGN

workflow CallRealignmentTask {

   Array[File] InputBams          # Array of Aligned Bams
   Array[File] InputBais     

   Array[String] SampleName       # Name of Sample

   Array[Int] Index = range(length(InputBams))

   scatter (idx in Index) {

      call REALIGN.realignmentTask as REALIGN_MultiSample {
         input:
            SampleName = SampleName[idx],
            InputBams = InputBams[idx],
            InputBais = InputBais[idx]

      }

   }

   output {
     
      Array[File] OutputBams = REALIGN_MultiSample.OutputBams
      Array[File] OutputBais = REALIGN_MultiSample.OutputBais
   }
}
