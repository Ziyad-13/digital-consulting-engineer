## 2025-05-18 - Fix N+1 query in Streamlit render loop
**Learning:** In Streamlit applications, querying the database inside a render loop (e.g., iterating through materials and fetching BOQ data for each) leads to severe N+1 performance bottlenecks because it triggers repetitive database calls.
**Action:** Always fetch batched data upfront (e.g., `db.get_boq_items(project_id)`) and convert it into a dictionary for O(1) lookups before entering Streamlit render loops.
