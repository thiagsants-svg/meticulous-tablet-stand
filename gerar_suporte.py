# -*- coding: utf-8 -*-
"""Suporte de tablet da Meticulous (metade esquerda), versao propria em duas pecas (19/11/2026).

Origem: origem/Meticulous_tablet_stand_left.stl (SketchUp, malha aberta com superficie fantasma).
Perfil do original (X = profundidade, Y = altura, Z = largura):
  barra inclinada 10 graus (frente de (15,3; 4) a (34,7; 114), 4 mm), travessa Y 32..36, perna de tras X 38..42,
  barra de cima Y 110..114 ate X 96,3, gancho X 92,3..96,3 descendo ate Y 67 (vao 50,3 x 43 para pendurar na maquina);
  quadro em Z 0..35, barra de cima + gancho em Z 0..75, degrau (piso 4 + labio 4 x 13) em Z -95..37 com passa-cabo.

Mudancas:
  1. duas pecas que imprimem SEM suporte: quadro deitado (perfil na mesa: camadas no plano do gancho, que fica forte)
     e regua do degrau deitada no piso; unidas por rabo de andorinha de 20 graus que trava a regua para baixo e de um lado.
  2. travessa de baixo (Y 7..11) fechando o triangulo da base; bloco traseiro na regua so junto ao quadro.
  3. cantos internos com raio (2 mm; 1 mm nas quinas externas) no lugar de quinas vivas.
  4. vao do tablet e altura do labio como parametros (vao=, labio=), para ajustar depois de medir o Galaxy.
Uso: python -I gerar_suporte.py [vao=8.1] [labio=13] [folga=0.30] [justo=0.15] [coluna=50.6] [folga_col=0.25]
"""
import os, sys, json
import numpy as np
import trimesh
from shapely.geometry import Polygon, box, Point, LineString
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
ARG = dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a)
# tablet: Galaxy Tab A 10.1 (2019) SM-T515, 245,2 x 149,4 x 7,5 (ficha tecnica), EM PE e SEM CAPA (usuario, 19/11/2026).
# Inclinado 10 graus, ocupa 7,5 / cos 10 = 7,62 na horizontal; + ~0,5 de folga = 8,1 (original 11,3)
VAO = float(ARG.get('vao', 8.1))        # entre a face interna do labio e a frente da barra, no nivel do piso
COSTAS_H, COSTAS_E = 10.0, 3.0          # parede traseira do canal no degrau inteiro (nova): altura e espessura
LABIO = float(ARG.get('labio', 13.0))   # altura do labio a partir da mesa (original 13)
FOLGA = float(ARG.get('folga', 0.30))   # por lado no rabo de andorinha (D63-T05: 0,30 a menor que deslizou livre; 0,20 nao deslizou)
# trecho final justo junto ao batente (pedido 19/11/2026: "o deslize mais justo que temos"): ultimos 8 mm com 0,15 por lado,
# receita do FID-T04 (rabo de andorinha 20 graus, 0,30 no curso + 0,15 nos ultimos 8 mm: "trava e solta com uma mao"); rampa de 2 mm
JUSTO = float(ARG.get('justo', 0.15))
L_JUSTO, L_RAMPA = 8.0, 2.0
# coluna da maquina onde o gancho encaixa: 50,6 MEDIDO pelo usuario com paquimetro em 19/11/2026 (o original tinha vao 50,3,
# menor que a coluna). Vao CAD = medida + 0,25 por lado; aberturas impressas saem 0,1 a 0,25 menores (D63-M01), sobra ~0,1 a 0,15 por lado.
COLUNA = float(ARG.get('coluna', 50.6))
FOLGA_COL = float(ARG.get('folga_col', 0.25))
GX0 = 42.0                                 # face interna da perna
GX1 = GX0 + COLUNA + 2 * FOLGA_COL         # face interna do gancho (original 92,3)
GX2 = GX1 + 4.0                            # face externa do gancho
RI_COL = 0.8                               # raio nos dois cantos que tocam a coluna (quina da maquina e reta)

inc = (34.7 - 15.3) / 110.0               # inclinacao da frente da barra (x por y)
f = lambda y: 15.3 + inc * (y - 4.0)      # frente da barra inclinada
PISO, BLOCO_Y, PE_Y = 4.0, 7.0, 7.2       # piso da regua, topo do bloco traseiro, base da travessa de baixo
XL = 15.3 - VAO                           # face interna do labio
X0 = XL - 4.0                             # frente do labio
BL_X0, BL_X1 = f(BLOCO_Y), 37.6           # bloco traseiro da regua (perna em 38,0)
CAUDA_XC, CAUDA_W, CAUDA_H, ANG = 27.0, 6.0, 4.0, np.radians(20)
Z_REG0, Z_REG1, Z_BLOCO0 = -95.0, 37.0, -5.0
Z_QUADRO, Z_GANCHO = 35.0, 75.0


def cauda(c, y_topo, y_fundo):
    """trapezio do rabo de andorinha: largura CAUDA_W - 2c no topo, alargando para baixo a 20 graus"""
    at = CAUDA_W / 2 - c + (BLOCO_Y - y_topo) * np.tan(ANG)
    ab = CAUDA_W / 2 - c + (BLOCO_Y - y_fundo) * np.tan(ANG)
    xc = CAUDA_XC
    return Polygon([(xc - ab, y_fundo), (xc + ab, y_fundo), (xc + at, y_topo), (xc - at, y_topo)])


def arredonda(p, ri=2.0, re=1.0):
    p = p.buffer(ri, join_style=1, quad_segs=16).buffer(-ri, join_style=1, quad_segs=16)
    return p.buffer(-re, join_style=1, quad_segs=16).buffer(re, join_style=1, quad_segs=16)


def perfil_quadro():
    barra = Polygon([(f(PE_Y), PE_Y), (f(PE_Y) + 4, PE_Y), (38.7, 114), (34.7, 114)])
    partes = [barra,
              box(f(32), 32, 42, 36),            # travessa do meio (original)
              box(f(PE_Y), PE_Y, 42, PE_Y + 4),  # travessa de baixo (nova)
              box(38, 0, 42, 114),               # perna de tras
              box(34.7, 110, GX2, 114),          # barra de cima
              box(GX1, 67, GX2, 114)]            # gancho
    p = canto_coluna(arredonda(unary_union(partes)))
    lingua = cauda(FOLGA, PE_Y + 0.5, BLOCO_Y - CAUDA_H + 0.5)   # 0,5 de vao no fundo; sobe ate dentro da travessa
    return unary_union([p, lingua]).buffer(0)


def perfil_gancho():
    return canto_coluna(arredonda(unary_union([box(42 - 3, 110, GX2, 114), box(GX1, 67, GX2, 114)])))


def canto_coluna(p):
    """refaz o vao da coluna com cantos de raio RI_COL (o raio de 2 faria a quina reta da maquina apoiar no arredondado)"""
    vao = box(GX0, 60, GX1, 110 - RI_COL).union(box(GX0 + RI_COL, 60, GX1 - RI_COL, 110))
    vao = vao.union(Point(GX0 + RI_COL, 110 - RI_COL).buffer(RI_COL, quad_segs=16)).union(Point(GX1 - RI_COL, 110 - RI_COL).buffer(RI_COL, quad_segs=16))
    return p.difference(vao).buffer(0)


def extrude(poly, z0, z1):
    m = trimesh.creation.extrude_polygon(poly, z1 - z0)
    m.apply_translation([0, 0, z0])
    return m


def regua(pc_z=-30.0, pc_comp=13.0, furos=None, inclina=0.0, folga_curso=None, folga_fim=None, ext_fora=0.0, costas_ext=6.7, passa_cabo=True, com_canal=True):
    base = arredonda(unary_union([box(X0, 0, f(PISO) + 4 * 0, PISO), box(X0, 0, XL, LABIO),
                                  Polygon([(X0, 0), (f(0) + COSTAS_E, 0), (f(PISO) + COSTAS_E, PISO), (X0, PISO)]),
                                  # parede traseira na linha da barra (10 graus): com o tablet em pe (149 de largura) e o quadro so numa
                                  # ponta (Z 0..35), sem ela a borda de baixo pode escorregar para tras e o tablet torce para o lado livre
                                  Polygon([(f(0), 0), (f(0) + COSTAS_E, 0), (f(COSTAS_H) + COSTAS_E, COSTAS_H), (f(COSTAS_H), COSTAS_H)])]), 1.0, 0.8)
    bloco = arredonda(unary_union([box(X0, 0, XL, LABIO), Polygon([(X0, 0), (BL_X1, 0), (BL_X1, BLOCO_Y), (BL_X0, BLOCO_Y), (f(PISO), PISO), (X0, PISO)])]), 1.0, 0.8)
    a = extrude(base, Z_REG0, Z_BLOCO0 + 1)
    b = extrude(bloco, Z_BLOCO0, Z_REG1)
    pecas = [a, b]
    if ext_fora:
        # 20/11/2026, tablet DEITADO: prolonga a regua para FORA do quadro (alem da ponta aberta do canal, Z > Z_REG1), so com o
        # perfil do degrau (piso + labio + parede). Na montagem o quadro passa por cima desse trecho ate o batente: a travessa de
        # baixo e a perna comecam em Y PE_Y (7,2) e a frente da barra em X ~15,9, entao a parede traseira ali fica com costas_ext
        # (6,7: 0,5 abaixo da travessa); labio e piso estao em X < 15,9 e nao cruzam. O canal (X 24..30) nao existe nesse perfil.
        ext = arredonda(unary_union([box(X0, 0, f(PISO), PISO), box(X0, 0, XL, LABIO),
                                     Polygon([(X0, 0), (f(0) + COSTAS_E, 0), (f(PISO) + COSTAS_E, PISO), (X0, PISO)]),
                                     Polygon([(f(0), 0), (f(0) + COSTAS_E, 0), (f(costas_ext) + COSTAS_E, costas_ext), (f(costas_ext), costas_ext)])]), 1.0, 0.8)
        pecas.append(extrude(ext, Z_REG1 - 1, Z_REG1 + ext_fora))
    m = trimesh.boolean.union(pecas, engine='manifold')
    if inclina:
        # compensacao de caimento (20/11/2026: o lado direito impresso ficou 3 graus inclinado com o peso do tablet, ponta de dentro
        # mais baixa): fora do bloco do rabo de andorinha (Z < Z_BLOCO0, ponta livre da regua) o piso, o labio e a parede sobem
        # tan(inclina) por mm; a face de baixo continua plana (desloca proporcional a y ate a altura do piso). O bloco e o canal
        # nao mudam, entao o encaixe no quadro e o mesmo.
        v = m.vertices.copy()
        dz = np.clip(Z_BLOCO0 - v[:, 2], 0, None)
        v[:, 1] += np.tan(np.radians(inclina)) * dz * np.clip(v[:, 1] / PISO, 0, 1)
        m = trimesh.Trimesh(v, m.faces, process=True)
    # canal do rabo de andorinha, aberto na ponta Z 37 e fechado em Z 0 (batente)
    # folga efetiva por lado contra a lingua do quadro (que e feita com FOLGA): por padrao FOLGA no curso e JUSTO no fim;
    # folga_curso / folga_fim menores estreitam so o canal da regua (reimprimir so a regua para apertar)
    canal = canal_regua(folga_curso, folga_fim)
    # passa-cabo: furo oblongo no piso, largura = vao do tablet (max. 9); original: centro em Z -30 (meio do degrau), 13 de comprido
    w = min(9.0, VAO); r = w / 2; meio = pc_comp / 2 - r
    pc = LineString([(XL + r, pc_z - meio), (XL + r, pc_z + meio)]).buffer(r, quad_segs=24)
    if furos:   # varios furos retangulares (cantos r 1) separados por pontes: lista de (z0, z1)
        pc = unary_union([box(XL + 1.3, z0 + 1, XL + w - 1.3, z1 - 1).buffer(1.0, quad_segs=8) for z0, z1 in furos])   # 0,3 longe das paredes do canal (evita lascas na malha)
    pcs = list(pc.geoms) if hasattr(pc, 'geoms') else [pc]
    furo = trimesh.util.concatenate([trimesh.creation.extrude_polygon(x, 40) for x in pcs])   # em XZ: extrudar em Y (40: passa o piso mesmo com compensacao)
    furo.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))   # (x, y_pol, z) -> (x, -z, y_pol): y do poligono vira Z
    furo.apply_translation([0, 30, 0])   # Y -10..30
    tira = ([canal] if com_canal else []) + ([furo] if passa_cabo else [])
    if tira:
        m = trimesh.boolean.difference([m] + tira, engine='manifold')
    return m


def canal_regua(folga_curso=None, folga_fim=None):
    """volume do canal do rabo de andorinha da regua (coordenadas da esquerda)"""
    fc = FOLGA if folga_curso is None else folga_curso
    ff = JUSTO if folga_fim is None else folga_fim
    canal = extrude(cauda(FOLGA - fc, BLOCO_Y + 1, BLOCO_Y - CAUDA_H), L_JUSTO + L_RAMPA, Z_REG1 + 1)
    aperto = FOLGA - ff   # o canal estreita isso por lado no trecho final (a lingua e a mesma)
    justo = extrude(cauda(aperto, BLOCO_Y + 1, BLOCO_Y - CAUDA_H), 0.0, L_JUSTO)
    rampa = trimesh.util.concatenate([extrude(cauda(aperto, BLOCO_Y + 1, BLOCO_Y - CAUDA_H), L_JUSTO - 0.01, L_JUSTO),
                                      extrude(cauda(FOLGA - fc, BLOCO_Y + 1, BLOCO_Y - CAUDA_H), L_JUSTO + L_RAMPA, L_JUSTO + L_RAMPA + 0.01)]).convex_hull
    canal = trimesh.boolean.union([canal, justo, rampa], engine='manifold')
    return canal


def quadro():
    a = extrude(perfil_quadro(), 0, Z_QUADRO)
    b = extrude(perfil_gancho(), Z_QUADRO - 1, Z_GANCHO)
    return trimesh.boolean.union([a, b], engine='manifold')


if __name__ == '__main__':
    q, r = quadro(), regua()
    for n, m in (('quadro', q), ('regua', r)):
        assert m.is_watertight, n
        print('%s: %.1f x %.1f x %.1f, %.1f cm3, ~%.1f g PETG macico' % (n, *m.extents, m.volume / 1000, m.volume / 1000 * 1.27))
    # montagem (para conferencia e previa), no sistema do original
    trimesh.util.concatenate([q, r]).export(os.path.join(AQUI, 'stl', 'Suporte_tablet_esq_v1_montado.stl'))
    # orientacao de impressao: quadro com Z 0 na mesa (ja esta); regua com o piso (Y 0) na mesa: Y -> Z
    rq = r.copy(); rq.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    rq.apply_translation(-rq.bounds[0]); qq = q.copy(); qq.apply_translation(-qq.bounds[0])
    qq.export(os.path.join(AQUI, 'stl', 'Suporte_tablet_esq_v1_quadro.stl'))
    rq.export(os.path.join(AQUI, 'stl', 'Suporte_tablet_esq_v1_regua.stl'))
    print('regua impressao:', rq.extents.round(1), ' quadro impressao:', qq.extents.round(1))
    json.dump(dict(vao=VAO, labio=LABIO, folga=FOLGA, justo=JUSTO, l_justo=L_JUSTO, coluna=COLUNA, folga_col=FOLGA_COL, vao_gancho=GX1 - GX0), open(os.path.join(AQUI, 'saida', 'parametros_v1.json'), 'w'))
