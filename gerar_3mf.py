# -*- coding: utf-8 -*-
"""3MF do suporte de tablet Meticulous (esquerda) v1: quadro deitado + regua do degrau, mesma mesa, SEM suporte.
Uso: python -I gerar_3mf.py [cli] [lado=esq|dir] [slot=3] [placa=texturizada|lisa] [original=1]
  original=1 gera o STL baixado (em pe, suporte em arvore so na placa, padrao de suporte PETG) para comparar.
Perfil (base D63 do projeto pa_graos_falcon): bico original brass, 240 C, PA 0,04, z_offset 0,1, ousado fluxo 20,
placa texturizada (18/11/2026). ACE: 1 vermelho, 2 amarelo, 3 preto, 4 branco."""
import json, os, sys, zipfile
import numpy as np
import trimesh

AQUI = os.path.dirname(os.path.abspath(__file__))
A = sys.argv[1:]
CLI = 'cli' in A
ORIG = 'original=1' in A
SO = next((a.split('=')[1] for a in A if a.startswith('so=')), '')   # so=regua: so a regua (reimpressao)
LADO = next((a.split('=')[1] for a in A if a.startswith('lado=')), 'esq')   # esq | dir
VER = next((a.split('=')[1] for a in A if a.startswith('ver=')), 'v1')   # ver=v2: quadro mais alto do tablet deitado (20/11/2026)
SLOT = int(next((a.split('=')[1] for a in A if a.startswith('slot=')), 3))
PLACA = next((a.split('=')[1] for a in A if a.startswith('placa=')), 'texturizada')
BASE = json.load(open(os.path.join(AQUI, 'fatiador', 'project_settings_base_D63_2026-10-12.json'), encoding='utf-8'))
NOME = ('Original_Meticulous_esq' if ORIG else 'Suporte_tablet_%s_%s' % (LADO, VER) + ('_deitado' if VER == 'v2' else '') + {'regua': '_so_regua', 'reguas': '_reguas_2,5e5graus', 'deitado': '_deitado_so_regua', '3,5': '_so_regua_3,5graus', '3,5sem': '_so_regua_3,5graus_sem_marca', '3,5sem3': '_so_regua_3,5graus_sem_marca_3furos', 'reta': '_so_regua_reta_3,5graus_3furos', 'reta45': '_so_regua_reta_4,5graus_3furos', 'adaptador': '_so_regua_adaptador_1grau', 'cabo_tras': '_so_regua_cabo_tras_1,5grau'}.get(SO, '')) + ''.join('_camada' + a.split('=')[1].replace('.', '') for a in A if a.startswith('x:layer_height=')) + '_KobraS1_PETG' + ('_cli' if CLI else '')
SAIDA = os.path.join(AQUI, 'fatiador' if CLI else 'saida', NOME + '.3mf')
CORES_ACE = ['#D62828', '#F2C200', '#161616', '#FFFFFF']


def malha_xml(m):
    v = ''.join('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % tuple(p) for p in m.vertices)
    t = ''.join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(f) for f in m.faces)
    return '<mesh><vertices>%s</vertices><triangles>%s</triangles></mesh>' % (v, t)


def pecas():
    if ORIG:
        m = trimesh.load(os.path.join(AQUI, 'origem', 'Meticulous_tablet_stand_left.stl'))
        b = [x for x in m.split(only_watertight=False) if x.is_watertight]
        m = trimesh.boolean.union(b, engine='manifold')
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))   # em pe: Y do original vira Z
        return [('Original Meticulous esq', m)]
    if SO == 'cabo_tras':   # 22/11/2026: regua reta 1,5 grau, adaptador USB-C 90 com cabo saindo por tras (gerar_regua_cabo_tras.py)
        return [('Regua cabo por tras', trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_dir_v2_regua_cabo_tras_1,5graus.stl')))]
    if SO == 'adaptador':   # 21/11/2026: regua reta 1 grau com tunel do adaptador USB-C 90 graus (gerar_regua_adaptador.py)
        return [('Regua adaptador 1 grau', trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_dir_v2_regua_adaptador_1graus.stl')))]
    if SO == 'reta45':   # 21/11/2026: idem com 4,5 graus
        return [('Regua reta 4,5 graus', trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_dir_v2_regua_reta_4,5graus_3furos.stl')))]
    if SO == 'reta':   # 21/11/2026: regua reta girada 3,5 graus no encaixe (gerar_regua_reta.py)
        return [('Regua reta 3,5 graus', trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_dir_v2_regua_reta_3,5graus_3furos.stl')))]
    if SO == '3,5sem3':   # 21/11/2026: idem com 3 furos longos ate 8 mm da ponta livre (pedido: abrir mais para a direita, menos pontes)
        return [('Regua 3,5 graus', trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_dir_v2_regua_3,5graus_sem_marca_3furos.stl')))]
    if SO == '3,5sem':   # 21/11/2026: v2 (canal 0,10/0,00), 3,5 graus, sem marcacao
        return [('Regua 3,5 graus', trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_dir_v2_regua_3,5graus_sem_marca.stl')))]
    if SO == '3,5':   # 20/11/2026: 2,5 graus ficou com 1 grau de caimento -> 3,5
        return [('Regua 3,5 graus', trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_dir_v1_regua_3,5graus_marcada.stl')))]
    if SO == 'deitado':   # 20/11/2026: regua longa para o tablet deitado (quadro direito ja impresso)
        return [('Regua deitado', trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_dir_deitado_regua.stl')))]
    if SO == 'reguas':   # 20/11/2026: as duas reguas de teste do lado direito (2,5 e 5 graus), marcadas, na mesma mesa
        return [('Regua %s graus' % g, trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_dir_v1_regua_%sgraus_marcada.stl' % g))) for g in ('2,5', '5')]
    q = trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_%s_%s_quadro.stl' % (LADO, VER)))
    r = trimesh.load(os.path.join(AQUI, 'stl', 'Suporte_tablet_%s_%s_regua.stl' % (LADO, VER)))
    return [('Regua do degrau', r)] if SO == 'regua' else [('Quadro', q), ('Regua do degrau', r)]


def gerar():
    ps = pecas()
    for _, m in ps:
        m.apply_translation(-m.bounds[0]); assert m.is_watertight
    larg = sum(m.extents[0] for _, m in ps) + 12 * (len(ps) - 1)
    x = (250 - larg) / 2
    objs, items, cfg = [], [], ['<?xml version="1.0" encoding="UTF-8"?>', '<config>']
    for i, (nome, m) in enumerate(ps):
        mid, oid = 2 * i + 1, 2 * i + 2
        y = (250 - m.extents[1]) / 2
        objs.append('  <object id="%d" type="model" name="%s [peca]">%s</object>' % (mid, nome, malha_xml(m)))
        objs.append('  <object id="%d" type="model" name="%s"><components><component objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object>' % (oid, nome, mid))
        items.append('  <item objectid="%d" transform="1 0 0 0 1 0 0 0 1 %.4f %.4f 0" printable="1"/>' % (oid, x, y))
        cfg += ['  <object id="%d">' % oid, '    <metadata key="name" value="%s"/>' % nome, '    <metadata key="extruder" value="%d"/>' % SLOT,
                '    <part id="%d" subtype="normal_part">' % mid, '      <metadata key="name" value="%s"/>' % nome,
                '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>', '      <metadata key="extruder" value="%d"/>' % SLOT, '    </part>', '  </object>']
        print('%s: %.1f x %.1f x %.1f em x %.0f..%.0f' % (nome, *m.extents, x, x + m.extents[0]))
        x += m.extents[0] + 12
    assert x - 12 <= 242
    cfg += ['  <plate>', '    <metadata key="plater_id" value="1"/>', '    <metadata key="plater_name" value="%s"/>' % ('' if CLI else 'Suporte tablet'), '    <metadata key="locked" value="false"/>']
    for i in range(len(ps)):
        cfg += ['    <model_instance>', '      <metadata key="object_id" value="%d"/>' % (2 * i + 2), '      <metadata key="instance_id" value="0"/>',
                '      <metadata key="identify_id" value="%d"/>' % (1002 + i), '    </model_instance>']
    cfg += ['  </plate>', '</config>']
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<model unit="millimeter" xml:lang="pt-BR" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">',
           ' <metadata name="Application">BambuStudio-2.0.0.3</metadata>', ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
           ' <metadata name="Title">%s - Kobra S1 PETG</metadata>' % NOME, ' <resources>'] + objs + [' </resources>', ' <build>'] + items + [' </build>', '</model>']

    pj = dict(BASE); n = len(pj['filament_settings_id'])
    pj['filament_colour'] = list(CORES_ACE)
    pj['filament_max_volumetric_speed'] = ['20'] * n
    pj['curr_bed_type'] = 'High Temp Plate' if PLACA == 'lisa' else 'Textured PEI Plate'
    for k in ('nozzle_temperature', 'nozzle_temperature_initial_layer'):
        for suf in ('', '_BRASS', '_HS'):
            pj[k + suf] = ['240'] * n
    mud = {'outer_wall_speed': '200', 'inner_wall_acceleration': '10000', 'internal_solid_infill_acceleration': '10000',
           'travel_acceleration': '15000', 'skirt_loops': '2', 'skirt_distance': '5', 'skirt_height': '1',
           'brim_type': 'no_brim', 'detect_thin_wall': '1', 'enable_support': '0'}
    if ORIG or 'sup=1' in A:   # padrao de suporte PETG desde 18/11/2026 (validado 21/11); sup=1 liga nas pecas proprias
        mud.update({'enable_support': '1', 'support_on_build_plate_only': '1', 'support_threshold_angle': '50',
                    'support_top_z_distance': '0.3', 'support_interface_top_layers': '3', 'support_interface_spacing': '0.3',
                    'support_object_xy_distance': '0.6', 'support_object_first_layer_gap': '2', 'support_base_pattern_spacing': '3',
                    'support_bottom_z_distance': '0.3', 'support_interface_bottom_layers': '0', 'support_type': 'tree(auto)', 'support_style': 'default'})
    mud.update(dict(a[2:].split('=', 1) for a in A if a.startswith('x:')))
    pj.update(mud)
    d = list(pj['different_settings_to_system'])
    d[0] = ';'.join(dict.fromkeys([k for k in d[0].split(';') if k] + list(mud)))
    for i in range(1, len(d) - 1):
        d[i] = ';'.join(dict.fromkeys([k for k in d[i].split(';') if k] + ['filament_max_volumetric_speed', 'pressure_advance'] + [k + s for k in ('nozzle_temperature', 'nozzle_temperature_initial_layer') for s in ('', '_BRASS', '_HS')]))
    assert pj['z_offset'] == '0.1'
    pj['pressure_advance'] = ['0.04'] * n; pj['nozzle_type'] = 'brass'
    d[-1] = 'z_offset;nozzle_type'
    pj['different_settings_to_system'] = d
    with zipfile.ZipFile(SAIDA, 'w', zipfile.ZIP_DEFLATED) as zo:
        zo.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                    '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                    '<Default Extension="config" ContentType="text/xml"/></Types>')
        zo.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        zo.writestr('3D/3dmodel.model', '\n'.join(xml))
        zo.writestr('Metadata/model_settings.config', '\n'.join(cfg))
        zo.writestr('Metadata/project_settings.config', json.dumps(pj, ensure_ascii=False, indent=1))
    print('gravado:', SAIDA)


gerar()
