
## 2026-05-25 - [Optimize N+1 Queries in Streamlit]
**Learning:** Streamlit reruns from top to bottom on every interaction. Calling the database within layout loops (like `st.sidebar`) causes N+1 queries on every render.
**Action:** Always batch fetch loop data into a `set` or `dict` at the top of the component before iterating to ensure O(1) lookups and minimize DB calls.
