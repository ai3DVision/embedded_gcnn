import numpy as np
from skimage.measure import regionprops
from skimage import color
from sklearn.preprocessing import MinMaxScaler


NUM_FORM_FEATURES = 77
NUM_FEATURES = 16


def form_feature_extraction(segmentation, image):
    # We need to increment the segmentation, because labels with value 0 are
    # ignored when calling `regionprops`.
    segmentation += 1

    intensity_image = color.rgb2gray(image)
    props = regionprops(segmentation, intensity_image)

    features = np.zeros((len(props), NUM_FORM_FEATURES), dtype=np.float32)

    for i, prop in enumerate(props):
        area = prop['area']
        min_row, min_col, max_row, max_col = prop['bbox']
        bbox_height = max_row - min_row
        bbox_width = max_col - min_col
        bbox_area = bbox_height * bbox_width
        convex_area = prop['convex_area']
        eccentricity = prop['eccentricity']
        equivalent_diameter = prop['equivalent_diameter']
        extent = prop['extent']
        filled_area = prop['filled_area']
        major_axis_length = prop['major_axis_length']
        minor_axis_length = prop['minor_axis_length']
        orientation = prop['orientation']
        perimeter = prop['perimeter']
        solidity = prop['solidity']  # 14 values
        inertia_tensor = prop['inertia_tensor'].flatten()  # 4 values
        inertia_tensor_eigvals = prop['inertia_tensor_eigvals']  # 2 values
        local_centroid = prop['local_centroid']  # 2 values
        moments = prop['moments'].flatten()  # 16 values
        moments_central = prop['moments_central'].flatten()  # 16 values
        moments_hu = prop['moments_hu']  # 7 values
        weighted_moments = prop['weighted_moments'].flatten()  # 16 values

        feature = [
            area, bbox_height, bbox_width, bbox_area, convex_area,
            eccentricity, equivalent_diameter, extent, filled_area,
            major_axis_length, minor_axis_length, orientation, perimeter,
            solidity
        ]  # bis index 13
        feature.extend(inertia_tensor)  # bis index 17
        feature.extend(inertia_tensor_eigvals)  # bis index 19
        feature.extend(local_centroid)  # bis index 21
        feature.extend(moments)  # bis index 37
        feature.extend(moments_central)  # bis index 53
        feature.extend(moments_hu)  # bis index 60
        feature.extend(weighted_moments)  # bis index 76

        assert len(feature) == NUM_FORM_FEATURES
        features[i] = np.array(feature)

    # Scale linear to [0, 1].
    return MinMaxScaler().fit_transform(features)


def feature_extraction(segmentation, image):
    segmentation += 1
    props = regionprops(segmentation)
    features = np.zeros((len(props), NUM_FEATURES), dtype=np.float32)

    for i, prop in enumerate(props):
        features[i][0] = prop['major_axis_length']  # Id: 9
        features[i][1] = prop['inertia_tensor'].flatten()[2]  # Id: 16
        features[i][2] = prop['inertia_tensor_eigvals'][0]  # Id: 18

        moments_central = prop['moments_central'].flatten()
        features[i][3:8] = moments_central[3:8]  # Id: 41-45
        features[i][8:11] = moments_central[13:16]  # Id: 51-53

        moments_hu = prop['moments_hu']
        features[i][11:13] = moments_hu[4:6]  # Id: 58-59

        # Mean color.
        min_row, min_col, max_row, max_col = prop['bbox']
        sliced_image = image[min_row:max_row, min_col:max_col]
        sliced_image = sliced_image[prop['image']]
        features[i][13] = sliced_image[..., 0].mean()
        features[i][14] = sliced_image[..., 1].mean()
        features[i][15] = sliced_image[..., 2].mean()

    # Scale linear to [0, 1].
    return MinMaxScaler().fit_transform(features)
