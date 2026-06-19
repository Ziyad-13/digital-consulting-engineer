import time
import database as db

db.init_db()
project_id = db.create_project("Perf Test", 1000000, "Riyadh")

for p in [0, 1, 2]:
    db.mark_phase_complete(project_id, p)

phase_order = [0, 1, 2, 3, 4, 5, 6]

def previous_phase(phase: int) -> int | None:
    if phase not in phase_order:
        return None
    idx = phase_order.index(phase)
    return phase_order[idx - 1] if idx > 0 else None

def test_original():
    start = time.perf_counter()
    for _ in range(100):
        # Simulated app.py sidebar loop
        for pn in phase_order:
            done = db.is_phase_marked_complete(project_id, pn)
            prev = previous_phase(pn)
            prereq_done = prev is None or db.is_phase_marked_complete(project_id, prev)

        # Simulated utils.py render_progress_bar loop
        for p in phase_order:
            done = db.is_phase_marked_complete(project_id, p)
        completed = sum(1 for p in phase_order if db.is_phase_marked_complete(project_id, p))
    return time.perf_counter() - start

# Simulated new function
def get_completed_phases(pid):
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT phase_number FROM phase_status WHERE project_id=? AND completed=1",
            (pid,)
        ).fetchall()
        return {r["phase_number"] for r in rows}

def test_optimized():
    start = time.perf_counter()
    for _ in range(100):
        # Simulated app.py sidebar loop
        completed_phases = get_completed_phases(project_id)
        for pn in phase_order:
            done = pn in completed_phases
            prev = previous_phase(pn)
            prereq_done = prev is None or prev in completed_phases

        # Simulated utils.py render_progress_bar loop
        completed_phases2 = get_completed_phases(project_id)
        for p in phase_order:
            done = p in completed_phases2
        completed = sum(1 for p in phase_order if p in completed_phases2)
    return time.perf_counter() - start

orig_time = test_original()
opt_time = test_optimized()

print(f"Original: {orig_time:.4f}s")
print(f"Optimized: {opt_time:.4f}s")
print(f"Improvement: {(orig_time - opt_time) / orig_time * 100:.1f}%")
