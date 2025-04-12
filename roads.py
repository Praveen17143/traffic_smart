# roads.py - Road components for the driving simulation

from ursina import Entity, Vec2, Vec3, color, Mesh
from math import sin, cos, radians, degrees, atan2

class RoadSegment(Entity):
    """
    A flat rectangular road segment (quad) at y=0.02 so it has no side walls.
    center: (x, z)
    size: (length_in_x, length_in_z)
    """
    def __init__(self, center, size, **kwargs):
        super().__init__(
            model='quad',
            position=(center[0], 0.02, center[1]),
            rotation_x=90,
            scale=(size[0], size[1]),
            color=color.rgb(30, 30, 30),  # asphalt black
            **kwargs
        )
        # For collision checks:
        self.center2d = Vec2(center[0], center[1])
        self.half_size = Vec2(size[0]*0.5, size[1]*0.5)

    def contains_point(self, pos):
        p2 = Vec2(pos.x, pos.z)
        return (
            abs(p2.x - self.center2d.x) <= self.half_size.x and
            abs(p2.y - self.center2d.y) <= self.half_size.y
        )


class RoadArc(Entity):
    """
    A quarter‐arc for smooth corners (right turns) at an intersection.
    center: (x, z) circle center
    radius: mid-line radius
    start_angle, end_angle: angles in degrees (0=+X, 90=+Z, etc.)
    width: thickness of road
    segments: how many quads to form the arc
    """
    def __init__(self, center, radius, start_angle, end_angle, width, segments=10, **kwargs):
        self.center2d = Vec2(center[0], center[1])
        inner_r = radius - width*0.5
        outer_r = radius + width*0.5

        verts = []
        tris = []
        idx = 0
        y_level = 0.02

        angle_range = end_angle - start_angle
        seg_angle = angle_range / segments

        for i in range(segments):
            a0 = radians(start_angle + i*seg_angle)
            a1 = radians(start_angle + (i+1)*seg_angle)
            v0 = Vec3(self.center2d.x + inner_r*cos(a0), y_level, self.center2d.y + inner_r*sin(a0))
            v1 = Vec3(self.center2d.x + outer_r*cos(a0), y_level, self.center2d.y + outer_r*sin(a0))
            v2 = Vec3(self.center2d.x + outer_r*cos(a1), y_level, self.center2d.y + outer_r*sin(a1))
            v3 = Vec3(self.center2d.x + inner_r*cos(a1), y_level, self.center2d.y + inner_r*sin(a1))
            verts += [v0, v1, v2, v3]
            tris += [idx, idx+1, idx+2, idx, idx+2, idx+3]
            idx += 4

        mesh = Mesh(vertices=verts, triangles=tris, mode='triangle')
        mesh.generate_normals()

        super().__init__(
            model=mesh,
            color=color.rgb(30,30,30),  # asphalt black
            **kwargs
        )
        self.inner_radius = inner_r
        self.outer_radius = outer_r
        self.start_angle = start_angle
        self.end_angle = end_angle

    def contains_point(self, pos):
        p2 = Vec2(pos.x, pos.z)
        dist = (p2 - self.center2d).length()
        if dist < self.inner_radius or dist > self.outer_radius:
            return False

        # angle in [0,360)
        ang = degrees(atan2(p2.y - self.center2d.y, p2.x - self.center2d.x)) % 360
        s = self.start_angle % 360
        e = self.end_angle % 360
        if s < e:
            return s <= ang <= e
        else:
            return ang >= s or ang <= e 