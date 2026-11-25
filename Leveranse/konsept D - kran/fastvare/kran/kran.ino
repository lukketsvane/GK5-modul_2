// kran.ino · fastvare for Kran (konsept D) · Seeed XIAO SAMD21
//
// Berøring på knotten åleine:
//   kort trykk (under 0,4 s)  slår lyset av og på, med ei mjuk overgang
//   hald inne                 dimmar trinnlaust; retninga byter kvar gong du held
// Lampa hugsar siste nivå, også etter straumbrot.
//
// Kopling (sjå montering/Kran-montering.pdf, kopling):
//   5V   <- VBUS frå USB-C-kortet (E04). Ikkje kople USB-en på XIAO-en til medan lampa står i straum.
//   GND  <- GND frå USB-C-kortet, MOSFET-kortet, jordleidningen (aksel og arm) og koparteipen på stativet
//   A1   <- berøringsleidningen til koparfolien i knotten (QTouch)
//   A2   -> gate på MOSFET-kortet (E03, 100 ohm i serie, 100 kohm til GND). PWM 20 kHz, TCC1/WO[0]
//   A4   <- CC1 på USB-C-kortet (5,1 kohm til GND på kortet)
//   A5   <- CC2 på USB-C-kortet (5,1 kohm til GND på kortet)
//   LED+ <- VBUS, LED- -> drain på MOSFET-en, source -> GND
//
// Byggje: Arduino IDE 2, kortpakka «Seeed SAMD Boards» (Seeeduino XIAO), biblioteka «Adafruit FreeTouch Library»
// og «FlashStorage» (cmaglie). Ikkje kompilert enno: prøv på benken med ei kort LED-list før lomma blir limt.

#include <Adafruit_FreeTouch.h>
#include <FlashStorage.h>

// ---------------------------------------------------------------- innstillingar
const uint8_t PIN_BERORING = A1;
const uint8_t PIN_CC1 = A4;
const uint8_t PIN_CC2 = A5;
const uint16_t PWM_TOPP = 2399;          // 48 MHz / (2399 + 1) = 20 kHz
const uint16_t NIVA_MAKS = 1000;         // nivå 0-1000 blir PWM etter ei potenskurve (opplevd lysstyrke)
const uint16_t NIVA_MIN = 15;            // lågaste nivå når lyset er på (om lag 1 % lys)
const float KURVE = 2.4;
const uint16_t TERSKEL = 45;             // utslag over grunnlinja som tel som berøring (still etter FEILSOK-utskrifta)
const uint16_t SLEPP = 22;               // under dette er fingeren borte (hysterese)
const uint32_t KORT_MS = 400;            // kortare enn dette er eit trykk, lengre er dimming
const float DIM_FART = 0.40;             // nivå per ms under dimming: heile området på om lag 2,5 s
const uint32_t FADE_MS = 250;
const uint32_t LAGRE_ETTER_MS = 8000;    // lagre nivået når det har stått i ro så lenge
const uint32_t PROVE_MS = 10;            // målefrekvens for berøringa: 100 Hz
// #define FEILSOK                       // skriv rå målingar på serieporten (berre på benken, utan VBUS-straum)

// ---------------------------------------------------------------- tilstand
struct Lagra {
  uint32_t merke;
  uint16_t niva;
  uint8_t paa;
};
FlashStorage(lager, Lagra);
const uint32_t MERKE = 0x4B52414E;       // «KRAN»

Adafruit_FreeTouch beroring(PIN_BERORING, OVERSAMPLE_16, RESISTOR_50K, FREQ_MODE_SPREAD_MEDIAN);

uint16_t maksPwm = PWM_TOPP;             // avgrensa av kor mykje ladaren lovar (CC)
float niva = 400;                        // ønskt nivå når lyset er på
bool paa = true;
float vist = 0;                          // nivået som faktisk blir vist (glir mot målet)
float grunnlinje = 0;
float kryss[5];                          // PWM-krysstale: målt utslag ved 0, 25, 50, 75 og 100 % pådrag
bool rort = false;
uint32_t rortFra = 0;
bool dimma = false;
int8_t retning = +1;
uint32_t sistEndra = 0;
bool ulagra = false;
uint8_t treff = 0;

// ---------------------------------------------------------------- PWM på A2 (PA10), TCC1/WO[0]
void pwmStart() {
  GCLK->CLKCTRL.reg = GCLK_CLKCTRL_CLKEN | GCLK_CLKCTRL_GEN_GCLK0 | GCLK_CLKCTRL_ID_TCC0_TCC1;
  while (GCLK->STATUS.bit.SYNCBUSY) {}
  PORT->Group[0].PINCFG[10].bit.PMUXEN = 1;
  PORT->Group[0].PMUX[10 >> 1].reg = (PORT->Group[0].PMUX[10 >> 1].reg & 0xF0) | PORT_PMUX_PMUXE_E;
  TCC1->CTRLA.bit.ENABLE = 0;
  while (TCC1->SYNCBUSY.bit.ENABLE) {}
  TCC1->CTRLA.reg = TCC_CTRLA_PRESCALER_DIV1;
  TCC1->WAVE.reg = TCC_WAVE_WAVEGEN_NPWM;
  while (TCC1->SYNCBUSY.bit.WAVE) {}
  TCC1->PER.reg = PWM_TOPP;
  while (TCC1->SYNCBUSY.bit.PER) {}
  TCC1->CC[0].reg = 0;
  while (TCC1->SYNCBUSY.bit.CC0) {}
  TCC1->CTRLA.bit.ENABLE = 1;
  while (TCC1->SYNCBUSY.bit.ENABLE) {}
}

uint16_t padrag = 0;
void pwmSet(uint16_t v) {
  if (v > PWM_TOPP) v = PWM_TOPP;
  padrag = v;
  TCC1->CCB[0].reg = v;                  // bufra: blir teke i bruk ved neste periode, ingen glitch
  while (TCC1->SYNCBUSY.bit.CCB0) {}
}

uint16_t nivaTilPwm(float n) {
  if (n <= 0.5) return 0;
  float x = n / NIVA_MAKS;
  return (uint16_t)(pow(x, KURVE) * maksPwm + 0.5);
}

// ---------------------------------------------------------------- USB-C: kor mykje straum lovar ladaren?
// Med 5,1 kohm på CC: 0,25-0,61 V er standard USB (500/900 mA), 0,70-1,16 V er 1,5 A, 1,31-2,04 V er 3 A.
// Lampa trekkjer om lag 0,55 A på full styrke; på standard USB blir pådraget avgrensa til 75 %.
void lesCc() {
  analogReadResolution(12);
  uint32_t a = 0, b = 0;
  for (int i = 0; i < 16; i++) {
    a += analogRead(PIN_CC1);
    b += analogRead(PIN_CC2);
  }
  float v = max(a, b) / 16.0 * 3.3 / 4095.0;  // kabelen kan vere snudd: bruk den høgaste
  maksPwm = (v > 0.66) ? PWM_TOPP : (uint16_t)(PWM_TOPP * 0.75);
}

// ---------------------------------------------------------------- berøring
float mal() {
  return (float)beroring.measure();
}

float krysstale() {                      // forventa utslag frå PWM-leidningen ved dette pådraget
  float p = 4.0 * padrag / maksPwm;
  int i = min(3, (int)p);
  float t = p - i;
  return kryss[i] + (kryss[i + 1] - kryss[i]) * t - kryss[0];
}

// Ved oppstart blinkar lyset kort opp i fem trinn (0,3 s), og utslaget frå PWM-leidningen blir målt ved kvart
// trinn. Det stadfestar òg at LED-en verkar. Ikkje rør knotten dei første sekunda.
void kalibrer() {
  for (int k = 0; k <= 4; k++) {
    pwmSet((uint16_t)((uint32_t)maksPwm * k / 4));
    delay(60);
    float s = 0;
    for (int i = 0; i < 16; i++) s += mal();
    kryss[k] = s / 16;
  }
  pwmSet(0);
  delay(30);
  float s = 0;
  for (int i = 0; i < 32; i++) s += mal();
  grunnlinje = s / 32;
}

// ---------------------------------------------------------------- lagring
void lagre() {
  Lagra l = {MERKE, (uint16_t)niva, (uint8_t)paa};
  lager.write(l);                        // flash toler om lag 10 000 skrivingar: lagrar berre når nivået har roa seg
  ulagra = false;
}

void setup() {
#ifdef FEILSOK
  Serial.begin(115200);
#endif
  pwmStart();
  pwmSet(0);
  lesCc();
  beroring.begin();
  kalibrer();
  Lagra l = lager.read();
  if (l.merke == MERKE && l.niva >= NIVA_MIN && l.niva <= NIVA_MAKS) {
    niva = l.niva;
    paa = l.paa;
  }
  vist = 0;
  sistEndra = millis();
}

void loop() {
  static uint32_t sistProve = 0, sistSteg = 0;
  uint32_t no = millis();
  if (no - sistProve < PROVE_MS) return;
  uint32_t dt = no - sistSteg;
  sistProve = no;
  sistSteg = no;

  float utslag = mal() - krysstale() - grunnlinje;
  if (!rort) {
    if (utslag > TERSKEL) {
      if (++treff >= 3) {                // tre målingar på rad: 30 ms
        rort = true;
        rortFra = no;
        dimma = false;
        treff = 0;
      }
    } else {
      treff = 0;
      grunnlinje += (utslag) / 64.0;     // følgjer langsam drift (temperatur, fukt) når ingen rører
    }
  } else if (no - rortFra > 20000) {     // noko har lege på knotten i 20 s: ikkje ein finger, ny grunnlinje
    grunnlinje += utslag;
    rort = false;
    dimma = false;
  } else {
    if (utslag < SLEPP) {
      rort = false;
      if (dimma) {
        retning = -retning;              // neste gong du held, går det andre vegen
      } else {
        paa = !paa;                      // kort trykk
        if (paa && niva < NIVA_MIN) niva = NIVA_MIN;
      }
      sistEndra = no;
      ulagra = true;
    } else if (no - rortFra > KORT_MS) {
      if (!dimma) {
        dimma = true;
        if (!paa) {                      // held du på eit avslått lys, startar det på lågaste og går opp
          paa = true;
          niva = NIVA_MIN;
          vist = NIVA_MIN;
          retning = +1;
        } else if (niva >= NIVA_MAKS - 1) {
          retning = -1;
        } else if (niva <= NIVA_MIN + 1) {
          retning = +1;
        }
      }
      niva += retning * DIM_FART * dt;
      niva = constrain(niva, (float)NIVA_MIN, (float)NIVA_MAKS);
      vist = niva;                       // dimminga følgjer fingeren direkte
      sistEndra = no;
      ulagra = true;
    }
  }

  // mjuk overgang mot målet ved av/på
  float mal_ = paa ? niva : 0;
  float steg = (float)NIVA_MAKS * dt / FADE_MS;
  if (vist < mal_) vist = min(mal_, vist + steg);
  else if (vist > mal_) vist = max(mal_, vist - steg);
  pwmSet(nivaTilPwm(vist));

  if (ulagra && !rort && no - sistEndra > LAGRE_ETTER_MS) lagre();

#ifdef FEILSOK
  static uint8_t n = 0;
  if (++n >= 10) {
    n = 0;
    Serial.print(utslag); Serial.print('\t'); Serial.print(grunnlinje); Serial.print('\t');
    Serial.print(niva); Serial.print('\t'); Serial.println(paa);
  }
#endif
}
