import cadquery as cq
from flatten_list import flatten_list


def fuse_parts(parts):
    if not len(parts):
        return cq.Workplane()

    part_values = flatten_list([part.vals() for part in parts])
    fused_parts = part_values[0].fuse(*part_values[1:], glue=True).clean()
    fused_object = cq.Workplane().newObject([fused_parts])

    return fused_object
