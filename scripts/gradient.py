import random
from scipy.spatial.distance import euclidean as distance
from pprint import pprint

def step(v, direction, step_size):
    return [v_i + step_size * direction_i for v_i, direction_i in zip(v, direction)]


def sum_of_squares_gradient(v):
    return [2 * v_i for v_i in v]

v = [random.randint(-10,10) for i in range(3)]

tolerance = 0.0001

while True:
    gradient = sum_of_squares_gradient(v)
    next_v = step(v, gradient, -0.01)

    if distance(next_v, v) < tolerance:
        break
    v = next_v


pprint(v)
