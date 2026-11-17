# -*- coding: utf-8 -*-
import os
import shutil
from PIL import Image, ImageSequence

KAYNAK = "foxy.gif"
HEDEF = "foxy_frames"
MAX_KARE = 50
MAX_BOYUT = 480

if not os.path.exists(KAYNAK):
    raise SystemExit("HATA: foxy.gif bulunamadi. main.py ile ayni klasorde olmali.")

if os.path.isdir(HEDEF):
    shutil.rmtree(HEDEF)
os.makedirs(HEDEF)

gif = Image.open(KAYNAK)
kareler = []
for kare in ImageSequence.Iterator(gif):
    kareler.append(kare.convert("RGBA"))

print("GIF icindeki toplam kare:", len(kareler))

adim = max(1, len(kareler) // MAX_KARE)
sayac = 0
for i in range(0, len(kareler), adim):
    k = kareler[i].copy()
    k.thumbnail((MAX_BOYUT, MAX_BOYUT))
    k.save(os.path.join(HEDEF, "f%03d.png" % sayac))
    sayac += 1

print("TAMAM:", sayac, "kare olusturuldu ->", HEDEF)