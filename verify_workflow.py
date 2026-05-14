from playwright.sync_api import sync_playwright

if __name__ == "__main__":
    import sqlite3
    from datetime import datetime, timezone

    # Create the db row just in case so we don't have to fill all forms
    conn = sqlite3.connect('construction_app_v2.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (name, budget, location, current_phase) VALUES ('Automated Test Project UI Verify', 1000000, 'Riyadh', 2)")
    project_id = cursor.lastrowid
    # mark phase 0 and 1 as complete
    now_str = datetime.now(timezone.utc).isoformat()
    cursor.execute("INSERT INTO phase_status (project_id, phase_number, completed, completed_at) VALUES (?, ?, 1, ?)", (project_id, 0, now_str))
    cursor.execute("INSERT INTO phase_status (project_id, phase_number, completed, completed_at) VALUES (?, ?, 1, ?)", (project_id, 1, now_str))
    conn.commit()
    conn.close()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/home/jules/verification/videos",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()
        try:
            page.goto("http://localhost:8501")
            page.wait_for_timeout(3000)

            # Click English toggle using get_by_text, force=True if invisible
            page.get_by_text("🇬🇧 English").click(force=True)
            page.wait_for_timeout(2000)

            # Find the active project dropdown
            page.locator('div[data-baseweb="select"]').click(force=True)
            page.wait_for_timeout(500)
            page.get_by_text("Automated Test Project UI Verify").first.click(force=True)
            page.wait_for_timeout(2000)

            # Now click on Phase 2 radio button label text
            page.locator("label").filter(has_text="Phase 2").click(force=True)
            page.wait_for_timeout(2000)

            # The page should now display "Phase 2 · Substructure & QA Testing"
            # Since the stub is removed, we should see the checklists
            page.screenshot(path="/home/jules/verification/screenshots/verification.png")
            page.wait_for_timeout(1000)

            # Expand one of the checklists to show it works
            page.locator("summary").first.click(force=True)
            page.wait_for_timeout(1000)

            # Click on Phase 3
            page.locator("label").filter(has_text="Phase 3").click(force=True)
            page.wait_for_timeout(2000)

            page.screenshot(path="/home/jules/verification/screenshots/verification2.png")
            page.wait_for_timeout(1000)

        finally:
            context.close()
            browser.close()
