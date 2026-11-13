# -*- coding: utf-8 -*-
"""Generasjon 2: identiteten til rørsla. Kva klipp kan vere overgangen?
Kvar kropp er ei anna handling: dreie, skyve to lag, vippe, skyve langs stonga, opne ei luke, vri lamellar.
Pluss optikken frå overheadprojektoren: fresnelplata som reflektor, og linsa som avbildar holet på veggen."""
from familie import *
from familie import _bokfor          # namn med understrek kjem ikkje med i import *
N2 = 20
lerp = lambda a, c, t: a + (c - a) * t

def maane_drei(t):      # skive med bit. Strålen siktar 4 cm ned på skiva. Dreiing flyttar bitet ut av strålen
    return lampe(t, klipp=maane(0.085, dv=-0.075), sikt=(0, -0.04), rull=lerp(0, 110, t), n=N2)
def halv_drei(t):       # halv skive på ein tapp i sentrum. Strålen siktar 4 cm ned
    return lampe(t, klipp=halv(0.0), sikt=(0, -0.04), rull=lerp(180, 35, t), n=N2)
def fase(t):            # to halve skiver oppå kvarandre, den eine dreier: opninga går frå 180 til 80 grader
    th = lerp(180, 80, t)
    return lampe(t, klipp=sektor(th, -90), lag=[halv(0.0), halv(0.0)], n=N2)
def formorking(t):      # skive med hol Ø 14 cm og ei lita skive Ø 15 cm som glir inn over holet ovanfrå
    d = lerp(0.16, 0.045, t); liten = lambda u, v: u * u + (v - d) ** 2 < 0.075 ** 2
    return lampe(t, klipp=eller(ring(0.07), liten), lag=[ring(0.07), lambda u, v: u * u + v * v < 0.075 ** 2], n=N2)
def ring_vipp(t):       # ring, arket vippar: speglinga går frå veggen til feltet
    return lampe(t, klipp=ring(0.05), mot=lerp(b(0.0, YV, 0.45), FELT, t), n=N2)
def heil_vipp(t):       # referanse: same vipp utan klipp
    return lampe(t, mot=lerp(b(0.0, YV, 0.45), FELT, t), n=N2)
def blad_skyv(t):       # bladet glir langs stonga: langt ute fangar det lite av strålen, nær fangar det mykje
    kp = OPPST['fram']['kp']; ax = nrm(OPPST['fram']['c'] - kp)
    return lampe(t, klipp=blad(0.12), c=kp + ax * lerp(0.56, 0.30, t), n=N2)
def luke(t):            # rund luke midt i skiva, hengsla nede, opnar seg mot kjelda
    return lampe(t, flikar=[dict(u=0.0, v=-0.055, b=0.11, l=0.11, vinkel=lerp(80, 25, t), akse=0)], n=N2)
def lamell(t):          # fire lamellar som blir vridde
    a = lerp(65, 12, t)
    return lampe(t, flikar=[dict(u=0.0, v=v0, b=1.7 * math.sqrt(R0 ** 2 - (v0 + 0.018) ** 2), l=0.036, vinkel=a, akse=0, rund=False)
                            for v0 in (-0.085, -0.04, 0.005, 0.05)], n=N2)
def to_lag_hol(t):      # to like holark, det eine blir skove
    h = hol(0.05, 0.017)
    return lampe(t, klipp=eller(h, flytt(h, du=lerp(0.0, 0.02, t))), lag=[h, h], n=24)
def vifte_drei(t):      # to vifter med tre blad, den eine dreier
    v1 = vifte(3, 0.5); v2 = vifte(3, 0.5, dreiing=lerp(0, 38, t))
    return lampe(t, klipp=eller(v1, v2), lag=[v1, v1], n=N2)

# overheadprojektoren
KPF = OPPST['fram']['c'] + 0.16 * nrm(OPPST['fram']['kp'] - OPPST['fram']['c'])     # kjelda 16 cm frå plata, innanfor brennvidda
def fresnel_heil(t):    # fresnelplata som reflektor. Omrisset er klippet: det som går forbi plata, går til veggen
    return lampe(t, kp=KPF, storleik=(0.285, 0.285), fresnel=dict(f=0.1871, spreiing=2.5), spreiing=30, n=30)
def fresnel_maske(t):   # matt halvmåne av papir oppå plata, glir frå å dekkje nedre halvdel til å dekkje lite
    m = halv(lerp(0.0, 0.10, t))
    return lampe(t, kp=KPF, storleik=(0.285, 0.285), fresnel=dict(f=0.1871, spreiing=2.5), spreiing=30, n=30,
                 klipp=lambda u, v: ~m(u, v), lag2=dict(klipp=m, side=MATT), lag=[None])
def ring_linse(t):      # projeksjonslinsa og spegelen bak holet avbildar holet som ei mjuk sol på veggen over skjermen
    r = 0.04
    def ekstra(ks, arka, rm):
        c, ex, ey, ez = rm
        heilt = ark(ks, c, ez, 2 * R0, n=N2, framside=SATIN).lm_inn
        _bokfor(ks, arka)                                   # ark() skreiv over lm_ut. Set attende
        gjennom = heilt - arka[0].lm_inn
        lm = 0.80 * gjennom                                 # ANTAKING: linse og spegel slepper 80 %
        for k in ks: k.lm_ut = max(k.lm_ut - gjennom / len(ks), 0.0)
        s = straale(c - 0.06 * ez, b(0.05, YV, 0.50), lm, ks[0].K, maske=maske_vegg(0.05, ZB + 0.50, 0.26, k=0.05), opning=0.035)
        s.lm_ut = lm; s.lm = 0.0                             # watten er alt rekna i kjelda
        return [s], [skive(c - 0.02 * ez, ez, r + 0.004)]
    return lampe(t, klipp=ring(r), ekstra=ekstra, n=N2)

def velt_sveip(t):      # heil skive som blir vend frå veggen til feltet framom ansiktet
    mot = lerp(b(-0.3, YV, 0.6), AUGE, 2 * t) if t < 0.5 else lerp(AUGE, FELT, 2 * t - 1)
    return lampe(t, mot=mot, n=N2)
def umogl_kuppel(t):    # holark pressa til kuppel: dobbeltkrumt
    Rk = 0.20
    return lampe(t, klipp=hol(0.05, 0.014), form=lambda U, V: (U, V, -(Rk - np.sqrt(Rk * Rk - U * U - V * V))), n=N2)

G2 = [('maane-drei', maane_drei), ('halv-drei', halv_drei), ('fase', fase), ('formorking', formorking),
      ('ring-vipp', ring_vipp), ('heil-vipp', heil_vipp), ('blad-skyv', blad_skyv), ('luke', luke),
      ('lamell-vri', lamell), ('to-lag-hol', to_lag_hol), ('vifte-drei', vifte_drei),
      ('fresnel', fresnel_heil), ('fresnel-maske', fresnel_maske), ('ring-linse', ring_linse),
      ('VELT-sveip', velt_sveip), ('UMOGL-kuppel', umogl_kuppel)]
if __name__ == '__main__':
    a = sys.argv[1:]
    if '--overgang' in a:
        sys.stdout.reconfigure(encoding='utf-8')
        for namn in a[a.index('--overgang') + 1:]:
            _, m = overgang(dict(G2)[namn], n=5)
            print('overgang %-12s topp %.2f sprang %.2f jamn auke %.2f  auge %s  felt %s  vegg %s'
                  % (namn, m['topp'], m['sprang'], m['jamn_auke'], [round(x) for x in m['auge']], [round(x) for x in m['felt']], [round(x) for x in m['vegg']]))
    else:
        kjor(G2, {}, os.path.join(HER, 'gen2'), px=0)
