#!/usr/bin/env python3
# Авторы: Камыталиев Даниел, Эшанкулов Муса, Арсен Алмазов
"""Планировщик учебного сервера: FCFS, SJF, RR, SRTF, Priority(preemptive),
Priority+aging, MLFQ.  Время дискретное (1 тик).  Меньше число приоритета = выше приоритет.

Соглашения:
  * равенство ключа -> раньше пришёл, затем меньший PID;
    у вытесняющих алгоритмов при полном равенстве продолжает текущий процесс;
  * RR: процесс, пришедший в момент t, встаёт в очередь РАНЬШЕ процесса,
    у которого в момент t закончился квант;
  * переключение контекста = смена исполняемого процесса на другой (простой CPU не считается).
"""
import sys
from collections import deque


def load(path):
    procs = []
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if not line:
            continue
        pid, a, b, p = line.split()
        procs.append(dict(pid=pid, arr=int(a), burst=int(b), prio=int(p)))
    return procs


# ---------------------------------------------------------------- алгоритмы
# каждый возвращает timeline: список pid (или None = простой) по тикам 0..T-1

def fcfs(procs):
    tl, t = [], 0
    for p in sorted(procs, key=lambda p: (p["arr"], p["pid"])):
        while t < p["arr"]:
            tl.append(None); t += 1
        tl += [p["pid"]] * p["burst"]; t += p["burst"]
    return tl


def sjf(procs):  # невытесняющий
    left = list(procs); tl, t = [], 0
    while left:
        ready = [p for p in left if p["arr"] <= t]
        if not ready:
            tl.append(None); t += 1; continue
        p = min(ready, key=lambda p: (p["burst"], p["arr"], p["pid"]))
        left.remove(p)
        tl += [p["pid"]] * p["burst"]; t += p["burst"]
    return tl


def _preemptive(procs, keyfn):
    rem = {p["pid"]: p["burst"] for p in procs}
    tl, t, cur = [], 0, None
    while any(rem.values()):
        ready = [p for p in procs if p["arr"] <= t and rem[p["pid"]] > 0]
        if not ready:
            tl.append(None); t += 1; cur = None; continue
        best = min(ready, key=lambda p: (keyfn(p, rem, t, cur),
                                         0 if p["pid"] == cur else 1,
                                         p["arr"], p["pid"]))
        cur = best["pid"]
        tl.append(cur); rem[cur] -= 1; t += 1
    return tl


def srtf(procs):
    return _preemptive(procs, lambda p, rem, t, cur: rem[p["pid"]])


def priority(procs):  # вытесняющий
    return _preemptive(procs, lambda p, rem, t, cur: p["prio"])


def priority_aging(procs, step=5, floor=0):
    """Старение: за каждые `step` тиков ожидания в очереди готовых приоритет
    улучшается на 1 (число уменьшается, не ниже `floor`). Пока процесс исполняется,
    накопленная «льгота» сохраняется; когда его вытесняют — счётчик обнуляется."""
    rem = {p["pid"]: p["burst"] for p in procs}
    waited = {p["pid"]: 0 for p in procs}
    tl, t, cur = [], 0, None
    while any(rem.values()):
        ready = [p for p in procs if p["arr"] <= t and rem[p["pid"]] > 0]
        if not ready:
            tl.append(None); t += 1; cur = None; continue
        eff = lambda p: max(floor, p["prio"] - waited[p["pid"]] // step)
        best = min(ready, key=lambda p: (eff(p), 0 if p["pid"] == cur else 1, p["arr"], p["pid"]))
        if cur is not None and best["pid"] != cur:
            waited[cur] = 0                  # текущего вытеснили -> льгота сгорает
        cur = best["pid"]
        tl.append(cur); rem[cur] -= 1; t += 1
        for p in ready:
            if p["pid"] != cur:
                waited[p["pid"]] += 1
    return tl


def rr(procs, q):
    rem = {p["pid"]: p["burst"] for p in procs}
    order = sorted(procs, key=lambda p: (p["arr"], p["pid"]))
    queue, tl, t, i = deque(), [], 0, 0
    def admit(t):
        nonlocal i
        while i < len(order) and order[i]["arr"] <= t:
            queue.append(order[i]["pid"]); i += 1
    admit(0)
    while queue or i < len(order):
        if not queue:
            tl.append(None); t += 1; admit(t); continue
        pid = queue.popleft()
        run = min(q, rem[pid])
        for _ in range(run):
            tl.append(pid); t += 1; rem[pid] -= 1
            admit(t)               # приходящие в ходе кванта (и ровно в конце) — раньше вытесняемого
        if rem[pid] > 0:
            queue.append(pid)
    return tl


def mlfq(procs, quanta=(2, 4, 8), boost=50):
    """3 очереди. Новый процесс -> уровень 0. Израсходовал весь квант -> уровнем ниже
    (на нижнем уровне RR с его квантом). Ушёл/вытеснен до исчерпания кванта -> остаётся на уровне.
    Пришедший процесс более высокого уровня вытесняет текущий (тот уходит в хвост своего уровня).
    Каждые `boost` тиков все готовые процессы возвращаются на уровень 0."""
    L = len(quanta)
    rem = {p["pid"]: p["burst"] for p in procs}
    order = sorted(procs, key=lambda p: (p["arr"], p["pid"]))
    queues = [deque() for _ in range(L)]
    level = {}
    tl, t, i = [], 0, 0
    cur, used = None, 0

    def admit(t):
        nonlocal i
        while i < len(order) and order[i]["arr"] <= t:
            pid = order[i]["pid"]; level[pid] = 0; queues[0].append(pid); i += 1

    def do_boost():
        for lv in range(1, L):
            while queues[lv]:
                pid = queues[lv].popleft(); level[pid] = 0; queues[0].append(pid)
        if cur is not None:
            level[cur] = 0

    admit(0)
    while any(rem.values()):
        if t > 0 and boost and t % boost == 0:
            do_boost()
        # вытеснение пришедшим на более высоком уровне
        if cur is not None:
            higher = any(queues[lv] for lv in range(level[cur]))
            if higher:
                queues[level[cur]].append(cur); cur, used = None, 0
        if cur is None:
            for lv in range(L):
                if queues[lv]:
                    cur = queues[lv].popleft(); used = 0; break
        if cur is None:
            tl.append(None); t += 1; admit(t); continue
        tl.append(cur); rem[cur] -= 1; used += 1; t += 1
        admit(t)
        if rem[cur] == 0:
            cur, used = None, 0
        elif used >= quanta[level[cur]]:
            if level[cur] < L - 1:
                level[cur] += 1
            queues[level[cur]].append(cur); cur, used = None, 0
    return tl


# ---------------------------------------------------------------- метрики
def metrics(procs, tl):
    first, last = {}, {}
    for t, pid in enumerate(tl):
        if pid is None:
            continue
        first.setdefault(pid, t); last[pid] = t + 1
    res = {}
    for p in procs:
        pid = p["pid"]
        ta = last[pid] - p["arr"]
        res[pid] = dict(start=first[pid], finish=last[pid], turnaround=ta,
                        waiting=ta - p["burst"], response=first[pid] - p["arr"])
    seq = [x for x in tl if x is not None]
    sw = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
    return res, sw


def summary(procs, tl):
    res, sw = metrics(procs, tl)
    n = len(procs)
    avg = lambda k: sum(r[k] for r in res.values()) / n
    return dict(wait=avg("waiting"), turn=avg("turnaround"), resp=avg("response"),
                sw=sw, maxwait=max(r["waiting"] for r in res.values()),
                makespan=len(tl), per=res)


def segments(tl):
    segs, start = [], 0
    for t in range(1, len(tl) + 1):
        if t == len(tl) or tl[t] != tl[start]:
            segs.append((start, t, tl[start])); start = t
    return segs


def gantt_text(tl):
    return " ".join(f"|{s}-{e}:{p or 'idle'}" for s, e, p in segments(tl)) + "|"


ALGOS = {
    "FCFS": fcfs, "SJF": sjf, "RR q=2": lambda p: rr(p, 2),
    "SRTF": srtf, "Priority": priority,
}

if __name__ == "__main__":
    f = sys.argv[1]
    procs = load(f)
    for name, fn in ALGOS.items():
        s = summary(procs, fn(procs))
        print(f"{name:10s} wait={s['wait']:.2f} turn={s['turn']:.2f} resp={s['resp']:.2f} sw={s['sw']}")
