## 2026-06-05 - [Batch DB queries in Streamlit render loops]
**Learning:** Streamlit reruns the whole script and layout logic on user interactions. Calling database queries in a loop within layout components (like rendering progress bar or sidebar phases) leads to the N+1 problem, significantly slowing down the application responsiveness.
**Action:** Always fetch batched data (e.g. `get_completed_phases`) into a collection like a `set` or `dict` before the rendering loop and use O(1) lookups during the iteration to drastically improve Streamlit render performance.
