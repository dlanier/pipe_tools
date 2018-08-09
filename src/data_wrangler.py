"""
Fall 2016, Spring 2018
lanier4@illinois.edu
mradmstr514226508@gmail.com
"""
import os
import importlib
import time
import numpy as np
import pandas as pd
from IPython.display import clear_output


def get_pip3_versions_dict():
    """ get installed versions from pip3 """
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
    """ get the installed versions from a version list"""
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

def show_df_heads(data_dir):
    """ display the head of dataframe files in a directory """
    files_dict = {}
    if os.path.isdir(data_dir):
        f_list = os.listdir(data_dir)
        for may_file in f_list:
            a_file = os.path.join(data_dir, may_file)
            if os.path.isfile(a_file):
                files_dict[may_file] = a_file
    dict_size = len(files_dict)
    if dict_size > 0:
        for may_file, a_file in files_dict.items():
            dict_size -= 1
            show_file = input('y er n? show: %s'%(may_file))
            if show_file == 'y':
                print('Trying to show contents of:', a_file)
                try:
                    some_df = pd.read_csv(a_file, sep='\t', index_col=0, header=0)
                    print(some_df.head())
                except:
                    print('nix nix')

            if dict_size > 0:
                keep_goin = input('continue? y er n?')
                if not keep_goin == 'y':
                    break
                else:
                    clear_output()


def get_directory_dataframe_shapes(data_directory):
    """ get the dataframe shapes in a directory """
    file_list = os.listdir(data_directory)
    dir_listing = []
    for f in file_list:
        maybe_file = os.path.join(data_directory, f)
        if os.path.isfile(maybe_file):
            n_rows, n_cols = get_dataframe_row_col_count(maybe_file)
            dir_listing.append('%-55s : (%6d, %6d)'%(f,n_rows,n_cols))
    return dir_listing        

def get_dataframe_row_col_count(full_file_name):
    """ if column count is zero or one then maybe file is not tab separated 
    Args:
        full_file_name:   full path name of file to examine
    Returns:
        row_count:        number of newline characters
        col_count:        number of tab characters in the first line
    """
    row_count = 1 # starts increment with second line
    firstline = ''
    if os.path.isfile(full_file_name):
        with open(full_file_name, 'r') as file_handle:
            firstline = file_handle.readline()
            for line in file_handle:
                row_count += 1
        col_count = len(firstline.split('\t'))
        return row_count, col_count
    else:
        return 0, 0

def show_dictionary(a_dict):
    """ display a set of run parameters """
    for k in sorted(a_dict.keys()):
        print(k,':\t',a_dict[k])
    
    
def show_matrix(A, n_dec=3):
    """ Display a matrix (nicely) with a fixed number of decimal places.
    """
    format_str = '%' + '0.0%df\t'%(n_dec)
    n_rows = A.shape[0]
    n_cols = 1
    if A.size > sum(A.shape): n_cols = A.shape[1]
    for row in range(0, n_rows):
        s = ''
        for col in range(0, n_cols):
            s = s + format_str%(A[row,col])
        print(s)
    return


def integer_to_alphabet_number(N):
    """ convert integer to spreadsheet column lettering """
    B = 26
    ALPH = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    max_mag = 100
    M = 0

    while (N > B**M) & (M <= max_mag):
        M += 1
        
    S = []
    for nada in range(0, M):
        M -= 1
        D = np.int_(np.floor(N / B**M))
        N = N - D * B**M
        S.append(ALPH[D-1])
    
    alpha_N = ''.join(S)
    
    return alpha_N


def alphabet_number_to_integer(N):
    """ convert spreadsheet column lettering to integer """
    ALPH = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    alphanumeric_dictionary = dict(zip(ALPH, np.arange(1, len(ALPH)+1)))
    N = list(N)[::-1]
    numeric_N = 0
    for p in range(0, len(N)):
        numeric_N += alphanumeric_dictionary[N[p]] * 26**p
    return numeric_N


def delay_time(time_delay=1):
    """ approximate time delay funtion for development stuff - probably accruate to 10 ms """
    step_size = 1000
    t0 = time.time()
    for k in range(0, step_size):
        if k == k: pass
    et_4_1step = time.time() - t0
    time_delay = int(time_delay * step_size / et_4_1step  - et_4_1step)
    for k in range(0, time_delay):
        if k == k: pass
    return

def is_prime(n):
    """ check if is prime """
    if n % 2 == 0: return False
    for k in range(3, int(np.sqrt(n))+2, 2):
        if n % k == 0: return False
    return True


def check_set_phenotype_alignment(pheno_file_full_name, sample_names):
    """ phenotype_rewrite_transposed = check_set_phenotype_alignment(pheno_file_full_name, sample_names) """
    phenotype_rewrite_transposed = False
    try:
        pheno_df = pd.read_csv(pheno_file_full_name, sep='\t', index_col=0, header=0)
        if pheno_df.empty:
            return phenotype_rewrite_transposed
        
        pheno_sample_names = list(pheno_df.columns)
        pheno_index_names = list(pheno_df.index)
        
        if len(list(set(pheno_sample_names) & set(sample_names))) > 0:
            pheno_df = pheno_df.transpose()
            pheno_df.to_csv(pheno_file_full_name, sep='\t', index=True, header=True)
            # print('\t\tPhenotype file Transposed and written!')
            phenotype_rewrite_transposed = True
        elif len(list(set(pheno_index_names) & set(sample_names))) > 0:
            # print('\t\tIt Is OK the orientation.')
            pass

        else:
            # print('\t\tNo Intersection Found - De Nada!')
            pass
        
    except:
        pass
    
    return phenotype_rewrite_transposed