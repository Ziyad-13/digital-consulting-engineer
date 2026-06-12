## 2026-06-12 - N+1 database queries in Streamlit loops
**Learning:** Streamlit component render loops making per-component DB calls cause noticeable UI latency bottlenecks.
**Action:** Hoist queries outside loop using `get_boq_items` and `get_materials`, and pass dictionaries for O(1) lookups to avoid N+1 queries.