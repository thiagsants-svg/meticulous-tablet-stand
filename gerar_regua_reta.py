# -*- coding: utf-8 -*-
"""Lado direito, REGUA RETA com o angulo no encaixe (21/11/2026, pedido: "deixar ele como se fosse 0 graus? mantendo a
barra reta e compensando no angulo da regiao de encaixe").
As reguas com inclina= dobram o piso (sobe a partir do bloco). Aqui a regua inteira (piso, labio, parede, furos) e reta e
fica GIRADA de GRAUS em relacao ao canal: a ponta livre sobe tan(GRAUS) por mm, como uma barra rigida.
  - canal do rabo de andorinha e topo do bloco ficam exatamente onde o quadro espera (horizontais, mesmas folgas);
  - o bloco original e mantido por cima (bloco do quadro em Y 0..7) e a barra girada passa por baixo dele; a face de baixo e
    um plano so (o que sobra abaixo do plano e cortado): imprime deitada nesse plano, sem suporte;
  - pivo em Z_PIVO (coordenada da esquerda; -2 = 3 mm alem do bloco do lado livre... ver abaixo): sob o canal a barra desce
    ate 2,4 mm no lado do batente, sobrando >= 3 mm de piso sob o canal.
Uso: python -I gerar_regua_reta.py [graus=3.5] [furo=36 ponte=4 n_furos=3] [folga_curso=0.10] [folga_fim=0.0]"""
import os, sys
ARGS = dict(base='142', graus='3.5', folga_curso='0.10', folga_fim='0.0', furo='36', ponte='4', n_furos='3', inclina='0')
ARGS.update(dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a))
sys.argv = [sys.argv[0]] + ['%s=%s' % kv for kv in ARGS.items()]
import numpy as np
import trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_suporte_dir as D
import gerar_regua_deitado as RD
G = D.G

GRAUS = float(ARGS['graus'])
T = np.tan(np.radians(GRAUS))
Z_PIVO = -2.0      # esquerda: a barra fica na altura original aqui (logo depois do bloco, lado livre em z < -5)


def gira(m):
    """barra rigida GIRADA de verdade em torno de X no pivo (nao cisalhada): depois de ceder GRAUS com o peso, fica reta e
    no esquadro (pontas verticais); a ponta livre (z = -95 na esquerda) sobe"""
    m = m.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.arctan(T), [1, 0, 0], point=[0, 0, Z_PIVO]))
    return m


def regua_esq():
    furos = [(G.Z_QUADRO - z1, G.Z_QUADRO - z0) for z0, z1 in D.FUROS]
    corpo = G.regua(furos=furos, inclina=0.0, com_canal=False)            # reta, com furos, sem canal
    barra = gira(corpo)
    # 21/11/2026 "pra visualmente nao aparecer a compensacao": do bloco original fica SO a parte de tras (X >= frente da
    # barra no piso, f(PISO)), que e a que o quadro usa (canal e topo a 7). Labio, piso do tablet e frente vem todos da barra
    # girada: o degrau parece uma regua reta, e o tablet apoia na barra (nao num piso mais alto junto ao batente).
    x_tras = G.f(G.PISO)
    bloco = trimesh.boolean.intersection([corpo, trimesh.creation.box(bounds=[[x_tras, -50, G.Z_BLOCO0], [100, 50, G.Z_REG1]])], engine='manifold')
    m = trimesh.boolean.union([barra, bloco], engine='manifold')
    abaixo = gira(trimesh.creation.box(bounds=[[-50, -60, -200], [100, 0, 200]]))   # tudo abaixo do plano da face de baixo
    canal = G.canal_regua(D.FOLGA_CURSO, D.FOLGA_FIM)
    return trimesh.boolean.difference([m, abaixo, canal], engine='manifold')


def para_direita(m):
    m = m.copy(); m.apply_scale([1, 1, -1]); m.apply_translation([0, 0, G.Z_QUADRO]); m.fix_normals()
    return m


if __name__ == '__main__':
    re_ = regua_esq()
    assert re_.is_watertight
    # impressao: deita no plano de baixo (gira atan(T) em X na esquerda) e depois o mesmo caminho das outras reguas
    rp = re_.copy(); rp.apply_transform(trimesh.transformations.rotation_matrix(-np.arctan(T), [1, 0, 0]))
    r = para_direita(re_)                      # montada (coordenadas do lado direito)
    rp = para_direita(rp)
    rp.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); rp.apply_translation(-rp.bounds[0])
    # o STL grava em float32 e juntava vertices quase iguais (faces de area zero): limpa no manifold e confere relendo
    import manifold3d
    for _ in range(3):
        mf = manifold3d.Manifold(manifold3d.Mesh(vert_properties=np.asarray(rp.vertices, np.float32), tri_verts=np.asarray(rp.faces, np.uint32)))
        mf = mf.simplify(0.002) if hasattr(mf, 'simplify') else mf
        mm = mf.to_mesh(); rp = trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))
        rp.apply_translation(-rp.bounds[0])
        t = trimesh.Trimesh(np.asarray(rp.vertices, np.float32).astype(float), rp.faces)
        if t.is_watertight and t.area_faces.min() > 0: break
    print('STL relido estanque:', t.is_watertight)
    # conferencias
    zs = rp.vertices[:, 2]; base = rp.vertices[zs < 0.01]
    print('face de baixo plana: %d vertices em z=0, area de contato ~%.0f mm2' % (len(base), rp.section(plane_origin=[0, 0, 0.1], plane_normal=[0, 0, 1]).to_2D()[0].area))
    q = D.quadro()
    print('interferencia montada: %.2f mm3; pior deslizando: %.2f mm3' % (
        trimesh.boolean.intersection([r, q], engine='manifold').volume, RD.montagem(r, q)))
    ponta = r.vertices[r.vertices[:, 2] > 129]
    print('ponta livre: piso sobe %.1f mm (%.1f graus)' % (ponta[:, 1].min() - 0.0, GRAUS))
    n = 'Suporte_tablet_dir_v2_regua_reta_%sgraus_%dfuros' % (('%g' % GRAUS).replace('.', ','), D.N_FUROS)
    rp.export(os.path.join(G.AQUI, 'stl', n + '.stl'))
    trimesh.util.concatenate([q, r]).export(os.path.join(G.AQUI, 'stl', n + '_montada.stl'))
    print(n, rp.extents.round(1), '%.1f cm3' % (rp.volume / 1000))
