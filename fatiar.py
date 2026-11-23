# -*- coding: utf-8 -*-
"""Fatia os 3MF _cli de fatiador/ pela linha de comando e resume tempo, filamento e tipos de linha."""
import os, sys, subprocess, shutil, re, collections
EXE = r"C:\Program Files\AnycubicSlicerNext\AnycubicSlicerNext.exe"
AQUI = os.path.dirname(os.path.abspath(__file__)); FAT = os.path.join(AQUI, 'fatiador')
for nome in sys.argv[1:]:
    tmp = os.path.join(os.environ['TEMP'], 'tablet_slice'); shutil.rmtree(tmp, True); os.makedirs(tmp)
    subprocess.run([EXE, '--slice', '0', '--outputdir', tmp, os.path.join(FAT, nome + '.3mf')], capture_output=True, timeout=600)
    g = os.path.join(tmp, 'plate_1.gcode')
    if not os.path.exists(g): print(nome, 'FALHOU'); continue
    shutil.copyfile(g, os.path.join(FAT, nome + '.gcode'))
    tipos = collections.Counter(); t = None; est = {}
    for l in open(g, encoding='utf-8', errors='ignore'):
        if l.startswith(';TYPE:'): t = l[6:].strip()
        elif t and l.startswith('G1') and ' E' in l: tipos[t] += 1
        if 'total filament used [g]' in l or 'estimated printing time (normal mode)' in l: est[l.split('=')[0].strip('; ')] = l.split('=')[1].strip()
    print(nome, est, dict(tipos))
