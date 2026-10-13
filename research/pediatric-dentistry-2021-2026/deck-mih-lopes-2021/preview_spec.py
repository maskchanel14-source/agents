#!/usr/bin/env python3
"""Approximate layout preview for spec.json (audit aid, not a deliverable).

Draws text, shapes, charts and tables with Pillow so a human can eyeball hierarchy,
spacing and clipping without a presentation renderer. Charts are re-drawn
approximately from their data. Fonts differ from PowerPoint (DejaVu here, Calibri in
the deck) and DejaVu runs wider, so a fit here is a conservative fit in the deck.
Text that overflows its box is painted red.

Output: audits/preview/slide-XX.png plus two contact sheets.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DPI = 96
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
OVERFLOW = "#B91C1C"


def px(inches: float) -> int:
    return int(round(inches * DPI))


def font_for(path: str, pt: float):
    return ImageFont.truetype(path, max(6, int(round(pt * DPI / 72))))


def rgba(value: str, alpha: float = 100) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16),
            int(round(255 * alpha / 100)))


def wrap(draw, text, font, max_width):
    lines, current = [], ""
    for word in text.split(" "):
        candidate = f"{current} {word}".strip()
        if not current or draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_text(base, obj, draw):
    b, style = obj["bbox"], obj["style"]
    box = [px(b["x"]), px(b["y"]), px(b["x"] + b["width"]), px(b["y"] + b["height"])]
    path = FONT_MONO if style.get("font") == "Consolas" else (
        FONT_BOLD if style.get("bold") else FONT_REG)
    font = font_for(path, style.get("font_size", 12))
    max_w = max(10, box[2] - box[0])
    lines: list[str] = []
    for raw in obj["content"]["text"].split("\n"):
        lines.extend(wrap(draw, raw, font, max_w) if raw else [""])
    line_h = int(round(style.get("font_size", 12) * 1.30 * DPI / 72))
    total = line_h * len(lines)
    if style.get("anchor") == "middle":
        y = box[1] + (box[3] - box[1] - total) // 2
    elif style.get("anchor") == "bottom":
        y = box[3] - total
    else:
        y = box[1]
    over = total > (box[3] - box[1] + 5)
    color = rgba(OVERFLOW if over else style.get("color", "#334155"))
    for line in lines:
        width = draw.textlength(line, font=font)
        if style.get("align") == "center":
            x = box[0] + (max_w - width) / 2
        elif style.get("align") == "right":
            x = box[2] - width
        else:
            x = box[0]
        draw.text((x, y), line, font=font, fill=color)
        y += line_h


def draw_shape(layer, obj, draw):
    b, style = obj["bbox"], obj["style"]
    box = [px(b["x"]), px(b["y"]), px(b["x"] + b["width"]), px(b["y"] + b["height"])]
    alpha = float(style.get("alpha", 100))
    fill = rgba(style.get("fill", "#FFFFFF"), alpha)
    outline = None if float(style.get("line_width", 0)) <= 0 else rgba(
        style.get("line_color", "#CBD5E1"), alpha)
    width = max(1, int(round(float(style.get("line_width", 0)) * DPI / 72)))
    kind = obj["content"].get("shape", "rectangle")
    if kind == "oval":
        draw.ellipse(box, fill=fill, outline=outline, width=width)
    elif kind == "right_arrow":
        x0, y0, x1, y1 = box
        mid = (y0 + y1) / 2
        draw.polygon([(x0, y0), (x1 - (x1 - x0) * 0.45, y0), (x1 - (x1 - x0) * 0.45, y0 - (y1 - y0) * 0.35),
                      (x1, mid), (x1 - (x1 - x0) * 0.45, y1 + (y1 - y0) * 0.35),
                      (x1 - (x1 - x0) * 0.45, y1), (x0, y1)], fill=fill)
    elif kind == "rounded_rectangle":
        draw.rounded_rectangle(box, radius=max(1, px(style.get("radius", 0.05))), fill=fill,
                               outline=outline, width=width)
    else:
        draw.rectangle(box, fill=fill, outline=outline, width=width)


def draw_chart(base, obj, draw):
    b, content, style = obj["bbox"], obj["content"], obj["style"]
    x0, y0, x1, y1 = px(b["x"]), px(b["y"]), px(b["x"] + b["width"]), px(b["y"] + b["height"])
    font = font_for(FONT_REG, content.get("font_size", 10.5))
    colors = content.get("colors") or ["#0E7490"]
    kind = content["chart_type"]
    draw.rectangle([x0, y0, x1, y1], outline=rgba("#E3E8EB"), width=1)
    if kind in ("col", "bar"):
        cats, vals = content["categories"], content["values"]
        peak = max(vals) or 1
        if kind == "col":
            slot = (x1 - x0) / len(cats)
            label_h = int(round(20 * DPI / 72))
            for i, (cat, val) in enumerate(zip(cats, vals)):
                cx = x0 + slot * i
                bar_h = (y1 - y0 - label_h - 8) * (val / peak)
                fill = rgba(colors[i % len(colors)])
                draw.rectangle([cx + slot * 0.26, y1 - label_h - bar_h, cx + slot * 0.74, y1 - label_h],
                               fill=fill)
                if content.get("data_labels"):
                    text = str(val)
                    w = draw.textlength(text, font=font)
                    draw.text((cx + slot / 2 - w / 2, y1 - label_h - bar_h - 16),
                              text, font=font, fill=rgba("#0F172A"))
                w = draw.textlength(cat, font=font)
                draw.text((cx + slot / 2 - w / 2, y1 - label_h + 3), cat, font=font,
                          fill=rgba("#3C4A55"))
        else:
            slot = (y1 - y0) / len(cats)
            for i, (cat, val) in enumerate(zip(cats, vals)):
                cy = y0 + slot * i
                w = draw.textlength(cat, font=font)
                draw.text((x0 + 4, cy + slot / 2 - 8), cat, font=font, fill=rgba("#3C4A55"))
                bar_x0 = x0 + 4 + w + 8
                bar_w = max(3, (x1 - bar_x0 - 6) * (val / peak))
                draw.rectangle([bar_x0, cy + slot * 0.28, bar_x0 + bar_w, cy + slot * 0.72],
                               fill=rgba(colors[i % len(colors)]))
    else:  # doughnut
        vals = content["values"]
        total = sum(vals) or 1
        side = min(x1 - x0, y1 - y0) - 10
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        box = [cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2]
        start = -90
        for i, val in enumerate(vals):
            end = start + 360 * val / total
            draw.arc(box, start=start, end=end, fill=rgba(colors[i % len(colors)]),
                     width=int(side * 0.26))
            start = end


def draw_table(draw, obj):
    b, content, style = obj["bbox"], obj["content"], obj["style"]
    rows = [content["header"]] + content["rows"]
    row_h = style.get("row_height", 0.3)
    font_h = font_for(FONT_BOLD, style["header_size"])
    font_b = font_for(FONT_REG, style["body_size"])
    y = b["y"]
    for r, row in enumerate(rows):
        x = b["x"]
        for c, value in enumerate(row):
            w = style["col_widths"][c]
            box = [px(x), px(y), px(x + w), px(y + row_h)]
            draw.rectangle(box, fill=rgba(style["header_fill"] if r == 0 else
                                          (style["band_fill"] if r % 2 == 0 else "#FFFFFF")),
                           outline=rgba(style["line_color"]))
            draw.text((box[0] + 6, box[1] + 5), value, font=font_h if r == 0 else font_b,
                      fill=rgba(style["header_color"] if r == 0 else "#334155"))
            x += w
        y += row_h


def main() -> None:
    spec = json.loads((HERE / "spec.json").read_text(encoding="utf-8"))
    out_dir = HERE / "audits" / "preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    size_in = spec["slides"][0]["layout_tree"]["slide_size"]
    for index, slide in enumerate(spec["slides"], start=1):
        base = Image.new("RGBA", (px(size_in["width"]), px(size_in["height"])), rgba("#F6F8F9"))
        objs = sorted(slide["layout_tree"]["objects"].values(), key=lambda o: (o["z_index"], o["id"]))
        for obj in objs:
            alpha = float(obj["style"].get("alpha", 100)) if obj["kind"] == "shape" else 100
            if alpha < 100:
                layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
                draw_shape(layer, obj, ImageDraw.Draw(layer))
                base = Image.alpha_composite(base, layer)
                continue
            draw = ImageDraw.Draw(base)
            if obj["kind"] == "text":
                draw_text(base, obj, draw)
            elif obj["kind"] == "shape":
                draw_shape(base, obj, draw)
            elif obj["kind"] == "chart":
                draw_chart(base, obj, draw)
            elif obj["kind"] == "table":
                draw_table(draw, obj)
            elif obj["kind"] == "line":
                b = obj["bbox"]
                draw.line([px(b["x"]), px(b["y"]), px(b["x"] + b["width"]), px(b["y"])],
                          fill=rgba(obj["style"].get("color", "#0E7490")),
                          width=max(2, int(obj["style"].get("width", 1.5))))
        base.convert("RGB").save(out_dir / f"slide-{index:02d}.png")
    names = sorted(out_dir.glob("slide-*.png"))
    cols, rows, w, h = 4, 2, 700, 394
    for page in range(2):
        sheet = Image.new("RGB", (cols * w, rows * h), "#0F172A")
        for i, name in enumerate(names[page * cols * rows:(page + 1) * cols * rows]):
            sheet.paste(Image.open(name).resize((w, h)), ((i % cols) * w, (i // cols) * h))
        sheet.save(out_dir / f"sheet-{page + 1}.png")
    print(f"preview written to {out_dir.relative_to(HERE)} ({len(names)} slides + 2 sheets)")


if __name__ == "__main__":
    main()
