## 2025-06-18 - Streamlit Disabled Button Accessibility

**Learning:** Streamlit's `st.button` components do not easily accept standard HTML attributes like `aria-label` or `title` to provide context for disabled states. This creates an accessibility and usability gap when a button is conditionally disabled (e.g., waiting for material validation or an image upload) without explaining *why*.

**Action:** Utilize the native Streamlit `help` parameter (`st.button(..., help='tooltip text')`) to render a built-in tooltip that explains the requirement or reason for the disabled state to the user.