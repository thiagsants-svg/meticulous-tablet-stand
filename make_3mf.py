# -*- coding: utf-8 -*-
"""3MF of the Meticulous tablet stand (left) v1: frame lying flat + step ledge, same bed, WITHOUT supports.
Usage: python -I make_3mf.py [cli] [side=left|right] [ver=v1|v2] [only=...] [slot=3] [plate=textured|smooth] [original=1] [support=1] [x:key=value]
  original=1 builds the downloaded STL (upright, tree supports on the build plate only, standard PETG supports) for comparison.
Profile (D63 base profile from another project of the user): original brass nozzle, 240 C, PA 0.04, z_offset 0.1, bold profile flow 20,
textured plate (18/11/2026). ACE: 1 red, 2 yellow, 3 black, 4 white."""
import json, os, sys, zipfile
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
A = sys.argv[1:]
CLI = 'cli' in A
ORIG = 'original=1' in A
ONLY = next((a.split('=')[1] for a in A if a.startswith('only=')), '')   # only=ledge: only the ledge (reprint)
SIDE = next((a.split('=')[1] for a in A if a.startswith('side=')), 'left')   # left | right
VER = next((a.split('=')[1] for a in A if a.startswith('ver=')), 'v1')   # ver=v2: taller frame for the landscape tablet (20/11/2026)
SLOT = int(next((a.split('=')[1] for a in A if a.startswith('slot=')), 3))
PLATE = next((a.split('=')[1] for a in A if a.startswith('plate=')), 'textured')
BASE = json.load(open(os.path.join(HERE, 'slicer', 'project_settings_base.json'), encoding='utf-8'))
NAME = ('original_meticulous_left' if ORIG else 'tablet_stand_%s_%s' % (SIDE, VER) + ('_landscape' if VER == 'v2' else '') + {'ledge': '_only_ledge', 'ledges': '_ledges_2.5and5deg', 'landscape': '_landscape_only_ledge', 'ledge_3.5': '_only_ledge_3.5deg', 'ledge_3.5_nomark': '_only_ledge_3.5deg_nomark', 'ledge_3.5_nomark_3holes': '_only_ledge_3.5deg_nomark_3holes', 'straight_3.5': '_only_ledge_straight_3.5deg_3holes', 'straight_4.5': '_only_ledge_straight_4.5deg_3holes', 'usbc_tunnel': '_only_ledge_usbc_tunnel_1deg', 'cable_back': '_only_ledge_cable_back_1.5deg'}.get(ONLY, '')) + ''.join('_layer' + a.split('=')[1].replace('.', '') for a in A if a.startswith('x:layer_height=')) + '_KobraS1_PETG' + ('_cli' if CLI else '')
OUTPUT = os.path.join(HERE, 'slicer' if CLI else 'output', NAME + '.3mf')
ACE_COLOURS = ['#D62828', '#F2C200', '#161616', '#FFFFFF']


def mesh_xml(m):
    v = ''.join('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % tuple(p) for p in m.vertices)
    t = ''.join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(f) for f in m.faces)
    return '<mesh><vertices>%s</vertices><triangles>%s</triangles></mesh>' % (v, t)


def parts():
    if ORIG:
        m = trimesh.load(os.path.join(HERE, 'original', 'Meticulous_tablet_stand_left.stl'))
        b = [x for x in m.split(only_watertight=False) if x.is_watertight]
        m = trimesh.boolean.union(b, engine='manifold')
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))   # upright: the original's Y becomes Z
        return [('Original Meticulous left', m)]
    if ONLY == 'cable_back':   # 22/11/2026: straight 1.5 degree ledge, 90 degree USB-C adapter with the cable leaving behind (ledge_cable_back.py)
        return [('Ledge cable back', trimesh.load(os.path.join(HERE, 'stl', 'tablet_stand_right_v2_ledge_cable_back_1.5deg.stl')))]
    if ONLY == 'usbc_tunnel':   # 21/11/2026: straight 1 degree ledge with a tunnel for the 90 degree USB-C adapter (ledge_usbc_tunnel.py)
        return [('Ledge USB-C tunnel 1 deg', trimesh.load(os.path.join(HERE, 'stl', 'tablet_stand_right_v2_ledge_usbc_tunnel_1deg.stl')))]
    if ONLY == 'straight_4.5':   # 21/11/2026: same with 4.5 degrees
        return [('Straight ledge 4.5 deg', trimesh.load(os.path.join(HERE, 'stl', 'tablet_stand_right_v2_ledge_straight_4.5deg_3holes.stl')))]
    if ONLY == 'straight_3.5':   # 21/11/2026: straight ledge rotated 3.5 degrees at the joint (ledge_straight.py)
        return [('Straight ledge 3.5 deg', trimesh.load(os.path.join(HERE, 'stl', 'tablet_stand_right_v2_ledge_straight_3.5deg_3holes.stl')))]
    if ONLY == 'ledge_3.5_nomark_3holes':   # 21/11/2026: same with 3 long holes up to 8 mm from the free end (request: open further to the right, fewer bridges)
        return [('Ledge 3.5 deg', trimesh.load(os.path.join(HERE, 'stl', 'tablet_stand_right_v2_ledge_3.5deg_nomark_3holes.stl')))]
    if ONLY == 'ledge_3.5_nomark':   # 21/11/2026: v2 (channel 0.10/0.00), 3.5 degrees, no marking
        return [('Ledge 3.5 deg', trimesh.load(os.path.join(HERE, 'stl', 'tablet_stand_right_v2_ledge_3.5deg_nomark.stl')))]
    if ONLY == 'ledge_3.5':   # 20/11/2026: 2.5 degrees left 1 degree of sag -> 3.5
        return [('Ledge 3.5 deg', trimesh.load(os.path.join(HERE, 'stl', 'tablet_stand_right_v1_ledge_3.5deg_marked.stl')))]
    if ONLY == 'landscape':   # 20/11/2026: long ledge for the landscape tablet (right frame already printed)
        return [('Landscape ledge', trimesh.load(os.path.join(HERE, 'stl', 'tablet_stand_right_landscape_ledge.stl')))]
    if ONLY == 'ledges':   # 20/11/2026: the two right-side test ledges (2.5 and 5 degrees), marked, on the same bed
        return [('Ledge %s deg' % g, trimesh.load(os.path.join(HERE, 'stl', 'tablet_stand_right_v1_ledge_%sdeg_marked.stl' % g))) for g in ('2.5', '5')]
    q = trimesh.load(os.path.join(HERE, 'stl', 'tablet_stand_%s_%s_frame.stl' % (SIDE, VER)))
    r = trimesh.load(os.path.join(HERE, 'stl', 'tablet_stand_%s_%s_ledge.stl' % (SIDE, VER)))
    return [('Step ledge', r)] if ONLY == 'ledge' else [('Frame', q), ('Step ledge', r)]


def build():
    ps = parts()
    for _, m in ps:
        m.apply_translation(-m.bounds[0]); assert m.is_watertight
    width = sum(m.extents[0] for _, m in ps) + 12 * (len(ps) - 1)
    x = (250 - width) / 2
    objs, items, cfg = [], [], ['<?xml version="1.0" encoding="UTF-8"?>', '<config>']
    for i, (name, m) in enumerate(ps):
        mid, oid = 2 * i + 1, 2 * i + 2
        y = (250 - m.extents[1]) / 2
        objs.append('  <object id="%d" type="model" name="%s [part]">%s</object>' % (mid, name, mesh_xml(m)))
        objs.append('  <object id="%d" type="model" name="%s"><components><component objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object>' % (oid, name, mid))
        items.append('  <item objectid="%d" transform="1 0 0 0 1 0 0 0 1 %.4f %.4f 0" printable="1"/>' % (oid, x, y))
        cfg += ['  <object id="%d">' % oid, '    <metadata key="name" value="%s"/>' % name, '    <metadata key="extruder" value="%d"/>' % SLOT,
                '    <part id="%d" subtype="normal_part">' % mid, '      <metadata key="name" value="%s"/>' % name,
                '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>', '      <metadata key="extruder" value="%d"/>' % SLOT, '    </part>', '  </object>']
        print('%s: %.1f x %.1f x %.1f at x %.0f..%.0f' % (name, *m.extents, x, x + m.extents[0]))
        x += m.extents[0] + 12
    assert x - 12 <= 242
    cfg += ['  <plate>', '    <metadata key="plater_id" value="1"/>', '    <metadata key="plater_name" value="%s"/>' % ('' if CLI else 'Tablet stand'), '    <metadata key="locked" value="false"/>']
    for i in range(len(ps)):
        cfg += ['    <model_instance>', '      <metadata key="object_id" value="%d"/>' % (2 * i + 2), '      <metadata key="instance_id" value="0"/>',
                '      <metadata key="identify_id" value="%d"/>' % (1002 + i), '    </model_instance>']
    cfg += ['  </plate>', '</config>']
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">',
           ' <metadata name="Application">BambuStudio-2.0.0.3</metadata>', ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
           ' <metadata name="Title">%s - Kobra S1 PETG</metadata>' % NAME, ' <resources>'] + objs + [' </resources>', ' <build>'] + items + [' </build>', '</model>']

    pj = dict(BASE); n = len(pj['filament_settings_id'])
    pj['filament_colour'] = list(ACE_COLOURS)
    pj['filament_max_volumetric_speed'] = ['20'] * n
    pj['curr_bed_type'] = 'High Temp Plate' if PLATE == 'smooth' else 'Textured PEI Plate'
    for k in ('nozzle_temperature', 'nozzle_temperature_initial_layer'):
        for suf in ('', '_BRASS', '_HS'):
            pj[k + suf] = ['240'] * n
    changes = {'outer_wall_speed': '200', 'inner_wall_acceleration': '10000', 'internal_solid_infill_acceleration': '10000',
               'travel_acceleration': '15000', 'skirt_loops': '2', 'skirt_distance': '5', 'skirt_height': '1',
               'brim_type': 'no_brim', 'detect_thin_wall': '1', 'enable_support': '0'}
    if ORIG or 'support=1' in A:   # standard PETG supports since 18/11/2026 (validated 21/11); support=1 turns them on for our own parts
        changes.update({'enable_support': '1', 'support_on_build_plate_only': '1', 'support_threshold_angle': '50',
                        'support_top_z_distance': '0.3', 'support_interface_top_layers': '3', 'support_interface_spacing': '0.3',
                        'support_object_xy_distance': '0.6', 'support_object_first_layer_gap': '2', 'support_base_pattern_spacing': '3',
                        'support_bottom_z_distance': '0.3', 'support_interface_bottom_layers': '0', 'support_type': 'tree(auto)', 'support_style': 'default'})
    changes.update(dict(a[2:].split('=', 1) for a in A if a.startswith('x:')))
    pj.update(changes)
    d = list(pj['different_settings_to_system'])
    d[0] = ';'.join(dict.fromkeys([k for k in d[0].split(';') if k] + list(changes)))
    for i in range(1, len(d) - 1):
        d[i] = ';'.join(dict.fromkeys([k for k in d[i].split(';') if k] + ['filament_max_volumetric_speed', 'pressure_advance'] + [k + s for k in ('nozzle_temperature', 'nozzle_temperature_initial_layer') for s in ('', '_BRASS', '_HS')]))
    assert pj['z_offset'] == '0.1'
    pj['pressure_advance'] = ['0.04'] * n; pj['nozzle_type'] = 'brass'
    d[-1] = 'z_offset;nozzle_type'
    pj['different_settings_to_system'] = d
    with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zo:
        zo.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                    '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                    '<Default Extension="config" ContentType="text/xml"/></Types>')
        zo.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        zo.writestr('3D/3dmodel.model', '\n'.join(xml))
        zo.writestr('Metadata/model_settings.config', '\n'.join(cfg))
        zo.writestr('Metadata/project_settings.config', json.dumps(pj, ensure_ascii=False, indent=1))
    print('written:', OUTPUT)


build()
