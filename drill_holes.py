import cadquery as cq


def drill_holes(self, size, rotation_angle, is_bottom=False, is_top=False):
    screw_size = 1.75
    screw_head_size = 1.85
    screw_head_height = 1

    def select_hole_positions(box):
        return (
            box.faces("<Z" if is_bottom else ">Z")
            .wires(cq.selectors.AreaNthSelector(-1))
            .toPending()
            .offset2D(
                (-size / 2) - (screw_head_size / 2),
                "intersection",
                forConstruction=True,
            )
            .vertices(
                "<X or >X" if rotation_angle == 0 else "<X or >X or >XY or >Y"
            )
        )

    if is_top:
        self = (
            select_hole_positions(self)
            .circle(screw_size)
            .cutBlind(-screw_head_height)
        )

    if is_bottom:
        self = (
            select_hole_positions(self)
            .polygon(6, screw_size * 2)
            .cutBlind(screw_head_height)
        )

    return select_hole_positions(self).circle(screw_size / 2).cutThruAll()
