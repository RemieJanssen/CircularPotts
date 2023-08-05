from shapely import Polygon, LinearRing
import math
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation


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

def animate_points(points_sequence, out_file='polygon.mp4'):
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

def main():
    points = generate_circular_points(100, 1)
    points_sequence = [points]

    area_target = area(points)
    perimeter_target = perimeter(points)
    area_weight = 1
    perimeter_weight = 1
    temperature = .1
    out_file = 'polygon.mp4'

    for i in range(1000):
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

    animate_points(points_sequence, out_file=out_file)




if __name__ == "__main__":
    main()
