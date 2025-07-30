import logging

import pandas as pd
import numpy as np

from skimage import measure

logger = logging.getLogger(__name__)


def cellextractor(image, mask):

    props = measure.regionprops(mask.values, intensity_image=image.values)

    minor_axis = [p.minor_axis_length for p in props]
    major_axis = [p.major_axis_length for p in props]
    zeros = np.where(np.array(minor_axis) == 0.00)[0]
    if len(zeros) != 0:
        for zz in range(len(zeros)):
            minor_axis[zeros[zz]] = 1.0e-24
    aspect_ratio = (np.array(major_axis) / np.array(minor_axis)).tolist()

    stats = {
        "xc": [p.centroid[1] for p in props],
        "yc": [p.centroid[0] for p in props],
        "intensity": [sum(p.image_intensity.ravel()) for p in props],
        "area": [p.area for p in props],
        "mean": [p.mean_intensity for p in props],
        "min": [p.min_intensity for p in props],
        "max": [p.max_intensity for p in props],
        "std": [p.std_intensity for p in props],
        "major_axis": major_axis,
        "minor_axis": minor_axis,
        "aspect_ratio": aspect_ratio,
        "eccentricity": [p.eccentricity for p in props],
        "solidity": [p.solidity for p in props],
        "perimeter": [p.perimeter for p in props],
        "extent": [p.extent for p in props],
        "orientation": [p.orientation for p in props],
        "convex_area": [p.convex_area for p in props],
        "equivalent_diameter": [p.equivalent_diameter for p in props],
        "euler_number": [p.euler_number for p in props],
        "filled_area": [p.filled_area for p in props],
    }

    df = pd.DataFrame(
        stats, index=pd.RangeIndex(start=1, stop=len(props) + 1, name="label")
    )
    return df
