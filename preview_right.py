# -*- coding: utf-8 -*-
"""Preview of the right side: profile with the machine, the button and the tablet."""
import os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trimesh, right_stand as D
m = trimesh.load(os.path.join(D.G.HERE, 'stl', 'tablet_stand_right_v1_assembled.stl'))
fig, ax = plt.subplots(figsize=(9, 9))
s = m.section(plane_origin=[0, 0, 20], plane_normal=[0, 0, 1])
for e in s.discrete: ax.plot(e[:, 0], e[:, 1], 'b', lw=1.5)
ax.add_patch(plt.Rectangle((D.XF, D.YT - 260), D.G.COLUMN, 260, color='0.75', label='machine (50.6)'))
ax.add_patch(plt.Rectangle((D.XF - D.BUTTON_PROTRUSION, D.YT - D.BUTTON_BOTTOM), D.BUTTON_PROTRUSION, D.BUTTON_BOTTOM - D.BUTTON_TOP, color='orange', alpha=.7, label='button (34.13 x 65..113)'))
c = np.cos(np.radians(10)); sn = np.sin(np.radians(10)); x0, y0 = D.f(4.0) - 7.5 * c, 4.0
ax.add_patch(plt.Polygon([(D.f(4.0) - 7.62, 4), (D.f(4.0), 4), (D.f(4.0) + 245.2 * sn, 4 + 245.2 * c), (D.f(4.0) - 7.62 + 245.2 * sn, 4 + 245.2 * c)], color='0.2', alpha=.35, label='Tab A 10.1 (7.5)'))
ax.set_aspect('equal'); ax.grid(alpha=.3); ax.legend(loc='lower right'); ax.set_xlim(-5, 135); ax.set_ylim(-5, 260)
ax.set_title('Right side v1: profile (Z = 20), bottom of the tablet %.0f mm below the top' % D.BASE)
plt.tight_layout(); plt.savefig(os.path.join(D.G.HERE, 'output', 'preview_right_v1.png'), dpi=80)
