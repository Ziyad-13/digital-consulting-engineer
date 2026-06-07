## 2024-06-07 - Optimize Streamlit rendering loop N+1 query problem
**Learning:** Found N+1 query pattern in `utils.py:render_progress_bar()` rendering loop which issues an individual query per phase checking if the phase is completed. In Streamlit applications, avoid N+1 database queries in layout components or render loops.
**Action:** Optimize by using batched queries returning a `set` or `dict` for O(1) lookups fetched once at the top of the file/component instead of repeatedly inside the iteration loop.
