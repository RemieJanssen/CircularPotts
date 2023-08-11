from shapely import Polygon
import numpy as np


def distance(p1, p2):
    """
    Returns the distance between two points.
    """
    p1 = np.array(p1)
    p2 = np.array(p2)
    return np.linalg.norm(p1 - p2)


def perimeter(points):
    polygon = Polygon(points)
    return polygon.length


def delta_perimeter(points, i, new_point):
    """
    Returns the change in perimeter from moving the ith point to new_point.
    """
    point_i_minus_one = points[i - 1]
    point_i_plus_one = points[(i + 1) % len(points)]
    previous_length = distance(point_i_minus_one, points[i]) + distance(
        points[i], point_i_plus_one
    )
    new_length = distance(point_i_minus_one, new_point) + distance(
        new_point, point_i_plus_one
    )
    return new_length - previous_length


def squared_sum_of_length_difference(points, target_length):
    """
    Returns the sum of the squared lengths of a polygon.
    """
    all_pairs = [(points[i - 1], points[i]) for i in range(len(points))]
    lengths = [distance(*pair) for pair in all_pairs]
    return sum([(length - target_length) ** 2 for length in lengths]) / len(points)


def delta_squared_sum_of_length_difference(points, i, new_point, target_length):
    """
    Returns the change in the sum of the squared lengths of a polygon from moving the ith point to new_point.
    """
    point_i_minus_one = points[i - 1]
    point_i_plus_one = points[(i + 1) % len(points)]
    previous_lengths = [
        distance(point_i_minus_one, points[i]),
        distance(points[i], point_i_plus_one),
    ]
    new_lengths = [
        distance(point_i_minus_one, new_point),
        distance(new_point, point_i_plus_one),
    ]
    previous_sum = sum([(length - target_length) ** 2 for length in previous_lengths])
    new_sum = sum([(length - target_length) ** 2 for length in new_lengths])
    return (new_sum - previous_sum) / len(points)

def max_length_deviation(points, target_length):
    """
    Returns the maximum deviation from the target length of a polygon.
    """
    all_pairs = [(points[i - 1], points[i]) for i in range(len(points))]
    lengths = [distance(*pair) for pair in all_pairs]
    return max([abs(length - target_length) for length in lengths])

def delta_max_length_deviation(points, i, new_point, target_length):
    """
    Returns the change in the maximum deviation from the target length of a polygon from moving the ith point to new_point.
    """
    # TODO be smarter by only checking the lengths of the two edges that change
    # all other lengths stay the same, but we do have to take them into account as
    # they affect the maximum deviation
    all_pairs = [(points[i - 1], points[i]) for i in range(len(points))]
    lengths = [distance(*pair) for pair in all_pairs]
    previous_max = max([abs(length - target_length) for length in lengths])
    lengths[i] = distance(points[i - 1], new_point)
    lengths[(i + 1) % len(points)] = distance(new_point, points[(i + 1) % len(points)])
    new_max = max([abs(length - target_length) for length in lengths])
    return new_max - previous_max