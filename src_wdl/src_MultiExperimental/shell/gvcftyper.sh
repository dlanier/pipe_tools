#!/bin/bash

#------------------------------------------------------------------------------------------------------------------------------
## gvcftyper.sh MANIFEST, USAGE DOCS, SET CHECKS
#------------------------------------------------------------------------------------------------------------------------------



read -r -d '' MANIFEST << MANIFEST
*******************************************
`readlink -m $0`
called by: `whoami` on `date`
command line input: ${@}
*******************************************
MANIFEST
echo -e "\n${MANIFEST}"






read -r -d '' DOCS << DOCS


#######################################################################################################################################################
#
# Perform Sentieon's GVCFtyper variant caller on a gvcf as part of the joint genotyping workflow.
# The Germline workflow must be run up to haplotyper.sh before this stage, with extra option --emit_mode gvcf for hapltoyper.
# Step 2/4 of the joint genotyping process.
#
########################################################################################################################################################

 USAGE:
 gvcftyper.sh       -s 	<sample_name>
                    -S	</path/to/sentieon>
                    -G	<reference_genome>
                    -g	<sample_1.g.vcf[,sample_2.g.vcf,...]>
                    -D	<dbsnp.vcf>
                    -o	<extra_gvcftyper_options>
                    -e   </path/to/env_profile_file>
                    -V   VCF Source Field (default: Sentieon)
                    -F   </path/to/shared_functions.sh>
                    -d   turn on debug mode

 EXAMPLES:
 gvcftyper.sh -h
 gvcftyper.sh -s sample -S /path/to/sentieon_directory -G reference.fa -g sample_1.g.vcf,sample_2.g.vcf,sample_3.g.vcf -D dbsnp.vcf -o "'--call_conf 30 --emit_conf 30 --emit_mode variant --max_alt_alleles 100'" -e /path/to/env_profile_file -F </path/to/shared_functions.sh> -d

NOTE: In order for getops to read in a string arguments for -o (extra_gvcftyper_options), the argument needs to be quoted with a double quote (") followed by a single quote ('). See the example above.
##########################################################################################################################################################


DOCS

set -o errexit
set -o pipefail
set -o nounset

SCRIPT_NAME=gvcfyper.sh
SGE_JOB_ID=TBD  # placeholder until we parse job ID
SGE_TASK_ID=TBD  # placeholder until we parse task ID
SOURCE_FIELD="Sentieon"



#-------------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------------
## LOGGING FUNCTIONS
#-------------------------------------------------------------------------------------------------------------------------------

function checkArg()
{
    if [[ "${OPTARG}" == -* ]]; then
        echo -e "\nError with option -${OPT} in command. Option passed incorrectly or without argument.\n"
        echo -e "\n${DOCS}\n"
        exit 1;
    fi
}




#--------------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------------
## GETOPS ARGUMENT PARSER
#--------------------------------------------------------------------------------------------------------------------------------

## Check if no arguments were passed
if (($# == 0))
then
        echo -e "\nNo arguments passed.\n\n${DOCS}\n"
        exit 1
fi

while getopts ":hs:S:G:g:D:o:e:F:dV:" OPT
do
	case ${OPT} in
		h ) # flag to display help message
			echo -e "\n${DOCS}\n "
			exit 0;
			;;
		s ) # Sample name
			SAMPLE=${OPTARG}
			checkArg
			;;
		S ) # Full path to Sentieon directory
			SENTIEON=${OPTARG}
			checkArg
			;;
		G ) # Full path to reference genome fasta file
			REF=${OPTARG}
			checkArg
			;;
		g ) # Full path to GVCF used as input
			INPUTGVCF=${OPTARG}
			checkArg
			;;
		D ) # Full path to DBSNP file
			DBSNP=${OPTARG}
			checkArg
			;;
		o ) #Extra options and arguments to GVCFtyper, input as a long string, can be empty if desired
			GVCFTYPER_OPTIONS=${OPTARG}
			checkArg
			;;
        e )  # Path to file with environmental profile variables
            ENV_PROFILE=${OPTARG}
            checkArg
            ;;
		F ) # Path to shared_functions.sh
			SHARED_FUNCTIONS=${OPTARG}
			checkArg
			;;
		d ) # Turn on debug mode. Turn on debug mode. Initiates 'set -x' to print all text. Invoked with -d
			echo -e "\nDebug mode is ON.\n"
			set -x
			;;
		V ) # Set the source field overriding 'Sentieon'
	        SOURCE_FIELD=${OPTARG}
	        ;;
		\? )  # Check for unsupported flag, print usage and exit.
            echo -e "\nInvalid option: -${OPTARG}\n\n${DOCS}\n"
            exit 1
            ;;
        : )  # Check for missing arguments, print usage and exit.
            echo -e "\nOption -${OPTARG} requires an argument.\n\n${DOCS}\n"
            exit 1
            ;;

	esac
done
#---------------------------------------------------------------------------------------------------------------------------






#---------------------------------------------------------------------------------------------------------------------------
## PRECHECK FOR INPUTS AND OPTIONS
#---------------------------------------------------------------------------------------------------------------------------


source ${SHARED_FUNCTIONS}


## Check if sample name is set
checkVar "${SAMPLE+x}" "Missing sample name option: -s" $LINENO

## Send Manifest to log
ERRLOG=${SAMPLE}.GVCFtyper.${SGE_JOB_ID}.log
truncate -s 0 "${ERRLOG}"
truncate -s 0 ${SAMPLE}.gvcftyper_sentieon.log

echo "${MANIFEST}" >> "${ERRLOG}"

## source the file with environmental profile variables
checkVar "${ENV_PROFILE+x}" "Missing environmental profile option: -e" $LINENO
source ${ENV_PROFILE}

checkVar "${SENTIEON+x}" "Missing Sentieon path option: -S" $LINENO
checkDir ${SENTIEON} "REASON=Sentieon directory ${SENTIEON} is not a directory or does not exist." $LINENO

checkVar "${REF+x}" "Missing reference genome option: -G" $LINENO
checkFile ${REF} "Reference genome file ${REF} is empty or does not exist." $LINENO

checkVar "${INPUTGVCF+x}" "Missing input GVCF option: -g" $LINENO
for GVCF in $(echo ${INPUTGVCF} | sed "s/,/ /g")
do
        checkFile ${GVCF} "Input GVCF file ${GVCF} is empty or does not exist." $LINENO
done

checkVar "${DBSNP+x}" "Missing dbSNP option: -D" $LINENO
checkFile ${DBSNP} "DBSNP ${DBSNP} is empty or does not exist." $LINENO


checkVar "${GVCFTYPER_OPTIONS+x}" "Missing extra GVCFtyper options option: -o" $LINENO


#--------------------------------------------------------------------------------------------------------------------------------------------------
GVCFTYPER_OPTIONS_PARSED=`sed -e "s/'//g" <<< ${GVCFTYPER_OPTIONS}`



#-------------------------------------------------------------------------------------------------------------------------------
## FILENAME PARSING
#-------------------------------------------------------------------------------------------------------------------------------

## Defining file names
GVCFS=`sed -e 's/,/ -v /g' <<< ${INPUTGVCF}`  ## Replace commas with spaces and -v






#--------------------------------------------------------------------------------------------------------------------------------------------------
## Perform GVCFTyper with Sentieon.
#--------------------------------------------------------------------------------------------------------------------------------------------------


## Record start time
logInfo "[GVCFTyper] START."


#Execute Sentieon with the GVCFTyper algorithm
TRAP_LINE=$(($LINENO + 1))
trap 'logError " $0 stopped at line ${TRAP_LINE}. Error in Sentieon GVCFTyper. " ' INT TERM EXIT
${SENTIEON}/bin/sentieon driver -r ${REF} --algo GVCFtyper -v ${GVCFS} -d ${DBSNP} ${GVCFTYPER_OPTIONS_PARSED} ${SAMPLE}.vcf >> ${SAMPLE}.gvcftyper_sentieon.log 2>&1
EXITCODE=$?
trap - INT TERM EXIT


checkExitcode ${EXITCODE} $LINENO
logInfo "[GVCFtyper] Finished running successfully. Output: ${SAMPLE}.vcf"
#------------------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------------
## POST-PROCESSING
#-------------------------------------------------------------------------------------------------------------------------------

## Inject Source Field into VCF Header (2nd row) and reindex

rm -f ${SAMPLE}.vcf.idx
TRAP_LINE=$(($LINENO + 1))
trap 'logError " $0 stopped at line ${TRAP_LINE}. Error in Sentieon GVCFtyper (vcfindex). " ' INT TERM EXIT
sed -i "2i##source=${SOURCE_FIELD}" ${SAMPLE}.vcf
${SENTIEON}/bin/sentieon util vcfindex ${SAMPLE}.vcf 2>&1
EXITCODE=$?
trap - INT TERM EXIT

## Check for the creation of the output VCF file
checkFile ${SAMPLE}.vcf "Output VCF is empty." $LINENO

## Open read permissions to the user group
chmod g+r ${SAMPLE}.vcf

## Check for the creation of the output VCF index file
checkFile ${SAMPLE}.vcf.idx "Output VCF index is empty." $LINENO

## Open read permissions to the user group
chmod g+r ${SAMPLE}.vcf.idx


#-------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------
## END
#-------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------
exit 0;
