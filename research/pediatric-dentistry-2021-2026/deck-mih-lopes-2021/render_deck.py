#!/usr/bin/env python3
"""Render the built PPTX to PNG with real font metrics, for design review.

Why this exists
---------------
The sandbox has no PowerPoint, LibreOffice, or browser, so the deck could only be
checked with a rough Pillow sketch. This renderer reads the actual .pptx package
(python-pptx + raw OOXML for transparency and letter spacing), lays it out with
ReportLab using metric-compatible fonts, and rasterises the result with PyMuPDF.
The output is a faithful proxy for PowerPoint: same fonts, same boxes, same sizes.

Preview fonts (metric-compatible, SIL OFL):
  Georgia  -> Gelasio     (Sorkin Type)
  Calibri  -> LC-Sans     (Carlito derivative)
  Consolas -> DejaVu Sans Mono (approximate)

Fetch them with `python3 render_deck.py --fetch-fonts` (clones two small GitHub
font repos). Without the fonts the renderer falls back to base-14 fonts and says so.

Usage:
  python3 render_deck.py [deck.pptx] [--outdir audits/render] [--dpi 110]
  python3 render_deck.py --fetch-fonts
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import pymupdf
from lxml import etree
from pptx import Presentation
from pptx.enum.chart import XL_CHART_TYPE
from pptx.oxml.ns import qn
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas

HERE = Path(__file__).resolve().parent
FONT_DIR = Path("/tmp/preview-fonts")
EMU_IN = 914400.0
PT_IN = 72.0

FONT_PLANS = {
    "Gelasio": {"regular": "Gelasio-Regular.ttf", "bold": "Gelasio-Bold.ttf",
                "italic": "Gelasio-Italic.ttf", "bolditalic": "Gelasio-Bold.ttf"},
    "LCSans": {"regular": "LCSans-Regular.ttf", "bold": "LCSans-Bold.ttf",
               "italic": "LCSans-Italic.ttf", "bolditalic": "LCSans-BoldItalic.ttf"},
    "DejaVuMono": {"regular": "DejaVuSansMono.ttf", "bold": "DejaVuSansMono-Bold.ttf",
                   "italic": "DejaVuSansMono.ttf", "bolditalic": "DejaVuSansMono-Bold.ttf"},
}
# metric-compatible preview faces for the fonts the deck asks for:
#   Cambria / Georgia -> Gelasio (SIL OFL, Sorkin Type)
#   Calibri / Segoe UI -> LC-Sans (SIL OFL, Carlito derivative)
#   Consolas / Courier -> DejaVu Sans Mono (Bitstream Vera derivative)
FAMILY_ALIASES = {
    "cambria": "Gelasio", "georgia": "Gelasio", "times new roman": "Gelasio",
    "calibri": "LCSans", "segoe ui": "LCSans", "segoe ui semibold": "LCSans",
    "arial": "LCSans", "helvetica": "LCSans",
    "consolas": "DejaVuMono", "courier new": "DejaVuMono", "courier": "DejaVuMono",
}
UNMAPPED: set[str] = set()

FALLBACK = {"Georgia": ("Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic"),
            "Calibri": ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique"),
            "Consolas": ("Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique")}
SLOTS = ("regular", "bold", "italic", "bolditalic")

FONT_SOURCES = {
    "Gelasio": "https://github.com/SorkinType/Gelasio",
    "LC-Sans": "https://github.com/cssobral2013/LC-Sans",
}
REGISTERED: dict[tuple[str, str], str] = {}
MISSING_FONTS = False


def fetch_fonts() -> None:
    """Clone the OFL font repos and copy the three faces we need."""
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    work = Path("/tmp/font-src")
    work.mkdir(exist_ok=True)
    if not (work / "Gelasio").exists():
        subprocess.run(["git", "clone", "--depth", "1", "--quiet", FONT_SOURCES["Gelasio"],
                        str(work / "Gelasio")], check=True)
    if not (work / "LC-Sans").exists():
        subprocess.run(["git", "clone", "--depth", "1", "--quiet", FONT_SOURCES["LC-Sans"],
                        str(work / "LC-Sans")], check=True)
    import shutil

    pairs = [
        (work / "Gelasio/fonts/ttf/Gelasio-Regular.ttf", "Gelasio-Regular.ttf"),
        (work / "Gelasio/fonts/ttf/Gelasio-Bold.ttf", "Gelasio-Bold.ttf"),
        (work / "Gelasio/fonts/ttf/Gelasio-Italic.ttf", "Gelasio-Italic.ttf"),
        (work / "LC-Sans/ttf/LCSans-Regular.ttf", "LCSans-Regular.ttf"),
        (work / "LC-Sans/ttf/LCSans-Bold.ttf", "LCSans-Bold.ttf"),
        (work / "LC-Sans/ttf/LCSans-Italic.ttf", "LCSans-Italic.ttf"),
        (work / "LC-Sans/ttf/LCSans-BoldItalic.ttf", "LCSans-BoldItalic.ttf"),
    ]
    for src, name in pairs:
        if src.exists():
            shutil.copy2(src, FONT_DIR / name)
    mono = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
    mono_bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf")
    if mono.exists():
        shutil.copy2(mono, FONT_DIR / "DejaVuSansMono.ttf")
    if mono_bold.exists():
        shutil.copy2(mono_bold, FONT_DIR / "DejaVuSansMono-Bold.ttf")
    print(f"fonts ready in {FONT_DIR}")


def register_fonts() -> None:
    global MISSING_FONTS
    for family, plan in FONT_PLANS.items():
        for slot in SLOTS:
            file = FONT_DIR / plan[slot]
            key = (family, slot)
            if file.exists():
                name = f"{family}-{slot}"
                pdfmetrics.registerFont(TTFont(name, str(file)))
                REGISTERED[key] = name
        if (family, "regular") not in REGISTERED:
            MISSING_FONTS = True
            for slot, base in zip(SLOTS, FALLBACK[family]):
                REGISTERED[(family, slot)] = base


def font_name(family: str, bold: bool, italic: bool) -> str:
    """Map a deck font name onto a registered metric-compatible preview face."""
    resolved = FAMILY_ALIASES.get((family or "").strip().lower())
    if resolved is None:
        UNMAPPED.add(family or "?")
        resolved = "LCSans"
    slot = "bold" if bold else "regular"
    if italic:
        slot = "bolditalic" if bold else "italic"
    return REGISTERED.get((resolved, slot)) or REGISTERED.get((resolved, "regular"), "Helvetica")


# ---------------------------------------------------------------- colour helpers
def rgb_of(color_format, default: str = "#000000") -> str:
    try:
        value = str(color_format.rgb)
        return "#" + value[-6:]
    except Exception:
        return default


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")[:6]
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def blend(fg: str, bg: str, alpha: float) -> Color:
    fr, fg_, fb = hex_to_rgb(fg)
    br, bg_, bb = hex_to_rgb(bg)
    a = max(0.0, min(1.0, alpha))
    return Color(fr * a + br * (1 - a), fg_ * a + bg_ * (1 - a), fb * a + bb * (1 - a))


def alpha_of(element) -> float:
    node = element.find(".//" + qn("a:alpha")) if element is not None else None
    if node is None:
        return 1.0
    try:
        return int(node.get("val", "100000")) / 100000.0
    except ValueError:
        return 1.0


# ------------------------------------------------------------------ text layout
def wrap_lines(text: str, font: str, size: float, max_width: float, char_space: float) -> list[str]:
    out: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            out.append("")
            continue
        words, current = paragraph.split(" "), ""
        for word in words:
            candidate = f"{current} {word}".strip()
            width = pdfmetrics.stringWidth(candidate, font, size) + char_space * max(0, len(candidate) - 1)
            if not current or width <= max_width:
                current = candidate
            else:
                out.append(current)
                current = word
        out.append(current)
    return out


def draw_text_frame(c, frame, box, bg: str, overflow: list) -> None:
    """Draw a PPTX text frame.

    `box` is (x0, y_bottom, x1, y_top) in PDF coordinates, so text flows downward
    from y_top. PowerPoint overflows a text box rather than clipping it, so the clip
    region is widened vertically instead of cutting descenders.
    """
    tf = frame
    x0 = box[0] + tf.margin_left / EMU_IN * PT_IN
    x1 = box[2] - tf.margin_right / EMU_IN * PT_IN
    y_top = box[3] - tf.margin_top / EMU_IN * PT_IN
    y_bottom = box[1] + tf.margin_bottom / EMU_IN * PT_IN
    width = x1 - x0
    height = y_top - y_bottom
    if width <= 2 or height <= 0:
        return

    blocks = []
    for paragraph in tf.paragraphs:
        text = "".join(run.text for run in paragraph.runs)
        run = paragraph.runs[0] if paragraph.runs else None
        size = (run.font.size.pt if run is not None and run.font.size else 12.0) * PT_IN / 72.0
        bold = bool(run.font.bold) if run is not None else False
        italic = bool(run.font.italic) if run is not None else False
        family = run.font.name if (run is not None and run.font.name) else "Calibri"
        colour = rgb_of(run.font.color) if run is not None else "#000000"
        space_after = paragraph.space_after.pt * PT_IN / 72 if paragraph.space_after else 0.0
        line_spacing = paragraph.line_spacing or 1.0
        if not isinstance(line_spacing, float) or line_spacing < 0.9:
            line_spacing = 1.0
        char_space = 0.0
        if run is not None and run.font._rPr is not None and run.font._rPr.get("spc"):
            char_space = int(run.font._rPr.get("spc")) / 100.0
        align = str(paragraph.alignment).split(".")[-1].split(" ")[0] if paragraph.alignment else "LEFT"
        font = font_name(family, bold, italic)
        lines = wrap_lines(text, font, size, width, char_space)
        advance = size * 1.2 * line_spacing
        blocks.append({"lines": lines, "font": font, "size": size, "colour": colour,
                       "align": align, "advance": advance, "space_after": space_after,
                       "char_space": char_space})
    total = sum(len(b["lines"]) * b["advance"] + b["space_after"] for b in blocks)
    anchor = str(tf.vertical_anchor).split(".")[-1].split(" ")[0] if tf.vertical_anchor else "TOP"
    if anchor == "MIDDLE":
        y = y_top - max(0.0, (height - total) / 2.0)
    elif anchor == "BOTTOM":
        y = y_bottom + total
    else:
        y = y_top
    if total > height + 2:
        overflow.append(round((total - height) / PT_IN, 3))

    slack = max(2.0, blocks[0]["size"] * 0.35) if blocks else 2.0
    c.saveState()
    clip = c.beginPath()
    clip.rect(box[0] - slack, box[1] - slack, (box[2] - box[0]) + 2 * slack,
              (box[3] - box[1]) + 2 * slack)
    c.clipPath(clip, stroke=0, fill=0)
    for block in blocks:
        ascent = block["size"] * 0.78
        for line in block["lines"]:
            text_width = (pdfmetrics.stringWidth(line, block["font"], block["size"])
                          + block["char_space"] * max(0, len(line) - 1))
            x = x0
            if block["align"] == "CENTER":
                x = x0 + (width - text_width) / 2
            elif block["align"] == "RIGHT":
                x = x0 + width - text_width
            text_object = c.beginText(x, y - ascent)
            text_object.setFont(block["font"], block["size"])
            text_object.setFillColor(hex_to_color(block["colour"]))
            if block["char_space"]:
                text_object.setCharSpace(block["char_space"])
            text_object.textOut(line)
            c.drawText(text_object)
            y -= block["advance"]
        y -= block["space_after"]
    c.restoreState()


def hex_to_color(value: str) -> Color:
    r, g, b = hex_to_rgb(value)
    return Color(r, g, b)


# ----------------------------------------------------------------- shape drawing
def build_path(c, kind: str, x: float, y: float, w: float, h: float, radius: float = 0.0):
    """Return a ReportLab path object for the shape kind."""
    path = c.beginPath()
    if kind == "oval":
        # NOTE: pdfgen's PdfPathObject.ellipse takes (cx, cy, rx, ry), unlike the
        # canvas.ellipse(x0, y0, x1, y1) bounding-box form used for chart arcs.
        path.ellipse(x + w / 2, y + h / 2, w / 2, h / 2)
    elif kind in ("triangle", "isosceles_triangle"):
        path.moveTo(x + w / 2, y + h)
        path.lineTo(x + w, y)
        path.lineTo(x, y)
        path.close()
    elif kind == "right_arrow":
        shaft = h * 0.42
        head = w * 0.42
        path.moveTo(x, y + (h - shaft) / 2)
        path.lineTo(x + w - head, y + (h - shaft) / 2)
        path.lineTo(x + w - head, y)
        path.lineTo(x + w, y + h / 2)
        path.lineTo(x + w - head, y + h)
        path.lineTo(x + w - head, y + (h + shaft) / 2)
        path.lineTo(x, y + (h + shaft) / 2)
        path.close()
    elif kind in ("rounded_rectangle", "round2same") and radius > 0:
        path.roundRect(x, y, w, h, min(radius, w / 2, h / 2))
    else:
        path.rect(x, y, w, h)
    return path


def gradient_stops(spPr):
    """Return (colours, positions, angle_degrees) for a gradient fill, else None."""
    grad = spPr.find(qn("a:gradFill"))
    if grad is None:
        return None
    stop_list = grad.find(qn("a:gsLst"))
    if stop_list is None:
        return None
    stops = []
    for stop in stop_list.findall(qn("a:gs")):
        colour_node = stop.find(qn("a:srgbClr"))
        if colour_node is None:
            continue
        try:
            position = int(stop.get("pos", "0")) / 100000.0
        except ValueError:
            position = 0.0
        stops.append((position, "#" + colour_node.get("val", "000000")))
    if len(stops) < 2:
        return None
    linear = grad.find(qn("a:lin"))
    angle = 0.0
    if linear is not None:
        try:
            angle = int(linear.get("ang", "0")) / 60000.0
        except ValueError:
            angle = 0.0
    for flip in ("a:flip",):
        if grad.find(qn(flip)) is not None:
            angle += 180.0
    return stops, angle


def draw_gradient(c, spPr, path, x, y, w, h, stops, angle) -> None:
    """Approximate a linear PowerPoint gradient with thin interpolated bands."""
    import math as _math

    (p0, c0), (p1, c1) = stops[0], stops[-1]
    r0, g0, b0 = hex_to_rgb(c0)
    r1, g1, b1 = hex_to_rgb(c1)
    bands = 120
    # PowerPoint angle: 0 = left-to-right, grows clockwise. PDF y grows upward.
    rad = _math.radians(angle)
    dx, dy = _math.cos(rad), _math.sin(rad)
    extent = abs(dx) * w + abs(dy) * h
    c.saveState()
    c.clipPath(path, stroke=0, fill=0)
    for i in range(bands):
        t = i / (bands - 1)
        colour = Color(r0 + (r1 - r0) * t, g0 + (g1 - g0) * t, b0 + (b1 - b0) * t)
        c.setFillColor(colour)
        # band strip perpendicular to the gradient axis
        s0 = (t - 0.5 / bands - 0.5) * extent
        s1 = (t + 0.5 / bands - 0.5) * extent
        strip = c.beginPath()
        if abs(dx) >= abs(dy):
            xa, xb = x + w / 2 + s0 * (1 if dx >= 0 else -1), x + w / 2 + s1 * (1 if dx >= 0 else -1)
            strip.rect(min(xa, xb), y - h, abs(xb - xa) + 0.5, 3 * h)
        else:
            ya = y + h / 2 + s0 * (1 if dy >= 0 else -1)
            yb = y + h / 2 + s1 * (1 if dy >= 0 else -1)
            strip.rect(x - w, min(ya, yb), 3 * w, abs(yb - ya) + 0.5)
        c.drawPath(strip, stroke=0, fill=1)
    c.restoreState()


def auto_shape_kind(shape) -> str:
    try:
        name = str(shape.auto_shape_type).split(".")[-1].split(" ")[0]
        return name.lower()
    except Exception:
        return "rectangle"


def draw_shape(c, shape, bg: str) -> None:
    slide_h = 7.5 * PT_IN
    width = shape.width / EMU_IN * PT_IN
    height = shape.height / EMU_IN * PT_IN
    x = shape.left / EMU_IN * PT_IN
    y = slide_h - shape.top / EMU_IN * PT_IN - height
    kind = auto_shape_kind(shape)
    rotation = float(getattr(shape, "rotation", 0.0) or 0.0)

    fill_color, alpha = None, 1.0
    spPr = shape._element.spPr
    try:
        if shape.fill.type is not None and shape.fill.type != 5:  # 5 = background
            fill_color = rgb_of(shape.fill.fore_color)
            alpha = alpha_of(spPr.find(qn("a:solidFill")))
    except Exception:
        fill_color = None

    line_color, line_width = None, 0.0
    ln = spPr.find(qn("a:ln"))
    try:
        if ln is not None and shape.line.width:
            no_fill = ln.find(qn("a:noFill"))
            if no_fill is None:
                line_color = rgb_of(shape.line.color)
                line_width = max(0.4, shape.line.width.pt * PT_IN / 72)
                alpha = min(alpha, alpha_of(ln))
    except Exception:
        line_color = None

    radius = min(width, height) * 0.16 if kind in ("rounded_rectangle", "round2same") else 0.0
    gradient = gradient_stops(spPr)
    c.saveState()
    if rotation:
        c.translate(x + width / 2, y + height / 2)
        c.rotate(-rotation)
        x, y = -width / 2, -height / 2
    path = build_path(c, kind, x, y, width, height, radius)
    if gradient:
        draw_gradient(c, spPr, path, x, y, width, height, gradient[0], gradient[1])
    elif fill_color:
        c.setFillColor(blend(fill_color, bg, alpha))
        c.drawPath(path, stroke=1 if line_color else 0, fill=1)
    if line_color:
        c.setStrokeColor(blend(line_color, bg, alpha))
        c.setLineWidth(line_width)
        c.drawPath(path, stroke=1, fill=0)
    c.restoreState()


# ------------------------------------------------------------------------- charts
def draw_chart(c, shape, top_h: float, bg: str, spec_chart: dict | None):
    chart = shape.chart
    left, top = shape.left / EMU_IN * PT_IN, shape.top / EMU_IN * PT_IN
    width, height = shape.width / EMU_IN * PT_IN, shape.height / EMU_IN * PT_IN
    x0 = left
    y1 = top_h - top
    y0 = y1 - height
    ctype = str(chart.chart_type).split(".")[-1].split(" ")[0].upper()
    values, categories = [], []
    try:
        plot = chart.plots[0]
        series = plot.series[0]
        values = [float(v) for v in series.values]
    except Exception:
        values = []
    try:
        categories = [str(cat) for cat in chart.plots[0].categories]
    except Exception:
        categories = []
    label_format = spec_chart.get("label_format") if spec_chart else None
    data_labels = bool(spec_chart.get("data_labels")) if spec_chart else False
    font_size = float(spec_chart.get("font_size", 10.5)) if spec_chart else 10.5
    gap = float(spec_chart.get("gap_width", 55)) if spec_chart else 55.0
    colors = list(spec_chart.get("colors", [])) if spec_chart else []
    if not colors:
        colors = ["#0E7490"]
    label_font = font_name("Calibri", False, False)
    if ctype.startswith("DOUGHNUT") or ctype.startswith("PIE"):
        total = sum(values) or 1.0
        side = min(width, height) - 6
        cx, cy = x0 + width / 2, y0 + height / 2
        thickness = side * 0.26
        angle = 90.0
        for index, value in enumerate(values):
            sweep = 360.0 * value / total
            c.setStrokeColor(hex_to_color(colors[index % len(colors)]))
            c.setLineWidth(thickness)
            c.arc(cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2,
                  -angle - sweep, sweep)
            angle += sweep
    elif ctype.startswith("COL"):
        peak = max(values) if values else 1.0
        slot = width / max(1, len(values))
        label_h = font_size * 1.5
        for index, value in enumerate(values):
            bar_h = (height - label_h - 6) * (value / peak if peak else 0)
            bx = x0 + slot * index + slot * (gap / 200.0)
            bw = slot * (1 - gap / 100.0)
            c.setFillColor(hex_to_color(colors[index % len(colors)]))
            c.rect(bx, y0 + label_h, bw, bar_h, stroke=0, fill=1)
            if data_labels:
                c.setFont(label_font, font_size)
                c.setFillColor(hex_to_color("#0F172A"))
                c.drawCentredString(bx + bw / 2, y0 + label_h + bar_h + 4, f"{value:g}")
            c.setFont(label_font, font_size)
            c.setFillColor(hex_to_color("#3C4A55"))
            c.drawCentredString(bx + bw / 2, y0 + 3, categories[index] if index < len(categories) else "")
    else:  # horizontal bars
        peak = max(values) if values else 1.0
        slot = height / max(1, len(values))
        for index, value in enumerate(values):
            label = categories[index] if index < len(categories) else ""
            c.setFont(label_font, font_size)
            c.setFillColor(hex_to_color("#3C4A55"))
            label_w = pdfmetrics.stringWidth(label, label_font, font_size)
            bar_x = x0 + label_w + 8
            bar_w = max(2.0, (x0 + width - bar_x - 4)) * (value / peak if peak else 0)
            cy = y0 + slot * (len(values) - index - 1) + slot / 2
            c.drawString(x0 + 2, cy - font_size * 0.32, label)
            c.setFillColor(hex_to_color(colors[index % len(colors)]))
            c.rect(bar_x, cy - slot * 0.22, bar_w, slot * 0.44, stroke=0, fill=1)


# ------------------------------------------------------------------------ tables
def draw_table(c, shape, top_h: float):
    table = shape.table
    left, top = shape.left / EMU_IN * PT_IN, shape.top / EMU_IN * PT_IN
    y_top = top_h - top
    fonts = {True: font_name("Calibri", True, False), False: font_name("Calibri", False, False)}
    widths = [col.width / EMU_IN * PT_IN for col in table.columns]
    heights = [row.height / EMU_IN * PT_IN for row in table.rows]
    y = y_top
    for r, row in enumerate(table.rows):
        x = left
        for cell_index, cell in enumerate(row.cells):
            w, h = widths[cell_index], heights[r]
            box_y = y - h
            try:
                fill = rgb_of(cell.fill.fore_color)
            except Exception:
                fill = "#FFFFFF"
            c.setFillColor(hex_to_color(fill))
            c.rect(x, box_y, w, h, stroke=0, fill=1)
            text = cell.text
            size = 11.0
            for paragraph in cell.text_frame.paragraphs:
                for run in paragraph.runs:
                    if run.font.size:
                        size = run.font.size.pt * PT_IN / 72
            if text:
                c.setFont(fonts[r == 0], size)
                c.setFillColor(hex_to_color("#FFFFFF" if r == 0 else "#3C4A55"))
                c.drawString(x + 5, box_y + h / 2 - size * 0.32, text)
            x += w
        y -= h


# ------------------------------------------------------------------------- main
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("deck", nargs="?", default=str(HERE / "Presentasi-Jurnal-MIH-Lopes-2021.pptx"))
    parser.add_argument("--outdir", default=str(HERE / "audits" / "render"))
    parser.add_argument("--dpi", type=int, default=110)
    parser.add_argument("--fetch-fonts", action="store_true")
    args = parser.parse_args()
    if args.fetch_fonts:
        fetch_fonts()
        return
    register_fonts()
    deck_path = Path(args.deck)
    spec_path = deck_path.with_name("spec.json")
    spec = json.loads(spec_path.read_text(encoding="utf-8")) if spec_path.exists() else {}
    spec_slides = {s["id"]: s for s in spec.get("slides", [])}

    prs = Presentation(str(deck_path))
    slide_w = prs.slide_width / EMU_IN * PT_IN
    slide_h = prs.slide_height / EMU_IN * PT_IN
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / (deck_path.stem + ".pdf")
    c = rl_canvas.Canvas(str(pdf_path), pagesize=(slide_w, slide_h))
    overflow_log: list[dict] = []

    for index, slide in enumerate(prs.slides, start=1):
        sid = spec["slides"][index - 1]["id"] if spec else f"slide{index}"
        bg = "#FFFFFF"
        for shape in slide.shapes:
            if shape.shape_type is not None and str(shape.shape_type).startswith("AUTO_SHAPE") \
                    and shape.width > prs.slide_width * 0.9:
                grad = gradient_stops(shape._element.spPr)
                if grad:
                    bg = grad[0][0][1]      # darkest stop as the clipping reference
                else:
                    try:
                        bg = rgb_of(shape.fill.fore_color)
                    except Exception:
                        pass
                break
        c.setFillColor(hex_to_color(bg))
        c.rect(0, 0, slide_w, slide_h, stroke=0, fill=1)
        chart_specs = []
        if spec:
            objs = spec["slides"][index - 1]["layout_tree"]["objects"]
            chart_specs = [o for o in obj_list(objs) if o["kind"] == "chart"]
        chart_i = 0
        for shape in slide.shapes:
            if shape.shape_type is not None and str(shape.shape_type).startswith("AUTO_SHAPE") \
                    and shape.width > prs.slide_width * 0.9:
                continue
            overflow: list[float] = []
            if getattr(shape, "has_chart", False) and shape.has_chart:
                draw_chart(c, shape, slide_h, bg,
                           chart_specs[chart_i] if chart_i < len(chart_specs) else None)
                chart_i += 1
            elif getattr(shape, "has_table", False) and shape.has_table:
                draw_table(c, shape, slide_h)
            elif shape.shape_type is not None and str(shape.shape_type).startswith("LINE"):
                left = shape.left / EMU_IN * PT_IN
                top = slide_h - shape.top / EMU_IN * PT_IN
                try:
                    colour = rgb_of(shape.line.color)
                    width = max(0.5, shape.line.width.pt * PT_IN / 72)
                except Exception:
                    colour, width = "#000000", 1.0
                c.setStrokeColor(hex_to_color(colour))
                c.setLineWidth(width)
                c.line(left, top, left + shape.width / EMU_IN * PT_IN, top)
            elif shape.shape_type is not None and str(shape.shape_type).startswith("TEXT_BOX"):
                draw_text_frame(c, shape.text_frame,
                                (shape.left / EMU_IN * PT_IN, slide_h - shape.top / EMU_IN * PT_IN
                                 - shape.height / EMU_IN * PT_IN,
                                 shape.left / EMU_IN * PT_IN + shape.width / EMU_IN * PT_IN,
                                 slide_h - shape.top / EMU_IN * PT_IN), bg, overflow)
            else:
                draw_shape(c, shape, bg)
                if shape.has_text_frame and shape.text_frame.text.strip():
                    draw_text_frame(c, shape.text_frame,
                                    (shape.left / EMU_IN * PT_IN,
                                     slide_h - shape.top / EMU_IN * PT_IN - shape.height / EMU_IN * PT_IN,
                                     shape.left / EMU_IN * PT_IN + shape.width / EMU_IN * PT_IN,
                                     slide_h - shape.top / EMU_IN * PT_IN), bg, overflow)
            if overflow:
                snippet = (shape.text_frame.text[:44].replace("\n", " ")
                           if shape.has_text_frame else "")
                overflow_log.append({"slide": sid, "shape": shape.name,
                                     "overflow_in": max(overflow), "text": snippet})
        page = c._pageNumber
        c.setFont(font_name("Calibri", False, False), 6)
        c.setFillColor(hex_to_color("#B9C2C7"))
        c.drawRightString(slide_w - 4, 3, f"{page}/{len(prs.slides.__iter__.__self__._sldIdLst)}")
        c.showPage()
    c.save()

    doc = pymupdf.open(pdf_path)
    zoom = args.dpi / 72.0
    images = []
    for page in doc:
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        out = out_dir / f"slide-{page.number + 1:02d}.png"
        pix.save(out)
        images.append(out)
    doc.close()

    cols, rows, w, h = 4, 2, 700, 394
    from PIL import Image

    for sheet_index in range(0, len(images), cols * rows):
        batch = images[sheet_index:sheet_index + cols * rows]
        sheet = Image.new("RGB", (cols * w, rows * h), "#20262B")
        for i, path in enumerate(batch):
            sheet.paste(Image.open(path).resize((w, h)), ((i % cols) * w, (i // cols) * h))
        sheet.save(out_dir / f"sheet-{sheet_index // (cols * rows) + 1}.png")

    if UNMAPPED:
        print(f"WARNING: unmapped font names fell back to LC-Sans: {sorted(UNMAPPED)}")
    if MISSING_FONTS:
        print("WARNING: preview fonts missing, fell back to base-14 fonts "
              "(run `python3 render_deck.py --fetch-fonts`)")
    print(f"rendered {len(images)} slides -> {out_dir} (pdf: {pdf_path.name}, dpi {args.dpi})")
    if overflow_log:
        print(f"text overflow detected on {len(overflow_log)} frames:")
        for item in overflow_log[:12]:
            print(f"  {item['slide']:<24} +{item['overflow_in']} in :: {item.get('text', '')!r}")
    else:
        print("no text overflow detected")


def obj_list(objs: dict) -> list[dict]:
    return sorted(objs.values(), key=lambda o: o["z_index"])


if __name__ == "__main__":
    main()
