## 2024-05-15 - Streamlit button disabled states
**Learning:** `st.button` components do not easily accept standard `aria-label` tags for accessibility in Streamlit.
**Action:** Utilize the native `help` parameter (`st.button(..., help='tooltip text')`) to provide context on why a button is currently disabled, which improves both UX and accessibility for screen readers and visual users.