def mirror_over_y_axis(point, mirror_at_point):
    offset = point[0] - mirror_at_point[0]
    return (mirror_at_point[0] - offset, point[1])


def mirror_over_x_axis(point, mirror_at_point):
    offset = point[1] - mirror_at_point[1]
    return (point[0], mirror_at_point[1] - offset)


def mirror_point(point, mirror_at_point, axis="Y"):
    return (
        mirror_over_y_axis(point, mirror_at_point)
        if axis == "Y"
        else mirror_over_x_axis(point, mirror_at_point)
    )
