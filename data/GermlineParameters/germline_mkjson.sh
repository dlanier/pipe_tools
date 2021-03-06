#!/bin/bash

#bash germline_mkjson.sh . MayomicsVC/src/wdl/GermlineMasterWorkflow.wdl "-i Config/sample_info.txt -i Config/tool_info.txt -i Config/run_info.txt -i Config/memory_info.txt"
# also in there have folders Config/, Jsons/, Inputs/ - although it is also a good practice  to keep all input data in one central place, not in test folder
# Let's name that workspace ${TestingMayomics}
# TestingMayomics="/projects/mgc/Project_1/LSM/CleaningUpWDLtails/Multilane/"
# Folder that includes hg38 simurlated data: /projects/bioinformatics/DataPacks/human/Hg38_chr20_21_22_simulated_data_Jan_2018/fastqs/

set -x
set -o errexit
set -o pipefail
set -o nounset

#Define the path to test folder
TestingMayomics=$1

#define which stage of the workflow is being tested: is a .wdl file
WorkflowBeingTested=$2;
BaseNameOfWorkflowBeingTested=`basename ${WorkflowBeingTested} .wdl`

#define which config files to use in this test
#should be in format "-i /full/path/to/config1.txt -i /full/path/to/config2.txt -i /full/path/to/config3.txt etc..."
ConfigsBeingUsed=$3;

if [[ "$(ls -A ./Delivery)" ]]; then
	rm -r ./Delivery/*
fi

cd ${TestingMayomics};

source /etc/profile.d/modules.sh
module load /usr/local/apps/bioapps/modules/cromwell/cromwell-34;
module load python/python-3.6.1;

# create JSON template
#cd "./MayomicsVC/"; 
java -jar ${WOMTOOL} inputs ${WorkflowBeingTested} > Jsons/${BaseNameOfWorkflowBeingTested}.template.json;
#cd ../;

#populate the JSON template
python MayomicsVC/src/python/config_parser.py ${ConfigsBeingUsed} --jsonTemplate Jsons/${BaseNameOfWorkflowBeingTested}.template.json -o Jsons/${BaseNameOfWorkflowBeingTested}.FilledIn.json;

#validate the JSON template
python MayomicsVC/src/python/key_validator.py -i Jsons/${BaseNameOfWorkflowBeingTested}.FilledIn.json --KeyTypeFile MayomicsVC/key_types.json;

#cd MayomicsVC ; 
#zip -r MayomicsVC.zip ./ ;
#mv MayomicsVC.zip ../ ;
#cd ../ ;

#module unload python/python-3.6.1;
##### RUN THE WORKFLOW #############:
#java -jar ${CROMWELL} run ${WorkflowBeingTested} -i Jsons/${BaseNameOfWorkflowBeingTested}.FilledIn.json -p MayomicsVC.zip ;

