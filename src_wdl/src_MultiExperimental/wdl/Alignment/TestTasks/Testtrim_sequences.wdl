#########################################################################

#       This WDL script calls the Marking Duplicates WDL Task     ##

#########################################################################

import "MayomicsVC/src/wdl/Alignment/Tasks/trim_sequences.wdl" as TRIMMING

workflow CalltrimTask {

   call TRIMMING.trimTask

}

