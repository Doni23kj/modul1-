import matplotlib
# Авторы: Камыталиев Даниел, Эшанкулов Муса, Арсен Алмазов
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scheduler import *

def draw(tl, procs, title, out):
    pids = [p["pid"] for p in procs]
    fig, ax = plt.subplots(figsize=(12, 2.2 + 0.3 * len(pids) / 3))
    colors = plt.cm.Set3.colors
    for s, e, pid in segments(tl):
        if pid is None:
            continue
        ax.barh(0, e - s, left=s, color=colors[pids.index(pid) % len(colors)], edgecolor="black")
        ax.text((s + e) / 2, 0, pid, ha="center", va="center", fontsize=10, fontweight="bold")
        ax.text(s, -0.55, str(s), ha="center", va="top", fontsize=8)
    ax.text(len(tl), -0.55, str(len(tl)), ha="center", va="top", fontsize=8)
    ax.set_yticks([]); ax.set_xlim(0, len(tl) + 0.5); ax.set_ylim(-1, 0.6)
    ax.set_title(title)
    fig.tight_layout(); fig.savefig(out, dpi=130); plt.close(fig)

P = load("jobs.txt")
draw(fcfs(P), P, "FCFS — jobs.txt", "gantt_fcfs_jobs.png")
for name, fn in [("srtf", srtf), ("priority", priority), ("mlfq", mlfq)]:
    pm = load("mixed.txt")
    draw(fn(pm), pm, f"{name.upper()} — mixed.txt", f"gantt_{name}_mixed.png")
ps = load("starve.txt")
draw(priority(ps), ps, "Priority (preemptive) — starve.txt: P1 стартует на 57", "gantt_priority_starve.png")
draw(priority_aging(ps, 3), ps, "Priority + aging (step=3) — starve.txt: P1 стартует на 21", "gantt_aging_starve.png")
