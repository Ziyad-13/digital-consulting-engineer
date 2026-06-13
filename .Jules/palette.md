## 2024-06-13 - Tooltips for disabled Streamlit buttons
**Learning:** Streamlit `st.button` components do not easily accept standard `aria-label` tags.
**Action:** To improve accessibility and user experience for disabled states, utilize the native `help` parameter (`st.button(..., help='tooltip text')`) to provide context on why the button is currently disabled.