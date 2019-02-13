#############################################################

###       This WDL script calls the Phasing WDL Task       ##

##############################################################

import "MayomicsVC/src/wdl/JointGenotyping/Tasks/phasing.wdl" as PHASING

workflow CallphasingTask {

   call PHASING.phasingTask

}
