## 2024-06-27 - Added Tooltips to Disabled Buttons

**Learning:** Streamlit `st.button` components do not easily accept standard `aria-label` tags. To improve accessibility and user experience for disabled states, utilize the native `help` parameter (`st.button(..., help='tooltip text')`) to provide context on why the button is currently disabled.

**Action:** Whenever a button is disabled, always pass an explicit string to the `help` parameter to inform the user about the missing condition instead of leaving them guessing.