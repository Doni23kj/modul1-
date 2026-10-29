#!/usr/bin/env bash
# Авторы: Камыталиев Даниел, Эшанкулов Муса, Арсен Алмазов
# Запуск одной командой на чистой Ubuntu (нужен только python3): bash run.sh
set -e
cd "$(dirname "$0")"
{
  python3 run_all.py
  echo; echo "## Диаграммы Ганта (текст)"
  python3 - <<'PY'
from scheduler import *
for f, n, fn in [("jobs.txt","FCFS",fcfs),("jobs.txt","SJF",sjf),("jobs.txt","RR q=2",lambda p:rr(p,2)),
                 ("starve.txt","Priority",priority),("starve.txt","Priority+aging step=3",lambda p:priority_aging(p,3))]:
    print(f"{f} {n}: {gantt_text(fn(load(f)))}")
PY
} | tee output.txt
python3 check.py | tee -a output.txt
python3 make_gantt.py || true
