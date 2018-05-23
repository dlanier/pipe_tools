"""
developed in support of KnowEnG BD2K projects circa 2017
author:
lanier4@illinois.edu
mradmstr514226508@gmail.com
"""
import os
import pandas as pd

import knpackage.toolbox as kn

def get_parameter_keys_dict(yaml_dir, parameter_key_dict=None, methods_list=None):
    """  get the list of yaml files in the yaml_dir, the list of methods in all those, and a dictionary of key types

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
        if os.path.isfile(ff) and nombre_ext == '.yml':
            yaml_files_list.append(f)

    for f_name in yaml_files_list:
        run_parameters = kn.get_run_parameters(yaml_dir, f_name)
        for k, v in run_parameters.items():
            if k not in parameter_key_dict.keys():
                parameter_key_dict[k] = type_dict[type(v)]
            if k == 'method' and k not in methods_list:
                methods_list.append(v)

    methods_list = list(set(methods_list))
    return parameter_key_dict, methods_list, sorted(yaml_files_list)


def get_yaml_df(yaml_dir, fill_string='not used'):
    """ Usage:  yaml_file_df = get_yaml_df(directory_with_yaml_files, fill_string)
    datafrme: rows are keys, columns are yaml file names: fill by yaml file values or unused fill string
    Args:
        yaml_dir:       path the the yaml files
        fill_string:    string to use for fill where a yaml file has no entry for a key (row name)
    """
    key_dict, methods_list, yaml_files_list = get_parameter_keys_dict(yaml_dir)
    if 'run_file' in key_dict.keys():
        key_dict.pop('run_file')

    yaml_file_df = pd.DataFrame(data=None, index=sorted(list(key_dict.keys())), columns=None)

    for f_name in yaml_files_list:
        run_parameters = kn.get_run_parameters(yaml_dir, f_name)
        if 'run_file' in run_parameters.keys():
            run_parameters.pop('run_file')

        yaml_file_df[f_name] = fill_string
        for k, v in run_parameters.items():
            yaml_file_df[f_name].loc[k] = v

    return yaml_file_df
