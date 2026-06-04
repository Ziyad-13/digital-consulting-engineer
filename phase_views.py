"""
Per-phase Streamlit view renderers (v2).

* render_phase_0          : Blueprints+BOQ, contract review, site preparation,
                            sign-off — bespoke 4-tab flow.
* render_phase_generic    : Data-driven renderer for Phases 1+ that supports
                            the **Rework Loop**, the **Material Delivery
                            Gate**, and **Payment Certificate** generation.
* render_phase_stub       : Placeholder shown for phases 2–6 (which will be
                            filled in after sign-off from the product owner).
"""
from __future__ import annotations

import os

import streamlit as st

import database as db
import ai_placeholders as ai
from i18n import t, translate_boq_item
from phase_definitions import PHASE_DEFINITIONS, next_phase
from excel_export import build_boq_workbook
from utils import (
    save_uploaded_file,
    alert_success, alert_warning, alert_error, alert_info,
    generate_payment_certificate,
)


# ============================================================================
# Phase 0 · Initiation & Planning
# ============================================================================
def render_phase_0(project_id: int) -> None:
    st.header(t("phase.0.title"))
    st.caption(t("phase.0.desc"))

    # NOTE: the "Site preparation" tab was hidden by user request.
    # `_render_siteprep_section` and the underlying `siteprep_photos` table
    # are kept intact. To restore the tab:
    #   1. Add t("p0.tab.siteprep") back to the tabs list below.
    #   2. Add `with tab_siteprep: _render_siteprep_section(project_id)`.
    #   3. Re-enable the site-prep check in `_render_phase0_signoff`.
    tab_bp, tab_contract, tab_signoff = st.tabs([
        t("p0.tab.bp"),
        t("p0.tab.contract"),
        t("p0.tab.signoff"),
    ])

    with tab_bp:        _render_blueprints_section(project_id)
    with tab_contract:  _render_contract_section(project_id)
    with tab_signoff:   _render_phase0_signoff(project_id)


def _render_blueprints_section(project_id: int) -> None:
    st.subheader(t("p0.bp.heading"))

    existing_bp = db.get_blueprints(project_id)
    if existing_bp:
        for bp in existing_bp:
            st.write(f"📄 `{os.path.basename(bp['file_path'])}` — {bp['uploaded_at']}")

    bp_file = st.file_uploader(
        t("p0.bp.upload_label"), type=["pdf"], key="bp_uploader"
    )
    if bp_file is not None and st.button(t("p0.bp.save_btn"), key="bp_save"):
        path = save_uploaded_file(bp_file, project_id, 0, "blueprints")
        db.save_blueprint(project_id, path)
        with st.spinner(t("p0.bp.generating")):
            bp_data = ai.parse_blueprint_pdf(path)
            boq = ai.estimate_boq(bp_data, floors=1, finish_level="economic")
            db.set_boq_items(project_id, boq)
        alert_success(t("p0.bp.saved"))
        st.rerun()

    st.subheader(t("p0.boq.heading"))
    boq = db.get_boq_items(project_id)

    if not boq:
        st.write(t("p0.boq.empty"))
        return

    # ---- Regeneration controls (floors + finish level) -------------------
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 2, 2])
        new_floors = c1.number_input(
            t("boq.floors"), min_value=1, max_value=5,
            value=int(st.session_state.get(f"boq_floors_{project_id}", 1)),
            key=f"boq_floors_input_{project_id}",
        )
        new_finish = c2.radio(
            t("boq.finish_level"),
            options=["economic", "luxury"],
            format_func=lambda v: t(f"boq.finish.{v}"),
            index=0 if st.session_state.get(
                f"boq_finish_{project_id}", "economic") == "economic" else 1,
            key=f"boq_finish_input_{project_id}",
            horizontal=True,
        )
        with c3:
            st.write("")  # vertical spacer
            if st.button(t("boq.regenerate"),
                         key=f"boq_regen_{project_id}",
                         use_container_width=True):
                bp_records = db.get_blueprints(project_id)
                bp_data = (ai.parse_blueprint_pdf(bp_records[-1]["file_path"])
                           if bp_records
                           else {"total_built_area_m2": 320, "floors": new_floors})
                new_boq = ai.estimate_boq(
                    bp_data, floors=int(new_floors), finish_level=new_finish
                )
                db.set_boq_items(project_id, new_boq)
                st.session_state[f"boq_floors_{project_id}"] = int(new_floors)
                st.session_state[f"boq_finish_{project_id}"] = new_finish
                st.rerun()

    # ---- Group BOQ items by category and render them in tabs ------------
    boq = db.get_boq_items(project_id)
    grouped: dict[str, list[dict]] = {}
    for row in boq:
        grouped.setdefault(row.get("category", "structural"), []).append(row)

    n_items = len(boq)
    n_cats = len(grouped)
    alert_info(t("boq.summary", n=n_items, c=n_cats))

    # Render in a deterministic order so the tab strip is stable across reruns.
    category_order = [
        "structural", "insulation", "mep",
        "electrical", "sanitary", "finishes",
    ]
    visible = [c for c in category_order if c in grouped]
    if visible:
        tabs = st.tabs([t(f"boq.cat.{c}") for c in visible])
        for tab, cat in zip(tabs, visible):
            with tab:
                rows = grouped[cat]
                st.dataframe(
                    [
                        {
                            t("p0.boq.col_item"): translate_boq_item(r["item_name"]),
                            t("p0.boq.col_qty"):  r["quantity"],
                            t("p0.boq.col_unit"): r["unit"],
                        }
                        for r in rows
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

    # ---- Single-file Excel export ----------------------------------------
    project = db.get_project(project_id)
    xlsx_bytes = build_boq_workbook(
        project=project,
        boq_items=boq,
        floors=int(st.session_state.get(f"boq_floors_{project_id}", 1)),
        finish_level=st.session_state.get(
            f"boq_finish_{project_id}", "economic"),
    )
    safe_name = (project["name"] or "project").replace(" ", "_")
    st.download_button(
        t("boq.export_xlsx"),
        data=xlsx_bytes,
        file_name=f"BOQ_{safe_name}_P{project['id']}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"boq_xlsx_{project_id}",
        type="primary",
        use_container_width=True,
    )

    alert_info(t("p0.boq.disclaimer"))


def _render_contract_section(project_id: int) -> None:
    st.subheader(t("p0.contract.heading"))

    existing = db.get_contract(project_id)
    skipped = bool(existing and existing.get("skipped"))

    # ---- Skip-contract escape hatch (for users without a formal contract) -
    new_skip = st.checkbox(
        t("p0.contract.skip"), value=skipped, key="contract_skip_chk"
    )
    if new_skip != skipped:
        db.set_contract_skipped(project_id, new_skip)
        st.rerun()

    if skipped:
        alert_warning(t("p0.contract.skip_warn"))
        return  # Hide the upload UI when skipped

    # ---- Normal upload + analysis flow -----------------------------------
    if existing and existing.get("file_path"):
        st.write(
            f"{t('p0.contract.current')} "
            f"`{os.path.basename(existing['file_path'])}`"
        )

    c_file = st.file_uploader(
        t("p0.contract.upload_label"), type=["pdf"], key="contract_uploader"
    )
    if c_file is not None and st.button(t("p0.contract.analyze_btn"),
                                        key="contract_analyze"):
        path = save_uploaded_file(c_file, project_id, 0, "contract")
        with st.spinner(t("p0.contract.analyzing")):
            review = ai.review_contract(path)
        missing_str = "; ".join(review["missing_clauses"].values())
        db.save_contract(project_id, path, missing_str, risks_accepted=False)
        st.rerun()

    contract = db.get_contract(project_id)
    if contract and contract.get("missing_clauses") is not None and contract.get("file_path"):
        missing_text = (contract["missing_clauses"] or "").strip()
        if missing_text:
            bullets = "\n".join(f"• {c}" for c in missing_text.split("; "))
            alert_warning(f"{t('p0.contract.high_risk')}\n\n{bullets}")
        else:
            alert_success(t("p0.contract.no_risk"))

        prior = bool(contract.get("risks_accepted", 0))
        accepted = st.checkbox(
            t("p0.contract.accept"), value=prior, key="risks_checkbox"
        )
        if accepted != prior:
            db.update_contract_risk_acceptance(project_id, accepted)
            st.rerun()


def _render_siteprep_section(project_id: int) -> None:
    st.subheader(t("p0.siteprep.heading"))
    photos = db.get_siteprep_photos(project_id)

    for kind, label_key in [("fencing", "p0.siteprep.fencing"),
                             ("board",   "p0.siteprep.board")]:
        st.markdown(f"**{t(label_key)}**")
        existing = photos.get(kind)
        if existing and os.path.exists(existing["file_path"]):
            st.image(existing["file_path"], width=320)
            st.caption(f"📸 {os.path.basename(existing['file_path'])}")
        uploaded = st.file_uploader(
            t("p0.siteprep.upload"),
            type=["png", "jpg", "jpeg"],
            key=f"siteprep_{kind}",
        )
        if uploaded is not None:
            path = save_uploaded_file(uploaded, project_id, 0, "siteprep")
            db.save_siteprep_photo(project_id, kind, path)
            alert_success(t("misc.image_uploaded"))
            st.rerun()
        st.markdown("---")


def _render_phase0_signoff(project_id: int) -> None:
    st.subheader(t("p0.signoff.heading"))

    boq = db.get_boq_items(project_id)
    contract = db.get_contract(project_id)

    has_blueprint = bool(db.get_blueprints(project_id)) and bool(boq)
    # The contract step is satisfied when either:
    #   (a) a contract was uploaded AND the user accepted the residual risk,
    #   (b) the user explicitly chose to skip the contract step.
    has_contract = bool(
        contract and (
            (contract.get("file_path") and contract.get("risks_accepted"))
            or contract.get("skipped")
        )
    )

    st.write(f"- {'✅' if has_blueprint else '❌'}  {t('p0.signoff.bp_done')}")
    st.write(f"- {'✅' if has_contract  else '❌'}  {t('p0.signoff.contract_done')}")
    # NOTE: site-prep gate disabled by user request. To re-enable, restore
    # the original three-condition check (see render_phase_0 comment).

    ready = has_blueprint and has_contract

    if db.is_phase_marked_complete(project_id, 0):
        alert_success(t("p0.signoff.approved"))
        return

    if not ready:
        alert_warning(t("p0.signoff.incomplete"))
        return

    if st.button(t("p0.signoff.approve"), type="primary", key="approve_p0"):
        db.mark_phase_complete(project_id, 0)
        db.update_current_phase(project_id, 1)
        alert_success(t("p0.signoff.approved"))
        st.rerun()


# ============================================================================
# Generic phase renderer (Phase 1 in v2; Phases 2-6 once filled in)
# ============================================================================
def render_phase_generic(project_id: int, phase_number: int) -> None:
    pdef = PHASE_DEFINITIONS[phase_number]
    st.header(t(pdef["title_key"]))
    st.caption(t(pdef["desc_key"]))

    project = db.get_project(project_id)

    # Weather-driven SBC advice (hot/humid → SRC concrete + extended curing).
    weather = ai.get_local_weather(project.get("location"))
    if weather.get("advice_key"):
        alert_warning(t(weather["advice_key"]))

    # Pre-fetch data for this phase to avoid N+1 queries in loops
    items_state = db.get_checklist_items(project_id, phase_number)
    materials_state = db.get_materials(project_id, phase_number)
    boq_items_list = db.get_boq_items(project_id)
    boq_items_dict = {row["item_name"]: row for row in boq_items_list}

    # 1) Material Delivery Gate (rendered first because checklist items
    #    depend on its match status).
    _render_material_gate(
        project_id, phase_number, pdef, materials_state, boq_items_dict
    )

    st.markdown("---")
    st.subheader("📋")

    # 2) Checklist
    for item in pdef["items"]:
        _render_checklist_item(
            project_id, phase_number, item, items_state, materials_state
        )

    st.markdown("---")
    _render_phase_signoff(
        project_id, phase_number, pdef, items_state, materials_state
    )


# --------------------- Material Delivery Gate -------------------------------
def _render_material_gate(
    project_id: int, phase_number: int, pdef: dict,
    materials_state: dict, boq_items_dict: dict
) -> None:
    if not pdef.get("materials"):
        return

    st.subheader(f"📦 {t('mat.heading')}")
    st.caption(t("mat.subheading"))

    for mat in pdef["materials"]:
        _render_material_row(
            project_id, phase_number, mat, materials_state, boq_items_dict
        )


def _render_material_row(
    project_id: int, phase_number: int, mat: dict,
    materials_state: dict, boq_items_dict: dict
) -> None:
    name = t(mat["name_key"])
    boq_row = boq_items_dict.get(mat["boq_match_name"])
    expected_qty = boq_row["quantity"] if boq_row else 0.0
    expected_unit = boq_row["unit"] if boq_row else ""

    cur = materials_state.get(mat["key"], {})

    with st.container(border=True):
        st.markdown(f"### {name}")

        col_a, col_b = st.columns(2)
        col_a.metric(
            t("mat.expected"),
            f"{expected_qty:.1f} {expected_unit}" if expected_qty else "—",
        )
        match_status = cur.get("match_status", "PENDING")
        match_label = {
            "PENDING":  t("mat.match_pending"),
            "MATCH":    t("mat.match_ok"),
            "MISMATCH": t("mat.match_bad"),
        }.get(match_status, match_status)
        col_b.metric(t("mat.match_status"), match_label)

        delivered = st.number_input(
            t("mat.delivered"),
            min_value=0.0, step=0.1,
            value=float(cur.get("delivered_qty") or 0.0),
            key=f"mat_qty_{phase_number}_{mat['key']}",
        )

        if cur.get("invoice_path") and os.path.exists(cur["invoice_path"]):
            st.caption(f"📄 {os.path.basename(cur['invoice_path'])}")

        invoice = st.file_uploader(
            t("mat.invoice"),
            type=["png", "jpg", "jpeg", "pdf"],
            key=f"mat_inv_{phase_number}_{mat['key']}",
        )

        if st.button(
            t("mat.run_check"), key=f"mat_run_{phase_number}_{mat['key']}"
        ):
            invoice_path = (
                save_uploaded_file(invoice, project_id, phase_number, "materials")
                if invoice is not None else cur.get("invoice_path")
            )
            check = ai.run_material_match(
                expected_qty, expected_unit, delivered, invoice_path
            )
            db.upsert_material(
                project_id, phase_number, mat["key"],
                material_name=name,
                expected_qty=expected_qty,
                expected_unit=expected_unit,
                delivered_qty=delivered,
                invoice_path=invoice_path,
                match_status=check["status"],
                notes=check["reason"],
            )
            if check["status"] == "MATCH":
                alert_success(check["reason"])
            elif check["status"] == "MISMATCH":
                alert_error(check["reason"])
            else:
                alert_info(check["reason"])
            st.rerun()


# --------------------- Checklist item with Rework Loop ----------------------
_STATUS_BADGE = {
    "PENDING": "⬜", "PASS": "✅", "FAIL": "🚫", "REWORK": "🔧",
}


def _render_checklist_item(
    project_id: int, phase_number: int, item: dict,
    items_state: dict, materials_state: dict,
) -> None:
    key = item["key"]
    cur = items_state.get(key, {})
    status = cur.get("status", "PENDING")
    has_image = bool(cur.get("image_path"))

    label = t(item["label_key"])
    badge = _STATUS_BADGE.get(status, "⬜")
    suffix = ""
    if item.get("requires_image") and not has_image:
        suffix += " 📷"
    if cur.get("rework_count"):
        suffix += f"  ({t('misc.rework_count', n=cur['rework_count'])})"

    with st.expander(f"{badge}  {label}{suffix}",
                     expanded=status in ("PENDING", "FAIL", "REWORK")):

        # Notes
        notes = st.text_area(
            "📝",
            value=cur.get("notes", "") or "",
            key=f"notes_{phase_number}_{key}",
            height=80,
            placeholder="…",
        )

        # Critical-rule warning when item is in FAIL/REWORK state
        if status in ("FAIL", "REWORK") and item.get("warn_on_fail_key"):
            alert_error(t(item["warn_on_fail_key"]))

        if status == "FAIL":
            alert_warning(t("alert.fail_explain"))
        elif status == "REWORK":
            alert_info(
                t("alert.rework_in_progress", n=cur.get("rework_count", 1))
            )

        # Image upload
        if item.get("requires_image"):
            img_label_key = item.get("image_label_key", "btn.upload")
            if has_image and os.path.exists(cur["image_path"]):
                st.image(cur["image_path"], width=320)
                st.caption(os.path.basename(cur["image_path"]))
            uploaded = st.file_uploader(
                t(img_label_key),
                type=["png", "jpg", "jpeg", "pdf"],
                key=f"img_{phase_number}_{key}",
            )
            if uploaded is not None:
                path = save_uploaded_file(uploaded, project_id, phase_number, key)
                db.upsert_checklist_item(
                    project_id, phase_number, key, image_path=path
                )
                alert_success(t("misc.image_uploaded"))
                st.rerun()

        # Material gate enforcement
        material_blocked = False
        if item.get("material_required"):
            mreq = materials_state.get(item["material_required"], {})
            if mreq.get("match_status") != "MATCH":
                material_blocked = True
                alert_warning(t("alert.material_required"))

        # Image gate enforcement (cannot PASS without proof)
        image_blocked = item.get("requires_image") and not has_image

        # Action buttons
        col_pass, col_fail, col_rework, col_save = st.columns(4)

        pass_disabled = material_blocked or image_blocked
        if col_pass.button(
            t("btn.mark_pass"),
            key=f"pass_{phase_number}_{key}",
            disabled=pass_disabled,
            type="primary",
        ):
            db.upsert_checklist_item(
                project_id, phase_number, key, status="PASS", notes=notes
            )
            st.rerun()

        if col_fail.button(
            t("btn.mark_fail"), key=f"fail_{phase_number}_{key}"
        ):
            db.upsert_checklist_item(
                project_id, phase_number, key, status="FAIL", notes=notes
            )
            st.rerun()

        # Rework button only matters once the item is in FAIL state
        if col_rework.button(
            t("btn.start_rework"),
            key=f"rework_{phase_number}_{key}",
            disabled=status not in ("FAIL", "REWORK"),
        ):
            db.start_rework(project_id, phase_number, key)
            alert_info(t("alert.rework_in_progress",
                         n=(cur.get("rework_count", 0) + 1)))
            st.rerun()

        if col_save.button(t("btn.save"), key=f"save_{phase_number}_{key}"):
            db.upsert_checklist_item(
                project_id, phase_number, key, notes=notes
            )
            alert_success(t("misc.image_uploaded"))


# --------------------- Phase sign-off & certificate -------------------------
def _render_phase_signoff(
    project_id: int, phase_number: int, pdef: dict,
    items_state: dict, materials_state: dict
) -> None:
    pending: list[str] = []
    for item in pdef["items"]:
        cur = items_state.get(item["key"], {})
        if cur.get("status") != "PASS":
            pending.append(f"❌ {t(item['label_key'])}")
            continue
        if item.get("requires_image") and not cur.get("image_path"):
            pending.append(f"📷 {t(item['label_key'])}")
            continue
        if item.get("material_required"):
            m = materials_state.get(item["material_required"], {})
            if m.get("match_status") != "MATCH":
                pending.append(f"📦 {t(item['label_key'])}")

    if db.is_phase_marked_complete(project_id, phase_number):
        certs = [c for c in db.get_payment_certificates(project_id)
                 if c["phase_number"] == phase_number]
        if certs:
            cert = certs[-1]
            alert_success(
                t("alert.cert_issued", no=cert["certificate_no"],
                  pct=cert["percentage"])
            )
            with open(cert["file_path"], "rb") as f:
                st.download_button(
                    t("btn.download_cert"),
                    data=f.read(),
                    file_name=os.path.basename(cert["file_path"]),
                    mime="text/plain",
                    key=f"dl_cert_{cert['id']}",
                )
        return

    if pending:
        alert_warning(t("alert.outstanding"))
        for line in pending:
            st.write(line)
        return

    alert_success(t("alert.all_passed"))
    if st.button(
        f"{t('btn.approve')} ({pdef['payment_pct']:.0f}%)",
        type="primary", key=f"approve_{phase_number}",
    ):
        db.mark_phase_complete(project_id, phase_number)
        db.add_financial(
            project_id, phase_number,
            pdef["payment_label"], pdef["payment_pct"],
        )
        db.mark_payment_released(
            project_id, phase_number, pdef["payment_label"]
        )
        project = db.get_project(project_id)
        cert_no, _, amount = generate_payment_certificate(
            project, phase_number,
            pdef["payment_label"], pdef["payment_pct"],
        )
        nxt = next_phase(phase_number)
        if nxt is not None:
            db.update_current_phase(project_id, nxt)
        alert_success(t("alert.cert_issued", no=cert_no,
                        pct=pdef["payment_pct"]))
        st.rerun()


# ============================================================================
# Stub for Phases 2-6 (filled in after sign-off from product owner)
# ============================================================================
def render_phase_stub(project_id: int, phase_number: int) -> None:
    pdef = PHASE_DEFINITIONS[phase_number]
    st.header(t(pdef["title_key"]))
    alert_info(
        "🚧 This phase has been unlocked by the gateway logic, but its "
        "checklist will be added in the next iteration."
    )
