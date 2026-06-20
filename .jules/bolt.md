## 2025-02-24 - Streamlit `format_func` O(N) Iteration Bottleneck
**Learning:** Using an O(N) list iteration inside a Streamlit component's `format_func` (such as `st.selectbox`) causes the iteration to be executed for *every* item in the dropdown list, turning it into an O(N^2) operation that significantly degrades performance as list size grows (e.g., 27x slower for 1000 items).
**Action:** When populating Streamlit UI components from a list, always pre-compute a dictionary mapping before the component definition to enable O(1) lookups inside the `format_func`.
