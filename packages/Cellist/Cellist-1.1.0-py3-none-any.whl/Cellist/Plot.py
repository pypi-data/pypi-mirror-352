# -*- coding: utf-8 -*-
# @Author: dongqing
# @Date:   2023-10-14 11:57:10
# @Last Modified by:   dongqing
# @Last Modified time: 2025-02-23 16:17:07


import pandas as pd
import numpy as np
from skimage import color
import matplotlib
import matplotlib.pyplot as plt
import os
import h5py
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial']
matplotlib.rcParams["legend.frameon"] = False
matplotlib.rcParams['pdf.fonttype'] = 42

def hex_to_rgb(hex_str):
    rgb = []
    for i in (1, 3, 5):
        decimal = int(hex_str[i:i+2], 16)/255
        rgb.append(decimal)
    return tuple(rgb)

zeileis_28 = [
    "#023fa5", "#7d87b9", "#bec1d4", "#d6bcc0", 
    "#bb7784", "#8e063b", "#4a6fe3", "#8595e1", 
    "#b5bbe3", "#e6afb9", "#e07b91", "#d33f6a", 
    "#11c638", "#8dd593", "#c6dec7", "#ead3c6", 
    "#f0b98d", "#ef9708", "#0fcfc0", "#9cded6", 
    "#d5eae7", "#f3e1eb", "#f6c4e1", "#f79cd4", 
    '#7f7f7f', "#c7c7c7", "#1CE6FF", "#336600",
]
zeileis_28_rgb = [hex_to_rgb(i) for i in zeileis_28]


def draw_segmentation(coord_df_sub, seg_res, out_prefix, out_dir, x = "X_img", y = "Y_img", figsize = (15, 15)):
    seg_color = zeileis_28_rgb
    community_seg = coord_df_sub.pivot(index = x, columns = y, values = seg_res)
    row_to_add = list(set(range(coord_df_sub[x].min(), coord_df_sub[x].max() + 1)) - set(community_seg.index))
    community_seg_row_to_add = pd.DataFrame(np.zeros((len(row_to_add), community_seg.shape[1])), index = row_to_add, columns = community_seg.columns)
    community_seg = pd.concat([community_seg, community_seg_row_to_add])
    community_seg = community_seg.loc[sorted(community_seg.index.tolist()), :]
    col_to_add = list(set(range(coord_df_sub[y].min(), coord_df_sub[y].max() + 1))  - set(community_seg.columns))
    community_seg.loc[:, col_to_add] = np.nan
    community_seg = community_seg.loc[:, sorted(community_seg.columns.tolist())]
    community_seg = community_seg.fillna(0)
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.imshow(color.label2rgb(np.array(community_seg), colors = seg_color, bg_label=0))
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "%s_segmentation_plot.pdf" %out_prefix))

def draw_segmentation_prob(coord_df_sub, col_prob, out_prefix, out_dir, x = "X_img", y = "Y_img", figsize = (16, 15)):
    community_seg = coord_df_sub.pivot(index = x, columns = y, values = col_prob)
    row_to_add = list(set(range(coord_df_sub[x].min(), coord_df_sub[x].max() + 1)) - set(community_seg.index))
    community_seg_row_to_add = pd.DataFrame(np.zeros((len(row_to_add), community_seg.shape[1])), index = row_to_add, columns = community_seg.columns)
    community_seg = pd.concat([community_seg, community_seg_row_to_add])
    community_seg = community_seg.loc[sorted(community_seg.index.tolist()), :]
    col_to_add = list(set(range(coord_df_sub[y].min(), coord_df_sub[y].max() + 1))  - set(community_seg.columns))
    community_seg.loc[:, col_to_add] = np.nan
    community_seg = community_seg.loc[:, sorted(community_seg.columns.tolist())]
    community_seg = community_seg.fillna(0)
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    im = ax.imshow(np.array(community_seg))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    ax.axis('off')
    plt.colorbar(im, cax = cax)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "%s_segmentation_probability_plot.pdf" %out_prefix))


def draw_segmentation_boundary(img_sub, coord_df_sub, seg_res, out_prefix, out_dir, x = "X_img", y = "Y_img", mode = "outer", figsize = (15, 15)):
    seg_color = zeileis_28_rgb
    community_seg = coord_df_sub.pivot(index = x, columns = y, values = seg_res)
    row_to_add = list(set(range(coord_df_sub[x].min(), coord_df_sub[x].max() + 1)) - set(community_seg.index))
    community_seg_row_to_add = community_seg.iloc[range(len(row_to_add)), :]
    community_seg_row_to_add.index = row_to_add
    community_seg_row_to_add.loc[:, :] = 0
    community_seg = pd.concat([community_seg, community_seg_row_to_add], ignore_index=True)
    community_seg = community_seg.loc[sorted(community_seg.index.tolist()), :]
    col_to_add = list(set(range(coord_df_sub[y].min(), coord_df_sub[y].max() + 1))  - set(community_seg.columns))
    community_seg.loc[:, col_to_add] = np.nan
    community_seg = community_seg.loc[:, sorted(community_seg.columns.tolist())]
    community_seg = community_seg.fillna(0)
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.imshow(segmentation.mark_boundaries(img_sub, np.array(community_seg).astype(int), mode = mode ,color = (1,0,0), background = 0))
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "%s_segmentation_boundary_plot.pdf" %out_prefix))
