from pathlib import Path
from PIL import Image
import numpy as np
p=Path(__file__).resolve().parent
image=np.asarray(Image.open(p/"renders"/"closed_front.png").convert("RGB"))
ref=[
(165,359,424),(215,314,456),(265,288,471),(315,274,479),(365,249,491),
(415,240,497),(465,218,501),(515,206,506),(565,203,509),(615,188,512),
(665,188,512),(715,193,512),(765,200,512),(815,188,512),(865,185,508),
(915,198,505),(965,216,501),(1015,230,498),(1065,234,491),(1115,253,483),
(1165,267,477),(1215,284,467),(1265,311,457),(1315,331,445),(1365,371,417)]
rows=[]
for x,t,b in ref:
 if x>=image.shape[1]:continue
 vals=image[145:560,x,:]
 mask=(vals.max(axis=1)>46)&(vals.min(axis=1)>24)
 ys=np.where(mask)[0]+145
 if len(ys):rows.append((x,t,b,int(ys.min()),int(ys.max())))
if len(rows)<16: raise RuntimeError("Object absent in reference camera framing")
print("REFERENCE_SILHOUETTE:")
for x,t,b,pt,pb in rows:
 print("%4d top %+4d bottom %+4d"%(x,pt-t,pb-b))
print("TOP_MAE",round(sum(abs(pt-t) for x,t,b,pt,pb in rows)/len(rows),1))
print("BOTTOM_MAE",round(sum(abs(pb-b) for x,t,b,pt,pb in rows)/len(rows),1))
