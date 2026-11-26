# Sveip · fastvare for micro:bit V2 (MicroPython). Legg fila på kortet med python.microbit.org.
#
# pin0  arbeidslyset (PWM, ned)                  pin1  stemningslyset (PWM, opp)
# pin2  messingknappen (kapasitiv berøring)     3V/GND  regulert 3,3 V inn
# Ring 2 ligg nærast messingknappen. Kvar PWM-pinne skal ha 10 kΩ til GND, så lyset er av
# medan kortet startar.
#
# Éi handling (F2): hald fingeren på messingen, og lyset sveiper mellom arbeid og stemning.
# Eit kort trykk slår lampa av og på. Matrisa viser lampa sjølv: dei to øvste radene er
# skjermen (stemning), dei tre nedste er stamma (arbeid), og lysstyrken følgjer lyset.
from microbit import *

SVEIPTID = 8000        # ms for heile sveipet (F2: under 10 s)
KORT = 400             # ms: kortare berøring enn dette er av/på
STEG = 20              # ms per runde

pin0.write_analog(0)                           # lyset av før noko anna
pin1.write_analog(0)
pin0.set_analog_period_microseconds(256)       # 3,9 kHz, felles for begge kanalane
pin2.set_touch_mode(pin2.CAPACITIVE)           # kalibrerer her: ikkje rør messingen ved oppstart
speaker.off()

paa = False
blanding = 0.0         # 0 = berre arbeid, 1 = berre stemning
retning = 1
nede = 0               # ms fingeren har lege på


def vis(arbeid, stemning):
    a = 0 if arbeid == 0 else max(1, round(9 * arbeid))
    s = 0 if stemning == 0 else max(1, round(9 * stemning))
    for y in range(5):
        for x in range(5):
            display.set_pixel(x, y, s if y < 2 else (a if x < 3 else 0))


def lys(arbeid, stemning):
    pin0.write_analog(int(1023 * arbeid ** 2.2))     # gamma: jamn dimming for auget
    pin1.write_analog(int(1023 * stemning ** 2.2))
    vis(arbeid, stemning)


while True:
    i_ro = abs(accelerometer.get_strength() - 1000) < 250    # lampa blir ikkje lyfta eller flytta
    if pin2.is_touched() and i_ro:
        nede += STEG
        if nede > KORT and paa:                              # hald: sveip
            blanding = min(1.0, max(0.0, blanding + retning * STEG / SVEIPTID))
    else:
        if 0 < nede <= KORT and i_ro:                        # kort trykk: av eller på
            paa = not paa
        elif nede > KORT:                                    # neste hald går andre vegen
            retning = -retning
        nede = 0
    if paa:
        lys(1.0 - blanding, blanding)
    else:
        lys(0.0, 0.0)
    sleep(STEG)
