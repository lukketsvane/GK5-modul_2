# Filmen i lysmotoren: bruksrettleiing

Dato: 13.11.2026. Tre filer i `konsept/film/`. Alt er modell, ikkje måling. Arket er førebels rekna som eit ideelt 90°-prisme (ANTAKING) til dommen i `konsept/vindauge/film/arket.md` ligg føre.

| Fil | Kva |
| --- | --- |
| `film.py` | Arket: strålesporing gjennom éin periode av profilen, per bølgjelengd |
| `kast.py` | Diode, masker og film som kastar lys ut i rommet. Gjev strøk til `tal()` og lux-kart |
| `vindauge.py` | Tre grep for «varmt vindauge utan linse», med same tal som A, B og C |

## film.py

```python
from film import Film, prisme, linse, boelgje
f = Film(prisme(toppvinkel=90, avrunding=0.0, land=0.0), n_d=1.59, abbe=30,
         spreiing=0.0, spreiing_langs=0.0, haze=0.0, T_ekstra=1.0)
```

Filmkoordinatar: x på tvers av rillene, y langs rillene, z ut av den rifla sida.

- `prisme(toppvinkel, avrunding, land)`: symmetrisk prisme. `avrunding` er radius på toppen og `land` flat dal, begge som del av perioden. `linse(radius)` er sylinderlinser, `boelgje(amplitude)` ein sinusprofil. Eigen profil: punkt `(x, h)` frå x = 0 til 1.
- `n_d`, `abbe`: brytingsindeks ved 587,6 nm og Abbe-tal. `f.n(lam)` gjev indeksen (Cauchy).
- `spreiing`, `spreiing_langs`: ekstra gaussisk spreiing i grader (sigma), på tvers av og langs rillene. `haze`: diffus del. Dette er der matt bakside og ujamne prisme kjem inn.
- `f.spor(D, lam=550, side='prisme')`: D er retningar (N, 3) i filmkoordinatar. `side='prisme'` sender lyset inn mot den rifla sida, `'flat'` inn gjennom den flate. Gjev `(D_ut, ut)` der `ut` er +1 gjennom, −1 kasta attende, 0 tapt.
- `f.gjennom(D, normal, riller, lam=550)`: same i romkoordinatar. `normal` peikar ut av den rifla sida, `riller` er retninga rillene går. Sida blir lesen av retninga til lyset.
- `f.lober(theta_x, theta_y=0, lam=550, side='prisme')`: gjev `(T, R, [(vinkel, del), ...])`. Vinklane er i planet på tvers av rillene.
- `f.fordeling(...)`: histogram over utgåande vinkel.
- `analytisk_splitt(n, toppvinkel)`: kontrollformelen for lys rett inn mot prismesida.

Komponenten langs rillene er bevart gjennom filmen (alle flatene er parallelle med rillene). Difor blir rette linjer langs rillene til bogar i kastet.

### Kontroll (`python film.py`)

| Prøve | Sporing | Analytisk |
| --- | --- | --- |
| Prismeside inn, rett på, 550 nm | to lober på ±30,8°, 0,47 kvar, T 0,93 | ±30,69° |
| Flatside inn, rett på | T 0,00, alt kasta attende | totalrefleksjon (45° > 38,9°) |
| Flatside inn, 30° | éi lobe på −0,8°, T 0,63 | samlar mot normalen |
| Fargebrot 450 til 650 nm | 31,75° til 30,25° | 31,57° til 30,18° |
| Energi | T + R + tapt = 1, tapt under 0,003 | |

Prismeside inn, vippa: 10° gjev 0,53 og 0,38 i dei to lobene, 20° gjev 0,60 og 0,27, 30° gjev 0,62 og 0,15. Ved 40 til 50° kjem 3 % gjennom: filmen er då ein spegel.

## kast.py

```python
from kast import Kast, maske, rekt, vindauge, kartbilete
k = Kast(pos, mot, W, K, film=f, riller=(1, 0, 0), side='prisme', a=0.05, diode=0.002, led='lambert',
         film_normal=None, film_storleik=(0.04, 0.04), masker=[maske(0.045, [rekt(-0.01, 0.01, -0.01, 0.01)])],
         N=4_000_000, opplaus=0.5)
lys = k.lys()        # til tal(), luminans(), par()
```

- `pos` er dioden, `mot` eit punkt aksen peikar mot, `a` avstanden frå dioden til filmen. Filmsenteret er `k.H`.
- `diode`: diameteren på den lysande flata. Han set halvskuggen. `led='lambert'` er ei naken diode. Eit tal er sigma i grader for ei lykt med eigen optikk.
- `masker`: `maske(avstand, opningar, etter=False)`. Opningane er konvekse firkantar i maskeplanet, i meter frå aksen. `etter=True` set maska etter filmen.
- `film=None` gjev open ramme. `film_normal` vippar filmen (retninga den rifla sida peikar).
- `k.rekneskap`: kvar lyset blir av. `k.kart_vegg` og `k.kart_bord`: lux (rgb) i ruter på 4 mm, utan skuggar frå rommet. `kartbilete(kart, lux_kvit)` gjev bilete på svart.
- W er watten til dioden, 100 lm/W. Alt som maske, ramme og film stoppar, er tapt.

Strøka blir slik: fotona blir samla i ein retningstabell rundt filmsenteret, ut frå kvar dei landar på vegg og bord. Motoren reknar så skuggar, indirekte lys og tal som for alle andre strøk.

## vindauge.py

`g_open()`, `g_spjeld()`, `g_vipp()` gjev lysgrep `g(t)`. `rekn(g)` gjev same tal som `tre.rekn`. Kommandoar: `python vindauge.py tal`, `bilete`, `kart`.

## Det modellen ikkje reknar

- Filmen er uendeleg tynn i kastet: fotonet skiftar retning, ikkje plass.
- Lys som filmen kastar attende, er tapt. Eit kvitt hus bak filmen ville gje noko attende.
- Upolarisert lys, éin brytingsindeks, ingen absorpsjon.
- Spekteret er ein svart lekam ved fargetemperaturen (ANTAKING). Ei verkeleg diode har ein blå topp, så den blå kanten blir tydelegare enn her.
- Luminansen mot auget inne i ei lobe er rekna som biletet av dioden i filmen. Hette framfor filmen er ikkje med i `vindauge.py` enno.
