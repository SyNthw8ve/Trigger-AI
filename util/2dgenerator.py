import random
import pickle as pk

centers = []
centers_num = 500
max_distance = 600

for i in range(centers_num):

    x = random.randint(-max_distance, max_distance)
    y = random.randint(-max_distance, max_distance)

    centers.append((x, y))

max_points = 100
min_points = 1
max_offset = 3000
points = []

for (x, y) in centers:
    for i in range(random.randint(min_points, max_points)):
        offset_point_x = random.randint(0, max_offset)
        offset_point_y = random.randint(0, max_offset)
        points.append((x + offset_point_x, y + offset_point_y))

with open('../examples/2D_points_no_true/5', 'wb') as f:
    pk.dump(points, f)
