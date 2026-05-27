## 2025-03-01 - Tooltips for disabled Streamlit buttons

**Learning:** Streamlit's `st.button` does not natively support HTML `aria-label` tags, which makes standard accessibility practices difficult to apply.
**Action:** Use the native `help` parameter (`st.button(..., help='tooltip text')`) to provide context and explain why a button is disabled, improving both accessibility and the overall user experience.
