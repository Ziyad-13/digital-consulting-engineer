## 2026-06-22 - [O(1) project selectbox format_func lookup]
**Learning:** [Using a list comprehension with `next(...)` inside a Streamlit component `format_func` evaluates across all items on every render. Because the projects loop scales by N, mapping items causes an unnecessary O(N) evaluation for an ID to String lookup.]
**Action:** [Pre-compute a dictionary (`{p["id"]: p["name"] for p in projects}`) prior to defining the `format_func` for an O(1) dictionary lookup, significantly reducing latency when project count is large.]
