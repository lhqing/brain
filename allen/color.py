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
