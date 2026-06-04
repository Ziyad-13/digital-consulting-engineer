## 2026-06-04 - Tooltips for disabled Streamlit buttons
**Learning:** `st.button` components do not easily accept standard `aria-label` tags, but utilizing the native `help` parameter provides essential context on why the button is currently disabled. This greatly improves accessibility and user experience for disabled states.
**Action:** Always map disabled state conditions to specific helper text using the `help` argument when rendering disabled Streamlit buttons to ensure users understand the blockage.
