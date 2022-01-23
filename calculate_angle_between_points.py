import math


def calculate_angle_between_points(start, end):
    return int(math.degrees(math.atan2(end[1] - start[1], end[0] - start[0])))
