#########################################################################                                                          
#       This WDL script calls the Mutect WDL Task                      ##

#########################################################################

import "MayomicsVC/src/wdl/SomaticVC/Tasks/mutect.wdl" as MUTECT

workflow CallMutectTask {

   call MUTECT.mutectTask as mutect
}

