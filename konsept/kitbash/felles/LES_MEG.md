# Felles verktøy for kitbash-lampene

Fire lamper blir sette saman av delane i byggjesettet (`modell/byggjesett/`), trykte delar (Bambu Lab P1S, 256 × 256 × 256 mm, PLA eller PETG) og kjøpte delar (LED, ballast, kjøleplate). Verktøya her gjer at alle fire blir bygde, kontrollerte, rendra og lysrekna på same måte. Alt er rekna, ikkje målt. Måla på delane frå settet er anslag frå foto.

## Tryggleik

- **P04 (straumforsyninga, 230 V) kan ikkje hentast med `sett()`.** Ho og elektronikken hennar skal aldri brukast. P09 (halogenpæra) er heller ikkje i bruk: ein LED erstattar ho.
- **Fresnelspegelen (P05) og linsene (P06, P07) må aldri stå i sol.** Dei samlar sollyset og kan tenne papir. Skriv det i byggjenotatet til lampa.
- **Trykt PLA mjuknar ved 55 til 60 °C.** LED-ar skal liggje på metall eller ha ein varmeveg, og watten skal stå i `kjopt(..., watt=...)`. `sjekk.varme()` reknar temperaturen.

## Filene

| Fil | Kva ho gjer |
| --- | --- |
| `kit.py` | Hentar delar frå settet (`sett`, `film`), lagar trykte og kjøpte delar (`trykt`, `kjopt`, `led_skive`, `led_stripe`), plasserer dei (`plass`, `T`, `Rx`, `Ry`, `Rz`, `om`), og gjev usikkerheita i måla (`usikker`, `klaring`). Former: `boks`, `sylinder`, `royr`, `hylse`, `plate` (med hol og spor), `vinkel`, `skal`, `kopp`, `dreielekam`, `ekstruder`, `minus`, `pluss`, `snitt`, `fraa_cq` (CadQuery). |
| `sjekk.py` | `kollisjonar`, `avstand`, `masse`, `kontakt`, `velt`, `tippkraft`, `varme`, `utskrift`, `eksporter`, og `rapport` som køyrer alt for fleire stillingar i gesten og skriv `sjekk.json` og `sjekk.md`. |
| `rendre.py`, `rendre_blender.py` | Studiorendrar med innstillingane til byggjesettet. `rendre_blender.py` er ein kopi av `modell/byggjesett/rendre_blender.py` (same materiale, lys, verd, kamera, prøvetal og utdata). Scener: `-samla`, `-sprengt`, `-del`. |
| `bru.py` | Frå lampa (mm) til rommet i lysmotoren (m): `i_rommet(delar, fot, dreiing)`. |
| `studie.py` | Lysstudien i oppsettet til `northern-lampe/form05/gen_d/studie_a.png`: `studie(g, tittel, fil)`. |
| `miljo.py` | Høgst fire trådar og lågaste prioritet. Blir importert av dei andre. |
| `demo/` | Prøvelampa som viser at alt heng saman. Ho er ikkje eit framlegg. |

## Koordinatar

Lampa er i **millimeter, Z opp**. Origo er midt i foten på bordflata (z = 0 er bordet), x mot høgre, y bort frå brukaren (mot veggen). Kvar del frå settet har sitt eige system, skildra i `modell/byggjesett/delar.py`. `python kit.py` skriv ut ankerpunkta (`del.punkt('hovudakse')`) og grensesnittmåla.

Rommet til lysmotoren er i **meter**: x mot høgre, y frå brukaren mot veggen, z opp, og `b(x, y, h)` er eit punkt h meter over bordplata. `bru.i_rommet(delar, fot=(x, y), dreiing=grader)` set origo i lampa i `b(x, y, 0)` og dreier lampa om loddlina (mot klokka sett ovanfrå). `pl.p(punkt_mm)` og `pl.r(retning)` gjev punkt og retning i rommet, og `pl.kropp(delar)` gjev lampa som skuggekropp.

## Minste døme

Legg fila i mappa til lampa di, til dømes `konsept/kitbash/lampe1/lampe.py`.

```python
import os, sys
sys.dont_write_bytecode = True
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', 'felles'))
from kit import *
import kit as K, sjekk, rendre, bru, studie

def samling(t=1.0):
    """Lampa i stillinga t: 0 er stemning, 1 er arbeid."""
    arm = sett('P01', T(0, 0, 4) @ Ry(-90), spreng=(0, 0, 80))          # armen loddrett, profilenden 16 mm over bordet
    b = klaring('P01', 'profil_breidd')['opning']                        # 43 ± 6 mm: opninga tek den største
    s = klaring('P01', 'profil_tjukk')['opning']
    fot = pluss(sylinder(180, 16), hylse(b, s, 40, vegg=4, z0=16))
    led = led_skive(40, watt=5.0, M=om((0, 1, 0), 90 * (1 - t), arm.punkt('hovudakse')) @ T(*arm.punkt('hovudakse')) @ T(-40, 0, -30) @ Rx(180))
    return [trykt('fot', fot, plast='PETG'), arm, led]

def grep(t):
    """Lysgrepet til lysmotoren: g(t) -> (lys, kropp)."""
    ls = bru.motor()
    delar = samling(t)
    pl = bru.i_rommet(delar, fot=(0.42, 0.25))
    W, Kelvin = ls.watt(t)                                               # 1,25 W og 2200 K i stemning, 5 W og 3000 K i arbeid
    led = K.finn(delar, 'led')
    n = led.retning((0, 0, 1))                                           # lysflata er +z på LED-skiva
    p = pkt(led.M, (0, 0, 1.6)) + 1.0 * n                                # 1 mm utanfor flata, elles skuggar kroppen
    return [ls.flate(pl.p(p), pl.r(n), 0.040, W * ls.LMW, Kelvin)], pl.kropp(delar)

if __name__ == '__main__':
    sjekk.rapport(samling, HER, 'lampe1', dytt=lambda d: K.finn(d, 'arm').punkt('hovudakse'))   # sjekk.json, sjekk.md, stl/, lampe1.glb
    rendre.scener(samling(1.0), HER, 'lampe1')                           # scener.json
    rendre.koyr(HER, prove=True)                                         # render/lampe1-samla-prove.png, -sprengt-, -del-
    studie.studie(grep, 'Lampe 1 · kva ho er laga av', os.path.join(HER, 'studie.png'), px=300)
```

`demo/demo.py` er det same med eit ledd, ei kjøleplate, ballast og fleire stillingar.

## Kommandoane

```
python kit.py                                      grensesnittmåla med usikkerheit, og ankerpunkta på kvar del
python demo/demo.py sjekk                          kollisjon, masse, velt, varme, trykk, STL og GLB   (20 s)
python demo/demo.py prove                          tre små prøverendrar                                (20 s)
python demo/demo.py full                           samla i 1600 x 1000                                 (køyr i bakgrunnen)
python demo/demo.py studie 300                     lysstudien som prøve; 560 er full oppløysing
python rendre.py <mappe> [scene ...] [--prove]     rendre scener som alt står i <mappe>/scener.json
```

Blender ligg i `C:/Users/Iver/Documents/verktoy/blender-5.1.2-windows-x64/blender.exe` (miljøvariabelen `KITBASH_BLENDER` byter stien). Éin tung prosess om gongen. Prøv med `prove=True` og `px=300` først.

## Slik brukar du kvart verktøy

**Delar.** `sett('P05', M, berre=('plate',))` hentar underdelar (namna står i `modell/byggjesett/stl/`). `film(breidd, hogd, M)` er eit stykke klipt av arket: prismesida er +z, rillene går langs `riller='breidd'` eller `'hogd'`, og funksjonen seier frå om stykket er større enn det minste arket kan vere (250 × 440 mm, ANTAKING). `trykt(namn, mesh, M, plast='PETG', print_R=Rx(180))` er ein trykt del: `print_R` er dreiinga til slik han ligg på plata. `kjopt(namn, mesh, materiale, masse_g, M, watt=, lyser=)` er ein kjøpt del. `del.spreng = (dx, dy, dz)` er flyttinga i det sprengde biletet. Ei stilling i gesten er ei ny liste: la `samling(t)` byggje henne, og bruk `om(akse, vinkel, punkt)` for ledd.

**Usikre mål.** `klaring('P01', 'profil_breidd')` gjev `opning` (sporet som tek delen om han er størst) og `slark` (kor mykje han sleng om han er minst). Slarken må ei klemskrue, ein kile eller ein mjuk innsats ta opp, eller så måler du delen først. Nesten alle mål er ± 3 til 20 mm.

**Kontroll.** `sjekk.rapport(samling, mappe, namn, stillingar=(0, .25, .5, .75, 1), dytt=..., trykk=..., tillat=[('a', 'b')])`. `dytt` er punktet handa dyttar i (mm). `trykk` gjev eit punkt og ei retning for ei ekstra kraft, til dømes rett ned på ein utkragar. `tillat` er par som skal overlappe (pressa tapp, film i spor). Kravet er at lampa toler 5 N.

**Rendring.** `rendre.scener(delar, mappe, namn, azimut=None, elevasjon=None, storleik=(1600, 1000))` skriv tre scener. `rendre.koyr(mappe, [namn + '-samla'], prove=True)` rendrar. Utan `prove` blir biletet 1600 × 1000 med 48 prøver. Materialmerka er dei i byggjesettet pluss `print` (matt raudbrun), `led` (lyser svakt) og `opal`. Kjøpte delar brukar gjerne `aluminium` eller `stål`.

**Lysstudie.** `studie.studie(g, tittel, fil, px=560, ekstra_arbeid=[...], ekstra_stemning=[...])`. `g(t) -> (lys, kropp)` er eit lysgrep slik `konsept/lysskisse/API.md` skildrar det. Bruk `pl.kropp(delar)` som kropp, så er biletet og tala same rekning. Lyskjelder må stå minst 1 mm utanfor kroppen. Ta ut av kroppen det lysmotoren alt har som strøk: `pl.kropp(delar, utan=('fresnelspegel/plate',))` når `ls.fresnelspegel()` står for plata. Glas, film og delar med `lyser=True` er alltid ute. Tala kjem attende som dict og blir skrivne til `<fil>.json`. `studie.rekn(g)` gjev berre tala (om lag 5 s).

## Kva verktøya går ut frå

- **Måla** er dei i `modell/byggjesett/delar.py` (lesne, ikkje kopierte). Endrar du `DIMS` der og køyrer `python delar.py`, følgjer alt med.
- **Masse.** Tettleik i g/cm³: stål 7,85, aluminium 2,70, glas 2,5, PMMA 1,19, PET 1,38, PLA 1,24, PETG 1,27 (kjent frå kjelde). ANTAKING: plasten i settet 1,05, gummi 1,1, keramikk 2,4, «kopar» 8,96. Tynne delar i settet er skal: armprofilen og hovudhuset er teikna hole (profilen med veggen frå `DIMS`, 1,5 ± 0,5 mm), og kappa på armen, lampesokkelen i hovudet og fatninga til projeksjonslinsa blir rekna som flate × vegg. Trykte delar blir rekna med 1,2 mm vegg og 15 % fyll (ANTAKING). Massen til delane frå settet er usikker (± 35 %, ANTAKING) til dei er vegne: set `vekt_g=` i `sett()`.
- **Armprofilen (P01)** er merkt aluminium i `delar.py`. Sit ein magnet på han, er han stål og tre gonger så tung: `sett('P01', materiale={'profil': 'stål'})`.
- **Velt.** Stiv kropp på stivt bord. Lampa står på det konvekse hylsteret av alt som er innanfor 0,5 mm frå det lågaste punktet. `dytt_N` er det minste vassrette dyttet over 72 retningar. Friksjonen 0,4 er ANTAKING.
- **Varme.** 70 % av watten blir varme, flata gjev frå seg 10 W/m²K og rommet held 25 °C (ANTAKING, same som `konsept/lysskisse/studie.py`). Kjøleflata er den ytre flata til metallet LED-en ligg mot (nærare enn 0,5 mm), og metall som ligg mot det att.
- **Trykk.** Overheng er flater som vender nedover brattare enn 45° og ikkje ligg på plata.
- **Rendring.** Kameraet har retninga og linsa til `projektoren-samla` (asimut −38, elevasjon 22, 50 mm). Avstanden blir rekna ut så heile lampa får plass. Delbanken er som i settet: ortografisk, asimut −35, elevasjon 28, 4 pikslar per mm, gjennomsiktig bakgrunn.
- **Lysstudie.** Rommet, kameraet, den låste eksponeringa, mannekengen og `tal()` er lysmotoren sine. Kravlinene er henta frå `grunnlag/04-kravspesifikasjon.md` og `konsept/tre/val-18-11.md`: 350 lx på feltet ved høgst 7,5 W, jamnheit 0,6, under 3 000 cd/m² mot auget i arbeid og 500 i stemning, 100 til 150 lx bak skjermen, 50 lx på ansiktet.

## Kva verktøya ikkje kan

- **Ingenting er målt.** Måla på delane frå settet er anslag frå foto. Eit spor som er sett etter `klaring()`, passar, men delen kan slenge fleire millimeter.
- **Kollisjon** finn overlapp i volum, ikkje for trong klaring. Bruk `sjekk.avstand(a, b)` for det. Underdelar i same del blir ikkje prøvde mot kvarandre. Skruar, leidningar og LED-drivar er ikkje med om du ikkje teiknar dei.
- **Velt** reknar ikkje svikt, glid i ledd eller at lampa glir før ho veltar (talet `glid_N` står i rapporten). Friksjonsledd og fjører er ikkje modellerte.
- **Varme** er eitt overslag med éin temperatur for heile kjøleflata. Det reknar ikkje varmemotstanden i overgangen eller ein lukka skjerm rundt LED-en.
- **Rendringa** viser form og materiale, ikkje lyset frå lampa. `led` lyser svakt berre for å lese som tend. Prismefilmen er vist som klar plast utan optikk, og fresnelrillene er ei bumpteikning.
- **Lysstudien** har avgrensingane til lysmotoren (`konsept/lysskisse/API.md`): arket skuggar ikkje seg sjølv, spegling av ark i skjermen er ikkje rekna, rommet er svart med éin vegg og tak. Prismefilmen krev `konsept/film/film.py` (sjå `konsept/film/API.md`): `studie()` teiknar alt som er eit lysgrep, men lagar ikkje filmoptikken for deg. Kroppen i lysstudien er matt og einsfarga per materiale: blankt metall speglar ikkje, og glas og film er ikkje med.
- **Sprengt bilete** flyttar delane beint. Det viser ikkje rekkjefølgja i monteringa og teiknar ikkje liner mellom delane.
