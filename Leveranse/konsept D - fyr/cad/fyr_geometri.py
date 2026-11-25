# -*- coding: utf-8 -*-
"""FYR · parametrisk geometri v4 (CadQuery, B-rep). Alle mål i mm.

Koordinatsystem: z = 0 er bordplata, lampeaksen er z-aksen. Asimut 0 = +X = vindauget (seks spalter),
vend mot brukaren. Bak = 180°. Asimut er positiv mot klokka sett ovanfrå.

Hylsa (messingkragen) blir dreidd med klokka sett ovanfrå når ho går frå open (θ = 0°) mot av (θ = 90°).
Ein detalj som sit på asimut φ i hylsa sitt eige system, står då på φ − θ i chassiset sitt system.

Delar (del-ID):
  01 fot         synleg, oksebloddraud (serie: aluminium dreia og pulverlakkert)
  03 chassis     berande kjerne: tappen hylsa går på, klikk, tre brytarar, sokkel for lysmodulen
  04 mantel      synleg aluminiumsrøyr 90 x 2 med seks spalter
  05 hylse       synleg messingrøyr (serie 0,8 mm valsa plate, prototype 1,6 mm prent)
  05b hylsefot   lagerring i botnen av hylsa: klikkspor, kamspor for brytarane, stoppskruar
  06 lysstav     aluminiumsflatstål 15 x 2 med LED-stripe og toppemitter (lysmodulen)
  07 lysrist     kvit kjerne: lamellar framme, kvitt skjold bak, refleksjonskopp og sete for loket
  08 lok         opal PMMA-skive
  10 glidering   POM-ring øvst i mantelen, styrer hylsa
  11 o-ring      silikon 85 x 3 under foten

Alle synlege røyr er «røyrlaser-reine»: konstant vegg og berre radielle gjennomskjeringar.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

import cadquery as cq

DEG = math.pi / 180.0
REVISJON = "v4"     # felles revisjon for kontroll, teikningar, rettleiing og dokument
DATO = "2026-11-25"


# ============================================================================ parametrar
@dataclass(frozen=True)
class FyrParams:
    variant: str = "serie"           # "serie" (produksjonsgeometri) eller "prototype" (P1S-prent)
    n_deling: int = 32               # 360/32 = 11,25° modul: spaltedeling = ein klikk

    # ---- 01 fot -------------------------------------------------------------
    fot_d: float = 99.0
    fot_h: float = 14.0
    fot_loft: float = 1.0            # O-ringen lyfter foten 1 mm (skuggefuge mot bordet)
    fot_fas: float = 1.0
    spor_djup: float = 6.0           # ringspor som tek imot mantelen
    spor_klaring_inn: float = 0.20
    spor_klaring_ut: float = 0.25
    fot_lomme_r: float = 30.0        # kabellomme ovanfrå, under chassiset
    fot_lomme_z: float = 4.0         # golv i lomma, i høgd med botnen av kabelholet
    kabel_d: float = 4.2             # gjennomføring for fast kabel, bak
    kabel_z: float = 6.2
    oring_id: float = 85.0           # 85 x 3 silikon, strekt 2,9 % inn på spordiameteren 87,5 (fell ikkje av)
    oring_strekk_r: float = 1.25
    oring_snor: float = 3.0
    oring_spor_b: float = 3.1
    oring_spor_djup: float = 2.0
    skrue_r: float = 36.0            # 3 x M3 nedanfrå inn i innsatsar i chassiset
    skrue_vinklar: tuple = (0.0, 120.0, 240.0)
    # bajonett: usymmetriske knastar (mantelen går berre på éin veg, spaltene mot rista), låser med klokka;
    # tre bitar silikonsnor i golvet av sporet trykkjer mantelen opp mot knastane, og ein nabb krev
    # «trykk ned og vri» for å låse opp (B22-prinsippet)
    baj_vinklar: tuple = (60.0, 180.0, 290.0)
    # knasten er ein radiell sylinderstift Ø2,5 (serie: ISO 8734 Ø2,5 x 14 m6 pressa inn frå lomma i hol H7;
    # prototype: prenta tapp med same mål). Breidd og høgd er difor båe stiftdiameteren; L-sporet blir rekna frå dei
    baj_knast_b: float = 2.5
    baj_knast_h: float = 2.5
    baj_knast_ut: float = 1.25
    baj_knast_z: float = 2.0         # over underkant mantel
    baj_vri: float = 14.0
    baj_spel: float = 0.6            # aksialt spel i L-sporet: snora løfter mantelen 0,6 til underkanten møter knasten
    baj_nabb_h: float = 0.55         # nabb på underkanten av sporet: knasten kjem forbi berre når mantelen er trykt ned
    snor_vinklar: tuple = (0.0, 120.0, 240.0)
    snor_d: float = 2.0
    snor_l: float = 10.0
    snor_spor_djup: float = 1.0
    # strekkavlastning: kabelen (Ø4) kjem inn langs -X, går under P1, over P2 og under P3 og opp gjennom holet i
    # chassisflensen på (kabel_ut_x, 0). Glipa mellom stolpane er 4,2 (kabel 4,0); kabelen blir bøygd om lag
    # 57°, 75° og 55° rundt P1, P2 og P3 (til saman ca 185° omslyng, rekna med tangentar). Kappa sluttar etter P3.
    # Serie: stift ISO 8734 Ø3 x 12 pressa opp gjennom golvet, flukt med botnen (z 1) -> topp z 13, 2 mm under
    # chassisflensen (kabelen Ø4 kan ikkje smette over). Prototypen prentar stolpane med same mål.
    stolpe_pos: tuple = ((-26.0, 2.3), (-20.5, -2.3), (-15.0, 2.3))
    stolpe_topp: float = 13.0
    kabel_ut_x: float = -10.5

    # ---- 04 mantel ----------------------------------------------------------
    mantel_d: float = 90.0
    mantel_t: float = 2.0
    mantel_synleg_h: float = 257.0
    n_spalter: int = 6
    spalte_b: float = 3.4            # skjeremål før pulverlakk (ferdig 3,2)
    spalte_l: float = 167.0
    spalte_topp: float = 12.0

    # ---- 10 glidering -------------------------------------------------------
    glide_t: float = 1.0
    glide_h: float = 6.0
    glide_under_kant: float = 1.0
    glide_klaring: float = 0.15

    # ---- 05 hylse -----------------------------------------------------------
    hylse_t: float = 0.8             # messing 0,8 (serie); prototype 1,6
    krage_h: float = 27.0
    port_margin: float = 3.9         # grader utanfor senter av ytste spalte
    port_under: float = 1.0
    krone_b: float = 4.0
    krone_topp: float = 6.0
    krone_under: float = 0.0         # kronespaltene startar ved mantelkanten, over gliderringen (rasp ikkje POM-en)
    krone_stasjonar: tuple = (90.0, 180.0, 270.0)
    # stumpskøyten i messingrøyret (serie, hylsesystem): midt mellom kronegruppene på 180 og 270 (10 mm steg på
    # kvar side, 8 mm til stoppskruholet på 240). Sett frå chassiset vandrar han 225 -> 135, alltid på baksida.
    hylse_saum: float = 225.0
    snepp_vinklar: tuple = (45.0, 165.0, 285.0)

    # ---- 05b hylsefot -------------------------------------------------------
    toppdekk_z1: float = 76.0        # = underkant hylsefot (ber mot toppdekket)
    fotring_h: float = 14.0          # hylsefoten er ein ring inne i røyret, z 76..90
    hylse_luft: float = 0.3          # røyret står 0,3 over toppdekket (berre fotringen ber)
    bor_r: float = 36.2
    vandring: float = 90.0
    # tre stoppskruar ISO 7380 M3x5 gjennom røyret inn i fotringen: låser røyret, er endestopp 0°/90°
    # og held hylsa nede (spissen går i eit spor i tappen på chassiset)
    stopp_vinklar: tuple = (0.0, 120.0, 240.0)   # hylsesystem
    # hovudholet Ø6 i messingen: 81 - 3 - 76,3 = 1,7 mm steg ned til underkanten av røyret (laserskjering og
    # valsing krev minst 2 x t = 1,6). Spor, tungeslisse og klikksone ligg like mykje høgare (steg 1,15 mellom dei).
    stopp_z: float = 81.0
    stopp_hovud_d: float = 5.7
    stopp_hovud_h: float = 1.65
    stopp_l: float = 5.0
    stopp_kjerne_d: float = 2.5      # kjernehol for gjengeformande M3 (prent og POM); skaftet er teikna på kjernediameter
    stopp_spor_h: float = 3.6        # sporhøgd i tappen: M3 + 0,6 -> ± 0,3 (SLS PA12 / FDM-toleranse); steg 1,0 til tungeslissa
    stopp_spor_botn: float = 34.1
    klikk_z0: float = 84.4
    klikk_djup: float = 1.15         # 90° V, opning 2,3: kula R1 går heilt ned på flankane (ikkje på kantane)
    # Brytarar Omron D2F (kontaktpunkt for armen: asimut i chassis, terskel θ der utsparinga har full djupn).
    # Tre parallelle høgsidevegar (ingen kontakt ber straum utanfor sitt område):
    #   SW1 D2F-01L3 gull : +5V -> R1 -> TOPP+   lukka 0..ca 84°  (svak glød 78,75°)
    #   SW3 D2F-01L3 gull : +5V -> R3 -> TOPP+   lukka 0..ca 73°  (full glød 67,5° og opne stillingar)
    #   SW2 D2F-L3  sølv  : +5V -> SIDE+         lukka 0..ca 62°  (sidelys når minst éi spalte er open)
    # Rampene (20°, 6,2° boge) ligg mellom klikkstillingane. Ingen utsparing passerer ein annan brytar.
    sw: tuple = ((235.0, 87.0), (125.0, 65.0), (345.0, 76.0))   # SW1, SW2, SW3
    sw_namn: tuple = ("SW1 D2F-01L3 gull (glød)", "SW2 D2F-L3 sølv (sidelys)", "SW3 D2F-01L3 gull (full glød)")
    sw_r: float = 38.0
    kam_r0: float = 36.0
    kam_r1: float = 40.0
    kam_djup: float = 1.8            # med justerbar brytar (± 1,2 mm spor): OP - 0,6 på flata, OP + 1,2 i utsparinga
    kam_rampe: float = 6.2           # grader (ca 24° rampe: 1,8 djup over 4,1 mm boge på r 38); rampe i båe endar av utsparinga
    sw_hol_z: float = 68.1           # holsenter D2F (OP 8,5 over holsenter -> armen på OP - 0,6 når fotringen står på 76)
    sw_just: float = 1.2             # justering ± (OP-toleransen til D2F er ± 1,2)

    # ---- 03 chassis ---------------------------------------------------------
    chassis_flens_t: float = 3.0
    chassis_r: float = 42.5
    soyle_vinklar: tuple = (60.0, 180.0, 300.0)
    dekk_z: float = 40.0
    dekk_t: float = 2.5
    toppdekk_t: float = 6.0
    mantel_styr_klaring: float = 0.15
    lager_klaring: float = 0.20
    tapp_ri: float = 33.0            # tappen (journal) r 33..36
    tapp_topp: float = 89.5          # 0,5 under toppen av fotringen (z 90); tungene 4,5 høge (z 85..89,5)
    tunge_vinklar: tuple = (60.0, 172.5, 285.0)   # tre klikktunger (112,5° og 225° er heile klikk): ringen står sentrert
    tunge_l: float = 12.0
    tunge_t: float = 1.8
    tunge_kul: float = 0.35          # kula står 0,35 inn i boret til fotringen
    tunge_slisse: float = 1.2        # spalte under tunga (prentbar, sveisar ikkje fast)
    tunge_ende_slisse: float = 1.6   # grader, spalte ved den frie enden
    knusribber_n: int = 6            # knusribber på kanten av toppdekket: mantelen sit utan slark
    innsats_hol_d: float = 4.0
    innsats_l: float = 5.7
    nokkel_r: float = 18.0           # nøkkeltapp på lysrista (asimut 0) og hol i navet på toppdekket
    nokkel_d: float = 5.0
    nokkel_z0: float = 57.0          # tappen går inn i holet 19 mm før modulen sit, før pluggen når kontakten
    sentrering_r: float = 29.85      # bogetapp under chassisflensen inn i kabellomma (sentrerer chassiset på foten)

    # ---- 06 lysstav (lysmodulen) -------------------------------------------
    stav_b: float = 15.0
    stav_t: float = 2.0
    stav_z0: float = 60.0            # nedre ende kviler på golvet i stavsporet i mastfoten, over lomma for pluggkroppen
    stav_z1: float = 253.0
    stripe_b: float = 8.0
    stripe_t: float = 1.6
    stripe_z0: float = 92.0
    stripe_z1: float = 250.0         # 158 mm, 7 W/m BTF FCOB 8 mm RA90
    mastfot_z0: float = 44.4         # kviler på mutteren til TRS-kontakten (topp 44,4); pluggen i bøssinga styrer sideleis
    mastfot_z1: float = 68.0         # 2 mm under toppdekket (z 70)
    mastfot_b: float = 8.0           # x: pluggkroppen Ø6 får 0,95 mm vegg; går gjennom toppdekket i ein gjennomgang + 0,3
    mastfot_l: float = 17.0          # y
    mastfot_lomme_klaring: float = 0.1   # diametral klaring for pluggkroppen (limt); prototype 0,3
    mastfot_kanal: float = 1.2       # leidningskanal bak staven (fire leiarar AWG 28: raud, blå, 2 x svart, ned til loddeøyra)
    trs_l: float = 14.0              # 3,5 mm TRS-plugg under mastfoten
    trs_kropp_d: float = 6.0         # loddekroppen til pluggen (utan skal) står i lomma, z 44,4 .. 58,4
    trs_kropp_l: float = 14.0
    # Rista er limt til staven (2K-epoksy på baksida og sidene av staven i klypa): ho kviler på toppen av staven,
    # sporet hindrar vriing, og limet held når modulen blir løfta i skjørtet. Lysmodulen er ei limt eining.
    # (Ein tverrskrue fekk ikkje plass: over stripa står taket i vegen, under stripa når ikkje skrujarnet fram forbi
    # den nedste lamellen.)
    leidning_b: float = 1.2          # leidningsgjennomgangar i golvet på rista (framfor staven og bak klypa)
    topp_n: int = 4                  # toppemitter: 4 x 25 mm stripe, tangentielt på kvadrat r 22
    topp_l: float = 25.0
    topp_r: float = 22.0

    # ---- 07 lysrist (PH-logikk: direkte lys berre ut under 37° ned) ----------
    rist_r_inn: float = 10.0
    rist_r_ut: float = 32.0
    rist_helling: float = 55.0       # grader under horisontalen, ned og ut
    rist_deling: float = 16.0        # tan d = tan b - (p - t/cos b)/(r_ut - r_inn) -> d = 37,4°
    rist_t: float = 0.8
    rist_vegg_t: float = 0.8
    rist_vegg_vinkel: float = 45.0   # sideveggane endar på r_ut ved ±45° (alle seks spaltene ser lamellar)
    rist_z0: float = 84.0            # golv
    golv_t: float = 1.2
    skjold_r: float = 31.5           # skjold bak (ryggrad frå golv til skjørt); 0,5 mm luft til tappen (r 33)
    skjold_t: float = 1.0
    topp_berar_z: float = 255.0      # berar for toppemitteren
    skjort_z0: float = 255.0         # skjørtet skjermar toppemitteren frå kronespaltene
    skjort_t: float = 1.2
    sete_t: float = 1.6

    # ---- 08 lok -------------------------------------------------------------
    lok_t: float = 3.0
    lok_under_krage: float = 18.0
    lok_klaring_hylse: float = 0.4   # randring til innsida av hylsa

    # ================================================================== avleidde mål
    @property
    def deling(self) -> float:
        return 360.0 / self.n_deling

    @property
    def z_fot_0(self) -> float:
        return self.fot_loft

    @property
    def z_fot_1(self) -> float:
        return self.fot_loft + self.fot_h

    @property
    def r_mo(self) -> float:
        return self.mantel_d / 2.0

    @property
    def r_mi(self) -> float:
        return self.mantel_d / 2.0 - self.mantel_t

    @property
    def z_mantel_0(self) -> float:
        return self.z_fot_1 - self.spor_djup

    @property
    def z_mantel_1(self) -> float:
        return self.z_fot_1 + self.mantel_synleg_h

    @property
    def z_spalte_1(self) -> float:
        return self.z_mantel_1 - self.spalte_topp

    @property
    def z_spalte_0(self) -> float:
        return self.z_spalte_1 - self.spalte_l

    @property
    def vindauge_vinklar(self) -> list:
        n = self.n_spalter
        return [(i - (n - 1) / 2.0) * self.deling for i in range(n)]

    @property
    def r_glide_i(self) -> float:
        return self.r_mi - self.glide_t

    @property
    def z_glide_1(self) -> float:
        return self.z_mantel_1 - self.glide_under_kant

    @property
    def z_glide_0(self) -> float:
        return self.z_glide_1 - self.glide_h

    @property
    def r_ho(self) -> float:
        return self.r_glide_i - self.glide_klaring

    @property
    def r_hi(self) -> float:
        return self.r_ho - self.hylse_t

    @property
    def z_hylse_0(self) -> float:
        return self.toppdekk_z1 + self.hylse_luft

    @property
    def z_fotring_1(self) -> float:
        return self.toppdekk_z1 + self.fotring_h

    @property
    def r_stopp_sete(self) -> float:
        """Radius der skruehovudet ligg an (hovudet 0,3 under ytterflata av røyret)."""
        return self.r_ho - 0.3 - self.stopp_hovud_h

    @property
    def z_hylse_1(self) -> float:
        return self.z_mantel_1 + self.krage_h

    @property
    def port_halv(self) -> float:
        return (self.n_spalter - 1) / 2.0 * self.deling + self.port_margin

    @property
    def z_port_0(self) -> float:
        return self.z_spalte_0 - self.port_under

    @property
    def z_port_1(self) -> float:
        return self.z_spalte_1 + self.port_under + 1.0

    @property
    def z_toppdekk_0(self) -> float:
        return self.toppdekk_z1 - self.toppdekk_t

    @property
    def tapp_ro(self) -> float:
        return self.bor_r - self.lager_klaring

    @property
    def z_lok_1(self) -> float:
        return self.z_hylse_1 - self.lok_under_krage

    @property
    def z_lok_0(self) -> float:
        return self.z_lok_1 - self.lok_t

    @property
    def r_rand_ut(self) -> float:
        return self.r_hi - self.lok_klaring_hylse

    @property
    def r_lok(self) -> float:
        return self.r_rand_ut - self.skjort_t - 0.15

    @property
    def rist_tv(self) -> float:
        return self.rist_t / math.cos(self.rist_helling * DEG)

    @property
    def rist_avskjering(self) -> float:
        """Kor mange grader under horisontalen det bratteste direkte strålen kan gå ut (2D-vilkåret)."""
        tb = math.tan(self.rist_helling * DEG)
        g = (self.rist_deling - self.rist_tv) / (self.rist_r_ut - self.rist_r_inn)
        return math.degrees(math.atan(tb - g))

    @property
    def tak_under_z(self) -> float:
        """Taket: undersida går gjennom (r 4,8, stripetopp + 0,5)."""
        return self.stripe_z1 + 0.5

    def tak_topp(self, r: float) -> float:
        return self.tak_under_z - (r - 4.8) * math.tan(self.rist_helling * DEG) + self.rist_tv

    @property
    def lamell_tuppar(self) -> list:
        """Z for oversida av ytterkanten (r_ut) til kvar lamell, nedanfrå; taket er den øvste."""
        z_tak = self.tak_topp(self.rist_r_ut)
        ut = []
        z = z_tak - self.rist_deling
        while z > self.rist_z0 + self.golv_t - 1.0:
            ut.append(z)
            z -= self.rist_deling
        return sorted(ut)

    @property
    def toppdekk_r(self) -> float:
        return self.r_mi - self.mantel_styr_klaring

    @property
    def klikk_vinklar(self) -> list:
        """Asimut (chassis) for senteret av klikk-kula på kvar tunge; spora i fotringen ligg på vinkel + k * 11,25."""
        return [a - self.tunge_ende_slisse - 1.0 for a in self.tunge_vinklar]

    @staticmethod
    def prototype(**kw) -> "FyrParams":
        """P1S-prent: tjukkare hylse (1,6 mm PLA), og større gangklaringar fordi FDM gjev ytre mål
        +0,05..0,15 og hol -0,1..-0,2. Elles same geometri som serien."""
        base = dict(variant="prototype", hylse_t=1.6, glide_klaring=0.45, lager_klaring=0.30,
                    mantel_styr_klaring=0.30, spor_klaring_inn=0.30, spor_klaring_ut=0.35, hylse_luft=0.0,
                    mastfot_lomme_klaring=0.3)
        base.update(kw)
        return FyrParams(**base)


# ============================================================================ hjelparar
def ring(r_o: float, r_i: float, z0: float, z1: float) -> cq.Workplane:
    wp = cq.Workplane("XY").workplane(offset=z0).circle(r_o)
    if r_i > 0:
        wp = wp.circle(r_i)
    return wp.extrude(z1 - z0)


def syl(r: float, z0: float, z1: float) -> cq.Workplane:
    return ring(r, 0.0, z0, z1)


def syl_xy(x: float, y: float, r: float, z0: float, z1: float) -> cq.Workplane:
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def polar(r: float, a_deg: float) -> tuple:
    return (r * math.cos(a_deg * DEG), r * math.sin(a_deg * DEG))


def kile(th0: float, th1: float, z0: float, z1: float, R: float = 200.0) -> cq.Workplane:
    """Kileforma kropp frå aksen ut til R mellom to asimutar (grader). Spenn under 180°."""
    span = th1 - th0
    n = max(2, int(abs(span) / 7.5) + 1)
    pts = [(0.0, 0.0)]
    for i in range(n + 1):
        a = (th0 + span * i / n) * DEG
        pts.append((R * math.cos(a), R * math.sin(a)))
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def sektor(r_i: float, r_o: float, th0: float, th1: float, z0: float, z1: float) -> cq.Workplane:
    """Ringsektor med radielle sidekantar. Spenn over 180° blir delt."""
    span = th1 - th0
    if span > 170.0:
        # del i to med 1° overlapp, så skøyten forsvinn heilt i unionen (ingen nesten-samanfallande flater)
        mid = th0 + span / 2.0
        return sektor(r_i, r_o, th0, mid + 0.5, z0, z1).union(sektor(r_i, r_o, mid - 0.5, th1, z0, z1)).clean()
    return ring(r_o, r_i, z0, z1).intersect(kile(th0, th1, z0, z1, R=r_o * 2.0 + 10.0))


def radial_spalte(theta: float, z0: float, z1: float, breidd: float, r_inn: float, r_ut: float) -> cq.Workplane:
    """Ståande stadionspalte med parallelle sider langs radien (slik ein røyrlaser skjer)."""
    s = (
        cq.Workplane("YZ")
        .workplane(offset=r_inn)
        .center(0.0, (z0 + z1) / 2.0)
        .slot2D(z1 - z0, breidd, 90)
        .extrude(r_ut - r_inn)
    )
    return s.rotate((0, 0, 0), (0, 0, 1), theta)


def radial_bor(theta: float, z: float, d: float, r_inn: float, r_ut: float) -> cq.Workplane:
    """Radielt hol (sylinder langs radien)."""
    s = cq.Workplane("YZ").workplane(offset=r_inn).center(0.0, z).circle(d / 2.0).extrude(r_ut - r_inn)
    return s.rotate((0, 0, 0), (0, 0, 1), theta)


def dreidd(pts, th0: float = 0.0, th1: float = 360.0) -> cq.Workplane:
    """Dreier eit (r, z)-profil om z-aksen frå asimut th0 til th1 (mot klokka)."""
    span = th1 - th0
    s = cq.Workplane("XZ").polyline(pts).close().revolve(span, (0, 0, 0), (0, 1, 0))
    if span < 359.999:
        c = s.val().Center()
        if math.atan2(c.y, c.x) < 0:
            s = s.mirror("XZ")
    if th0:
        s = s.rotate((0, 0, 0), (0, 0, 1), th0)
    return s


def boks(x0, x1, y0, y1, z0, z1) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center((x0 + x1) / 2.0, (y0 + y1) / 2.0)
        .rect(x1 - x0, y1 - y0)
        .extrude(z1 - z0)
    )


def roter(s: cq.Workplane, theta: float) -> cq.Workplane:
    return s.rotate((0, 0, 0), (0, 0, 1), theta) if theta else s


def radial_rekt(a_deg: float, r0: float, r1: float, z0: float, z1: float) -> cq.Wire:
    c, s = math.cos(a_deg * DEG), math.sin(a_deg * DEG)
    pts = [cq.Vector(r0 * c, r0 * s, z0), cq.Vector(r1 * c, r1 * s, z0),
           cq.Vector(r1 * c, r1 * s, z1), cq.Vector(r0 * c, r0 * s, z1)]
    return cq.Wire.makePolygon(pts, close=True)


def rampe(r0: float, r1: float, a0: float, a1: float, z_lo: float, z_a: float, z_b: float) -> cq.Workplane:
    """Kile i ein bogesektor: høgd z_lo..z_a ved asimut a0, z_lo..z_b ved a1 (linjal-loft)."""
    w0 = radial_rekt(a0, r0, r1, z_lo, z_a)
    w1 = radial_rekt(a1, r0, r1, z_lo, z_b)
    return cq.Workplane("XY").add(cq.Solid.makeLoft([w0, w1], True))


def v_spor(theta: float, r_flate: float, djup: float, opning: float, z0: float, z1: float, inn: bool = False) -> cq.Workplane:
    """Loddrett V-spor (90°) i ei sylinderflate. inn=False: sporet går utover (i eit bor)."""
    sgn = 1.0 if not inn else -1.0
    pts = [(r_flate - sgn * 0.3, -opning / 2.0 - 0.3), (r_flate + sgn * djup, 0.0), (r_flate - sgn * 0.3, opning / 2.0 + 0.3)]
    s = cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)
    return roter(s, theta)


# ============================================================================ 01 fot
def fot(p: FyrParams) -> cq.Workplane:
    R = p.fot_d / 2.0
    z0, z1 = p.z_fot_0, p.z_fot_1
    k = dreidd([(0, z0), (R - 0.5, z0), (R, z0 + 0.5), (R, z1 - p.fot_fas), (R - p.fot_fas, z1), (0, z1)])
    r_a = p.r_mi - p.spor_klaring_inn
    r_b = p.r_mo + p.spor_klaring_ut
    k = k.cut(ring(r_b, r_a, p.z_mantel_0, z1 + 1))
    k = k.cut(dreidd([(r_b - 0.01, z1 - 0.6), (r_b + 0.6, z1 + 0.01), (r_b - 0.01, z1 + 0.01)]))
    # bajonettknastar på innerveggen i sporet: radielle sylinderstift Ø2,5 (serie: ISO 8734 Ø2,5 x 14 pressa inn
    # frå lomma; prototype: prenta tapp med same mål)
    zk0 = p.z_mantel_0 + p.baj_knast_z
    zc = zk0 + p.baj_knast_b / 2.0
    for th in p.baj_vinklar:
        k = k.union(radial_bor(th, zc, p.baj_knast_b, r_a - 0.3, r_a + p.baj_knast_ut + p.spor_klaring_inn))
    # kabellomme ovanfrå (under chassisflensen)
    k = k.cut(syl(p.fot_lomme_r, p.fot_lomme_z, z1 + 1))
    # strekkavlastning: tre stolpar Ø3 i lomma (kabelen går i sikk-sakk mellom dei); serie: innpressa stift ISO 8734
    for (x, y) in p.stolpe_pos:
        k = k.union(syl_xy(x, y, 1.5, p.fot_lomme_z - 0.01, p.stolpe_topp))     # frå golvet i lomma til stifttoppen
    # kabelgjennomføring bak (radiell, Ø4,2) med 0,8 mm fas ytst
    k = k.cut(radial_bor(180.0, p.kabel_z, p.kabel_d, p.fot_lomme_r - 2.0, R + 1.0))
    fas = (cq.Workplane("YZ").workplane(offset=R - 0.8).center(0.0, p.kabel_z).circle(p.kabel_d / 2.0)
           .workplane(offset=0.81).circle(p.kabel_d / 2.0 + 0.8).loft()).rotate((0, 0, 0), (0, 0, 1), 180.0)
    k = k.cut(fas)
    # lommer for silikonsnor i golvet av mantelsporet (forspenning av bajonetten), vekk frå knastane og kabelen
    r_s = (p.r_mi + p.r_mo) / 2.0
    for a in p.snor_vinklar:
        da = math.degrees((p.snor_l + 2.0) / 2.0 / r_s)
        k = k.cut(sektor(r_s - (p.snor_d + 0.2) / 2.0, r_s + (p.snor_d + 0.2) / 2.0, a - da, a + da,
                         p.z_mantel_0 - p.snor_spor_djup, p.z_mantel_0 + 0.01))
    # O-ringspor under (O-ringen blir strekt 2,9 % inn på innerkanten)
    r_o_in = p.oring_id / 2.0 + p.oring_strekk_r
    k = k.cut(ring(r_o_in + p.oring_spor_b, r_o_in, z0 - 1, z0 + p.oring_spor_djup))
    # 3 x M3 nedanfrå: gjennomgåande Ø3,4, forsenking Ø6,4 x 2,2 for knappskrue ISO 7380
    for a in p.skrue_vinklar:
        x, y = polar(p.skrue_r, a)
        k = k.cut(syl_xy(x, y, 1.7, z0 - 1, z1 + 1))
        k = k.cut(syl_xy(x, y, 3.2, z0 - 1, z0 + 2.2))
    return k


def snorbitar(p: FyrParams) -> cq.Workplane:
    """3 bitar silikonsnor Ø2 x 10 i lommene under mantelen, teikna samanpressa (1,0 høg) under mantelkanten."""
    r_s = (p.r_mi + p.r_mo) / 2.0
    s = None
    for a in p.snor_vinklar:
        da = math.degrees(p.snor_l / 2.0 / r_s)
        e = sektor(r_s - p.snor_d / 2.0, r_s + p.snor_d / 2.0, a - da, a + da, p.z_mantel_0 - p.snor_spor_djup, p.z_mantel_0)
        s = e if s is None else s.union(e)
    return s


def oring(p: FyrParams) -> cq.Workplane:
    """Montert O-ring: strekt inn mot innerkanten av sporet, 1 mm under foten."""
    r_major = p.oring_id / 2.0 + p.oring_strekk_r + p.oring_snor / 2.0 + 0.001
    zc = p.z_fot_0 + p.oring_spor_djup - p.oring_snor / 2.0 + 0.0
    prof = []
    n = 24
    for i in range(n):
        a = 2 * math.pi * i / n
        prof.append((r_major + p.oring_snor / 2.0 * math.cos(a), zc + p.oring_snor / 2.0 * math.sin(a)))
    return dreidd(prof)


# ============================================================================ 04 mantel
def mantel(p: FyrParams) -> cq.Workplane:
    m = ring(p.r_mo, p.r_mi, p.z_mantel_0, p.z_mantel_1)
    for th in p.vindauge_vinklar:
        m = m.cut(radial_spalte(th, p.z_spalte_0, p.z_spalte_1, p.spalte_b, p.r_mi - 1, p.r_mo + 1))
    # bajonett: L-spor i underkanten. Mantelen blir sett ned med inngangen over knastane og vridd 14° MED klokka
    # (sett ovanfrå) for å låse. Teikna i nedtrykt stilling (mantelen på golvet i sporet).
    halv = math.degrees(p.baj_knast_b / 2.0 / p.r_mi) + 0.5
    zk0 = p.z_mantel_0 + p.baj_knast_z
    z_lag = zk0 - p.baj_spel
    z_topp = zk0 + p.baj_knast_h + 0.6          # over fasa på knasten
    for th in p.baj_vinklar:
        m = m.cut(sektor(p.r_mi - 1, p.r_mo + 1, th - p.baj_vri - halv, th + halv, z_lag, z_topp))
        m = m.cut(sektor(p.r_mi - 1, p.r_mo + 1, th - p.baj_vri - halv, th - p.baj_vri + halv, p.z_mantel_0 - 1, z_topp))
        # nabb på underkanten mellom låst stilling og inngangen
        m = m.union(sektor(p.r_mi, p.r_mo, th - halv - 1.8, th - halv - 0.2, z_lag - 0.01, z_lag + p.baj_nabb_h))
    return m


def mantel_prototype_delar(p: FyrParams, z_skoyt: float = 78.0, overlapp: float = 8.0):
    """P1S tek 256 mm i høgda; mantelen er 263. Prototypen blir delt i to med falsskøyt (limt)
    under spaltene. Ytre fuge ligg på z_skoyt + overlapp (86), 7 mm under spaltene."""
    m = mantel(p)
    r_mid = (p.r_mo + p.r_mi) / 2.0
    lim = 0.25                       # halv limfuge: 0,5 mm radielt spel i falsen (fuzzy skin + FDM-mål + lim)
    z1 = z_skoyt + overlapp
    big = 60.0
    nedre_kutt = syl(big, z1, p.z_mantel_1 + 5).union(ring(r_mid + lim, 0.0, z_skoyt, z1 + 0.01))
    nedre = m.cut(nedre_kutt)
    ovre_kutt = syl(big, p.z_mantel_0 - 5, z_skoyt).union(ring(big, r_mid - lim, z_skoyt - 0.01, z1))
    ovre = m.cut(ovre_kutt)
    return nedre, ovre


def glidering(p: FyrParams) -> cq.Workplane:
    """Serie: POM-C delt ring presspassa i boret. Prototype: 0,1 mm under boret og limt (FDM gjev overmål)."""
    r_ut = p.r_mi - (0.1 if p.variant == "prototype" else 0.0)
    g = ring(r_ut, p.r_glide_i, p.z_glide_0, p.z_glide_1)
    # innføringsfas nedst og øvst på innsida
    for zf, s in ((p.z_glide_0, 1), (p.z_glide_1, -1)):
        g = g.cut(dreidd([(p.r_glide_i - 0.01, zf - s * 0.01), (p.r_glide_i + 0.5, zf - s * 0.01), (p.r_glide_i - 0.01, zf + s * 0.5)]))
    return g


# ============================================================================ 05 hylse
def hylse_royr(p: FyrParams) -> cq.Workplane:
    h = ring(p.r_ho, p.r_hi, p.z_hylse_0, p.z_hylse_1)
    h = h.cut(sektor(p.r_hi - 1, p.r_ho + 1, -p.port_halv, p.port_halv, p.z_port_0, p.z_port_1))
    zk1 = p.z_hylse_1 - p.krone_topp
    zk0 = p.z_mantel_1 - p.krone_under
    for st in p.krone_stasjonar:
        for th in p.vindauge_vinklar:
            h = h.cut(radial_spalte(st + th, zk0, zk1, p.krone_b, p.r_hi - 1, p.r_ho + 1))
    # tre hol for stoppskruane (hovudet ligg søkk i holet, skjult under mantelen)
    for a in p.stopp_vinklar:
        h = h.cut(radial_bor(a, p.stopp_z, p.stopp_hovud_d + 0.3, p.r_hi - 0.5, p.r_ho + 1.0))
    return h


def kam_spor(p: FyrParams):
    """Gjev (a0, a1) i hylsesystemet for kvar brytar: utsparinga (full djupn) der brytaren har sleppt.
    Rampa ligg framfor a0 (frå a0 - kam_rampe til a0)."""
    ut = []
    for a_sw, terskel in p.sw:
        ut.append((a_sw + terskel, a_sw + p.vandring + 4.0))
    return ut


def hylsefot(p: FyrParams, samanprent: bool = False) -> cq.Workplane:
    """Fotringen inne i røyret: lager på tappen, klikkspor, kamspor for brytarane, gjenger for stoppskruane.
    Serie: 0,05 mm glidepasning i messingrøyret (skruane låser). samanprent=True: ringen går 0,2 mm inn i
    røyrveggen så prototypen blir éin lekam."""
    z0 = p.toppdekk_z1
    z1 = p.z_fotring_1
    rb = p.bor_r
    f = ring(p.r_hi + 0.2 if samanprent else p.r_hi - 0.05, rb, z0, z1)
    # innføringsfas i boret
    f = f.cut(dreidd([(rb - 0.01, z0 - 0.01), (rb + 0.8, z0 - 0.01), (rb - 0.01, z0 + 0.8)]))
    # klikkspor: ni V-spor (90°) i boret per tunge (tre tunger), eitt per stilling
    for a_k in p.klikk_vinklar:
        for k in range(int(round(p.vandring / p.deling)) + 1):
            f = f.cut(v_spor(a_k + k * p.deling, rb, p.klikk_djup, 2 * p.klikk_djup, p.klikk_z0, z1 + 1))
    # stoppskruar: forsenking for hovudet + kjernehol Ø2,5 for gjengeformande M3
    for a in p.stopp_vinklar:
        f = f.cut(radial_bor(a, p.stopp_z, p.stopp_hovud_d + 0.3, p.r_stopp_sete, p.r_ho + 1.0))
        f = f.cut(radial_bor(a, p.stopp_z, p.stopp_kjerne_d, rb - 1.0, p.r_stopp_sete + 0.01))
    # kamspor på undersida for brytarane: utsparing med rampe i båe endar (armen blir aldri treft frå sida)
    for (a0, a1) in kam_spor(p):
        rw = p.kam_rampe
        f = f.cut(sektor(p.kam_r0, p.kam_r1, a0, a1, z0 - 1.0, z0 + p.kam_djup))
        f = f.cut(rampe(p.kam_r0, p.kam_r1, a0 - rw, a0, z0 - 1.0, z0 + 0.02, z0 + p.kam_djup))
        f = f.cut(rampe(p.kam_r0, p.kam_r1, a1, a1 + rw, z0 - 1.0, z0 + p.kam_djup, z0 + 0.02))
    return f


def hylse(p: FyrParams) -> cq.Workplane:
    """Prototypen prentar røyr og fot i éitt stykke (éin lekam)."""
    return hylse_royr(p).union(hylsefot(p, samanprent=True))


def stoppskruar(p: FyrParams) -> cq.Workplane:
    """3 x ISO 7380 M3x5 knappskrue. Hovudet ligg i røyret, spissen går i sporet i tappen på chassiset."""
    s = None
    for a in p.stopp_vinklar:
        hovud = radial_bor(a, p.stopp_z, p.stopp_hovud_d, p.r_stopp_sete, p.r_stopp_sete + p.stopp_hovud_h)
        skaft = radial_bor(a, p.stopp_z, p.stopp_kjerne_d, p.r_stopp_sete - p.stopp_l, p.r_stopp_sete + 0.01)   # kjernediameter
        e = hovud.union(skaft)
        s = e if s is None else s.union(e)
    return s


# ============================================================================ 03 chassis
def chassis(p: FyrParams) -> cq.Workplane:
    zb = p.z_fot_1
    R = p.chassis_r
    zt0, zt1 = p.z_toppdekk_0, p.toppdekk_z1
    c = syl(R, zb, zb + p.chassis_flens_t)
    # sentrering: bogetapp under flensen inn i kabellomma i foten (hoppar over 150..210° der kabelen går)
    c = c.union(sektor(p.sentrering_r - 1.4, p.sentrering_r, 210.0, 510.0, zb - 2.0, zb + 0.01))
    # søyler
    for th in p.soyle_vinklar:
        c = c.union(sektor(R - 4.0, R, th - 11.0, th + 11.0, zb, zt0 + 0.1))
    # elektronikkdekk: Y-bru med nav. TRS-kontakten heng under navet; mutteren ligg oppå og blir trekt til
    # med ein 8 mm fastnøkkel frå sida. Mastfoten kviler på mutteren, pluggen i bøssinga styrer han sideleis.
    zd0, zd1 = p.dekk_z, p.dekk_z + p.dekk_t
    for th in p.soyle_vinklar:
        arm = boks(0.0, R - 2.0, -4.0 if th != 180.0 else -8.5, 4.0 if th != 180.0 else 8.5, zd0, zd1)
        c = c.union(roter(arm, th))
    c = c.union(syl(14.0, zd0, zd1))
    c = c.cut(syl(3.1, zd0 - 1.0, zd1 + 1.0))                                                    # hol for TRS-bøssinga (M6)
    # toppdekk: ring som styrer mantelen + Y-bru til navet, seks knusribber mot boret i mantelen
    c = c.union(ring(p.toppdekk_r, 26.0, zt0, zt1))
    halv_rib = math.degrees(0.75 / p.r_mi)
    for i in range(p.knusribber_n):
        a = i * 360.0 / p.knusribber_n
        c = c.union(dreidd([(p.toppdekk_r - 0.5, zt0), (p.r_mi, zt0), (p.r_mi, zt1 - 1.0), (p.toppdekk_r, zt1),
                            (p.toppdekk_r - 0.5, zt1)], a - halv_rib, a + halv_rib))
    for th in p.soyle_vinklar:
        c = c.union(roter(boks(0.0, 27.0, -5.0, 5.0, zt0, zt1), th))
    # nav (r 24) med styrehol for nøkkeltappen på lysrista: berre éin veg inn (rista mot spaltene)
    c = c.union(syl(24.0, zt0, zt1))
    c = c.cut(syl_xy(p.nokkel_r, 0.0, p.nokkel_d / 2.0 + 0.25, zt0 - 1.0, zt1 + 1.0))
    c = c.cut(syl_xy(p.nokkel_r, 0.0, p.nokkel_d / 2.0 + 0.25, zt1 - 1.2, zt1 + 1.0).union(
        cq.Workplane("XY").workplane(offset=zt1 - 1.2).center(p.nokkel_r, 0).circle(p.nokkel_d / 2.0 + 0.25)
        .workplane(offset=1.21).circle(p.nokkel_d / 2.0 + 1.4).loft()))
    # tappen (journal) som hylsefoten går på
    c = c.union(ring(p.tapp_ro, p.tapp_ri, zt1 - 0.01, p.tapp_topp))
    # spor for stoppskruane: kvar skruespiss går 90° (endestopp i båe endar); høgd M3 + 0,6 (stopp_spor_h)
    halv = math.degrees(1.8 / p.tapp_ro)
    hs = p.stopp_spor_h / 2.0
    for a in p.stopp_vinklar:
        c = c.cut(sektor(p.stopp_spor_botn, p.tapp_ro + 1.0, a - p.vandring - halv, a + halv, p.stopp_z - hs, p.stopp_z + hs))
    # tre klikktunger: tangentielle utkragingar i øvre del av tappen (ringen blir halden sentrert)
    l_deg = math.degrees(p.tunge_l / p.tapp_ro)
    zt_a, zt_b = p.klikk_z0 + 0.6, p.tapp_topp
    kul_r = 1.0
    for a_t, a_k in zip(p.tunge_vinklar, p.klikk_vinklar):
        es = p.tunge_ende_slisse
        c = c.cut(sektor(p.tapp_ri - 1.0, p.tapp_ro + 1.0, a_t - es, a_t, zt_a, zt_b + 1))                        # fri ende
        c = c.cut(sektor(p.tapp_ri - 1.0, p.tapp_ro + 1.0, a_t - l_deg - es, a_t, zt_a - p.tunge_slisse, zt_a))     # slisse under
        c = c.cut(sektor(p.tapp_ri - 1.0, p.tapp_ro - p.tunge_t, a_t - l_deg - es, a_t, zt_a - p.tunge_slisse, zt_b + 1))  # tynn tunge
        xk, yk = polar(p.bor_r + p.tunge_kul - kul_r, a_k)          # kula står 0,35 inn i boret til fotringen
        c = c.union(syl_xy(xk, yk, kul_r, zt_a + 0.3, zt_b - 0.3)
                    .intersect(sektor(p.tapp_ri, p.tapp_ro + 1.0, a_t - 5.0, a_t - es, zt_a, zt_b)))
    # gjennomgang og trakt i navet på toppdekket: mastfoten (mastfot_b x mastfot_l) med TRS-pluggen må gjennom når
    # lysmodulen blir sett ned ovanfrå; bøssinga i navet styrer pluggen, skjørtet styrer toppen av modulen
    kl = 0.3
    fx, fy = p.mastfot_b / 2.0 + kl, p.mastfot_l / 2.0 + kl
    c = c.cut(boks(-fx, fx, -fy, fy, zt0 - 1, zt1 + 1))
    trakt = cq.Workplane("XY").workplane(offset=zt1 - 3.0).rect(2 * fx, 2 * fy).workplane(offset=3.01).rect(2 * fx + 7.0, 2 * fy + 7.0).loft()
    c = c.cut(trakt)
    # brytarar: lomme under toppdekket, slisse for armen, brakett med to loddrette M2-spor (justering ± sw_just)
    for (a_sw, _t) in p.sw:
        lomme = sw_lokal(p, a_sw, boks(-3.2, 3.2, -10.3, 3.1, zt0 - 1.0, zt0 + 4.5))
        slisse = sw_lokal(p, a_sw, boks(-2.0, 2.0, -6.0, 6.0, zt0 - 1.0, zt1 + 1.0))
        brakett = sw_lokal(p, a_sw, boks(-4.7, -2.95, -12.0, 4.8, zt0 - 9.0, zt0 + 0.01))
        c = c.union(brakett).cut(lomme).cut(slisse)
        for y_h in (-6.85, -0.35):
            spor = (cq.Workplane("YZ").workplane(offset=-6.0).center(y_h, p.sw_hol_z)
                    .slot2D(2 * p.sw_just + 2.3, 2.3, 90).extrude(4.0))
            c = c.cut(sw_lokal(p, a_sw, spor))
    # innsatsar M3 nedanfrå
    for a in p.skrue_vinklar:
        x, y = polar(p.skrue_r, a)
        c = c.union(syl_xy(x, y, 4.2, zb, zb + p.innsats_l + 2.5))
        c = c.cut(syl_xy(x, y, p.innsats_hol_d / 2.0, zb - 0.01, zb + p.innsats_l + 1.0))
    # kabel opp frå lomma i foten (strekkavlastinga står i foten), etter siste stolpe
    c = c.cut(syl_xy(p.kabel_ut_x, 0.0, 3.5, zb - 3, zb + p.chassis_flens_t + 1))
    return c


def sw_lokal(p: FyrParams, a_sw: float, s: cq.Workplane) -> cq.Workplane:
    """Flytt ein kropp frå brytarens lokale ramme (x radielt ut, y tangentielt mot klokka, origo i kontaktpunktet
    for armen på r = sw_r) til chassisets ramme."""
    x, y = polar(p.sw_r, a_sw)
    return s.rotate((0, 0, 0), (0, 0, 1), a_sw).translate((x, y, 0))


def brytarar(p: FyrParams) -> cq.Workplane:
    """3 x Omron D2F-01L3 / D2F-L3 (simulert rulle-arm): kropp 12,8 x 5,8 x 6,5, hol Ø2 med 6,5 deling 3,15 frå enden,
    arma 3 mm brei med kontaktpunkt 10 mm frå svingenden. Teikna med arma inntrykt mot fotringen (z 76)."""
    b = None
    for (a_sw, _t) in p.sw:
        z_b0 = p.sw_hol_z - 1.5
        kropp = boks(-2.9, 2.9, -10.0, 2.8, z_b0, z_b0 + 6.5)
        for y_h in (-6.85, -0.35):
            kropp = kropp.cut(cq.Workplane("YZ").workplane(offset=-3.0).center(y_h, p.sw_hol_z).circle(1.0).extrude(6.0))
        arm = boks(-1.5, 1.5, -1.3, 1.3, z_b0 + 6.5, p.toppdekk_z1)
        e = sw_lokal(p, a_sw, kropp.union(arm))
        b = e if b is None else b.union(e)
    return b


def jack(p: FyrParams) -> cq.Workplane:
    """3,5 mm TRS-kontakt for panelmontering (M6-bøssing gjennom navet, mutter oppå), loddrett under elektronikkdekket."""
    zd0, zd1 = p.dekk_z, p.dekk_z + p.dekk_t
    kropp = boks(-5.5, 5.5, -5.5, 5.5, zd0 - 11.5, zd0)
    bossing = syl(3.0, zd0 - 0.01, zd1 + 0.01)
    mutter = syl(4.5, zd1, zd1 + 1.9)
    j = kropp.union(bossing).union(mutter)
    return j.cut(syl(1.85, zd0 - 11.0, zd1 + 2.0))


def kretskort(p: FyrParams) -> cq.Workplane:
    """Hullkort 24 x 15 med R1, R3, PTC F1 og JST PH for kabelen, på armen bak (asimut 180) på elektronikkdekket."""
    zd1 = p.dekk_z + p.dekk_t
    return boks(-37.5, -13.5, -7.5, 7.5, zd1, zd1 + 1.6).union(boks(-34.0, -17.0, -6.0, 6.0, zd1 + 1.6, zd1 + 7.5))


# ============================================================================ 06 lysmodul
def lysstav(p: FyrParams) -> cq.Workplane:
    """Aluminiumsflatstål 15 x 2 (EN AW-6060), baksida svart eloksert. Limt i mastfoten og i klypa på rista."""
    return boks(-p.stav_t / 2, p.stav_t / 2, -p.stav_b / 2, p.stav_b / 2, p.stav_z0, p.stav_z1)


def led_side(p: FyrParams) -> cq.Workplane:
    x0 = p.stav_t / 2
    return boks(x0, x0 + p.stripe_t, -p.stripe_b / 2, p.stripe_b / 2, p.stripe_z0, p.stripe_z1)


def led_topp(p: FyrParams) -> cq.Workplane:
    """4 x 25 mm stripe, tangentielt på eit kvadrat r 22 (45°, 135°, 225°, 315°), lyser opp mot loket."""
    z = p.topp_berar_z + 1.5
    e = None
    for i in range(p.topp_n):
        a = 45.0 + i * 360.0 / p.topp_n
        bit = boks(p.topp_r - p.stripe_b / 2, p.topp_r + p.stripe_b / 2, -p.topp_l / 2, p.topp_l / 2, z, z + p.stripe_t)
        e = roter(bit, a) if e is None else e.union(roter(bit, a))
    return e


def mastfot(p: FyrParams) -> cq.Workplane:
    """Mastfoten åleine (POM; prototype PETG HF): lomme nedanfrå for loddekroppen til 3,5 mm TRS-pluggen, stavspor
    ovanfrå med leidningskanal bak staven ned i lomma. Staven kviler på golvet i sporet utanfor lomma (|y| > 3)."""
    bx, ly = p.mastfot_b / 2.0, p.mastfot_l / 2.0
    f = boks(-bx, bx, -ly, ly, p.mastfot_z0, p.mastfot_z1)
    f = f.edges("|Z").chamfer(0.5)
    # lomme for pluggkroppen (limt), open nedover
    f = f.cut(syl((p.trs_kropp_d + p.mastfot_lomme_klaring) / 2.0, p.mastfot_z0 - 1.0, p.stav_z0 + 0.01))
    # stavspor (0,05 klaring rundt staven, limt) og leidningskanal bak staven (-X, baksida)
    f = f.cut(boks(-p.stav_t / 2 - 0.05 - p.mastfot_kanal, p.stav_t / 2 + 0.05, -p.stav_b / 2 - 0.05, p.stav_b / 2 + 0.05,
                   p.stav_z0, p.mastfot_z1 + 1))
    return f


def trs_plugg(p: FyrParams) -> cq.Workplane:
    """3,5 mm TRS-plugg, slank loddeutgåve utan skal: skaft Ø3,5 x trs_l med tupp, loddekropp Ø trs_kropp_d i lomma.
    Kroppen er teikna 0,1 større enn lomma (limt presspassing), så mastfot + plugg blir éin lekam i samanstillinga."""
    skaft = syl(1.75, p.mastfot_z0 - p.trs_l, p.mastfot_z0 + 0.01)
    tupp = cq.Workplane("XY").workplane(offset=p.mastfot_z0 - p.trs_l - 1.2).circle(0.6).workplane(offset=1.21).circle(1.75).loft()
    kropp = syl((p.trs_kropp_d + p.mastfot_lomme_klaring + 0.1) / 2.0, p.mastfot_z0, p.mastfot_z0 + p.trs_kropp_l)
    return skaft.union(tupp).union(kropp)


def modulkontakt(p: FyrParams) -> cq.Workplane:
    """Mastfot med 3,5 mm TRS-plugg (tupp TOPP+, ring SIDE+, hylse GND), slik han sit i samanstillinga."""
    return mastfot(p).union(trs_plugg(p))


# ============================================================================ 07 lysrist
def rist_kile(p: FyrParams, z0: float, z1: float) -> cq.Workplane:
    """Planet til lysrista (kilen mellom sideveggane, ut til r_ut), ekstrudert z0..z1."""
    cx, cy = p.stav_t / 2 + p.stripe_t, p.stav_b / 2 + 1.6
    ae = p.rist_vegg_vinkel
    pts = [(cx, -cy), (cx, cy)]
    for i in range(13):
        a = ae - 2 * ae * i / 12
        pts.append(polar(p.rist_r_ut, a))
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def rist_vegg(p: FyrParams, s: float, z0: float, z1: float) -> cq.Workplane:
    """Sidevegg (s = +1 / -1) frå hjørnet på klypa ut til r_ut ved ±rist_vegg_vinkel; tjukkleiken ligg utanfor kilen."""
    cx, cy = p.stav_t / 2 + p.stripe_t, s * (p.stav_b / 2 + 1.6)
    ex, ey = polar(p.rist_r_ut, s * p.rist_vegg_vinkel)
    L = math.hypot(ex - cx, ey - cy)
    ang = math.degrees(math.atan2(ey - cy, ex - cx))
    t = p.rist_vegg_t
    v = (cq.Workplane("XY").workplane(offset=z0).center(L / 2, s * t / 2).rect(L + 0.6, t).extrude(z1 - z0)
         .rotate((0, 0, 0), (0, 0, 1), ang).translate((cx, cy, 0)))
    return v


def lysrist(p: FyrParams) -> cq.Workplane:
    """Lysrista (07): PH-logikk. Lamellar 55° ned-og-ut med deling 16 mellom r 10 og 32 i ein kile på ±45°.
    Inga direkte stråle frå stripa går ut over 37° under horisontalen (sjå FyrParams.rist_avskjering).
    Golv, tak, sidevegger, skjold bak, berar for toppemitteren, skjørt og sete for loket i éin del.
    Loftet mellom taket og bereren er ope mot toppkammeret, så øvre del av spaltene får mjuk glød."""
    tb = math.tan(p.rist_helling * DEG)
    tv = p.rist_tv
    fall = (p.rist_r_ut - p.rist_r_inn) * tb
    kl = 0.2
    zf0, zf1 = p.rist_z0, p.rist_z0 + p.golv_t
    z_tak_inn = p.tak_topp(2.0)
    kile_hoy = rist_kile(p, zf0 - 1.0, z_tak_inn + 2.0)
    # lamellar (kjeglesegment) skorne til kilen
    lam = None
    for zt in p.lamell_tuppar:
        prof = [(p.rist_r_inn, zt + fall), (p.rist_r_ut, zt), (p.rist_r_ut, zt - tv), (p.rist_r_inn, zt + fall - tv)]
        l1 = dreidd(prof, -85.0, 85.0)
        lam = l1 if lam is None else lam.union(l1)
    k = lam.intersect(kile_hoy) if lam is not None else None
    # tak: øvste lamell, lukka inn til stripa (undersida over stripetoppen ved r 4,8)
    tak = dreidd([(2.0, p.tak_topp(2.0)), (p.rist_r_ut, p.tak_topp(p.rist_r_ut)),
                  (p.rist_r_ut, p.tak_topp(p.rist_r_ut) - tv), (2.0, p.tak_topp(2.0) - tv)], -85.0, 85.0)
    tak = tak.intersect(kile_hoy)
    k = tak if k is None else k.union(tak)
    # sideveggar opp til oversida av taket
    under_tak = dreidd([(0.0, zf0 - 1.0), (p.rist_r_ut + 6.0, zf0 - 1.0), (p.rist_r_ut + 6.0, p.tak_topp(p.rist_r_ut + 6.0)),
                        (0.0, p.tak_topp(0.0))])
    for s in (1.0, -1.0):
        k = k.union(rist_vegg(p, s, zf0, z_tak_inn + 1.0).intersect(under_tak))
    # golv (heil skive) og skjold bak (ryggrad), kjegle opp til skjørtet bak
    golv = syl(p.skjold_r + p.skjold_t, zf0, zf1)
    k = k.union(golv)
    z_kopp0 = p.skjort_z0 - 8.0          # kjegla skjold -> skjørt 46° (prentar utan støtte opp ned)
    k = k.union(sektor(p.skjold_r, p.skjold_r + p.skjold_t, p.rist_vegg_vinkel, 360.0 - p.rist_vegg_vinkel, zf0, z_kopp0 + 0.01))
    r_sk_i = p.r_rand_ut - p.skjort_t
    k = k.union(dreidd([(p.skjold_r, z_kopp0), (p.skjold_r + p.skjold_t, z_kopp0), (p.r_rand_ut, p.skjort_z0 + 0.01),
                        (r_sk_i, p.skjort_z0 + 0.01)], p.rist_vegg_vinkel, 360.0 - p.rist_vegg_vinkel))
    # klype rundt lysstaven (open framover for stripa), frå golvet til taket
    kx0, kx1 = -p.stav_t / 2 - 1.6, p.stav_t / 2 + p.stripe_t
    ky = p.stav_b / 2 + 1.6
    klype = boks(kx0, kx1, -ky, ky, zf0, z_tak_inn)
    # stavsporet sluttar på toppen av staven: rista kviler på staven (klypa er massiv over z stav_z1)
    klype = klype.cut(boks(-p.stav_t / 2 - kl, p.stav_t / 2 + kl, -p.stav_b / 2 - kl, p.stav_b / 2 + kl, zf0 - 1, p.stav_z1))
    klype = klype.cut(boks(0.0, 10.0, -p.stripe_b / 2 - 0.6, p.stripe_b / 2 + 0.6, zf0 + 0.01, p.stripe_z1 + 0.3))
    k = k.union(klype)
    # skjørt (kvitt inni) frå bereren opp forbi loket, sete og nabbar
    k = k.union(ring(p.r_rand_ut, r_sk_i, p.skjort_z0, p.z_lok_1 + 0.4))
    k = k.union(ring(r_sk_i + 0.01, p.r_lok - 1.5, p.z_lok_0 - 1.2, p.z_lok_0))
    for a in (0.0, 120.0, 240.0):          # nabbane ligg vekk frå fingergrepa (90° og 270°)
        k = k.union(dreidd([(p.r_lok - 0.25, p.z_lok_1 + 0.05), (r_sk_i + 0.01, p.z_lok_1 + 0.05),
                            (r_sk_i + 0.01, p.z_lok_1 + 0.4), (p.r_lok - 0.05, p.z_lok_1 + 0.4)], a - 3.0, a + 3.0))
    for a in (90.0, 270.0):        # fingergrep: løft loket ut, grip deretter skjørtet og trekk modulen opp
        k = k.cut(sektor(p.r_lok - 0.5, p.r_rand_ut + 1.0, a - 6.0, a + 6.0, p.z_lok_0 + 0.8, p.z_lok_1 + 1.0))
    # berar for toppemitteren: ring r 14..30 med fire eiker ut til skjørtet og to inn til klypa
    zb0, zb1 = p.topp_berar_z, p.topp_berar_z + 1.5
    k = k.union(ring(30.0, 14.0, zb0, zb1))
    for a in (0.0, 90.0, 180.0, 270.0):
        k = k.union(roter(boks(29.5, r_sk_i + 0.3, -2.0, 2.0, zb0, zb1), a))
    for a in (90.0, 270.0):
        k = k.union(roter(boks(ky - 0.5, 14.5, -2.0, 2.0, zb0, zb1), a))
    k = k.union(boks(kx0, kx1, -ky, ky, z_tak_inn - 0.01, zb1))
    # leidningshol for toppemitteren
    for a in (90.0, 270.0):
        x, y = polar(17.0, a)
        k = k.cut(syl_xy(x, y, 1.2, zb0 - 1, zb1 + 1))
    # nøkkeltapp gjennom navet på toppdekket: går inn i holet 19 mm før modulen sit, altså før pluggen når
    # kontakten; modulen kan berre setjast ned med rista mot spaltene
    k = k.union(syl_xy(p.nokkel_r, 0.0, p.nokkel_d / 2.0, p.nokkel_z0, zf0 + 0.6))
    k = k.cut(cq.Workplane("XY").workplane(offset=p.nokkel_z0 - 0.01).center(p.nokkel_r, 0)
              .circle(p.nokkel_d / 2.0 + 0.01).workplane(offset=0.81).circle(p.nokkel_d / 2.0 - 0.8).loft(combine=False)
              .cut(syl_xy(p.nokkel_r, 0.0, p.nokkel_d / 2.0 - 0.8, p.nokkel_z0 - 0.5, p.nokkel_z0 + 1.0)))
    # prototype: radiell rygg 0,8 mm på asimut 0 (i skuggen av vevet mellom dei to midtre spaltene) som
    # deler brua under kvar lamell når rista blir prenta opp ned
    if p.variant == "prototype":
        rygg = boks(p.rist_r_inn - 0.2, p.rist_r_ut, -0.4, 0.4, zf0, p.tak_topp(p.rist_r_ut) + 0.5)
        k = k.union(rygg.intersect(under_tak))
    # gjennomgang for lysstaven gjennom golv og klype (0,2 limfuge); rista kviler på toppen av staven (z stav_z1)
    k = k.cut(boks(-p.stav_t / 2 - kl, p.stav_t / 2 + kl, -p.stav_b / 2 - kl, p.stav_b / 2 + kl, zf0 - 2.0, p.stav_z1))
    # leidningsgjennomgangar i golvet: framfor staven for sidestripa (06b), bak klypa for toppstripene (06c);
    # under golvet går leiarane rundt staven til kanalen bak han i mastfoten
    lb = p.leidning_b
    # framfor staven må sidestripa (06b, ut til x stav_t/2 + stripe_t) kunne førast gjennom golvet når rista blir senka
    xf1 = max(p.stav_t / 2 + kl + lb, p.stav_t / 2 + p.stripe_t + 0.2)
    yf = max(4.0, p.stripe_b / 2 + 0.2)
    k = k.cut(boks(p.stav_t / 2 + kl - 0.01, xf1, -yf, yf, zf0 - 1.0, zf1 + 0.5))
    k = k.cut(boks(kx0 - lb - 0.4, kx0 - 0.01, 3.0, 7.5, zf0 - 1.0, zf1 + 0.5))
    return k


def lok(p: FyrParams) -> cq.Workplane:
    """Opal PMMA 3 mm (PLEXIGLAS Satinice WH02, 44 % transmisjon), laserskoren."""
    return syl(p.r_lok, p.z_lok_0, p.z_lok_1)


# ============================================================================ samanstilling
DELAR = {
    # namn: (byggjar, materiale, RGB, roterer_med_hylsa)
    "01_fot": (fot, "aluminium EN AW-6082 T6, pulverlakk RAL 3005 / PLA Matte mørk raud", (0.36, 0.09, 0.10), False),
    "03_chassis": (chassis, "PA12 SLS svart / PETG HF svart", (0.08, 0.08, 0.09), False),
    "04_mantel": (mantel, "aluminiumsrøyr EN AW-6060 T66 90x2, pulverlakk RAL 3005 / PLA Matte", (0.36, 0.09, 0.10), False),
    "05_hylse": (hylse_royr, "messing CuZn37 0,8 valsa, børsta + klarlakk / PLA Silk+ gull", (0.78, 0.60, 0.28), True),
    "05b_hylsefot": (hylsefot, "POM-C sprøytestøypt / PLA (prenta saman med hylsa)", (0.12, 0.12, 0.12), True),
    "05c_stoppskruar": (stoppskruar, "3 x ISO 7380 M3x5 A2 svart", (0.4, 0.4, 0.42), True),
    "06_lysstav": (lysstav, "aluminium EN AW-6060 flat 15x2, bak svart eloksert", (0.75, 0.76, 0.78), False),
    "06b_led_side": (led_side, "COB LED 5 V 8 mm RA90 2700 K, 158 mm", (1.0, 0.85, 0.55), False),
    "06c_led_topp": (led_topp, "COB LED 5 V 8 mm RA90 2700 K, 4 x 25 mm", (1.0, 0.85, 0.55), False),
    "06d_kontakt": (modulkontakt, "mastfot POM + 3,5 mm TRS-plugg", (0.2, 0.2, 0.2), False),
    "07_lysrist": (lysrist, "PA12 SLS kvit / PETG HF kvit (ugjennomsiktig)", (0.93, 0.92, 0.88), False),
    "08_lok": (lok, "PMMA opal 3 mm (PLEXIGLAS Satinice WH02)", (0.96, 0.94, 0.88), False),
    "10_glidering": (glidering, "POM-C svart, delt ring / PETG HF svart", (0.05, 0.05, 0.05), False),
    "11_oring": (oring, "O-ring silikon 85x3 60 ShA", (0.10, 0.10, 0.10), False),
    "11b_snor": (snorbitar, "3 x silikonsnor Ø2 x 10 (forspenning bajonett)", (0.12, 0.12, 0.12), False),
    "12_brytarar": (brytarar, "Omron 2 x D2F-01L3 + 1 x D2F-L3", (0.15, 0.15, 0.6), False),
    "13_jack": (jack, "3,5 mm TRS-kontakt, panel (M6)", (0.25, 0.25, 0.25), False),
    "14_kretskort": (kretskort, "hullkort: R1, R3, PTC F1, JST PH", (0.1, 0.35, 0.15), False),
}


def bygg_alle(p: FyrParams | None = None, theta: float = 0.0) -> dict:
    """Byggjer alle delane. theta = vinkelen hylsa er dreidd (0 = open, 90 = av)."""
    p = p or FyrParams()
    ut = {}
    for namn, (f, _m, _c, roterer) in DELAR.items():
        s = f(p)
        if roterer and theta:
            s = s.rotate((0, 0, 0), (0, 0, 1), -theta)
        ut[namn] = s
    return ut
