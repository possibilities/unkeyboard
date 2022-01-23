import math


def calculate_point_for_angle(point, distance, angle):
    angle_radian = math.pi / 2 - math.radians(angle)
    return (
        point[0] + distance * math.cos(angle_radian),
        point[1] + distance * math.sin(angle_radian),
    )
