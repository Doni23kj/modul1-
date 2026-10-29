from scheduler import *
# Авторы: Камыталиев Даниел, Эшанкулов Муса, Арсен Алмазов
def row(name, P, tl):
    s = summary(P, tl)
    print(f"| {name} | {s['wait']:.2f} | {s['turn']:.2f} | {s['resp']:.2f} | {s['sw']} | {s['maxwait']} |")
hdr = "| Алгоритм | ср. ожидание | ср. оборот | ср. отклик | перекл. | макс. ожидание |\n|---|---|---|---|---|---|"
print("## A: jobs.txt"); print(hdr)
P = load("jobs.txt")
for n, f in [("FCFS", fcfs), ("SJF", sjf), ("RR q=2", lambda p: rr(p, 2))]: row(n, P, f(P))
print("\n## set1.txt (самопроверка)"); print(hdr)
P = load("set1.txt")
for n, f in [("FCFS", fcfs), ("SJF", sjf), ("RR q=2", lambda p: rr(p, 2)), ("SRTF", srtf), ("Priority", priority)]: row(n, P, f(P))
print("\n## B: mixed.txt, 5 алгоритмов"); print(hdr)
P = load("mixed.txt")
for n, f in [("FCFS", fcfs), ("SJF", sjf), ("RR q=2", lambda p: rr(p, 2)), ("SRTF", srtf), ("Priority", priority)]: row(n, P, f(P))
print("\n## B: RR, q=1..10"); print(hdr)
for q in range(1, 11): row(f"RR q={q}", P, rr(P, q))
print("\n## C: MLFQ vs SRTF vs RR (mixed)"); print(hdr)
for n, f in [("SRTF", srtf), ("RR q=2", lambda p: rr(p, 2)), ("RR q=4", lambda p: rr(p, 4)),
             ("MLFQ 2/4/8 boost50", mlfq), ("MLFQ boost25", lambda p: mlfq(p, boost=25)), ("MLFQ без boost", lambda p: mlfq(p, boost=0))]:
    row(n, P, f(P))
