import cadquery as cq


def add_bezel(self, size, thickness):
    if size == 0:
        return self
    return (
        self.tag("layer")
        .faces("<Z", tag="layer")
        .wires(cq.selectors.AreaNthSelector(-1))
        .toPending()
        .offset2D(size, "intersection")
        .faces("<Z", tag="layer")
        .wires(cq.selectors.AreaNthSelector(-1))
        .toPending()
        .extrude(thickness)
    )
