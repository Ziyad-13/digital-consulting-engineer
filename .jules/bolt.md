
## 2024-05-18 - Optimized material row rendering by lifting db.get_materials out of the loop
**Learning:** Calling database fetching functions inside a loop that iterates over UI components leads to an N+1 query problem and redundant data fetching, significantly degrading rendering performance in Streamlit applications.
**Action:** When a loop requires data that is fetched based on the overall context (like phase or project) rather than the individual row items, fetch the data once before the loop into a dictionary/state object, and pass that object into the loop iterations for O(1) lookups.
