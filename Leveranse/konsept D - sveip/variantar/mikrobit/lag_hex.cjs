// Lagar sveip_mikrobit.hex: MicroPython 2.1.2 for micro:bit V2 med sveip_mikrobit.py som main.py.
// Fila kan dragast rett over på MICROBIT-disken, eller opnast i python.microbit.org.
//
// Køyr frå mikrobit/:
//   npm install --prefix /tmp/mbfs @microbit/microbit-fs
//   NODE_PATH=/tmp/mbfs/node_modules node lag_hex.cjs microbit-micropython-v2.hex
// Grunnfila er den same som python.microbit.org brukar (MicroPython 2.1.2):
//   github.com/microbit-foundation/python-editor-v3, src/micropython/main/microbit-micropython-v2.hex
const fs = require("fs");
const path = require("path");
const { MicropythonFsHex, microbitBoardId } = require("@microbit/microbit-fs");

const grunn = fs.readFileSync(process.argv[2], "utf8");
const program = fs.readFileSync(path.join(__dirname, "sveip_mikrobit.py"), "utf8");
const ut = path.join(__dirname, "sveip_mikrobit.hex");

const fsHex = new MicropythonFsHex([{ hex: grunn, boardId: microbitBoardId.V2 }]);
fsHex.write("main.py", program);
fs.writeFileSync(ut, fsHex.getIntelHex(microbitBoardId.V2));

// Les fila attende og kontroller at main.py er det same som programmet.
const kontroll = new MicropythonFsHex([{ hex: grunn, boardId: microbitBoardId.V2 }]);
const filer = kontroll.importFilesFromHex(fs.readFileSync(ut, "utf8"));
if (filer.length !== 1 || kontroll.read("main.py") !== program) {
  throw new Error("main.py i hex-fila er ikkje lik sveip_mikrobit.py");
}
console.log(`${path.basename(ut)}: ${fs.statSync(ut).size} byte, main.py ${Buffer.byteLength(program)} byte, kontrollert`);
