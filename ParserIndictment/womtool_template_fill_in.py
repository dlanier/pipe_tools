""" 
Starting with a WOMTOOL created workflow.template.json file 
a list of properly formatted configureation files
is assembled and written to a workflow.FilledIn.json file.

The previous repository version of the python command-line interface is preserved.
"""
import os
import argparse
import sys
import json
import yaml
from collections import OrderedDict, defaultdict, Counter


def get_json_file_dict(data_fullfilename):
    """ Usage: json_dict = get_json_file_dict(data_fullfilename)
    
    Args:
        data_fullfilename: json or yaml format full path filename
                                quoted strings or not (if consistant) 
                                -but no lines start with tab characters
    Returns:
        json_dict:               python dictionary of name - value parameters.
    """
    with open(data_fullfilename, 'r') as fh:
        json_dict = yaml.load(fh)

    return json_dict


def get_config_file_dict(configfile_fullpath):
    """ Usage:   config_file_dict = get_config_file_dict(configfile_fullpath)
    
    User must insure plain text encoding and the format dictated by WOMTOOLS - template.json 
    key="value in a string form" 
    key="124.7654"
    key="0"
    key="true"
    key=""
    key=[[["value1", "value2"]]]
    
    Args:
        configfile_fullpath:    full path to formatted plain text file 
                                
    Returns:
        config_file_dict:       python dictionary of key-value pairs 
                                (suitable for json file insertion)
    """
    pairs_list = []
    
    with open(configfile_fullpath, 'r') as fh:
        lines = fh.readlines()
        
    for line in lines:
        l = line.strip().split("=")
        if len(l) > 0 and len(l[0]) > 0:
            lefty = l[0].strip()
            if len(lefty) == 0:
                continue

            if not lefty[0] == "#" and len(l) > 1 and len(l[1]) > 0:
                righty = l[1].strip()
                if len(righty) == 0:
                    righty = ' '
                        
                if len(lefty) > 0:
                    pairs_list.append((lefty, righty))

    if len(pairs_list) > 0:
        config_file_dict = OrderedDict(pairs_list)
    else:
        config_file_dict = {}

    return config_file_dict


def assemble_config_dict(config_files_list):
    """ Usage: config_dict = assemble_config_dict(config_files_list)
    Get an orderd dictionary of all variables from the config files list.
    Note that the config files must exist and be of proper mayo format. 
        (ascii key="value" with one special magic string value format)
    -- stdout if file not found or duplicate information .
    -- future version could return specific config duplicates info if they are not exact key:values match.
    
    Args:
        config_files_list:      python list of configurateion.txt files
        
    Returns:
        config_dict:            python ordered dictionary of 
    """
    config_dict_list = []
    for file_name in config_files_list:
        if os.path.isfile(file_name):
            conf_dict_next = get_config_file_dict(file_name)
            for k, v in conf_dict_next.items():
                config_dict_list.append((k, v))
        else:
            print('\n\t', file_name, '\n\tNot found - Ignoring this file\n')

    total_number_of_tuples = len(config_dict_list)
    if total_number_of_tuples > 0:
        config_dict = OrderedDict(config_dict_list)
        number_of_duplicates = total_number_of_tuples - len(config_dict)
        if number_of_duplicates > 0:
            print('\nDuplicates Found: %i\n'%(number_of_duplicates))
    else:
        config_dict = {}
    
    return config_dict


def get_json_keys_config_dict(json_dict):
    """ Usage:    keys_dict = get_json_keys_config_dict(json_dict) 
    
    Args:
        json_dict:      json template file as python dict
        
    Returns:
        keys_dict:      key is righmost member of json key
                        value is list of json keys in the input dict
    """
    keys_dict = defaultdict(list)
    for k, v in json_dict.items():
        k_list = k.split('.')
        keys_dict[k_list[-1]].append(k)
    
    return keys_dict


def configure_json_dict(json_dict, config_dict):
    """ Usage: 
    configured_dict, json_missing_dict, config_used_dict = configure_json_dict(json_dict, config_dict)
    
    Args:
        json_dict:          python dict from json template file
        config_dict:        python dict from config.txt file intended to fill in the json template
        
    Returns:
        configured_dict:    json dict keys: config dict values
        json_missing_dict:  keys: value (= types)  for json dict keys not found in config dict
        config_used_dict:   the config file key-value pairs used
    """
    configured_dict = defaultdict()
    json_missing_dict = defaultdict()
    config_used_dict = defaultdict()
    json_keys_counter = Counter(json_dict.keys())
    
    keys_d = get_json_keys_config_dict(json_dict)
    
    #                              put the config dict values in the json file full-key
    for k, v in config_dict.items():
        if k in keys_d:
            config_used_dict[k] = v

            for var_name in keys_d[k]:
                if len(v) > 2 and v[0:2] == '""':
                    v_fixed = '"' + '\\' + '"'
                    v_fixed += v[2:-2]
                    v_fixed += '"' + '\\'  + '"'
                    configured_dict[var_name] = v_fixed
                else:
                    configured_dict[var_name] = v.strip()
                    
                json_keys_counter[var_name] += 1
                
    for k, v in json_keys_counter.items():
        if v < 2:
            json_missing_dict[k] = json_dict[k]
                
    return configured_dict, json_missing_dict, config_used_dict


def write_filled_in_json_dict(json_dict, template_dict, filename_prefix='test', output_dir=None):
    """ Usage:    
    outfile = write_filled_in_json_dict(json_dict, json_template_dict, filename_prefix, output_dir)
    Write the json file input with respect to the types defined in the template.
    
    Args:
        json_dict:              template.json as dict and filled in with config.txt
        template_dict:          WOMTOOL template.json as python dict.
        filename_prefix:        (='test') string to prepend to .FilledIn.json
        output_dir:             (=None) if DNE current directory is used
        
    Returns:
        full_filename:          written output filename
    """
    #                                   assemble full file name
    if output_dir is None or os.path.isdir(output_dir) == False:
        output_dir = os.getcwd()
        
    filename_suffix = '.FilledIn.json'
    if len(filename_prefix) < 1:
        full_filename = os.path.join(output_dir, 'test' + filename_suffix)
    else:
        full_filename = os.path.join(output_dir, filename_prefix.strip('.') + filename_suffix)
        
    #                                   assemble filled-in json file as string
    out_string = '{\n'
    for json_key, json_value in json_dict.items():
        out_string += '    "' + json_key + '":'
        #                               magic string value first
        if json_value[0:4] == '"\\"\'':
            out_string += ' \"\\\"' + json_value[3:] + '\"\n'
        else:
            out_string += ' ' + json_value + ',\n'
            
    out_string = out_string[:-2] + '\n}\n'
    
    #                                   open file handle an write the string
    with open(full_filename, 'w') as fh:
        fh.writelines(out_string)
        
    return full_filename


def args_dict_to_filledin_json(args_dict, output_dir=None):
    """ Usage: return_code = args_dict_to_filledin_json(args_dict, output_dir) 
    WRAPPER - assemble all the above fucntions in the context of the input command line args.
    
    Args:
        args_dict:          Command line arguments converted to a python dict
        output_dir:         Where to write the output
        
    Returns:
        rc:                 return code = 0 if write operation succeeded, else rc = -1
    """
    
    if output_dir is None or os.path.isdir(output_dir) == False:
        output_dir = os.getcwd()
        
    # get the template.json dictionary
    json_template_dict = get_json_file_dict(args_dict['jsonTemplate'])
    
    # assemble config files list into a single config dictionary
    config_dict = assemble_config_dict(config_files_list=args_dict["i"])
    
    # get the Filled In dict
    filled_in_dict, json_missing_dict, config_used_dict = configure_json_dict(json_template_dict, config_dict)
    
    # make up the output file name
    filename_prefix = args_dict['jsonTemplate'].split('.')[0]
    full_filename = write_filled_in_json_dict(filled_in_dict, json_template_dict, filename_prefix, output_dir)

    if os.path.isfile(full_filename):
        rc = 0
    else:
        rc = -1
    
    return rc


def parse_args(args):
    """         This function (parse_args) is copied from existing repo to preserve input signature 
    By default, argparse treats all arguments that begin with '-' or '--' as optional in the help menu 
    (preferring to have required arguments be positional).

    To get around this, we must define a required group to contain the required arguments
    This will cause the help menu to be displayed correctly
    """
    parser = argparse.ArgumentParser()

    required_group = parser.add_argument_group('required arguments')
    
    required_group.add_argument("-i", action='append', required=True, metavar='',
                                help="The input configuration files (Multiple entries of this flag are allowed)")
    
    required_group.add_argument("--jsonTemplate", required=True, metavar='',
                                help='The json template file that is filled in with data from the input files')
    
    required_group.add_argument("-o", required=True, metavar='',
                                help='The location for the output file')
    
    # Truly optional argument
    parser.add_argument('--jobID', type=str, metavar='', help='The job ID', default=None, required=False)
    
    # Debug mode is on when the flag is present and is false by default
    parser.add_argument("-d", action="store_true", help="Turns on debug mode", default=False, required=False)
    
    return parser.parse_args(args)
