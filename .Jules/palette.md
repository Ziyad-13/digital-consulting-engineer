## 2024-06-08 - Added helpful tooltips for disabled Streamlit buttons
**Learning:** Streamlit buttons don't accept standard 'aria-label' or title tags cleanly for disabled states. Using the native 'help' parameter provides a tooltip that explains to users exactly why a button (like 'Pass' or 'Rework') is disabled, improving UX and clarity without custom HTML.
**Action:** Always use the 'help' parameter on st.button to provide context when the 'disabled' parameter evaluates to True.
