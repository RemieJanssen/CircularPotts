import math
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from stl import mesh
from mpl_toolkits import mplot3d
import numpy as np
import json
import argparse
import os

from circularpotts.hamiltonian import (
    hamiltonian,
    delta_hamiltonian,
    accept_move_delta,
    all_values,
)
from circularpotts.perimeter import perimeter


def generate_circular_points(n, radius):
    points = []
    for i in range(n):
        points.append(
            (
                radius * math.cos(2 * math.pi * i / n),
                radius * math.sin(2 * math.pi * i / n),
            )
        )
    return points


def jiggle_point(point, radius):
    x, y = point
    return (x + random.uniform(-radius, radius), y + random.uniform(-radius, radius))


def animate_points_as_polygon(points_sequence, out_file="output/polygon.mp4"):
    """
    Makes an animation of the polygon as it evolves over time.
    Uses matplotlib fill to create a filled polygon in each frame.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    ax.set_title("Polygon")
    polygon = plt.Polygon(points_sequence[0], fill=True)
    ax.add_patch(polygon)

    def init():
        polygon.set_xy([(0, 0)])
        return (polygon,)

    def animate(i):
        polygon.set_xy(points_sequence[i])
        return (polygon,)

    anim = animation.FuncAnimation(
        fig,
        animate,
        init_func=init,
        frames=len(points_sequence),
        interval=20,
        blit=True,
    )
    anim.save(out_file, fps=30, extra_args=["-vcodec", "libx264"])


def points_sequence_to_3d_mesh(points_sequence, outfile="output/polygon.stl", height=2):
    """
    Converts a sequence of 2d polygons to a 3d polygon, where the z coordinate is the index of the point in the sequence.
    Output format is 3d printable file in STL format.
    """
    # add z coordinate
    points_sequence = [
        [
            (point[0], point[1], height * float(i) / len(points_sequence))
            for point in points
        ]
        for i, points in enumerate(points_sequence)
    ]
    # Create the mesh
    vertices = np.array(points_sequence)
    number_of_squares = (len(points_sequence) - 1) * len(points_sequence[0])
    faces = np.array(range(number_of_squares * 2))
    # Create the mesh
    _mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for polygon_index in range(len(points_sequence) - 1):
        for point_index in range(len(points_sequence[0])):
            i = polygon_index
            j = point_index
            f1 = 2 * (i * len(points_sequence[0]) + j)
            f2 = 2 * (i * len(points_sequence[0]) + j) + 1
            _mesh.vectors[f1][0] = vertices[i][j]
            _mesh.vectors[f1][1] = vertices[i][j - 1]
            _mesh.vectors[f1][2] = vertices[i + 1][j - 1]
            _mesh.vectors[f2][0] = vertices[i][j]
            _mesh.vectors[f2][1] = vertices[i + 1][j - 1]
            _mesh.vectors[f2][2] = vertices[i + 1][j]
    # Write the mesh to file
    _mesh.save(outfile)


def shuffled_enumerate_generator(l):
    """
    Returns a generator that yields the elements of l in random order.
    """
    indices = list(range(len(l)))
    random.shuffle(indices)
    for i in indices:
        yield i, l[i]


def simulate(
    number_of_points,
    steps,
    out_folder,
    area_target=None,
    area_weight=1,
    perimeter_target=1,
    perimeter_weight=1,
    angles_weight=1,
    temperature=0.1,
    jiggle_radius=0.02,
    length_target=None,
    length_weight=1,
    animate=True,
    mesh=True,
):
    points = generate_circular_points(number_of_points, 1)
    length_target = perimeter_target * perimeter(points) / len(points)

    values = all_values(points, length_target=length_target)

    area_target = area_target * values["area"]
    perimeter_target = perimeter_target * values["perimeter"]

    points_sequence = [points]

    for i in range(steps):
        print(i)
        for i, point in shuffled_enumerate_generator(points):
            point = jiggle_point(point, jiggle_radius)
            delta_H, new_values = delta_hamiltonian(
                points,
                i,
                point,
                perimeter_weight,
                perimeter_target,
                values["perimeter"],
                area_weight,
                area_target,
                values["area"],
                angles_weight,
                values["angles"],
                length_weight,
                length_target,
                values["length"],
            )
            if accept_move_delta(delta_H, temperature):
                points_new = points.copy()
                points_new[i] = point
                points = points_new
                values = new_values
        points_sequence.append(points)

    # save points to file
    json.dump(points_sequence, open(os.path.join(out_folder, "points.json"), "w"))
    if animate:
        animate_points_as_polygon(
            points_sequence, out_file=os.path.join(out_folder, "animation.mp4")
        )
    if mesh:
        points_sequence_to_3d_mesh(
            points_sequence, outfile=os.path.join(out_folder, "mesh.stl")
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Run the circular Potts model.")
    parser.add_argument(
        "-n",
        "--number_of_points",
        dest="number_of_points",
        type=int,
        help="number of points in the polygon",
    )
    parser.add_argument(
        "-s",
        "--steps",
        dest="steps",
        type=int,
        help="number of steps to run the simulation for",
    )
    parser.add_argument(
        "-o", "--outfolder", dest="out_folder", type=str, help="output file name"
    )
    parser.add_argument(
        "--animate", action="store_true", help="whether to animate the polygon"
    )
    parser.add_argument(
        "--mesh", action="store_true", help="whether to create a 3d mesh of the polygon"
    )
    parser.add_argument(
        "--area_target",
        type=float,
        help="target area of the polygon as a multiple of the starting area",
        default=1,
    )
    parser.add_argument(
        "--area_weight",
        type=float,
        help="weight of the area term in the Hamiltonian",
        default=0.6,
    )
    parser.add_argument(
        "--perimeter_target",
        type=float,
        help="target perimeter of the polygon as a multiple of the starting perimeter",
        default=2,
    )
    parser.add_argument(
        "--perimeter_weight",
        type=float,
        help="weight of the perimeter term in the Hamiltonian",
        default=0,
    )
    parser.add_argument(
        "--angles_weight",
        type=float,
        help="weight of the angles term in the Hamiltonian",
        default=2000,
    )
    parser.add_argument(
        "--length_target",
        type=float,
        help="target length of the polygon as a multiple of the starting length",
        default=6,
    )
    parser.add_argument(
        "--length_weight",
        type=float,
        help="weight of the length term in the Hamiltonian",
        default=10,
    )
    parser.add_argument(
        "--temperature", type=float, help="temperature of the simulation", default=0.05
    )
    parser.add_argument(
        "--jiggle_radius", type=float, help="radius of the jiggle move", default=0.02
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not os.path.exists(args.out_folder):
        os.makedirs(args.out_folder)
    simulate(
        args.number_of_points,
        args.steps,
        args.out_folder,
        args.area_target,
        args.area_weight,
        args.perimeter_target,
        args.perimeter_weight,
        args.angles_weight,
        args.temperature,
        args.jiggle_radius,
        args.animate,
        args.mesh,
    )


if __name__ == "__main__":
    main()
