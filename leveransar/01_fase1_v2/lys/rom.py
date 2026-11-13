# -*- coding: utf-8 -*-
"""Lysbilete til fase 1-sidene: rommet med lyset briefen ber om, før lampa finst.

Brukar motoren i konsept/lysskisse/lysskisse.py. Modell, ikkje måling.
Kjeldene står utanfor biletet eller bak skjermen, så berre lyset syner.

  python rom.py overgang [px] [ss]     tre bilete: stemning, på veg, arbeid
  python rom.py krav [px] [ss]         arbeidsrommet med punkt til merkelappar
"""
import sys, os, json, time
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HER, '..', '..', '..', 'konsept', 'lysskisse')))
from lysskisse import *          # noqa: F401,F403
from PIL import Image

# Ryggfiguren er pølge-mannekengen (modell/polge_1.glb). Han blir sett inn før rommet blir bygd.
sys.path.insert(0, os.path.normpath(os.path.join(HER, '..', '..', '..', 'modell')))
try:
    import polge
    FIGUR = polge.byt(sys.modules['lysskisse'])
except Exception as e:                      # utan modellen: den gamle figuren av kuler og sylindrar
    FIGUR = None
    print('mannekengen vart ikkje sett inn:', e)

UT = os.path.normpath(os.path.join(HER, '..', 'bilete'))
os.makedirs(UT, exist_ok=True)

FELT_LM = 87.7      # gjev 350 lx i snitt på feltet (0,24 m², mjuke kantar)
VEGG_LM = 180.0     # blir kalibrert mot veggsona i tal()
HALO_LM = 100.0     # stemning


def proj(P):
    """Punkt i rommet -> (x, y) i biletet, 0 til 1 frå øvre venstre hjørne."""
    d = np.asarray(P, float) - KAM.C
    z = float(d @ KAM.f)
    return [round((float(d @ KAM.r) / z / KAM.h + 1) / 2, 4), round((1 - float(d @ KAM.u) / z / KAM.h) / 2, 4)]


def rom_t(t, vegg_lm=VEGG_LM):
    """t = 0 er stemning, t = 1 er arbeid. Gjev (strøk, kropp). Ingen kropp: lampa finst ikkje enno."""
    K = 2200 + 800 * t
    lys = []
    if t < 1:
        # varm glød på veggen bak skjermen, kjelda skjult bak skjermen
        lys.append(straale(b(0, 0.60, 0.07), b(0, YV, 0.45), HALO_LM * (1 - t), K, flat=(55, 24), kutt=80, opning=(0.30, 0.03)))
    if t > 0:
        # arbeidsfeltet, kjelda over biletkanten
        lys.append(straale(b(0.0, 0.25, 1.5), FELT, FELT_LM * t, K, maske=maske_bord(-0.3, 0.3, 0.05, 0.45, k=0.02), opning=0.03, sprut=0.0))
        # veggen rundt skjermen, kjelda over biletkanten
        lys.append(straale(b(0.0, -0.2, 1.3), b(0.0, YV, 0.45), vegg_lm * t, K, maske=maske_vegg(0.0, ZB + 0.45, 0.75, k=0.18), opning=0.03, sprut=0.0))
    return lys, []


def marknad():
    """Tre lamper som finst, éi frå kvar kategori, med produsenten sitt lumental og forenkla form.
    Gjev {namn: (strøk, kropp)}."""
    ut = {}
    # Northern Snowball oppladbar: opalkule Ø 7 cm, 33 cm høg, fot Ø 9 cm, 158 lm, 2700 K (northern.no)
    c = b(0.47, 0.40, 0.295)
    ut['snowball'] = ([glod(c, 0.035, 158.0, 2700)],
                      [syl(b(0.47, 0.40, 0), b(0.47, 0.40, 0.012), 0.045), syl(b(0.47, 0.40, 0.012), b(0.47, 0.40, 0.262), 0.006)])
    # Luxo L-1 med E27-pære: 529 lm, 2700 K, skjerm Ø 155 mm (Glamox produktark). Lysfordelinga er forenkla.
    pos = b(0.28, 0.38, 0.45); n = nrm(FELT - pos)
    ut['l1'] = ([straale(pos, FELT, 529.0, 2700, spreiing=27, kutt=50, opning=0.0775)],
                [syl(b(0.56, 0.60, 0), b(0.56, 0.60, 0.02), 0.07), syl(b(0.56, 0.60, 0.02), b(0.50, 0.56, 0.36), 0.006),
                 syl(b(0.50, 0.56, 0.36), pos - 0.09 * n, 0.006), hovud(pos, n, 0.08, 0.09)])
    # Logitech Litra Glow: 250 lm, lysflate om lag 9 x 9 cm, på skjermkanten mot ansiktet. 3000 K vald.
    # Kroppen er ein tynn list bak flata. (Første utgåve hadde ein kropp som slukte flata, og gav null lys.)
    ut['litra'] = ([flate(b(0.0, 0.44, 0.475), (0, -1, 0.08), (0.09, 0.09), 250.0, 3000)],
                   [syl(b(-0.045, 0.462, 0.475), b(0.045, 0.462, 0.475), 0.012)])
    return ut


def tal_lampe(lys, kropp):
    d = tal(lys, kropp)
    return dict(lm=round(float(d['lm']), 1), felt_lx=round(float(d['E_felt']), 1), jamnheit=round(float(d['U']), 2),
                vegg_lx=round(float(d['E_vegg']), 1), ansikt_lx=round(float(d['E_ansikt']), 1),
                lampe_cd=round(float(d['L_lampe']), 0), lysaste_flate_cd=round(float(d['L_flate']), 1),
                spegla_cd=round(float(d['L_spegl']), 0))


def bilete_k(lys, kropp, fil, px, ss):
    t0 = time.time()
    img = framkall(luminans(lys, kropp, px, ss), px)
    Image.fromarray(img).save(os.path.join(UT, fil))
    print(fil, round(time.time() - t0, 1), 's')


def tal_rom(lys):
    d = tal(lys, [])
    return dict(lm=round(float(d['lm']), 1), felt_lx=round(float(d['E_felt']), 1), jamnheit=round(float(d['U']), 2),
                vegg_lx=round(float(d['E_vegg']), 1), ansikt_lx=round(float(d['E_ansikt']), 1),
                lysaste_flate_cd=round(float(d['L_flate']), 1))


def bilete(lys, fil, px, ss):
    t0 = time.time()
    img = framkall(luminans(lys, [], px, ss), px)
    Image.fromarray(img).save(os.path.join(UT, fil))
    print(fil, round(time.time() - t0, 1), 's')


def kalibrer_vegg(maal=100.0):
    """Finn lumen på veggstrøket som gjev målet i veggsona i arbeid."""
    d0 = tal(rom_t(1.0, 0.0)[0], [])['E_vegg']
    d1 = tal(rom_t(1.0, 100.0)[0], [])['E_vegg']
    return (maal - d0) / max((d1 - d0) / 100.0, 1e-9)


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    try:      # lågaste prioritet og kjerne 2 til 7, så lyden og resten av maskina går først
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040); ctypes.windll.kernel32.SetProcessAffinityMask(ctypes.windll.kernel32.GetCurrentProcess(), 0xFC)
    except Exception: pass
    kva = sys.argv[1] if len(sys.argv) > 1 else 'overgang'
    px = int(sys.argv[2]) if len(sys.argv) > 2 else 700
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    if kva == 'marknad':
        berre = sys.argv[4] if len(sys.argv) > 4 else None       # til dømes: python rom.py marknad 500 2 litra
        mfil = os.path.join(UT, 'marknad.json')
        ut = json.load(open(mfil, encoding='utf-8')) if (berre and os.path.exists(mfil)) else {}
        for namn, (lys, kropp) in marknad().items():
            if berre and namn != berre: continue
            ut[namn] = tal_lampe(lys, kropp)
            print(namn, ut[namn], flush=True)
            if px: bilete_k(lys, kropp, f'marknad-{namn}.png', px, ss)
        json.dump(ut, open(os.path.join(UT, 'marknad.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        sys.exit(0)
    vlm = kalibrer_vegg(100.0)
    print('veggstrøk for 100 lx:', round(vlm, 1), 'lm')
    ut = {'veggstrok_lm': round(vlm, 1)}
    if kva == 'overgang':
        for namn, t in (('stemning', 0.0), ('paa-veg', 0.5), ('arbeid', 1.0)):
            lys, _ = rom_t(t, vlm)
            ut[namn] = dict(t=t, K=2200 + 800 * t, **tal_rom(lys))
            print(namn, ut[namn])
            if px: bilete(lys, f'rom-{namn}.png', px, ss)
        json.dump(ut, open(os.path.join(UT, 'rom-overgang.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    elif kva == 'krav':
        lys, _ = rom_t(1.0, vlm)
        ut['arbeid'] = tal_rom(lys)
        ut['punkt'] = dict(
            felt=[proj(b(-0.3, 0.05, 0)), proj(b(0.3, 0.05, 0)), proj(b(0.3, 0.45, 0)), proj(b(-0.3, 0.45, 0))],
            felt_midt=proj(FELT),
            vegg=[proj(b(-0.7, YV, 0.08)), proj(b(0.7, YV, 0.08)), proj(b(0.7, YV, 0.78)), proj(b(-0.7, YV, 0.78))],
            vegg_merke=proj(b(0.45, YV, 0.60)),
            skjerm_midt=proj(b(0, 0.45, 0.265)),
            auge=proj(AUGE), hovud=proj(b(0, -0.25, 0.49)),
            lampeplass=proj(b(0.47, 0.40, 0.0)),
        )
        print(ut)
        if px: bilete(lys, 'rom-krav.png', px, ss)
        json.dump(ut, open(os.path.join(UT, 'rom-krav.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
