"""Shared helpers: file saving, custom CSS, alert wrappers, certificates,
sticky progress bar."""
from __future__ import annotations

import base64
import os
import time
from datetime import datetime

import streamlit as st

import database as db
from i18n import t, is_rtl
from logo_data import DUCK_LOGO_DATA_URI

UPLOAD_ROOT = "uploads"


# ---------------------------------------------------------------------------
# Brand logo — white duck supplied by the project owner.
# We decode the embedded base64 PNG once at import time and feed the bytes
# to st.image(). Earlier we tried <img src="data:..."> via st.markdown, but
# Streamlit's markdown renderer silently drops very long data URIs in some
# versions. Bytes through st.image() always work.
# ---------------------------------------------------------------------------
DUCK_LOGO_BYTES: bytes = base64.b64decode(DUCK_LOGO_DATA_URI.split(",", 1)[1])


def render_header_with_logo(title: str, subtitle: str | None = None) -> None:
    """Render the project title with the duck logo in the top-right corner.

    Uses two columns. In RTL (Arabic) the column order is reversed by the
    page-level CSS, so the logo lands on the visual right next to the title.
    """
    col_title, col_logo = st.columns([5, 1])
    with col_title:
        st.title(title)
        if subtitle:
            st.caption(subtitle)
    with col_logo:
        st.image(DUCK_LOGO_BYTES, width=96)


# ---------------------------------------------------------------------------
# File handling
# ---------------------------------------------------------------------------
def ensure_upload_dir(project_id: int, phase: int,
                      subfolder: str | None = None) -> str:
    parts = [UPLOAD_ROOT, f"project_{project_id}", f"phase_{phase}"]
    if subfolder:
        parts.append(subfolder)
    path = os.path.join(*parts)
    os.makedirs(path, exist_ok=True)
    return path


def save_uploaded_file(uploaded_file, project_id: int, phase: int,
                       subfolder: str | None = None) -> str | None:
    if uploaded_file is None:
        return None
    folder = ensure_upload_dir(project_id, phase, subfolder)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = uploaded_file.name.replace(" ", "_")
    file_path = os.path.join(folder, f"{timestamp}_{safe_name}")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


# ---------------------------------------------------------------------------
# Standard alerts (Red/Amber/Green)
# ---------------------------------------------------------------------------
def alert_success(msg: str) -> None: st.success(f"✅ {msg}")
def alert_warning(msg: str) -> None: st.warning(f"⚠️ {msg}")
def alert_error(msg: str) -> None:   st.error(f"🚫 {msg}")
def alert_info(msg: str) -> None:    st.info(f"ℹ️ {msg}")


# ---------------------------------------------------------------------------
# CSS — outdoor-readable buttons + RTL toggle
# ---------------------------------------------------------------------------
_BASE_CSS = """
<style>
.stButton > button, .stDownloadButton > button {
    min-height: 50px;
    font-size: 1.05rem;
    font-weight: 700;
    border-radius: 12px;
    border: 2px solid transparent;
}
[data-testid="stMetricValue"] { font-size: 1.7rem; font-weight: 800; }
[data-testid="stMetricLabel"] { font-size: 0.95rem; }
[data-testid="stCheckbox"] label, [data-testid="stRadio"] label {
    font-size: 1.0rem;
}
.dce-progress {
    position: sticky; top: 0; z-index: 999;
    background: rgba(255,255,255,0.97);
    backdrop-filter: blur(6px);
    padding: 10px 4px 12px 4px;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 12px;
}
.dce-progress-row {
    display: flex; gap: 6px; flex-wrap: wrap; align-items: center;
}
.dce-pill {
    padding: 6px 12px; border-radius: 999px; font-weight: 700;
    font-size: 0.9rem; color: #fff; min-width: 44px; text-align: center;
}
.dce-pill.done    { background: #16a34a; }
.dce-pill.current { background: #f59e0b; }
.dce-pill.locked  { background: #94a3b8; }
.dce-progress-label { font-size: 0.85rem; color: #475569; margin-bottom: 4px; }
</style>
"""

_RTL_CSS = """
<style>
[data-testid="stAppViewContainer"], [data-testid="stSidebar"],
[data-testid="stHeader"], [data-testid="stMainBlockContainer"] {
    direction: rtl;
}
input[type="number"], code, pre { direction: ltr; }
</style>
"""


def inject_styles() -> None:
    st.markdown(_BASE_CSS, unsafe_allow_html=True)
    if is_rtl():
        st.markdown(_RTL_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sticky progress bar (rendered at the top of the main column)
# ---------------------------------------------------------------------------
def render_progress_bar(project_id: int, current_phase: int,
                        phase_order: list[int]) -> None:
    pills_html = []
    completed_phases = db.get_completed_phases(project_id)
    for p in phase_order:
        done = p in completed_phases
        cls = "done" if done else ("current" if p == current_phase else "locked")
        label = t(f"phase.{p}.short")
        pills_html.append(f'<div class="dce-pill {cls}">{label}</div>')

    completed = sum(1 for p in phase_order if p in completed_phases)
    label = t("hdr.progress")
    html = (
        f'<div class="dce-progress">'
        f'  <div class="dce-progress-label">{label}: '
        f'    <strong>{completed} / {len(phase_order)}</strong></div>'
        f'  <div class="dce-progress-row">{"".join(pills_html)}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Payment certificate (text format for MVP — readable in either language)
# ---------------------------------------------------------------------------
def generate_payment_certificate(
    project: dict, phase_number: int, milestone_name: str,
    percentage: float,
) -> tuple[str, str, float]:
    """Generate a bilingual text certificate and persist it."""
    cert_no = f"PC-{project['id']:04d}-P{phase_number}-{int(time.time())}"
    amount = float(project["budget"]) * percentage / 100.0
    issued = datetime.utcnow().isoformat(timespec="seconds")

    body_en = (
        f"PAYMENT CERTIFICATE\n"
        f"-------------------\n"
        f"Certificate No. : {cert_no}\n"
        f"Project         : {project['name']} (#{project['id']})\n"
        f"Phase           : {phase_number} — {milestone_name}\n"
        f"Percentage      : {percentage:.1f}%\n"
        f"Amount (SAR)    : {amount:,.2f}\n"
        f"Issued (UTC)    : {issued}\n"
        f"\n"
        f"This certificate authorises the release of the milestone payment\n"
        f"to the contractor. Generated by the Digital Consulting Engineer.\n"
    )
    body_ar = (
        f"شهادة دفع\n"
        f"---------\n"
        f"رقم الشهادة     : {cert_no}\n"
        f"المشروع         : {project['name']} (#{project['id']})\n"
        f"المرحلة         : {phase_number} — {milestone_name}\n"
        f"النسبة          : {percentage:.1f}٪\n"
        f"المبلغ (ر.س)    : {amount:,.2f}\n"
        f"تاريخ الإصدار   : {issued}\n"
        f"\n"
        f"تعتمد هذه الشهادة صرف دفعة هذه المرحلة للمقاول.\n"
        f"تم توليدها بواسطة المستشار الهندسي الرقمي.\n"
    )

    folder = ensure_upload_dir(project["id"], phase_number, "certificates")
    file_path = os.path.join(folder, f"{cert_no}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(body_en + "\n\n" + body_ar)

    db.save_payment_certificate(
        project["id"], phase_number, cert_no, percentage, amount, file_path
    )
    return cert_no, file_path, amount
