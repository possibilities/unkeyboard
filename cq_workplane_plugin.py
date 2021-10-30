import cadquery as cq


def cq_workplane_plugin(func):
    setattr(cq.Workplane, func.__name__, func)
    return func
