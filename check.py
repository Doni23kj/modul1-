# Авторы: Камыталиев Даниел, Эшанкулов Муса, Арсен Алмазов
"""Самопроверка: каждый процесс получил ровно burst тиков и не стартовал до прихода."""
from scheduler import *
algos = {"FCFS": fcfs, "SJF": sjf, "RR q=2": lambda p: rr(p, 2), "SRTF": srtf, "Priority": priority,
         "Aging": lambda p: priority_aging(p, 3), "MLFQ": mlfq}
bad = 0
for f in ["set1", "jobs", "mixed", "starve"]:
    P = load(f + ".txt")
    for n, fn in algos.items():
        tl = fn(P); arr = {p["pid"]: p["arr"] for p in P}
        ok = all(tl.count(p["pid"]) == p["burst"] for p in P) and all(x is None or arr[x] <= t for t, x in enumerate(tl))
        bad += not ok
        if not ok: print("ОШИБКА", f, n)
print("Самопроверка:", "OK, все алгоритмы корректны" if not bad else f"ошибок: {bad}")
