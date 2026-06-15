## 2024-06-15 - Streamlit Button Disabled State Accessibility
**Learning:** In Streamlit applications, `st.button` components do not easily accept standard `aria-label` tags. To improve accessibility and user experience for disabled states, it's best to utilize the native `help` parameter (`st.button(..., help='tooltip text')`) to provide context on why the button is currently disabled.
**Action:** Use the `help` parameter on Streamlit buttons with conditional text based on the disabled state to act as tooltips and improve accessibility.
