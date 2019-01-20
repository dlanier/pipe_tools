#!/bin/bash

# Usage:
# bash AutoGermlineMaster.sh . src/wdl/GermlineMasterWorkflow.wdl "-i Config/run_info.txt -i Config/tool_info.txt -i Config/memory_info.txt -i Config/sample_info.txt"

set -x
set -o errexit
set -o pipefail
set -o nounset

#			Path to test folder
TestingMayomics=$1

#			Stage of workflow being tested (is a) .wdl file
WorkflowBeingTested=$2;
BaseNameOfWorkflowBeingTested=`basename ${WorkflowBeingTested} .wdl`

#			Config files to use in this test in format "-i /fullpath/config1.txt -i /fullpath/config2.txt -i /...
ConfigsBeingUsed=$3;

if [[ "$(ls -A ./Delivery)" ]]; then
	rm -r ./Delivery/*
fi

#			Change to test directory, load modules		(Red Hat)
cd ${TestingMayomics};
source /etc/profile.d/modules.sh
module load /usr/local/apps/bioapps/modules/cromwell/cromwell-34;
module load python/python-3.6.1;

# 			check JSON template against the workflow	(java)
cd "./"; 
java -jar ${WOMTOOL} inputs ../${WorkflowBeingTested} > ../Jsons/${BaseNameOfWorkflowBeingTested}.template.json;
cd ../;

echo ${ConfigsBeingUsed}

# 			Fill In the JSON template			(python)
python src/python/config_parser.py ${ConfigsBeingUsed} --jsonTemplate Jsons/${BaseNameOfWorkflowBeingTested}.template.json -o Jsons/${BaseNameOfWorkflowBeingTested}.FilledIn.json;

#			Validate FilledIn JSON key file			(pyton)
python src/python/key_validator.py -i Jsons/${BaseNameOfWorkflowBeingTested}.FilledIn.json --KeyTypeFile key_types.json;

#			Zip the code repository for cromwell		(linux)
cd MayomicsVC ; 
zip -r MayomicsVC.zip ./ ;
mv MayomicsVC.zip ../ ;
cd ../ ;

#			Run the workflow with WDL and .json file	(java - cromwell)
java -jar ${CROMWELL} run ${WorkflowBeingTested} -i Jsons/${BaseNameOfWorkflowBeingTested}.FilledIn.json -p MayomicsVC.zip ;

