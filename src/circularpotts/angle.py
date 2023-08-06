import numpy as np
import math


def angle(p1, p2, p3):
    """
    Returns the angle between the lines p1p2 and p2p3.
    """
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)
    v1 = p1 - p2
    v2 = p3 - p2
    return np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


def squared_sum_of_angles(points):
    """
    Returns the sum of the squared angles of a polygon.
    """
    all_triples = [
        (points[i - 2], points[i - 1], points[i]) for i in range(len(points))
    ]
    angles = [angle(*triple) for triple in all_triples]
    return sum([(angle / math.pi - 1) ** 2 for angle in angles]) / len(points)


def delta_squared_sum_of_angles(points, i, new_point):
    """
    Returns the change in the sum of the squared angles of a polygon from moving the ith point to new_point.
    """
    point_i_minus_two = points[i - 2]
    point_i_minus_one = points[i - 1]
    point_i_plus_one = points[(i + 1) % len(points)]
    point_i_plus_two = points[(i + 2) % len(points)]

    previous_points = [
        point_i_minus_two,
        point_i_minus_one,
        points[i],
        point_i_plus_one,
        point_i_plus_two,
    ]
    previous_point_triples = [
        (point_i_minus_two, point_i_minus_one, points[i]),
        (point_i_minus_one, points[i], point_i_plus_one),
        (points[i], point_i_plus_one, point_i_plus_two),
    ]
    previous_angles = [angle(*triple) for triple in previous_point_triples]

    new_points = [
        point_i_minus_two,
        point_i_minus_one,
        new_point,
        point_i_plus_one,
        point_i_plus_two,
    ]
    new_point_triples = [
        (point_i_minus_two, point_i_minus_one, new_point),
        (point_i_minus_one, new_point, point_i_plus_one),
        (new_point, point_i_plus_one, point_i_plus_two),
    ]
    new_angles = [angle(*triple) for triple in new_point_triples]

    previous_sum = sum([(angle / math.pi - 1) ** 2 for angle in previous_angles])
    new_sum = sum([(angle / math.pi - 1) ** 2 for angle in new_angles])

    return (new_sum - previous_sum) / 3
