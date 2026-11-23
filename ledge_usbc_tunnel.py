# -*- coding: utf-8 -*-
"""Right side, STRAIGHT LEDGE WITH A HOUSING FOR THE 90 DEGREE USB-C ADAPTER (21/11/2026).
Results that led to this version (the user, 21/11): the 3.5 degree straight ledge (channel 0.10/0.00, layer 0.08) "was
overdone, it ended up at -2" and "the channel came out really firm"; back on the 2.5 one with the tablet in portrait, "I can't
centre it well with the cable" (holes separated by bridges); asked to "leave room for this adapter [USB-C male-female 90 degrees,
listing photo], I want it hidden and to have more adjustment play in the centre".
  - continuous TUNNEL under the floor, open at the free end (cable exit, away from the heated group) and closed next to the
    stop: the adapter body lies in the tunnel along the ledge, the plug goes up through a continuous SLIT in the floor to the
    tablet's port, and the cable (its plug inserted in the adapter's female end) runs through the tunnel to exit at the end. The
    tablet can sit at any position along the slit (no bridges).
  - Adapter dimensions ESTIMATED (it had not arrived; listing without dimensions): body ~24 x 12.5 x 7, male plug with a collar
    ~4.5 thick. Tunnel 13 x 13 (fits the body lying in both orientations and rotated 10 degrees like the tablet's port), roof
    1.5 under the floor (the plug collar takes up that height inside the slit), slit 5.5.
  - The ledge gets a keel underneath (bottom 12.5 below the old floor): much stiffer, so the compensation drops.
    3.5 gave -2 with the tight channel => the assembly sags ~1.5; with the keel it sags less: 1 degree.
Usage: python -I ledge_usbc_tunnel.py [deg=1.0] [tunnel_w=13] [tunnel_h=13] [roof=1.5] [slit=5.5]"""
import os, sys
ARGS = dict(base='142', deg='1.0', run_clearance='0.10', end_clearance='0.0', tilt='0', tunnel_w='13', tunnel_h='13', roof='1.5', slit='5.5')
ARGS.update(dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a))
sys.argv = [sys.argv[0]] + ['%s=%s' % kv for kv in ARGS.items()]
import numpy as np
import trimesh
from shapely.geometry import box
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import right_stand as D
import ledge_landscape as RD
G = D.G

DEG = float(ARGS['deg']); T = np.tan(np.radians(DEG))
Z_PIVOT = -2.0
TW, TH, ROOF, SLIT = (float(ARGS[k]) for k in ('tunnel_w', 'tunnel_h', 'roof', 'slit'))
WALL = 2.0
XC = (G.XL + G.f(G.FLOOR)) / 2                        # middle of the tablet gap at the floor: the USB port is here
T_TOP = G.FLOOR - ROOF                                # top of the tunnel
T_BOTTOM = T_TOP - TH
X_T0 = max(G.X0 + WALL, XC - TW / 2); X_T1 = X_T0 + TW   # does not thin the lip wall
BOTTOM = T_BOTTOM - WALL                              # bottom face of the ledge (was 0)
Z_CLOSED = G.Z_FRAME - 0.0                            # left side: tunnel closed next to the stop (right side Z 0); open at the free end


def rotate_bar(m):
    m = m.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.arctan(T), [1, 0, 0], point=[0, 0, Z_PIVOT]))
    return m


def cuboid(x0, y0, z0, x1, y1, z1):
    return trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])


def ledge_left():
    body = G.ledge(tilt=0.0, with_channel=False, cable_hole=False)
    keel = cuboid(G.X0, BOTTOM, G.Z_LEDGE0, X_T1 + WALL, 0.5, G.Z_LEDGE1)
    # back wall of the tunnel goes up to the back wall of the step (otherwise floor + wall would be loose, held only by the lip);
    # only outside the block: on top of the block runs the frame's crossbar (Y 7.2)
    keel = trimesh.boolean.union([keel, cuboid(X_T1 - 0.01, BOTTOM, G.Z_LEDGE0, X_T1 + WALL, G.BACK_WALL_H, G.Z_BLOCK0 + 1)], engine='manifold')
    body = trimesh.boolean.union([body, keel], engine='manifold')
    # cross-section of the void: tunnel with 45 degree gussets (1.5) at the top corners, so the roof (two overhangs up to the slit)
    # prints without supports; the adapter body (7 wide, centred on the plug) passes between them
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    gu = 1.5
    sec = box(X_T0, T_BOTTOM, X_T1, T_TOP).difference(Polygon([(X_T0, T_TOP), (X_T0 + gu, T_TOP), (X_T0, T_TOP - gu)]))         .difference(Polygon([(X_T1, T_TOP), (X_T1 - gu, T_TOP), (X_T1, T_TOP - gu)]))
    sec = unary_union([sec, box(XC - SLIT / 2, T_TOP - 0.5, XC + SLIT / 2, G.FLOOR + 1)])
    void = G.extrude(sec, G.Z_LEDGE0 - 1, Z_CLOSED)
    bar = rotate_bar(body)
    block = trimesh.boolean.intersection([G.ledge(tilt=0.0, with_channel=False, cable_hole=False),
                                          cuboid(G.f(G.FLOOR), -50, G.Z_BLOCK0, 100, 50, G.Z_LEDGE1)], engine='manifold')
    m = trimesh.boolean.union([bar, block], engine='manifold')
    below = rotate_bar(cuboid(-50, BOTTOM - 60, -200, 100, BOTTOM, 200))
    return trimesh.boolean.difference([m, below, rotate_bar(void), G.ledge_channel(D.RUN_CLEARANCE, D.END_CLEARANCE)], engine='manifold')


def to_right(m):
    m = m.copy(); m.apply_scale([1, 1, -1]); m.apply_translation([0, 0, G.Z_FRAME]); m.fix_normals()
    return m


def clean_mesh(rp):
    import manifold3d
    for _ in range(3):
        mf = manifold3d.Manifold(manifold3d.Mesh(vert_properties=np.asarray(rp.vertices, np.float32), tri_verts=np.asarray(rp.faces, np.uint32)))
        mf = mf.simplify(0.002)
        mm = mf.to_mesh(); rp = trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))
        rp.apply_translation(-rp.bounds[0])
        t = trimesh.Trimesh(np.asarray(rp.vertices, np.float32).astype(float), rp.faces)
        if t.is_watertight and t.area_faces.min() > 0: break
    return rp


if __name__ == '__main__':
    print('tunnel X %.1f..%.1f (port at %.1f), Y %.1f..%.1f, roof %.1f, slit %.1f; bottom of the ledge at Y %.1f' % (X_T0, X_T1, XC, T_BOTTOM, T_TOP, ROOF, SLIT, BOTTOM))
    rl = ledge_left(); assert rl.is_watertight
    rp = rl.copy(); rp.apply_transform(trimesh.transformations.rotation_matrix(-np.arctan(T), [1, 0, 0], point=[0, BOTTOM, 0]))
    r = to_right(rl); rp = to_right(rp)
    rp.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rp.apply_translation(-rp.bounds[0])
    rp = clean_mesh(rp)
    print('bottom face: contact %.0f mm2' % rp.section(plane_origin=[0, 0, 0.1], plane_normal=[0, 0, 1]).to_2D()[0].area)
    q = D.frame()
    print('assembled interference %.2f mm3; worst while sliding %.2f mm3' % (trimesh.boolean.intersection([r, q], engine='manifold').volume, RD.assembly_interference(r, q)))
    # cross-section in the middle of the run, to check tunnel, roof, slit and walls
    s = r.section(plane_origin=[0, 0, 70], plane_normal=[0, 0, 1])
    print('section at Z 70 (right side):', [tuple(np.round(p.bounds, 1)) for p in s.to_2D()[0].polygons_full])
    n = 'tablet_stand_right_v2_ledge_usbc_tunnel_%gdeg' % DEG
    rp.export(os.path.join(G.HERE, 'stl', n + '.stl'))
    trimesh.util.concatenate([q, r]).export(os.path.join(G.HERE, 'stl', n + '_assembled.stl'))
    print(n, rp.extents.round(1), '%.1f cm3' % (rp.volume / 1000), 'watertight', trimesh.load(os.path.join(G.HERE, 'stl', n + '.stl')).is_watertight)
