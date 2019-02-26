import sys
import json
sys.path.insert(1, '.')
from json_template_configuration import parse_args, args_dict_to_filledin_json

def main(args):
    parsed_args = parse_args(args)
    args_dict = json.dumps(vars(parsed_args), indent=4)
    args_dict = json.loads(args_dict)
    
    rc = args_dict_to_filledin_json(args_dict)
    
    return rc
        
if __name__ == '__main__':
    rc = main(sys.argv[1:])
