import pandas as pd
import json
from scipy.ndimage import convolve


def get_reference_space(annotation_grid_path, structure_graph_path, resolution=100):
    if isinstance(resolution, int):
        resolution = [resolution, resolution, resolution]

    import nrrd
    from allensdk.core.structure_tree import StructureTree
    from allensdk.core.reference_space import ReferenceSpace

    annotation, meta = nrrd.read(annotation_grid_path)
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


def get_region_image(region, ref_space, tree, cemba_region_df):
    region_coronal = 2100 + int(region[0]) * 600
    mask = get_cemba_region_mask(region, ref_space, tree, cemba_region_df)
    coronal_img = ref_space.get_slice_image(0, region_coronal)
    img = mask[int(region_coronal / ref_space.resolution[0]), :, :][:, :, None] * coronal_img
    return img


def get_cemba_region_mask(region_ids, ref_space, tree, cemba_region_df):
    if isinstance(region_ids, str):
        region_ids = [region_ids]
    regions = ','.join(cemba_region_df.loc[region_ids]['Region'].tolist())
    regions_id_list = [i['id'] for i in tree.get_structures_by_acronym(regions.split(','))]
    mask = ref_space.make_structure_mask(regions_id_list)
    return mask


