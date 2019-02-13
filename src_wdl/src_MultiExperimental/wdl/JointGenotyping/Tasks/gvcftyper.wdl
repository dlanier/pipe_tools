#########################################################################################################

# This WDL script performs GVCFtyper variant caller on a gvcf as part of the joint genotyping workflow

#########################################################################################################

task gvcfTyperTask {

   Array[File] Inputgvcf                # Input GVCF files
   Array[File] InputgvcfIdx             # Input GVCF Indes files

   File Ref                             # Reference Genome
   File RefFai                          # Reference files that are provided as implicit inputs

   File DBSNP                           # DBSNP file
   File DBSNPIdx                        # Index file for the DBSNPs

   String SampleName             # Name of Sample

   String gvcfTyperExtraOptionsString   # String of extra options for gvcftyper, this can be an empty string

   String Sentieon                      # Path to Sentieon
   String SentieonThreads                # No of Threads for the Tool

   String gvcfTyperSoftMemLimit         # Soft memory limit - nice shutdown
   String gvcfTyperHardMemLimit         # Hard memory limit - kill immediately

   File BashPreamble                    # Path to bash script to source before every task
   File BashSharedFunctions             # Bash script with shared functions
   File gvcfTyperScript                 # Path to bash script called within WDL script
   File gvcfTyperEnvProfile             # File containing the environmental profile variables

   String DebugMode                     # Enable or Disable Debug Mode

   command <<<
      source ${BashPreamble}
      /bin/bash ${gvcfTyperScript} \
           -s ${SampleName} \
           -S ${Sentieon} \
           -G ${Ref} \
           -g ${sep=',' Inputgvcf} \
           -D ${DBSNP} \
           -o "'${gvcfTyperExtraOptionsString}'" \
           -e ${gvcfTyperEnvProfile} \
            -F ${BashSharedFunctions} ${DebugMode}
   >>>

   runtime {
      cpu: "${SentieonThreads}"
      s_vmem: "${gvcfTyperSoftMemLimit}"
      h_vmem: "${gvcfTyperHardMemLimit}"
   }

   output {
      File Outputvcf = "${SampleName}.vcf"
      File OutputvcfIdx = "${SampleName}.vcf.idx" 
   }

}

