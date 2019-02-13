#!/bin/bash

#-------------------------------------------------------------------------------------------------------------------------------
## phasing.sh MANIFEST, USAGE DOCS, SET CHECKS
#-------------------------------------------------------------------------------------------------------------------------------

read -r -d '' MANIFEST << MANIFEST

*****************************************************************************
`readlink -m $0`
called by: `whoami` on `date`
command line input: ${@}
*****************************************************************************

MANIFEST
echo -e "${MANIFEST}"








read -r -d '' DOCS << DOCS

#############################################################################
#
# Phasing and imputing missing genotypes Beagle. Part of the MayomicsVC Workflow.
#
#############################################################################

 USAGE:
 phasing.sh  -s     <sample_name>
             -S     </path/to/Sentieon>
             -i   	<Joint_Genotyped_VCF_file>
             -B     </path/to/Beagle_jar>
             -J		<Java_path>
             -j     <Java_memory_options_string>
             -o     <extra_Beagle_options>
             -e     </path/to/env_profile_file>
             -F     </path/to/shared_functions.sh>
             -d     turn on debug mode
             -h     Display this usage/help text(No arg)

 EXAMPLES:
 phasing.sh -h
 phasing.sh -s sample -S /path/to/Sentieon -i joint_genotyped_vcf -B /path/to/Beagle.jar -j "'-Xms2G -Xmx8G'" -o "'Extra options string'" -e /path/to/env_profile_file -F /path/to/shared_functions.sh -d

#############################################################################

DOCS






set -o errexit
set -o pipefail
set -o nounset

SCRIPT_NAME=phasing.sh
SGE_JOB_ID=TBD  # placeholder until we parse job ID
SGE_TASK_ID=TBD  # placeholder until we parse task ID




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






#-------------------------------------------------------------------------------------------------------------------------------
## GETOPTS ARGUMENT PARSER
#-------------------------------------------------------------------------------------------------------------------------------

## Check if no arguments were passed
if (($# == 0))
then
        echo -e "\nNo arguments passed.\n\n${DOCS}\n"
        exit 1
fi

## Input and Output parameters
while getopts ":hs:S:i:B:J:j:o:e:F:d" OPT
do
        case ${OPT} in
                h )  # Flag to display usage
                    echo -e "\n${DOCS}\n"
                    exit 0
                    ;;
                s )  # Sample name
                    SAMPLE=${OPTARG}
                    checkArg
                    ;;
                S ) # path to Sentieon folder
                    SENTIEON=${OPTARG}
                    checkArg
                    ;;
                i )  # Full path to the input BAM
                    INPUTVCF=${OPTARG}
                    checkArg
                    ;;
                B )  # Full path to Beagle jar
                    BEAGLE=${OPTARG}
                    checkArg
                    ;;
                o )  # Extra options for Beagle
                    OPTIONS=${OPTARG}
                    checkArg
                    ;;
                J )  # Java path
                    JAVA=${OPTARG}
                    checkArg
                    ;;
                j )  # java memory options
                    JAVA_MEMORY_OPTIONS=${OPTARG}
                    checkArg
                    ;;
                e )  # Path to file with environmental profile variables
                    ENV_PROFILE=${OPTARG}
                    checkArg
                    ;;
                F )  # Path to shared_functions.sh
                    SHARED_FUNCTIONS=${OPTARG}
                    checkArg
                    ;;
                d )  # Turn on debug mode. Initiates 'set -x' to print all text. Invoked with -d
                    echo -e "\nDebug mode is ON.\n"
			        set -x
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






#-------------------------------------------------------------------------------------------------------------------------------
## PRECHECK FOR INPUTS AND OPTIONS
#-------------------------------------------------------------------------------------------------------------------------------


source ${SHARED_FUNCTIONS}

## Check if Sample Name variable exists
checkVar "${SAMPLE+x}" "Missing sample name option: -s" $LINENO

## Create log for JOB_ID/script
ERRLOG=${SAMPLE}.phasing.${SGE_JOB_ID}.log
truncate -s 0 "${ERRLOG}"
truncate -s 0 ${SAMPLE}.phasing_beagle.log

## Write manifest to log
echo "${MANIFEST}" >> "${ERRLOG}"

## source the file with environmental profile variables
checkVar "${ENV_PROFILE+x}" "Missing environmental profile option: -e" $LINENO
source ${ENV_PROFILE}

## Check if input files, directories, and variables are non-zero
checkVar "${INPUTVCF+x}" "Missing input VCF option: -i" $LINENO
checkFile ${INPUTVCF} "Input joint genotyped VCF file ${INPUTVCF} is empty or does not exist." $LINENO
checkFile ${INPUTVCF}.idx "Input joint genotyped VCF index file ${INPUTVCF}.idx is empty or does not exist." $LINENO

checkVar "${SENTIEON+x}" "Missing Sentieon path option: -S" $LINENO
checkDir ${SENTIEON} "REASON=Sentieon directory ${SENTIEON} is not a directory or does not exist." $LINENO

checkVar "${JAVA+x}" "Missing Java directory option: -J" $LINENO
checkDir ${JAVA} "Reason= Java directory ${JAVA} is not a directory or does not exist." $LINENO

checkVar "${JAVA_MEMORY_OPTIONS+x}" "Missing Java memory option: -j" $LINENO

checkVar "${BEAGLE+x}" "Missing Beagle jar option: -S" $LINENO
checkFile ${BEAGLE} "REASON=Beagle jar file ${BEAGLE} is not a jar file or does not exist." $LINENO
checkVar "${OPTIONS+x}" "Missing extra options option: -o" $LINENO
#------------------------------------------------------------------------------------------------------------------------------
## Extra options
PHASING_OPTIONS_PARSED=`sed -e "s/'//g" <<< ${OPTIONS}`
JAVA_MEMORY_OPTIONS_PARSED=`sed -e "s/'//g" <<< ${JAVA_MEMORY_OPTIONS}`




#-------------------------------------------------------------------------------------------------------------------------------
## FILENAME PARSING
#-------------------------------------------------------------------------------------------------------------------------------

## Defining file names
LOG=${SAMPLE}.log
OUT=${SAMPLE}.vcf.gz





#-------------------------------------------------------------------------------------------------------------------------------
## Phasing
#-------------------------------------------------------------------------------------------------------------------------------

## Record start time
logInfo "[BEAGLE] running analysis on input."

## Dedup command (Note: optional --rmdup flag will remove duplicates; without, duplicates are marked but not removed)
TRAP_LINE=$(($LINENO + 1))
trap 'logError " $0 stopped at line ${TRAP_LINE}. Beagle phasing error. " ' INT TERM EXIT
${JAVA}/java ${JAVA_MEMORY_OPTIONS_PARSED} -jar ${BEAGLE} ${PHASING_OPTIONS_PARSED} gt=${INPUTVCF} out=${SAMPLE} >> ${SAMPLE}.phasing_beagle.log 2>&1
EXITCODE=$?
trap - INT TERM EXIT

checkExitcode ${EXITCODE} $LINENO
logInfo "[BEAGLE] phasing finished. Analyzed VCF found at ${OUT}"






#-------------------------------------------------------------------------------------------------------------------------------
## POST-PROCESSING
#-------------------------------------------------------------------------------------------------------------------------------

## Create an index for the vcf
TRAP_LINE=$(($LINENO + 1))
trap 'logError " $0 stopped at line ${TRAP_LINE}. Error in Beagle Phasing (vcfindex). " ' INT TERM EXIT
${SENTIEON}/bin/sentieon util vcfindex ${OUT} 2>&1
EXITCODE=$?
trap - INT TERM EXIT

## Check for creation of output BAM and index. Open read permissions to the user group
checkFile ${OUT} "Output genotyped VCF file ${OUT} is empty." $LINENO


chmod g+r ${OUT}
chmod g+r ${LOG}




#-------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------
## END
#-------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------
exit 0;
