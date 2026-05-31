## 2025-05-31 - Streamlit Layout Loops and Database N+1 Queries
**Learning:** In Streamlit applications, drawing dynamic UI elements (like progress bars or navigation menus) inside a loop (`for phase in phases:`) can cause severe N+1 database queries if the completion status is checked inside the loop. This happens on every re-render and for every project.
**Action:** Always pre-fetch batched data (e.g., pulling all completed phases as a `set` for O(1) lookups) before starting UI rendering loops in Streamlit to eliminate N+1 overhead.
