import cadquery as cq
from rotate_2d import rotate_2d


def calculate_rectangle_corners(center_point, width, height, angle=0):
    offset = cq.Vector(*center_point)
    vectors = [
        cq.Vector(width / -2.0, height / -2.0, 0),
        cq.Vector(width / 2.0, height / -2.0, 0),
        cq.Vector(width / 2.0, height / 2.0, 0),
        cq.Vector(width / -2.0, height / 2.0, 0),
    ]
    points = [((vector + offset).x, (vector + offset).y) for vector in vectors]
    if angle:
        return [rotate_2d(center_point, point, angle) for point in points]
    return points
