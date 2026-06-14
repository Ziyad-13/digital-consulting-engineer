## 2026-06-14 - Add tooltips to disabled buttons using Streamlit's help parameter

**Learning:** Streamlit's `st.button` component does not natively accept standard `aria-label` tags well, making disabled buttons difficult to understand for screen readers and general UX.

**Action:** Utilize the native `help` parameter (`st.button(..., help='tooltip text')`) to provide context on why a button is disabled, which improves both visual UX and accessibility.