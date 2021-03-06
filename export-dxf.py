import os
import ezdxf
from ezdxf import units
from cadquery import exporters
from cadquery.units import RAD2DEG
from OCP.gp import gp_Dir
from OCP.GeomConvert import GeomConvert
from case import make_case_parts

# This is largely copped from cadquery with the bottom modified:
# * Adds models to named layers
#   * Includes thickness in layer name
# * Updates the units to MM
# * Removes empty 'Defpoints' layer

CURVE_TOLERANCE = 1e-9


def _dxf_line(e, msp, plane, layer_name):

    msp.add_line(
        e.startPoint().toTuple(),
        e.endPoint().toTuple(),
        dxfattribs={"layer": layer_name},
    )


def _dxf_circle(e, msp, plane, layer_name):

    geom = e._geomAdaptor()
    circ = geom.Circle()

    r = circ.Radius()
    c = circ.Location()

    c_dy = circ.YAxis().Direction()
    c_dz = circ.Axis().Direction()

    dy = gp_Dir(0, 1, 0)

    phi = c_dy.AngleWithRef(dy, c_dz)

    if c_dz.XYZ().Z() > 0:
        a1 = RAD2DEG * (geom.FirstParameter() - phi)
        a2 = RAD2DEG * (geom.LastParameter() - phi)
    else:
        a1 = -RAD2DEG * (geom.LastParameter() - phi) + 180
        a2 = -RAD2DEG * (geom.FirstParameter() - phi) + 180

    if e.IsClosed():
        msp.add_circle(
            (c.X(), c.Y(), c.Z()),
            r,
            dxfattribs={"layer": layer_name},
        )
    else:
        msp.add_arc(
            (c.X(), c.Y(), c.Z()),
            r,
            a1,
            a2,
            dxfattribs={"layer": layer_name},
        )


def _dxf_ellipse(e, msp, plane, layer_name):

    geom = e._geomAdaptor()
    ellipse = geom.Ellipse()

    r1 = ellipse.MinorRadius()
    r2 = ellipse.MajorRadius()

    c = ellipse.Location()
    xdir = ellipse.XAxis().Direction()
    xax = r2 * xdir.XYZ()

    msp.add_ellipse(
        (c.X(), c.Y(), c.Z()),
        (xax.X(), xax.Y(), xax.Z()),
        r1 / r2,
        geom.FirstParameter(),
        geom.LastParameter(),
        dxfattribs={"layer": layer_name},
    )


def _dxf_spline(e, msp, plane, layer_name):

    adaptor = e._geomAdaptor()
    curve = GeomConvert.CurveToBSplineCurve_s(adaptor.Curve().Curve())

    spline = GeomConvert.SplitBSplineCurve_s(
        curve,
        adaptor.FirstParameter(),
        adaptor.LastParameter(),
        CURVE_TOLERANCE,
    )

    # need to apply the transform on the geometry level
    spline.Transform(plane.fG.wrapped.Trsf())

    order = spline.Degree() + 1
    knots = list(spline.KnotSequence())
    poles = [(p.X(), p.Y(), p.Z()) for p in spline.Poles()]
    weights = (
        [spline.Weight(i) for i in range(1, spline.NbPoles() + 1)]
        if spline.IsRational()
        else None
    )

    if spline.IsPeriodic():
        pad = spline.NbKnots() - spline.LastUKnotIndex()
        poles += poles[:pad]

    dxf_spline = ezdxf.math.BSpline(poles, order, knots, weights)

    msp.add_spline(
        dxfattribs={"layer": layer_name},
    ).apply_construction_tool(dxf_spline)


DXF_CONVERTERS = {
    "LINE": _dxf_line,
    "CIRCLE": _dxf_circle,
    "ELLIPSE": _dxf_ellipse,
    "BSPLINE": _dxf_spline,
}


def export_flat_dxf(file_name):
    rotate_parts = False
    parts_per_column = 1
    space_between_parts = 3

    offset_y = 0
    offset_x = 0

    [case_parts, case_geometry] = make_case_parts()

    dxf = ezdxf.new(setup=True, units=units.MM)
    msp = dxf.modelspace()

    layer_name = "All parts"
    dxf.layers.new(name=layer_name)

    for (index, layer_name_and_part) in enumerate(case_parts):
        part = layer_name_and_part[1]

        if rotate_parts:
            part = part.rotateAboutCenter((0, 0, 1), 90)

        height = (
            part.vertices(">Y").val().Center().y
            - part.vertices("<Y").val().Center().y
        )

        width = (
            part.vertices(">X").val().Center().x
            - part.vertices("<X").val().Center().x
        )

        part = part.translate([offset_x, offset_y, 0]).faces("front")

        plane = part.plane
        shape = exporters.toCompound(part).transformShape(plane.fG)

        for e in shape.Edges():
            conv = DXF_CONVERTERS.get(e.geomType(), _dxf_spline)
            conv(e, msp, plane, layer_name)

        if ((index + 1) % parts_per_column) == 0:
            offset_x = 0
            offset_y = offset_y + height + space_between_parts
        else:
            offset_x = offset_x + width + space_between_parts

    dxf.layers.remove("Defpoints")
    dxf.saveas(file_name)


def export_layered_dxf(file_name):
    [case_parts, case_geometry] = make_case_parts()

    dxf = ezdxf.new(setup=True, units=units.MM)
    dxf = ezdxf.new(setup=True)
    msp = dxf.modelspace()

    for layer_name_and_part in case_parts:
        [layer_name, part, options] = layer_name_and_part
        thickness = (
            part.vertices("front").val().Center().z
            - part.vertices("back").val().Center().z
        )
        part = part.faces("front")
        full_layer_name = "%s (1 x %smm)" % (layer_name, thickness)
        dxf.layers.new(name=full_layer_name)
        plane = part.plane
        shape = exporters.toCompound(part).transformShape(plane.fG)

        for e in shape.Edges():
            conv = DXF_CONVERTERS.get(e.geomType(), _dxf_spline)
            conv(e, msp, plane, full_layer_name)

    dxf.layers.remove("Defpoints")
    dxf.saveas(file_name)


def main():
    try:
        os.mkdir("./data")
    except Exception:
        pass

    file_name = "./data/keyboard.dxf"
    preset = os.getenv("PRESET") if os.getenv("PRESET") else "layered"

    if preset == "layered":
        export_layered_dxf(file_name)
    else:
        export_flat_dxf(file_name)

    print()
    print("Exported: %s" % (file_name))


main()
