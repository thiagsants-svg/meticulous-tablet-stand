# -*- coding: utf-8 -*-
"""Right side, STRAIGHT LEDGE with the 90 degree USB-C ADAPTER and the CABLE LEAVING BEHIND the tablet (22/11/2026).
The user sent the listing's dimensions: body 19.2 (length) x 12.8 (width) x 8.2 (thickness), male plug sticking out 7.2,
coming out of the wide face next to one end; female at the other end. "The cable will come out behind the tablet, I don't think
the ledge needs to grow much, just open up the space."
  - the adapter sits with the plug up in the tablet's port (axis tilted 10 degrees like the tablet), the body lying down
    going BACKWARDS under the floor (12.8 along the ledge), the female end facing back: the cable leaves behind the tablet,
    towards the machine. No keel: the ledge stays 13 high; the body's void is open underneath and at the back.
  - the void (envelope of the body + 0.6, collar 5.5 x 1.5 in the slit) is continuous along the ledge, from the stop end to 2 mm
    from the free end: the tablet can sit at any position (port from Z ~8 to ~122). Under the joint block the void becomes a
    tilted recess under the block (>= 1.5 left under the channel).
  - no floor in front of the slit (the body passes there): the tablet rests on the back strip, on the frame's 10 degree ramp
    and on the lip (which keeps it from going forwards; clearance 0.25).
  - void roof almost horizontal (10 degrees): prints with the standard PETG supports (tree, on the build plate only).
  - 1.5 degree compensation: the 3.5 straight one with the tight channel ended up at -2.
Usage: python -I ledge_cable_back.py [deg=1.5] [plug_offset=5.0] [body_clearance=0.6] [front_clearance=2.5] [top_clearance=1.0]
       [side_clearance=2.0] [collar=6.5] [lip_extra=2.5] [port_range=30,100]"""
import os, sys
ARGS = dict(base='142', deg='1.5', run_clearance='0.10', end_clearance='0.0', tilt='0', plug_offset='5.0', body_clearance='0.6',
            front_clearance='2.5', top_clearance='1.0', side_clearance='2.0', collar='6.5', lip_extra='2.5', port_range='30,100')
ARGS.update(dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a))
sys.argv = [sys.argv[0]] + ['%s=%s' % kv for kv in ARGS.items()]
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import right_stand as D
import ledge_landscape as RD
import ledge_usbc_tunnel as RA
G = D.G

DEG = float(ARGS['deg']); T = np.tan(np.radians(DEG))
Z_PIVOT = -2.0
C_L, C_W, C_E, PLUG, COLLAR_H = 19.2, 12.8, 8.2, 7.2, 1.5    # body, plug, collar height
# 22/11/2026 "I want plenty of clearance around the adapter": underneath, behind and along the ledge the void is already open; the
# clearances that limited it were the FRONT one (lip), the TOP one (roof of the back strip) and the collar slit:
#   front 2.5 (the lip grows LIP_EXTRA forwards so it does not get thinner), top 1.0, ends 2.0, slit 6.5 (tablet is 7.6)
COLLAR_T = float(ARGS['collar'])
FF, FT, FL, LX = (float(ARGS[k]) for k in ('front_clearance', 'top_clearance', 'side_clearance', 'lip_extra'))
A = float(ARGS['plug_offset'])                 # centre of the plug to the front end of the body (estimated)
FC = float(ARGS['body_clearance'])
XC = (G.XL + G.f(G.FLOOR)) / 2                 # tablet port at the floor
ANG = np.radians(10)
AXIS = np.array([np.sin(ANG), np.cos(ANG)])    # plug axis (rises tilted like the tablet)
U = np.array([np.cos(ANG), -np.sin(ANG)])      # along the body, backwards
O = np.array([XC, G.FLOOR]) - COLLAR_H * AXIS  # centre of the top face of the body, on the plug axis
# port range (right-side Z). The lip is only held to the rest by the walls at the two ends (the void runs along the whole
# ledge), so they are ~5 mm: port from 11 to 119 (portrait tablet of 149: middle between 11 and 119)
# 22/11/2026 "increase support at the sides": the void is only in the MIDDLE (adjusting the tablet's centre), and both ends of
# the ledge get a full floor again joining lip and back wall (tablet support at the sides and a stiffer ledge).
# port_range= from 30 to 100 (ledge centre ~64, +-35): full floor at Z -2..~22 and ~108..130
PORT_RANGE = tuple(float(x) for x in ARGS.get('port_range', '30,100').split(','))


def section_profile():
    """void in the XY plane: body + clearance, extended backwards (cable plug), plus the collar slit up to the floor"""
    def rect(u0, u1, v0, v1):
        return Polygon([tuple(O + U * u + AXIS * v) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))])
    body = rect(-A - FF, 80, -C_E - 20, FT)                    # open backwards (u up to 80) and underneath
    collar = rect(-COLLAR_T / 2, COLLAR_T / 2, -1, COLLAR_H + 3)   # slit: goes through the floor
    return unary_union([body, collar]).buffer(0)


def ledge_left():
    body = G.ledge(tilt=0.0, with_channel=False, cable_hole=False)
    body = trimesh.boolean.union([body, RA.cuboid(G.X0 - LX, 0, G.Z_LEDGE0, G.X0 + 1, G.LIP, G.Z_LEDGE1)], engine='manifold')   # lip thicker towards the front
    bar = body.copy(); bar.apply_transform(trimesh.transformations.rotation_matrix(np.arctan(T), [1, 0, 0], point=[0, 0, Z_PIVOT]))
    block = trimesh.boolean.intersection([body, RA.cuboid(G.f(G.FLOOR), -50, G.Z_BLOCK0, 100, 50, G.Z_LEDGE1)], engine='manifold')
    m = trimesh.boolean.union([bar, block], engine='manifold')
    # port range -> void range in Z (body is 12.8 along the ledge), in left-side coordinates (z = 35 - z_right)
    z0d, z1d = PORT_RANGE[0] - C_W / 2 - FL, PORT_RANGE[1] + C_W / 2 + FL
    void = G.extrude(section_profile(), G.Z_FRAME - z1d, G.Z_FRAME - z0d)
    void.apply_transform(trimesh.transformations.rotation_matrix(np.arctan(T), [1, 0, 0], point=[0, 0, Z_PIVOT]))
    below = RA.cuboid(-50, -60, -200, 100, 0, 200)
    below.apply_transform(trimesh.transformations.rotation_matrix(np.arctan(T), [1, 0, 0], point=[0, 0, Z_PIVOT]))
    return trimesh.boolean.difference([m, below, void, G.ledge_channel(D.RUN_CLEARANCE, D.END_CLEARANCE)], engine='manifold')


if __name__ == '__main__':
    s = section_profile()
    print('void: X %.1f..%.1f; top of the body on the axis Y %.2f; front end of the body at X %.2f (inner lip %.1f)'
          % (s.bounds[0], s.bounds[2], O[1], (O + U * (-A))[0], G.XL))
    rl = ledge_left(); assert rl.is_watertight
    rp = rl.copy(); rp.apply_transform(trimesh.transformations.rotation_matrix(-np.arctan(T), [1, 0, 0], point=[0, 0, 0]))
    r = RA.to_right(rl); rp = RA.to_right(rp)
    rp.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rp.apply_translation(-rp.bounds[0])
    rp = RA.clean_mesh(rp)
    q = D.frame()
    print('assembled interference %.2f mm3; worst while sliding %.2f mm3; pieces %d' % (
        trimesh.boolean.intersection([r, q], engine='manifold').volume, RD.assembly_interference(r, q), len(rp.split(only_watertight=False))))
    n = 'tablet_stand_right_v2_ledge_cable_back_%gdeg' % DEG
    rp.export(os.path.join(G.HERE, 'stl', n + '.stl'))
    trimesh.util.concatenate([q, r]).export(os.path.join(G.HERE, 'stl', n + '_assembled.stl'))
    print(n, rp.extents.round(1), '%.1f cm3' % (rp.volume / 1000), 'watertight', trimesh.load(os.path.join(G.HERE, 'stl', n + '.stl')).is_watertight)
