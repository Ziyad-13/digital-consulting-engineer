# Digital Consulting Engineer · المستشار الهندسي الرقمي (v2)

Bilingual (AR/EN) Streamlit MVP that gates a Saudi residential build
phase by phase. Includes the **Rework Loop**, the **Material Delivery
Gate**, **Payment Certificates**, and a hot/humid weather hint that
suggests SRC concrete in coastal Saudi cities.

---

## How to run · كيفية التشغيل

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app creates `construction_app_v2.db` and an `uploads/` folder on
first run. Open <http://localhost:8501> in your browser.

---

## Architecture

```
app.py                  ← entrypoint: lang toggle, sidebar, sticky progress bar
phase_views.py          ← Phase 0 (4 tabs), generic Phase-1 renderer with
                          Rework Loop + Material Gate, stub for Phases 2-6
phase_definitions.py    ← config-driven phase metadata
database.py             ← SQLite + CRUD (Rework status, materials, certs, timers)
i18n.py                 ← AR/EN dictionary + t() helper
ai_placeholders.py      ← Mock OCR / contract / material match / weather
utils.py                ← file save, alerts, RTL CSS, certificate generator
requirements.txt
```

### What works in v2

- **Phase 0** — Blueprint upload → mock BOQ; contract review with risk
  acceptance; site-prep photos (fencing + municipality board).
- **Phase 1** — fully built: 4 SBC checklist items, the **Material
  Delivery Gate** (anti-termite invoice must match BOQ before the
  related item can PASS), **Rework Loop** (FAIL → 🔧 Re-submit →
  re-upload proof → PASS), automatic **Payment Certificate** download
  on phase approval.
- **Bilingual UI** with RTL layout when Arabic is selected.
- **Outdoor-readable** styling: ≥50 px buttons, high-contrast traffic-
  light alerts, sticky progress bar at the top.
- **Gateway** enforced in three places: sidebar lock icons, server-side
  block in `app.py`, and a per-phase sign-off panel that refuses to
  approve until every item is PASS, every required image is uploaded,
  and every required material has match_status=MATCH.

### What is stubbed (intentional, per the spec)

- **Phases 2–6** — The spec says "build Phase 0 and Phase 1 ONLY. Pause
  and wait for my feedback." Phases 2–6 are reachable through the
  navigation and show a placeholder; their checklists will be added in
  the next iteration.
