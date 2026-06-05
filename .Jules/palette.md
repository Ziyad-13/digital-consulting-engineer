## 2024-05-24 - Tooltips for Disabled Buttons in Streamlit

**Learning:** `st.button` components in Streamlit do not easily accept standard `aria-label` tags. However, when a button is visually disabled, it is a critical UX and accessibility anti-pattern to leave the user guessing *why* it is disabled. Using Streamlit's native `help` parameter (`st.button(..., help='tooltip text')`) provides a built-in tooltip mechanism to explain the disabled state, acting as an effective workaround to improve accessibility and user experience.

**Action:** Whenever implementing a disabled state for an interactive component in Streamlit (like `st.button`), always conditionally apply a `help` string that explicitly explains the required prerequisite actions (e.g., "Upload an image first" or "Material delivery must match").
