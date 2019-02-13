##########################################################################                                                          
#       This WDL script calls the Manta WDL Task                      	##
##########################################################################

import "MayomicsVC/src/wdl/SomaticVC/Tasks/manta.wdl" as MANTA

workflow CallMantaTask {

   call MANTA.mantaTask as manta

  output {
      File OutputCandidateSmallIndelsVcfGz = manta.OutputCandidateSmallIndelsVcfGz
      File OutputCandidateSmallIndelsVcfGzTbi = manta.OutputCandidateSmallIndelsVcfGzTbi
      File OutputCandidateSVVcfGz = manta.OutputCandidateSVVcfGz
      File OutputCandidateSVVcfGzTbi = manta.OutputCandidateSVVcfGzTbi
      File OutputDiploidSVVcfGz = manta.OutputDiploidSVVcfGz
      File OutputDiploidSVVcfGzTbi = manta.OutputDiploidSVVcfGzTbi
      File OutputsomaticSVVcfGz = manta.OutputsomaticSVVcfGz
      File OutputsomaticSVVcfGzTbi = manta.OutputsomaticSVVcfGz
   }

}

