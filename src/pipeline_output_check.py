import os
import sys
import filecmp
import numpy as np
import pandas as pd

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