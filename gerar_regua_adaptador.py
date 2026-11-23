# -*- coding: utf-8 -*-
"""Lado direito, REGUA RETA COM ALOJAMENTO DO ADAPTADOR USB-C 90 graus (21/11/2026).
Resultados que levaram a esta versao (usuario, 21/11): a regua reta de 3,5 graus (canal 0,10/0,00, camada 0,08) "ficou
exagerada, ficou em -2" e "o canal ficou bem firme"; de volta na de 2,5 com o tablet em pe, "nao consigo centralizar bem com o
cabo" (furos separados por pontes); pediu "prever espaco para esse adaptador [USB-C macho-femea 90 graus, foto de anuncio],
quero que ele fique escondido e tenha um jogo maior de ajuste no centro".
  - TUNEL continuo por baixo do piso, aberto na ponta livre (saida do cabo, longe do grupo aquecido) e fechado junto ao
    batente: o corpo do adaptador deita no tunel ao longo da regua, o plugue sobe por um RASGO continuo no piso ate a porta
    do tablet, e o cabo (plugue dele encaixado na femea do adaptador) corre pelo tunel ate sair na ponta. O tablet pode ficar
    em qualquer posicao ao longo do rasgo (sem pontes).
  - Medidas do adaptador ESTIMADAS (nao chegou; anuncio sem cotas): corpo ~24 x 12,5 x 7, plugue macho com colar ~4,5 de
    espessura. Tunel 13 x 13 (cabe o corpo deitado nas duas posicoes e girado 10 graus como a porta do tablet), teto de 1,5
    sob o piso (o colar do plugue ocupa essa altura dentro do rasgo), rasgo de 5,5.
  - A regua fica com uma quilha por baixo (fundo 12,5 abaixo do piso antigo): bem mais rigida, entao a compensacao cai.
    3,5 deu -2 com o canal justo => o conjunto cede ~1,5; com a quilha cede menos: 1 grau.
Uso: python -I gerar_regua_adaptador.py [graus=1.0] [tunel_l=13] [tunel_h=13] [teto=1.5] [rasgo=5.5]"""
import os, sys
ARGS = dict(base='142', graus='1.0', folga_curso='0.10', folga_fim='0.0', inclina='0', tunel_l='13', tunel_h='13', teto='1.5', rasgo='5.5')
ARGS.update(dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a))
sys.argv = [sys.argv[0]] + ['%s=%s' % kv for kv in ARGS.items()]
import numpy as np
import trimesh
from shapely.geometry import box
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_suporte_dir as D
import gerar_regua_deitado as RD
G = D.G

GRAUS = float(ARGS['graus']); T = np.tan(np.radians(GRAUS))
Z_PIVO = -2.0
TL, TH, TETO, RASGO = (float(ARGS[k]) for k in ('tunel_l', 'tunel_h', 'teto', 'rasgo'))
PAREDE = 2.0
XC = (G.XL + G.f(G.PISO)) / 2                         # meio do vao do tablet no piso: a porta USB fica aqui
T_TOPO = G.PISO - TETO                                # topo do tunel
T_FUNDO = T_TOPO - TH
X_T0 = max(G.X0 + PAREDE, XC - TL / 2); X_T1 = X_T0 + TL   # nao afina a parede do labio
FUNDO = T_FUNDO - PAREDE                              # face de baixo da regua (era 0)
Z_FECHO = G.Z_QUADRO - 0.0                            # esquerda: tunel fechado junto ao batente (direita Z 0); aberto na ponta livre


def gira(m):
    m = m.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.arctan(T), [1, 0, 0], point=[0, 0, Z_PIVO]))
    return m


def caixa(x0, y0, z0, x1, y1, z1):
    return trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])


def regua_esq():
    corpo = G.regua(inclina=0.0, com_canal=False, passa_cabo=False)
    quilha = caixa(G.X0, FUNDO, G.Z_REG0, X_T1 + PAREDE, 0.5, G.Z_REG1)
    # parede de tras do tunel sobe ate a parede traseira do degrau (senao piso + parede ficam soltos, presos so pelo labio);
    # so fora do bloco: em cima do bloco passa a travessa do quadro (Y 7,2)
    quilha = trimesh.boolean.union([quilha, caixa(X_T1 - 0.01, FUNDO, G.Z_REG0, X_T1 + PAREDE, G.COSTAS_H, G.Z_BLOCO0 + 1)], engine='manifold')
    corpo = trimesh.boolean.union([corpo, quilha], engine='manifold')
    # secao do vazio: tunel com mao-francesa de 45 graus (1,5) nos cantos de cima, para o teto (dois balancos ate o rasgo)
    # imprimir sem suporte; o corpo do adaptador (7 de largura, centrado no plugue) passa entre elas
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    mf = 1.5
    sec = box(X_T0, T_FUNDO, X_T1, T_TOPO).difference(Polygon([(X_T0, T_TOPO), (X_T0 + mf, T_TOPO), (X_T0, T_TOPO - mf)]))         .difference(Polygon([(X_T1, T_TOPO), (X_T1 - mf, T_TOPO), (X_T1, T_TOPO - mf)]))
    sec = unary_union([sec, box(XC - RASGO / 2, T_TOPO - 0.5, XC + RASGO / 2, G.PISO + 1)])
    vazio = G.extrude(sec, G.Z_REG0 - 1, Z_FECHO)
    barra = gira(corpo)
    bloco = trimesh.boolean.intersection([G.regua(inclina=0.0, com_canal=False, passa_cabo=False),
                                          caixa(G.f(G.PISO), -50, G.Z_BLOCO0, 100, 50, G.Z_REG1)], engine='manifold')
    m = trimesh.boolean.union([barra, bloco], engine='manifold')
    abaixo = gira(caixa(-50, FUNDO - 60, -200, 100, FUNDO, 200))
    return trimesh.boolean.difference([m, abaixo, gira(vazio), G.canal_regua(D.FOLGA_CURSO, D.FOLGA_FIM)], engine='manifold')


def para_direita(m):
    m = m.copy(); m.apply_scale([1, 1, -1]); m.apply_translation([0, 0, G.Z_QUADRO]); m.fix_normals()
    return m


def limpa(rp):
    import manifold3d
    for _ in range(3):
        mf = manifold3d.Manifold(manifold3d.Mesh(vert_properties=np.asarray(rp.vertices, np.float32), tri_verts=np.asarray(rp.faces, np.uint32)))
        mf = mf.simplify(0.002)
        mm = mf.to_mesh(); rp = trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))
        rp.apply_translation(-rp.bounds[0])
        t = trimesh.Trimesh(np.asarray(rp.vertices, np.float32).astype(float), rp.faces)
        if t.is_watertight and t.area_faces.min() > 0: break
    return rp


if __name__ == '__main__':
    print('tunel X %.1f..%.1f (porta em %.1f), Y %.1f..%.1f, teto %.1f, rasgo %.1f; fundo da regua em Y %.1f' % (X_T0, X_T1, XC, T_FUNDO, T_TOPO, TETO, RASGO, FUNDO))
    re_ = regua_esq(); assert re_.is_watertight
    rp = re_.copy(); rp.apply_transform(trimesh.transformations.rotation_matrix(-np.arctan(T), [1, 0, 0], point=[0, FUNDO, 0]))
    r = para_direita(re_); rp = para_direita(rp)
    rp.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rp.apply_translation(-rp.bounds[0])
    rp = limpa(rp)
    print('face de baixo: contato %.0f mm2' % rp.section(plane_origin=[0, 0, 0.1], plane_normal=[0, 0, 1]).to_2D()[0].area)
    q = D.quadro()
    print('interferencia montada %.2f mm3; pior deslizando %.2f mm3' % (trimesh.boolean.intersection([r, q], engine='manifold').volume, RD.montagem(r, q)))
    # corte transversal no meio do curso, para conferir tunel, teto, rasgo e paredes
    s = r.section(plane_origin=[0, 0, 70], plane_normal=[0, 0, 1])
    print('corte em Z 70 (direita):', [tuple(np.round(p.bounds, 1)) for p in s.to_2D()[0].polygons_full])
    n = 'Suporte_tablet_dir_v2_regua_adaptador_%sgraus' % ('%g' % GRAUS).replace('.', ',')
    rp.export(os.path.join(G.AQUI, 'stl', n + '.stl'))
    trimesh.util.concatenate([q, r]).export(os.path.join(G.AQUI, 'stl', n + '_montada.stl'))
    print(n, rp.extents.round(1), '%.1f cm3' % (rp.volume / 1000), 'estanque', trimesh.load(os.path.join(G.AQUI, 'stl', n + '.stl')).is_watertight)
