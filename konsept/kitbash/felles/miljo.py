# -*- coding: utf-8 -*-
"""miljo.py  ·  omsyn til maskina: blir importert først av alle verktøya her

Maskina har åtte kjernar og blir delt med anna arbeid, og lyden hakkar under last. Difor: høgst fire trådar
(numba og BLAS), lågaste prioritet (same grep som _skaansam i modell/byggjesett/rendre_blender.py), og ingen
.pyc eller numba-lager i mappene vi berre les frå.
"""
import os, sys, tempfile

sys.dont_write_bytecode = True
for _k in ('NUMBA_NUM_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_k, '4')
os.environ.setdefault('NUMBA_CACHE_DIR', os.path.join(tempfile.gettempdir(), 'kitbash_numba'))


def skaansam():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x40)              # IDLE_PRIORITY_CLASS
        k.SetProcessAffinityMask(h, 0xFC)        # kjerne 2 til 7
    except Exception:
        pass


skaansam()
