###############################################################################################
####              This WDL script is used to run Alignment and HaplotyperVC blocks together  ##
###############################################################################################

import "MayomicsVC/src/wdl/Alignment/Workflow/Runtrim_sequences.wdl" as CUTADAPTTRIM
import "MayomicsVC/src/wdl/Alignment/Workflow/Runalignment.wdl" as ALIGNMENT
import "MayomicsVC/src/wdl/Alignment/Tasks/merge_aligned_bam.wdl" as MERGEBAM
import "MayomicsVC/src/wdl/Alignment/Tasks/dedup.wdl" as DEDUP

import "MayomicsVC/src/wdl/DeliveryOfAlignment/Tasks/deliver_alignment.wdl" as DELIVER_Alignment

import "MayomicsVC/src/wdl/HaplotyperVC/Tasks/realignment.wdl" as REALIGNMENT
import "MayomicsVC/src/wdl/HaplotyperVC/Tasks/bqsr.wdl" as BQSR
import "MayomicsVC/src/wdl/HaplotyperVC/Tasks/haplotyper.wdl" as HAPLOTYPER
import "MayomicsVC/src/wdl/HaplotyperVC/Tasks/vqsr.wdl" as VQSR

import "MayomicsVC/src/wdl/DeliveryOfHaplotyperVC/Tasks/deliver_HaplotyperVC.wdl" as DELIVER_HaplotyperVC


workflow GermlineMasterWF {

   Array[Array[File]] NormalInputReads

   Boolean Trimming
   Boolean MarkDuplicates
   Boolean Bqsr
   Boolean Vqsr

   if(Trimming) {

      call CUTADAPTTRIM.RunTrimSequencesTask as trimseq {
         input:
            InputReads = NormalInputReads
      }
   }
   
   Array[Array[File]] AlignInputReads = select_first([trimseq.Outputs,NormalInputReads])


   call ALIGNMENT.RunAlignmentTask as align {
      input:
         InputReads = AlignInputReads
   }

   call MERGEBAM.mergebamTask as merge {
      input:
         InputBams = align.OutputBams,
         InputBais = align.OutputBais
   }

   if(MarkDuplicates) {
   
      call DEDUP.dedupTask as dedup {
         input:
            InputBams = merge.OutputBams,
            InputBais = merge.OutputBais
      }
   }

   File DeliverAlignOutputBams = select_first([dedup.OutputBams,merge.OutputBams])
   File DeliverAlignOutputBais = select_first([dedup.OutputBais,merge.OutputBais])


   call DELIVER_Alignment.deliverAlignmentTask as DAB {
      input:
         InputBams = DeliverAlignOutputBams,
         InputBais = DeliverAlignOutputBais
   }



   call REALIGNMENT.realignmentTask  as realign {
      input:
         InputBams = DeliverAlignOutputBams,
         InputBais = DeliverAlignOutputBais
   }


   if(Bqsr) {

      call BQSR.bqsrTask as bqsr {
         input:
            InputBams = realign.OutputBams,
            InputBais = realign.OutputBais
      }
   }

   call HAPLOTYPER.variantCallingTask as haplotype {
      input:
         InputBams = realign.OutputBams,
         InputBais = realign.OutputBais,
         RecalTable = bqsr.RecalTable
   }

   if(Vqsr) {
      call VQSR.vqsrTask as vqsr {
         input:
            InputVcf = haplotype.OutputVcf,
            InputVcfIdx = haplotype.OutputVcfIdx
      }
   }

   File DeliverHaplotyperVcf = select_first([vqsr.OutputVcf,haplotype.OutputVcf])
   File DeliverHaplotyperVcfIdx = select_first([vqsr.OutputVcfIdx,haplotype.OutputVcfIdx])


   call DELIVER_HaplotyperVC.deliverHaplotyperVCTask as DHVC {
      input:
         InputVcf = DeliverHaplotyperVcf,
         InputVcfIdx = DeliverHaplotyperVcfIdx
   } 

}
