#!/usr/bin/env python3
"""Build the PPTX from spec.json. Pure coordinate mapping: no layout decisions here.

Every position, size, style, and z-index comes from the specification; this script
only translates inches to EMU and applies the declared styles. It also writes a
build record so the deck, spec, and audits stay together.

Usage:  python3 build_deck.py [spec.json] [out.pptx]
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "Presentasi-Jurnal-MIH-Lopes-2021.pptx"

ANCHORS = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}
ALIGNS = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}
SHAPES = {"rectangle": MSO_SHAPE.RECTANGLE, "rounded_rectangle": MSO_SHAPE.ROUNDED_RECTANGLE,
          "oval": MSO_SHAPE.OVAL, "right_arrow": MSO_SHAPE.RIGHT_ARROW,
          "isosceles_triangle": MSO_SHAPE.ISOSCELES_TRIANGLE, "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE,
          "round2same": MSO_SHAPE.ROUND_2_SAME_RECTANGLE, "arc": MSO_SHAPE.ARC,
          "block_arc": MSO_SHAPE.BLOCK_ARC}
CHARTS = {"col": XL_CHART_TYPE.COLUMN_CLUSTERED, "bar": XL_CHART_TYPE.BAR_CLUSTERED,
          "doughnut": XL_CHART_TYPE.DOUGHNUT, "pie": XL_CHART_TYPE.PIE}


def rgb(value: str) -> RGBColor:
    value = value.lstrip("#")
    return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def no_shadow(shape) -> None:
    try:
        shape.shadow.inherit = False
    except Exception:  # connectors and some shapes have no shadow interface
        pass


def apply_alpha(color_element, alpha: float) -> None:
    """Set transparency on an srgbClr element (100 = opaque, 0 = invisible)."""
    if alpha >= 100:
        return
    node = color_element.find(qn("a:alpha"))
    if node is None:
        node = etree.SubElement(color_element, qn("a:alpha"))
    node.set("val", str(int(max(0, alpha) * 1000)))


def set_lang(run, lang: str) -> None:
    rpr = run._r.get_or_add_rPr()
    rpr.set("lang", lang)


def style_text_frame(tf, style: dict, lang: str, body_size_default: float | None = None) -> None:
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = Inches(style.get("inset_left", 0.05))
    tf.margin_right = Inches(style.get("inset_right", 0.05))
    tf.margin_top = Inches(style.get("inset_top", 0.02))
    tf.margin_bottom = Inches(style.get("inset_bottom", 0.02))
    tf.vertical_anchor = ANCHORS.get(style.get("anchor", "top"), MSO_ANCHOR.TOP)


def fill_paragraph(paragraph, text: str, style: dict, lang: str) -> None:
    paragraph.alignment = ALIGNS.get(style.get("align", "left"), PP_ALIGN.LEFT)
    if style.get("line_spacing"):
        paragraph.line_spacing = float(style["line_spacing"])
    paragraph.space_after = Pt(style.get("space_after_pt", 0))
    paragraph.space_before = Pt(style.get("space_before_pt", 0))
    run = paragraph.add_run()
    run.text = text
    font = run.font
    font.name = style.get("font", "Calibri")
    font.size = Pt(style.get("font_size", 12))
    font.bold = bool(style.get("bold", False))
    font.italic = bool(style.get("italic", False))
    font.color.rgb = rgb(style.get("color", "#334155"))
    if style.get("spc"):
        run.font._rPr.set("spc", str(int(style["spc"])))
    set_lang(run, lang)


def add_text(slide, o):
    b = o["bbox"]
    box = slide.shapes.add_textbox(Inches(b["x"]), Inches(b["y"]), Inches(b["width"]), Inches(b["height"]))
    tf = box.text_frame
    style_text_frame(tf, o["style"], "id-ID")
    lines = o["content"]["text"].split("\n")
    for index, line in enumerate(lines):
        paragraph = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        fill_paragraph(paragraph, line, o["style"], "id-ID")
    return box


def add_shape_like(slide, o):
    b = o["bbox"]
    shape_type = SHAPES[o["content"].get("shape", "rectangle")]
    shape = slide.shapes.add_shape(shape_type, Inches(b["x"]), Inches(b["y"]),
                                   Inches(b["width"]), Inches(b["height"]))
    style = o["style"]
    if shape_type == MSO_SHAPE.ROUNDED_RECTANGLE:
        radius = float(style.get("radius", 0.06))
        shape.adjustments[0] = max(0.0, min(0.5, radius / max(0.01, min(b["width"], b["height"]))))
    if style.get("gradient"):
        stops = style["gradient"]
        shape.fill.gradient()
        gradient_stops = shape.fill.gradient_stops
        gradient_stops[0].color.rgb = rgb(stops[0])
        gradient_stops[0].position = 0.0
        gradient_stops[1].color.rgb = rgb(stops[1])
        gradient_stops[1].position = 1.0
        shape.fill.gradient_angle = float(style.get("gradient_angle", 45.0))
        alphas = style.get("gradient_alpha")
        if alphas:
            grad_fill = shape._element.spPr.find(qn("a:gradFill"))
            gs_list = grad_fill.find(qn("a:gsLst")) if grad_fill is not None else None
            if gs_list is not None:
                stops = gs_list.findall(qn("a:gs"))
                for stop, value in zip(stops, alphas):
                    clr = stop.find(qn("a:srgbClr"))
                    if clr is not None:
                        apply_alpha(clr, float(value))
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(style.get("fill", "#FFFFFF"))
        apply_alpha(shape.fill.fore_color._xFill.find(qn("a:srgbClr")),
                    float(style.get("alpha", 100)))
    if float(style.get("rotation", 0.0)):
        shape.rotation = float(style["rotation"])
    if float(style.get("line_width", 1)) <= 0:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = rgb(style.get("line_color", "#CBD5E1"))
        shape.line.width = Pt(float(style.get("line_width", 1)))
        apply_alpha(shape.line.color._xFill.find(qn("a:srgbClr")), float(style.get("alpha", 100)))
    no_shadow(shape)
    if shape.has_text_frame:
        shape.text_frame.text = ""
    return shape


def add_picture(slide, o):
    b = o["bbox"]
    path = (HERE / o["content"]["path"]).resolve()
    if not path.exists():
        raise SystemExit(f"missing asset for {o['id']}: {path}")
    picture = slide.shapes.add_picture(str(path), Inches(b["x"]), Inches(b["y"]),
                                       Inches(b["width"]), Inches(b["height"]))
    return picture


def add_line(slide, o):
    b = o["bbox"]
    x1, y1, x2, y2 = o["content"]["x1"], o["content"]["y1"], o["content"]["x2"], o["content"]["y2"]
    left, top = min(x1, x2), min(y1, y2)
    width, height = abs(x2 - x1), abs(y2 - y1)
    connector = slide.shapes.add_connector(1, Inches(left), Inches(top),
                                           Inches(left + max(width, 0.001)), Inches(top + max(height, 0.001)))
    connector.line.color.rgb = rgb(o["style"].get("color", "#0E7490"))
    connector.line.width = Pt(float(o["style"].get("width", 1.5)))
    return connector


def add_table(slide, o):
    b = o["bbox"]
    content = o["content"]
    rows = len(content["rows"]) + 1
    cols = len(content["header"])
    shape = slide.shapes.add_table(rows, cols, Inches(b["x"]), Inches(b["y"]),
                                   Inches(b["width"]), Inches(b["height"]))
    table = shape.table
    style = o["style"]
    for index, width in enumerate(style["col_widths"]):
        table.columns[index].width = Inches(width)
    for index in range(rows):
        table.rows[index].height = Inches(style.get("row_height", 0.3))

    data = [content["header"]] + content["rows"]
    for r, row in enumerate(data):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.02)
            cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            if r == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = rgb(style["header_fill"])
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = rgb(style["band_fill"] if r % 2 == 0 else "#FFFFFF")
            tf = cell.text_frame
            tf.word_wrap = True
            paragraph = tf.paragraphs[0]
            align = PP_ALIGN.LEFT if c == len(row) - 1 else PP_ALIGN.LEFT
            paragraph.alignment = align
            run = paragraph.add_run()
            run.text = value
            run.font.name = "Calibri"
            run.font.size = Pt(style["header_size"] if r == 0 else style["body_size"])
            run.font.bold = r == 0
            run.font.color.rgb = rgb(style["header_color"] if r == 0 else "#334155")
            set_lang(run, "id-ID")
    # remove banded-row / first-column styling so explicit fills win visually
    tbl_pr = table._tbl.find(qn("a:tblPr"))
    if tbl_pr is not None:
        tbl_pr.set("bandRow", "0")
        tbl_pr.set("firstRow", "1")
    return shape


def add_chart(slide, o):
    content, style, b = o["content"], o["style"], o["bbox"]
    chart_type = CHARTS[content["chart_type"]]
    data = CategoryChartData()
    data.categories = content["categories"]
    data.add_series(content.get("series_name", "nilai"), tuple(content["values"]))
    frame = slide.shapes.add_chart(chart_type, Inches(b["x"]), Inches(b["y"]),
                                   Inches(b["width"]), Inches(b["height"]), data)
    chart = frame.chart
    chart.has_title = False
    chart.has_legend = False
    chart.font.name = style.get("font", "Calibri")
    chart.font.size = Pt(float(content.get("font_size", 10.5)))
    chart.font.color.rgb = rgb(style.get("color", "#334155"))

    plot = chart.plots[0]
    colors = content.get("colors") or ["#0E7490"]
    series = plot.series[0]
    points = list(getattr(series, "points", []))
    if points:
        for index, point in enumerate(points):
            point.format.fill.solid()
            point.format.fill.fore_color.rgb = rgb(colors[index % len(colors)])
    else:
        series.format.fill.solid()
        series.format.fill.fore_color.rgb = rgb(colors[0])

    if content.get("gap_width") and hasattr(plot, "gap_width"):
        plot.gap_width = int(content["gap_width"])
    if content.get("data_labels"):
        plot.has_data_labels = True
        labels = plot.data_labels
        labels.number_format = content.get("label_format", '0.0"%"')
        labels.number_format_is_linked = False
        labels.font.size = Pt(float(content.get("font_size", 10.5)))
        labels.font.bold = True
        labels.font.name = style.get("font", "Calibri")
        labels.font.color.rgb = rgb("#0F172A")
        if content["chart_type"] in ("col", "bar"):
            labels.position = XL_LABEL_POSITION.OUTSIDE_END
    if hasattr(plot, "has_data_labels") and not content.get("data_labels"):
        plot.has_data_labels = False

    if content["chart_type"] in ("col", "bar"):
        value_axis = chart.value_axis
        value_axis.visible = bool(content.get("show_value_axis"))
        value_axis.has_major_gridlines = False
        category_axis = chart.category_axis
        category_axis.has_major_gridlines = False
        category_axis.tick_labels.font.size = Pt(float(content.get("font_size", 10.5)))
        category_axis.tick_labels.font.color.rgb = rgb(style.get("color", "#334155"))
        if not content.get("axis_labels"):
            category_axis.visible = False
    return frame


BUILDERS = {"text": add_text, "shape": add_shape_like, "line": add_line, "table": add_table,
            "chart": add_chart, "picture": add_picture}


def main() -> None:
    spec_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "spec.json"
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    prs = Presentation()
    prs.slide_width = Inches(spec["slides"][0]["layout_tree"]["slide_size"]["width"])
    prs.slide_height = Inches(spec["slides"][0]["layout_tree"]["slide_size"]["height"])
    prs.core_properties.title = spec["summary"]["accessibility"]["presentation_title"]
    prs.core_properties.language = "id-ID"
    prs.core_properties.subject = spec["summary"]["deck_title"]
    prs.core_properties.comments = "Dibangun dari spec.json oleh build_deck.py (skill pptx-deck-creation)."
    prs.core_properties.author = "Arena Agent"

    record = {"built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "spec": spec_path.name, "output": out_path.name, "slides": []}

    for slide_spec in spec["slides"]:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        tree = slide_spec["layout_tree"]
        objects = sorted(tree["objects"].values(), key=lambda o: (o["z_index"], o["id"]))
        placed = []
        for o in objects:
            b = o["bbox"]
            if b["width"] <= 0 or b["height"] <= 0:
                raise SystemExit(f"non-positive geometry on {slide_spec['id']}:{o['id']}")
            builder = BUILDERS.get(o["kind"])
            if builder is None:
                raise SystemExit(f"unsupported kind {o['kind']} on {o['id']}")
            shape = builder(slide, o)
            if o.get("alt_text") and hasattr(shape, "name"):
                shape.name = o["alt_text"]
            placed.append({"object_id": o["id"], "kind": o["kind"], "z_index": o["z_index"]})
        notes = slide_spec.get("notes", "").strip()
        if notes:
            notes_frame = slide.notes_slide.notes_text_frame
            notes_frame.text = notes
            for paragraph in notes_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(12)
                    run.font.name = "Calibri"
            record_notes = len(notes)
        else:
            record_notes = 0
        record["slides"].append({"slide_id": slide_spec["id"], "objects": placed,
                                 "notes_chars": record_notes})

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)
    (HERE / "build_record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    total = sum(len(s["objects"]) for s in record["slides"])
    print(f"built {out_path.name}: {len(record['slides'])} slides, {total} objects")


if __name__ == "__main__":
    main()
