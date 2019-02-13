#!/bin/bash

#-------------------------------------------------------------------------------------------------------------------------------
## manta.sh MANIFEST, USAGE DOCS, SET CHECKS
#-------------------------------------------------------------------------------------------------------------------------------
read -r -d '' MANIFEST << MANIFEST

*****************************************************************************
`readlink -m $0`
called by: `whoami` on `date`
command line input: ${@}
*****************************************************************************

MANIFEST
echo -e "\n${MANIFEST}"

read -r -d '' DOCS << DOCS

#############################################################################
#
# Script to run Manta on a normal and tumor bam file
# 
#############################################################################
 USAGE:
 manta.sh        
                   -s           <sample_name>
      		   -N           <normal_bam> 
                   -T           <tumor_bam>
                   -g           <reference_genome_fasta>
                   -M           <MantaSV_install_path>
####################                   -A           <Manta_Analysis_Path>
                   -t		<Number of threads>
		   -F           <shared_functions>
                   -d           Turn on debug mode
                   -h           Display this usage/help text(No arg)
                   
EXAMPLES:
manta.sh -h
strelka.sh -N normal.fastq -T tumor.fastq -g reference_genome.fasta -I /path/to/strelka/install -M /path/to/manta/install -B /path/to/BCFTools -S /path/to/samtools -Z /path/to/bgzip -e /path/to/envprofile.file -F /path/to/MayomicsVC/shared_functions.sh -i /path/to/fix_indels.pl -p /path/to/fix_snps.pl -o "'--extra_option'" -O "'extra_bcf_options'"

NOTES: 

#############################################################################


DOCS

set -o errexit
set -o pipefail
set -o nounset

SCRIPT_NAME=manta.sh
SGE_JOB_ID=TBD  # placeholder until we parse job ID
SGE_TASK_ID=TBD  # placeholder until we parse task ID

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------



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






#-------------------------------------------------------------------------------------------------------------------------------
## GETOPTS ARGUMENT PARSER
#------------------------------------------------------------------------------------------------------------------------------
## Check if no arguments were passed
if (($# == 0))
then
        echo -e "\nNo arguments passed.\n\n${DOCS}\n"
        exit 1
fi

## Input and Output parameters
while getopts ":hs:N:T:g:M:t:F:d" OPT
do
        case ${OPT} in
                h )  # Flag to dispay help message
                        echo -e "\n${DOCS}\n"
                        exit 0
                        ;;
		s )  # Sample name
                        SAMPLE=${OPTARG}
                        checkArg
                        ;;
	        N )  # Normal sample BAM
                        NORMAL=${OPTARG}
                        checkArg
                        ;;
                T )  # Tumor sample BAM
                        TUMOR=${OPTARG}
                        checkArg
                        ;;
                g )  # Full path to reference genome fasta file
                        REFGEN=${OPTARG}
                        checkArg
                        ;;
                M )  # MantaSV install path
                        MANTA=${OPTARG}
                        checkArg
                        ;;
#                A )  # Manta Analysis Path
#                        MANTA_ANALYSIS_PATH=${OPTARG}
#                        checkArg
#                        ;;
	        t )  # Number of threads
                        THR=${OPTARG}
                        checkArg
                        ;;
		F )  # Shared functions 
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

#---------------------------------------------------------------------------------------------------------------------------



#---------------------------------------------------------------------------------------------------------------------------
## PRECHECK FOR INPUTS AND OPTIONS 
#---------------------------------------------------------------------------------------------------------------------------

source "${SHARED_FUNCTIONS}"

## Check if Sample Name variable exists
checkVar "${SAMPLE+x}" "Missing sample name option: -s" $LINENO

## Create log for JOB_ID/script and tool
ERRLOG=${SAMPLE}.manta_variant_calling.${SGE_JOB_ID}.log
truncate -s 0 "${ERRLOG}"
TOOL_LOG=${SAMPLE}.manta.log
truncate -s 0 ${TOOL_LOG}

## Send manifest to log
echo "${MANIFEST}" >> "${ERRLOG}"

## source the file with environmental profile variables
#checkVar "${ENV_PROFILE+x}" "Missing environmental profile option: -e" $LINENO
#source ${ENV_PROFILE}


## Check if input files, directories, and variables are non-zero
checkVar "${NORMAL+x}" "Missing normal BAM option: -B" $LINENO
checkFile ${NORMAL} "Input normal BAM file ${NORMAL} is empty or does not exist." $LINENO

checkVar "${TUMOR+x}" "Missing tumor BAM option: -T" $LINENO
checkFile ${TUMOR} "Input tumor BAM file ${TUMOR} is empty or does not exist." $LINENO

checkVar "${REFGEN+x}" "Missing reference genome option: -g" $LINENO
checkFile ${REFGEN} "Input tumor BAM file ${REFGEN} is empty or does not exist." $LINENO

checkVar "${MANTA+x}" "Missing MantaSV install directory option: -M" $LINENO
checkDir ${MANTA} "Reason= directory ${MANTA} is not a directory or does not exist." $LINENO

#checkVar "${MANTA_ANALYSIS_PATH+x}" "Missing MantaSV install directory option: -A" $LINENO
#checkDir ${MANTA_ANALYSIS_PATH} "Reason= directory ${MANTA_ANALYSIS_PATH} is not a directory or does not exist." $LINENO

checkVar "${THR+x}" "Missing number of threads option: -t" $LINENO

checkVar "${SHARED_FUNCTIONS+x}" "Missing shared functions option: -F" $LINENO
checkFile ${SHARED_FUNCTIONS} "Shared functions file ${SHARED_FUNCTIONS} is empty or does not exist." $LINENO

#--------------------------------------------------------------------------------------------------------------------------------------------------

## Parsing extra options string
#STRELKA_OPTIONS_PARSED=`sed -e "s/'//g" <<< ${STRELKA_OPTIONS}`
#BCFTOOLS_OPTIONS_PARSED=`sed -e "s/'//g" <<< ${BCFTOOLS_OPTIONS}`



#--------------------------------------------------------------------------------------------------------------------------------------------------
## Perform Manta variant calling
#--------------------------------------------------------------------------------------------------------------------------------------------------
## Record start time
logInfo "[Manta] START."


## Configure MantaSV
TRAP_LINE=$(($LINENO+1))
trap 'logError " $0 stopped at line ${TRAP_LINE}. Error in configuring MantaSV. " ' INT TERM EXIT
${MANTA}/bin/configManta.py \
        --normalBam ${NORMAL} \
        --tumorBam ${TUMOR} \
        --referenceFasta ${REFGEN} \
        --runDir=./manta \

EXITCODE=$?
trap - INT TERM EXIT

checkExitcode ${EXITCODE} $LINENO

## Run MantaSV
TRAP_LINE=$(($LINENO+1))
trap 'logError " $0 stopped at line ${TRAP_LINE}. Error in execution of runWorkflow.py. " ' INT TERM EXIT
./manta/runWorkflow.py -m local -j ${THR}

EXITCODE=$?
trap - INT TERM EXIT

checkExitcode ${EXITCODE} $LINENO

#checkFile ./strelka/results/variants/somatic.indels.vcf.gz "Output somatic indels file failed to create." $LINENO
#checkFile ./strelka/results/variants/somatic.snvs.vcf.gz "Output somatic SNV file failed to create." $LINENO

#----------------------------------------------------------------------------------------------------------------------------------------------

logInfo "Manta workflow completed."

#----------------------------------------------------------------------------------------------------------------------------------------------

                                                                                    
