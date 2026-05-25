"""
Digital Consulting Engineer (المستشار الهندسي الرقمي) — v2

Bilingual (AR/EN) Streamlit MVP that gates a Saudi residential build phase
by phase. Run with::

    pip install -r requirements.txt
    streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

import database as db
from i18n import t, init_lang, current_lang, SUPPORTED_LANGS
from phase_definitions import PHASE_DEFINITIONS, PHASE_ORDER, previous_phase
from phase_views import render_phase_0, render_phase_generic
from utils import (
    inject_styles, render_progress_bar, render_header_with_logo,
    alert_error, alert_info,
)


# ---------------------------------------------------------------------------
# Page config + global state init
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Digital Consulting Engineer",
    page_icon="🏗️",
    layout="wide",
)

init_lang()                # populates st.session_state.lang
db.init_db()
inject_styles()            # outdoor CSS + RTL overlay if Arabic


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def _phase_label(phase_number: int) -> str:
    return t(f"phase.{phase_number}.title")


with st.sidebar:
    st.markdown(f"### 🏗️  {t('app.title')}")
    st.caption(t("app.subtitle"))

    # ---- Language toggle (Arabic by default) ------------------------------
    st.markdown("---")
    chosen_lang = st.radio(
        t("nav.lang"),
        options=list(SUPPORTED_LANGS),
        format_func=lambda code: "🇸🇦 العربية" if code == "ar" else "🇬🇧 English",
        index=list(SUPPORTED_LANGS).index(current_lang()),
        horizontal=True,
        key="lang_radio",
    )
    if chosen_lang != current_lang():
        st.session_state.lang = chosen_lang
        st.rerun()

    st.markdown("---")

    # ---- Project picker --------------------------------------------------
    projects = db.list_projects()
    if projects:
        selected_id = st.selectbox(
            t("nav.active_project"),
            options=[p["id"] for p in projects],
            format_func=lambda pid: next(
                p["name"] for p in projects if p["id"] == pid
            ),
            key="active_project_id",
        )
    else:
        st.info(t("nav.no_projects"))
        selected_id = None

    with st.expander(t("nav.new_project")):
        with st.form("new_project_form", clear_on_submit=True):
            new_name = st.text_input(t("nav.project_name"))
            new_loc = st.text_input(t("nav.project_loc"),
                                    placeholder="e.g., Jeddah / جدة")
            new_budget = st.number_input(
                t("nav.project_budget"), min_value=0.0, step=10_000.0
            )
            if st.form_submit_button(t("nav.create")):
                if new_name.strip():
                    pid = db.create_project(
                        new_name.strip(), new_budget, new_loc.strip()
                    )
                    st.session_state.active_project_id = pid
                    st.rerun()

    st.markdown("---")

    # ---- Phase navigation (with lock icons) ------------------------------
    if selected_id is not None:
        st.subheader(t("nav.phases"))
        radio_labels: dict[int, str] = {}
        # ⚡ Bolt Optimization: Batch fetch completed phases to prevent N+1 queries during render loop
        completed_phases = db.get_completed_phases(selected_id)
        for pn in PHASE_ORDER:
            done = pn in completed_phases
            prev = previous_phase(pn)
            prereq_done = prev is None or prev in completed_phases
            icon = "✅" if done else ("🔧" if prereq_done else "🔒")
            radio_labels[pn] = f"{icon}  {_phase_label(pn)}"
        st.radio(
            t("nav.phases"),
            options=PHASE_ORDER,
            format_func=lambda pn: radio_labels[pn],
            key="current_phase_nav",
            label_visibility="collapsed",
        )

        # ---- Payment ledger ----------------------------------------------
        st.markdown("---")
        st.caption(t("nav.payment_ledger"))
        fins = db.get_financials(selected_id)
        if fins:
            for f in fins:
                icon = "💰" if f["paid"] else "⏳"
                st.write(
                    f"{icon} P{f['phase_number']} · "
                    f"{f['milestone_name']} — {f['percentage']:.0f}%"
                )
        else:
            st.caption(t("nav.no_payments"))

        # ---- Issued certificates ----------------------------------------
        certs = db.get_payment_certificates(selected_id)
        if certs:
            st.caption(t("nav.certificates"))
            for c in certs:
                st.caption(
                    f"📄 {c['certificate_no']} · "
                    f"{c['amount']:,.0f} SAR ({c['percentage']:.0f}%)"
                )

        # ---- Danger zone: delete project -------------------------------
        # Hidden inside an expander + requires typing the project name as a
        # confirmation, since deletion is permanent and cascades to every
        # child table.
        st.markdown("---")
        with st.expander(t("nav.delete_project")):
            project_name = next(
                (p["name"] for p in projects if p["id"] == selected_id), ""
            )
            st.caption(t("nav.delete_warning"))
            typed = st.text_input(
                t("nav.confirm_delete"),
                key=f"delete_confirm_{selected_id}",
                placeholder=project_name,
            )
            if st.button(t("nav.confirm_delete_btn"),
                         key=f"delete_btn_{selected_id}",
                         type="secondary",
                         use_container_width=True):
                if typed.strip() == project_name:
                    db.delete_project(selected_id)
                    # Clear the active selection so the welcome screen
                    # appears (or the next project is auto-selected).
                    if "active_project_id" in st.session_state:
                        del st.session_state["active_project_id"]
                    st.success(t("nav.deleted"))
                    st.rerun()
                else:
                    st.error(t("nav.name_mismatch"))


# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
if selected_id is None:
    render_header_with_logo(t("app.welcome.h"))
    st.markdown(t("app.welcome.body"))
else:
    project = db.get_project(selected_id)
    current_phase: int = st.session_state.get("current_phase_nav", 0)

    # 1) Sticky progress bar at the very top of the main column.
    render_progress_bar(selected_id, current_phase, PHASE_ORDER)

    # 2) Header with title + duck logo
    render_header_with_logo(project["name"])
    m1, m2, m3 = st.columns(3)
    m1.metric(t("hdr.budget"), f"{project['budget']:,.0f}")
    m2.metric(t("hdr.last_phase"), f"P{project['current_phase']}")
    paid_pct = sum(f["percentage"] for f in db.get_financials(selected_id)
                   if f["paid"])
    m3.metric(t("hdr.released"), f"{paid_pct:.0f}%")
    st.markdown("---")

    # 3) Gateway enforcement: block locked phases.
    prev = previous_phase(current_phase)
    locked = prev is not None and not db.is_phase_marked_complete(selected_id, prev)

    if locked:
        alert_error(t("alert.locked", phase=current_phase, prev=prev))
    elif current_phase == 0:
        render_phase_0(selected_id)
    else:
        # All other phases (1-6) use the same data-driven renderer.
        render_phase_generic(selected_id, current_phase)
