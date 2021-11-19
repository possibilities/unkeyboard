import math


def calculate_point_for_angle(vertice, distance, angel):
    angle_radian = math.pi / 2 - math.radians(angel)
    return (
        vertice[0] + distance * math.cos(angle_radian),
        vertice[1] + distance * math.sin(angle_radian),
    )
