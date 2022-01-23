from rotate_2d import rotate_2d


def calculate_rectangle_corners(center_point, width, height, angle=0):
    [offset_x, offset_y] = center_point
    points = [
        (width / -2.0 + offset_x, height / 2.0 + offset_y),
        (width / 2.0 + offset_x, height / 2.0 + offset_y),
        (width / 2.0 + offset_x, height / -2.0 + offset_y),
        (width / -2.0 + offset_x, height / -2.0 + offset_y),
    ]
    if angle:
        return [rotate_2d(center_point, point, angle) for point in points]
    return points
