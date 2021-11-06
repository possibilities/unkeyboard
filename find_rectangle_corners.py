import cadquery as cq


def find_rectangle_corners(point, width, height):
    offset = cq.Vector(*point)
    points = [
        cq.Vector(width / -2.0, height / -2.0, 0),
        cq.Vector(width / 2.0, height / -2.0, 0),
        cq.Vector(width / 2.0, height / 2.0, 0),
        cq.Vector(width / -2.0, height / 2.0, 0),
    ]
    return [((point + offset).x, (point + offset).y) for point in points]
