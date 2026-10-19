# Cetak naskah_presentasi.md menjadi HTML siap cetak (A4).
# Tanpa dependensi: hanya parser markdown kecil untuk heading, paragraf, garis, dan tebal.
#   python3 tools/build_script.py

import html
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "naskah_presentasi.md")
OUT = os.path.join(HERE, "naskah-presentasi.html")

META_RE = re.compile(r"^(Pemateri:|20 Oktober|Total sekitar|Stainless steel crown pada gigi)")


def inline(text):
    text = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def convert(md):
    lines = md.split("\n")
    out = []
    para = []
    open_slide = False

    def flush():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))
            para.clear()

    def close_slide():
        nonlocal open_slide
        if open_slide:
            out.append("</section>")
            open_slide = False

    for ln in lines:
        ln = ln.rstrip()
        if ln.startswith("# "):
            flush()
            close_slide()
            out.append("<h1>%s</h1>" % inline(ln[2:]))
        elif ln.startswith("## "):
            flush()
            close_slide()
            out.append('<section class="slide">')
            open_slide = True
            out.append("<h2>%s</h2>" % inline(ln[3:]))
        elif ln.strip() == "---":
            flush()
            close_slide()
        elif not ln.strip():
            flush()
        elif META_RE.match(ln):
            flush()
            out.append('<p class="meta">%s</p>' % inline(ln))
        else:
            para.append(ln.strip())
    flush()
    close_slide()
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 20mm 18mm 18mm; }
* { box-sizing: border-box; }
body {
  margin: 0; background: #fff; color: #15323a;
  font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
  font-size: 11.4pt; line-height: 1.6;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
.wrap { max-width: 152mm; margin: 0 auto; }
h1 {
  font-family: "Source Serif 4", Georgia, serif; font-weight: 600;
  font-size: 27pt; line-height: 1.1; letter-spacing: -.01em;
  margin: 0 0 7mm; padding-top: 2mm;
}
p.meta { margin: 0 0 1.6mm; color: #5b7378; font-size: 10.8pt; }
p.meta:first-of-type { color: #15323a; font-size: 12.4pt; }
h2 {
  font-family: "Source Serif 4", Georgia, serif; font-weight: 600;
  font-size: 14.5pt; margin: 0 0 4mm; padding-top: 3mm;
  border-top: 2.2pt solid #c65b45; display: inline-block;
  padding-right: 14mm; break-after: avoid;
}
section.slide { break-inside: avoid; padding: 4mm 0 6mm; }
p { margin: 0 0 3.4mm; }
p + p { margin-top: 0; }
strong { font-weight: 650; }
hr { border: 0; border-top: 1px solid #e3d9c8; margin: 7mm 0 2mm; }
section.slide p { orphans: 2; widows: 2; }
"""


def main():
    md = open(SRC, encoding="utf-8").read()
    body = convert(md)
    doc = """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>Naskah presentasi SSC</title>
<style>%s</style>
</head>
<body>
<div class="wrap">
%s
</div>
</body>
</html>
""" % (CSS, body)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print("wrote naskah-presentasi.html", len(doc), "bytes")


if __name__ == "__main__":
    main()
