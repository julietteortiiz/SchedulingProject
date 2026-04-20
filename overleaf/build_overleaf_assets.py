#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import statistics
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ALL_RESULTS_DIR = REPO_ROOT / "experiments" / "all_results"
OUT_DIR = REPO_ROOT / "overleaf"
DATA_DIR = OUT_DIR / "data"
TABLES_DIR = OUT_DIR / "tables"
FIGURES_DIR = OUT_DIR / "figures"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def latex_escape(text: str) -> str:
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("%", "\\%")
        .replace("&", "\\&")
        .replace("#", "\\#")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def f3(value: float) -> str:
    if value == 0:
        return "0"
    if abs(value) < 0.001:
        return f"{value:.2e}"
    if abs(value) >= 100:
        return f"{value:.0f}"
    return f"{value:.3f}"


@dataclass(frozen=True)
class Summary:
    mean: float
    stdev: float
    min: float
    max: float
    n: int


def summarize(values: list[float]) -> Summary:
    if not values:
        return Summary(mean=math.nan, stdev=math.nan, min=math.nan, max=math.nan, n=0)
    if len(values) == 1:
        v = values[0]
        return Summary(mean=v, stdev=0.0, min=v, max=v, n=1)
    return Summary(
        mean=statistics.mean(values),
        stdev=statistics.stdev(values),
        min=min(values),
        max=max(values),
        n=len(values),
    )


def aggregate_class_scale() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    paths = sorted(ALL_RESULTS_DIR.glob("class_scale_seed_*_results.csv"))
    rows_by_classes: dict[int, list[dict[str, str]]] = {}
    for path in paths:
        if "fixcheck" in path.name:
            continue
        for row in read_csv(path):
            classes = int(row["classes"])
            rows_by_classes.setdefault(classes, []).append(row)

    agg_rows: list[dict[str, object]] = []
    for classes in sorted(rows_by_classes):
        scheduling_seconds = [float(r["scheduling_seconds"]) for r in rows_by_classes[classes]]
        optimality = [float(r["optimality"]) for r in rows_by_classes[classes]]
        sched = summarize(scheduling_seconds)
        opt = summarize(optimality)
        agg_rows.append(
            {
                "classes": classes,
                "scheduling_seconds_mean": sched.mean,
                "scheduling_seconds_stdev": sched.stdev,
                "optimality_mean": opt.mean,
                "optimality_min": opt.min,
                "runs": sched.n,
            }
        )

    # Also produce a per-run flat file so pgfplots can plot jitter if desired.
    per_run: list[dict[str, object]] = []
    for classes, rows in rows_by_classes.items():
        for r in rows:
            per_run.append(
                {
                    "seed": int(r["seed"]),
                    "classes": classes,
                    "scheduling_seconds": float(r["scheduling_seconds"]),
                    "optimality": float(r["optimality"]),
                }
            )

    return agg_rows, per_run


def aggregate_optimality() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    paths = sorted(ALL_RESULTS_DIR.glob("optimality_seed_*_results.csv"))
    rows_by_case: dict[str, list[dict[str, str]]] = {}
    for path in paths:
        for row in read_csv(path):
            case = row["case"]
            rows_by_case.setdefault(case, []).append(row)

    desired_order = [
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
    cases = [c for c in desired_order if c in rows_by_case] + [
        c for c in sorted(rows_by_case) if c not in desired_order
    ]

    agg_rows: list[dict[str, object]] = []
    per_run: list[dict[str, object]] = []
    for case in cases:
        case_tex = case.replace("_", "\\_")
        optimality = [float(r["optimality"]) for r in rows_by_case[case]]
        scheduling_seconds = [float(r["scheduling_seconds"]) for r in rows_by_case[case]]
        opt = summarize(optimality)
        sched = summarize(scheduling_seconds)
        agg_rows.append(
            {
                "case": case,
                "case_tex": case_tex,
                "optimality_mean": opt.mean,
                "optimality_stdev": opt.stdev,
                "optimality_min": opt.min,
                "optimality_max": opt.max,
                "scheduling_seconds_mean": sched.mean,
                "runs": opt.n,
            }
        )
        for r in rows_by_case[case]:
            per_run.append(
                {
                    "case": case,
                    "case_tex": case_tex,
                    "seed": int(r["seed"]),
                    "optimality": float(r["optimality"]),
                    "scheduling_seconds": float(r["scheduling_seconds"]),
                }
            )

    return agg_rows, per_run


def write_tables(class_scale_agg: list[dict[str, object]], optimality_agg: list[dict[str, object]]) -> None:
    # Class scale table.
    class_lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Runtime scaling with the number of classes (mean over seeds 100--500).}",
        "\\label{tab:time-scale}",
        "\\begin{tabular}{rrrrr}",
        "\\toprule",
        "Classes & Runs & Mean time (s) & Stdev (s) & Mean quality \\\\",
        "\\midrule",
    ]
    for row in class_scale_agg:
        class_lines.append(
            f"{row['classes']} & {row['runs']} & {f3(float(row['scheduling_seconds_mean']))} & "
            f"{f3(float(row['scheduling_seconds_stdev']))} & {f3(float(row['optimality_mean']))} \\\\"
        )
    class_lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    write_text(TABLES_DIR / "class_scale.tex", "\n".join(class_lines))

    # Optimality scenario table.
    opt_lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Solution quality (fraction of best-case upper bound) across scenarios (mean over seeds 100--500).}",
        "\\label{tab:quality-scenarios}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Scenario & Runs & Mean & Min & Max \\\\",
        "\\midrule",
    ]
    for row in optimality_agg:
        scenario = latex_escape(str(row["case"]))
        opt_lines.append(
            f"{scenario} & {row['runs']} & {f3(float(row['optimality_mean']))} & "
            f"{f3(float(row['optimality_min']))} & {f3(float(row['optimality_max']))} \\\\"
        )
    opt_lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    write_text(TABLES_DIR / "optimality.tex", "\n".join(opt_lines))


def write_figures() -> None:
    # Runtime vs classes (log-log).
    write_text(
        FIGURES_DIR / "time_analysis.tex",
        "\n".join(
            [
                "\\begin{figure}[t]",
                "\\centering",
                "\\begin{tikzpicture}",
                "\\begin{axis}[",
                "  width=0.9\\linewidth,",
                "  height=6cm,",
                "  xmode=log, ymode=log,",
                "  log basis x={10}, log basis y={10},",
                "  xlabel={Number of classes},",
                "  ylabel={Scheduling time (seconds)},",
                "  grid=both,",
                "  legend style={at={(0.02,0.98)},anchor=north west},",
                "]",
                "\\addplot+[mark=*, thick] table [col sep=comma, x=classes, y=scheduling_seconds_mean] {overleaf/data/class_scale_agg.csv};",
                "\\addlegendentry{Mean over seeds}",
                "\\end{axis}",
                "\\end{tikzpicture}",
                "\\caption{Scheduling runtime as the number of classes increases.}",
                "\\label{fig:time-analysis}",
                "\\end{figure}",
                "",
            ]
        ),
    )

    # Scenario quality bar chart.
    write_text(
        FIGURES_DIR / "quality_analysis.tex",
        "\n".join(
            [
                "\\begin{figure}[t]",
                "\\centering",
                "\\begin{tikzpicture}",
                "\\begin{axis}[",
                "  width=0.98\\linewidth,",
                "  height=7cm,",
                "  ybar,",
                "  ymin=0, ymax=1,",
                "  ylabel={Quality (achieved / best-case upper bound)},",
                "  xlabel={Scenario},",
                "  symbolic x coords={baseline,rooms\\_20,rooms\\_40,class\\_times\\_12,class\\_times\\_18,students\\_75,students\\_150,capacity\\_tight,capacity\\_large,hours\\_more\\_short,hours\\_more\\_long},",
                "  xtick=data,",
                "  x tick label style={rotate=35, anchor=east},",
                "  bar width=9pt,",
                "  grid=y,",
                "]",
                "\\addplot table [col sep=comma, x=case_tex, y=optimality_mean] {overleaf/data/optimality_agg.csv};",
                "\\end{axis}",
                "\\end{tikzpicture}",
                "\\caption{Average solution quality across scenario variations (mean over seeds 100--500).}",
                "\\label{fig:quality-analysis}",
                "\\end{figure}",
                "",
            ]
        ),
    )


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    class_scale_agg, class_scale_runs = aggregate_class_scale()
    optimality_agg, optimality_runs = aggregate_optimality()

    write_csv(
        DATA_DIR / "class_scale_agg.csv",
        [
            "classes",
            "scheduling_seconds_mean",
            "scheduling_seconds_stdev",
            "optimality_mean",
            "optimality_min",
            "runs",
        ],
        class_scale_agg,
    )
    write_csv(
        DATA_DIR / "class_scale_runs.csv",
        ["seed", "classes", "scheduling_seconds", "optimality"],
        class_scale_runs,
    )
    write_csv(
        DATA_DIR / "optimality_agg.csv",
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
        optimality_agg,
    )
    write_csv(
        DATA_DIR / "optimality_runs.csv",
        ["case", "case_tex", "seed", "optimality", "scheduling_seconds"],
        optimality_runs,
    )

    write_tables(class_scale_agg, optimality_agg)
    write_figures()

    # A small summary snippet we can include in the write-up.
    global_min_quality = min(float(r["optimality"]) for r in optimality_runs) if optimality_runs else math.nan
    global_min_quality_case = min(optimality_runs, key=lambda r: float(r["optimality"])) if optimality_runs else None
    details = ""
    if global_min_quality_case is not None:
        details = f" (case={global_min_quality_case['case']}, seed={global_min_quality_case['seed']})"

    summary = [
        "Computed aggregates from experiments/all_results.",
        f"Minimum observed scenario quality: {f3(global_min_quality)}{details}",
        "",
    ]
    write_text(OUT_DIR / "summary.txt", "\n".join(summary))


if __name__ == "__main__":
    main()
