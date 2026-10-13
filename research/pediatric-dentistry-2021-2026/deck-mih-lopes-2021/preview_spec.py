#!/usr/bin/env python3
"""Task-local approximate preview renderer (audit aid, not a deliverable).

Draws spec.json with Pillow so a human can eyeball hierarchy, spacing, and clipping
without installing a presentation renderer. Fonts differ from PowerPoint, so treat
the images as a layout check only. Output: audits/preview/slide-XX.png
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DPI = 96
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_ITAL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # oblique face not installed


def px(inches: float) -> int:
    return int(round(inches * DPI))


def scaled(font_path: str, pt: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(font_path, max(7, int(round(pt * DPI / 72))))


def wrap(draw, text, font, max_width):
    words, lines, current = text.split(" "), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def main() -> None:
    spec = json.loads((HERE / "spec.json").read_text(encoding="utf-8"))
    out_dir = HERE / "audits" / "preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    for index, slide in enumerate(spec["slides"], start=1):
        size = slide["layout_tree"]["slide_size"]
        img = Image.new("RGB", (px(size["width"]), px(size["height"])), "#F8FAFC")
        draw = ImageDraw.Draw(img)
        for obj in sorted(slide["layout_tree"]["objects"].values(), key=lambda o: o["z_index"]):
            b, style, kind = obj["bbox"], obj["style"], obj["kind"]
            box = [px(b["x"]), px(b["y"]), px(b["x"] + b["width"]), px(b["y"] + b["height"])]
            if kind == "shape":
                fill = style.get("fill", "#FFFFFF")
                outline = style.get("line_color", fill)
                radius = px(style.get("radius", 0.05))
                if "rounded" in obj["content"].get("shape", ""):
                    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline,
                                           width=max(1, int(style.get("line_width", 1))))
                else:
                    draw.rectangle(box, fill=fill, outline=outline)
            elif kind == "line":
                draw.line([box[0], box[1], box[2], box[1]], fill=style.get("color", "#0E7490"),
                          width=max(2, int(style.get("width", 1.5) * 1.6)))
            elif kind == "table":
                rows = [obj["content"]["header"]] + obj["content"]["rows"]
                widths = [px(w) for w in style["col_widths"]]
                header_h = px(style.get("row_height", 0.3))
                y = box[1]
                for r, row in enumerate(rows):
                    h = header_h if r == 0 else px(style.get("row_height", 0.3))
                    x = box[0]
                    for c, value in enumerate(row):
                        cell = [x, y, x + widths[c], y + h]
                        draw.rectangle(cell, fill=style["header_fill"] if r == 0 else
                                       (style["band_fill"] if r % 2 == 0 else "#FFFFFF"),
                                       outline=style["line_color"])
                        color = style["header_color"] if r == 0 else "#334155"
                        f = scaled(FONT_BOLD if r == 0 else FONT_REG,
                                   style["header_size"] if r == 0 else style["body_size"])
                        draw.text((x + 6, y + 5), value, font=f, fill=color)
                        x += widths[c]
                    y += h
            elif kind == "text":
                path = FONT_BOLD if style.get("bold") else (FONT_ITAL if style.get("italic") else FONT_REG)
                font = scaled(path, style.get("font_size", 12))
                color = style.get("color", "#334155")
                max_w = box[2] - box[0]
                lines: list[str] = []
                for raw in obj["content"]["text"].split("\n"):
                    lines.extend(wrap(draw, raw, font, max_w) if raw else [""])
                line_h = int(round(style.get("font_size", 12) * 1.28 * DPI / 72))
                total_h = line_h * len(lines)
                if style.get("anchor") == "middle":
                    y = box[1] + (box[3] - box[1] - total_h) // 2
                elif style.get("anchor") == "bottom":
                    y = box[3] - total_h
                else:
                    y = box[1]
                for line in lines:
                    width = draw.textlength(line, font=font)
                    if style.get("align") == "center":
                        x = box[0] + (max_w - width) / 2
                    elif style.get("align") == "right":
                        x = box[2] - width
                    else:
                        x = box[0]
                    clipped = total_h > (box[3] - box[1] + 4)
                    draw.text((x, y), line, font=font, fill="#B91C1C" if clipped else color)
                    y += line_h
        img.save(out_dir / f"slide-{index:02d}.png")
    print(f"preview written to {out_dir.relative_to(HERE)} ({len(spec['slides'])} images)")


if __name__ == "__main__":
    main()
