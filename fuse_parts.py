import cadquery as cq


def fuse_parts(parts):
    part_values = [part.val() for part in parts]
    fused_parts = part_values[0].fuse(*part_values[1:], glue=True).clean()
    return cq.Workplane().newObject([fused_parts])
