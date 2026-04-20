from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "project" / "scripts" / "generate_duration_constraints.py"
SCHEDULER = ROOT / "greedy_algorithm.py"
VALIDATOR = ROOT / "is_valid_v2.pl"

SCHEDULE_PATTERN = re.compile(
    r"Course\tRoom\tTeacher\tTime\tDays\tStudents\n.*", re.DOTALL
)


@dataclass(frozen=True)
class Case:
    name: str
    seed: int
    class_times: int
    rooms: int
    classes: int
    min_rooms_per_building: int
    min_room_capacity: int
    max_room_capacity: int
    students: int
    credit_hours: str
    credit_hour_weights: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate multiple constraint/preference files, run greedy_algorithm.py "
            "on each, and record experiment results."
        )
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "experiments" / "optimality"),
        help="Directory where generated cases, schedules, and results.csv should be written.",
    )
    parser.add_argument(
        "--base-seed",
        type=int,
        default=100,
        help="Seed used for the first case. Later cases increment from this value.",
    )
    parser.add_argument(
        "--suite",
        choices=("default", "class-scale"),
        default="default",
        help="Which preset experiment suite to run.",
    )
    return parser.parse_args()


def build_cases(base_seed: int, suite: str) -> list[Case]:
    baseline = {
        "class_times": 15,
        "rooms": 30,
        "classes": 50,
        "min_rooms_per_building": 1,
        "min_room_capacity": 6,
        "max_room_capacity": 120,
        "students": 100,
        "credit_hours": "2,3,4",
        "credit_hour_weights": "0.15,0.55,0.30",
    }

    if suite == "class-scale":
        case_specs = [
            ("classes_10", {"classes": 10}),
            ("classes_100", {"classes": 100}),
            ("classes_1000", {"classes": 1000}),
            ("classes_10000", {"classes": 10000}),
        ]
    else:
        case_specs = [
            ("baseline", {}),
            ("rooms_20", {"rooms": 20}),
            ("rooms_40", {"rooms": 40}),
            ("class_times_12", {"class_times": 12}),
            ("class_times_18", {"class_times": 18}),
            ("students_75", {"students": 75}),
            ("students_150", {"students": 150}),
            ("capacity_tight", {"min_room_capacity": 6, "max_room_capacity": 60}),
            ("capacity_large", {"min_room_capacity": 40, "max_room_capacity": 140}),
            ("hours_more_short", {"credit_hour_weights": "0.45,0.40,0.15"}),
            ("hours_more_long", {"credit_hour_weights": "0.05,0.35,0.60"}),
        ]

    cases: list[Case] = []
    for index, (name, overrides) in enumerate(case_specs):
        params = dict(baseline)
        params.update(overrides)
        cases.append(Case(name=name, seed=base_seed + index, **params))
    return cases


def run_command(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def format_seconds(value: float) -> str:
    return f"{value:.4f}"


def extract_schedule(text: str) -> str:
    match = SCHEDULE_PATTERN.search(text)
    if not match:
        raise RuntimeError(f"Could not find schedule output.\n{text}")
    return match.group(0)


def count_total_requests(prefs_path: Path) -> int:
    total_requests = 0
    with prefs_path.open() as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("Students\t"):
                continue
            total_requests += max(0, len(line.split()) - 1)
    return total_requests


def count_successful_enrollments(schedule_text: str) -> int:
    total_successful = 0
    for line in schedule_text.splitlines()[1:]:
        if not line.strip():
            continue
        fields = line.split("\t", 5)
        if len(fields) != 6:
            raise RuntimeError(f"Unexpected schedule row format:\n{line}")
        students = fields[5].strip()
        if students:
            total_successful += len(students.split())
    return total_successful


def format_ratio(successful: int, couldnt_enroll: int) -> str:
    total_requests = successful + couldnt_enroll
    if total_requests == 0:
        return ""
    return f"{successful / total_requests:.4f}".rstrip("0").rstrip(".")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []

    for case in build_cases(args.base_seed, args.suite):
        constraints_path = output_dir / f"{case.name}_c.txt"
        prefs_path = output_dir / f"{case.name}_p.txt"
        schedule_path = output_dir / f"{case.name}_schedule.txt"

        generate_cmd = [
            sys.executable,
            str(GENERATOR),
            "--output",
            str(constraints_path),
            "--student-pref",
            str(prefs_path),
            "--seed",
            str(case.seed),
            "--class-times",
            str(case.class_times),
            "--rooms",
            str(case.rooms),
            "--classes",
            str(case.classes),
            "--min-rooms-per-building",
            str(case.min_rooms_per_building),
            "--min-room-capacity",
            str(case.min_room_capacity),
            "--max-room-capacity",
            str(case.max_room_capacity),
            "--students",
            str(case.students),
            "--credit-hours",
            case.credit_hours,
            "--credit-hour-weights",
            case.credit_hour_weights,
        ]
        started = time.perf_counter()
        generated = run_command(generate_cmd, ROOT)
        generation_seconds = time.perf_counter() - started
        if generated.returncode != 0:
            rows.append(
                {
                    "case": case.name,
                    "seed": str(case.seed),
                    "class_times": str(case.class_times),
                    "rooms": str(case.rooms),
                    "classes": str(case.classes),
                    "min_rooms_per_building": str(case.min_rooms_per_building),
                    "min_room_capacity": str(case.min_room_capacity),
                    "max_room_capacity": str(case.max_room_capacity),
                    "students": str(case.students),
                    "credit_hours": case.credit_hours,
                    "credit_hour_weights": case.credit_hour_weights,
                    "generation_seconds": format_seconds(generation_seconds),
                    "scheduling_seconds": "",
                    "couldnt_enroll": "",
                    "optimality": "",
                    "validation": "generation_failed",
                }
            )
            continue

        started = time.perf_counter()
        scheduled = run_command(
            [sys.executable, str(SCHEDULER), str(prefs_path), str(constraints_path)],
            ROOT,
        )
        scheduling_seconds = time.perf_counter() - started
        if scheduled.returncode != 0:
            rows.append(
                {
                    "case": case.name,
                    "seed": str(case.seed),
                    "class_times": str(case.class_times),
                    "rooms": str(case.rooms),
                    "classes": str(case.classes),
                    "min_rooms_per_building": str(case.min_rooms_per_building),
                    "min_room_capacity": str(case.min_room_capacity),
                    "max_room_capacity": str(case.max_room_capacity),
                    "students": str(case.students),
                    "credit_hours": case.credit_hours,
                    "credit_hour_weights": case.credit_hour_weights,
                    "generation_seconds": format_seconds(generation_seconds),
                    "scheduling_seconds": format_seconds(scheduling_seconds),
                    "couldnt_enroll": "",
                    "optimality": "",
                    "validation": "scheduling_failed",
                }
            )
            (output_dir / f"{case.name}_scheduler.stderr.txt").write_text(scheduled.stderr)
            continue
        schedule_text = extract_schedule(scheduled.stdout)
        schedule_path.write_text(schedule_text)

        total_requests = count_total_requests(prefs_path)
        successful = count_successful_enrollments(schedule_text)
        couldnt_enroll = max(0, total_requests - successful)
        validation_run = run_command(
            ["perl", str(VALIDATOR), str(constraints_path), str(prefs_path), str(schedule_path)],
            ROOT,
        )
        validation = "valid" if validation_run.returncode == 0 else "invalid"
        if validation_run.returncode != 0:
            (output_dir / f"{case.name}_validator.stderr.txt").write_text(
                validation_run.stdout + validation_run.stderr
            )

        rows.append(
            {
                "case": case.name,
                "seed": str(case.seed),
                "class_times": str(case.class_times),
                "rooms": str(case.rooms),
                "classes": str(case.classes),
                "min_rooms_per_building": str(case.min_rooms_per_building),
                "min_room_capacity": str(case.min_room_capacity),
                "max_room_capacity": str(case.max_room_capacity),
                "students": str(case.students),
                "credit_hours": case.credit_hours,
                "credit_hour_weights": case.credit_hour_weights,
                "generation_seconds": format_seconds(generation_seconds),
                "scheduling_seconds": format_seconds(scheduling_seconds),
                "couldnt_enroll": str(couldnt_enroll),
                "optimality": format_ratio(successful, couldnt_enroll),
                "validation": validation,
            }
        )

    results_path = output_dir / "results.csv"
    with results_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {results_path}")


if __name__ == "__main__":
    main()
