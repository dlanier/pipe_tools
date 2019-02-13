#############################################################

###       This WDL script calls the VQSR WDL Task       ##

##############################################################

import "MayomicsVC/src/wdl/JointGenotyping/Tasks/vqsr.wdl" as VQSR

workflow CallvqsrTask {

   call VQSR.vqsrTask

}
