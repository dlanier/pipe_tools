"""
developed in support of KnowEnG BD2K projects circa 2017
author:
lanier4@illinois.edu
mradmstr514226508@gmail.com
"""
import os
import pandas as pd
import yaml


def get_run_parameters(run_directory, run_file):
    """ Read system input arguments run directory name and run_file into a dictionary.

    Args:
        run_directory: directory where run_file is expected.

    Returns:
        run_parameters: python dictionary of name - value parameters.
    """
    run_file_name = os.path.join(run_directory, run_file)
    with open(run_file_name, 'r') as file_handle:
        run_parameters = yaml.load(file_handle)
    if not isinstance(run_parameters, dict):
        run_parameters = {}

    # run_parameters["run_directory"] = run_directory
    run_parameters["run_file"] = run_file

    return run_parameters


def get_parameter_keys_dict(yaml_dir, parameter_key_dict=None, methods_list=None, file_ext=['.yml', '.json']):
    """ get the list of yaml files in the yaml_dir, the list of methods in all those,
        and a dictionary of key types

    Args:
        yaml_dir:           path the the yaml files
        parameter_key_dict: (optional) dictionary to add key types
        methods_list:       (optional) list of methods to append

    Returns:
        yaml_files_list:    the list of yaml files in the yaml_dir
        methods_list:       the list of methods in the yaml files
        parameter_key_dict: key-name: key-type   dictionary
    """
    if parameter_key_dict is None:
        parameter_key_dict = {}
    if methods_list is None:
        methods_list = []

    type_dict = {int: 'int', float: 'real', str: 'string', list: 'list'}

    yaml_files_list = []
    for f in os.listdir(yaml_dir):
        ff = os.path.join(yaml_dir, f)
        some_nombre, nombre_ext = os.path.splitext(f)
        if os.path.isfile(ff) and nombre_ext in file_ext:
            yaml_files_list.append(f)

    for f_name in yaml_files_list:
        run_parameters = get_run_parameters(yaml_dir, f_name)
        for k, v in run_parameters.items():
            if k not in parameter_key_dict.keys():
                parameter_key_dict[k] = type_dict[type(v)]
            if k == 'method' and k not in methods_list:
                methods_list.append(v)

    methods_list = list(set(methods_list))
    return parameter_key_dict, methods_list, yaml_files_list


def show_parameter_keys_dict(parameter_key_dict):
    """ formatted display of dictionary key value pairs
    """
    for k, v in parameter_key_dict.items():
        print('%30s: %s' % (k, v))


def get_yaml_df(yaml_dir, UNUSED_FILL='not used'):
    """ read the yaml files in 'yaml_dir' and constuct a datafrme with rows of keys, columns of file names and
        filled with the each yaml file values.
    Args:
        yaml_dir:       path the the yaml files
        UNUSED_FILL:    string to use for fill where a yaml file has no entry for a key (row name)
    """
    key_dict, methods_list, yaml_files_list = get_parameter_keys_dict(yaml_dir)
    if 'run_file' in key_dict.keys():
        key_dict.pop('run_file')
    yaml_file_df = pd.DataFrame(data=None, index=key_dict.keys(), columns=None)

    for f_name in yaml_files_list:
        run_parameters = get_run_parameters(yaml_dir, f_name)
        if 'run_file' in run_parameters.keys():
            run_parameters.pop('run_file')

        yaml_file_df[f_name] = UNUSED_FILL
        for k, v in run_parameters.items():
            yaml_file_df[f_name].loc[k] = v

    return yaml_file_df

