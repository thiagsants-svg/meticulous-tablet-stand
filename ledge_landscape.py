# -*- coding: utf-8 -*-
"""Right side, tablet in LANDSCAPE (20/11/2026, request "make a version for the tablet in landscape").
Reuses the right frame already printed (bottom of the tablet 190 below the top); only the ledge is new:
  - extended OUTWARD from the machine (ext_outward, past the open end of the channel), spanning Z -100..130 (230 mm, fits the bed);
    inwards it still goes to 130, a length that has already proven to fit (printed and assembled on 20/11);
  - the 245 mm tablet has its middle near the frame (Z ~15): the weight barely levers the dovetail,
    so the default sag compensation is 0 (tilt=);
  - no cable holes: in landscape the USB-C is at one end of the tablet and the cable leaves sideways;
  - tightened dovetail (0.20 along the run, 0.10 in the last 8 mm, like the 2.5/5 degree ledges);
  - "landscape" engraved on the front of the lip.
Usage: python -I ledge_landscape.py [outward=98] [tilt=0] [back_wall_ext=6.7]"""
import os, sys
import numpy as np
import trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import right_stand as D
import marked_ledges as RM
G = D.G

OUTWARD = float(G.ARG.get('outward', 98.0))
TILT = float(G.ARG.get('tilt', 0.0))
BACK_WALL_EXT = float(G.ARG.get('back_wall_ext', 6.7))


def ledge():
    r = G.ledge(tilt=TILT, run_clearance=D.RUN_CLEARANCE, end_clearance=D.END_CLEARANCE, ext_outward=OUTWARD, back_wall_ext=BACK_WALL_EXT, cable_hole=False)
    r.apply_scale([1, 1, -1]); r.apply_translation([0, 0, G.Z_FRAME]); r.fix_normals()
    g, w = RM.engraving('landscape')
    return trimesh.boolean.difference([r, g], engine='manifold'), w


def assembly_interference(r, q):
    """the frame slides in from outside (smaller Z) up to the stop: interference volume at several positions"""
    worst = 0.0
    for dz in np.arange(-150, 0.1, 2.0):
        qq = q.copy(); qq.apply_translation([0, 0, dz])
        i = trimesh.boolean.intersection([r, qq], engine='manifold')
        v = i.volume if len(i.faces) else 0.0
        worst = max(worst, v)
        if v > 0.5: print('  interference %.1f mm3 with the frame shifted %.0f' % (v, dz))
    return worst


if __name__ == '__main__':
    r, w = ledge()
    assert r.is_watertight
    q = D.frame()
    print('assembled ledge Z %.1f..%.1f, text %.0f mm; worst interference while assembling: %.2f mm3' % (r.bounds[0][2], r.bounds[1][2], w, assembly_interference(r, q)))
    trimesh.util.concatenate([q, r]).export(os.path.join(G.HERE, 'stl', 'tablet_stand_right_landscape_assembled.stl'))
    rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rq.apply_translation(-rq.bounds[0])
    rq.export(os.path.join(G.HERE, 'stl', 'tablet_stand_right_landscape_ledge.stl'))
    print('print: ledge', rq.extents.round(1), '%.2f cm3' % (rq.volume / 1000))
