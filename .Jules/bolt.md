## 2026-06-14 - Streamlit N+1 Query Optimization in Render Loop
**Learning:** Streamlit rendering loops (like generating lists of UI components) are heavily susceptible to N+1 query bottlenecks if database calls are embedded inside the iteration loop (e.g. fetching individual rows for `boq_items` and `materials`).
**Action:** Always pre-fetch and batch required database queries into memory dictionaries (for O(1) lookups) at the top of the component or render path, before entering the iteration loop to optimize Streamlit rendering performance.
