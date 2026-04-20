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
OVERLEAF_DATA_DIR = REPO_ROOT / "overleaf" / "data"

REDUCED_RUNS_CSV = OVERLEAF_DATA_DIR / "optimality_reduced_days_runs.csv"
REDUCED_AGG_CSV = OVERLEAF_DATA_DIR / "optimality_reduced_days_agg.csv"
RESTORED_RUNS_CSV = OVERLEAF_DATA_DIR / "optimality_restored_days_runs.csv"
RESTORED_AGG_CSV = OVERLEAF_DATA_DIR / "optimality_restored_days_agg.csv"
COMPARISON_CSV = OVERLEAF_DATA_DIR / "optimality_days_comparison.csv"

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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


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


def run_scheduler(pref_path: Path, constraints_path: Path, days_mode: str) -> tuple[float, dict[str, str], str]:
    env = dict(os.environ)
    env["SCHED_NO_OUTPUT"] = "1"
    env["SCHED_SUMMARY"] = "1"
    env["SCHED_DAYS_MODE"] = days_mode
    argv = [sys.executable, str(REPO_ROOT / "greedy_algorithm.py"), str(pref_path), str(constraints_path)]
    t0 = time.perf_counter()
    proc = subprocess.run(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, env=env)
    elapsed = time.perf_counter() - t0
    stderr_text = proc.stderr or ""
    if proc.returncode != 0:
        raise RuntimeError(
            f"Scheduler failed for {constraints_path.name}\n"
            f"stderr:\n{stderr_text}"
        )
    return elapsed, parse_summary(stderr_text), stderr_text


def collect_runs(days_mode: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seed_dirs = sorted(EXPERIMENTS_DIR.glob("optimality_seed_*"))
    for seed_dir in seed_dirs:
        for constraints_path in sorted(seed_dir.glob("*_c.txt")):
            case = constraints_path.stem.removesuffix("_c")
            pref_path = seed_dir / f"{case}_p.txt"
            elapsed, summary, _stderr_text = run_scheduler(pref_path, constraints_path, days_mode)
            rows.append(
                {
                    "case": case,
                    "case_tex": case.replace("_", "\\_"),
                    "seed": int(seed_dir.name.rsplit("_", 1)[1]),
                    "optimality": float(summary["optimality"]),
                    "scheduling_seconds": elapsed,
                }
            )
            print(
                f"{days_mode} {seed_dir.name}/{case}: optimality={float(summary['optimality']):.4f} "
                f"time={elapsed:.4f}s",
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
        opt = summarize([float(r["optimality"]) for r in case_rows])
        sched = summarize([float(r["scheduling_seconds"]) for r in case_rows])
        agg_rows.append(
            {
                "case": case,
                "case_tex": case.replace("_", "\\_"),
                "optimality_mean": opt.mean,
                "optimality_stdev": opt.stdev,
                "optimality_min": opt.min,
                "optimality_max": opt.max,
                "scheduling_seconds_mean": sched.mean,
                "runs": opt.n,
            }
        )
    return agg_rows


def fmt(value: float) -> str:
    return f"{value:.3f}"


def fmt_delta(value: float) -> str:
    return f"{value:+.3f}"


def render_optimality_table(title: str, rows: list[dict[str, str]], out_name: str) -> None:
    table_rows = []
    for row in rows:
        table_rows.append(
            [
                row["case"].replace("_", " "),
                row["runs"],
                fmt(float(row["optimality_mean"])),
                fmt(float(row["optimality_min"])),
                fmt(float(row["optimality_max"])),
            ]
        )
    render_jpegs.table_jpeg(
        title,
        ["Scenario", "Runs", "Mean", "Min", "Max"],
        table_rows,
        out_name,
    )


def render_comparison_table(
    reduced_rows: list[dict[str, str]],
    restored_rows: list[dict[str, str]],
    out_name: str,
) -> list[dict[str, object]]:
    reduced_by_case = {row["case"]: row for row in reduced_rows}
    restored_by_case = {row["case"]: row for row in restored_rows}
    all_cases = sorted(set(reduced_by_case) | set(restored_by_case), key=case_sort_key)

    comparison_rows: list[dict[str, object]] = []
    table_rows: list[list[str]] = []
    for case in all_cases:
        reduced = reduced_by_case[case]
        restored = restored_by_case[case]
        mean_before = float(reduced["optimality_mean"])
        min_before = float(reduced["optimality_min"])
        max_before = float(reduced["optimality_max"])
        mean_after = float(restored["optimality_mean"])
        min_after = float(restored["optimality_min"])
        max_after = float(restored["optimality_max"])
        comparison_rows.append(
            {
                "case": case,
                "runs_reduced": reduced["runs"],
                "runs_restored": restored["runs"],
                "mean_reduced": mean_before,
                "mean_restored": mean_after,
                "mean_delta": mean_after - mean_before,
                "min_reduced": min_before,
                "min_restored": min_after,
                "min_delta": min_after - min_before,
                "max_reduced": max_before,
                "max_restored": max_after,
                "max_delta": max_after - max_before,
            }
        )
        table_rows.append(
            [
                case.replace("_", " "),
                fmt(mean_before),
                fmt(mean_after),
                fmt_delta(mean_after - mean_before),
                fmt(min_before),
                fmt(min_after),
                fmt(max_before),
                fmt(max_after),
            ]
        )

    render_jpegs.table_jpeg(
        "OPTIMALITY TABLE:  STANDARD DAYS VS NON-STANDARD DAYS",
        ["Scenario", "Mean Standard", "Mean Non-Standard", "Delta", "Min Standard", "Min Non-Standard", "Max Standard", "Max Non-Standard"],
        table_rows,
        out_name,
    )
    return comparison_rows


def main() -> int:
    reduced_runs = collect_runs("reduced")
    restored_runs = collect_runs("full")

    reduced_agg = aggregate_runs(reduced_runs)
    restored_agg = aggregate_runs(restored_runs)

    write_csv(
        REDUCED_RUNS_CSV,
        ["case", "case_tex", "seed", "optimality", "scheduling_seconds"],
        reduced_runs,
    )
    write_csv(
        REDUCED_AGG_CSV,
        [
            "case",
            "case_tex",
            "optimality_mean",
            "optimality_stdev",
            "optimality_min",
            "optimality_max",
            "scheduling_seconds_mean",
            "runs",
        ],
        reduced_agg,
    )
    write_csv(
        RESTORED_RUNS_CSV,
        ["case", "case_tex", "seed", "optimality", "scheduling_seconds"],
        restored_runs,
    )
    write_csv(
        RESTORED_AGG_CSV,
        [
            "case",
            "case_tex",
            "optimality_mean",
            "optimality_stdev",
            "optimality_min",
            "optimality_max",
            "scheduling_seconds_mean",
            "runs",
        ],
        restored_agg,
    )

    render_optimality_table(
        "TABLE: STANDARD DAYS",
        [{k: str(v) for k, v in row.items()} for row in reduced_agg],
        "optimality_table_reduced_days",
    )
    render_optimality_table(
        "TABLE: NON-STANDARD DAYS",
        [{k: str(v) for k, v in row.items()} for row in restored_agg],
        "optimality_table_restored_days",
    )
    comparison_rows = render_comparison_table(
        [{k: str(v) for k, v in row.items()} for row in reduced_agg],
        [{k: str(v) for k, v in row.items()} for row in restored_agg],
        "optimality_table_days_comparison",
    )
    write_csv(
        COMPARISON_CSV,
        [
            "case",
            "runs_reduced",
            "runs_restored",
            "mean_reduced",
            "mean_restored",
            "mean_delta",
            "min_reduced",
            "min_restored",
            "min_delta",
            "max_reduced",
            "max_restored",
            "max_delta",
        ],
        comparison_rows,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
