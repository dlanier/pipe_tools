#########################################################################

#       This WDL script calls the Marking Duplicates WDL Task     ##

#########################################################################

import "MayomicsVC/src/wdl/Alignment/Tasks/alignment.wdl" as ALIGNMENT

workflow CallalignmentTask {

   call ALIGNMENT.alignmentTask

}

