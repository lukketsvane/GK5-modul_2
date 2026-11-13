# form04 «Prisme» · 2026-11-13 · erstattar (c) flak

**Grep.** Overhead-armen frå (c) er beholden. Under han heng ei klar prismeplate (lineær Fresnel, PMMA 3 mm, 60 × 16 cm), 5 cm under ei LED-line i ei renne.
**Éi setning.** Ei klar plate der kvar rille er rekna frå lyslova, slik at lyset fell der du arbeider og ingen annan stad.
**Rekna flate.** Rillevinkelen τ(s) kjem frå tre krav (`optikk()` i motor.py):
1. Lambertsk vifte inn frå LED-lina.
2. Snell ved oversida og ved rilla, med Fresnel-tap per stråle.
3. Fluksbevaring som gjev jamn illuminans på arbeidsflata (kumulativ fluks ∝ tan θ), mellom kantane av sona (−17° til +16°).

Rillene går frå −65° til +65°, og innfallet er aldri over 31°, så ingen stråle vert totalreflektert.

**Gest.** Vipp hovudet (lineholdar + plate) 105°. Vifta går då frå arbeidsflata til veggen. Vippeaksen ligg i tyngdepunktet til hovudet (33 mm under LED-lina), så leddet treng berre friksjon.
**Rekna fridomsgrad.** α. Søkt: LED-aksen (ys, zs), 6 av 20 punkt held alle krav (`sok.json`). Vald: ys 0,22, zs 0,70.

## Tal (`tal.csv`, `skjerm.json`)
| Φ LED | W | E snitt | U0 | mot auga | på skjermen | stemning (25 %) | ansikt 150 lx | vipp | masse | fot | tipp aleine | svikt | batteri |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **433 lm** | **4,3** | 500 lx | 0,69 | 11 cd/m² | **9 lx** (maks 37) | 40 lx på veggen, 100 % | 0,66 kcd/m² i snitt med 79 lm | 105° | 3,11 kg | 720 cm² | 22° | 0,19 mm | 4,5 t |

- **Kontroll:** fluksen integrert over heile kula gjev 0,7388, og η er 0,7388. Optikken lagar altså ikkje lys.
- **Trefjerdedelar mindre lys enn (a) og (b)** for same 500 lx, fordi lyset går dit det trengst. Det er grunnen til at batteri vert realistisk (4,5 t).

## Forkasta på vegen
- Første versjon vippa om LED-lina. Plata hang då som ein pendel (0,22 N·m), gestkrafta vart 5,3 N, og 12 mm fot var ikkje nok. Ein balansert akse løyste det.
- Foten tippa bakover fordi næraste kant var bakkanten. Han går no 4 cm bak søyla, og tjukna er 7 mm, rekna frå stabilitetslova.

## Premissar og feil (ikkje løyste)
- RISS 0,95 (tap i rilleveggane), 1 % strølys og 4° mattering er anslag.
- Rillene er teikna med 5 mm deling; den reelle delinga er 0,5–1 mm.
- Ansiktslyset er **snittluminans**. Ei prismeplate syner striper; toppen er ikkje rekna.
- Lyset er rekna som om hovudet vippar om LED-lina, ikkje om tyngdepunktet 33 mm under. Feilen er liten, men ikkje rekna.
- Stemninga er 25 % av arbeidsfluksen, og sidan arbeidsfluksen er låg, vert stemninga svakare enn i (a) og (b) (40 mot 62–69 lx). Ein høgare stemningsprosent kostar ingenting i effekt.
- Søyle og arm er ikkje rekna for vridning (open U-profil).

## Formkritikk
- Same «skilt på stolpe» som flak, men hovudet er no ei line med ei klar plate under, ikkje ei tung flate. Prosessen syner i overflata: rillene er sjølve lyslova, gjort synleg.
