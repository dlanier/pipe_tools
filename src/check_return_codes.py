"""
Usage:
python ~/python/check_return_codes.py -d /projects/mgc/Project_1/DEL/MVP/cromwell-executions/GermlineMasterWF/
or 
python ~/python/check_return_codes.py -d `pwd`

check return codes in directory tree
"""

import os
import argparse

good_return_codes_list = ['0', '0\n']

def check_rc_codes(x_directory=None):
    if not x_directory is None and os.path.isdir(x_directory):
        dir_tree_root = x_directory
    else:
        dir_tree_root = os.getcwd()
    root_trim_str, _ = os.path.split(dir_tree_root)
    for dir_name, dir_list, files_list in os.walk(dir_tree_root):
        for filename in files_list:
            if filename == 'rc':
                full_filename = os.path.join(dir_name, filename)
                with open(full_filename, 'r') as fh:
                    lines = fh.readlines()
                if lines[0] in good_return_codes_list:
                    top_dir = dir_name.replace(root_trim_str, '..')
                    print('good rc:  %s'%(top_dir))
                else:
                    print('\n\tBad Dog! Bad Dog!')
                    print('code = %s in \n%s'%(str(lines[0]).strip(), full_filename))
                    print('\tBad Dog! Bad Dog!\n')
                    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str)
    args = parser.parse_args()
    check_rc_codes(args.d)

