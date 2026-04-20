#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import subprocess
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "overleaf" / "data"


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


def benchmark_classes_100000(seed: int = 600) -> tuple[float, float]:
    constraints = Path("/tmp/classes_100000_c.txt")
    prefs = Path("/tmp/classes_100000_p.txt")

    # Generate inputs.
    gen_cmd = [
        "python3",
        str(REPO_ROOT / "generate_random_data.py"),
        "--output",
        str(constraints),
        "--student-pref",
        str(prefs),
        "--classes",
        "100000",
        "--students",
        "100",
        "--rooms",
        "30",
        "--class-times",
        "15",
        "--min-rooms-per-building",
        "1",
        "--seed",
        str(seed),
    ]
    t0 = time.perf_counter()
    subprocess.run(gen_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    gen_s = time.perf_counter() - t0

    # Schedule (suppress massive stdout).
    env = dict(os.environ)
    env["SCHED_NO_OUTPUT"] = "1"
    sched_cmd = [
        "python3",
        str(REPO_ROOT / "greedy_algorithm.py"),
        str(prefs),
        str(constraints),
    ]
    t1 = time.perf_counter()
    subprocess.run(sched_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    sched_s = time.perf_counter() - t1
    return gen_s, sched_s


def main() -> None:
    base = DATA_DIR / "class_scale_agg.csv"
    if not base.exists():
        raise SystemExit("Missing overleaf/data/class_scale_agg.csv. Run: python3 overleaf/build_overleaf_assets.py")

    rows = read_csv(base)
    existing = {int(r["classes"]) for r in rows}

    out_rows: list[dict[str, object]] = []
    for r in rows:
        out_rows.append(
            {
                "classes": int(r["classes"]),
                "scheduling_seconds_mean": float(r["scheduling_seconds_mean"]),
                "optimality_mean": float(r["optimality_mean"]),
                "runs": int(r["runs"]),
            }
        )

    if 100000 not in existing:
        gen_s, sched_s = benchmark_classes_100000()
        out_rows.append(
            {
                "classes": 100000,
                "scheduling_seconds_mean": sched_s,
                "optimality_mean": "",  # not computed in this quick benchmark
                "runs": 1,
            }
        )
        # Write a small note so the write-up can cite where the point came from.
        (DATA_DIR / "class_scale_100000_note.txt").write_text(
            f"classes=100000 benchmark (seed=600): generation_seconds={gen_s:.4f}, scheduling_seconds={sched_s:.4f}\n",
            encoding="utf-8",
        )

    out_rows.sort(key=lambda r: int(r["classes"]))
    write_csv(
        DATA_DIR / "class_scale_extended.csv",
        ["classes", "scheduling_seconds_mean", "optimality_mean", "runs"],
        out_rows,
    )


if __name__ == "__main__":
    main()

