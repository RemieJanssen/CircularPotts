from shapely import Polygon, LinearRing
import math
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from stl import mesh
from mpl_toolkits import mplot3d
import numpy as np


def perimeter(points):
    polygon = Polygon(points)
    return polygon.length

def area(points):
    polygon = Polygon(points)
    return polygon.area

def generate_circular_points(n, radius):
    points = []
    for i in range(n):
        points.append((radius * math.cos(2 * math.pi * i / n), radius * math.sin(2 * math.pi * i / n)))
    return points

def jiggle_point(point, radius):
    x, y = point
    return (x + random.uniform(-radius, radius), y + random.uniform(-radius, radius))

def Hamiltonian(points, perimeter_weight, perimeter_target, area_weight, area_target):
    if not LinearRing(points).is_simple:
        return float('inf')
    return perimeter_weight * (perimeter(points) - perimeter_target) ** 2 + area_weight * (area(points) - area_target) ** 2

def accept_move(H_old, H_new, T):
    if H_new < H_old:
        return True
    else:
        return random.uniform(0, 1) < math.exp(-(H_new - H_old) / T)

def animate_points(points_sequence, out_file='output/polygon.mp4'):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.set_title('Polygon')
    line, = ax.plot([], [], 'o-')
    def init():
        line.set_data([], [])
        return line,
    def animate(i):
        x = [point[0] for point in points_sequence[i]]
        y = [point[1] for point in points_sequence[i]]
        line.set_data(x, y)
        return line,
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(points_sequence), interval=20, blit=True)
    anim.save(out_file, fps=30, extra_args=['-vcodec', 'libx264'])

def animate_points_as_polygon(points_sequence, out_file='output/polygon.mp4'):
    """
    Makes an animation of the polygon as it evolves over time.
    Uses matplotlib fill to create a filled polygon in each frame.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.set_title('Polygon')
    polygon = plt.Polygon(points_sequence[0], fill=True)
    ax.add_patch(polygon)
    def init():
        polygon.set_xy([(0,0)])
        return polygon,
    def animate(i):
        polygon.set_xy(points_sequence[i])
        return polygon,
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(points_sequence), interval=20, blit=True)
    anim.save(out_file, fps=30, extra_args=['-vcodec', 'libx264'])

def points_sequence_to_3d_plot(points_sequence, outfile='output/polygon3.stl'):
    """
    Converts a sequence of 2d polygons to a 3d polygon, where the z coordinate is the index of the point in the sequence.
    Output format is 3d printable file in STL format.
    """
    # Create the mesh
    vertices = np.array(points_sequence)
    faces = np.array([range(len(points_sequence))])
    # Create the mesh
    mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            mesh.vectors[i][j] = vertices[f[j],:]
    # Write the mesh to file
    mesh.save(outfile)




def main():
    points = generate_circular_points(100, 1)
    points_sequence = [points]

    area_target = area(points)
    perimeter_target = perimeter(points)
    area_weight = 1
    perimeter_weight = 1
    temperature = .1
    out_file = 'output/polygon4'

    for i in range(100):
        print(i)
        for i, point in enumerate(points):
            point = jiggle_point(point, 0.1)
            points_new = points.copy()
            points_new[i] = point
            H_old = Hamiltonian(points, perimeter_weight, perimeter_target, area_weight, area_target)
            H_new = Hamiltonian(points_new, perimeter_weight, perimeter_target, area_weight, area_target)
            if accept_move(H_old, H_new, temperature):
                points = points_new
        points_sequence.append(points)

    animate_points_as_polygon(points_sequence, out_file=f"{out_file}.mp4")
    points_sequence_to_3d_plot(points_sequence, outfile=f"{out_file}.stl")



if __name__ == "__main__":
    main()
