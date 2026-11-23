# -*- coding: utf-8 -*-
"""Right side, 20/11/2026: the two test ledges (2.5 and 5 degree compensation, dovetail 0.20/0.10) with the
compensation ENGRAVED on the front of the lip ("2.5°" and "5°", 0.6 deep, at the outer end next to the block, which does not tilt).
The text reads from the front (someone looking at the machine). Output: stl/tablet_stand_right_v1_ledge_{2.5|5}deg_marked.stl
Usage: python -I marked_ledges.py [deg=2.5,5]"""
import os, sys
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely import affinity
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import right_stand as D
G = D.G

DEGREES = [float(x) for x in G.ARG.get('deg', '2.5,5').split(',')]
TEXT_H, DEPTH = 7.0, 0.6          # letter height, engraving depth


def text_polygon(s):
    tp = TextPath((0, 0), s, size=10, prop=FontProperties(family='DejaVu Sans', weight='bold'))
    pol = None
    for ring in tp.to_polygons():
        if len(ring) < 3: continue
        p = Polygon(ring).buffer(0)
        pol = p if pol is None else pol.symmetric_difference(p)   # even-odd: holes of the "°"
    x0, y0, x1, y1 = pol.bounds
    k = TEXT_H / (y1 - y0)
    return affinity.scale(affinity.translate(pol, -x0, -y0), k, k, origin=(0, 0))


def engraving(s):
    """text in (z, y) on the front face of the lip (X = G.X0), centred on the outer end (Z -2..35), going DEPTH into X"""
    p = text_polygon(s)
    w = p.bounds[2]
    zc, yc = 16.5, (G.LIP) / 2 + 0.5        # middle of the Z -2..35 stretch and of the lip (floor on the bed = Y 0)
    p = affinity.translate(p, zc - w / 2, yc - TEXT_H / 2)
    m = trimesh.util.concatenate([trimesh.creation.extrude_polygon(g, DEPTH + 1) for g in (p.geoms if hasattr(p, 'geoms') else [p])])
    # polygon in (a=z, b=y), extrusion in c: (a, b, c) -> (x = X0 - 1 + c, y = b, z = a)
    T = np.array([[0, 0, 1, G.X0 - 1], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)
    m.apply_transform(T)
    m.fix_normals()
    return m, w


if __name__ == '__main__':
    for gr in DEGREES:
        D.TILT = gr
        r = D.ledge()
        s = '%g°' % gr
        g, w = engraving(s)
        r = trimesh.boolean.difference([r, g], engine='manifold')
        assert r.is_watertight
        r.export(os.path.join(G.HERE, 'stl', 'tablet_stand_right_v1_ledge_%gdeg_assembled_marked.stl' % gr))
        rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rq.apply_translation(-rq.bounds[0])
        name = 'tablet_stand_right_v1_ledge_%gdeg_marked.stl' % gr
        rq.export(os.path.join(G.HERE, 'stl', name))
        print('%s: "%s" %.1f mm wide; ledge %s, %.2f cm3' % (name, s, w, rq.extents.round(1), rq.volume / 1000))
