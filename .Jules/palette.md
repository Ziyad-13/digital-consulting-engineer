## 2024-05-24 - [Tooltip on disabled buttons]
**Learning:** Streamlit disabled buttons (`st.button(disabled=True)`) can still display tooltips via the `help` parameter. This is a very effective pattern for clarifying complex gateway rules (e.g. "needs image", "needs material") directly on the blocked action, preventing user frustration without needing to render separate warning banners.
**Action:** Always use the `help` parameter on Streamlit buttons that are conditionally disabled to explain exactly *why* they are blocked and what the user needs to do.
