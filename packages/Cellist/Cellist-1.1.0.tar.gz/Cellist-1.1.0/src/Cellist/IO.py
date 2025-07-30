# -*- coding: utf-8 -*-
# @Author: dongqing
# @Date:   2023-10-14 12:05:31
# @Last Modified by:   dongqing
# @Last Modified time: 2025-03-24 20:55:29

import os
import h5py
import tables
import collections
import numpy as np
import pandas as pd
from scipy import sparse
from Cellist.Utility import get_cell_mat, longdf_to_mat

FeatureBCMatrix = collections.namedtuple('FeatureBCMatrix', ['ids', 'names', 'barcodes', 'matrix'])

def read_10X_h5(filename):
    """Read 10X HDF5 files, support both gene expression and peaks."""
    with tables.open_file(filename, 'r') as f:
        try:
            group = f.get_node(f.root, 'matrix')
        except tables.NoSuchNodeError:
            print("Matrix group does not exist in this file.")
            return None
        feature_group = getattr(group, 'features')
        ids = getattr(feature_group, 'id').read()
        names = getattr(feature_group, 'name').read()
        barcodes = getattr(group, 'barcodes').read()
        data = getattr(group, 'data').read()
        indices = getattr(group, 'indices').read()
        indptr = getattr(group, 'indptr').read()
        shape = getattr(group, 'shape').read()
        matrix = sparse.csc_matrix((data, indices, indptr), shape=shape)
        return FeatureBCMatrix(ids, names, barcodes, matrix)

def write_10X_h5(filename, matrix, features, barcodes, datatype = 'Peak'):
    """Write 10X HDF5 files, support both gene expression and peaks."""
    f = h5py.File(filename, 'w')
    if datatype == 'Peak':
       M = sparse.csc_matrix(matrix, dtype=np.int8)
    else:
       M = sparse.csc_matrix(matrix, dtype=np.float32)
    B = np.array(barcodes, dtype='|S200')
    P = np.array(features, dtype='|S100')
    FT = np.array([datatype]*len(features), dtype='|S100')
    AT = np.array(['genome'], dtype='|S10')
    mat = f.create_group('matrix')
    mat.create_dataset('barcodes', data=B)
    mat.create_dataset('data', data=M.data)
    mat.create_dataset('indices', data=M.indices)
    mat.create_dataset('indptr', data=M.indptr)
    mat.create_dataset('shape', data=M.shape)
    fet = mat.create_group('features')
    fet.create_dataset('_all_tag_keys', data=AT)
    fet.create_dataset('feature_type', data=FT)
    fet.create_dataset('id', data=P)
    fet.create_dataset('name', data=P)
    f.close()

def read_h5(h5_file):
    expr_read = read_10X_h5(filename = h5_file)
    expr_mat = expr_read.matrix
    expr_genes = expr_read.names.tolist()
    expr_cells = expr_read.barcodes.tolist()
    if type(expr_genes[0]) == bytes:
        expr_genes = [i.decode() for i in expr_genes]
    if type(expr_cells[0]) == bytes:
        expr_cells = [i.decode() for i in expr_cells]
    return(expr_mat, expr_genes, expr_cells)

def write_segmentation_h5(count_df_seg, seg_res, out_prefix, out_dir, count_name):
    expr_mat, gene_list, cell_list = get_cell_mat(count_df_seg, seg_res, count_name)
    count_h5_file = os.path.join(out_dir, "%s_segmentation_cell_count.h5" %out_prefix)
    write_10X_h5(filename = count_h5_file, matrix = expr_mat, features = gene_list, barcodes = cell_list, datatype = 'Gene')

def write_segmentation_cell_coord(coord_df_seg, seg_res, out_prefix, out_dir):
    coord_df_seg = coord_df_seg.dropna(subset = [seg_res])
    cell_coord = coord_df_seg[['x', 'y', seg_res]].groupby(seg_res).mean()
    cell_nspot = coord_df_seg[['x',seg_res]].groupby(seg_res).count()
    cell_nspot = cell_nspot.rename(columns = {'x': "nSpot"})
    cell_coord_nspot = pd.merge(cell_coord, cell_nspot, on = seg_res)
    cell_coord_file = os.path.join(out_dir, "%s_segmentation_cell_coord.txt" %out_prefix)
    cell_coord_nspot.to_csv(cell_coord_file, sep = "\t")
    return(cell_coord_nspot)

def gem_to_mat(gem_df, outfile, countname = 'MIDCount'):
    gem_df['x_y'] = gem_df['x'].astype(str) + '_' + gem_df['y'].astype(str)
    gene_spot = gem_df[countname].groupby([gem_df['x_y'], gem_df['geneID']]).sum()
    spot_expr_mat, gene_list, spot_list = longdf_to_mat(gene_spot)
    count_h5_file = outfile
    write_10X_h5(filename = count_h5_file, matrix = spot_expr_mat, features = gene_list, barcodes = spot_list,  datatype = 'Gene')
    return(gem_df)
