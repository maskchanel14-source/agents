#!/usr/bin/env python3
"""Gabungkan deck HTML dengan ilustrasinya menjadi satu berkas mandiri.

Dipakai untuk berkas yang diunggah ke Google Drive atau dikirim lewat surel:
tanpa berkas ini, deck harus dibuka dari folder yang utuh agar gambar tampil.

Jalankan: python3 tools/make_standalone.py
"""
import base64
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "ssc-pedodonsia.html")
OUT = os.path.join(ROOT, "ssc-pedodonsia-standalone.html")

cache = {}


def data_uri(path):
    if path not in cache:
        ext = "jpeg" if path.endswith((".jpg", ".jpeg")) else "png"
        blob = base64.b64encode(open(os.path.join(ROOT, path), "rb").read()).decode()
        cache[path] = "data:image/%s;base64,%s" % (ext, blob)
    return cache[path]


html = open(SRC, encoding="utf-8").read()
html = re.sub(r'src="(assets/art/[^"]+)"', lambda m: 'src="%s"' % data_uri(m.group(1)), html)
# ilustrasi yang dipasang lewat JavaScript pada panel langkah klinis
html = re.sub(r'"(assets/art/[^"]+\.jpg)"', lambda m: '"%s"' % data_uri(m.group(1)), html)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

left = len(re.findall(r"assets/art", html))
print("wrote", os.path.basename(OUT), round(os.path.getsize(OUT) / 1048576, 2), "MB; sisa referensi luar:", left)
