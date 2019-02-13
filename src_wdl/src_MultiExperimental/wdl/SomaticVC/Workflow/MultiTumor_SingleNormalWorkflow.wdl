#########################################################################################################################
####              This WDL script is used to run Alignment and HaplotyperVC blocks together  on Multiple Tumor Samples ##
#########################################################################################################################

import "MayomicsVC/src/wdl/SomaticVC/Tasks/Runtrim_sequences.wdl" as CUTADAPTTRIM
import "MayomicsVC/src/wdl/SomaticVC/Tasks/Runalignment.wdl" as ALIGNMENT
import "MayomicsVC/src/wdl/SomaticVC/Tasks/Testdedup.wdl" as DEDUP
import "MayomicsVC/src/wdl/SomaticVC/Tasks/Testrealignment.wdl" as REALIGNMENT

workflow MultiTumorSampleWF {

   Array[Array[File]] MultiTumorInputReads
   Array[Array[File]] NormalInputReads
   Array[String] SampleNameTumor
   Array[String] SampleNameNormal


   ######     Alignment subworkflow for Mutliple Tumor samples      ######
   #######################################################################

   call CUTADAPTTRIM.RunTrimSequencesTask as TumorTrimseq {
      input:
         SampleName = SampleNameTumor,
         InputReads = MultiTumorInputReads
   }

   call ALIGNMENT.RunAlignmentTask as TumorAlign {
      input:
         SampleName = SampleNameTumor,
         InputReads = TumorTrimseq.Outputs
   }  

   call DEDUP.CalldedupTask as TumorDedup {
      input:
         SampleName = SampleNameTumor,
         InputBams = TumorAlign.OutputBams,
         InputBais = TumorAlign.OutputBais
   }

   call REALIGNMENT.CallRealignmentTask  as TumorRealign {
      input:
        SampleName = SampleNameTumor,
        InputBams = TumorDedup.OutputBams,
        InputBais = TumorDedup.OutputBais
   }



   ######         Alignment subworkflow for Normal sample           ######
   #######################################################################
 
   call CUTADAPTTRIM.RunTrimSequencesTask as NormalTrimseq {
      input:
         SampleName = SampleNameNormal,
         InputReads = NormalInputReads
   }

   call ALIGNMENT.RunAlignmentTask as NormalAlign {
      input:
         SampleName = SampleNameNormal,
         InputReads = NormalTrimseq.Outputs
   }

   call DEDUP.CalldedupTask as NormalDedup {
      input:
         SampleName = SampleNameNormal,
         InputBams = NormalAlign.OutputBams,
         InputBais = NormalAlign.OutputBais
   }

   call REALIGNMENT.CallRealignmentTask  as NormalRealign {
      input:
         SampleName = SampleNameNormal,
         InputBams = NormalDedup.OutputBams,
         InputBais = NormalDedup.OutputBais
   }


}


