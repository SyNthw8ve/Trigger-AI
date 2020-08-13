import random

centers = [(1, 1), (10, 10), (50, 0), (0, 50), (25, 25), (100, 0), (30, 70)]
max_points = 5
min_points = 1
max_offset = 5
points = []

for (x, y) in centers:
    for i in range(random.randint(min_points, max_points)):
        offset_point_x = random.randint(0, max_offset)
        offset_point_y = random.randint(0, max_offset)
        points.append((x + offset_point_x, y + offset_point_y))

print(points)