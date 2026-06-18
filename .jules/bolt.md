## 2024-05-18 - Hidden O(N^2) Complexity in Streamlit Selectbox
**Learning:** In Streamlit, `st.selectbox` evaluates its `format_func` for every option every time it renders. If the format function contains an O(N) array iteration (like `next(...)` over a list of dictionaries), it creates a hidden O(N^2) performance bottleneck as the list of options grows.
**Action:** Always pre-compute a mapping dictionary (like `project_names = {p["id"]: p["name"] for p in projects}`) for O(1) lookups before passing a format function into Streamlit selection components.
