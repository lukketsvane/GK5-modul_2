# Lysmotoren: bruksrettleiing

`lysskisse.py` reknar lyset frå ei lampe i eit fast rom og gjev same tal for alle. Start frå `konsept/reflektor/_mal.py`.

```python
import sys, os
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))   # tilpass stien
from lysskisse import *
```

## Rommet

Meter. x mot høgre, y frå brukaren mot veggen, z opp. `b(x, y, h)` gjev eit punkt h meter over bordplata.

| Ting | Plass |
| --- | --- |
| Bord | x frå -0,7 til 0,7, y frå 0 til 0,7. Vegg ved y = 0,70 (`YV`) |
| Skjerm | 54 × 31 cm, framsida i y = 0,45, underkant 11 cm og overkant 42 cm over bordet |
| Auge | `AUGE` = b(0, -0.15, 0.47): 47 cm over bordet, 60 cm frå skjermen |
| Arbeidsfelt | 0,6 × 0,4 m: x frå -0,3 til 0,3, y frå 0,05 til 0,45. `FELT` = b(0, 0.25, 0) er midten |
| Veggsona | veggen rundt skjermen: x frå -0,7 til 0,7, 8 til 78 cm over bordet |

Regel frå første brett: lyspunkt og reflektor må stå framfor skjermplanet (y under 0,45) eller over skjermkanten. Elles legg skjermen skugge over feltet.

## Strøk (lys rett ut i rommet)

```python
glod(pos, r, lm, K)                                   # glødande kule
royr(a, b, r, lm, K)                                  # glødande røyr
flate(senter, normal, storleik, lm, K, tosidig=False) # matt lysande flate. storleik: diameter eller (breidd, høgd)
straale(pos, mot, lm, K, spreiing=20, flat=None, kutt=None, horisont=None,
        maske=None, opning=0.03, sprut=0.02, bronn=None)
```

`straale`: `spreiing` er sigma i grader. `flat=(vassrett, loddrett)` gjev vifte. `kutt` skjer av alt over ein vinkel frå aksen. `horisont=-8` gjev ingen lys over 8° under vassrett. `opning` er radius eller (breidd, høgd). `sprut` er delen som lek diffust frå opninga (ANTAKING 2 %). `bronn=40` senkar opninga ned i ein brønn, så ingenting syner over 40° frå aksen. `maske=maske_bord(x0, x1, y0, y1)` og `maske=maske_vegg(cx, cz, r)` gjev skarp form avbilda på bord eller vegg.

## Arket (reflektoren som form)

```python
k = straale(kjeldeplass, arksenter, W * LMW_KJELDE, K, spreiing=10, kutt=20, opning=0.02, bronn=40)
a = ark(k, senter, normal, storleik=0.25, form=None, klipp=None, n=22, rull=0.0,
        framside=SATIN, bakside=MORK, fresnel=None, tone=None)
lys = [k, a]          # ta alltid med kjelda òg. Lys som går forbi arket, held fram ut i rommet
```

- `senter`, `normal`: plass og retning for framsida av det flate arket. `rull` dreier arket i eige plan (grader).
- For at speglinga skal gå frå kjelda mot eit mål: `normal = nrm(nrm(kjeldeplass - senter) + nrm(maal - senter))`.
- `storleik`: diameter (rundt ark) eller (breidd langs u, høgd langs v).
- `form=boy(kappa)`: sylindrisk bøy langs u. `kappa` er krumming i 1/m (tal eller funksjon av u). Positiv gjer framsida hol. Radius R er `boy(1/R)`.
- `form=fald([(u, vinkel), ...])`: faldar parallelt med v.
- Eiga form: `form=lambda U, V: (X, Y, Z)` i arket sine koordinatar, Z ut frå framsida.
- `klipp=lambda u, v: ...` gjev True der arket finst. Det som er klipt bort, slepper lyset frå kjelda gjennom.
- Overflater: `MATT` (0,85 diffust), `SATIN` (0,65 i ei lobe med sigma 10°, 0,15 diffust; ANTAKING), `BLANK` (spegel), `MORK`. Eigen: `dict(rd=..., rs=..., sigma=...)`.
- `tone=(1.0, 0.85, 0.55)` fargar lyset, til dømes messing.
- `a.strekk`: kor mykje arket må tøyast. 0 for alt som kan bøyast av eit flatt ark. Over 0,006 kan det ikkje lagast ved å bøye.
- `fresnelspegel(k, senter, normal, f=0.1871, storleik=(0.285, 0.285), spreiing=2.5)`: plata frå overheadprojektoren. `spreiing` 2,5 er rein plate, 8 til 14 er med diffusorark oppå.

## Budsjett

`W, K = watt(t)`: t = 0 er stemning (1,25 W, 2200 K), t = 1 er arbeid (5 W, 3000 K). Alt imellom er overgangen.

- Kjelde som lyser på eit ark: `lm = W * LMW_KJELDE` (100 lm/W).
- Strøk rett ut i rommet: `lm = W * LMW` (80 lm/W).

Alle får same watt. Det gjer at berre fordelinga skil dei.

## Lysgrep, tal og bilete

Eit lysgrep er `g(t) -> (lys, kropp)`. `kropp` er svarte lekamar: `syl(a, c, r)`, `skive(c, n, r)`, `kule(c, r)`.

```python
d = tal(lys, kropp)                      # om lag 1 s med ark
rader = familie(GREP, mappe, px=200)     # GREP = [(namn, g), ...]. Skriv tal.md, tal.csv og brett. px=0 gjev berre tal
R, m = overgang(g, n=7)                  # går overgangen i n steg
par(g, 'fil.png', px=240, ss=1, steg=(0, 0.5, 1))
```

`tal()` gjev mellom anna: `W`, `lm` (lumen ut av lampa), `E_felt` (snitt lux på feltet), `U` (jamnheit: lågaste rute delt på snittet), `nytte`, `E_vegg` (veggsona), `E_ansikt` (loddrett ved auget, utan skjermen), `E_skjerm` og `E_skjerm_maks` (loddrett lux på framsida av skjermen, frå lampa åleine: gjenskin som et kontrasten), `L_lampe` (lysaste del av lampa mot auget, cd/m²), `L_flate` (lysaste romflate), `strekk`.

Lyset på skjermflata blir samanlikna som forholdet til lyset på feltet, så ulike lux-mål kan stillast side om side. Første lysbrett låg på 0,08 til 0,49. Bru og krok frå `Documents/northern-lampe` ligg på om lag 1,2 til 1,3, prisma på 0,02.

`familie()` gjev rader med: `felt`, `jamnheit`, `nytte`, `W350` (watt for 350 lx på feltet), `timar` (per 21700-celle), `vegg`, `ansikt`, `auge`, `auge350` (mot auget ved 350 lx), `s_auge`, `s_felt`, `s_vegg` (stemning), `likskap`, `strekk`.

`overgang()` gjev `topp` (lysaste mellomsteg mot auget delt på lysaste endepunkt, over 1 er blending undervegs), `sprang` (største endring i lysfordeling mellom nabosteg, 0 er glatt), `jamn_auke`, og listene `t`, `auge`, `felt`, `vegg`.

`likskap` er cosinus mellom lysfordelinga i stemning og arbeid. Over 0,9 er lampa ein dimmar, ikkje ein overgang.

## Måla frå kravspesifikasjonen

| Krav | Mål |
| --- | --- |
| F3 arbeidsfelt | 350 lx åleine på feltet |
| F1 blending | inga flate over 3000 cd/m² mot auget, inga kjelde synleg eller spegla i skjermen |
| F5 luminans | under 1500 cd/m² i arbeid, under 500 i stemning |
| F6 vegg | 100 til 150 lx bak skjermen |
| F10 ansikt | 50 til 200 lx, sekundært |
| F2 overgang | éi handling, under 10 s, saumlaust |
| jamnheit | referansen er 0,6 |
| B3 | 7,5 W på leidning er taket |
| F8, F9 | høgst 1,2 kg og 200 cm² fotavtrykk |

## Fart

- Søk med `tal()` og `familie(..., px=0)`. Lag brett med `px=200` først når familien står.
- Køyr éin python-prosess om gongen. Ikkje bruk multiprocessing.
- `n=22` fliser held til søk. Bruk `n=30` eller meir for blanke flater.

## Det modellen ikkje reknar

- Arket skuggar ikkje seg sjølv og lyser ikkje på seg sjølv. Djupe holformer blir for lyse.
- Spegling av arket i dataskjermen er ikkje rekna.
- `SATIN` og 2 % sprut er antakingar, ikkje målingar.
- Rommet er svart med éin vegg og tak. Auget står i 47 cm. Kravet F1 gjeld 25 til 60 cm.
- Kontroll: energien held (85 lm ut av 100 lm inn på matt), spegelbiletet stemmer innanfor 5 %, og fresnelplata samlar lyset 0,74 m framfor seg med kjelda 250 mm unna, slik `research/13` reknar.
