## 2025-02-25 - [Add tooltips to disabled Streamlit buttons]
**Learning:** In Streamlit applications, buttons that are disabled (`st.button(..., disabled=True)`) provide no context to the user or screen readers about *why* they are disabled, causing frustration.
**Action:** Use the native `help="..."` parameter in `st.button` to inject an explanatory tooltip (e.g., using `st.button(..., disabled=True, help="Reason for disabled state")`) whenever a button is conditionally disabled.
