"""
Excel exporter for the BOQ.

Builds a single .xlsx workbook with:

* "📋 Summary" / "📋 الملخص" — first sheet showing the project name,
  total item count, and a per-category breakdown.
* One sheet per category (structural / insulation / mep / electrical /
  sanitary / finishes) with styled headers, frozen first row, and
  auto-sized columns.

Styling kept minimal but professional: bold white text on a slate header,
zebra-striped data rows, thin borders. No external libraries beyond
openpyxl, which already ships with Streamlit.
"""
from __future__ import annotations

import io
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from i18n import t, current_lang, translate_boq_item


# Visual order of category sheets in the workbook.
CATEGORY_ORDER = [
    "structural", "insulation", "mep",
    "electrical", "sanitary", "finishes",
]


# ---------------------------------------------------------------------------
# Style constants — defined once, reused on every sheet.
# ---------------------------------------------------------------------------
_HDR_FILL    = PatternFill("solid", fgColor="1F2937")   # slate-800
_HDR_FONT    = Font(bold=True, color="FFFFFF", size=12)
_TITLE_FONT  = Font(bold=True, size=16, color="1F2937")
_SUB_FONT    = Font(italic=True, size=10, color="475569")
_ZEBRA_FILL  = PatternFill("solid", fgColor="F1F5F9")   # slate-100
_THIN        = Side(style="thin", color="CBD5E1")       # slate-300
_CELL_BORDER = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)
_CENTER      = Alignment(horizontal="center", vertical="center")
_LEFT_WRAP   = Alignment(horizontal="left",   vertical="center", wrap_text=True)


def _style_header_row(ws: Worksheet, row: int, num_cols: int) -> None:
    for c in range(1, num_cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = _HDR_FILL
        cell.font = _HDR_FONT
        cell.alignment = _CENTER
        cell.border = _CELL_BORDER
    ws.row_dimensions[row].height = 26


def _autosize_columns(ws: Worksheet, max_widths: dict[int, int] | None = None) -> None:
    """Approximate auto-sizing: scan every cell, take the longest string +2,
    cap at the optional per-column max."""
    max_widths = max_widths or {}
    for col_idx, col in enumerate(ws.columns, start=1):
        longest = 0
        for cell in col:
            if cell.value is None:
                continue
            longest = max(longest, len(str(cell.value)))
        cap = max_widths.get(col_idx, 60)
        ws.column_dimensions[get_column_letter(col_idx)].width = min(longest + 2, cap)


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------
def build_boq_workbook(
    project: dict,
    boq_items: list[dict],
    floors: int = 1,
    finish_level: str = "economic",
) -> bytes:
    """Return the .xlsx bytes for the given project + BOQ rows."""
    wb = Workbook()
    rtl = current_lang() == "ar"

    # ---- Group by category --------------------------------------------------
    grouped: dict[str, list[dict]] = {}
    for r in boq_items:
        grouped.setdefault(r.get("category", "structural"), []).append(r)

    # ---- Sheet 1: Summary ---------------------------------------------------
    summary = wb.active
    summary.title = "📋 " + t("xlsx.summary.title")
    if rtl:
        summary.sheet_view.rightToLeft = True

    _build_summary_sheet(summary, project, grouped, floors, finish_level)

    # ---- Sheet 2..N: one per category --------------------------------------
    for cat in CATEGORY_ORDER:
        if cat not in grouped:
            continue
        sheet_name = t(f"boq.cat.{cat}")
        # Excel limits sheet names to 31 chars; emojis count as 1 char each.
        ws = wb.create_sheet(sheet_name[:31])
        if rtl:
            ws.sheet_view.rightToLeft = True
        _build_category_sheet(ws, sheet_name, grouped[cat])

    # ---- Serialize ---------------------------------------------------------
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Per-sheet builders
# ---------------------------------------------------------------------------
def _build_summary_sheet(
    ws: Worksheet, project: dict, grouped: dict[str, list[dict]],
    floors: int, finish_level: str,
) -> None:
    # Title block
    ws.cell(row=1, column=1, value=t("xlsx.summary.heading")).font = _TITLE_FONT
    ws.cell(row=2, column=1, value=t("xlsx.summary.subtitle",
                                     name=project["name"])).font = _SUB_FONT
    ws.cell(row=3, column=1, value=t(
        "xlsx.summary.generated",
        when=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    )).font = _SUB_FONT

    # Project info table
    info_pairs = [
        (t("xlsx.summary.col_label"),  t("xlsx.summary.col_value")),
        (t("nav.project_name"),        project.get("name", "")),
        (t("nav.project_loc"),         project.get("location") or "—"),
        (t("nav.project_budget"),      f"{project.get('budget', 0):,.0f}"),
        (t("boq.floors"),              str(floors)),
        (t("boq.finish_level"),        t(f"boq.finish.{finish_level}")),
    ]
    info_start = 5
    for i, (k, v) in enumerate(info_pairs):
        ws.cell(row=info_start + i, column=1, value=k)
        ws.cell(row=info_start + i, column=2, value=v)
        if i == 0:
            _style_header_row(ws, info_start + i, 2)
        else:
            for c in (1, 2):
                ws.cell(row=info_start + i, column=c).border = _CELL_BORDER
                ws.cell(row=info_start + i, column=c).alignment = _LEFT_WRAP
                if i % 2 == 0:
                    ws.cell(row=info_start + i, column=c).fill = _ZEBRA_FILL

    # Per-category breakdown table
    breakdown_start = info_start + len(info_pairs) + 2
    ws.cell(row=breakdown_start, column=1,
            value=t("xlsx.summary.breakdown")).font = _TITLE_FONT

    headers = [t("xlsx.summary.col_category"),
               t("xlsx.summary.col_count")]
    head_row = breakdown_start + 2
    for c, h in enumerate(headers, start=1):
        ws.cell(row=head_row, column=c, value=h)
    _style_header_row(ws, head_row, len(headers))

    total_items = 0
    valid_cat_index = 0
    for cat in CATEGORY_ORDER:
        if cat not in grouped:
            continue
        count = len(grouped[cat])
        total_items += count
        r = head_row + 1 + valid_cat_index
        ws.cell(row=r, column=1, value=t(f"boq.cat.{cat}"))
        ws.cell(row=r, column=2, value=count)
        for c in (1, 2):
            ws.cell(row=r, column=c).border = _CELL_BORDER
            ws.cell(row=r, column=c).alignment = _LEFT_WRAP if c == 1 else _CENTER
            if valid_cat_index % 2 == 0:
                ws.cell(row=r, column=c).fill = _ZEBRA_FILL
        valid_cat_index += 1

    # Totals row
    total_row = head_row + 1 + len([c for c in CATEGORY_ORDER if c in grouped])
    ws.cell(row=total_row, column=1, value=t("xlsx.summary.total"))
    ws.cell(row=total_row, column=2, value=total_items)
    for c in (1, 2):
        cell = ws.cell(row=total_row, column=c)
        cell.font = Font(bold=True, size=12)
        cell.fill = PatternFill("solid", fgColor="FEF3C7")  # amber-100
        cell.border = _CELL_BORDER
        cell.alignment = _LEFT_WRAP if c == 1 else _CENTER

    _autosize_columns(ws, max_widths={1: 36, 2: 28})


def _build_category_sheet(
    ws: Worksheet, sheet_title: str, rows: list[dict],
) -> None:
    # Sheet title
    ws.cell(row=1, column=1, value=sheet_title).font = _TITLE_FONT
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=3)
    ws.cell(row=2, column=1,
            value=t("xlsx.cat.subtitle", n=len(rows))).font = _SUB_FONT
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=3)

    # Header row at row 4
    headers = [t("p0.boq.col_item"), t("p0.boq.col_qty"), t("p0.boq.col_unit")]
    for c, h in enumerate(headers, start=1):
        ws.cell(row=4, column=c, value=h)
    _style_header_row(ws, 4, len(headers))
    ws.freeze_panes = "A5"  # keep header visible while scrolling

    # Data rows
    for i, row in enumerate(rows):
        r = 5 + i
        ws.cell(row=r, column=1, value=translate_boq_item(row["item_name"]))
        ws.cell(row=r, column=2, value=row["quantity"])
        ws.cell(row=r, column=3, value=row["unit"])
        for c in range(1, 4):
            cell = ws.cell(row=r, column=c)
            cell.border = _CELL_BORDER
            cell.alignment = _LEFT_WRAP if c == 1 else _CENTER
            if i % 2 == 1:
                cell.fill = _ZEBRA_FILL

    _autosize_columns(ws, max_widths={1: 50, 2: 14, 3: 14})
