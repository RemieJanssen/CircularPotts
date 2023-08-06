from shapely import LinearRing
import math
import random

from circularpotts.perimeter import perimeter, delta_perimeter
from circularpotts.area import area, delta_area
from circularpotts.angle import squared_sum_of_angles, delta_squared_sum_of_angles

def all_values(points):
    return {
        'perimeter': perimeter(points),
        'area': area(points),
        'angles': squared_sum_of_angles(points)
    }

def hamiltonian(points, perimeter_weight, perimeter_target, area_weight, area_target, angles_weight):
    if not LinearRing(points).is_simple:
        return float('inf')
    return (
        perimeter_weight * (perimeter(points) - perimeter_target) ** 2 + 
        area_weight * (area(points) - area_target) ** 2 +
        angles_weight * squared_sum_of_angles(points)
    )

def delta_hamiltonian(points, i, new_point, 
        perimeter_weight, perimeter_target, perimeter_current, 
        area_weight, area_target, area_current,
        angles_weight, angles_current):
    new_points = points.copy()
    new_points[i] = new_point
    if not LinearRing(new_points).is_simple:
        return float('inf'), {'perimeter': 'inf', 'area': 'inf', 'angles': 'inf'}
    delta_values = {
        'perimeter': delta_perimeter(points, i, new_point),
        'area': delta_area(points, i, new_point),
        'angles': delta_squared_sum_of_angles(points, i, new_point)
    }
    new_values = {
        'perimeter': perimeter_current + delta_values['perimeter'],
        'area': area_current + delta_values['area'],
        'angles': angles_current + delta_values['angles']
    }
    return (
        contribution_delta_hamiltonian(perimeter_current, delta_values['perimeter'], perimeter_target, perimeter_weight) +
        contribution_delta_hamiltonian(area_current, delta_values['area'], area_target, area_weight) +
        contribution_delta_hamiltonian(angles_current, delta_values['angles'], 0, angles_weight),
        new_values
    )

def contribution_delta_hamiltonian(current, delta, target, weight):
    return weight * (2 * current * delta + delta ** 2 - 2 * delta * target)

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