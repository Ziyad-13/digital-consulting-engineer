## 2024-05-24 - [N+1 Streamlit Optimization]
**Learning:** In Streamlit applications, avoid N+1 database queries in layout components or render loops. Optimize by using batched queries (e.g., returning a `set` for O(1) lookups) fetched once at the top of the file/component instead of repeatedly inside the iteration loop.
**Action:** Use batched queries and set lookups instead of repeated single database checks inside `for` loops that render layout elements.
