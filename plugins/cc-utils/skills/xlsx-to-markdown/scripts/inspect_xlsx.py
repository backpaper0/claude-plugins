#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""xlsxファイルの内容をMarkdown化する際の下調べに使う補助ツール。

事前に `unzip <file>.xlsx -d <dir>` などでxlsxを展開しておき、
展開先ディレクトリ（`xl/` を含むディレクトリ）を第1引数の `xlsx_dir` に渡して使う。

サブコマンド:
  sheets                     シート一覧（可視/非表示、対応する図形描画パート）を表示
  grid   <sheet> [--all]     シート全体を行番号付きでダンプ（既定では空行を省略）
  cells  <sheet> <r1> <r2>   指定した行範囲のセルを「セル参照: 値」形式で列挙し、
                             範囲にかかる結合セル（マージ）情報も表示する
  shapes <sheet>             シートに紐づく描画（図形・テキストボックス・画像）を
                             アンカー位置（行・列）とテキストの一覧として表示する

いずれもテキスト抽出時、ふりがな（拼音/読み仮名用の <rPh> 要素）を除外して
本来の文字列だけを取り出す。
"""

import argparse
import os
import re
import xml.etree.ElementTree as ET

NS = {
    "x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def col_to_idx(col):
    idx = 0
    for c in col:
        idx = idx * 26 + (ord(c) - ord("A") + 1)
    return idx


def parse_ref(ref):
    m = re.match(r"([A-Z]+)(\d+)", ref)
    assert m is not None
    return col_to_idx(m.group(1)), int(m.group(2))


def load_rels(path):
    """rels XMLを {Id: Target} の辞書として読む。存在しなければ空辞書。"""
    if not os.path.exists(path):
        return {}
    tree = ET.parse(path)
    return {
        rel.get("Id"): rel.get("Target")
        for rel in tree.getroot().findall("rel:Relationship", NS)
    }


def load_sheets(xlsx_dir):
    """workbook.xmlとそのrelsから、シート名・可視状態・シートXMLパスの一覧を返す。"""
    tree = ET.parse(os.path.join(xlsx_dir, "xl", "workbook.xml"))
    rels = load_rels(os.path.join(xlsx_dir, "xl", "_rels", "workbook.xml.rels"))
    sheets = []
    sheets_el = tree.getroot().find("x:sheets", NS)
    assert sheets_el is not None
    for sheet_el in sheets_el:
        rid = sheet_el.get(R_ID)
        target = rels.get(rid, "")
        sheet_path = os.path.normpath(os.path.join(xlsx_dir, "xl", target))
        sheets.append(
            {
                "name": sheet_el.get("name"),
                "state": sheet_el.get("state", "visible"),
                "path": sheet_path,
                "rels_path": os.path.join(
                    os.path.dirname(sheet_path),
                    "_rels",
                    os.path.basename(sheet_path) + ".rels",
                ),
            }
        )
    return sheets


def find_sheet(xlsx_dir, name_or_index):
    sheets = load_sheets(xlsx_dir)
    if name_or_index.isdigit():
        return sheets[int(name_or_index)]
    for s in sheets:
        if s["name"] == name_or_index:
            return s
    raise SystemExit(
        f"シートが見つかりません: {name_or_index!r} "
        f"(候補: {[s['name'] for s in sheets]})"
    )


def sheet_drawing_path(sheet):
    """シートに紐づく描画パート(drawingN.xml)のパスを返す。無ければNone。"""
    rels = load_rels(sheet["rels_path"])
    for target in rels.values():
        if "drawing" in target and target.endswith(".xml"):
            return os.path.normpath(
                os.path.join(os.path.dirname(sheet["path"]), target)
            )
    return None


def load_shared_strings(xlsx_dir):
    """sharedStrings.xmlから文字列一覧を読む。<rPh>（ふりがな）は除外する。"""
    path = os.path.join(xlsx_dir, "xl", "sharedStrings.xml")
    if not os.path.exists(path):
        return []
    root = ET.parse(path).getroot()
    strings = []
    for si in root.findall("x:si", NS):
        strings.append(_extract_text(si))
    return strings


def _extract_text(el):
    """<si>または<is>要素から、直下の<t>とrun(<r><t>)のテキストだけを連結する。
    <rPh>配下の<t>（ふりがな）は無視する。
    """
    parts = []
    direct_t = el.find("x:t", NS)
    if direct_t is not None:
        parts.append(direct_t.text or "")
    for r_el in el.findall("x:r", NS):
        t_el = r_el.find("x:t", NS)
        if t_el is not None:
            parts.append(t_el.text or "")
    return "".join(parts)


def load_grid(xlsx_dir, sheet):
    shared = load_shared_strings(xlsx_dir)
    tree = ET.parse(sheet["path"])
    root = tree.getroot()
    grid = {}
    max_row = max_col = 0
    for row_el in root.findall(".//x:sheetData/x:row", NS):
        for c_el in row_el.findall("x:c", NS):
            ref = c_el.get("r")
            col, row = parse_ref(ref)
            t = c_el.get("t")
            v_el = c_el.find("x:v", NS)
            is_el = c_el.find("x:is", NS)
            val = ""
            if is_el is not None:
                val = _extract_text(is_el)
            elif v_el is not None:
                if t == "s":
                    idx = int(v_el.text or 0)
                    val = shared[idx] if idx < len(shared) else ""
                else:
                    val = v_el.text or ""
            grid[(row, col)] = val
            max_col = max(max_col, col)
            max_row = max(max_row, row)
    merges = []
    mc = root.find(".//x:mergeCells", NS)
    if mc is not None:
        for m in mc.findall("x:mergeCell", NS):
            ref = m.get("ref")
            assert ref is not None
            start, end = ref.split(":") if ":" in ref else (ref, ref)
            c1, r1 = parse_ref(start)
            c2, r2 = parse_ref(end)
            merges.append((r1, c1, r2, c2))
    return grid, max_row, max_col, merges


def cmd_sheets(args):
    for s in load_sheets(args.xlsx_dir):
        drawing = sheet_drawing_path(s)
        drawing_note = (
            f" drawing={os.path.relpath(drawing, args.xlsx_dir)}" if drawing else ""
        )
        print(
            f"{s['name']}\tstate={s['state']}\t{os.path.relpath(s['path'], args.xlsx_dir)}{drawing_note}"
        )


def cmd_grid(args):
    sheet = find_sheet(args.xlsx_dir, args.sheet)
    grid, max_row, max_col, merges = load_grid(args.xlsx_dir, sheet)
    print(
        f"# sheet={sheet['name']} max_row={max_row} max_col={max_col} merges={len(merges)}"
    )
    for r in range(1, max_row + 1):
        row_vals = [grid.get((r, c), "") for c in range(1, max_col + 1)]
        if args.all or any(row_vals):
            print(f"{r}\t" + "|".join(row_vals))


def cmd_cells(args):
    sheet = find_sheet(args.xlsx_dir, args.sheet)
    grid, _max_row, max_col, merges = load_grid(args.xlsx_dir, sheet)
    r1, r2 = args.row_start, args.row_end
    print("MERGES in range:")
    for mr1, mc1, mr2, mc2 in merges:
        if mr1 <= r2 and mr2 >= r1:
            print(f"  rows {mr1}-{mr2} cols {mc1}-{mc2}")
    print("CELLS:")
    for r in range(r1, r2 + 1):
        for c in range(1, max_col + 1):
            v = grid.get((r, c), "")
            if v:
                print(f"  r{r}c{c}: {v!r}")


def cmd_shapes(args):
    sheet = find_sheet(args.xlsx_dir, args.sheet)
    drawing_path = sheet_drawing_path(sheet)
    if not drawing_path or not os.path.exists(drawing_path):
        print("(このシートに紐づく描画パートはありません)")
        return
    drawing_rels = load_rels(
        os.path.join(
            os.path.dirname(drawing_path),
            "_rels",
            os.path.basename(drawing_path) + ".rels",
        )
    )
    root = ET.parse(drawing_path).getroot()
    for anchor in root:
        tag = anchor.tag.split("}")[1]
        if tag not in ("twoCellAnchor", "oneCellAnchor"):
            continue
        frm = anchor.find("xdr:from", NS)
        row_el = frm.find("xdr:row", NS) if frm is not None else None
        col_el = frm.find("xdr:col", NS) if frm is not None else None
        frow = int(row_el.text) if row_el is not None and row_el.text else -1
        fcol = int(col_el.text) if col_el is not None and col_el.text else -1
        name_el = anchor.find(".//xdr:cNvPr", NS)
        name = name_el.get("name") if name_el is not None else "?"
        texts = [
            t.text for t in anchor.findall(".//a:t", NS) if t.text and t.text.strip()
        ]

        pic = anchor.find(".//xdr:pic", NS)
        pic_note = ""
        if pic is not None:
            blip = pic.find(".//a:blip", NS)
            if blip is not None:
                rid = blip.get(R_ID)
                target = drawing_rels.get(rid)
                if target:
                    media_path = os.path.normpath(
                        os.path.join(os.path.dirname(drawing_path), target)
                    )
                    pic_note = (
                        f" [PICTURE -> {os.path.relpath(media_path, args.xlsx_dir)}]"
                    )

        if texts or pic_note:
            print(f"row={frow:5d} col={fcol:3d} name={name}{pic_note} text={texts}")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "xlsx_dir", help="unzip済みのxlsx展開先ディレクトリ（xl/を含む）"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("sheets", help="シート一覧を表示")

    p_grid = sub.add_parser("grid", help="シート全体を行番号付きでダンプ")
    p_grid.add_argument("sheet", help="シート名またはインデックス（0始まり）")
    p_grid.add_argument("--all", action="store_true", help="空行も含めて全行出力する")

    p_cells = sub.add_parser("cells", help="行範囲のセルとマージ情報を表示")
    p_cells.add_argument("sheet", help="シート名またはインデックス（0始まり）")
    p_cells.add_argument("row_start", type=int)
    p_cells.add_argument("row_end", type=int)

    p_shapes = sub.add_parser("shapes", help="図形・テキストボックス・画像の一覧を表示")
    p_shapes.add_argument("sheet", help="シート名またはインデックス（0始まり）")

    args = parser.parse_args()
    {
        "sheets": cmd_sheets,
        "grid": cmd_grid,
        "cells": cmd_cells,
        "shapes": cmd_shapes,
    }[args.command](args)


if __name__ == "__main__":
    main()
