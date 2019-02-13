#########################################################################                                                          
#       This WDL script calls the Strelka WDL Task                     ##

#########################################################################
import "MayomicsVC/src/wdl/SomaticVC/Tasks/strelka.wdl" as STRELKA

workflow CallStrelkaTask {

   Array[File] MutectVcfBgz
   Array[File] MutectVcfBgzTbi

   Array[String] SampleName       # Name of Sample

   Array[Int] Index = range(length(InputBams))

   scatter (idx in Index) {

      call STRELKA.strelkaTask as Strelka_MultiSample {
         input:
             SampleName = SampleName[idx],
             MutectVcfBgz = MutectVcfBgz[idx]
             MutectVcfBgz = MutectVcfBgz[idx]
      }

   }

   output {
      File StrelkaVcfBgz = strelka.OutputVcfBgz
      File StrelkaVcfBgzTbi = strelka.OutputVcfBgzTbi
   }

}
