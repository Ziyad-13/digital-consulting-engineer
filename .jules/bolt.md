
## 2024-05-18 - [Batched Database Queries in Streamlit Render Loops]
**Learning:** Streamlit re-runs the entire script on every user interaction, making it highly susceptible to N+1 query bottlenecks when database queries are placed inside component rendering loops (e.g., iterating over phases to render a progress bar). This architecture exacerbates seemingly trivial database overhead.
**Action:** When working with Streamlit layout components or loops over static definitions, avoid placing database query functions inside the loop. Instead, use a single batched query to fetch the necessary data as a `set` or `dict` before the loop, enabling O(1) lookups during the render cycle.
