# -*- coding: utf-8 -*-
"""Lado direito, 20/11/2026: as duas reguas de teste (compensacao 2,5 e 5 graus, rabo de andorinha 0,20/0,10) com a
compensacao GRAVADA na frente do labio ("2,5°" e "5°", 0,6 de fundo, na ponta de fora junto ao bloco, que nao inclina).
O texto le de frente (quem olha a maquina). Saida: stl/Suporte_tablet_dir_v1_regua_{2,5|5}graus_marcada.stl
Uso: python -I reguas_marcadas.py [graus=2.5,5]"""
import os, sys
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely import affinity
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_suporte_dir as D
G = D.G

GRAUS = [float(x) for x in G.ARG.get('graus', '2.5,5').split(',')]
ALT, FUNDO = 7.0, 0.6          # altura das letras, profundidade da gravacao


def texto(s):
    tp = TextPath((0, 0), s, size=10, prop=FontProperties(family='DejaVu Sans', weight='bold'))
    pol = None
    for anel in tp.to_polygons():
        if len(anel) < 3: continue
        p = Polygon(anel).buffer(0)
        pol = p if pol is None else pol.symmetric_difference(p)   # par-impar: furos do "°"
    x0, y0, x1, y1 = pol.bounds
    k = ALT / (y1 - y0)
    return affinity.scale(affinity.translate(pol, -x0, -y0), k, k, origin=(0, 0))


def gravacao(s):
    """texto em (z, y) na face da frente do labio (X = G.X0), centrado na ponta de fora (Z -2..35), entrando FUNDO em X"""
    p = texto(s)
    w = p.bounds[2]
    zc, yc = 16.5, (G.LABIO) / 2 + 0.5        # meio do trecho Z -2..35 e do labio (piso na mesa = Y 0)
    p = affinity.translate(p, zc - w / 2, yc - ALT / 2)
    m = trimesh.util.concatenate([trimesh.creation.extrude_polygon(g, FUNDO + 1) for g in (p.geoms if hasattr(p, 'geoms') else [p])])
    # poligono em (a=z, b=y), extrusao em c: (a, b, c) -> (x = X0 - 1 + c, y = b, z = a)
    T = np.array([[0, 0, 1, G.X0 - 1], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)
    m.apply_transform(T)
    m.fix_normals()
    return m, w


if __name__ == '__main__':
    for gr in GRAUS:
        D.INCLINA = gr
        r = D.regua()
        s = ('%g°' % gr).replace('.', ',')
        g, w = gravacao(s)
        r = trimesh.boolean.difference([r, g], engine='manifold')
        assert r.is_watertight
        r.export(os.path.join(G.AQUI, 'stl', 'Suporte_tablet_dir_v1_regua_%sgraus_montada_marcada.stl' % ('%g' % gr).replace('.', ',')))
        rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rq.apply_translation(-rq.bounds[0])
        nome = 'Suporte_tablet_dir_v1_regua_%sgraus_marcada.stl' % ('%g' % gr).replace('.', ',')
        rq.export(os.path.join(G.AQUI, 'stl', nome))
        print('%s: "%s" %.1f mm de largo; regua %s, %.2f cm3' % (nome, s, w, rq.extents.round(1), rq.volume / 1000))
