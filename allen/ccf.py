from collections import defaultdict
import pandas as pd
import json
from scipy.ndimage import convolve
import pathlib
import allen
import seaborn as sns
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


def change_background(img, color, current_bg_color=None):
    if current_bg_color is None:
        # guess the background color
        current_bg_color = img[0, 0, :]

    def change_color_helper(value):
        if np.all(value == current_bg_color):
            return color
        else:
            return value

    convert_img = np.apply_along_axis(change_color_helper, axis=2, arr=img)
    return convert_img


def get_region_image(region, ref_space, tree, mask_only=False, bg_color=(255, 255, 255)):
    region_coronal = 2100 + int(region[:-1]) * 600
    mask = get_cemba_region_3d_mask(region, ref_space, tree)
    if mask_only:
        return mask[int(region_coronal / ref_space.resolution[0]), :, :]
    coronal_img = ref_space.get_slice_image(0, region_coronal)
    img = mask[int(region_coronal / ref_space.resolution[0]), :, :][:, :, None] * coronal_img
    if np.any(bg_color != (0, 0, 0)):
        img = change_background(img, bg_color, current_bg_color=(0, 0, 0))
    return img


def get_slice_image(brain_slice, ref_space, bg_color=(255, 255, 255)):
    region_coronal = 2100 + brain_slice * 600
    coronal_img = ref_space.get_slice_image(0, region_coronal)
    if np.any(bg_color != (0, 0, 0)):
        coronal_img = change_background(coronal_img, bg_color, current_bg_color=(0, 0, 0))
    return coronal_img


def get_cemba_region_3d_mask(region_ids, ref_space, tree):
    if isinstance(region_ids, str):
        region_ids = [region_ids]
    regions = ','.join(CEMBA_REGION.loc[region_ids]['Region'].tolist())
    regions_id_list = [i['id'] for i in tree.get_structures_by_acronym(regions.split(','))]
    mask = ref_space.make_structure_mask(regions_id_list)
    return mask


def plot_slice_img(slice_number, ax, resolution, space, tree):
    slice_number = int(slice_number)
    if 0 < slice_number < 19:
        raise ValueError(f'Slice number should be in [1, 18], got {slice_number}.')

    img = get_slice_image(slice_number, space)
    sns.despine(ax=ax, left=True, top=True, bottom=True, right=True)
    major_grid = 500 / resolution
    minor_grid = major_grid / 5

    ax.set_yticks(np.arange(0, img.shape[0], major_grid), minor=False)
    ax.set_yticklabels((np.arange(0, img.shape[0], major_grid) * resolution).astype(int),
                       minor=False)
    ax.set_yticks(np.arange(0, img.shape[0], minor_grid), minor=True)
    ax.set_xticks(np.arange(0, img.shape[1], major_grid), minor=False)
    ax.set_xticklabels((np.arange(0, img.shape[1], major_grid) * resolution).astype(int),
                       minor=False, rotation=45)
    ax.set_xticks(np.arange(0, img.shape[1], minor_grid), minor=True)
    ax.imshow(img)
    ax.grid(which='minor', color='lightgray', linewidth=0.3)
    ax.grid(which='major', color='black', linewidth=1)

    cemba_regions = set()
    # only select regions for this slice
    for regions in CEMBA_REGION[CEMBA_REGION.index.map(
            lambda i: int(i[:-1]) == slice_number)]['Region']:
        for region in regions.split(','):
            cemba_regions.add(region)
    cemba_region_ids = [i['id'] for i in tree.get_structures_by_acronym(list(cemba_regions))]

    slice_annot = space.annotation[int((2100 + 600 * slice_number) / resolution), :, :]
    structure_dict = defaultdict(list)
    for structure in np.unique(slice_annot):
        if structure == 0:
            continue
        if structure in cemba_region_ids:
            structure_dict[structure].append(structure)
        else:
            ancestors = tree.ancestor_ids([structure])[0]
            for ancestor in ancestors:
                if ancestor in cemba_region_ids:
                    structure_dict[ancestor].append(structure)

    for main_structure, structure_list in structure_dict.items():
        ys, xs = np.where(np.isin(slice_annot, structure_list))
        middle_x = int(slice_annot.shape[1] / 2)
        mid_x = np.median(xs[xs >= middle_x])
        if np.isnan(mid_x):
            mid_x = xs
        mid_y = np.median(ys)
        record = (mid_x, mid_y, tree.get_structures_by_id([main_structure])[0]['acronym'])
        ax.text(*record,
                horizontalalignment='center',
                verticalalignment='center')
    return ax
