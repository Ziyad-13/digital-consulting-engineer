## 2024-07-03 - Tooltips for Disabled States
**Learning:** Streamlit buttons don't support standard `aria-label` tags easily, so utilizing the native `help` parameter provides accessibility context on why the button is currently disabled.
**Action:** Use `st.button(..., help='reason')` for disabled buttons to improve user experience.
