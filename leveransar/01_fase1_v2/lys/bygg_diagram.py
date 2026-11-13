# -*- coding: utf-8 -*-
"""Byggjer dei fire diagramsidene: 3B, berekraft, prosjektplan og bedriftsbesøk.
Innhaldet er henta frå første utgåve (leveransar/01_fase1_sider), der tala er kontrollerte.

  python bygg_diagram.py [3|5|6|7 ...]     utan argument: alle fire
"""
import os, sys

HER = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.normpath(os.path.join(HER, '..'))
NB = '&nbsp;'


def side(nr, namn, tittel, stil, innhald, kjelder, merknad, fil):
    html = ('<!doctype html>\n<html lang="nn">\n<head>\n<meta charset="utf-8">\n<title>' + nr + ' · ' + namn + '</title>\n'
            '<link rel="stylesheet" href="felles.css">\n<style>\n' + stil + '\n</style>\n</head>\n<body>\n<div class="side">\n'
            '  <header class="topp">\n    <span>GK5 · Northern · fase 1</span>\n    <span>' + nr + ' · ' + namn + '</span>\n'
            '    <span>Iver R. Finne · 13.11.2026</span>\n  </header>\n\n'
            '  <h1 class="tittel">' + tittel + '</h1>\n\n  <main class="innhald">\n' + innhald + '\n  </main>\n\n'
            '  <footer class="botn">\n    <span>' + kjelder + '</span>\n    <span>' + merknad + '</span>\n  </footer>\n</div>\n</body>\n</html>\n')
    open(os.path.join(V2, fil), 'w', encoding='utf-8', newline='\n').write(html)
    print('skrive', fil)


FELLES_STIL = '''  svg .kv { fill: var(--blekk); }
  svg .g { fill: var(--graa); }
  svg .stort { font-family: var(--serif); font-size: 42px; fill: var(--blekk); letter-spacing: -0.01em; }
  svg .mellom { font-family: var(--serif); font-size: 22px; fill: var(--blekk); }
  svg .kvs { stroke: var(--blekk); fill: none; }
  svg .gs { stroke: var(--graa); fill: none; }
  .tekst p:not(.etikett) { font-size: 13.5px; line-height: 1.34; }
  .tekst p.kv { color: var(--blekk); }
  ul.rad { list-style: none; margin: 0; padding: 0; }
  ul.rad li { font-size: 13px; line-height: 1.3; padding: 4px 0 5px; border-top: 1px solid var(--linje); }'''


# ------------------------------------------------------------------ 03 · 3B-analyse
def side3():
    def x(h):
        return round(70 + (h - 7) * 60.5, 2)
    S = []
    # store tal i det tome hjørnet
    S.append(f'<text x="0" y="40" class="stort">45,1{NB}%</text>')
    S.append('<text x="0" y="58" class="graa">HAR HEIMEKONTOR</text>')
    S.append(f'<text x="0" y="112" class="stort">5,7{NB}%</text>')
    S.append('<text x="0" y="130" class="graa">MINST HALVE TIDA</text>')
    S.append('<text x="0" y="158" class="graa">AV SYSSELSETTE · SSB 4. KV. 2025</text>')
    # tre rom ved sine klokkeslett
    for fil, hc, t1, t2 in (('rom-arbeid.png', 11.75, 'ARBEID', f'350{NB}lx på feltet'),
                            ('rom-paa-veg.png', 16.5, 'SKIFTET', f'éi rørsle, under 10{NB}s'),
                            ('rom-stemning.png', 20.25, 'STEMNING', f'50 til 200{NB}lm')):
        x0 = round(x(hc) - 107, 1)
        S.append(f'<image href="bilete/{fil}" x="{x0}" y="0" width="214" height="214"/>')
        S.append(f'<text x="{x0}" y="228"><tspan class="kv">{t1}</tspan><tspan class="g"> · {t2}</tspan></text>')
    S.append('<g transform="translate(0,28)">')
    # kritisk steg
    xk = x(16.5)
    S.append(f'<line x1="{xk}" y1="206" x2="{xk}" y2="320" class="kvs" stroke-width="1.5"/>')
    S.append(f'<text x="{xk + 7}" y="222" class="kv">KRITISK STEG 16.30</text>')
    S.append(f'<text x="{xk + 7}" y="234" class="graa">éi rørsle frå arbeid til stemning · krav F2</text>')
    # dagslys
    S.append('<text x="0" y="235" class="graa">DAGSLYS</text>')
    S.append(f'<line x1="{x(9.3)}" y1="232" x2="{x(15.2)}" y2="232" stroke="#6A6A6A" stroke-width="5"/>')
    S.append(f'<text x="{x(9.3) + 6}" y="222" class="graa">09.18 til 15.12 (Oslo ved vintersolverv)</text>')
    # straum
    S.append('<text x="0" y="261" class="graa">STRAUM</text>')
    S.append(f'<line x1="{x(7.5)}" y1="258" x2="{x(19)}" y2="258" class="kvs" stroke-width="1.5"/>')
    S.append(f'<text x="{x(7.5) + 4}" y="250">leidning, USB-C</text>')
    S.append(f'<line x1="{x(19)}" y1="258" x2="{x(22.5)}" y2="258" class="kvs" stroke-width="1.5" stroke-dasharray="4 3"/>')
    S.append(f'<text x="{x(19) + 6}" y="250">batteri</text>')
    S.append(f'<line x1="{x(22.5)}" y1="258" x2="{x(23)}" y2="258" class="kvs" stroke-width="1.5"/>')
    # modus
    S.append('<text x="0" y="292" class="graa">MODUS</text>')
    S.append(f'<rect x="{x(7.5)}" y="276" width="{xk - x(7.5):.2f}" height="24" class="strek"/>')
    S.append(f'<text x="{x(7.5) + 8}" y="292">arbeid · 350{NB}lx på feltet frå lampa, 500 med romlys</text>')
    S.append(f'<rect x="{xk}" y="288" width="{x(22.5) - xk:.2f}" height="12" class="lysflate"/>')
    S.append(f'<line x1="{xk}" y1="288" x2="{x(22.5)}" y2="288" class="kvs" stroke-width="1.5"/>')
    S.append(f'<text x="{xk + 7}" y="282">stemning · 50 til 200{NB}lm</text>')
    for h in (10, 13):
        S.append(f'<circle cx="{x(h)}" cy="276" r="3" class="fyll"/>')
        S.append(f'<text x="{x(h) + 7}" y="271">møte</text>')
    # tidsakse
    S.append(f'<line x1="{x(7)}" y1="320" x2="{x(23)}" y2="320" class="strek"/>')
    for h in range(7, 24):
        l = 5 if h % 2 else 3
        S.append(f'<line x1="{x(h)}" y1="320" x2="{x(h)}" y2="{320 + (5 if h % 2 == 1 else 3)}" class="strek"/>')
        if h % 2 == 1:
            a = 'end' if h == 23 else 'middle'
            S.append(f'<text x="{x(h)}" y="336" class="graa" text-anchor="{a}">{h:02d}</text>')
    # steg
    for xx, t, kl, a in ((100, '1 morgon', '', 'start'), (225, '2 fokusarbeid', '', 'start'), (405, '3 møte', '', 'start'),
                         (520, '4 ettermiddag', '', 'start'), (xk, '5 arbeidsslutt', 'kv', 'start'),
                         (796, '6 kveld, lampa står der folk sit', '', 'start'), (x(23), '7 natt', '', 'end')):
        k = ' class="kv"' if kl else ' class="graa"'
        S.append(f'<text x="{xx}" y="354"{k} text-anchor="{a}">{t}</text>')
    S.append('</g>')
    svg = '<svg width="1039" height="388" viewBox="0 0 1039 388" xmlns="http://www.w3.org/2000/svg">\n        ' + '\n        '.join(S) + '\n      </svg>'

    # veka
    U = []
    for i, d in enumerate('mtotfls'):
        cx = 96 + i * 27
        U.append(f'<text x="{cx + 11}" y="9" class="graa" text-anchor="middle">{d}</text>')
        fyll = '#F4F4F4' if i == 0 else ('#6A6A6A' if i == 1 else 'none')
        U.append(f'<rect x="{cx}" y="16" width="22" height="13" fill="{fyll}" stroke="#4A4A4A" stroke-width="1"/>')
        U.append(f'<rect x="{cx}" y="36" width="22" height="13" fill="#F4F4F4" stroke="#4A4A4A" stroke-width="1"/>')
    U.append('<text x="0" y="26" class="graa">ARBEIDSLYS</text>')
    U.append('<text x="0" y="46" class="graa">STEMNINGSLYS</text>')
    U.append('<text x="292" y="26" class="graa">1 til 2</text>')
    U.append('<text x="292" y="46" class="graa">7 av 7</text>')
    veke = '<svg width="336" height="52" viewBox="0 0 336 52" xmlns="http://www.w3.org/2000/svg">\n          ' + '\n          '.join(U) + '\n        </svg>'

    innhald = f'''    <figure class="k12">
      {svg}
    </figure>

    <section class="k3 tekst">
      <p class="etikett">Brukar</p>
      <p class="kv">Hybridarbeidaren, om lag 30 til 55{NB}år (mi avgrensing), som arbeider heime ein til to dagar i veka frå ein plass i eit fleirbruksrom.</p>
      <p class="graa">Halvparten sat i slike rom i 2021 (AFI, sekundærkjelde). Sekundærbrukarar: andre i hushaldet, den ein møter på skjermen, forhandlaren og attvinnaren.</p>
    </section>

    <section class="k5">
      <p class="etikett">Brukssituasjon</p>
      <table class="sit">
        <tr><td class="s">Fokusarbeid</td><td>350{NB}lx på feltet, 100 til 150{NB}lx ved skjermen, inga synleg eller spegla lyskjelde</td><td class="id">F1 F3 F6</td></tr>
        <tr><td class="s">Digitalt møte</td><td>50 til 200{NB}lx mjukt lys på ansiktet, utan flimmer</td><td class="id">F10 T1</td></tr>
        <tr><td class="s">Arbeidsslutt</td><td>frå arbeidslys til stemningslys med éi rørsle</td><td class="id">F2</td></tr>
        <tr><td class="s">Kveld</td><td>varmt og avskjerma lys, 50 til 200{NB}lm, på batteri</td><td class="id">F4 F5 F7</td></tr>
        <tr><td class="s">Flytting</td><td>berast med éi hand, høgst 1,2{NB}kg, og stå stødig</td><td class="id">F8 T2 T7</td></tr>
      </table>
    </section>

    <section class="k4 tekst">
      <p class="etikett">Bruksmåte</p>
      <figure style="margin-bottom: 8px;">
        {veke}
      </figure>
      <p class="kv">Ved arbeidsslutt tek den som ryddar, i lampa, skiftar lyset med éi rørsle og ser det bli varmt og lågt.</p>
      <p class="graa">Antakingar: økter på 8{NB}timar, stemningslys 3,5{NB}timar kvar kveld, flytting to gonger dagleg. Intervju og fotoobservasjon 14. og 15.11 prøver dei.</p>
    </section>'''
    stil = FELLES_STIL + '''
  .innhald { row-gap: 10px; }
  table.sit td { padding: 4px 8px 5px 0; font-size: 13px; line-height: 1.3; }
  table.sit tr:first-child td { border-top: 1px solid var(--linje); }
  table.sit td.s { color: var(--blekk); white-space: nowrap; width: 92px; }
  table.sit td.id { text-align: right; padding-right: 0; font-size: 10px; }'''
    side('03', '3B-analyse', 'Arbeidsslutten er det kritiske steget.', stil, innhald,
         'Bileta er modell: lyset briefen ber om, før lampa finst. Kjelder: SSB tabell 13999, AFI 2021 via Simployer, NS-EN 12464-1 via Arbeidstilsynet.',
         'Døgnlinja er konstruert, ikkje observert.', 'side-3-3b-analyse.html')


# ------------------------------------------------------------------ 05 · Berekraftshandling
def side5():
    def x(yr):
        return round(150 + yr * 500 / 30.0, 2)
    S = []
    # lag 1
    S.append('<text x="0" y="58" class="kv">1 KROPP OG SKJERM</text>')
    S.append('<text x="150" y="30">laga for tiår (mål, ikkje målt tal)</text>')
    S.append('<rect x="150" y="42" width="500" height="22" class="fyll"/>')
    S.append('<path d="M650 53 H678 M670 46 L678 53 L670 60" class="kvs"/>')
    S.append('<text x="150" y="86" class="graa">ingen byter kroppen · eigaren byter skjermen ved skade</text>')
    # lag 2
    S.append('<text x="0" y="161" class="kv">2 LYSMODUL OG</text>')
    S.append('<text x="0" y="174" class="kv">ELEKTRONIKK</text>')
    S.append(f'<text x="150" y="140">lysmodul 60{NB}000{NB}t (L70) oppgjeve for ei anna lampe · elektronikk ikkje talfesta</text>')
    S.append('<rect x="150" y="152" width="500" height="22" class="kvs" stroke-dasharray="5 4"/>')
    S.append('<text x="150" y="196" class="graa">eigaren eller Northern byter · under fem minutt</text>')
    # lag 3
    S.append('<text x="0" y="277" class="kv">3 BATTERI</text>')
    S.append(f'<text x="150" y="250">om lag 5{NB}år ved 100{NB}lm (2 til 9{NB}år) · 70 til 80{NB}% etter 500 syklusar</text>')
    for k in range(6):
        kl = 'fyll' if k == 0 else 'kvs'
        S.append(f'<rect x="{x(5 * k) + (2 if k else 0)}" y="262" width="{500 / 6.0 - 4:.2f}" height="22" class="{kl}"/>')
    for k in range(1, 6):
        S.append(f'<line x1="{x(5 * k) - 1}" y1="255" x2="{x(5 * k) - 1}" y2="291" class="kvs"/>')
    S.append(f'<path d="M{x(2)} 304 H{x(9)} M{x(2)} 300 V308 M{x(9)} 300 V308" class="gs"/>')
    S.append(f'<text x="{x(9) + 8}" y="307" class="graa">spennet 2 til 9{NB}år · kvar strek er eit byte om det blir fem år</text>')
    S.append('<text x="150" y="328" class="graa">eigaren byter · under eitt minutt</text>')
    # akse
    S.append('<line x1="150" y1="362" x2="650" y2="362" class="strek"/>')
    for yr in range(0, 31, 5):
        S.append(f'<line x1="{x(yr)}" y1="362" x2="{x(yr)}" y2="367" class="strek"/>')
        t = f'30{NB}år' if yr == 30 else str(yr)
        S.append(f'<text x="{x(yr)}" y="381" class="graa" text-anchor="middle">{t}</text>')
    svg = '<svg width="687" height="388" viewBox="0 0 687 388" xmlns="http://www.w3.org/2000/svg">\n        ' + '\n        '.join(S) + '\n      </svg>'

    innhald = f'''    <section class="k8">
      <p class="etikett">Lampa i lag etter levetid</p>
      <figure>
      {svg}
      </figure>
      <p class="handling">Eg byggjer lampa i lag etter levetid. Ho lyser fullt ut på leidning utan batteri, batteriet blir skåna, og batteri, elektronikk og lysmodul kan kjøpast og bytast.</p>
      <div class="maal">
        <div>under 1{NB}min<small>batteriet ute</small></div>
        <div>under 5{NB}min<small>lysmodul og elektronikk</small></div>
        <div>2<small>vanlege verktøy, høgst</small></div>
        <div>0<small>limfuger</small></div>
      </div>
    </section>

    <section class="k4 tekst">
      <p class="etikett">Kvifor levetid og ikkje lysutbyte</p>
      <div class="tal3">
        <div>29{NB}%<small>av påverknaden til ei LED-pære i Noreg ligg i bruken (Bertin mfl. 2020)</small></div>
        <div>7 mot 28{NB}kg<small>CO<sub>2</sub>e: ti års straum mot produksjonen av ein armatur (eige overslag, Glamox-EPD)</small></div>
        <div>om lag 2{NB}×<small>så mykje gjev lengre levetid som høgare lysutbyte (Bertin mfl. 2020)</small></div>
      </div>
      <p class="etikett" style="margin-top: 12px;">Lov</p>
      <p>Reparasjonsdirektivet (EU) 2024/1799 gjeld ikkje lamper. Batteriforordninga artikkel 11 krev brukarbytbart batteri frå 18.02.2027. Handlinga går lenger: drift utan batteri, bytbar elektronikk og tidfesta byte.</p>
      <p class="etikett" style="margin-top: 10px;">Northern</p>
      <p>Snowball oppladbar er oppgjeven med utskiftbar LED-modul og batteri. Per 12.11.2026 ligg ingen av dei i nettbutikken, og rettleiinga viser ikkje bytet.</p>
      <p class="graa" style="margin-top: 10px;">Usikkert: eg har ikkje funne LCA for ei oppladbar bordlampe. Brukarar og Northern er ikkje spurde.</p>
    </section>'''
    stil = FELLES_STIL + '''
  .handling { font-size: 19px; line-height: 1.26; color: var(--blekk); margin: 14px 0 16px; max-width: 660px; }
  .maal { display: flex; gap: 34px; align-items: flex-end; }
  .maal div { font: 400 30px/1 var(--serif); color: var(--blekk); white-space: nowrap; }
  .maal small, .tal3 small { display: block; font: 400 9.5px/1.35 var(--mono); letter-spacing: 0.06em; text-transform: uppercase; color: var(--graa); margin-top: 6px; white-space: normal; }
  .tal3 div { font: 400 32px/1 var(--serif); color: var(--blekk); padding: 8px 0 9px; border-top: 1px solid var(--linje); }
  .tal3 small { text-transform: none; letter-spacing: 0.03em; font-size: 10px; }'''
    side('05', 'Berekraftshandling', 'Delen som eldest først, skal kunne bytast utan at resten blir rørt.', stil, innhald,
         'Kjelder: Samsung SDI, Louis Poulsen, Battery University, Glamox EPD NEPD-7583-6966, Bertin mfl. 2020, (EU) 2024/1799 og 2023/1542, northern.no.',
         'Overslaga viser storleiksorden.', 'side-5-berekraftshandling.html')


# ------------------------------------------------------------------ 06 · Prosjektplan
def side6():
    X0, W = 190, 31

    def x(d):
        return X0 + W * d
    dagar = [12 + i for i in range(19)] + [1 + i for i in range(7)]          # 12.11 til 7.12
    veke = 'tflsmtotflsmtotflsmtotflsm'
    S = []
    S.append(f'<text x="{x(0)}" y="10" class="graa">NOVEMBER</text>')
    S.append(f'<text x="{x(19)}" y="10" class="graa">DESEMBER</text>')
    for d in range(26):
        helg = veke[d] in 'ls'
        if helg:
            S.append(f'<rect x="{x(d)}" y="44" width="{W}" height="218" fill="#161616"/>')
        kl = 'g' if helg else 'kv'
        S.append(f'<text x="{x(d) + W / 2}" y="26" class="{kl}" text-anchor="middle">{dagar[d]}</text>')
        S.append(f'<text x="{x(d) + W / 2}" y="38" class="graa" text-anchor="middle">{veke[d]}</text>')
    S.append(f'<line x1="{x(0)}" y1="44" x2="{x(26)}" y2="44" class="haar"/>')
    # fasar
    fasar = (('1 RESEARCH OG GRUNNLAG', 0, 5, 24), ('2 KONSEPT', 0, 8, 38), ('3 FORM', 8, 15, 36), ('4 KONSTRUKSJON OG MODELL', 15, 26, 52))
    for i, (namn, a, c, t) in enumerate(fasar):
        y = 70 + i * 42
        S.append(f'<text x="0" y="{y + 4}" class="kv">{namn}</text>')
        S.append(f'<rect x="{x(a)}" y="{y - 7}" width="{W * (c - a)}" height="14" class="fyll"/>')
        S.append(f'<text x="1039" y="{y + 7}" class="mellom" text-anchor="end">{t}{NB}t</text>')
    # milepælar
    ym = 276
    S.append(f'<text x="0" y="{ym + 3}" class="graa">MILEPÆLAR</text>')
    S.append(f'<line x1="{x(0)}" y1="{ym}" x2="{x(26)}" y2="{ym}" class="haar"/>')
    mil = ((1, '13.11 fase 1 i Figma · i dag', 'over', 'end', True), (5, '17.11 Moodle kl. 23', 'under', 'end', False),
           (6, '18.11 KONSEPTGJENNOMGANG', 'over', 'start', True), (11, '23.11 refleksjonsoppgåve kl. 09 (eige arbeid)', 'under', 'start', False),
           (13, '25.11 formgjennomgang', 'over', 'start', False), (25, '7.12 Moodle kl. 08 og sluttpresentasjon', 'over', 'end', True))
    for d, t, kvar, anker, kvit in mil:
        cx = x(d) + W / 2
        S.append(f'<line x1="{cx}" y1="44" x2="{cx}" y2="{ym - 27}" class="gs" stroke-dasharray="2 3"/>')
        S.append(f'<path d="M{cx} {ym - 6} L{cx + 6} {ym} L{cx} {ym + 6} L{cx - 6} {ym} Z" class="fyll"/>')
        yy = ym - 13 if kvar == 'over' else ym + 20
        dx = 10 if anker == 'start' else -10
        kl = 'kv' if kvit else 'graa'
        S.append(f'<text x="{cx + dx}" y="{yy}" class="{kl}" text-anchor="{anker}">{t}</text>')
    svg = '<svg width="1039" height="302" viewBox="0 0 1039 302" xmlns="http://www.w3.org/2000/svg">\n        ' + '\n        '.join(S) + '\n      </svg>'

    innhald = f'''    <figure class="k12">
      <p class="etikett">Tidsplan 12. november til 7. desember 2026</p>
      {svg}
    </figure>

    <section class="k4">
      <p class="etikett">Førehandsprøver før konseptvalet</p>
      <ul class="rad">
        <li>Blending: foto frå tre augehøgder over bordet.</li>
        <li>Arbeidslys: lux i rutenett over 0,6 × 0,4{NB}m.</li>
        <li>Overgang: rørsler og tid. Mål: éi rørsle, under 10{NB}s.</li>
        <li>Northern: mot Salto, Balancer mini, Kin og Snowball.</li>
        <li>Reparasjon: steg og verktøy, lesne av snittet.</li>
      </ul>
      <p class="liten kvit" style="margin-top: 8px;">Føreseiinga blir skriven ned først. Same lyskjelde i alle tre konsepta.</p>
    </section>

    <section class="k4">
      <p class="etikett">Risiko og tiltak</p>
      <ul class="rad">
        <li>Ulikt nivå på konsepta: same mal, målestokk og materiale.</li>
        <li>Modellane kjem etter teksten: to blir bygde i helga.</li>
        <li>Lyset held ikkje måla: prøver før valet, lysrigg etter.</li>
        <li>Lysdelar kjem seint: tinging 16.11, reserve LED-pære.</li>
        <li>Prenten feilar: reservemodell i papp og skum.</li>
        <li>Northern svarar ikkje: pris og volum blir antakingar.</li>
      </ul>
    </section>

    <section class="k4 tekst">
      <div class="timar"><div>150{NB}t<small>frå 12.11 til 7.12</small></div><div class="graatal">34 · 36 · 36 · 40 · 4<small>per veke</small></div></div>
      <p class="graa">Helgane etter 15.11 er reserve. Refleksjonsoppgåva og mekanikken ligg utanfor. Timane før 12.11 er ikkje førte.</p>
      <p class="etikett" style="margin-top: 10px;">Spørsmål denne veka</p>
      <p><em>Faglærar:</em> korleis eg oppgjev KI-bruk, om plansja gjeld eitt eller tre konsept, og når mekanikktesten er. <em>Ekstern rettleiar:</em> luminans på synleg lysflate, kompakt optikk som hyllevare, lån av luxmålar. <em>Northern, blir sende 13.11:</em> produksjon, årsvolum, målpris, kundar og reservedelar.</p>
    </section>'''
    stil = FELLES_STIL + '''
  .innhald { row-gap: 12px; }
  .timar { display: flex; gap: 26px; align-items: flex-end; margin-bottom: 8px; }
  .timar div { font: 400 34px/1 var(--serif); color: var(--blekk); white-space: nowrap; }
  .timar div.graatal { font-size: 20px; color: var(--tekst); }
  .timar small { display: block; font: 400 9.5px/1.3 var(--mono); letter-spacing: 0.06em; text-transform: uppercase; color: var(--graa); margin-top: 6px; }
  .tekst em { color: var(--blekk); }'''
    side('06', 'Prosjektplan', 'Tre konsept skal vere bygde og prøvde likt før 18. november.', stil, innhald,
         'Kjelder: prosjektbeskrivinga, designbriefen og Teams-post frå modulansvarleg 11.11.2026.',
         'Rettleiing og Figma-fristar etter 13.11 er ikkje stadfesta.', 'side-6-prosjektplan.html')


# ------------------------------------------------------------------ 07 · Bedriftsbesøk
def side7():
    def x(aar):
        return round(210 + (aar - 1930) * 790 / 96.0, 2)
    S = []
    rader = (('L-1', 'Glamox med Luxo', 1937, False, True), ('Doggerbank', 'Aalesund Protective Wear', 1956, True, True),
             ('Siesta', 'LK Hjelle', 1965, False, True), ('Stressless', 'Ekornes', 1971, False, True),
             ('Tripp Trapp', 'Stokke', 1972, False, True), ('Birdy', 'Northern', 1952, False, False))
    for i, (prod, bed, aar, foer, kvit) in enumerate(rader):
        y = 30 + i * 31 + (10 if i == 5 else 0)
        kl = 'kv' if kvit else 'g'
        S.append(f'<text x="0" y="{y + 4}"><tspan class="{kl}">{prod.upper()}</tspan><tspan class="g"> · {bed}</tspan></text>')
        if foer:
            S.append(f'<line x1="{x(1930)}" y1="{y}" x2="{x(aar)}" y2="{y}" class="kvs" stroke-width="2" stroke-dasharray="3 4"/>')
            S.append(f'<text x="{x(aar) - 6}" y="{y - 7}" class="graa" text-anchor="end">før {aar}</text>')
        else:
            S.append(f'<text x="{x(aar)}" y="{y - 7}" class="{"kv" if kvit else "graa"}">{aar}</text>')
        farge = '#F4F4F4' if kvit else '#6A6A6A'
        S.append(f'<line x1="{x(aar)}" y1="{y}" x2="{x(2026)}" y2="{y}" stroke="{farge}" stroke-width="{5 if kvit else 3}"/>')
        S.append(f'<circle cx="{x(aar)}" cy="{y}" r="{4 if kvit else 3}" fill="{farge}"/>')
    S.append(f'<line x1="0" y1="181" x2="{x(2026)}" y2="181" class="haar"/>')
    # femti år sidan
    S.append(f'<line x1="{x(1976)}" y1="6" x2="{x(1976)}" y2="212" class="gs" stroke-dasharray="2 3"/>')
    S.append(f'<text x="{x(1976) + 7}" y="12" class="kv">1976 · FEMTI ÅR SIDAN</text>')
    S.append(f'<text x="{x(2026)}" y="12" class="graa" text-anchor="end">I SAL I DAG</text>')
    # akse
    S.append(f'<line x1="{x(1930)}" y1="212" x2="{x(2026)}" y2="212" class="strek"/>')
    for aar in list(range(1930, 2021, 10)) + [2026]:
        S.append(f'<line x1="{x(aar)}" y1="212" x2="{x(aar)}" y2="217" class="strek"/>')
        a = 'end' if aar == 2026 else 'middle'
        if aar != 2020:
            S.append(f'<text x="{x(aar)}" y="230" class="graa" text-anchor="{a}">{aar}</text>')
    svg = '<svg width="1039" height="236" viewBox="0 0 1039 236" xmlns="http://www.w3.org/2000/svg">\n        ' + '\n        '.join(S) + '\n      </svg>'

    innhald = f'''    <figure class="k12">
      {svg}
    </figure>

    <section class="k12">
      <p class="felles">Alle fem har eit produkt som er over femti år og framleis i sal. Northern har same slags arv i Birdy av Birger Dahl frå 1952. Glamox og Luxo lagar arbeidslys for yrkesbygg, Northern lamper for heimen. Arbeidslys for heimearbeidsplassen ligg mellom dei.</p>
    </section>

    <section class="k12">
      <table class="bed">
        <tr><th style="width: 19%;">Bedrift</th><th style="width: 41%;">Verksemd og identitet (mi tolking)</th><th>Det eg tek med til lampa</th></tr>
        <tr><td class="n">AALESUND PROTECTIVE WEAR<small>Ålesund</small></td><td>Arbeidsklede, regntøy og redningsutstyr til fiskeri, havbruk og industri. Vernar folk i arbeid, og prøver ut saman med brukarane.</td><td>Eg prøver skissemodellane på folk som ikkje kjenner dei.</td></tr>
        <tr><td class="n">STOKKE<small>Ålesund</small></td><td>Barneutstyr i premiumsegmentet, produsert hos leverandørar i ti land. Produkt som veks med barnet.</td><td>Eit produkt som følgjer brukaren, blir verande. Lampa skal følgje dagen frå arbeid til kveld.</td></tr>
        <tr><td class="n">EKORNES<small>Sykkylven</small></td><td>Møblar under merka Stressless, IMG og Svane, frå eigne fabrikkar. Komfort i stor serie.</td><td>Komfort som lovnad. For lampa er det lys som ikkje blendar.</td></tr>
        <tr><td class="n">LK HJELLE<small>Sykkylven</small></td><td>Sofaer og lenestolar frå eigen fabrikk, om lag 35 tilsette. Møblane skal kunne reparerast.</td><td>Reservedelar som eigen kategori: det berekraftshandlinga mi ber Northern om.</td></tr>
        <tr><td class="n">GLAMOX MED LUXO<small>registrert i Molde</small></td><td>Profesjonelt lys til yrkesbygg, skip og offshore. Fagleverandør til profesjonelle kundar.</td><td>L-1 som målestokk for arbeidslys: 529{NB}lm, med E27-pære som eigaren byter sjølv.</td></tr>
      </table>
    </section>'''
    stil = FELLES_STIL + '''
  .innhald { row-gap: 12px; }
  .felles { font-size: 19px; line-height: 1.28; color: var(--blekk); max-width: 940px; margin: 2px 0 2px; }
  table.bed { font-size: 13.5px; line-height: 1.32; }
  table.bed td { padding: 6px 18px 7px 0; }
  table.bed td.n { font: 400 10px/1.4 var(--mono); letter-spacing: 0.04em; color: var(--blekk); padding-top: 9px; }
  table.bed td.n small { display: block; color: var(--graa); font-size: 10px; }'''
    side('07', 'Bedriftsbesøk i Ålesund-regionen', 'Fem bedrifter, lesne frå skrivebordet.', stil, innhald,
         'Eg var ikkje med på studieturen. Kjelder (12.11.2026): nettsidene til bedriftene, Brønnøysundregistra, Store norske leksikon, northern.no.',
         'Sal utan opphald er ikkje kontrollert.', 'side-7-bedriftsbesok.html')


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    kva = sys.argv[1:] or ['3', '5', '6', '7']
    for k in kva:
        {'3': side3, '5': side5, '6': side6, '7': side7}[k]()
