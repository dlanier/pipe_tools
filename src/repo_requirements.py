"""
get pip3 requirements file only for the required .py and .ipynb files in a repository
"""
import os
import sys
import argparse
import tempfile
import json


def get_pip_requirements_dict():
    """ get the pip3 list of python installed modules
    
    Args:                   (none)
        
    Returns:
        requirements_dict:  {module_name: version_number, ...}
        
    """
    tf_name = tempfile.NamedTemporaryFile().name
    req_str = 'pip3 freeze' + ' ' + '&>' + ' ' + tf_name
    
    os.system(req_str)
    
    with open(tf_name, 'r') as fh:
        lines = fh.readlines()
        
    requirements_dict = {}
    for line in lines:
        req_line_list = line.strip().split('==')
        if len(req_line_list) == 2:
            requirements_dict[req_line_list[0]] = req_line_list[-1]

    return requirements_dict

def get_ipynb_import_list(nb_file_name, imports_list=None):
    """ get the list of imported modules in a ipynb
    """
    import_keys_list = ['import', 'from']
    
    if imports_list is None or not isinstance(imports_list, list):
        imports_list = []

    _, f_ext = os.path.splitext(nb_file_name)
    if f_ext == '.ipynb':
        nb_dict = json.load(open(nb_file_name))
        for cell in nb_dict['cells']:
            for l in cell['source']:
                src_line_list = l.split()
                if len(src_line_list) > 1 and src_line_list[0] in import_keys_list:
                    module_str_list = src_line_list[1].split('.')
                    imports_list.append(module_str_list[0])
                
    return sorted(list(set(imports_list)))

def get_python_file_import_list(py_file_name, imports_list=None):
    """ get the list of imported modules in a ipynb
    """
    import_keys_list = ['import', 'from']
    
    if imports_list is None or not isinstance(imports_list, list):
        imports_list = []

    _, f_ext = os.path.splitext(py_file_name)
    if f_ext == '.py':
        with open(py_file_name, 'r') as fh:
            lines = fh.readlines()
        for line in lines:
            line_list = line.split()
            if len(line_list) > 1 and line_list[0] in import_keys_list:
                imports_list.append(line_list[1].split('.')[0])
                                
    return sorted(list(set(imports_list)))


def get_py_requirements_for_dirname(dirname):
    """  """
    actual_required_dict = {}
    missed_list = []
    requirements_dict = get_pip_requirements_dict()
    imports_list = []
    if os.path.isdir(dirname) and len(requirements_dict) > 0:
        for d_name, d_list, f_list in os.walk(dirname):
            for f in f_list:
                _, f_ext = os.path.splitext(f)
                if f_ext == '.py':
                    py_file_name = os.path.join(d_name, f)
                    imports_list = get_python_file_import_list(py_file_name, imports_list)
                elif f_ext == '.ipynb':
                    nb_file_name = os.path.join(d_name, f)
                    imports_list = get_ipynb_import_list(nb_file_name, imports_list)
                    
    if len(imports_list) > 0:
        imports_list = sorted(list(set(imports_list)))
        if len(imports_list) > 0:    
            for maybe_import in imports_list:
                if maybe_import in requirements_dict:
                    actual_required_dict[maybe_import] = requirements_dict[maybe_import]
                else:
                    missed_list.append(maybe_import)

    return actual_required_dict, sorted(list(set(missed_list)))

def get_pip_requirements_string(actual_required_dict):
    """ get string for .txt file from actual_required_dict
    """
    pip_requirements_string = ''
    
    if len(actual_required_dict) > 0:    
        for module_name, version_number in actual_required_dict.items():
            pip_requirements_string += '%s==%s\n'%(module_name, version_number)
                
    return pip_requirements_string

def write_requirements_for(dirname, output_filename='requirements.txt'):
    """ write requirements.txt only python files and notebooks in dirname
    """
    actual_req_dict, miss_list = get_py_requirements_for_dirname(dirname)
    S = get_pip_requirements_string(actual_req_dict)

    with open(output_filename, 'w') as fh:
        fh.write(S)

    if os.path.isfile(output_filename):
        print('File written:\n', output_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-dirname', required=True)
    parser.add_argument('-o', required=False)
    parsed_args = parser.parse_args(sys.argv[1:])
    args_dict = json.dumps(vars(parsed_args), indent=4)
    args_dict = json.loads(args_dict)

    if args_dict['o'] is None:
        write_requirements_for(args_dict['dirname'])
    else:
        write_requirements_for(args_dict['dirname'], args_dict['o'])
