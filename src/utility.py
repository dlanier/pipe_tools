from inspect import getmembers, isfunction, getsource, signature

def display_module_functions(any_module):
    """ Usage: display_module_functions(any_module) 
    Args:
        any_module:         an imported python module
        
    """
    imported_functions_list = ['getmembers', 'isfunction', 'getsource', 'signature']

    functions_list = [o for o in getmembers(any_module) if isfunction(o[1])]
    docs_list = [getsource(o[1]) for o in getmembers(any_module) if isfunction(o[1])]

    for k in range(len(functions_list)):
        f = functions_list[k]
        if f[0] in imported_functions_list: 
            continue
        else:
            d = docs_list[k]
            split_fails = True
            try:
                A, B, C = d.split('"""')
                split_fails = False
            except:
                try:
                    A, B, C, D, F = d.split('"""')
                    split_fails = False
                except:
                    pass
            
            if split_fails == False:
                print('def %s%s'%(f[0], signature(f[1])))
                print(B,'\n')
                

def get_pip3_versions_dict():
    """ Usage: get_pip3_versions_dict()
         
    Returns:
        pip3_vd:                pip3 installed versions dictionary
    """
    file_name = 'pip_tst_list.txt'
    pip_str = 'pip3 list &> ' + file_name
    os.system(pip_str)

    pip3_vd = {}
    with open(file_name, 'r') as fh:
        for line in fh:
            n, N = line.split()
            if n[0] == '-' or n == 'Package':
                continue
            pip3_vd[n] = N

    os.remove(file_name)

    return pip3_vd

def get_version_dict(package_names_list, display_version_numbers=True):
    """ get the installed versions from a version list 
    
    Args:
        package_names_list:         a python list of pypi packages
        display_version_numbers:    print the output to the command line
        
    Returns:
        actual_version_dict:        python dict of form { package_name: installed_version_number }
    """
    actual_version_dict = {}
    for lib_in in package_names_list:
        IMPORTED_SUCCESSFULLY = False
        installed_version = '-.--.-'
        try:
            one_module = importlib.import_module(lib_in)
            IMPORTED_SUCCESSFULLY = True
            installed_version = one_module.__version__

        except:
            pass

        if IMPORTED_SUCCESSFULLY == True:
            actual_version_dict[lib_in] = installed_version
        else:
            actual_version_dict[lib_in] = 'Not Found'

        if display_version_numbers == True:
            if IMPORTED_SUCCESSFULLY == True:
                print('%20s:  %s'%(lib_in, installed_version))
            else:
                print('%20s:  %s'%(lib_in, 'Not Found'))

    return actual_version_dict