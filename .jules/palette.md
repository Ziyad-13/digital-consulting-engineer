## 2025-06-25 - Fix Mobile RTL Viewport Layout

**Learning:** Streamlit's structural layout elements (`stAppViewContainer`, `stSidebar`, `stHeader`, `stMainBlockContainer`) use flexible box models that can unexpectedly break (like off-screen components or broken sidebars) when the global document direction is forced to `rtl` directly on those containers in smaller viewports.

**Action:** When implementing Right-To-Left (RTL) styling in Streamlit apps across both desktop and mobile viewports, do not apply `direction: rtl;` to root/structural layout containers. Instead, target the internal content containers (`[data-testid="stMarkdownContainer"] *`, `[data-testid="stMetricValue"]`, `.stTextInput`, `.stButton`, etc.) explicitly. This enforces the RTL text direction while preserving Streamlit's native responsive layout mechanisms.
