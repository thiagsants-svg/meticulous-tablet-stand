# -*- coding: utf-8 -*-
"""Lado direito, REGUA RETA com o ADAPTADOR USB-C 90 graus e o CABO SAINDO POR TRAS do tablet (22/11/2026).
Usuario mandou as cotas do anuncio: corpo 19,2 (comprimento) x 12,8 (largura) x 8,2 (espessura), plugue macho 7,2 para fora,
saindo da face larga junto a uma ponta; femea na outra ponta. "O cabo saira por tras do tablet, acho que nao precisa aumentar
muito a regua, so abrir o espaco."
  - o adaptador fica com o plugue para cima na porta do tablet (eixo inclinado 10 graus como o tablet), o corpo deitado
    indo para TRAS por baixo do piso (12,8 ao longo da regua), a femea virada para tras: o cabo sai atras do tablet, rumo a
    maquina. Nada de quilha: a regua continua com 13 de altura; o vao do corpo e aberto por baixo e por tras.
  - o vao (envoltoria do corpo + 0,6, colar 5,5 x 1,5 no rasgo) e continuo ao longo da regua, da ponta do batente ate 2 mm da
    ponta livre: o tablet pode ficar em qualquer posicao (porta de Z ~8 a ~122). Embaixo do bloco do encaixe o vao vira um
    rebaixo inclinado sob o bloco (sobram >= 1,5 sob o canal).
  - sem piso na frente do rasgo (o corpo passa ali): o tablet apoia na faixa de tras, na rampa de 10 graus do quadro e no
    labio (que o impede de ir para a frente; folga 0,25).
  - teto do vao quase horizontal (10 graus): imprime com o suporte padrao PETG (arvore so na placa).
  - compensacao 1,5 graus: a reta de 3,5 com o canal justo ficou em -2.
Uso: python -I gerar_regua_cabo_tras.py [graus=1.5] [a_plugue=5.0] [folga_corpo=0.6]"""
import os, sys
ARGS = dict(base='142', graus='1.5', folga_curso='0.10', folga_fim='0.0', inclina='0', a_plugue='5.0', folga_corpo='0.6',
            folga_frente='2.5', folga_topo='1.0', folga_lado='2.0', colar='6.5', labio_extra='2.5', porta='30,100')
ARGS.update(dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a))
sys.argv = [sys.argv[0]] + ['%s=%s' % kv for kv in ARGS.items()]
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_suporte_dir as D
import gerar_regua_deitado as RD
import gerar_regua_adaptador as RA
G = D.G

GRAUS = float(ARGS['graus']); T = np.tan(np.radians(GRAUS))
Z_PIVO = -2.0
C_L, C_W, C_E, PLUG, COLAR_H = 19.2, 12.8, 8.2, 7.2, 1.5    # corpo, plugue, altura do colar
# 22/11/2026 "quero bastante folga na regiao do adaptador": por baixo, por tras e ao longo da regua o vao ja e aberto; as
# folgas que limitavam eram a da FRENTE (labio) e a de CIMA (teto da faixa de tras) e o rasgo do colar:
#   frente 2,5 (o labio cresce LABIO_EXTRA para a frente para nao afinar), cima 1,0, pontas 2,0, rasgo 6,5 (tablet tem 7,6)
COLAR_E = float(ARGS['colar'])
FF, FT, FL, LX = (float(ARGS[k]) for k in ('folga_frente', 'folga_topo', 'folga_lado', 'labio_extra'))
A = float(ARGS['a_plugue'])                    # centro do plugue ate a ponta da frente do corpo (estimado)
FC = float(ARGS['folga_corpo'])
XC = (G.XL + G.f(G.PISO)) / 2                  # porta do tablet no piso
ANG = np.radians(10)
EIXO = np.array([np.sin(ANG), np.cos(ANG)])    # eixo do plugue (sobe inclinado como o tablet)
U = np.array([np.cos(ANG), -np.sin(ANG)])      # ao longo do corpo, para tras
O = np.array([XC, G.PISO]) - COLAR_H * EIXO    # centro da face de cima do corpo, no eixo do plugue
# faixa da porta (Z do lado direito). O labio so fica preso ao resto pelas paredes das duas pontas (o vao corre a regua
# inteira), entao elas ficam com ~5 mm: porta de 11 a 119 (tablet em pe de 149: meio entre 11 e 119)
# 22/11/2026 "aumentar sustentacao nas laterais": o vao fica so no MEIO (ajuste do centro do tablet), e as duas pontas da
# regua voltam a ter piso inteiro ligando labio e parede de tras (apoio do tablet nas laterais e regua mais rigida).
# porta= de 30 a 100 (centro da regua ~64, +-35): piso inteiro em Z -2..~22 e ~108..130
PORTA_R = tuple(float(x) for x in ARGS.get('porta', '30,100').split(','))


def secao():
    """vao no plano XY: corpo + folga, prolongado para tras (plugue do cabo), mais o rasgo do colar ate o piso"""
    def ret(u0, u1, v0, v1):
        return Polygon([tuple(O + U * u + EIXO * v) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))])
    corpo = ret(-A - FF, 80, -C_E - 20, FT)                    # aberto para tras (u ate 80) e por baixo
    colar = ret(-COLAR_E / 2, COLAR_E / 2, -1, COLAR_H + 3)    # rasgo: passa o piso
    return unary_union([corpo, colar]).buffer(0)


def regua_esq():
    corpo = G.regua(inclina=0.0, com_canal=False, passa_cabo=False)
    corpo = trimesh.boolean.union([corpo, RA.caixa(G.X0 - LX, 0, G.Z_REG0, G.X0 + 1, G.LABIO, G.Z_REG1)], engine='manifold')   # labio mais grosso para a frente
    barra = corpo.copy(); barra.apply_transform(trimesh.transformations.rotation_matrix(np.arctan(T), [1, 0, 0], point=[0, 0, Z_PIVO]))
    bloco = trimesh.boolean.intersection([corpo, RA.caixa(G.f(G.PISO), -50, G.Z_BLOCO0, 100, 50, G.Z_REG1)], engine='manifold')
    m = trimesh.boolean.union([barra, bloco], engine='manifold')
    # faixa da porta -> faixa do vao em Z (corpo tem 12,8 ao longo da regua), em coordenada da esquerda (z = 35 - z_dir)
    z0d, z1d = PORTA_R[0] - C_W / 2 - FL, PORTA_R[1] + C_W / 2 + FL
    vao = G.extrude(secao(), G.Z_QUADRO - z1d, G.Z_QUADRO - z0d)
    vao.apply_transform(trimesh.transformations.rotation_matrix(np.arctan(T), [1, 0, 0], point=[0, 0, Z_PIVO]))
    abaixo = RA.caixa(-50, -60, -200, 100, 0, 200)
    abaixo.apply_transform(trimesh.transformations.rotation_matrix(np.arctan(T), [1, 0, 0], point=[0, 0, Z_PIVO]))
    return trimesh.boolean.difference([m, abaixo, vao, G.canal_regua(D.FOLGA_CURSO, D.FOLGA_FIM)], engine='manifold')


if __name__ == '__main__':
    s = secao()
    print('vao: X %.1f..%.1f; topo do corpo no eixo Y %.2f; ponta da frente do corpo em X %.2f (labio interno %.1f)'
          % (s.bounds[0], s.bounds[2], O[1], (O + U * (-A))[0], G.XL))
    re_ = regua_esq(); assert re_.is_watertight
    rp = re_.copy(); rp.apply_transform(trimesh.transformations.rotation_matrix(-np.arctan(T), [1, 0, 0], point=[0, 0, 0]))
    r = RA.para_direita(re_); rp = RA.para_direita(rp)
    rp.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rp.apply_translation(-rp.bounds[0])
    rp = RA.limpa(rp)
    q = D.quadro()
    print('interferencia montada %.2f mm3; pior deslizando %.2f mm3; pecas %d' % (
        trimesh.boolean.intersection([r, q], engine='manifold').volume, RD.montagem(r, q), len(rp.split(only_watertight=False))))
    n = 'Suporte_tablet_dir_v2_regua_cabo_tras_%sgraus' % ('%g' % GRAUS).replace('.', ',')
    rp.export(os.path.join(G.AQUI, 'stl', n + '.stl'))
    trimesh.util.concatenate([q, r]).export(os.path.join(G.AQUI, 'stl', n + '_montada.stl'))
    print(n, rp.extents.round(1), '%.1f cm3' % (rp.volume / 1000), 'estanque', trimesh.load(os.path.join(G.AQUI, 'stl', n + '.stl')).is_watertight)
