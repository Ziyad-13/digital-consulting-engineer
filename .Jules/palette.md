## 2024-05-23 - Tooltips on disabled buttons
**Learning:** In Streamlit, a disabled button silently blocks the user without providing context. Adding the `help` attribute natively provides a hover tooltip that explains *why* the button is disabled (e.g. missing material invoice or missing image), significantly improving accessibility and UX.
**Action:** Always check if a disabled button can benefit from a `help` attribute explaining the condition.
