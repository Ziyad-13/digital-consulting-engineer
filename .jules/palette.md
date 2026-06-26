## 2025-03-01 - Provide Accessibility Context for Disabled Streamlit Buttons

**Learning:** Streamlit's `st.button` does not easily accept standard `aria-label` tags. Disabling interactive elements without context creates an accessibility gap, particularly for screen reader users and those navigating complex state-driven forms like phase checklists where multiple conditions (image required, material check) cause a button to become inactive.

**Action:** Utilize the native `help` parameter (`st.button(..., help='reason')`) in Streamlit for disabled buttons. This creates a tooltip that explains why the interaction is currently blocked (e.g. "Cannot pass: requires image or material match"), drastically improving UX by transforming a silent failure into actionable guidance.