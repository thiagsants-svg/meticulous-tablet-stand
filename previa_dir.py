# -*- coding: utf-8 -*-
"""Previa do lado direito: perfil com a maquina, o botao e o tablet."""
import os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trimesh, gerar_suporte_dir as D
m = trimesh.load(os.path.join(D.G.AQUI, 'stl', 'Suporte_tablet_dir_v1_montado.stl'))
fig, ax = plt.subplots(figsize=(9, 9))
s = m.section(plane_origin=[0, 0, 20], plane_normal=[0, 0, 1])
for e in s.discrete: ax.plot(e[:, 0], e[:, 1], 'b', lw=1.5)
ax.add_patch(plt.Rectangle((D.XF, D.YT - 260), D.G.COLUNA, 260, color='0.75', label='maquina (50,6)'))
ax.add_patch(plt.Rectangle((D.XF - D.BOTAO_SAI, D.YT - D.BOTAO_BASE), D.BOTAO_SAI, D.BOTAO_BASE - D.BOTAO_TOPO, color='orange', alpha=.7, label='botao (34,13 x 65..113)'))
c = np.cos(np.radians(10)); sn = np.sin(np.radians(10)); x0, y0 = D.f(4.0) - 7.5 * c, 4.0
ax.add_patch(plt.Polygon([(D.f(4.0) - 7.62, 4), (D.f(4.0), 4), (D.f(4.0) + 245.2 * sn, 4 + 245.2 * c), (D.f(4.0) - 7.62 + 245.2 * sn, 4 + 245.2 * c)], color='0.2', alpha=.35, label='Tab A 10.1 (7,5)'))
ax.set_aspect('equal'); ax.grid(alpha=.3); ax.legend(loc='lower right'); ax.set_xlim(-5, 135); ax.set_ylim(-5, 260)
ax.set_title('Lado direito v1: perfil (Z = 20), base do tablet %.0f mm abaixo do topo' % D.BASE)
plt.tight_layout(); plt.savefig(os.path.join(D.G.AQUI, 'saida', 'previa_dir_v1.png'), dpi=80)
