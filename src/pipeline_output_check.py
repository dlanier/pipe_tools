import os
import sys
import filecmp
import numpy as np
import pandas as pd

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

def get_functions_dict(file_name):
    """ Usage: function_dict = get_functions_dict(file_name)
    Args:
        file_name:      full path of python file name
    Returns:
        function_dict:  function name: function definition string
    """
    fname = os.path.abspath(file_name)
    function_dict = {'header': ''}
    build_string = ''
    header_name = 'header'
    last_function_name = header_name
    with open(fname, 'r') as fh:
        for line in fh:
            if "def " in line:
                function_dict[last_function_name] = build_string
                build_string = line
                func_name = line.split('(')[0]
                func_name = func_name[4:]
                function_dict[func_name] = ''
                last_function_name = func_name
            else:
                build_string += line
                
    return function_dict

def dataframe_is_binary(unk_df):
    """ is_binary = dataframe_is_binary(unk_df)
    check matrix to see if the data is all equal to either 1 or 0 
    Args:
        unk_df:     numerical pandas dataframe of unknown data conformity
        
    Returns:
        is_binary:  True or False (all data is either = 1 or = 0)
    """
    row_size = unk_df.shape[0]
    col_size = unk_df.shape[1]
    non_binary = 0
    for index, row in unk_df.iterrows():
        if (int(sum(row == 0)) + int(sum(row == 1))) != col_size:
            non_binary += 1
    
    if non_binary > 0:
        return False
    else:
        return True


def get_cluster_sets_dict(one_df, column_name=1):
    """ csd = get_cluster_sets_dict(one_df) 
    Args:
        one_df:         dataframe of labels and clusterings
        column_name:    column name to count the clustering
    Returns:
        clusters_dict:  cluster_number: number_in_cluster
    """
    csd = {}
    n_clusters = one_df[column_name].max() + 1
    for k in range(0, n_clusters):
        s = (one_df[column_name] == k).sum()
        csd[k] = s
        
    return csd

def get_cluster_sets_dict_from_array(one_arr):
    """ csd = get_cluster_sets_dict(one_df) 
    Args:
        one_arr:
    Returns:
        clusters_dict:  cluster_number: number_in_cluster
    """
    csd = {}
    n_clusters = one_arr.max() + 1
    for k in range(0, n_clusters):
        s = (one_arr == k).sum()
        csd[k] = s
        
    return csd

def compare_labels(df1, df2, verbose=True):
    """ eq_count, neq_count = compare_labels(df1, df2) 
    Args:
        df1:        dataframe 1
        df2:        dataframe 2 (with same set of labels as dataframe 1)
        (verbose):  default True - prints row name differences
    Returns:
        eq_count:   number of rows that are equal
        neq_count:  number of rows that are not equal
        
    std_out:        prints name of 
    """
    eq_count = 0
    neq_count = 0
    for r in list(df1.index):
        if df2[1].loc[r] == df2[1].loc[r]:
            eq_count += 1
        else:
            neq_count += 1
            if verbose == True:
                print('Not EQ',r ,cmat1[1].loc[r], df2[1].loc[r])
            
    return eq_count, neq_count

def renumber_clusters_by_sort_order(labels_df, column_name=1):
    """ Usage: renumbered_df = renumber_clusters_by_sort_order(labels_df, column_name=1) 
    Args:
        labels_df:      dataframe with no header (labels are index)
        column_name:    default = 1
    Returns:
        renumbered_df:  dataframe with same clustering where the cluster are renumbered in standard way
    """
    clusters_reverse_dict = get_sorted_clustering_reverse_dictionary(labels_df, column_name=1)
    renumbered_df = labels_df.copy()
    for idx_name in list(labels_df.index):
        renumbered_df[column_name].loc[idx_name] = clusters_reverse_dict[labels_df[column_name].loc[idx_name]]
        
    return renumbered_df

def get_sorted_clustering_reverse_dictionary(labels_df, column_name=1):
    """ clusters_dict = get_sorted_clustering_reverse_dictionary(labels_df, column_name=1) 
    Args:
        labels_df:      labels x cluster_number one column dataframe without header
        column_name:    default is first column 
                        - not tested with multiple cols but expect it would work
    Returns:
        clusters_dict:  reverse dictionay of cluster-numbers-as-input to cluster-numbers-for-sort-order-labels
                        - use to compare labels where different cluster number assignments were used
    """
    n_clusters = labels_df[column_name].max() + 1
    cluster_number_dict = {k: k for k in range(0, n_clusters)}
    cmat1_dict = labels_df.to_dict()[column_name]

    for k, v in cluster_number_dict.items():
        for bkey in sorted(list(labels_df.index)):
            if labels_df[column_name].loc[bkey] == k:
                cluster_number_dict[k] = labels_df[column_name].loc[bkey]
                break

    return {v: k for k, v in cluster_number_dict.items()}


def pipeline_results_compare(results_directory, trim_point):
    """ differs_dict_of_lists = pipeline_results_compare(results_directory, trim_point) 
    Args:
        results_directory:      with multiple runs of (exactly) the same pipeline
        trim_point:             Place to split the time stamp off of the file name e.g. "_Tue_10"
    Returns:
        differs_dict_of_lists:  dict of lists of file that did not match their predicessor
    """
    dir_list = os.listdir(results_directory)
    previous_file_name = ''
    previous_full_file_name = ''
    differs_dict_of_lists = {}
    for fn in dir_list:
        if previous_file_name == '' or previous_file_name != fn.split(trim_point)[0]:
            previous_full_file_name = os.path.join(results_directory, fn)
            previous_file_name = fn.split(trim_point)[0]

        elif previous_file_name == fn.split(trim_point)[0]:
            
            if filecmp.cmp(previous_full_file_name, os.path.join(results_directory, fn), shallow=False) != True:

                if fn.split(trim_point)[0] in differs_dict_of_lists.keys():
                    differs_dict_of_lists[fn.split(trim_point)[0]].append(fn)
                else:
                    _, pfn = os.path.split(previous_full_file_name)
                    differs_dict_of_lists[fn.split(trim_point)[0]] = [pfn]
                    differs_dict_of_lists[fn.split(trim_point)[0]].append(fn)
                    
            previous_full_file_name = os.path.join(results_directory, fn)
            previous_file_name = fn.split(trim_point)[0]
            
    return differs_dict_of_lists

def display_pipeline_results_compare(differs_dict_of_lists):
    """ display a result from pipeline_results_compare function 
    Args:
        differs_dict_of_lists:  return dictionary of mismatched files list from pipeline_results_compare
    """
    for k in list(differs_dict_of_lists.keys()):
        print(k,':')
        k_list = differs_dict_of_lists[k]
        for fn in k_list:
            print('\t',fn)