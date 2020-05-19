import os
import time
from collections import defaultdict
import inspect

IMPORT_WORDS = ['import', 'from']

def find_in_files(root_dir, f_types_list, seek_strings_list):
    """search files in a directory tree for strings
    
    Args:
        root_dir:           search tree root
        f_types_list:       list of file extensions (with '.') like ['.py', '.wdl', '.json', 'etc']
        seek_strings_list:  list of strings to hunt for in files of f-type in the code-rood_dir
        
    Returns:
        file_targets_line:  dict of file-names: dict of locations for seed strings
        target_files_dict:  dict of seek-list-string: to list of files containing it
                            (empty if no seek_list strings found)
    """
    search_start_time = time.time()
    number_of_files_checked = 0
    
    # initialize the (empty) return values
    file_targets_line = defaultdict(dict)
    target_files_dict =  defaultdict(list)
    
    # fail immediately if the root directory is not available
    if not os.path.isdir(root_dir):
        print('Unable to locate root directory:\n', root_dir)
        return file_targets_line, target_files_dict
    
    # guard the file types list input
    if isinstance(f_types_list, str):
        f_types = [f_types_list]
    elif isinstance(f_types_list, list):
        f_types = f_types_list
    else:
        print('Unable to process file types input. Need: [".py", ".ipynb"]\nGot:\n', f_types_list)
        return file_targets_line, target_files_dict
        
    # guard user misuse where file extensions do not start with period character
    for i in range(len(f_types_list)):
        if f_types_list[i][0] != '.':
            f_types_list[i] = ''.join('.', f_types_list[i])
            
    # guard the list of strings to find in the files of type
    if isinstance(seek_strings_list, str):
        seek_list = [seek_strings_list]
    elif isinstance(seek_strings_list, list):
        seek_list = seek_strings_list
    else:
        print('Bad seek string input. Need: ["ducks", "turles"]\nGot:\n', seek_strings_list)
        return file_targets_line, target_files_dict
        
    # for every directory in the input root directory
    for d, dl, fl in os.walk(root_dir):
        
        # for each file in that directory
        for f in fl:
            
            # it the file is of one of the input types
            if os.path.splitext(f)[1] in f_types:
                
                full_file = os.path.join(d, f)
                
                lines = []
                
                try:
                    with open(full_file, 'r') as fh:
                        lines = fh.readlines()
                        
                except:
                    print('Unable to open file:\n%s\n', full_file)
                    
                finally:
                    
                    # if the file was opened and not empty
                    if len(lines) > 0:
                        number_of_files_checked += 1
                        
                        # read each line in the file
                        for line_n in range(len(lines)):
                            line = lines[line_n]
                            
                            # check each string in the input list
                            for s in seek_list:
                                
                                if s in line:
                                    
                                    # append the dictionary of target_word : files
                                    target_files_dict[s].append(full_file)
                                    
                                    # Note: this will require reader to use the same space replacement chars
                                    s_line = s.replace(' ', '_')
                                    
                                    # add the line number to the dictionary of files.target_word : locations
                                    if s_line in file_targets_line[full_file]:
                                        file_targets_line[full_file][s_line].append(line_n)
                                        
                                    else:
                                        file_targets_line[full_file][s_line] = [line_n]

    # alphabetize the target-word : filename dictionary
    if len(target_files_dict) > 1:
        for k in target_files_dict.keys():
            target_files_dict[k] = sorted(list(set(target_files_dict[k])))
            
    # Brag about it (er maybe not)
    tt = time.time() - search_start_time
    print('%s searched in %i files in %0.3f s'%(inspect.stack()[0][3], number_of_files_checked, tt))
    
    return file_targets_line, target_files_dict
