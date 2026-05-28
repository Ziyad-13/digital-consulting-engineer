## 2024-05-18 - Avoid N+1 queries in Streamlit loops
**Learning:** Calling database functions inside layout iterations like `for pn in PHASE_ORDER:` causes N+1 query problems which slows down UI rendering.
**Action:** When a UI component needs to check states repeatedly (e.g. `is_phase_marked_complete`), fetch all required states upfront via a single batched query into a memory `set` for O(1) lookups.
