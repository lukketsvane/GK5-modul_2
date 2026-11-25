# -*- coding: utf-8 -*-
"""FYR · køyrer lysmodellen for den endelege rista og skriv kontroll/fyr_lys.json.

    py -3 cad/lysmodell/kjor.py            # 250 000 strålar, om lag eitt minutt på 6 kjernar

Modellen (fyrlys.py + run_side.py) er ein Monte Carlo-strålefylgjar i numpy for sidelyset: lamellar, tak, sidevegger,
stav og stripe, hylse med port og mantel med spalter. Geometrien står i cfg_serie.json og er skriven av frå FyrParams
for hand (rista r 10..32, 55°, deling 16, vegg 0,8, stripe z 92..250, hylse r 41,05..41,85): endrar du rista i
fyr_geometri.py, må cfg_serie.json følgje med. Mellomfiler (res_*.json, maps_*.npz, logg) hamnar i ei mellombels mappe.
Toppkammeret under loket er rekna for seg i topp.py; tala derifrå står i samle.py.
"""
import ctypes
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HER = Path(__file__).resolve().parent
ROT = HER.parent.parent


def main() -> None:
    ut = Path(tempfile.mkdtemp(prefix="fyr_lys_"))
    for f in ("fyrlys.py", "run_side.py"):
        shutil.copy2(HER / f, ut / f)
    cfg = (HER / "cfg_serie.json").read_text(encoding="utf-8").strip()
    strålar = sys.argv[1] if len(sys.argv) > 1 else "250000"
    with open(ut / "logg_FYR_final.txt", "w", encoding="utf-8") as logg:
        p = subprocess.Popen([sys.executable, "-W", "ignore", "run_side.py", "FYR_final", cfg, strålar], cwd=ut,
                             stdout=logg, stderr=subprocess.STDOUT)
        try:  # låg prioritet og to kjernar fri, så lyden ikkje hakkar
            h = ctypes.windll.kernel32.OpenProcess(0x0200 | 0x0400, False, p.pid)
            ctypes.windll.kernel32.SetPriorityClass(h, 0x40)
            ctypes.windll.kernel32.SetProcessAffinityMask(h, 0xFC)
        except Exception:  # noqa: BLE001
            pass
        if p.wait():
            raise SystemExit(f"run_side.py feila, sjå {ut / 'logg_FYR_final.txt'}")
    subprocess.run([sys.executable, str(HER / "samle.py"), str(ut), str(ROT / "kontroll" / "fyr_lys.json")], check=True)
    print("mellomfiler:", ut)


if __name__ == "__main__":
    main()
