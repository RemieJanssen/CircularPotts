from shapely import Polygon


def area(points):
    polygon = Polygon(points)
    return polygon.area


def delta_area(points, i, new_point):
    """
    Returns the change in area from moving the ith point to new_point.
    """
    point_i_minus_one = points[i - 1]
    point_i_plus_one = points[(i + 1) % len(points)]
    previous_area = Polygon([point_i_minus_one, points[i], point_i_plus_one]).area
    new_area = Polygon([point_i_minus_one, new_point, point_i_plus_one]).area
    return new_area - previous_area
