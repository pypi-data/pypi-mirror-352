import numpy as np

import shapely
from shapely.geometry import Point

def points_in_shape(shape, points: np.ndarray):
    geoms = np.array([Point(point) for point in points])
    return shapely.contains(shape, geoms)