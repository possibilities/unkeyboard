import os
import ezdxf
from ezdxf import units
from cadquery import exporters
from cadquery.units import RAD2DEG
from OCP.gp import gp_Dir
from OCP.GeomConvert import GeomConvert

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


def export_to_dxf_layers(parts, fname):
    try:
        os.mkdir("./data")
    except:
        pass

    dxf = ezdxf.new(setup=True, units=units.MM)
    msp = dxf.modelspace()

    for layer_name_and_part in parts:
        [layer_name, part] = layer_name_and_part
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
    dxf.saveas(fname)
