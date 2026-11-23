# -*- coding: utf-8 -*-
"""Slices the _cli 3MFs in slicer/ from the command line and summarises time, filament and line types.
Usage: python -I slice_cli.py <3mf name without extension> [...]"""
import os, sys, subprocess, shutil, re, collections
EXE = r"C:\Program Files\AnycubicSlicerNext\AnycubicSlicerNext.exe"
HERE = os.path.dirname(os.path.abspath(__file__)); SLICER = os.path.join(HERE, 'slicer')
for name in sys.argv[1:]:
    tmp = os.path.join(os.environ['TEMP'], 'tablet_slice'); shutil.rmtree(tmp, True); os.makedirs(tmp)
    subprocess.run([EXE, '--slice', '0', '--outputdir', tmp, os.path.join(SLICER, name + '.3mf')], capture_output=True, timeout=600)
    g = os.path.join(tmp, 'plate_1.gcode')
    if not os.path.exists(g): print(name, 'FAILED'); continue
    shutil.copyfile(g, os.path.join(SLICER, name + '.gcode'))
    types = collections.Counter(); t = None; est = {}
    for l in open(g, encoding='utf-8', errors='ignore'):
        if l.startswith(';TYPE:'): t = l[6:].strip()
        elif t and l.startswith('G1') and ' E' in l: types[t] += 1
        if 'total filament used [g]' in l or 'estimated printing time (normal mode)' in l: est[l.split('=')[0].strip('; ')] = l.split('=')[1].strip()
    print(name, est, dict(types))
