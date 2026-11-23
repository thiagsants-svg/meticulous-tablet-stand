# -*- coding: utf-8 -*-
"""Right side, STRAIGHT LEDGE with the angle in the joint (21/11/2026, request: "leave it as if it were 0 degrees? keeping the
bar straight and compensating in the angle of the joint area").
The ledges with tilt= bend the floor (it rises from the block). Here the whole ledge (floor, lip, wall, holes) is straight and
is ROTATED by DEG relative to the channel: the free end rises tan(DEG) per mm, like a rigid bar.
  - dovetail channel and top of the block stay exactly where the frame expects them (horizontal, same clearances);
  - the original block is kept on top (frame block at Y 0..7) and the rotated bar passes underneath it; the bottom face is
    a single plane (whatever is below the plane is cut off): it prints lying on that plane, without supports;
  - pivot at Z_PIVOT (left-side coordinate; -2 = 3 mm past the block on the free side... see below): under the channel the bar
    goes down to 2.4 mm on the stop side, leaving >= 3 mm of floor under the channel.
Usage: python -I ledge_straight.py [deg=3.5] [hole=36 bridge=4 n_holes=3] [run_clearance=0.10] [end_clearance=0.0]"""
import os, sys
ARGS = dict(base='142', deg='3.5', run_clearance='0.10', end_clearance='0.0', hole='36', bridge='4', n_holes='3', tilt='0')
ARGS.update(dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a))
sys.argv = [sys.argv[0]] + ['%s=%s' % kv for kv in ARGS.items()]
import numpy as np
import trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import right_stand as D
import ledge_landscape as RD
G = D.G

DEG = float(ARGS['deg'])
T = np.tan(np.radians(DEG))
Z_PIVOT = -2.0      # left side: the bar stays at its original height here (just past the block, free side at z < -5)


def rotate_bar(m):
    """rigid bar truly ROTATED about X at the pivot (not sheared): after sagging DEG under the weight, it ends up straight and
    square (vertical ends); the free end (z = -95 on the left) rises"""
    m = m.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.arctan(T), [1, 0, 0], point=[0, 0, Z_PIVOT]))
    return m


def ledge_left():
    holes = [(G.Z_FRAME - z1, G.Z_FRAME - z0) for z0, z1 in D.HOLES]
    body = G.ledge(holes=holes, tilt=0.0, with_channel=False)            # straight, with holes, without channel
    bar = rotate_bar(body)
    # 21/11/2026 "so the compensation doesn't show visually": of the original block only the BACK part stays (X >= front of the
    # bar at the floor, f(FLOOR)), which is the part the frame uses (channel and top at 7). Lip, tablet floor and front all come
    # from the rotated bar: the step looks like a straight ledge, and the tablet rests on the bar (not on a higher floor next to the stop).
    x_back = G.f(G.FLOOR)
    block = trimesh.boolean.intersection([body, trimesh.creation.box(bounds=[[x_back, -50, G.Z_BLOCK0], [100, 50, G.Z_LEDGE1]])], engine='manifold')
    m = trimesh.boolean.union([bar, block], engine='manifold')
    below = rotate_bar(trimesh.creation.box(bounds=[[-50, -60, -200], [100, 0, 200]]))   # everything below the plane of the bottom face
    channel = G.ledge_channel(D.RUN_CLEARANCE, D.END_CLEARANCE)
    return trimesh.boolean.difference([m, below, channel], engine='manifold')


def to_right(m):
    m = m.copy(); m.apply_scale([1, 1, -1]); m.apply_translation([0, 0, G.Z_FRAME]); m.fix_normals()
    return m


if __name__ == '__main__':
    rl = ledge_left()
    assert rl.is_watertight
    # print: lay it on the bottom plane (rotate atan(T) about X on the left) and then the same path as the other ledges
    rp = rl.copy(); rp.apply_transform(trimesh.transformations.rotation_matrix(-np.arctan(T), [1, 0, 0]))
    r = to_right(rl)                      # assembled (right-side coordinates)
    rp = to_right(rp)
    rp.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rp.apply_translation(-rp.bounds[0])
    # the STL is written in float32 and merged nearly equal vertices (zero-area faces): clean in manifold and check by reloading
    import manifold3d
    for _ in range(3):
        mf = manifold3d.Manifold(manifold3d.Mesh(vert_properties=np.asarray(rp.vertices, np.float32), tri_verts=np.asarray(rp.faces, np.uint32)))
        mf = mf.simplify(0.002) if hasattr(mf, 'simplify') else mf
        mm = mf.to_mesh(); rp = trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))
        rp.apply_translation(-rp.bounds[0])
        t = trimesh.Trimesh(np.asarray(rp.vertices, np.float32).astype(float), rp.faces)
        if t.is_watertight and t.area_faces.min() > 0: break
    print('reloaded STL watertight:', t.is_watertight)
    # checks
    zs = rp.vertices[:, 2]; base = rp.vertices[zs < 0.01]
    print('flat bottom face: %d vertices at z=0, contact area ~%.0f mm2' % (len(base), rp.section(plane_origin=[0, 0, 0.1], plane_normal=[0, 0, 1]).to_2D()[0].area))
    q = D.frame()
    print('assembled interference: %.2f mm3; worst while sliding: %.2f mm3' % (
        trimesh.boolean.intersection([r, q], engine='manifold').volume, RD.assembly_interference(r, q)))
    tip = r.vertices[r.vertices[:, 2] > 129]
    print('free end: floor rises %.1f mm (%.1f degrees)' % (tip[:, 1].min() - 0.0, DEG))
    n = 'tablet_stand_right_v2_ledge_straight_%gdeg_%dholes' % (DEG, D.N_HOLES)
    rp.export(os.path.join(G.HERE, 'stl', n + '.stl'))
    trimesh.util.concatenate([q, r]).export(os.path.join(G.HERE, 'stl', n + '_assembled.stl'))
    print(n, rp.extents.round(1), '%.1f cm3' % (rp.volume / 1000))
