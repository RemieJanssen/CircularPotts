from shapely import Polygon
import numpy as np

def distance(p1, p2):
    """
    Returns the distance between two points.
    """
    p1 = np.array(p1)
    p2 = np.array(p2)
    return np.linalg.norm(p1-p2)

def perimeter(points):
    polygon = Polygon(points)
    return polygon.length

def delta_perimeter(points, i, new_point):
    """
    Returns the change in perimeter from moving the ith point to new_point.
    """
    point_i_minus_one = points[i-1]
    point_i_plus_one = points[(i+1) % len(points)]
    previous_length = distance(point_i_minus_one, points[i]) + distance(points[i], point_i_plus_one)
    new_length = distance(point_i_minus_one, new_point) + distance(new_point, point_i_plus_one)
    return new_length - previous_length
