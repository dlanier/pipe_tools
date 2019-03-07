"""
NCSA Industry Genomics Group
lanier4@illinois.edu

main function for receiving command-line args & calling  womtool_template_fill_in.py

requred args: '-i', '-o', '--jsonTemplate'

return code is either 0 (success) or -1 (fail)
"""
import sys
import json

path_to_womtool_template_fill_in_module = '.'
sys.path.insert(1, path_to_womtool_template_fill_in_module)
from womtool_template_fill_in import parse_args, args_dict_to_filledin_json

def main(args):
    """ Usage:
    python3 config_parser_II.py --jsonTemplate a.template.json -o a.FilledIn.json -i c1.txt -i c2.txt
    
    Args (command line args):
        --jsonTemplate: womtool generated json template file
        -o              output file name (usually like - Workflowname.FilledIn.json)
        -i              one or more config_whatever.txt files each preceeded by "-i"
        
    Returns:
        rc:             0=success, -1=fail
    """
    parsed_args = parse_args(args)
    args_dict = json.dumps(vars(parsed_args), indent=4)
    args_dict = json.loads(args_dict)
    
    rc = args_dict_to_filledin_json(args_dict)
    
    return rc
        
if __name__ == '__main__':
    rc = main(sys.argv[1:])
