import sys
import random
import pickle as pk

centers = []
centers_num = 100
max_distance = 500

for i in range(centers_num):

    x = random.randint(-max_distance, max_distance)
    y = random.randint(-max_distance, max_distance)

    centers.append((x, y))

max_points = 100
min_points = 10
max_offset = 100
points = []

for c, (x, y) in enumerate(centers):
    for i in range(random.randint(min_points, max_points)):
        offset_point_x = random.randint(0, max_offset)
        offset_point_y = random.randint(0, max_offset)
        points.append((x + offset_point_x, y + offset_point_y, c))


path = sys.argv[1]

with open(path, 'wb') as f:
    pk.dump(points, f)
