from shapely import LinearRing
import math
import random

from circularpotts.perimeter import (
    perimeter,
    delta_perimeter,
    squared_sum_of_length_difference,
    delta_squared_sum_of_length_difference,
    # max_length_deviation as squared_sum_of_length_difference,
    # delta_max_length_deviation as delta_squared_sum_of_length_difference,
)
from circularpotts.area import area, delta_area
from circularpotts.angle import squared_sum_of_angles, delta_squared_sum_of_angles


def all_values(points, length_target=None):
    return {
        "perimeter": perimeter(points),
        "area": area(points),
        "angles": squared_sum_of_angles(points),
        "length": squared_sum_of_length_difference(points, length_target),
    }


def hamiltonian(
    points,
    perimeter_weight,
    perimeter_target,
    area_weight,
    area_target,
    angles_weight,
    length_weight,
    length_target,
):
    if not LinearRing(points).is_simple:
        return float("inf")
    return (
        area_weight * (area(points) - area_target) ** 2
        + angles_weight * squared_sum_of_angles(points)
        + perimeter_weight * (perimeter(points) - perimeter_target) ** 2
        + length_weight * squared_sum_of_length_difference(points, length_target)
    )


def delta_hamiltonian(
    points,
    i,
    new_point,
    perimeter_weight,
    perimeter_target,
    perimeter_current,
    area_weight,
    area_target,
    area_current,
    angles_weight,
    angles_current,
    length_weight,
    length_target,
    length_current,
):
    new_points = points.copy()
    new_points[i] = new_point
    if not LinearRing(new_points).is_simple:
        return float("inf"), {
            "perimeter": "inf",
            "area": "inf",
            "angles": "inf",
            "length": "inf",
        }
    delta_values = {
        "perimeter": delta_perimeter(points, i, new_point),
        "area": delta_area(points, i, new_point),
        "angles": delta_squared_sum_of_angles(points, i, new_point),
        "length": delta_squared_sum_of_length_difference(
            points, i, new_point, length_target
        ),
    }
    new_values = {
        "perimeter": perimeter_current + delta_values["perimeter"],
        "area": area_current + delta_values["area"],
        "angles": angles_current + delta_values["angles"],
        "length": length_current + delta_values["length"],
    }
    return (
        contribution_delta_hamiltonian(
            perimeter_current,
            delta_values["perimeter"],
            perimeter_target,
            perimeter_weight,
        )
        + contribution_delta_hamiltonian(
            area_current, delta_values["area"], area_target, area_weight
        )
        + contribution_delta_hamiltonian(
            angles_current, delta_values["angles"], 0, angles_weight
        )
        + contribution_delta_hamiltonian(
            length_current, delta_values["length"], length_target, length_weight
        ),
        new_values,
    )


def contribution_delta_hamiltonian(current, delta, target, weight):
    return weight * (2 * current * delta + delta**2 - 2 * delta * target)


def accept_move(H_old, H_new, T):
    if H_new < H_old:
        return True
    else:
        return random.uniform(0, 1) < math.exp(-(H_new - H_old) / T)


def accept_move_delta(delta_H, T):
    if delta_H < 0:
        return True
    else:
        return random.uniform(0, 1) < math.exp(-delta_H / T)
