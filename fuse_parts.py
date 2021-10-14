import cadquery as cq


def fuse_parts(parts):
    if len(parts) == 1:
        return parts[0]
    part_values = [part.val() for part in parts]
    fused_parts = part_values[0].fuse(*part_values[1:], glue=True).clean()
    return cq.Workplane().newObject([fused_parts])
