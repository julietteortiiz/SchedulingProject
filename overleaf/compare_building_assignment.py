#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import render_jpegs


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
DATA_DIR = REPO_ROOT / "overleaf" / "data"

MAPPED_RUNS_CSV = DATA_DIR / "building_assignment_mapped_runs.csv"
MAPPED_AGG_CSV = DATA_DIR / "building_assignment_mapped_agg.csv"
RANDOM_RUNS_CSV = DATA_DIR / "building_assignment_random_runs.csv"
RANDOM_AGG_CSV = DATA_DIR / "building_assignment_random_agg.csv"
SUMMARY_CSV = DATA_DIR / "building_assignment_summary.csv"
SCENARIO_CSV = DATA_DIR / "building_assignment_scenario_comparison.csv"

DESIRED_ORDER = [
    "baseline",
    "rooms_20",
    "rooms_40",
    "class_times_12",
    "class_times_18",
    "students_75",
    "students_150",
    "capacity_tight",
    "capacity_large",
    "hours_more_short",
    "hours_more_long",
]


@dataclass(frozen=True)
class Summary:
    mean: float
    stdev: float
    min: float
    max: float
    n: int


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def summarize(values: list[float]) -> Summary:
    if len(values) == 1:
        value = values[0]
        return Summary(value, 0.0, value, value, 1)
    return Summary(
        mean=statistics.mean(values),
        stdev=statistics.stdev(values),
        min=min(values),
        max=max(values),
        n=len(values),
    )


def parse_summary(stderr_text: str) -> dict[str, str]:
    lines = stderr_text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == "SCHED_SUMMARY"), None)
    if start is None:
        return {}
    parsed: dict[str, str] = {}
    for line in lines[start + 1 :]:
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def case_sort_key(case: str) -> tuple[int, str]:
    if case in DESIRED_ORDER:
        return (DESIRED_ORDER.index(case), case)
    return (len(DESIRED_ORDER), case)


def run_scheduler(pref_path: Path, constraints_path: Path, building_mode: str, random_seed: int) -> tuple[float, dict[str, str]]:
    env = dict(os.environ)
    env["SCHED_NO_OUTPUT"] = "1"
    env["SCHED_SUMMARY"] = "1"
    env["SCHED_BUILDING_MODE"] = building_mode
    env["SCHED_BUILDING_RANDOM_SEED"] = str(random_seed)
    argv = [sys.executable, str(REPO_ROOT / "greedy_algorithm.py"), str(pref_path), str(constraints_path)]
    t0 = time.perf_counter()
    proc = subprocess.run(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, env=env)
    elapsed = time.perf_counter() - t0
    stderr_text = proc.stderr or ""
    if proc.returncode != 0:
        raise RuntimeError(f"Scheduler failed for {constraints_path.name}\n{stderr_text}")
    return elapsed, parse_summary(stderr_text)


def collect_runs(building_mode: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for seed_dir in sorted(EXPERIMENTS_DIR.glob("optimality_seed_*")):
        scenario_seed = int(seed_dir.name.rsplit("_", 1)[1])
        for constraints_path in sorted(seed_dir.glob("*_c.txt")):
            case = constraints_path.stem.removesuffix("_c")
            pref_path = seed_dir / f"{case}_p.txt"
            random_seed = scenario_seed * 1000 + sum(ord(ch) for ch in case)
            elapsed, summary = run_scheduler(pref_path, constraints_path, building_mode, random_seed)
            rows.append(
                {
                    "case": case,
                    "seed": scenario_seed,
                    "optimality": float(summary["optimality"]),
                    "couldnt_enroll": int(summary["couldnt_enroll"]),
                    "student_pref_value": int(summary["student_pref_value"]),
                    "best_case_pref_value": int(summary["best_case_pref_value"]),
                    "scheduling_seconds": elapsed,
                }
            )
            print(
                f"{building_mode} {seed_dir.name}/{case}: optimality={float(summary['optimality']):.4f} "
                f"couldnt_enroll={int(summary['couldnt_enroll'])}",
                file=sys.stderr,
            )
    rows.sort(key=lambda row: (case_sort_key(str(row["case"])), int(row["seed"])))
    return rows


def aggregate_runs(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows_by_case: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        rows_by_case.setdefault(str(row["case"]), []).append(row)

    agg_rows: list[dict[str, object]] = []
    for case in sorted(rows_by_case, key=case_sort_key):
        case_rows = rows_by_case[case]
        optimality = summarize([float(r["optimality"]) for r in case_rows])
        blocked = summarize([float(r["couldnt_enroll"]) for r in case_rows])
        scheduling = summarize([float(r["scheduling_seconds"]) for r in case_rows])
        agg_rows.append(
            {
                "case": case,
                "optimality_mean": optimality.mean,
                "optimality_min": optimality.min,
                "optimality_max": optimality.max,
                "couldnt_enroll_mean": blocked.mean,
                "scheduling_seconds_mean": scheduling.mean,
                "runs": optimality.n,
            }
        )
    return agg_rows


def fmt(value: float) -> str:
    return f"{value:.3f}"


def fmt_delta(value: float) -> str:
    return f"{value:+.3f}"


def fmt_blocked(value: float) -> str:
    return f"{value:.1f}"


def summarize_mode(name: str, rows: list[dict[str, object]]) -> dict[str, object]:
    optimality = summarize([float(r["optimality"]) for r in rows])
    blocked = summarize([float(r["couldnt_enroll"]) for r in rows])
    scheduling = summarize([float(r["scheduling_seconds"]) for r in rows])
    return {
        "mode": name,
        "runs": optimality.n,
        "optimality_mean": optimality.mean,
        "optimality_min": optimality.min,
        "optimality_max": optimality.max,
        "couldnt_enroll_mean": blocked.mean,
        "scheduling_seconds_mean": scheduling.mean,
    }


def render_summary_table(summary_rows: list[dict[str, object]]) -> None:
    rows = [
        [
            str(row["mode"]),
            str(row["runs"]),
            fmt(float(row["optimality_mean"])),
            fmt(float(row["optimality_min"])),
            fmt(float(row["optimality_max"])),
            fmt_blocked(float(row["couldnt_enroll_mean"])),
            fmt(float(row["scheduling_seconds_mean"])),
        ]
        for row in summary_rows
    ]
    render_jpegs.table_jpeg(
        "TABLE: DEPT BUILDINGS VS RANDOM BUILDINGS",
        ["Mode", "Runs", "Mean opt", "Min opt", "Max opt", "Mean blocked", "Mean sec"],
        rows,
        "building_assignment_comparison",
    )


def render_scenario_table(rows: list[dict[str, object]]) -> None:
    table_rows = []
    for row in rows:
        table_rows.append(
            [
                str(row["case"]).replace("_", " "),
                fmt(float(row["mapped_mean"])),
                fmt(float(row["random_mean"])),
                fmt_delta(float(row["delta_mean"])),
                fmt_blocked(float(row["mapped_blocked"])),
                fmt_blocked(float(row["random_blocked"])),
            ]
        )
    render_jpegs.table_jpeg(
        "TABLE: MAPPED VS RANDOM BUILDINGS BY SCENARIO",
        ["Scenario", "Mapped", "Random", "Delta", "Blk map", "Blk rnd"],
        table_rows,
        "building_assignment_scenarios",
    )


def main() -> int:
    mapped_runs = collect_runs("mapped")
    random_runs = collect_runs("random")
    mapped_agg = aggregate_runs(mapped_runs)
    random_agg = aggregate_runs(random_runs)

    write_csv(
        MAPPED_RUNS_CSV,
        ["case", "seed", "optimality", "couldnt_enroll", "student_pref_value", "best_case_pref_value", "scheduling_seconds"],
        mapped_runs,
    )
    write_csv(
        RANDOM_RUNS_CSV,
        ["case", "seed", "optimality", "couldnt_enroll", "student_pref_value", "best_case_pref_value", "scheduling_seconds"],
        random_runs,
    )
    write_csv(
        MAPPED_AGG_CSV,
        ["case", "optimality_mean", "optimality_min", "optimality_max", "couldnt_enroll_mean", "scheduling_seconds_mean", "runs"],
        mapped_agg,
    )
    write_csv(
        RANDOM_AGG_CSV,
        ["case", "optimality_mean", "optimality_min", "optimality_max", "couldnt_enroll_mean", "scheduling_seconds_mean", "runs"],
        random_agg,
    )

    mapped_summary = summarize_mode("dept mapped", mapped_runs)
    random_summary = summarize_mode("random bldg", random_runs)
    delta_summary = {
        "mode": "delta",
        "runs": mapped_summary["runs"],
        "optimality_mean": float(mapped_summary["optimality_mean"]) - float(random_summary["optimality_mean"]),
        "optimality_min": float(mapped_summary["optimality_min"]) - float(random_summary["optimality_min"]),
        "optimality_max": float(mapped_summary["optimality_max"]) - float(random_summary["optimality_max"]),
        "couldnt_enroll_mean": float(mapped_summary["couldnt_enroll_mean"]) - float(random_summary["couldnt_enroll_mean"]),
        "scheduling_seconds_mean": float(mapped_summary["scheduling_seconds_mean"]) - float(random_summary["scheduling_seconds_mean"]),
    }
    summary_rows = [mapped_summary, random_summary, delta_summary]
    write_csv(
        SUMMARY_CSV,
        ["mode", "runs", "optimality_mean", "optimality_min", "optimality_max", "couldnt_enroll_mean", "scheduling_seconds_mean"],
        summary_rows,
    )

    random_by_case = {str(row["case"]): row for row in random_agg}
    scenario_rows: list[dict[str, object]] = []
    for mapped_row in mapped_agg:
        case = str(mapped_row["case"])
        random_row = random_by_case[case]
        scenario_rows.append(
            {
                "case": case,
                "mapped_mean": mapped_row["optimality_mean"],
                "random_mean": random_row["optimality_mean"],
                "delta_mean": float(mapped_row["optimality_mean"]) - float(random_row["optimality_mean"]),
                "mapped_blocked": mapped_row["couldnt_enroll_mean"],
                "random_blocked": random_row["couldnt_enroll_mean"],
            }
        )
    write_csv(
        SCENARIO_CSV,
        ["case", "mapped_mean", "random_mean", "delta_mean", "mapped_blocked", "random_blocked"],
        scenario_rows,
    )

    render_summary_table(summary_rows)
    render_scenario_table(scenario_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
