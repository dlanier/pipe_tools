######################################################################

###       This WDL script calls the gvcfTyper WDL Task       ##

#######################################################################

import "MayomicsVC/src/wdl/JointGenotyping/Tasks/gvcftyper.wdl" as GVCFTYPER

workflow CallgvcfTyperTask {

   call GVCFTYPER.gvcfTyperTask as GVCF 

}
