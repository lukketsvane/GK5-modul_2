# Fire design frå skulpturformene, tenkte mot Northern-briefen

19.11.2026. Ingen av dei er teikna enno: både OpenAI (gpt-6.2-astra, gpt-image-2.6-sunburst) og ElevenLabs stod på 0 kreditt. Teikneprompten for kvart design står under, klar til `gpt-image-2.6-sunburst`.

| Design | Skulptur | Handling | Stemning | Arbeid | Møte (sekundært i briefen) |
| --- | --- | --- | --- | --- | --- |
| Hette | 03 | Drei hetta på messingtappen | Skyggen mot veggen: veggen lyser | Skyggen mot skjermsida: lys under skyggen på tastaturet | Skyggen mot deg: dei opplyste innsidene av platene vert ei stor, mjuk kjelde |
| Lykt | 12 | Løft kapselen ut av vogga, eller rull han i vogga | Løfta ut: oppladbar lykt du ber til sofaen | I vogga ved skjermen: lang, lineær kjelde over tastaturet | Rulla mot deg: breitt, mjukt lys |
| Halo | 07 | Vipp skiva | Bak skjermen: veggen rundt skjermen lyser, kontrasten fell | Vippa fram over skjermkanten: lys på tastaturet, skjermen skjermar auget | Kameraet ser ein roleg, lysande vegg bak hovudet |
| Le | 09 | Snu le-veggen | Snudd mot veggen: mjuk vask på veggen | Mot deg: lyset klatrar opp den bøygde flata | Den bøygde flata er ein stor refleks: mjukt ansiktslys |

Felles for alle: lyskjelda er aldri synleg frå augehøgd (gitteret av plater er lameller, eller kjelda sit gøymd i foten), varmt lys, éin matt farge og éin messingdetalj, og alt kan skjerast i slicerman som plater med halvt-i-halvt-spor (Le treng i tillegg eit bøygd ark, som motoren kan skjere).

Svar på briefen punkt for punkt: stemning og komfort (kveld/stemning), låg blending (lameller, gøymd kjelde), samspel med skjerm og kamera (Halo, møte-stillinga), saumlaus overgang (éi handling), enkel og kompakt (Hette 220 mm, Lykt oppladbar og flyttbar), Northern-identitet (skulpturform, matt farge, messing), ansiktslys utan blending (Hette, Lykt, Le).

## Teikning

Stil (felles): Andreas Töpfer, «Speculative Drawing». Svart tusj på kvitt papir, skjelvande fri strek, nesten utan skravur, figurar spreidde med mykje luft, gjenstand som glir over i omgrep, handskrivne merknader i STORE BOKSTAVAR med A–E, piler og leiestrekar. Kvadratisk side.

- **Hette.** A skulptur 03 · B forma skoren i plater som går i kvarandre · C snitt: kjelda høgt inne, eit auge med stipla siktliner som stoppar i platene, lyset går berre rett ned · D ei hand dreier hetta på tappen, tre piler til tastatur, ansikt og vegg. Tekst: HETTE, SKULPTUR 03, PLATER I KVARANDRE, AUGA SER ALDRI LYSET, DREI HETTA, ARBEID, MØTE, KVELD.
- **Lykt.** A skulptur 12 · B kapselen lettar frå foten og vert eit ribbeskjelett med lysløkker inni · C foten som vogge med to kontaktpunkt · D kapselen i vogga ved skjermen, eit jamt lysband over tastaturet · E ei hand ber lykta til ein lenestol · sirkelpil for rulling. Tekst: LYKT, SKULPTUR 12, RIBBER, VOGGA LADAR, ARBEID, LØFT UT, KVELD, RULL.
- **Halo.** A skulptur 07 · B skiva vert eit flatt gitter på ei tynn line · C sidesnitt: skjerm på bordet, skiva bak han, lyset sprer seg på veggen som ein glorie · D skiva vippa fram over skjermkanten, lys på tastaturet, auget blokkert av skjermen · E eit kamera ser eit hovud mot ein roleg lysande vegg. Tekst: HALO, SKULPTUR 07, BAK SKJERMEN, VEGGEN LYSER, VIPP FRAM, ARBEID, KAMERAET SER RO.
- **Le.** A skulptur 09 · B ryggen flassar av som eitt bøygd ark med små ribber bak · C snitt: lyslinja gøymd i tunnelen i foten, lyset klatrar opp kurva i mjuke bølgjer · D eit ansikt mjukt lyst av den store kurva · E lampa snudd mot veggen, mjuk vask og ei lita måneløkke. Tekst: LE, SKULPTUR 09, BØYGD ARK, LYSET KLATRAR, MJUKT ANSIKT, SNU, KVELD.

## Køyring når det er kreditt

OpenAI (føretrekt, med Töpfer-referansane i OpenAI Files):

```
python kjelde/astra_nord.py tenk --brief "context/2 Endelig designbrief Northern.md" --ramme kjelde/ramme.md --former skulptur-01-12.png --forsok slicerman-tre-forsok.png
python kjelde/astra_nord.py teikn 1-4 -j 2
```

Steg 1 lèt Astra 6.2 (max) lage sine eigne fire design; designa over er mitt framlegg om Astra ikkje kan køyre.
