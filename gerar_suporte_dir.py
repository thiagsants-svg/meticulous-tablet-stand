# -*- coding: utf-8 -*-
"""Suporte de tablet Meticulous, LADO DIREITO (19/11/2026): tablet em pe na frente da parte direita (tela e botao),
como na foto do usuario segurando o Tab A 10.1 ali. Reaproveita de gerar_suporte.py a regua, o rabo de andorinha,
o vao do tablet, a parede traseira e o gancho; o quadro e novo.

Botao da maquina (medido pelo usuario com paquimetro): de 65,07 a 113,08 abaixo do topo, saliente 34,13 da face.
O botao e o "push to brew": nada pode encostar nele. Por isso o quadro forma uma JANELA em volta do botao:
  perna na face so ate PERNA_H abaixo do topo (acima do botao), travessa ali, barra do tablet afastada da face
  (costas da barra a >= botao + FOLGA_BOTAO em toda a faixa do botao, com 5 mm de margem acima e abaixo),
  escora de baixo voltando ate a face abaixo do botao. A posicao horizontal do botao deixa de importar.
Regua: a mesma da esquerda espelhada em Z (estende para dentro da maquina, mesmo lado da barra de cima com gancho;
  a ponta aberta do rabo de andorinha fica do lado de fora).
Uso: python -I gerar_suporte_dir.py [base=190] [furo=12] [ponte=2.5] [n_furos=5] [vao=8.1] [coluna=50.6] ... (os parametros de gerar_suporte.py valem)
  base = quanto a base do tablet (piso do degrau) fica abaixo do topo da maquina.
"""
import os, sys, json
import numpy as np
import trimesh
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_suporte as G

ARG = G.ARG
BASE = float(ARG.get('base', 190.0))   # escolha do usuario 19/11/2026: "Mais baixo (190)" (topo do tablet ~51 acima da maquina)
BOTAO_TOPO, BOTAO_BASE, BOTAO_SAI = 65.07, 113.08, 34.13
FOLGA_BOTAO, MARGEM = 3.0, 5.0
PERNA_H = 55.0                      # perna encosta na face do topo ate 55 abaixo (botao comeca em 65)
# passa-cabo do lado direito (pedido 20/11/2026: ampliar para as laterais e levar para a direita, longe do grupo aquecido):
# centro a PC_Z do lado de fora da regua (Z -2 = ponta de fora, junto a borda direita da maquina), PC_COMP de comprido.
# O plugue USB-C sai do meio da borda de baixo do tablet: com o furo em 45 o tablet fica deslocado para a direita
# (de ~-30 a ~120 em Z, passando ~28 mm alem da ponta de fora da regua), longe da cabeca.
# 20/11/2026, esclarecimento: "no caso de eu precisar puxar o tablet mais para a direita ainda" -> furo corrido do meio ate
# 8 mm da ponta de fora (Z 6..70): o plugue (~12 mm) desce com o centro do tablet entre ~12 e ~64 mm da ponta de fora
PC_Z = float(ARG.get('pc_z', 38.0))
PC_COMP = float(ARG.get('pc_comp', 64.0))
# 20/11/2026: "da para acrescentar varias pontes, o cabo usb c em si eh pequeno" -> no lugar do rasgo corrido, FUROS de
# FURO_COMP separados por pontes de PONTE (piso inteiro, ligam o labio ao resto), a partir de 8 mm da ponta de fora
FURO_COMP = float(ARG.get('furo', 12.0))
PONTE = float(ARG.get('ponte', 2.5))
N_FUROS = int(ARG.get('n_furos', 5))
FUROS = [(6 + i * (FURO_COMP + PONTE), 6 + i * (FURO_COMP + PONTE) + FURO_COMP) for i in range(N_FUROS)]   # em Z do lado direito
# 20/11/2026: impresso, "ficou bom", mas com o peso do tablet ficou 3 graus inclinado (nivel do iPhone), ponta de dentro
# mais baixa (foto). Regua nova com o piso subindo INCLINA graus para dentro a partir do bloco; o quadro nao muda.
# 20/11/2026, depois: "aperta mais o rabo de andorinha, nao ficou firme". So a regua e reimpressa (a lingua do quadro tem
# 0,30 por lado no CAD): canal estreitado para 0,20 por lado no curso (D63-T05: 0,20 foi a primeira que NAO deslizou livre
# numa tampa de 28 mm, ou seja, justo) e 0,10 nos ultimos 8 mm (trava). Subida possivel da lingua (folga / tan 20, calculado):
# 0,82 -> 0,55 no curso e 0,27 no fim. Parte do caimento de 3 graus vinha desse jogo (~1,3 graus calculado com 0,82 em 35 mm),
# por isso a compensacao cai para 2,5 graus.
FOLGA_CURSO = float(ARG.get('folga_curso', 0.20))
FOLGA_FIM = float(ARG.get('folga_fim', 0.10))
INCLINA = float(ARG.get('inclina', 2.5))
BARRA_E = 5.0                       # barra do tablet mais grossa que a do original (4): vao livre maior

YT = G.PISO + BASE                  # topo da maquina = face de baixo da barra de cima
f = G.f
# face da maquina: a costa da barra no alto da faixa do botao tem de ficar a botao + folga da face
y_alto = YT - BOTAO_TOPO + MARGEM
XF = f(y_alto) + BARRA_E + BOTAO_SAI + FOLGA_BOTAO
GX1 = XF + G.COLUNA + 2 * G.FOLGA_COL
GX2 = GX1 + 4.0


def canto_coluna(p):
    r = G.RI_COL
    vao = box(XF, YT - 50, GX1, YT - r).union(box(XF + r, YT - 50, GX1 - r, YT))
    vao = vao.union(Point(XF + r, YT - r).buffer(r, quad_segs=16)).union(Point(GX1 - r, YT - r).buffer(r, quad_segs=16))
    return p.difference(vao).buffer(0)


def perfil_quadro():
    y0 = G.PE_Y
    barra = Polygon([(f(y0), y0), (f(y0) + BARRA_E, y0), (f(YT + 4) + BARRA_E, YT + 4), (f(YT + 4), YT + 4)])
    partes = [barra,
              box(f(y0), y0, XF, y0 + 4),                       # escora de baixo (sobre a regua), ate a face
              box(XF - 4, y0, XF, y0 + 18),                     # sapata na face, abaixo do botao
              box(f(YT - PERNA_H - 4), YT - PERNA_H - 4, XF, YT - PERNA_H),   # travessa acima do botao
              box(XF - 4, YT - PERNA_H - 4, XF, YT + 4),        # perna curta na face
              box(f(YT + 4), YT, GX2, YT + 4),                  # barra de cima
              box(GX1, YT - 43, GX2, YT + 4)]                   # gancho
    p = canto_coluna(G.arredonda(unary_union(partes)))
    lingua = G.cauda(G.FOLGA, y0 + 0.5, G.BLOCO_Y - G.CAUDA_H + 0.5)
    return unary_union([p, lingua]).buffer(0)


def perfil_gancho():
    return canto_coluna(G.arredonda(unary_union([box(XF - 3, YT, GX2, YT + 4), box(GX1, YT - 43, GX2, YT + 4)])))


def quadro():
    a = G.extrude(perfil_quadro(), 0, G.Z_QUADRO)
    b = G.extrude(perfil_gancho(), G.Z_QUADRO - 1, G.Z_GANCHO)
    return trimesh.boolean.union([a, b], engine='manifold')


def regua():
    r = G.regua(furos=[(G.Z_QUADRO - z1, G.Z_QUADRO - z0) for z0, z1 in FUROS], inclina=INCLINA, folga_curso=FOLGA_CURSO, folga_fim=FOLGA_FIM)   # coordenada da esquerda antes do espelho z -> 35 - z
    r.apply_scale([1, 1, -1]); r.apply_translation([0, 0, G.Z_QUADRO])   # z -> 35 - z: regua -2..130, canal -2..35, batente em 35
    r.fix_normals()
    return r


def conferir(q):
    """menor distancia entre o quadro e o volume do botao (caixa de faixa vertical x saliencia), em qualquer Z"""
    bot = box(XF - BOTAO_SAI, YT - BOTAO_BASE, XF, YT - BOTAO_TOPO)
    p = perfil_quadro()
    return p.distance(bot), p.intersects(bot)


if __name__ == '__main__':
    q, r = quadro(), regua()
    for n, m in (('quadro dir', q), ('regua dir', r)):
        assert m.is_watertight, n
        print('%s: %.1f x %.1f x %.1f, %.1f cm3' % (n, *m.extents, m.volume / 1000))
    d, cruza = conferir(q)
    print('face da maquina em X %.1f; topo em Y %.1f; folga minima ate o botao %.2f mm (cruza: %s)' % (XF, YT, d, cruza))
    print('tablet: topo ~%.0f mm acima da maquina' % (245.2 * np.cos(np.radians(10)) - BASE))
    A = G.AQUI
    trimesh.util.concatenate([q, r]).export(os.path.join(A, 'stl', 'Suporte_tablet_dir_v1_montado.stl'))
    rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rq.apply_translation(-rq.bounds[0])
    qq = q.copy(); qq.apply_translation(-qq.bounds[0])
    qq.export(os.path.join(A, 'stl', 'Suporte_tablet_dir_v1_quadro.stl'))
    rq.export(os.path.join(A, 'stl', 'Suporte_tablet_dir_v1_regua.stl'))
    print('impressao: quadro', qq.extents.round(1), ' regua', rq.extents.round(1))
    json.dump(dict(base=BASE, vao=G.VAO, coluna=G.COLUNA, folga_col=G.FOLGA_COL, botao=[BOTAO_TOPO, BOTAO_BASE, BOTAO_SAI],
                   face_x=XF, folga_botao_min=d), open(os.path.join(A, 'saida', 'parametros_dir_v1.json'), 'w'))
