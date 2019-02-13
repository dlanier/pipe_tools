#########################################################################################################
####              This WDL script is used to run the  steps as individual modules              ##
#########################################################################################################

import "MayomicsVC/src/wdl/JointGenotyping/Tasks/gvcftyper.wdl" as GVCFTYPER
import "MayomicsVC/src/wdl/HaplotyperVC/Tasks/vqsr.wdl" as VQSR
import "MayomicsVC/src/wdl/JointGenotyping/Tasks/phasing.wdl" as PHASING 

workflow CallJointGenotypingTasks {


   call GVCFTYPER.gvcfTyperTask as GVCFTASK 

   call VQSR.vqsrTask as VQSRTASK {
      input:
         InputVcf = GVCFTASK.Outputvcf,
         InputVcfIdx = GVCFTASK.OutputvcfIdx
   }

   call PHASING.phasingTask as PHASINGTASK {
      input:
         Inputvcf = VQSRTASK.OutputVcf,
         InputVcfIdx = VQSRTASK.OutputVcfIdx
   }

}

   
