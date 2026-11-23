# -*- coding: utf-8 -*-
"""Right side v2, tablet in LANDSCAPE (20/11/2026). Result of v1 with the tablet in landscape on the short 5 degree ledge: level 0,
but "I didn't like the Met's clock showing" (the round dial showed above the tablet) and "the dovetail still
isn't firm" (0.20 per side along the run, 0.10 in the last 8 mm).
  - new taller frame: BASE (tablet floor below the top of the machine) from 190 to 142 -> top of the tablet in landscape
    (149.4 x cos 10 = 147.1 above the floor) ~5 above the top of the machine, covering the dial. The frame's tongue keeps
    the design value of 0.30, so the old ledges also fit it.
  - new ledge: channel 0.10 per side along the run and 0.00 in the last 8 mm (a real squeeze next to the stop; if it does not go
    all the way in, sand the flanks of the tongue), 4.5 degree compensation (5 gave 0 with the looser fit), "4.5°" engraved.
Usage: python -I landscape_v2.py [base=142] [tilt=4.5] [run_clearance=0.10] [end_clearance=0.0] [mark=1] [only=ledge]"""
import os, sys
ARGS = dict(base='142', tilt='4.5', run_clearance='0.10', end_clearance='0.0', mark='1', only='')
ARGS.update(dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a))
sys.argv = [sys.argv[0]] + ['%s=%s' % kv for kv in ARGS.items()]
import numpy as np
import trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import right_stand as D
import marked_ledges as RM
G = D.G

if __name__ == '__main__':
    q = D.frame()
    r = D.ledge()
    gr = '%g°' % D.TILT
    if ARGS['mark'] != '0':   # mark=0: without the engraved text (request 21/11/2026)
        g, w = RM.engraving(gr)
        r = trimesh.boolean.difference([r, g], engine='manifold')
    if ARGS['only'] == 'ledge':   # only=ledge: only the ledge, saved with the degrees in the name (does not overwrite v2)
        assert r.is_watertight
        rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rq.apply_translation(-rq.bounds[0])
        n = 'tablet_stand_right_v2_ledge_%gdeg%s.stl' % (D.TILT, ('' if ARGS['mark'] != '0' else '_nomark') + ('' if D.N_HOLES == 5 else '_%dholes' % D.N_HOLES))
        rq.export(os.path.join(G.HERE, 'stl', n)); print(n, rq.extents.round(1), 'channel %.2f/%.2f' % (D.RUN_CLEARANCE, D.END_CLEARANCE)); sys.exit()
    for n, m in (('frame', q), ('ledge', r)):
        assert m.is_watertight, n
        print('%s: %s, %.1f cm3' % (n, m.extents.round(1), m.volume / 1000))
    d, crosses = D.check_button_clearance(q)
    print('BASE %.0f: face at X %.1f, minimum clearance to the button %.2f (crosses %s); top of the landscape tablet %.1f above the machine'
          % (D.BASE, D.XF, d, crosses, 149.4 * np.cos(np.radians(10)) - D.BASE))
    print('channel: %.2f run / %.2f end per side; compensation %s' % (D.RUN_CLEARANCE, D.END_CLEARANCE, gr))
    A = G.HERE
    trimesh.util.concatenate([q, r]).export(os.path.join(A, 'stl', 'tablet_stand_right_v2_landscape_assembled.stl'))
    rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rq.apply_translation(-rq.bounds[0])
    qq = q.copy(); qq.apply_translation(-qq.bounds[0])
    qq.export(os.path.join(A, 'stl', 'tablet_stand_right_v2_frame.stl'))
    rq.export(os.path.join(A, 'stl', 'tablet_stand_right_v2_ledge.stl'))
    print('print: frame', qq.extents.round(1), ' ledge', rq.extents.round(1))
