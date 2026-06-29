## 2024-05-15 - Improve accessibility of disabled buttons in Streamlit
**Learning:** `st.button` components do not easily accept standard `aria-label` tags, but we can utilize the native `help` parameter to provide contextual tooltips. This is critical for accessibility because users need to understand *why* a button is disabled, rather than just seeing a grayed-out component.
**Action:** When making a button conditionally disabled (`disabled=True`), always evaluate if a `help="..."` text is necessary to explain the condition to the user.
