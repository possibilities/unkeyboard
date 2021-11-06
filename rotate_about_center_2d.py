import math


def rotate_2d(origin, point, angle):
    angle_radian = math.radians(angle)
    [origin_x, origin_y] = origin
    [point_x, point_y] = point

    rotated_x = (
        origin_x
        + math.cos(angle_radian) * (point_x - origin_x)
        - math.sin(angle_radian) * (point_y - origin_y)
    )
    rotated_y = (
        origin_y
        + math.sin(angle_radian) * (point_x - origin_x)
        + math.cos(angle_radian) * (point_y - origin_y)
    )
    return (rotated_x, rotated_y)


def rotate_about_center_2d(key, angle):
    return rotate_2d((0, 0), key, angle)
