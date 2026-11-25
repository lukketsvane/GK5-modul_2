# -*- coding: utf-8 -*-
"""V1 Plate: nagla aluminiumspanel der saumane følgjer geometrien til lampa.

Panelplanen står i panel.py. Kvar boge er éi valsa plate, skøytane er forskyvde og endar i T,
og naglane står per plate med felles hjørnenagle.
"""
from panel import panel


def felt(G):
    p = panel(G)
    return dict(h=p["h"], tone=p["tone"], rough=p["rough"], mat=dict(sky=0.2, strok=0.5))
