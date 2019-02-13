#########################################################################################################

# this WDL script is used for phasing genotypes and for imputing ungenotyped markers

#########################################################################################################

task phasingTask {

   File Inputvcf                         # Input VCF File
   File InputVcfIdx                      # Input VCF Index

   String SampleName                     # Name of Sample
   
   String phasingExtraOptionsString      # String of extra options for gvcftyper, this can be an empty string 

   
   File BashPreamble                     # Path to bash script to source before every task
   File BashSharedFunctions              # Bash script with shared functions
   File phasingScript                    # Path to bash script called within WDL script
   File phasingEnvProfile                # File containing the environmental profile variables

   File Beagle                           # Path to Beagle Tool
 
   String Sentieon                       # Path to Sentieon
   String SentieonThreads                # No of Threads for the Tool
   String Java
   String phasingSoftMemLimit            # Soft memory limit - nice shutdown
   String phasingHardMemLimit            # Hard memory limit - kill immediately

   String phasingJavaMemOptions          # Setting memory option for Java               
   
   String DebugMode                      # Enable or Disable Debug Mode

   command <<<
      source ${BashPreamble}
      /bin/bash ${phasingScript} -s ${SampleName} -S ${Sentieon} -i ${Inputvcf} -B ${Beagle} -J ${Java} -j "'${phasingJavaMemOptions}'" -o "'${phasingExtraOptionsString}'" -e ${phasingEnvProfile} -F ${BashSharedFunctions} ${DebugMode}
   >>>

   runtime {
      cpu: "${SentieonThreads}"
      s_vmem: "${phasingSoftMemLimit}"
      h_vmem: "${phasingHardMemLimit}"
   }

   output {
      File OutputVcf = "${SampleName}.vcf.gz"
      File OutputVcfIdx = "${SampleName}.vcf.gz.tbi"
      File phasingLog  = "${SampleName}.log"
   }
}
