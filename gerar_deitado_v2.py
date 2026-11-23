# -*- coding: utf-8 -*-
"""Lado direito v2, TABLET DEITADO (20/11/2026). Resultado da v1 com o tablet deitado na regua curta de 5 graus: nivel 0,
mas "nao gostei do relogio da Met aparecendo" (o mostrador redondo aparecia acima do tablet) e "o rabo de andorinha ainda
nao ficou firme" (0,20 por lado no curso, 0,10 nos ultimos 8 mm).
  - quadro novo mais alto: BASE (piso do tablet abaixo do topo da maquina) de 190 para 142 -> topo do tablet deitado
    (149,4 x cos 10 = 147,1 acima do piso) ~5 acima do topo da maquina, cobrindo o mostrador. A lingua do quadro continua
    com 0,30 de projeto, entao as reguas antigas tambem entram nele.
  - regua nova: canal 0,10 por lado no curso e 0,00 nos ultimos 8 mm (aperto de verdade junto ao batente; se nao entrar ate o
    fim, lixar os flancos da lingua), compensacao 4,5 graus (5 deu 0 com o encaixe mais solto), "4,5°" gravado.
Uso: python -I gerar_deitado_v2.py [base=142] [inclina=4.5] [folga_curso=0.10] [folga_fim=0.0]"""
import os, sys
ARGS = dict(base='142', inclina='4.5', folga_curso='0.10', folga_fim='0.0', marca='1', so='')
ARGS.update(dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a))
sys.argv = [sys.argv[0]] + ['%s=%s' % kv for kv in ARGS.items()]
import numpy as np
import trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_suporte_dir as D
import reguas_marcadas as RM
G = D.G

if __name__ == '__main__':
    q = D.quadro()
    r = D.regua()
    gr = ('%g°' % D.INCLINA).replace('.', ',')
    if ARGS['marca'] != '0':   # marca=0: sem o texto gravado (pedido 21/11/2026)
        g, w = RM.gravacao(gr)
        r = trimesh.boolean.difference([r, g], engine='manifold')
    if ARGS['so'] == 'regua':   # so=regua: so a regua, salva com os graus no nome (nao sobrescreve a v2)
        assert r.is_watertight
        rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rq.apply_translation(-rq.bounds[0])
        n = 'Suporte_tablet_dir_v2_regua_%sgraus%s.stl' % (('%g' % D.INCLINA).replace('.', ','), ('' if ARGS['marca'] != '0' else '_sem_marca') + ('' if D.N_FUROS == 5 else '_%dfuros' % D.N_FUROS))
        rq.export(os.path.join(G.AQUI, 'stl', n)); print(n, rq.extents.round(1), 'canal %.2f/%.2f' % (D.FOLGA_CURSO, D.FOLGA_FIM)); sys.exit()
    for n, m in (('quadro', q), ('regua', r)):
        assert m.is_watertight, n
        print('%s: %s, %.1f cm3' % (n, m.extents.round(1), m.volume / 1000))
    d, cruza = D.conferir(q)
    print('BASE %.0f: face em X %.1f, folga minima ao botao %.2f (cruza %s); topo do tablet deitado %.1f acima da maquina'
          % (D.BASE, D.XF, d, cruza, 149.4 * np.cos(np.radians(10)) - D.BASE))
    print('canal: %.2f curso / %.2f fim por lado; compensacao %s' % (D.FOLGA_CURSO, D.FOLGA_FIM, gr))
    A = G.AQUI
    trimesh.util.concatenate([q, r]).export(os.path.join(A, 'stl', 'Suporte_tablet_dir_v2_deitado_montado.stl'))
    rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rq.apply_translation(-rq.bounds[0])
    qq = q.copy(); qq.apply_translation(-qq.bounds[0])
    qq.export(os.path.join(A, 'stl', 'Suporte_tablet_dir_v2_quadro.stl'))
    rq.export(os.path.join(A, 'stl', 'Suporte_tablet_dir_v2_regua.stl'))
    print('impressao: quadro', qq.extents.round(1), ' regua', rq.extents.round(1))
