# -*- coding: utf-8 -*-
"""Meticulous tablet stand (left half), own version in two parts (19/11/2026).

Source: original/Meticulous_tablet_stand_left.stl (SketchUp, open mesh with a ghost surface).
Profile of the original (X = depth, Y = height, Z = width):
  bar tilted 10 degrees (front from (15.3; 4) to (34.7; 114), 4 mm), crossbar Y 32..36, back leg X 38..42,
  top bar Y 110..114 up to X 96.3, hook X 92.3..96.3 going down to Y 67 (gap 50.3 x 43 to hang on the machine);
  frame in Z 0..35, top bar + hook in Z 0..75, step (floor 4 + lip 4 x 13) in Z -95..37 with a cable hole.

Changes:
  1. two parts that print WITHOUT supports: frame lying flat (profile on the bed: layers in the plane of the hook, which
     comes out strong) and the step ledge lying on its floor; joined by a 20 degree dovetail that locks the ledge downwards
     and to one side.
  2. bottom crossbar (Y 7..11) closing the triangle of the base; back block on the ledge only next to the frame.
  3. inner corners with a radius (2 mm; 1 mm on the outer corners) instead of sharp corners.
  4. tablet gap and lip height as parameters (gap=, lip=), to adjust after measuring the Galaxy.
Usage: python -I left_stand.py [gap=8.1] [lip=13] [clearance=0.30] [tight=0.15] [column=50.6] [column_clearance=0.25]
"""
import os, sys, json
import numpy as np
import trimesh
from shapely.geometry import Polygon, box, Point, LineString
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ARG = dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a)
# tablet: Galaxy Tab A 10.1 (2019) SM-T515, 245.2 x 149.4 x 7.5 (spec sheet), PORTRAIT and WITHOUT A CASE (the user, 19/11/2026).
# Tilted 10 degrees, it takes 7.5 / cos 10 = 7.62 horizontally; + ~0.5 clearance = 8.1 (original 11.3)
GAP = float(ARG.get('gap', 8.1))        # between the inner face of the lip and the front of the bar, at floor level
BACK_WALL_H, BACK_WALL_T = 10.0, 3.0    # back wall of the channel along the whole step (new): height and thickness
LIP = float(ARG.get('lip', 13.0))       # lip height from the bed (original 13)
CLEARANCE = float(ARG.get('clearance', 0.30))   # per side in the dovetail (D63-T05: 0.30 was the smallest that slid freely; 0.20 did not slide)
# tight final stretch next to the stop (request 19/11/2026: "the tightest slide we have"): last 8 mm with 0.15 per side,
# recipe from FID-T04 (20 degree dovetail, 0.30 along the run + 0.15 in the last 8 mm: "locks and releases with one hand"); 2 mm ramp
TIGHT = float(ARG.get('tight', 0.15))
L_TIGHT, L_RAMP = 8.0, 2.0
# machine column where the hook fits: 50.6 MEASURED by the user with calipers on 19/11/2026 (the original had a 50.3 gap,
# smaller than the column). CAD gap = measurement + 0.25 per side; printed openings come out 0.1 to 0.25 smaller (D63-M01), leaving ~0.1 to 0.15 per side.
COLUMN = float(ARG.get('column', 50.6))
COLUMN_CLEARANCE = float(ARG.get('column_clearance', 0.25))
GX0 = 42.0                                     # inner face of the leg
GX1 = GX0 + COLUMN + 2 * COLUMN_CLEARANCE      # inner face of the hook (original 92.3)
GX2 = GX1 + 4.0                                # outer face of the hook
RI_COL = 0.8                                   # radius at the two corners that touch the column (the machine's edge is sharp)

inc = (34.7 - 15.3) / 110.0               # slope of the front of the bar (x per y)
f = lambda y: 15.3 + inc * (y - 4.0)      # front of the tilted bar
FLOOR, BLOCK_Y, FOOT_Y = 4.0, 7.0, 7.2    # ledge floor, top of the back block, bottom of the lower crossbar
XL = 15.3 - GAP                           # inner face of the lip
X0 = XL - 4.0                             # front of the lip
BL_X0, BL_X1 = f(BLOCK_Y), 37.6           # back block of the ledge (leg at 38.0)
DOVETAIL_XC, DOVETAIL_W, DOVETAIL_H, ANG = 27.0, 6.0, 4.0, np.radians(20)
Z_LEDGE0, Z_LEDGE1, Z_BLOCK0 = -95.0, 37.0, -5.0
Z_FRAME, Z_HOOK = 35.0, 75.0


def dovetail(c, y_top, y_bottom):
    """dovetail trapezoid: width DOVETAIL_W - 2c at the top, widening downwards at 20 degrees"""
    at = DOVETAIL_W / 2 - c + (BLOCK_Y - y_top) * np.tan(ANG)
    ab = DOVETAIL_W / 2 - c + (BLOCK_Y - y_bottom) * np.tan(ANG)
    xc = DOVETAIL_XC
    return Polygon([(xc - ab, y_bottom), (xc + ab, y_bottom), (xc + at, y_top), (xc - at, y_top)])


def round_profile(p, ri=2.0, re=1.0):
    p = p.buffer(ri, join_style=1, quad_segs=16).buffer(-ri, join_style=1, quad_segs=16)
    return p.buffer(-re, join_style=1, quad_segs=16).buffer(re, join_style=1, quad_segs=16)


def frame_profile():
    bar = Polygon([(f(FOOT_Y), FOOT_Y), (f(FOOT_Y) + 4, FOOT_Y), (38.7, 114), (34.7, 114)])
    parts = [bar,
             box(f(32), 32, 42, 36),                # middle crossbar (original)
             box(f(FOOT_Y), FOOT_Y, 42, FOOT_Y + 4),  # lower crossbar (new)
             box(38, 0, 42, 114),                   # back leg
             box(34.7, 110, GX2, 114),              # top bar
             box(GX1, 67, GX2, 114)]                # hook
    p = column_corners(round_profile(unary_union(parts)))
    tongue = dovetail(CLEARANCE, FOOT_Y + 0.5, BLOCK_Y - DOVETAIL_H + 0.5)   # 0.5 gap at the bottom; goes up into the crossbar
    return unary_union([p, tongue]).buffer(0)


def hook_profile():
    return column_corners(round_profile(unary_union([box(42 - 3, 110, GX2, 114), box(GX1, 67, GX2, 114)])))


def column_corners(p):
    """redoes the column gap with corners of radius RI_COL (the 2 mm radius would make the machine's sharp edge rest on the rounding)"""
    gap = box(GX0, 60, GX1, 110 - RI_COL).union(box(GX0 + RI_COL, 60, GX1 - RI_COL, 110))
    gap = gap.union(Point(GX0 + RI_COL, 110 - RI_COL).buffer(RI_COL, quad_segs=16)).union(Point(GX1 - RI_COL, 110 - RI_COL).buffer(RI_COL, quad_segs=16))
    return p.difference(gap).buffer(0)


def extrude(poly, z0, z1):
    m = trimesh.creation.extrude_polygon(poly, z1 - z0)
    m.apply_translation([0, 0, z0])
    return m


def ledge(cable_z=-30.0, cable_len=13.0, holes=None, tilt=0.0, run_clearance=None, end_clearance=None, ext_outward=0.0, back_wall_ext=6.7, cable_hole=True, with_channel=True):
    base = round_profile(unary_union([box(X0, 0, f(FLOOR) + 4 * 0, FLOOR), box(X0, 0, XL, LIP),
                                      Polygon([(X0, 0), (f(0) + BACK_WALL_T, 0), (f(FLOOR) + BACK_WALL_T, FLOOR), (X0, FLOOR)]),
                                      # back wall along the line of the bar (10 degrees): with the tablet in portrait (149 wide) and the frame
                                      # only at one end (Z 0..35), without it the bottom edge can slip backwards and the tablet twists to the free side
                                      Polygon([(f(0), 0), (f(0) + BACK_WALL_T, 0), (f(BACK_WALL_H) + BACK_WALL_T, BACK_WALL_H), (f(BACK_WALL_H), BACK_WALL_H)])]), 1.0, 0.8)
    block = round_profile(unary_union([box(X0, 0, XL, LIP), Polygon([(X0, 0), (BL_X1, 0), (BL_X1, BLOCK_Y), (BL_X0, BLOCK_Y), (f(FLOOR), FLOOR), (X0, FLOOR)])]), 1.0, 0.8)
    a = extrude(base, Z_LEDGE0, Z_BLOCK0 + 1)
    b = extrude(block, Z_BLOCK0, Z_LEDGE1)
    pieces = [a, b]
    if ext_outward:
        # 20/11/2026, tablet in LANDSCAPE: extends the ledge OUTWARD from the frame (past the open end of the channel, Z > Z_LEDGE1),
        # with only the step profile (floor + lip + wall). When assembling, the frame passes over this stretch up to the stop: the
        # lower crossbar and the leg start at Y FOOT_Y (7.2) and the front of the bar at X ~15.9, so the back wall there is
        # back_wall_ext high (6.7: 0.5 below the crossbar); lip and floor are at X < 15.9 and do not cross. The channel (X 24..30)
        # does not exist in this profile.
        ext = round_profile(unary_union([box(X0, 0, f(FLOOR), FLOOR), box(X0, 0, XL, LIP),
                                         Polygon([(X0, 0), (f(0) + BACK_WALL_T, 0), (f(FLOOR) + BACK_WALL_T, FLOOR), (X0, FLOOR)]),
                                         Polygon([(f(0), 0), (f(0) + BACK_WALL_T, 0), (f(back_wall_ext) + BACK_WALL_T, back_wall_ext), (f(back_wall_ext), back_wall_ext)])]), 1.0, 0.8)
        pieces.append(extrude(ext, Z_LEDGE1 - 1, Z_LEDGE1 + ext_outward))
    m = trimesh.boolean.union(pieces, engine='manifold')
    if tilt:
        # sag compensation (20/11/2026: the printed right side ended up tilted 3 degrees under the tablet's weight, inner end
        # lower): outside the dovetail block (Z < Z_BLOCK0, free end of the ledge) the floor, the lip and the wall rise
        # tan(tilt) per mm; the bottom face stays flat (offset proportional to y up to floor height). The block and the
        # channel do not change, so the fit on the frame is the same.
        v = m.vertices.copy()
        dz = np.clip(Z_BLOCK0 - v[:, 2], 0, None)
        v[:, 1] += np.tan(np.radians(tilt)) * dz * np.clip(v[:, 1] / FLOOR, 0, 1)
        m = trimesh.Trimesh(v, m.faces, process=True)
    # dovetail channel, open at the Z 37 end and closed at Z 0 (stop)
    # effective clearance per side against the frame's tongue (which is made with CLEARANCE): by default CLEARANCE along the
    # run and TIGHT at the end; smaller run_clearance / end_clearance narrow only the ledge channel (reprint only the ledge to tighten)
    channel = ledge_channel(run_clearance, end_clearance)
    # cable hole: oblong hole in the floor, width = tablet gap (max. 9); original: centred at Z -30 (middle of the step), 13 long
    w = min(9.0, GAP); r = w / 2; half = cable_len / 2 - r
    ch = LineString([(XL + r, cable_z - half), (XL + r, cable_z + half)]).buffer(r, quad_segs=24)
    if holes:   # several rectangular holes (corners r 1) separated by bridges: list of (z0, z1)
        ch = unary_union([box(XL + 1.3, z0 + 1, XL + w - 1.3, z1 - 1).buffer(1.0, quad_segs=8) for z0, z1 in holes])   # 0.3 away from the channel walls (avoids slivers in the mesh)
    chs = list(ch.geoms) if hasattr(ch, 'geoms') else [ch]
    hole = trimesh.util.concatenate([trimesh.creation.extrude_polygon(x, 40) for x in chs])   # in XZ: extrude in Y (40: goes through the floor even with compensation)
    hole.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))   # (x, y_pol, z) -> (x, -z, y_pol): polygon y becomes Z
    hole.apply_translation([0, 30, 0])   # Y -10..30
    cut = ([channel] if with_channel else []) + ([hole] if cable_hole else [])
    if cut:
        m = trimesh.boolean.difference([m] + cut, engine='manifold')
    return m


def ledge_channel(run_clearance=None, end_clearance=None):
    """volume of the ledge's dovetail channel (left-side coordinates)"""
    fc = CLEARANCE if run_clearance is None else run_clearance
    ff = TIGHT if end_clearance is None else end_clearance
    channel = extrude(dovetail(CLEARANCE - fc, BLOCK_Y + 1, BLOCK_Y - DOVETAIL_H), L_TIGHT + L_RAMP, Z_LEDGE1 + 1)
    squeeze = CLEARANCE - ff   # the channel narrows by this per side in the final stretch (the tongue is the same)
    tight = extrude(dovetail(squeeze, BLOCK_Y + 1, BLOCK_Y - DOVETAIL_H), 0.0, L_TIGHT)
    ramp = trimesh.util.concatenate([extrude(dovetail(squeeze, BLOCK_Y + 1, BLOCK_Y - DOVETAIL_H), L_TIGHT - 0.01, L_TIGHT),
                                     extrude(dovetail(CLEARANCE - fc, BLOCK_Y + 1, BLOCK_Y - DOVETAIL_H), L_TIGHT + L_RAMP, L_TIGHT + L_RAMP + 0.01)]).convex_hull
    channel = trimesh.boolean.union([channel, tight, ramp], engine='manifold')
    return channel


def frame():
    a = extrude(frame_profile(), 0, Z_FRAME)
    b = extrude(hook_profile(), Z_FRAME - 1, Z_HOOK)
    return trimesh.boolean.union([a, b], engine='manifold')


if __name__ == '__main__':
    q, r = frame(), ledge()
    for n, m in (('frame', q), ('ledge', r)):
        assert m.is_watertight, n
        print('%s: %.1f x %.1f x %.1f, %.1f cm3, ~%.1f g solid PETG' % (n, *m.extents, m.volume / 1000, m.volume / 1000 * 1.27))
    # assembly (for checking and preview), in the original's coordinate system
    trimesh.util.concatenate([q, r]).export(os.path.join(HERE, 'stl', 'tablet_stand_left_v1_assembled.stl'))
    # print orientation: frame with Z 0 on the bed (already is); ledge with the floor (Y 0) on the bed: Y -> Z
    rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    rq.apply_translation(-rq.bounds[0]); qq = q.copy(); qq.apply_translation(-qq.bounds[0])
    qq.export(os.path.join(HERE, 'stl', 'tablet_stand_left_v1_frame.stl'))
    rq.export(os.path.join(HERE, 'stl', 'tablet_stand_left_v1_ledge.stl'))
    print('ledge print:', rq.extents.round(1), ' frame print:', qq.extents.round(1))
    json.dump(dict(gap=GAP, lip=LIP, clearance=CLEARANCE, tight=TIGHT, l_tight=L_TIGHT, column=COLUMN, column_clearance=COLUMN_CLEARANCE, hook_gap=GX1 - GX0), open(os.path.join(HERE, 'output', 'parameters_v1.json'), 'w'))
