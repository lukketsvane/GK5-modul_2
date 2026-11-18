from pathlib import Path
p=Path(__file__).resolve().parent
target=p/"build.py"
original=target.read_text(encoding="utf-8")
new=(p/"blade_astra.py").read_text(encoding="utf-8").strip()+"\n\n"
assert original.count("def blade(kind, sign):")==1
assert "def shoe(sign):" in original
a=original.index("def blade(kind, sign):")
z=original.index("def shoe(sign):",a)
(p/"build_before_astra.py").write_text(original,encoding="utf-8")
target.write_text(original[:a]+new+original[z:],encoding="utf-8")
print("patched blade() from gpt-6.2-astra; source bytes",len(new),flush=True)
