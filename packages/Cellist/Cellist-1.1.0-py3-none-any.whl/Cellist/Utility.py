# -*- coding: utf-8 -*-
# @Author: dongqing
# @Date:   2023-08-26 22:39:03
# @Last Modified by:   dongqing
# @Last Modified time: 2025-04-28 20:02:19

import os
import matplotlib
import pandas as pd
import numpy as np
import scanpy as sc
import anndata as ad
import matplotlib.pyplot as plt

from scipy.spatial import KDTree
from scipy import sparse
import concurrent.futures


def sub_mat(mat, genes, cells, genes_sub = None, cells_sub = None):
	mat_use = mat
	if not genes_sub:
		if type(genes[0]) == bytes:
			genes = [i.decode() for i in genes]
		genes_sub = genes	
	if not cells_sub:
		if type(genes[0]) == bytes:
			cells = [i.decode() for i in cells]
		cells_sub = cells
	genes_used = sorted(genes_sub)
	genes_used_array = np.array(genes_used)
	genes_array = np.array(genes)
	genes_sorter = np.argsort(genes_array)
	genes_used_index = genes_sorter[np.searchsorted(genes_array, genes_used_array, sorter = genes_sorter)]
	mat_use = mat_use[genes_used_index, :]
	cells_used = sorted(cells_sub)
	cells_used_array = np.array(cells_used)
	cells_array = np.array(cells)
	cells_sorter = np.argsort(cells_array)
	cells_used_index = cells_sorter[np.searchsorted(cells_array, cells_used_array, sorter = cells_sorter)]
	mat_use = mat_use[:, cells_used_index]
	return(mat_use, genes_used, cells_used)

def longdf_to_mat(gene_cell_df):
	cells = set(str(x[0]) for x in gene_cell_df.index)
	genes = set(str(x[1]) for x in gene_cell_df.index)
	cells_dict = dict(zip(cells, range(0, len(cells))))
	genes_dict = dict(zip(genes, range(0, len(genes))))
	rows = [cells_dict[str(x[0])] for x in gene_cell_df.index]
	cols = [genes_dict[str(x[1])] for x in gene_cell_df.index]
	expr_mat = sparse.csr_matrix((gene_cell_df.values, (rows, cols)))
	expr_mat= expr_mat.T
	gene_list = list(genes)
	cell_list = list(cells)
	return(expr_mat, gene_list, cell_list)

def SpotBinGene(gem_df, bin_size, countname = 'MIDCount'):
	gem_df['x_bin'] = (gem_df['x']/bin_size).astype(np.uint32)*bin_size
	gem_df['y_bin'] = (gem_df['y']/bin_size).astype(np.uint32)*bin_size
	gem_df['binID'] = gem_df['x_bin'].astype(str) + "_" + gem_df['y_bin'].astype(str)
	gem_df_bin_gene = gem_df[countname].groupby([gem_df['binID'], gem_df['geneID']]).sum()
	expr_mat, gene_list, cell_list = longdf_to_mat(gem_df_bin_gene)
	return(gem_df, expr_mat, gene_list, cell_list)

def cal_dist(coord_df, mdist):
	kd_tree = KDTree(coord_df)
	sdm = kd_tree.sparse_distance_matrix(kd_tree, mdist)
	sdm_csc = sparse.csc_matrix(sdm, dtype=np.float32)
	return(kd_tree, sdm_csc)

def cal_weight(sdm_csc):
	weight = sdm_csc.copy()
	np.reciprocal(weight.data, out=weight.data)
	np.power(weight.data, 2, out=weight.data)
	weight.setdiag(1)
	return(weight)

def enhance_spot_expr(coord_df, coord_expr_mat, neigh_dist = 5, x_colname = "x", y_colname = "y"):
	kd_tree, sdm_csc = cal_dist(coord_df[[x_colname, y_colname]], neigh_dist)
	weight = cal_weight(sdm_csc)
	coord_expr_mat_enhanced = coord_expr_mat.dot(weight)
	coord_expr_mat_enhanced_array = coord_expr_mat_enhanced.toarray()
	return(coord_expr_mat_enhanced_array)

def pearson_corr(x_array, y_array):
	xmean = x_array.mean(axis = 0)
	ymean = y_array.mean(axis = 0)
	xm = x_array - xmean
	ym = y_array - ymean
	normxm = np.linalg.norm(xm, axis = 0)
	normym = np.linalg.norm(ym, axis = 0)
	x_normalized = xm/normxm
	y_normalized = ym/normym
	r = x_normalized.T @ y_normalized
	return(r)

def pearson_corr_sparse(x_array, y_array):
	xmean = x_array.mean(axis = 0)
	ymean = y_array.mean(axis = 0)
	xm = x_array - xmean
	ym = y_array - ymean
	xm = sparse.csc_matrix(xm)
	ym = sparse.csc_matrix(ym)
	normxm = sparse.linalg.norm(xm, axis = 0)
	normym = sparse.linalg.norm(ym, axis = 0)
	r = np.dot((xm/normxm).T, ym/normym)
	return(r)

def slice_coord(coord_df, span_length, overlap_length, x_colname = "x", y_colname = "y"):
	xmin = coord_df[x_colname].min()
	xmax = coord_df[x_colname].max()
	ymin = coord_df[y_colname].min()
	ymax = coord_df[y_colname].max()
	i = xmin
	coord_sliced_list = []
	while i + span_length <= xmax:
		xmin_sliced = i
		xmax_sliced = i + span_length
		j = ymin
		while j + span_length <= ymax:
			ymin_sliced = j
			ymax_sliced = j + span_length
			coord_sliced_list.append((xmin_sliced, xmax_sliced, ymin_sliced, ymax_sliced))
			j = j + span_length - overlap_length
		ymin_sliced = j
		ymax_sliced = ymax
		coord_sliced_list.append((xmin_sliced, xmax_sliced, ymin_sliced, ymax_sliced))
		i = i + span_length - overlap_length
	xmin_sliced = i
	xmax_sliced = xmax + 1
	j = ymin
	while j + span_length <= ymax:
		ymin_sliced = j
		ymax_sliced = j + span_length
		coord_sliced_list.append((xmin_sliced, xmax_sliced, ymin_sliced, ymax_sliced))
		j = j + span_length - overlap_length
	ymin_sliced = j
	ymax_sliced = ymax + 1
	coord_sliced_list.append((xmin_sliced, xmax_sliced, ymin_sliced, ymax_sliced))
	return(coord_sliced_list)

def filter_mat(all_count_mat, all_count_genes, all_count_spots, sub_spots = None, gene_pct = 0.05):
	if sub_spots:
		sub_expr, sub_gene, sub_spot = sub_mat(mat = all_count_mat, 
											   genes = all_count_genes, 
											   cells = all_count_spots, 
											   cells_sub = sub_spots)
	else:
		sub_expr, sub_gene, sub_spot = all_count_mat, all_count_genes, all_count_spots
	sub_gene_inspot = sub_expr.sum(axis = 1)
	nSpot = np.quantile(np.array(sub_gene_inspot.flatten())[0], (1 - gene_pct))
	sub_gene_over = np.array(sub_gene)[np.array((sub_gene_inspot > nSpot).flatten())[0]]
	sub_expr_over, sub_gene_over_list, sub_spot_over = sub_mat(mat = sub_expr, 
															   genes = sub_gene, 
															   cells = sub_spot, 
															   genes_sub = sub_gene_over.tolist())
	sub_spot_ngene = sub_expr.sum(axis = 0)
	sub_spot_over0 = np.array(sub_spot_over)[np.array((sub_spot_ngene > 0).flatten())[0]]
	sub_expr_over0, sub_gene_over_list0, sub_spot_over0_list = sub_mat(mat = sub_expr_over, 
															   genes = sub_gene_over_list, 
															   cells = sub_spot_over, 
															   cells_sub = sub_spot_over0.tolist())
	return(sub_expr_over0, sub_gene_over_list0, sub_spot_over0_list)

def get_hvg(all_count_mat, all_count_genes, all_count_spots, n_top_genes):
	all_count_ad = ad.AnnData(
		all_count_mat.T,
		obs=pd.DataFrame(index=all_count_spots),
		var=pd.DataFrame(index=all_count_genes),
	)
	# sc.pp.filter_cells(all_count_ad, min_genes=200)
	# sc.pp.filter_genes(all_count_ad, min_cells=3)
	# sc.pp.normalize_total(all_count_ad, target_sum=1e4)
	# sc.pp.log1p(all_count_ad)
	sc.pp.highly_variable_genes(all_count_ad, n_top_genes=n_top_genes, flavor='seurat_v3', span=1.0)
	hvg = all_count_ad.var[all_count_ad.var.highly_variable].index.tolist()
	return(hvg)

def get_frequent_gene(all_count_mat, all_count_genes, all_count_spots, gene_pct):
	all_count_mat[all_count_mat > 0] = 1
	gene_inspot = all_count_mat.sum(axis = 1)
	nSpot = np.quantile(np.array(gene_inspot.flatten())[0], (1 - gene_pct))
	freq_gene = np.array(all_count_genes)[np.array((gene_inspot > nSpot).flatten())[0]]
	return(freq_gene.tolist())

def get_cell_dist(props_df_sub):
	cell_cell_dist = cal_dist(props_df_sub.loc[:,('centroid-0','centroid-1')], 100)[1]
	cell_cell_dist_array = cell_cell_dist.toarray()
	props_df_sub.loc[:, 'min_cell_dist'] = np.amin(cell_cell_dist_array, axis = 1, where = cell_cell_dist_array!=0, initial = 100)
	props_df_sub.loc[:, 'min_cell_dist'] = np.round(props_df_sub['min_cell_dist'], 2)
	cell_cell_dist_median = np.median(props_df_sub['min_cell_dist'])
	max_dist = cell_cell_dist_median/2
	return(max_dist)

def filter_mat_by_var(all_count_mat, all_count_genes, all_count_spots, sub_spots = None):
	if sub_spots:
		sub_expr, sub_gene, sub_spot = sub_mat(mat = all_count_mat, 
											   genes = all_count_genes, 
											   cells = all_count_spots, 
											   cells_sub = sub_spots)
	else:
		sub_expr, sub_gene, sub_spot = all_count_mat, all_count_genes, all_count_spots
	all_count_ad = ad.AnnData(
		all_count_mat.T,
		obs=pd.DataFrame(index=all_count_spots),
		var=pd.DataFrame(index=all_count_genes),
	)
	sc.pp.highly_variable_genes(all_count_ad, n_top_genes=2000, flavor='seurat_v3', span=1.0)
	selected_gene = all_count_ad.var[all_count_ad.var.highly_variable].index
	sub_expr_over, sub_gene_over_list, sub_spot_over = sub_mat(mat = sub_expr, 
															   genes = sub_gene, 
															   cells = sub_spot, 
															   genes_sub = selected_gene.tolist())
	sub_spot_ngene = sub_expr_over.sum(axis = 0)
	sub_spot_over0 = np.array(sub_spot_over)[np.array((sub_spot_ngene > 0).flatten())[0]]
	sub_expr_over0, sub_gene_over_list0, sub_spot_over0_list = sub_mat(mat = sub_expr_over, 
															   genes = sub_gene_over_list, 
															   cells = sub_spot_over, 
															   cells_sub = sub_spot_over0.tolist())
	return(sub_expr_over0, sub_gene_over_list0, sub_spot_over0_list)

def cal_corr_within_seg(count_df_sub, seg_res, count_name = 'MIDCount', genes_list = None):
	count_df_sub_in = count_df_sub[count_df_sub[seg_res].notna()]
	count_df_sub_in_1 = count_df_sub[count_df_sub['Random_divide'] == 1]
	count_df_sub_in_2 = count_df_sub[count_df_sub['Random_divide'] == 2]
	gene_seg_cell_1 = count_df_sub_in_1[count_name].groupby([count_df_sub_in_1[seg_res], count_df_sub_in_1['geneID']]).sum()
	seg_count_mat_1, seg_count_genes_1, seg_count_cells_1 = longdf_to_mat(gene_seg_cell_1)
	gene_seg_cell_2 = count_df_sub_in_2[count_name].groupby([count_df_sub_in_2[seg_res], count_df_sub_in_2['geneID']]).sum()
	seg_count_mat_2, seg_count_genes_2, seg_count_cells_2 = longdf_to_mat(gene_seg_cell_2)
	if genes_list:
		genes_overlap = list((set(genes_list) & set(seg_count_genes_1)) & set(seg_count_genes_2))
	else:
		genes_overlap = list(set(seg_count_genes_1) & set(seg_count_genes_2))
	cells_overlap = list(set(seg_count_cells_1) & set(seg_count_cells_2))
	seg_count_mat_1_overlap, seg_count_gene_1_overlap, seg_count_cell_1_overlap = sub_mat(mat = seg_count_mat_1, 
								   genes = seg_count_genes_1, 
								   cells = seg_count_cells_1, 
								   cells_sub = cells_overlap, 
								   genes_sub = genes_overlap)
	seg_count_mat_2_overlap, seg_count_gene_2_overlap, seg_count_cell_2_overlap = sub_mat(mat = seg_count_mat_2, 
								   genes = seg_count_genes_2, 
								   cells = seg_count_cells_2, 
								   cells_sub = cells_overlap, 
								   genes_sub = genes_overlap)
	corr_random = pearson_corr(seg_count_mat_1_overlap.toarray(), seg_count_mat_2_overlap.toarray()).diagonal()
	return(corr_random, seg_count_cell_1_overlap)

def cal_corr_within_seg_nucleus(count_df_sub, seg_res, genes_list, count_name = 'MIDCount'):
	count_df_sub_in = count_df_sub[count_df_sub[seg_res].notna()]
	count_df_sub_in_1 = count_df_sub_in[count_df_sub_in['Nucleus'] == 0]
	count_df_sub_in_2 = count_df_sub_in[count_df_sub_in['Nucleus'] == 1]
	gene_seg_cell_1 = count_df_sub_in_1[count_name].groupby([count_df_sub_in_1[seg_res], count_df_sub_in_1['geneID']]).sum()
	seg_count_mat_1, seg_count_genes_1, seg_count_cells_1 = longdf_to_mat(gene_seg_cell_1)
	gene_seg_cell_2 = count_df_sub_in_2[count_name].groupby([count_df_sub_in_2[seg_res], count_df_sub_in_2['geneID']]).sum()
	seg_count_mat_2, seg_count_genes_2, seg_count_cells_2 = longdf_to_mat(gene_seg_cell_2)
	genes_overlap = list((set(genes_list) & set(seg_count_genes_1)) & set(seg_count_genes_2))
	cells_overlap = list(set(seg_count_cells_1) & set(seg_count_cells_2))
	seg_count_mat_1_overlap, seg_count_gene_1_overlap, seg_count_cell_1_overlap = sub_mat(mat = seg_count_mat_1, 
	                               genes = seg_count_genes_1, 
	                               cells = seg_count_cells_1, 
	                               cells_sub = cells_overlap, 
	                               genes_sub = genes_overlap)
	seg_count_mat_2_overlap, seg_count_gene_2_overlap, seg_count_cell_2_overlap = sub_mat(mat = seg_count_mat_2, 
	                               genes = seg_count_genes_2, 
	                               cells = seg_count_cells_2, 
	                               cells_sub = cells_overlap, 
	                               genes_sub = genes_overlap)
	corr_random = pearson_corr(seg_count_mat_1_overlap, seg_count_mat_2_overlap).A.diagonal()
	return((corr_random, seg_count_cell_2_overlap))

def cal_corr_between_seg(count_df_sub, seg_res_1, seg_res_2, count_name = 'MIDCount', genes_list = None):
	count_df_sub_overlap = count_df_sub.loc[count_df_sub[seg_res_1] == count_df_sub[seg_res_2], :]
	count_df_sub_nonoverlap = count_df_sub.loc[count_df_sub[seg_res_1] != count_df_sub[seg_res_2], :]
	# overlap
	count_df_sub_overlap = count_df_sub_overlap[count_df_sub_overlap[seg_res_1].notna()]
	gene_seg_cell_overlap = count_df_sub_overlap[count_name].groupby([count_df_sub_overlap[seg_res_1], count_df_sub_overlap['geneID']]).sum()
	seg_count_mat_overlap, seg_count_genes_overlap, seg_count_cells_overlap = longdf_to_mat(gene_seg_cell_overlap)
	# segmentation 1
	count_df_sub_nonoverlap_1 = count_df_sub_nonoverlap[count_df_sub_nonoverlap[seg_res_1].notna()]
	gene_seg_cell_1 = count_df_sub_nonoverlap_1[count_name].groupby([count_df_sub_nonoverlap_1[seg_res_1], count_df_sub_nonoverlap_1['geneID']]).sum()
	seg_count_mat_1, seg_count_genes_1, seg_count_cells_1 = longdf_to_mat(gene_seg_cell_1)
	# segmentation 2
	count_df_sub_nonoverlap_2 = count_df_sub_nonoverlap[count_df_sub_nonoverlap[seg_res_2].notna()]
	gene_seg_cell_2 = count_df_sub_nonoverlap_2[count_name].groupby([count_df_sub_nonoverlap_2[seg_res_2], count_df_sub_nonoverlap_2['geneID']]).sum()
	seg_count_mat_2, seg_count_genes_2, seg_count_cells_2 = longdf_to_mat(gene_seg_cell_2)
	# determine cells and genes to use
	cells_overlap = sorted(np.intersect1d(np.intersect1d(seg_count_cells_overlap, seg_count_cells_1), seg_count_cells_2).tolist())
	genes_overlap = sorted(np.intersect1d(np.intersect1d(seg_count_genes_overlap, seg_count_genes_1), seg_count_genes_2).tolist())
	if genes_list:
		genes_use = sorted(np.intersect1d(genes_overlap, np.array(genes_list)).tolist())
	else:
		genes_use = genes_overlap
	seg_count_mat_overlap_use, seg_count_genes_overlap_use, seg_count_cells_overlap_use = sub_mat(
											  mat = seg_count_mat_overlap, 
											  genes = seg_count_genes_overlap, 
											  cells = seg_count_cells_overlap, 
											  cells_sub = cells_overlap, 
											  genes_sub = genes_use)
	seg_count_mat_1_use, seg_count_genes_1_use, seg_count_cells_1_use = sub_mat(
											  mat = seg_count_mat_1, 
											  genes = seg_count_genes_1, 
											  cells = seg_count_cells_1, 
											  cells_sub = cells_overlap, 
											  genes_sub = genes_use)
	seg_count_mat_2_use, seg_count_genes_2_use, seg_count_cells_2_use = sub_mat(
											  mat = seg_count_mat_2, 
											  genes = seg_count_genes_2, 
											  cells = seg_count_cells_2, 
											  cells_sub = cells_overlap, 
											  genes_sub = genes_use)
	corr_1 = pearson_corr(seg_count_mat_overlap_use, seg_count_mat_1_use).A.diagonal()
	corr_2 = pearson_corr(seg_count_mat_overlap_use, seg_count_mat_2_use).A.diagonal()
	return((corr_1, corr_2, seg_count_cells_2_use))

def KL_divergence(X, Y):
	X = X + 0.01
	Y = Y + 0.01
	X = X/X.sum(axis=1, keepdims=True)
	Y = Y/Y.sum(axis=1, keepdims=True)
	log_X = np.log(X)
	log_Y = np.log(Y)
	X_log_X = np.matrix((X*log_X).sum(axis = 1))
	D = X_log_X.T - np.dot(X,log_Y.T)
	return np.asarray(D)

def KL_divergence_rm0(X, Y):
	d_list = []
	for x_idx in range(X.shape[0]):
		d_x_list = []
		for y_idx in range(Y.shape[0]):
			x = X[x_idx, :]
			y = Y[y_idx, :]
			gene_union = np.union1d(np.where(x !=0), np.where(y !=0))
			x = x[gene_union]
			y = y[gene_union]
			x = x + 0.01
			y = y + 0.01
			x = x/x.sum()
			y = y/y.sum()
			log_x = np.log(x)
			log_y = np.log(y)
			x_log_x = (x*log_x).sum()
			d = x_log_x.T - np.dot(x,log_y.T)
			d_x_list.append(d)
		d_list.append(d_x_list)
	D = np.array(d_list)
	return(D)

def get_cell_mat(count_df_seg, seg_res, count_name = "MIDCount"):
	count_df_seg = count_df_seg.dropna(subset = [seg_res])
	gene_cell = count_df_seg[count_name].groupby([count_df_seg[seg_res], count_df_seg['geneID']]).sum()
	expr_mat, gene_list, cell_list = longdf_to_mat(gene_cell)
	return(expr_mat, gene_list, cell_list)

def split_cell_with_line(coord_df_sub_cell, seg_res):
    """
    Splits a cell by a randomly oriented line and assigns labels based on projections.
    
    Parameters:
    - coord_df_sub_cell (pd.DataFrame): Subset DataFrame containing coordinates of a single cell.
    - seg_res (str): Column name representing the segmentation result.
    
    Returns:
    - pd.DataFrame: Modified DataFrame with a new 'Random_{seg_res}' column.
    """
    # Calculate the center point
    cx, cy = coord_df_sub_cell[['x', 'y']].mean()
    
    # Generate a random angle for the line
    line_angle = np.random.uniform(0, np.pi)
    line_normal = np.array([np.cos(line_angle), np.sin(line_angle)])
    
    # Calculate projections of points onto the line
    points_centered = coord_df_sub_cell[['x', 'y']].to_numpy() - np.array([cx, cy])
    projections = points_centered @ line_normal  # Using matrix multiplication for efficiency
    
    # Assign labels based on projection values
    coord_df_sub_cell = coord_df_sub_cell.copy()
    coord_df_sub_cell[f'Random_{seg_res}'] = np.where(projections >= 0, 2, 1)
    
    return coord_df_sub_cell

def split_cells_with_line(coord_df, seg_res, num_workers=16):
    """
    Splits multiple cells by randomly oriented lines in parallel.
    
    Parameters:
    - coord_df (pd.DataFrame): Main DataFrame containing all cell coordinates.
    - seg_res (str): Column name representing the segmentation result.
    - num_workers (int): Number of parallel processes to use.
    
    Returns:
    - pd.DataFrame: Concatenated DataFrame with new 'Random_{seg_res}' columns.
    """
    # Get a list of unique cell IDs
    cell_list = coord_df[seg_res].unique()
    
    # Use map instead of submit and wait for better efficiency and simplified code
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Use a lambda to pass each cell_id and process it in parallel
        # This approach reduces data transmission by processing subsets efficiently
        results = list(executor.map(
            lambda cell_id: split_cell_with_line(
                coord_df.loc[coord_df[seg_res] == cell_id].copy(),
                seg_res
            ),
            cell_list
        ))
    
    # Concatenate all resulting DataFrames into one
    coord_df_merge = pd.concat(results, axis=0, ignore_index=True)
    return coord_df_merge

def split_cell_with_line(coord_df_sub_cell, seg_res):
	print(coord_df_sub_cell[seg_res].unique())
	cx, cy = coord_df_sub_cell.loc[:,['x', 'y']].mean()
	# generate the angle of the line randomly
	line_angle = np.random.uniform(0, np.pi)
	line_normal = np.array([np.cos(line_angle), np.sin(line_angle)])
	# calculate the the projection from point to line
	points_centered = coord_df_sub_cell.loc[:,['x', 'y']] - np.array([cx, cy])
	projections = np.dot(points_centered, line_normal)
	coord_df_sub_cell['Random_%s' %seg_res] = 1
	coord_df_sub_cell.loc[projections >= 0, 'Random_%s' %seg_res] = 2
	return coord_df_sub_cell

def split_cells_with_line(coord_df, seg_res):
	cell_list = coord_df[seg_res].unique()
	res_list = []
	with concurrent.futures.ProcessPoolExecutor(max_workers = 16) as executor:
		for cell_id in cell_list:
			coord_df_sub_cell = coord_df.loc[coord_df[seg_res] == cell_id, ]
			arg_tuple = (coord_df_sub_cell, seg_res)
			res_list.append(executor.submit(split_cell_with_line, *arg_tuple))
	done, not_done = concurrent.futures.wait(res_list, timeout=None)
	coord_df_list = [future.result() for future in done]
	coord_df_merge = pd.concat(coord_df_list, axis = 0, ignore_index = True)
	return(coord_df_merge)

def cal_corr_within_seg_line(count_df_sub, seg_res, count_name = 'MIDCount', genes_list = None):
	count_df_sub_in_1 = count_df_sub[count_df_sub['Random_%s' %seg_res] == 1]
	count_df_sub_in_2 = count_df_sub[count_df_sub['Random_%s' %seg_res] == 2]
	gene_seg_cell_1 = count_df_sub_in_1[count_name].groupby([count_df_sub_in_1[seg_res], count_df_sub_in_1['geneID']]).sum()
	seg_count_mat_1, seg_count_genes_1, seg_count_cells_1 = longdf_to_mat(gene_seg_cell_1)
	gene_seg_cell_2 = count_df_sub_in_2[count_name].groupby([count_df_sub_in_2[seg_res], count_df_sub_in_2['geneID']]).sum()
	seg_count_mat_2, seg_count_genes_2, seg_count_cells_2 = longdf_to_mat(gene_seg_cell_2)
	if genes_list:
		genes_overlap = list((set(genes_list) & set(seg_count_genes_1)) & set(seg_count_genes_2))
	else:
		genes_overlap = list(set(seg_count_genes_1) & set(seg_count_genes_2))
	cells_overlap = list(set(seg_count_cells_1) & set(seg_count_cells_2))
	seg_count_mat_1_overlap, seg_count_gene_1_overlap, seg_count_cell_1_overlap = sub_mat(mat = seg_count_mat_1, 
								   genes = seg_count_genes_1, 
								   cells = seg_count_cells_1, 
								   cells_sub = cells_overlap, 
								   genes_sub = genes_overlap)
	seg_count_mat_2_overlap, seg_count_gene_2_overlap, seg_count_cell_2_overlap = sub_mat(mat = seg_count_mat_2, 
								   genes = seg_count_genes_2, 
								   cells = seg_count_cells_2, 
								   cells_sub = cells_overlap, 
								   genes_sub = genes_overlap)
	corr_random = pearson_corr(seg_count_mat_1_overlap, seg_count_mat_2_overlap).A.diagonal()
	return(corr_random, seg_count_cell_1_overlap)


