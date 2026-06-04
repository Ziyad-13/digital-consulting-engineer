## 2024-06-04 - [Avoid N+1 queries in Streamlit loops]
**Learning:** [In Streamlit applications, avoid N+1 database queries in layout components or render loops. Calling the database for every row or item significantly slows down render times.]
**Action:** [Optimize by using batched queries (e.g., returning a `set` or `dict` for O(1) lookups) fetched once at the top of the file/component instead of repeatedly inside the iteration loop. Pass these fetched dictionaries as arguments to the rendering helper functions.]
