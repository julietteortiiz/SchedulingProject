#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import time
from pathlib import Path

import render_jpegs


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKDIR = REPO_ROOT / "experiments" / "class_scale"
DEFAULT_RESULTS_CSV = DEFAULT_WORKDIR / "results.csv"
DEFAULT_OVERLEAF_CLASS_SCALE_CSV = REPO_ROOT / "overleaf" / "data" / "class_scale_agg.csv"


def parse_sizes(raw: str) -> list[int]:
    sizes = []
    for piece in raw.split(","):
        piece = piece.strip()
        if not piece:
            continue
        sizes.append(int(piece))
    if not sizes:
        raise argparse.ArgumentTypeError("Provide at least one class size.")
    return sizes


def parse_summary(stderr_text: str) -> dict[str, str]:
    if "SCHED_SUMMARY" not in stderr_text:
        return {}
    lines = stderr_text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == "SCHED_SUMMARY"), None)
    if start is None:
        return {}
    out: dict[str, str] = {}
    for line in lines[start + 1 :]:
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def run_cmd(argv: list[str], *, env: dict[str, str] | None = None) -> tuple[float, subprocess.CompletedProcess]:
    t0 = time.perf_counter()
    proc = subprocess.run(argv, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    t1 = time.perf_counter()
    return t1 - t0, proc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run greedy scheduler at multiple class sizes and render a JPEG runtime plot."
    )
    parser.add_argument(
        "--sizes",
        type=parse_sizes,
        default=parse_sizes("10,100,1000,10000,100000"),
        help="Comma-separated class counts to benchmark. Default: 10,100,1000,10000,100000.",
    )
    parser.add_argument("--seed-start", type=int, default=100, help="Seed used for the smallest size. Default: 100.")
    parser.add_argument("--class-times", type=int, default=15, help="Number of time blocks. Default: 15.")
    parser.add_argument("--rooms", type=int, default=30, help="Number of rooms. Default: 30.")
    parser.add_argument(
        "--min-rooms-per-building",
        type=int,
        default=1,
        help="Minimum rooms per building. Default: 1.",
    )
    parser.add_argument("--students", type=int, default=100, help="Number of students. Default: 100.")
    parser.add_argument("--min-room-capacity", type=int, default=6, help="Minimum room capacity. Default: 6.")
    parser.add_argument("--max-room-capacity", type=int, default=120, help="Maximum room capacity. Default: 120.")
    parser.add_argument(
        "--workdir",
        type=Path,
        default=DEFAULT_WORKDIR,
        help=f"Where to write generated inputs. Default: {DEFAULT_WORKDIR}.",
    )
    parser.add_argument(
        "--results-csv",
        type=Path,
        default=DEFAULT_RESULTS_CSV,
        help=f"Where to write the per-run results CSV. Default: {DEFAULT_RESULTS_CSV}.",
    )
    parser.add_argument(
        "--overleaf-class-scale-csv",
        type=Path,
        default=DEFAULT_OVERLEAF_CLASS_SCALE_CSV,
        help=(
            "Where to write the plotting CSV consumed by overleaf/render_jpegs.py. "
            f"Default: {DEFAULT_OVERLEAF_CLASS_SCALE_CSV}."
        ),
    )
    parser.add_argument("--force", action="store_true", help="Regenerate inputs and rerun even if files exist.")
    args = parser.parse_args()

    args.workdir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    plot_rows: list[dict[str, str]] = []

    for i, classes in enumerate(args.sizes):
        seed = args.seed_start + i
        case = f"classes_{classes}"
        constraints_path = args.workdir / f"{case}_c.txt"
        prefs_path = args.workdir / f"{case}_p.txt"
        stderr_path = args.workdir / f"{case}_scheduler.stderr.txt"

        if args.force or not (constraints_path.exists() and prefs_path.exists()):
            gen_argv = [
                sys.executable,
                str(REPO_ROOT / "generate_random_data.py"),
                "--output",
                str(constraints_path),
                "--student-pref",
                str(prefs_path),
                "--classes",
                str(classes),
                "--students",
                str(args.students),
                "--rooms",
                str(args.rooms),
                "--class-times",
                str(args.class_times),
                "--min-rooms-per-building",
                str(args.min_rooms_per_building),
                "--min-room-capacity",
                str(args.min_room_capacity),
                "--max-room-capacity",
                str(args.max_room_capacity),
                "--seed",
                str(seed),
            ]
            generation_seconds, gen_proc = run_cmd(gen_argv)
            if gen_proc.returncode != 0:
                sys.stderr.write(gen_proc.stderr or "")
                raise SystemExit(f"Failed to generate inputs for {classes} classes (seed={seed}).")
        else:
            generation_seconds = 0.0

        env = dict(os.environ)
        env["SCHED_NO_OUTPUT"] = "1"
        env["SCHED_SUMMARY"] = "1"

        sched_argv = [
            sys.executable,
            str(REPO_ROOT / "greedy_algorithm.py"),
            str(prefs_path),
            str(constraints_path),
        ]
        scheduling_seconds, sched_proc = run_cmd(sched_argv, env=env)
        stderr_text = sched_proc.stderr or ""
        stderr_path.write_text(stderr_text, encoding="utf-8")
        if sched_proc.returncode != 0:
            raise SystemExit(
                f"Scheduler failed for {classes} classes (seed={seed}). See: {stderr_path}"
            )

        summary = parse_summary(stderr_text)
        couldnt_enroll = summary.get("couldnt_enroll", "")
        optimality = summary.get("optimality", "")

        rows.append(
            {
                "case": case,
                "seed": str(seed),
                "class_times": str(args.class_times),
                "rooms": str(args.rooms),
                "classes": str(classes),
                "min_rooms_per_building": str(args.min_rooms_per_building),
                "min_room_capacity": str(args.min_room_capacity),
                "max_room_capacity": str(args.max_room_capacity),
                "students": str(args.students),
                "credit_hours": "2,3,4",
                "credit_hour_weights": "0.15,0.55,0.30",
                "generation_seconds": f"{generation_seconds:.4f}",
                "scheduling_seconds": f"{scheduling_seconds:.4f}",
                "couldnt_enroll": str(couldnt_enroll),
                "optimality": str(optimality),
                "validation": "",
            }
        )

        plot_rows.append(
            {
                "classes": str(classes),
                "scheduling_seconds_mean": f"{scheduling_seconds:.6f}",
            }
        )

        print(f"{classes} classes: {scheduling_seconds:.3f}s", file=sys.stderr)

    # Write the per-run experiment CSV in the same schema used elsewhere in the repo.
    fieldnames = [
        "case",
        "seed",
        "class_times",
        "rooms",
        "classes",
        "min_rooms_per_building",
        "min_room_capacity",
        "max_room_capacity",
        "students",
        "credit_hours",
        "credit_hour_weights",
        "generation_seconds",
        "scheduling_seconds",
        "couldnt_enroll",
        "optimality",
        "validation",
    ]
    args.results_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.results_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    overleaf_fieldnames = ["classes", "scheduling_seconds_mean"]
    args.overleaf_class_scale_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.overleaf_class_scale_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=overleaf_fieldnames)
        writer.writeheader()
        for row in plot_rows:
            writer.writerow({k: row[k] for k in overleaf_fieldnames})

    # Render the JPEG runtime plot.
    render_jpegs.OUT_DIR.mkdir(parents=True, exist_ok=True)
    render_jpegs.time_analysis_jpeg(plot_rows)
    print(f"Wrote {args.results_csv}", file=sys.stderr)
    print(f"Wrote {args.overleaf_class_scale_csv}", file=sys.stderr)
    print(f"Wrote {render_jpegs.OUT_DIR / 'time_analysis.jpg'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
