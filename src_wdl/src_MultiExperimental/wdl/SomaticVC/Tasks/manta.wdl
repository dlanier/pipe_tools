###########################################################################################

##		This WDL script performs tumor/normal Variant Calling  using manta     ##

############################################################################################

task mantaTask {

   File TumorBams                                 # Input Sorted Deduped Tumor Bam
   File TumorBais                                 # Input Sorted Deduped Tumor Bam Index
   File NormalBams                                # Input Sorted Deduped Normal Bam
   File NormalBais                                # Input Sorted Deduped Normal Bam Index

   File Ref                                       # Reference Genome
   File RefFai                                    # Reference Genome index

   String SampleName                              # Name of the Sample
   String MantaAnalysisPath			  # Name of the Manta Analysis Path output

   String Manta                                   # Path to Manta 
   String MantaThreads                            # No of Threads for the Tool

   File BashPreamble                              # Bash script that helps control zombie processes
   File BashSharedFunctions                       # Bash script that contains shared helpful functions
   File MantaScript                               # Path to bash script called within WDL script

   String DebugMode                               # Enable or Disable Debug Mode

   String MantaSoftMemLimit                       # Soft memory limit - nice shutdown
   String MantaHardMemLimit                       # Hard memory limit - kill immediately


   command <<<
        source ${BashPreamble}
        /bin/bash ${MantaScript} -s ${SampleName} -N ${NormalBams} -T ${TumorBams} -g ${Ref} -M ${Manta} -A ${MantaAnalysisPath} -t ${MantaThreads} -F ${BashSharedFunctions} ${DebugMode}
   >>>


   runtime {
      cpu: "${MantaThreads}"
      s_vmem: "${MantaSoftMemLimit}"
      h_vmem: "${MantaHardMemLimit}"
   }


   output {
      Array[File] OutputVcf = glob("*.vcf.gz")
      Array[File] OutputVcfTbi = glob("*.vcf.gz.tbi")
   }

}

