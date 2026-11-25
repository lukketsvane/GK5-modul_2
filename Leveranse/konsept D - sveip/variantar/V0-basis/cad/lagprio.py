# -*- coding: utf-8 -*-
"""Set prosessen til lågaste prioritet og hald kjerne 0 og 1 frie.

Tunge reknejobbar får lyden på maskina til å hakke når dei tek alle kjernane.
Alle skripta i denne mappa kallar `lag_prioritet()` først.
"""
from __future__ import annotations


def lag_prioritet() -> None:
    try:
        import psutil

        p = psutil.Process()
        if hasattr(psutil, "IDLE_PRIORITY_CLASS"):
            p.nice(psutil.IDLE_PRIORITY_CLASS)
        else:  # ikkje Windows
            p.nice(19)
        n = psutil.cpu_count() or 0
        if n > 2 and hasattr(p, "cpu_affinity"):
            p.cpu_affinity(list(range(2, n)))
    except Exception:
        pass
