import math
from OCP.Geom2dAPI import Geom2dAPI_InterCurveCurve
from OCP.gp import gp_Pnt2d, gp_Ax2d, gp_Dir2d, gp_Vec2d
from OCP.Geom2d import Geom2d_Line


def calculate_line_at_angle(point, angle):
    angle = math.radians(angle)

    x1 = point[0]
    y1 = point[1]
    p1 = gp_Pnt2d(x1, y1)

    x = math.cos(angle)
    y = math.sin(angle)

    vec1 = gp_Vec2d(x, -y)
    dire1 = gp_Dir2d(vec1)
    axis1 = gp_Ax2d(p1, dire1)

    return Geom2d_Line(axis1)


def calculate_intersection_of_points(point1, angle1, point2, angle2):
    line1 = calculate_line_at_angle(point1, angle1)
    line2 = calculate_line_at_angle(point2, angle2)

    intersector = Geom2dAPI_InterCurveCurve(line1, line2, 0.001)

    pt = intersector.Point(1)

    xp = pt.X()
    yp = pt.Y()

    return (xp, yp)
