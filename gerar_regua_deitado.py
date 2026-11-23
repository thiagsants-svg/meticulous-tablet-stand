# -*- coding: utf-8 -*-
"""Lado direito, TABLET DEITADO (20/11/2026, pedido "gerar versao para o tablet deitado").
Reaproveita o quadro direito ja impresso (base do tablet 190 abaixo do topo); so a regua e nova:
  - prolongada para FORA da maquina (ext_fora, alem da ponta aberta do canal), ficando Z -100..130 (230 mm, cabe na mesa);
    para dentro continua ate 130, comprimento que ja provou caber (impresso e montado em 20/11);
  - o tablet de 245 fica com o meio perto do quadro (Z ~15): o peso quase nao faz alavanca no rabo de andorinha,
    por isso a compensacao de caimento padrao e 0 (inclina=);
  - sem furos de cabo: deitado, o USB-C fica numa ponta do tablet e o cabo sai de lado;
  - rabo de andorinha apertado (0,20 no curso, 0,10 nos ultimos 8 mm, como as reguas de 2,5/5 graus);
  - "deitado" gravado na frente do labio.
Uso: python -I gerar_regua_deitado.py [fora=98] [inclina=0] [costas_ext=6.7]"""
import os, sys
import numpy as np
import trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_suporte_dir as D
import reguas_marcadas as RM
G = D.G

FORA = float(G.ARG.get('fora', 98.0))
INCL = float(G.ARG.get('inclina', 0.0))
COSTAS_EXT = float(G.ARG.get('costas_ext', 6.7))


def regua():
    r = G.regua(inclina=INCL, folga_curso=D.FOLGA_CURSO, folga_fim=D.FOLGA_FIM, ext_fora=FORA, costas_ext=COSTAS_EXT, passa_cabo=False)
    r.apply_scale([1, 1, -1]); r.apply_translation([0, 0, G.Z_QUADRO]); r.fix_normals()
    g, w = RM.gravacao('deitado')
    return trimesh.boolean.difference([r, g], engine='manifold'), w


def montagem(r, q):
    """o quadro desliza de fora (Z menor) ate o batente: volume de interferencia em varias posicoes"""
    pior = 0.0
    for dz in np.arange(-150, 0.1, 2.0):
        qq = q.copy(); qq.apply_translation([0, 0, dz])
        i = trimesh.boolean.intersection([r, qq], engine='manifold')
        v = i.volume if len(i.faces) else 0.0
        pior = max(pior, v)
        if v > 0.5: print('  interferencia %.1f mm3 com o quadro deslocado %.0f' % (v, dz))
    return pior


if __name__ == '__main__':
    r, w = regua()
    assert r.is_watertight
    q = D.quadro()
    print('regua montada Z %.1f..%.1f, texto %.0f mm; pior interferencia na montagem: %.2f mm3' % (r.bounds[0][2], r.bounds[1][2], w, montagem(r, q)))
    trimesh.util.concatenate([q, r]).export(os.path.join(G.AQUI, 'stl', 'Suporte_tablet_dir_deitado_montado.stl'))
    rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rq.apply_translation(-rq.bounds[0])
    rq.export(os.path.join(G.AQUI, 'stl', 'Suporte_tablet_dir_deitado_regua.stl'))
    print('impressao: regua', rq.extents.round(1), '%.2f cm3' % (rq.volume / 1000))
