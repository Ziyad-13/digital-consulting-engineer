## 2024-05-24 - Tooltips for disabled buttons
**Learning:** Disabled Streamlit buttons without tooltips cause confusion because native HTML doesn't easily expose the reason to screen readers or users. Using the native `help` parameter provides instant context.
**Action:** Always use `help=` for `st.button` when `disabled=True` is conditionally applied.
