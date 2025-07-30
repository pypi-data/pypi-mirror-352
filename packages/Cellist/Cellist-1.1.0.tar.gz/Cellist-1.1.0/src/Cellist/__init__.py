VERSION = '1.1.0'
import os
import sys
import logging
import argparse as ap

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

from Cellist.version import __version__
from Cellist.Segmentation import CellistParser, Cellist
from Cellist.Registration import AlignmentParser, Alignment
from Cellist.Watershed import WatershedParser, Watershed
from Cellist.Imputation import ImputationParser, Imputation
from Cellist.Cellpose import CellposeParser, Cellpose


def main():
    """
    Add main function argument parsers.
    """
    parser = ap.ArgumentParser(description = "Cellist (Cell identification in high-resolution Spatial Transcriptomics) is a cell segmentation tool for high-resolution spatial transcriptomics. ")
    parser.add_argument("-v", "--version", action = "store_true", help = "Print version info.")

    subparsers = parser.add_subparsers(dest = "subcommand")
    CellistParser(subparsers)
    AlignmentParser(subparsers)
    WatershedParser(subparsers)
    CellposeParser(subparsers)
    ImputationParser(subparsers)

    logging.basicConfig(format="%(levelname)s: %(message)s", stream=sys.stderr)
    args = parser.parse_args()

    version = __version__

    if args.version:
        print(version)
        exit(0)
    elif args.subcommand == "seg":
        platform = args.platform
        resolution = args.resolution
        spot_expr_file = args.spot_expr_file
        all_spot_count_h5_file = args.all_spot_count_h5_file
        nucleus_seg_method = args.nucleus_seg_method
        props_file = args.props_file
        nucleus_count_h5_file = args.nucleus_count_h5_file
        nucleus_coord_file = args.nucleus_coord_file
        patch_data_dir = args.patch_data_dir
        num_workers = args.num_workers
        max_dist = args.max_dist
        neigh_dist = args.neigh_dist
        noise_prop = args.noise_prop
        alpha = args.alpha
        sigma = args.sigma
        beta = args.beta
        gene_use = args.gene_use
        two_step = args.two_step
        cyto = args.cyto
        out_dir = args.out_dir
        out_prefix = args.out_prefix
        max_dist_s1_scale = args.max_dist_s1_scale
        noise_prop_s1 = args.noise_prop_s1
        Cellist(platform = platform, resolution = resolution, nucleus_seg_method = nucleus_seg_method, 
            props_file = props_file, nucleus_count_h5_file = nucleus_count_h5_file, 
            nucleus_coord_file = nucleus_coord_file, all_spot_count_h5_file = all_spot_count_h5_file, 
            spot_expr_file = spot_expr_file, patch_data_dir = patch_data_dir, num_workers = num_workers, 
            alpha = alpha, sigma = sigma, beta = beta, 
            gene_use = gene_use, max_dist = max_dist, 
            two_step = two_step, cyto = cyto, max_dist_s1_scale = max_dist_s1_scale, 
            noise_prop_s1 = noise_prop_s1, noise_prop = noise_prop, neigh_dist = neigh_dist,
            out_dir = out_dir, out_prefix = out_prefix)
    elif args.subcommand == "align":
        gem_path = args.spot_expr_file
        img_path = args.regist_tif_file
        num_workers = args.num_workers
        out_dir = args.out_dir
        out_prefix = args.out_prefix
        Alignment(gem_path = gem_path, img_path = img_path, num_workers = num_workers, 
            out_dir = out_dir, out_prefix = out_prefix)
    elif args.subcommand == "watershed":
        platform = args.platform
        gem_path = args.spot_expr_file
        img_path = args.regist_tif_file
        out_dir = args.out_dir
        out_prefix = args.out_prefix
        min_distance = args.min_distance
        no_local_threshold = args.no_local_threshold
        expansion = args.expansion
        expansion_dist = args.expansion_dist
        Watershed(platform = platform, gem_path = gem_path, img_path = img_path, out_dir = out_dir, out_prefix = out_prefix,
        min_distance = min_distance, no_local_threshold = no_local_threshold, expansion = expansion, expansion_dist = expansion_dist)
    elif args.subcommand == "cellpose":
        platform = args.platform
        gem_path = args.spot_expr_file
        img_path = args.regist_tif_file
        out_dir = args.out_dir
        out_prefix = args.out_prefix
        no_local_threshold = args.no_local_threshold
        diameter = args.diameter
        model_type = args.model_type
        flow_threshold = args.flow_threshold
        cellprob_threshold = args.cellprob_threshold
        expansion = args.expansion
        expansion_dist = args.expansion_dist
        Cellpose(platform = platform, gem_path = gem_path, img_path = img_path, out_dir = out_dir, out_prefix = out_prefix, 
        no_local_threshold = no_local_threshold, diameter = diameter, model_type = model_type, flow_threshold = flow_threshold, cellprob_threshold = cellprob_threshold,
        expansion = expansion, expansion_dist = expansion_dist)
    elif args.subcommand == "impute":
        expr_file = args.expr
        spatial_file = args.spatial
        num_workers = args.num_workers
        out_dir = args.out_dir
        out_prefix = args.out_prefix
        Imputation(expr_file = expr_file, spatial_file = spatial_file, num_workers = num_workers, 
            out_dir = out_dir, out_prefix = out_prefix)
    else:
        parser.print_help()
        exit(1)
    exit(0)

if __name__ == "__main__":
    main()
