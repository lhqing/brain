import pandas as pd
import json
from scipy.ndimage import convolve
import pathlib
import allen
import numpy as np

PACKAGE_DIR = pathlib.Path(allen.__path__[0])
CEMBA_REGION = pd.read_table(PACKAGE_DIR / 'data/cemba_region_anno.tsv',
                             index_col=0)


def get_reference_space(resolution=100):
    if isinstance(resolution, int):
        resolution = [resolution, resolution, resolution]

    for r in resolution:
        if r not in [10, 25, 50, 100]:
            raise ValueError(f'Axis resolution must in 10, 25, 50, 100 micron, got {r}.')
    resolution_file = min(resolution)
    annotation_grid_path = PACKAGE_DIR / f'data/ccf2017_annotation_{resolution_file}.nrrd'
    structure_graph_path = PACKAGE_DIR / f'data/StructureGraph_Set1_Adult_Mouse_Brain.json'

    import nrrd
    from allensdk.core.structure_tree import StructureTree
    from allensdk.core.reference_space import ReferenceSpace

    annotation, meta = nrrd.read(str(annotation_grid_path))
    with open(structure_graph_path) as f:
        # This removes some unused fields returned by the query
        structure_graph = json.load(f)
        structure_graph = StructureTree.clean_structures(structure_graph)
        tree = StructureTree(structure_graph)

    rsp = ReferenceSpace(tree, annotation, resolution)
    return rsp, tree


def make_structure_mask_border(structure_id, ref_space):
    mask = ref_space.make_structure_mask(structure_id)
    mask = convolve(mask, np.ones((3, 3, 3)), mode='constant')
    mask = ((mask < 8) & (mask > 1))
    return mask


def get_region_image(region, ref_space, tree, mask_only=False):
    region_coronal = 2100 + int(region[:-1]) * 600
    mask = get_cemba_region_3d_mask(region, ref_space, tree)
    if mask_only:
        return mask[int(region_coronal / ref_space.resolution[0]), :, :]
    coronal_img = ref_space.get_slice_image(0, region_coronal)
    img = mask[int(region_coronal / ref_space.resolution[0]), :, :][:, :, None] * coronal_img
    return img


def get_slice_image(region, ref_space):
    region_coronal = 2100 + int(region[:-1]) * 600
    coronal_img = ref_space.get_slice_image(0, region_coronal)
    return coronal_img


def get_cemba_region_3d_mask(region_ids, ref_space, tree):
    if isinstance(region_ids, str):
        region_ids = [region_ids]
    regions = ','.join(CEMBA_REGION.loc[region_ids]['Region'].tolist())
    regions_id_list = [i['id'] for i in tree.get_structures_by_acronym(regions.split(','))]
    mask = ref_space.make_structure_mask(regions_id_list)
    return mask
