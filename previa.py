# -*- coding: utf-8 -*-
"""Previa: montagem (original x v1) e perfil da junta."""
import os, trimesh, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
AQUI = os.path.dirname(os.path.abspath(__file__))
q = trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_esq_v1_montado.stl'))
o = trimesh.load(os.path.join(AQUI, 'origem', 'Meticulous_tablet_stand_left.stl'))
fig = plt.figure(figsize=(16, 7))
def vista(ax, m, cor, tit):
    tri = m.vertices[m.faces][:, :, [2, 0, 1]]   # Z largura -> x, X prof -> y, Y altura -> z
    n = m.face_normals[:, [2, 0, 1]]; l = np.clip(n @ np.array([0.4, -0.6, 0.7]), 0.15, 1)
    ax.add_collection3d(Poly3DCollection(tri, facecolors=[(cor[0]*v, cor[1]*v, cor[2]*v) for v in l], edgecolor='none'))
    ax.set_xlim(-100, 80); ax.set_ylim(-40, 140); ax.set_zlim(-30, 150); ax.set_box_aspect((1, 1, 1)); ax.view_init(18, -125); ax.set_title(tit); ax.axis('off')
vista(fig.add_subplot(1, 3, 1, projection='3d'), o, (0.9, 0.5, 0.4), 'Original (montado)')
vista(fig.add_subplot(1, 3, 2, projection='3d'), q, (0.35, 0.5, 0.85), 'v1: quadro + regua')
ax = fig.add_subplot(1, 3, 3)
for z, c, lb in ((20, 'b', 'v1 Z=20 (junta)'),):
    s = q.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    for e in s.discrete: ax.plot(e[:, 0], e[:, 1], c)
s = o.section(plane_origin=[0, 0, 20], plane_normal=[0, 0, 1])
for e in s.discrete: ax.plot(e[:, 0], e[:, 1], 'r', lw=0.6)
ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_title('Perfil: original (vermelho) x v1 (azul)'); ax.set_xlim(-3, 100)
plt.tight_layout(); plt.savefig(os.path.join(AQUI, 'saida', 'previa_v1.png'), dpi=80)
