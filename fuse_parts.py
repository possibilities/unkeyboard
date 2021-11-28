import cadquery as cq


def fuse_parts(parts):
    if not len(parts):
        return cq.Workplane()

    part_values = [part.val() for part in parts]
    fused_parts = part_values[0].fuse(*part_values[1:], glue=True).clean()
    fused_object = cq.Workplane().newObject([fused_parts])

    return fused_object
