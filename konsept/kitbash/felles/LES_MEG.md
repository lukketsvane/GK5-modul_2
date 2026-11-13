# Felles verktøy for kitbash-lampene

Fire lamper blir sette saman av delane i byggjesettet (`modell/byggjesett/`), trykte delar (Bambu Lab P1S, 256 × 256 × 256 mm, PLA eller PETG) og kjøpte delar (LED, ballast, kjøleplate). Verktøya her gjer at alle fire blir bygde, kontrollerte, rendra og lysrekna på same måte. Alt er rekna, ikkje målt. Måla på delane frå settet er anslag frå foto.

## Tryggleik

- **P04 (straumforsyninga, 230 V) kan ikkje hentast med `sett()`.** Ho og elektronikken hennar skal aldri brukast. P09 (halogenpæra) er heller ikkje i bruk: ein LED erstattar ho.
- **Fresnelspegelen (P05) og linsene (P06, P07) må aldri stå i sol.** Dei samlar sollyset og kan tenne papir. Skriv det i byggjenotatet til lampa.
- **Trykt PLA mjuknar ved 55 til 60 °C.** LED-ar skal liggje på metall eller ha ein varmeveg, og watten skal stå i `kjopt(..., watt=...)`. `sjekk.varme()` reknar temperaturen.

## Filene

| Fil | Kva ho gjer |
| --- | --- |
| `kit.py` | Hentar delar frå settet (`sett`, `film`), lagar trykte og kjøpte delar (`trykt`, `kjopt`, `led_skive`, `led_stripe`), plasserer dei (`plass`, `T`, `Rx`, `Ry`, `Rz`, `om`, `retta`, `speglnormal`), og gjev usikkerheita i måla (`usikker`, `klaring`). Former: `boks`, `sylinder`, `royr`, `hylse`, `plate` (med hol og spor), `vinkel`, `skal`, `kopp`, `dreielekam`, `ekstruder`, `minus`, `pluss`, `snitt`, `fraa_cq` (CadQuery 2.8 er installert). |
| `sjekk.py` | `kollisjonar`, `avstand`, `masse`, `kontakt`, `velt`, `tippkraft`, `moment`, `varme`, `utskrift`, `eksporter`, og `rapport` som køyrer alt for fleire stillingar i gesten og skriv `sjekk.json` og `sjekk.md`. `python sjekk.py` prøver kontrollane mot kjende svar. |
| `rendre.py`, `rendre_blender.py` | Studiorendrar med innstillingane til byggjesettet. `rendre_blender.py` er ein kopi av `modell/byggjesett/rendre_blender.py` (same materiale, lys, verd, kamera, prøvetal og utdata). Scener: `-samla`, `-sprengt`, `-del`. |
| `bru.py` | Frå lampa (mm) til rommet i lysmotoren (m): `i_rommet(delar, fot, dreiing)`, og derifrå `pl.p`, `pl.r`, `pl.kropp`, `pl.fresnel`, `pl.film`, `pl.skjerm`, `pl.sjekk`. |
| `studie.py` | Lysstudien i oppsettet til `northern-lampe/form05/gen_d/studie_a.png`: `studie(g, tittel, fil)` og `rekn(g)`. |
| `miljo.py` | Høgst fire trådar og lågaste prioritet. Blir importert av dei andre. |
| `demo/` | Prøvelampa som viser at alt heng saman, og `demo/minste/lampe.py`, det minste dømet under. Ingen av dei er framlegg. |

## Koordinatar og brua

Lampa er i **millimeter, Z opp**. Origo er midt i foten på bordflata (z = 0 er bordet), x mot høgre, y bort frå brukaren (mot veggen). Kvar del frå settet har sitt eige system, skildra i `modell/byggjesett/delar.py`. `python kit.py` skriv ut ankerpunkta (`del.punkt('hovudakse')`) og grensesnittmåla.

Rommet til lysmotoren er i **meter**: x mot høgre, y frå brukaren mot veggen, z opp, og `b(x, y, h)` er eit punkt h meter over bordplata.

```python
pl = bru.i_rommet(delar, fot=(0.42, 0.25), dreiing=0, h=0)   # origo i lampa -> b(0.42, 0.25, h), dreidd om loddlina (mot klokka ovanfrå)
pl.p(punkt_mm)      # punkt i lampa (mm) -> punkt i rommet (m)
pl.r(retning)       # retning i lampa -> einingsvektor i rommet
pl.kropp(delar)     # lampa som skuggekropp i lysmotoren (trekantnett per materiale)
pl.sjekk(delar)     # står foten på bordet og utanfor feltet, går noko gjennom skjermen eller veggen
```

Ei lampe som heng på skjermkanten, har ikkje foten på bordet: vel eit origo sjølv (til dømes midt på skjermkanten) og bruk `h`, til dømes `i_rommet(delar, fot=(0, 0.45), h=0.42)`.

## Minste døme

`demo/minste/lampe.py` er denne fila, køyrt og prøvd (2 min 20 s i alt). Kopier henne til `konsept/kitbash/<lampa di>/` og byt `FELLES` til `os.path.join(HER, '..', 'felles')`.

```python
import os, sys
sys.dont_write_bytecode = True
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', 'felles'))
from kit import *
import kit as K, sjekk, rendre, bru, studie

FOT = (0.42, 0.25)                                    # midt i foten i rommet (m): rett til høgre for arbeidsfeltet

def samling(t=1.0):
    """Lampa i stillinga t: 0 er stemning, 1 er arbeid. Alt i mm, z = 0 er bordet."""
    arm = sett('P01', T(0, 0, 4) @ Ry(-90), spreng=(0, 0, 80))           # armen loddrett, profilenden 16 mm over bordet
    b = klaring('P01', 'profil_breidd')['opning']                        # 43 ± 6 mm: opninga tek den største profilen
    s = klaring('P01', 'profil_tjukk')['opning']
    fot = pluss(sylinder(180, 16), hylse(b, s, 40, vegg=4, z0=16))       # trykt fot med hylse rundt profilen
    topp = arm.grenser()[1][2]                                           # høgste punkt på armen
    plate = kjopt('plate', boks(60, 120, 2, (0, -40, topp + 1)), 'aluminium', 60 * 120 * 2 / 1000 * 2.70, spreng=(0, 0, 130))
    led = led_skive(40, watt=5.0, M=T(0, -70, topp) @ Rx(180), spreng=(0, 0, 100))    # under plata, lysflata ned
    return [trykt('fot', fot, plast='PETG'), arm, plate, led]

def grep(t):
    """Lysgrepet til lysmotoren: g(t) -> (lys, kropp)."""
    ls = bru.motor()
    delar = samling(t)
    pl = bru.i_rommet(delar, fot=FOT)
    W, Kelvin = ls.watt(t)                                               # 1,25 W og 2200 K i stemning, 5 W og 3000 K i arbeid
    led = K.finn(delar, 'led')
    n = led.retning((0, 0, 1))                                           # lysflata er +z på LED-skiva
    p = pkt(led.M, (0, 0, 1.6)) + 1.0 * n                                # 1 mm utanfor flata, elles skuggar kroppen ho
    return [ls.flate(pl.p(p), pl.r(n), 0.040, W * ls.LMW, Kelvin)], pl.kropp(delar)

if __name__ == '__main__':
    sjekk.rapport(samling, HER, 'minste', dytt=lambda d: K.finn(d, 'arm').punkt('hovudakse'))   # sjekk.json, sjekk.md, stl/, minste.glb
    namn = rendre.scener(samling(1.0), HER, 'minste')                    # scener.json: minste-samla, minste-sprengt, minste-del
    rendre.koyr(HER, namn, prove=True)                                   # render/minste-samla-prove.png og dei to andre
    studie.studie(grep, 'Minste døme · armen P01 på trykt fot, LED under ei aluminiumsplate', os.path.join(HER, 'studie.png'), px=200)
```

`demo/demo.py` er det same med eit ledd (plata vippar om tappen), ballast og fem stillingar.

## Kommandoane

Køyr frå `konsept/kitbash/felles/`. Tidene er frå denne maskina.

```
python kit.py                                  grensesnittmåla med usikkerheit, og ankerpunkta på kvar del            2 s
python sjekk.py                                kontrollane mot kjende svar (kollisjon, masse, velt, moment, trykk)     3 s
python demo/demo.py sjekk                      kollisjon, masse, velt, varme, trykk, STL og GLB                       25 s
python demo/demo.py prove                      fire små prøverendrar (samla, sprengt, delbank, stemning)              40 s
python demo/demo.py full                       samla i 1600 x 1000, 48 prøver: køyr i bakgrunnen                       2 min
python demo/demo.py studie 560                 lysstudien i full oppløysing (300 er prøve)                            30 til 60 s
python demo/demo.py sett                       alle delane frå settet og eit filmstykke: massetabell og prøverendring 10 s
python demo/demo.py kryss                      fresnelplata gjennom kit og bru, mot talet til søkjebrettet            10 s
python demo/minste/lampe.py                    det minste dømet, alt på éin gong                                       2 min 20 s
python rendre.py <mappe> [scene ...] [--prove] rendre scener som alt står i <mappe>/scener.json
python rendre.py demo demo-del                 delbanken i full storleik (4 px per mm, gjennomsiktig)                 30 s
```

Blender ligg i `C:/Users/Iver/Documents/verktoy/blender-5.1.2-windows-x64/blender.exe` (miljøvariabelen `KITBASH_BLENDER` byter stien). Éin tung prosess om gongen. Prøv med `prove=True` og `px=300` først.

## Slik brukar du kvart verktøy

**Delar.** `sett('P05', M, berre=('plate',))` hentar underdelar (namna står i `modell/byggjesett/stl/`). `film(breidd, hogd, M)` er eit stykke klipt av arket: prismesida er +z, rillene går langs `riller='breidd'` eller `'hogd'`, og funksjonen seier frå om stykket krev eit ark større enn 250 × 440 mm (det minste arket kan vere, ANTAKING). `trykt(namn, mesh, M, plast='PETG', print_R=Rx(180))` er ein trykt del: `print_R` er dreiinga til slik han ligg på plata. `kjopt(namn, mesh, materiale, masse_g, M, watt=, lyser=)` er ein kjøpt del. `spreng=(dx, dy, dz)` er flyttinga i det sprengde biletet. Ei stilling i gesten er ei ny liste: la `samling(t)` byggje henne, og bruk `om(akse, vinkel, punkt)` for ledd. Det som skal peike ein stad: `T(*pos) @ retta(n)` tek +z i delen til retninga `n`, og `speglnormal(c, kjelde, maal)` gjev retninga ein spegel i `c` må ha.

**Usikre mål.** `klaring('P01', 'profil_breidd')` gjev `opning` (sporet som tek delen om han er størst) og `slark` (kor mykje han sleng om han er minst). Slarken må ei klemskrue, ein kile eller ein mjuk innsats ta opp, eller så måler du delen først. Nesten alle mål er ± 3 til 20 mm.

**Kontroll.** `sjekk.rapport(samling, mappe, namn, stillingar=(0, .25, .5, .75, 1), dytt=..., trykk=..., tillat=[('a', 'b')])`. `dytt` er punktet handa dyttar i (mm). `trykk` gjev eit punkt og ei retning for ei ekstra kraft, til dømes rett ned på ein utkragar. `tillat` er par som skal overlappe (pressa tapp, film i spor). Kravet er at lampa toler 5 N. Rapporten gjev òg massen og dyttet om armprofilen er stål.

**Lamper på skjermen eller under skjermfoten.** `pl.skjerm()` gjev skjermen i rommet som ein del i lampa sitt system, merkt `omgjevnad`. Legg han til lista: `sjekk.kollisjonar(delar + [pl.skjerm()])` viser om lampa går inn i skjermen, og `sjekk.velt(delar + [pl.skjerm()], punkt)` reknar skjerm og lampe som éin kropp på skjermfoten. `sjekk.moment(delar, punkt, akse, dytt=(punkt, retning, N))` gjev massen støtta må bere og momentet om støtteaksen. Omgjevnaden er ikkje med i massen til lampa (F8), i rendringane eller i lysstudien. Skjermen er 4 kg, 5 cm djup og har fotplate 24 × 20 cm (ANTAKING frå søkjebrettet).

**Rendring.** `rendre.scener(delar, mappe, namn, azimut=None, elevasjon=None, storleik=(1600, 1000), sprengt=None)` skriv tre scener. `rendre.koyr(mappe, [namn + '-samla'], prove=True)` rendrar. Utan `prove` blir biletet 1600 × 1000 med 48 prøver. Materialmerka er dei i byggjesettet pluss `print` (matt raudbrun), `led` (lyser svakt) og `opal`. Kjøpte delar brukar gjerne `aluminium` eller `stål`. Ved sida av kvart bilete ligg `<scene>.json` med kvar kvar del hamnar i biletet (pikslar) og om han er `sett`, `print` eller `kjopt`: til merking på oppsummeringsarket. Delbanken har `px_per_mm` i same fil.

**Lysstudie.** `studie.studie(g, tittel, fil, px=560, ekstra_arbeid=[...], ekstra_stemning=[...])`. `g(t) -> (lys, kropp)` er eit lysgrep slik `konsept/lysskisse/API.md` skildrar det. Bruk `pl.kropp(delar)` som kropp, så er biletet og tala same rekning. Lyskjelder må stå minst 1 mm utanfor kroppen. Glas, film og delar med `lyser=True` er aldri med i kroppen. Tala kjem attende som dict og blir skrivne til `<fil>.json`. `studie.rekn(g)` gjev berre tala. Linene under arbeidsbiletet: først `tal()` ved watten lysgrepet sjølv gjev (det biletet viser), så «ved 350 lx», der tala er skalerte til 350 lx på feltet. Krava blir prøvde på dei skalerte tala, slik `konsept/tre/val-18-11.md` og søkjebrettet gjer (nøklane `W350`, `bak350`, `skjerm350`, `ansikt350`, `auge25`, `auge47`, `auge60` er dei same som i `konsept/tre/tre.py`).

**Fresnelplata i lysmotoren.** Plasser plata med `sett('P05', M)`. Spegelsida er +z i delen. Så:

```python
plate = K.finn(delar, 'fresnelspegel')
k = ls.straale(pl.p(diode_mm), pl.p(plate.punkt('spegelflate')), W * ls.LMW_KJELDE, Kelvin, spreiing=40, kutt=50, opning=0.02, bronn=50)
lys = [k, pl.fresnel(plate, k, spreiing=2.5)]       # 2,5 er rein plate, 8 til 14 med diffusorark oppå
return lys, pl.kropp(delar)                         # plata kan stå i kroppen: reflektoren ligg 1 mm framfor spegelflata
```

`demo/demo.py kryss` er eit heilt døme.

**Filmen i lysmotoren.** `pl.film(stykke)` gjev `senter`, `normal` (ut av prismesida), `riller` (retninga rillene går) og `storleik` i rommet. Optikken ligg i `konsept/film/film.py` og `northern-lampe/form05/rute/` (`rute.rute`), skildra i `konsept/film/API.md`. Strøka derifrå går rett inn i `studie()`.

## Massen til delane i settet

Rekna frå dei anslåtte måla (`python demo/demo.py sett`), ± 35 % (ANTAKING) til delane er vegne. Set `vekt_g=` i `sett()` når du har vege ein del.

| Del | Gram | Merknad |
| --- | --- | --- |
| P01 arm | 184 | 425 om profilen er stål. `delar.py` seier aluminium, oppdraget seier stål: prøv med magnet |
| P02 hengsel | 221 | stål, 2 mm |
| P03 hovud | 695 | huset er stål 1,2 mm, lagerskiva er rekna som massiv kopar (ANTAKING) |
| P05 fresnelspegel | 306 | PMMA 1,19 med ramme |
| P06 glaslinse | 29 | glas 2,5 |
| P07 projeksjonslinse | 57 | fatninga som skal, 2,5 mm (ANTAKING) |
| P08 prismeark | 45 | heile arket 306 × 535 × 0,2 mm, PET 1,38 |

## Kontroll av verktøya

- `python sjekk.py`: to boksar 5 mm inn i kvarandre gjev 2 000 mm³, ein stålkloss på 2 000 cm³ veg 15 700 g, dyttet som veltar han er m g 50 / 200 = 38,5 N, ei rund søyle 17,95 mot 17,97 N, momentet om ein akse 150 mm unna 23,1 Nm. Alt stemmer.
- `python demo/demo.py kryss`: fresnelplata plassert med `kit` og sett i rommet med `bru`, same grep som «over-vipp» på søkjebrettet (`modell/byggjesett/kitbash/tal_lys.json`). Søkjebrettet: 1,73 W for 350 lx, jamnheit 0,47, 15,8 lx bak skjermen, 79,0 lx på skjermflata, 227 / 75 / 75 cd/m² mot auget. Her: 1,73 W, 0,48, 15,8 lx, 79,1 lx, 237 / 77 / 75 cd/m². Skilnaden mot auget (4 %) kjem av at reflektoren ligg 1 mm framfor spegelflata. Skorne hjørne på plata endrar ingenting som syner. Med ein stolpe bak skjermen i kroppen fell veggen bak skjermen om lag 5 % (15,5 til 14,7 lx med 22 fliser): kroppen skuggar, og søkjebrettet rekna dette grepet utan kropp. Talet på fliser i plata (16 eller 22) flyttar same tal 2 %.

## Kva verktøya går ut frå

- **Måla** er dei i `modell/byggjesett/delar.py` (lesne, ikkje kopierte). Endrar nokon `DIMS` der, følgjer alt med.
- **Masse.** Tettleik i g/cm³: stål 7,85, aluminium 2,70, glas 2,5, PMMA 1,19, PET 1,38, PLA 1,24, PETG 1,27 (kjent frå kjelde). ANTAKING: plasten i settet 1,05, gummi 1,1, keramikk 2,4, «kopar» 8,96. Tynne delar i settet er skal: armprofilen og hovudhuset er teikna hole (profilen med veggen frå `DIMS`, 1,5 ± 0,5 mm), og kappa på armen, lampesokkelen i hovudet og fatninga til projeksjonslinsa blir rekna som flate × vegg. Trykte delar blir rekna med 1,2 mm vegg og 15 % fyll (ANTAKING).
- **Velt.** Stiv kropp på stivt bord. Lampa står på det konvekse hylsteret av alt som er innanfor 0,5 mm frå det lågaste punktet. `dytt_N` er det minste vassrette dyttet over 72 retningar. Friksjonen 0,4 er ANTAKING.
- **Varme.** 70 % av watten blir varme, flata gjev frå seg 10 W/m²K og rommet held 25 °C (ANTAKING, same som `konsept/lysskisse/studie.py`). Kjøleflata er den ytre flata til metallet LED-en ligg mot (nærare enn 0,5 mm), og metall som ligg mot det att.
- **Trykk.** Overheng er flater som vender nedover brattare enn 45° og ikkje ligg på plata.
- **Rendring.** Kameraet har retninga og linsa til `projektoren-samla` (asimut −38, elevasjon 22, 50 mm). Avstanden blir rekna ut så heile lampa får plass. Delbanken er som i settet: ortografisk, asimut −35, elevasjon 28, 4 pikslar per mm, gjennomsiktig bakgrunn. Fargen på trykte delar er den raudbrune frå `konsept/film/cad/render.py`, senka til (0,07 0,010 0,006) fordi studiolyset til settet gjorde originalverdien rosa.
- **Lysstudie.** Rommet, kameraet, den låste eksponeringa, mannekengen og `tal()` er lysmotoren sine. Krava er henta frå `grunnlag/04-kravspesifikasjon.md` og `konsept/tre/val-18-11.md`: 350 lx på feltet ved høgst 7,5 W, jamnheit 0,6, under 3 000 cd/m² mot auget i arbeid og 500 i stemning, minst 100 lx bak skjermen (over 150 blir merkt), 50 lx på ansiktet.

## Kva verktøya ikkje kan

- **Ingenting er målt.** Måla på delane frå settet er anslag frå foto. Eit spor som er sett etter `klaring()`, passar, men delen kan slenge fleire millimeter.
- **Kollisjon** finn overlapp i volum, ikkje for trong klaring. Bruk `sjekk.avstand(a, b)` for det. Underdelar i same del blir ikkje prøvde mot kvarandre. Skruar, leidningar og LED-drivar er ikkje med om du ikkje teiknar dei.
- **Velt** reknar ikkje svikt, glid i ledd eller at lampa glir før ho veltar (talet `glid_N` står i rapporten). Friksjonsledd og fjører er ikkje modellerte. Om ei klype eller ein skjerm toler momentet frå `sjekk.moment()`, må prøvast.
- **Varme** er eitt overslag med éin temperatur for heile kjøleflata. Det reknar ikkje varmemotstanden i overgangen eller ein lukka skjerm rundt LED-en.
- **Rendringa** viser form og materiale, ikkje lyset frå lampa. `led` lyser svakt berre for å lese som tend. Prismefilmen er vist som klar plast utan optikk, og fresnelrillene er ei bumpteikning.
- **Lysstudien** har avgrensingane til lysmotoren (`konsept/lysskisse/API.md`): arket skuggar ikkje seg sjølv, spegling av ark i skjermen er ikkje rekna, rommet er svart med éin vegg og tak. Lysmotoren prøver ikkje om noko står mellom kjelda og fresnelplata. `studie()` teiknar alt som er eit lysgrep, men lagar ikkje filmoptikken for deg. Kroppen i lysstudien er matt og einsfarga per materiale: blankt metall speglar ikkje, og glas og film er ikkje med. Lampa er liten i biletet (kameraet til lysmotoren viser heile rommet), så kroppen blir grov.
- **Sprengt bilete** flyttar delane beint. Det viser ikkje rekkjefølgja i monteringa og teiknar ikkje liner mellom delane.
