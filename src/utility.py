"""
lanier4@illinois.edu
"""
import os
import time
import numpy as np
import pandas as pd

import yaml
from inspect import getmembers, isfunction, getsource, signature

conscientious_message = 'USER MISTAKE -- NOT AN ERROR'

def show_conscientious_message():
    """ avoid throwing an error: just show_conscientious_message() """
    print(conscientious_message)


def get_sample_n_nans(in_df):
    """ get the number of nans in each column

    Args:
         in_df:                 a pandas dataframe with column names or numbers

    Returns:
        columns_n_nans_dict:    column name to number of nans dict
    """
    columns_n_nans_dict = {}
    for col_name in list(in_df.columns):
        km_nan_index = in_df[col_name].index[in_df[col_name].apply(np.isnan)]
        L = km_nan_index.tolist()
        columns_n_nans_dict[col_name] = len(L)

    return columns_n_nans_dict


def txt_to_list(file_name):
    """ pythonically read text file into a list of lines

    Args:
        file_name:           text file - each line will be treated as one name with spaces removed

    Returns:
        text_list:           list of lines with spaces removed
    """
    with open(file_name, 'r') as fd:
        data = fd.readlines()
    return [d.strip() for d in data]


def merge_txt_to_samples_df(file_name_1, file_name_2):
    """ get the binary dataframe of one file list inside the other

    Args:
        file_name_1:          text file one - each line will equal one row (without spaces)
        file_name_2:          text file two

    Returns:
        samples_df:           dataframe with file one names as index to ones if in file two, else zero
    """
    samples_df = None
    data_list_1 = sorted(list(set(txt_to_list(file_name_1))))
    data_list_2 = sorted(list(set(txt_to_list(file_name_2))))
    if len(data_list_1) > 0 and len(data_list_2) > 0:
        if len(data_list_1) >= len(data_list_2):
            samples_df = pd.DataFrame(data=np.zeros(len(data_list_1)), index=data_list_1)
            for gene_name in data_list_2:
                if gene_name in data_list_1:
                    samples_df.loc[gene_name] = 1

    return samples_df


def display_module_functions(imported_module, show_imported_functions=False):
    """ Usage: display_module_functions(any_module)

    Args:
        imported_module:         an imported python module
        show_imported_functions: default is False - ignore imported functions
        
    """
    ignore_functions_list = ['getmembers', 'isfunction', 'getsource', 'signature']

    functions_list = [o for o in getmembers(imported_module) if isfunction(o[1])]
    source_list = [getsource(o[1]) for o in getmembers(imported_module) if isfunction(o[1])]
    
    if len(source_list) != len(functions_list): return  #       This should not be possible
    
    for list_number in range(len(functions_list)):
        function_tuple = functions_list[list_number]    
        if function_tuple[0] in ignore_functions_list:
            if show_imported_functions == True:
                print('using: %s%s'%(function_tuple[0], signature(function_tuple[1])))
        else:
            source_str = source_list[list_number]
            docs_string = None
            try:
                docs_string = source_str.split('"""')[1]
            except:
                pass

            print('def %s%s'%(function_tuple[0], signature(function_tuple[1])))
            if docs_string is None:
                print('doc_missing\n')
            else:
                print(docs_string,'\n')


def save_installed_versions_to_txt(dir_name=None, file_name=None, time_stamp=True):
    """ write the pip3 view of installed packages

    Args:
        dir_name:           directory name to save in (default is current - run directory)
        file_name:          file name without directory or extension
        time_stamp:         default is True: add a time-date stamp to the name 
    """
    if dir_name is None:
        dir_name = os.getcwd()
        
    if file_name is None:
        file_name = 'py_module_versions_'
    else:
        _, file_name = os.path.split(file_name)
        file_name, _ = os.path.splitext(file_name)
        
    if time_stamp == True:
        file_name = file_name + time.strftime("%a_%d_%b_%Y_%H_%M_%S", time.localtime()) + '.txt'
    else:
        file_name = file_name + '.txt'
    
    full_file_name = os.path.join(dir_name, file_name)
    pip_str = 'pip3 list &> ' + full_file_name
    os.system(pip_str)

    return full_file_name


def get_pip3_versions_dict():
    """ Usage: get_pip3_versions_dict()
         
    Returns:
        pip3_vd:                pip3 installed versions dictionary
    """
    file_name = 'pip_tmp_list.txt'
    pip_str = 'pip3 list &> ' + file_name
    os.system(pip_str)
    
    pip3_vd = {}
    with open(file_name, 'r') as fh:
        for line in fh:
            n, N = line.split()
            if n[-5:] == '-----' or n[-5:] == '----:' or n == 'Package':
                continue
            pip3_vd[n] = N

    os.remove(file_name)

    return pip3_vd


def read_version_dict_file(versions_file_full_path):
    """ get the installed versions from a version list 
    
    Args:
        versions_file_full_path:    valid path to a text file created with unix command: pip3 list &> ver.txt
        display_version_numbers:    print the output to the command line
        
    Returns:
        actual_version_dict:        python dict of form { package_name: installed_version_number }
    """
    try:
        with open(versions_file_full_path, 'r') as fd:
            package_names_lines = fd.read().splitlines()
    except:
        print(versions_file_full_path, '\nfailed to open\n')
        return None
    
    ignore_name_list = ['Package']
    ignore_version_list = ['-------']
    package_names_dict = {}    
    for line in package_names_lines:
        str_list = line.split()
        package_name = str_list[0]
        package_version = str_list[1]
        if package_name in ignore_name_list or package_version in ignore_version_list:
            # print('skipp', package_name)
            continue

        else:
            package_names_dict[package_name] = package_version
            
    return package_names_dict


def display_version_dictionary(python_dict, header=None):
    """ std out formatted display of a python dictionary

    Args:
        python_dict:    a python dictionary {'name1':'def1', 'name2':'def2',... }
    """
    if not isinstance(python_dict, dict):
        show_conscientious_message()
        print('Input variable is not a python "dict"')
        return
    L = max([len(o) for o in list(python_dict.keys())])
    format_string = '%s%i%s: %s'%('%', L, 's', '%s')
    dict_keys = sorted(list(python_dict.keys()))

    if not header is None:
        print(format_string % (header[0], header[1]))
        print('')

    for key_n in dict_keys:
        if key_n[-3:] == '---' or key_n[-3:] == '--:' or key_n == 'Packages':
            continue

        print(format_string % (key_n, str(python_dict[key_n])))


def get_versions_intallation_dict(required_versions_dict, installed_versions_dict=None):
    """ required versions compare installed versions """
    not_found_message = '--.--.--'
    if installed_versions_dict is None:
        installed_versions_dict = get_pip3_versions_dict()
        
    inst_keys = list(installed_versions_dict.keys())
    comparison_dict = {}
    for req_key, req_ver in required_versions_dict.items():
        if req_key in inst_keys:
            comparison_dict[req_key] = [req_ver, installed_versions_dict[req_key]]
        else:
            comparison_dict[req_key] = [req_ver, not_found_message]
            
    return comparison_dict


def get_installed_differences_dict(required_versions_dict):
    """ returns dict of versions required vs versions installed that are different """
    comparison_dict = get_versions_intallation_dict(required_versions_dict)
    differences_dict = {}

    for package_name, compare_list in comparison_dict.items():
        if compare_list[0] != compare_list[1]:
            differences_dict[package_name] = compare_list
            
    return differences_dict


def dict_file_read(file_name):
    """ read a text file into a python dict - intended for version installation data """
    output_dict = None
    try:
        with open(file_name) as fd:
            for line in fd:
                (key, val) = line.split()
                if key[-2:] == '-:':
                    continue
                output_dict[key] = val
    except:
        pass
    
    if output_dict is None:
        try:
            output_dict = read_version_dict_file(file_name)
        except:
            print(file_name,'failed to load')
            pass
    
    return output_dict


def dict_write_file(input_dict, file_name='dict_file.txt'):
    """ write a python dict to a text file - intended for version installation data """
    try:
        with open(file_name, 'w') as file:
             file.write(yaml.dumps(input_dict))
    except:
        print(file_name,'fails to write')
        pass


def get_clone_imported_modules_list(dir_path):
    """ Usage: modules_list = get_clone_imported_modules_list(dir_path) """
    lib_list = []
    for dir, dir_list, files_list in os.walk(dir_path):
        for file in files_list:
            if len(file) > len('.py') and file[-3:] == '.py':
                full_file = os.path.join(dir, file)
                with open(full_file, 'r') as fh:
                    lines = fh.readlines()
                if len(lines) > 1:
                    for line in lines:
                        if line[0] != "#" and "import" in line:
                            line_list = line.strip().split(' ')
                            if line_list[0] == 'import':
                                if len(line_list) > 2:
                                    for lib in line_list[1:]:
                                        if lib != 'import' and lib != 'as':
                                            lib_list.append(lib.split('.')[0])
                                else:
                                    lib_list.append(line_list[1].split('.')[0])
                            elif line_list[0] == 'from':
                                lib = line_list[1].split('\t')[0]
                                lib_list.append(lib)

    return sorted(list(set(lib_list)))