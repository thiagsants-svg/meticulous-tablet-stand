# -*- coding: utf-8 -*-
"""Meticulous tablet stand, RIGHT SIDE (19/11/2026): tablet in portrait in front of the right-hand part (screen and button),
as in the user's photo holding the Tab A 10.1 there. Reuses from left_stand.py the ledge, the dovetail,
the tablet gap, the back wall and the hook; the frame is new.

Machine button (measured by the user with calipers): from 65.07 to 113.08 below the top, protruding 34.13 from the face.
The button is the "push to brew": nothing may touch it. So the frame forms a WINDOW around the button:
  leg on the face only down to LEG_H below the top (above the button), crossbar there, tablet bar held away from the face
  (back of the bar at >= button + BUTTON_CLEARANCE over the whole button band, with 5 mm margin above and below),
  lower strut coming back to the face below the button. The horizontal position of the button no longer matters.
Ledge: the same as the left one mirrored in Z (extends into the machine, same side as the top bar with the hook;
  the open end of the dovetail is on the outside).
Usage: python -I right_stand.py [base=190] [hole=12] [bridge=2.5] [n_holes=5] [gap=8.1] [column=50.6] ... (the parameters of left_stand.py apply)
  base = how far the bottom of the tablet (step floor) sits below the top of the machine.
"""
import os, sys, json
import numpy as np
import trimesh
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import left_stand as G

ARG = G.ARG
BASE = float(ARG.get('base', 190.0))   # the user's choice 19/11/2026: "Lower (190)" (top of the tablet ~51 above the machine)
BUTTON_TOP, BUTTON_BOTTOM, BUTTON_PROTRUSION = 65.07, 113.08, 34.13
BUTTON_CLEARANCE, MARGIN = 3.0, 5.0
LEG_H = 55.0                        # leg rests on the face from the top down to 55 below (button starts at 65)
# cable hole on the right side (request 20/11/2026: widen it to the sides and move it to the right, away from the heated group):
# centre at CABLE_Z from the outer end of the ledge (Z -2 = outer end, next to the right edge of the machine), CABLE_LEN long.
# The USB-C plug comes out of the middle of the tablet's bottom edge: with the hole at 45 the tablet is shifted to the right
# (from ~-30 to ~120 in Z, ~28 mm past the outer end of the ledge), away from the head.
# 20/11/2026, clarification: "in case I need to pull the tablet even further to the right" -> continuous slot from the middle to
# 8 mm from the outer end (Z 6..70): the plug (~12 mm) goes down with the centre of the tablet between ~12 and ~64 mm from the outer end
CABLE_Z = float(ARG.get('cable_z', 38.0))
CABLE_LEN = float(ARG.get('cable_len', 64.0))
# 20/11/2026: "you can add several bridges, the USB-C cable itself is small" -> instead of the continuous slot, HOLES of
# HOLE_LEN separated by bridges of BRIDGE (full floor, they join the lip to the rest), starting 8 mm from the outer end
HOLE_LEN = float(ARG.get('hole', 12.0))
BRIDGE = float(ARG.get('bridge', 2.5))
N_HOLES = int(ARG.get('n_holes', 5))
HOLES = [(6 + i * (HOLE_LEN + BRIDGE), 6 + i * (HOLE_LEN + BRIDGE) + HOLE_LEN) for i in range(N_HOLES)]   # in right-side Z
# 20/11/2026: printed, "it came out good", but under the tablet's weight it ended up tilted 3 degrees (iPhone level), inner end
# lower (photo). New ledge with the floor rising TILT degrees inwards from the block; the frame does not change.
# 20/11/2026, later: "tighten the dovetail more, it was not firm". Only the ledge is reprinted (the frame's tongue has
# 0.30 per side in CAD): channel narrowed to 0.20 per side along the run (D63-T05: 0.20 was the first that did NOT slide freely
# on a 28 mm lid, i.e. tight) and 0.10 in the last 8 mm (lock). Possible rise of the tongue (clearance / tan 20, calculated):
# 0.82 -> 0.55 along the run and 0.27 at the end. Part of the 3 degree sag came from this play (~1.3 degrees calculated with 0.82 over 35 mm),
# so the compensation drops to 2.5 degrees.
RUN_CLEARANCE = float(ARG.get('run_clearance', 0.20))
END_CLEARANCE = float(ARG.get('end_clearance', 0.10))
TILT = float(ARG.get('tilt', 2.5))
BAR_T = 5.0                         # tablet bar thicker than the original's (4): larger free gap

YT = G.FLOOR + BASE                 # top of the machine = bottom face of the top bar
f = G.f
# machine face: the back of the bar at the top of the button band must be button + clearance away from the face
y_high = YT - BUTTON_TOP + MARGIN
XF = f(y_high) + BAR_T + BUTTON_PROTRUSION + BUTTON_CLEARANCE
GX1 = XF + G.COLUMN + 2 * G.COLUMN_CLEARANCE
GX2 = GX1 + 4.0


def column_corners(p):
    r = G.RI_COL
    gap = box(XF, YT - 50, GX1, YT - r).union(box(XF + r, YT - 50, GX1 - r, YT))
    gap = gap.union(Point(XF + r, YT - r).buffer(r, quad_segs=16)).union(Point(GX1 - r, YT - r).buffer(r, quad_segs=16))
    return p.difference(gap).buffer(0)


def frame_profile():
    y0 = G.FOOT_Y
    bar = Polygon([(f(y0), y0), (f(y0) + BAR_T, y0), (f(YT + 4) + BAR_T, YT + 4), (f(YT + 4), YT + 4)])
    parts = [bar,
             box(f(y0), y0, XF, y0 + 4),                       # lower strut (over the ledge), up to the face
             box(XF - 4, y0, XF, y0 + 18),                     # foot on the face, below the button
             box(f(YT - LEG_H - 4), YT - LEG_H - 4, XF, YT - LEG_H),   # crossbar above the button
             box(XF - 4, YT - LEG_H - 4, XF, YT + 4),          # short leg on the face
             box(f(YT + 4), YT, GX2, YT + 4),                  # top bar
             box(GX1, YT - 43, GX2, YT + 4)]                   # hook
    p = column_corners(G.round_profile(unary_union(parts)))
    tongue = G.dovetail(G.CLEARANCE, y0 + 0.5, G.BLOCK_Y - G.DOVETAIL_H + 0.5)
    return unary_union([p, tongue]).buffer(0)


def hook_profile():
    return column_corners(G.round_profile(unary_union([box(XF - 3, YT, GX2, YT + 4), box(GX1, YT - 43, GX2, YT + 4)])))


def frame():
    a = G.extrude(frame_profile(), 0, G.Z_FRAME)
    b = G.extrude(hook_profile(), G.Z_FRAME - 1, G.Z_HOOK)
    return trimesh.boolean.union([a, b], engine='manifold')


def ledge():
    r = G.ledge(holes=[(G.Z_FRAME - z1, G.Z_FRAME - z0) for z0, z1 in HOLES], tilt=TILT, run_clearance=RUN_CLEARANCE, end_clearance=END_CLEARANCE)   # left-side coordinate before the z -> 35 - z mirror
    r.apply_scale([1, 1, -1]); r.apply_translation([0, 0, G.Z_FRAME])   # z -> 35 - z: ledge -2..130, channel -2..35, stop at 35
    r.fix_normals()
    return r


def check_button_clearance(q):
    """smallest distance between the frame and the button volume (box of vertical band x protrusion), at any Z"""
    btn = box(XF - BUTTON_PROTRUSION, YT - BUTTON_BOTTOM, XF, YT - BUTTON_TOP)
    p = frame_profile()
    return p.distance(btn), p.intersects(btn)


if __name__ == '__main__':
    q, r = frame(), ledge()
    for n, m in (('right frame', q), ('right ledge', r)):
        assert m.is_watertight, n
        print('%s: %.1f x %.1f x %.1f, %.1f cm3' % (n, *m.extents, m.volume / 1000))
    d, crosses = check_button_clearance(q)
    print('machine face at X %.1f; top at Y %.1f; minimum clearance to the button %.2f mm (crosses: %s)' % (XF, YT, d, crosses))
    print('tablet: top ~%.0f mm above the machine' % (245.2 * np.cos(np.radians(10)) - BASE))
    A = G.HERE
    trimesh.util.concatenate([q, r]).export(os.path.join(A, 'stl', 'tablet_stand_right_v1_assembled.stl'))
    rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rq.apply_translation(-rq.bounds[0])
    qq = q.copy(); qq.apply_translation(-qq.bounds[0])
    qq.export(os.path.join(A, 'stl', 'tablet_stand_right_v1_frame.stl'))
    rq.export(os.path.join(A, 'stl', 'tablet_stand_right_v1_ledge.stl'))
    print('print: frame', qq.extents.round(1), ' ledge', rq.extents.round(1))
    json.dump(dict(base=BASE, gap=G.GAP, column=G.COLUMN, column_clearance=G.COLUMN_CLEARANCE, button=[BUTTON_TOP, BUTTON_BOTTOM, BUTTON_PROTRUSION],
                   face_x=XF, min_button_clearance=d), open(os.path.join(A, 'output', 'parameters_right_v1.json'), 'w'))
