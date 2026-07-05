## 2026-07-05 - Add tooltips to disabled buttons in Streamlit
**Learning:** Streamlit's `st.button` does not easily accept standard `aria-label` tags, so disabled buttons provide poor accessibility/UX without context.
**Action:** Always utilize the native `help` parameter (`st.button(..., help='tooltip text')`) to provide context on why a button is currently disabled.