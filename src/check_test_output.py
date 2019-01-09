"""
check_test_ouput.py
Usage:
python ~/python/check_test_output.py -d /projects/mgc/Project_1/DEL/MVP/cromwell-executions/GermlineMasterWF/
or 
python ~/python/check_test_output.py -d `pwd` -show_stds True

check return codes and std_out in directory tree
"""

import os
import argparse

good_return_codes_list = ['0', '0\n']
file_names_to_show_list = ['rc', 'stdout', 'stderr']

def check_rc_codes(x_directory=None, show_stds=False):
    if not x_directory is None and os.path.isdir(x_directory):
        dir_tree_root = x_directory
    else:
        dir_tree_root = os.getcwd()
    root_trim_str, _ = os.path.split(dir_tree_root)
    for dir_name, dir_list, files_list in os.walk(dir_tree_root):
        for filename in files_list:
            if filename in file_names_to_show_list:
                full_filename = os.path.join(dir_name, filename)
                with open(full_filename, 'r') as fh:
                    lines = fh.readlines()
                if len(lines) <= 0:
                    continue
                elif filename == 'rc':
                    if lines[0] in good_return_codes_list:
                        top_dir = dir_name.replace(root_trim_str, '..')
                        print('\ngood rc:  %s'%(top_dir))
                    else:
                        print('\n\tBad Dog! Bad Dog!')
                        print('code = %s in \n%s\n'%(str(lines[0]).strip(), full_filename))
                elif show_stds:
                    # opportunity to reformat for readability
                    print('\n\n~~~~~~~~~~full_filename~~~~~~~~~~~~~~:\n%s\n'%(full_filename))
                    for line in lines:
                        print(line)
                    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str)
    parser.add_argument('-show_stds', nargs="?", const=False, type=bool)
    args = parser.parse_args()
    check_rc_codes(args.d, args.show_stds)

