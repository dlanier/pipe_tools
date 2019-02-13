##########################################################################################################
####              This WDL script is used to run the Alignment steps as individual modules              ##
##########################################################################################################

import "MayomicsVC/src/wdl/Alignment/Workflow/Runtrim_sequences.wdl" as CUTADAPTTRIM
import "MayomicsVC/src/wdl/Alignment/Workflow/Runalignment.wdl" as ALIGNMENT
import "MayomicsVC/src/wdl/Alignment/Tasks/dedup.wdl" as DEDUP 
import "MayomicsVC/src/wdl/Alignment/Tasks/merge_aligned_bam.wdl" as MERGE

workflow CallAlignmentTasks {
   
   Boolean Trimming
   Boolean MarkDuplicates

   if(Trimming) {

      call CUTADAPTTRIM.RunTrimSequencesTask as trimseq
       
      call ALIGNMENT.RunAlignmentTask as align_w_trim {
         input:
            InputReads = trimseq.Outputs
      }
   }

   if(!Trimming) {
      
      call ALIGNMENT.RunAlignmentTask as align_wo_trim
   }
   
   Array[File] AlignOutputBams = select_first([align_w_trim.OutputBams,align_wo_trim.OutputBams])
   Array[File] AlignOutputBais = select_first([align_w_trim.OutputBais,align_wo_trim.OutputBais])


   call MERGE.mergebamTask as merge {
      input:
         InputBams = AlignOutputBams,
         InputBais = AlignOutputBais
   }

   if(MarkDuplicates) {
   
      call DEDUP.dedupTask as dedup {
         input:
            InputBams = merge.OutputBams,
            InputBais = merge.OutputBais
      }
   }

   output {
     
      File OutputBams = select_first([dedup.OutputBams,merge.OutputBams])
      File OutputBais = select_first([dedup.OutputBais,merge.OutputBais])
   }    
    
}
