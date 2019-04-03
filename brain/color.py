import pandas as pd
import pathlib
import brain

PACKAGE_DIR = pathlib.Path(brain.__path__[0])
CEMBA_REGION = pd.read_csv(PACKAGE_DIR / 'data/rs1_paper_region.tsv',
                           index_col=0, sep='\t')
CEMBA_REGION['ID'] = pd.Series(CEMBA_REGION.index.tolist(), index=CEMBA_REGION.index)


def _get_color_map_from_table(key_col, color_col):
    """Get """
    records = {}
    _data = CEMBA_REGION[[key_col, color_col]]
    for _, row in _data.iterrows():
        records[row[key_col]] = row[color_col]
    return records


ID_MAJOR_COLOR_TAB20 = _get_color_map_from_table('ID', 'MajorColor1')
ID_SUB_COLOR_TAB20 = _get_color_map_from_table('ID', 'SubColor1')
ID_MAJOR_COLOR_HLS = _get_color_map_from_table('ID', 'MajorColor2')
ID_SUB_COLOR_HLS = _get_color_map_from_table('ID', 'SubColor2')
MAJOR_REGION_MAJOR_COLOR_TAB20 = _get_color_map_from_table('MajorRegion', 'MajorColor1')
MAJOR_REGION_SUB_COLOR_TAB20 = _get_color_map_from_table('MajorRegion', 'SubColor1')
MAJOR_REGION_MAJOR_COLOR_HLS = _get_color_map_from_table('MajorRegion', 'MajorColor2')
MAJOR_REGION_SUB_COLOR_HLS = _get_color_map_from_table('MajorRegion', 'SubColor2')
SUB_REGION_MAJOR_COLOR_TAB20 = _get_color_map_from_table('SubRegion', 'MajorColor1')
SUB_REGION_SUB_COLOR_TAB20 = _get_color_map_from_table('SubRegion', 'SubColor1')
SUB_REGION_MAJOR_COLOR_HLS = _get_color_map_from_table('SubRegion', 'MajorColor2')
SUB_REGION_SUB_COLOR_HLS = _get_color_map_from_table('SubRegion', 'SubColor2')


def get_alpha_colormap(tree, rois=None, non_roi_alpha=0.25):
    rois = set(rois)
    color_map = tree.get_colormap()
    color_map[0] = (255, 255, 255)
    # add transparent dim
    alpha_color_map = {}
    for k, v in color_map.items():
        if k in rois:
            alpha = 1
        else:
            alpha = non_roi_alpha
        color_with_alpha = tuple([i / 255 for i in v] + [alpha])
        alpha_color_map[k] = color_with_alpha
    return alpha_color_map
