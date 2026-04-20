#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "overleaf" / "data"
OUT_DIR = REPO_ROOT / "overleaf" / "jpeg"


# --- Minimal bitmap font (5x7) ---
# Each glyph is 7 rows of 5 pixels (1=on, 0=off).
FONT_5X7: dict[str, tuple[str, ...]] = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "11000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "/": ("00001", "00010", "00100", "01000", "10000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00100", "01000", "10110", "00110", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "#": ("01010", "11111", "01010", "01010", "11111", "01010", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "11111", "00000", "11111", "00000", "00000", "00000"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "?": ("01110", "10001", "00010", "00100", "00100", "00000", "00100"),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


@dataclass
class RGB:
    r: int
    g: int
    b: int


WHITE = RGB(255, 255, 255)
BLACK = RGB(0, 0, 0)
GRAY = RGB(210, 210, 210)
DARK_GRAY = RGB(120, 120, 120)
BLUE = RGB(40, 90, 180)
ORANGE = RGB(220, 120, 40)


class Canvas:
    def __init__(self, width: int, height: int, bg: RGB = WHITE):
        self.width = width
        self.height = height
        self.pixels = bytearray([bg.r, bg.g, bg.b] * (width * height))

    def _idx(self, x: int, y: int) -> int:
        return (y * self.width + x) * 3

    def set(self, x: int, y: int, color: RGB) -> None:
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return
        i = self._idx(x, y)
        self.pixels[i] = color.r
        self.pixels[i + 1] = color.g
        self.pixels[i + 2] = color.b

    def fill_rect(self, x0: int, y0: int, x1: int, y1: int, color: RGB) -> None:
        x0 = max(0, min(self.width - 1, x0))
        x1 = max(0, min(self.width - 1, x1))
        y0 = max(0, min(self.height - 1, y0))
        y1 = max(0, min(self.height - 1, y1))
        if x1 < x0 or y1 < y0:
            return
        for y in range(y0, y1 + 1):
            row_start = self._idx(x0, y)
            for x in range(x0, x1 + 1):
                i = row_start + (x - x0) * 3
                self.pixels[i] = color.r
                self.pixels[i + 1] = color.g
                self.pixels[i + 2] = color.b

    def line(self, x0: int, y0: int, x1: int, y1: int, color: RGB, thickness: int = 1) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for tx in range(-thickness // 2, thickness // 2 + 1):
                for ty in range(-thickness // 2, thickness // 2 + 1):
                    self.set(x + tx, y + ty, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def text(self, x: int, y: int, s: str, color: RGB = BLACK, scale: int = 2) -> None:
        cx = x
        for ch in s:
            glyph = FONT_5X7.get(ch.upper(), FONT_5X7["?"])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.fill_rect(
                            cx + col * scale,
                            y + row * scale,
                            cx + col * scale + scale - 1,
                            y + row * scale + scale - 1,
                            color,
                        )
            cx += (5 + 1) * scale

    def save_ppm(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        header = f"P6\n{self.width} {self.height}\n255\n".encode("ascii")
        path.write_bytes(header + bytes(self.pixels))


def run_convert(ppm_path: Path, jpg_path: Path, quality: int = 92) -> None:
    jpg_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "convert",
            str(ppm_path),
            "-strip",
            "-interlace",
            "Plane",
            "-quality",
            str(quality),
            str(jpg_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def nice_sci(value: float) -> str:
    if value == 0:
        return "0"
    if value < 0:
        return "-" + nice_sci(-value)
    if value < 0.01:
        exp = int(math.floor(math.log10(value)))
        mant = value / (10**exp)
        return f"{mant:.1f}e{exp}"
    if value >= 100:
        return f"{value:.0f}"
    if value >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def time_analysis_jpeg(rows: list[dict[str, str]]) -> None:
    points = [(int(r["classes"]), float(r["scheduling_seconds_mean"])) for r in rows]
    points.sort(key=lambda p: p[0])
    if not points:
        return

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.plot(xs, ys, color="#285AB4", linewidth=2.5, zorder=2)
    ax.scatter(xs, ys, color="#D04E26", s=70, zorder=3)

    ax.set_title("Greedy Scheduler Runtime vs Number of Classes", fontsize=18, pad=14)
    ax.set_xlabel("Number of Classes", fontsize=13)
    ax.set_ylabel("Runtime (seconds)", fontsize=13)

    # Show the exact measured x-values instead of scientific notation.
    ax.set_xticks(xs)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{int(value):,}" if value >= 1 else f"{value:g}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
    ax.tick_params(axis="x", rotation=45)

    ax.grid(True, which="both", linestyle="--", linewidth=0.6, alpha=0.45)

    for x_val, y_val in points:
        ax.annotate(
            f"{y_val:.3f}s",
            xy=(x_val, y_val),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.tight_layout()
    jpg = OUT_DIR / "time_analysis.jpg"
    fig.savefig(jpg, dpi=300, bbox_inches="tight")
    plt.close(fig)

def time_analysis_linear_100000_jpeg(rows: list[dict[str, str]]) -> None:
    # Linear axes, x up to 100000. We only have measured points up to 10000 in the repo
    # results, so we extrapolate a final point using a power-law fit on the last two points.
    points = [(int(r["classes"]), float(r["scheduling_seconds_mean"])) for r in rows]
    points.sort(key=lambda p: p[0])
    if not points:
        return

    max_measured_x = max(x for x, _ in points)
    if max_measured_x < 1000:
        return

    # Choose last two distinct points for a simple power fit y = k * x^b.
    last = points[-1]
    prev = next((p for p in reversed(points[:-1]) if p[0] != last[0]), None)
    if prev is None:
        return

    x1, y1 = prev
    x2, y2 = last
    if y1 <= 0 or y2 <= 0 or x1 <= 0 or x2 <= 0:
        return

    b = math.log(y2 / y1) / math.log(x2 / x1)
    x3 = 100000
    y3 = y2 * ((x3 / x2) ** b)

    w, h = 1700, 900
    c = Canvas(w, h)
    margin_l, margin_r, margin_t, margin_b = 140, 60, 90, 160
    x0, y0 = margin_l, margin_t
    x1p, y1p = w - margin_r, h - margin_b

    c.text(40, 20, "TIME ANALYSIS (LINEAR) WITH 100000-CLASS EXTRAPOLATION", BLACK, scale=3)

    x_min, x_max = 0.0, 100000.0
    y_max = max(max(y for _, y in points), y3) * 1.15
    y_min = 0.0

    def px_x(v: float) -> int:
        return int(x0 + (v - x_min) / (x_max - x_min) * (x1p - x0))

    def px_y(v: float) -> int:
        return int(y1p - (v - y_min) / (y_max - y_min) * (y1p - y0))

    # Grid lines.
    for i in range(0, 11):
        y = int(y1p - i / 10 * (y1p - y0))
        c.line(x0, y, x1p, y, GRAY, thickness=1)
        if i % 2 == 0:
            c.text(30, y - 6, f"{(i/10)*y_max:.0f}s", DARK_GRAY, scale=2)

    for i in range(0, 6):
        xv = i * 20000
        x = px_x(xv)
        c.line(x, y0, x, y1p, GRAY, thickness=1)
        c.text(x - 25, y1p + 18, str(xv), DARK_GRAY, scale=2)

    # Axes.
    c.line(x0, y1p, x1p, y1p, BLACK, thickness=2)
    c.line(x0, y0, x0, y1p, BLACK, thickness=2)

    c.text((x0 + x1p) // 2 - 200, h - 80, "NUMBER OF CLASSES", BLACK, scale=2)
    c.text(10, (y0 + y1p) // 2 - 20, "SCHEDULING TIME (SECONDS)", BLACK, scale=2)

    # Measured polyline.
    prev_px = None
    for x_val, y_val in points:
        x = px_x(x_val)
        y = px_y(y_val)
        c.fill_rect(x - 6, y - 6, x + 6, y + 6, BLUE)
        if prev_px is not None:
            c.line(prev_px[0], prev_px[1], x, y, BLUE, thickness=4)
        prev_px = (x, y)
        c.text(x - 40, y - 28, f"{y_val:.2f}s", DARK_GRAY, scale=2)

    # Extrapolated segment (dashed) from last measured to 100000.
    x2p = px_x(x2)
    y2p = px_y(y2)
    x3p = px_x(x3)
    y3p = px_y(y3)
    dash = 14
    segs = max(1, int(math.hypot(x3p - x2p, y3p - y2p) // (dash * 2)))
    for i in range(segs):
        t0 = i / segs
        t1 = min(1.0, (i + 0.5) / segs)
        ax = int(x2p + (x3p - x2p) * t0)
        ay = int(y2p + (y3p - y2p) * t0)
        bx = int(x2p + (x3p - x2p) * t1)
        by = int(y2p + (y3p - y2p) * t1)
        c.line(ax, ay, bx, by, ORANGE, thickness=4)

    c.fill_rect(x3p - 7, y3p - 7, x3p + 7, y3p + 7, ORANGE)
    c.text(x3p - 140, y3p - 32, f"EXTRAPOLATED: {y3:.1f}s", ORANGE, scale=2)

    # Legend.
    c.fill_rect(x0 + 10, y0 + 10, x0 + 500, y0 + 70, RGB(250, 250, 250))
    c.fill_rect(x0 + 20, y0 + 22, x0 + 40, y0 + 42, BLUE)
    c.text(x0 + 55, y0 + 18, "MEASURED (MEAN OVER SEEDS)", BLACK, scale=2)
    c.fill_rect(x0 + 20, y0 + 50, x0 + 40, y0 + 70, ORANGE)
    c.text(x0 + 55, y0 + 46, "EXTRAPOLATED TO 100000", BLACK, scale=2)

    ppm = OUT_DIR / "_tmp_time_linear.ppm"
    jpg = OUT_DIR / "time_analysis_100000_linear.jpg"
    c.save_ppm(ppm)
    run_convert(ppm, jpg, quality=92)
    ppm.unlink(missing_ok=True)


def quality_analysis_jpeg(rows: list[dict[str, str]]) -> None:
    cases = [(r["case"], float(r["optimality_mean"])) for r in rows]

    label_map = {
        "baseline": "baseline",
        "rooms_20": "rooms 20",
        "rooms_40": "rooms 40",
        "class_times_12": "times 12",
        "class_times_18": "times 18",
        "students_75": "stud 75",
        "students_150": "stud 150",
        "capacity_tight": "cap tight",
        "capacity_large": "cap large",
        "hours_more_short": "short hrs",
        "hours_more_long": "long hrs",
    }
    cases = [(label_map.get(k, k.replace("_", " ")), v) for (k, v) in cases]

    w, h = 1700, 900
    c = Canvas(w, h)
    margin_l, margin_r, margin_t, margin_b = 130, 60, 90, 190
    x0, y0 = margin_l, margin_t
    x1, y1 = w - margin_r, h - margin_b

    c.text(40, 20, "SOLUTION QUALITY (ACHIEVED / BEST-CASE UPPER BOUND)", BLACK, scale=3)

    # Grid/axes (0..1).
    for i in range(0, 11):
        y = int(y1 - i / 10 * (y1 - y0))
        c.line(x0, y, x1, y, GRAY, thickness=1)
        if i % 2 == 0:
            c.text(40, y - 6, f"{i/10:.1f}", DARK_GRAY, scale=2)
    c.line(x0, y1, x1, y1, BLACK, thickness=2)
    c.line(x0, y0, x0, y1, BLACK, thickness=2)
    c.text(10, (y0 + y1) // 2 - 20, "QUALITY", BLACK, scale=2)

    n = len(cases)
    plot_w = x1 - x0
    bar_gap = 12
    bar_w = max(10, (plot_w - bar_gap * (n + 1)) // n)
    x = x0 + bar_gap
    for label, val in cases:
        bar_h = int(val * (y1 - y0))
        c.fill_rect(x, y1 - bar_h, x + bar_w, y1 - 1, BLUE)
        c.line(x, y1, x, y1 + 8, BLACK, thickness=2)
        c.text(x, y1 + 18, label, BLACK, scale=2)
        c.text(x, y1 - bar_h - 26, f"{val:.3f}", DARK_GRAY, scale=2)
        x += bar_w + bar_gap

    ppm = OUT_DIR / "_tmp_quality.ppm"
    jpg = OUT_DIR / "quality_analysis.jpg"
    c.save_ppm(ppm)
    run_convert(ppm, jpg, quality=92)
    ppm.unlink(missing_ok=True)

def fit_percentage_scenarios_jpeg(rows: list[dict[str, str]]) -> None:
    # Fit percentage = optimality_mean * 100.
    cases = [(r["case"], float(r["optimality_mean"])) for r in rows]
    cases.sort(key=lambda kv: kv[1], reverse=True)

    label_map = {
        "baseline": "baseline",
        "rooms_20": "rooms 20",
        "rooms_40": "rooms 40",
        "class_times_12": "times 12",
        "class_times_18": "times 18",
        "students_75": "stud 75",
        "students_150": "stud 150",
        "capacity_tight": "cap tight",
        "capacity_large": "cap large",
        "hours_more_short": "short hrs",
        "hours_more_long": "long hrs",
    }
    items = [(label_map.get(k, k.replace("_", " ")), v * 100.0) for (k, v) in cases]

    w, h = 1800, 950
    c = Canvas(w, h)
    margin_l, margin_r, margin_t, margin_b = 150, 60, 90, 220
    x0, y0 = margin_l, margin_t
    x1, y1 = w - margin_r, h - margin_b

    c.text(40, 20, "FIT PERCENTAGE BY SCENARIO (HIGHER IS BETTER)", BLACK, scale=3)

    # Grid/axes (0..100%).
    for i in range(0, 11):
        y = int(y1 - i / 10 * (y1 - y0))
        c.line(x0, y, x1, y, GRAY, thickness=1)
        if i % 2 == 0:
            c.text(35, y - 6, f"{i*10}%", DARK_GRAY, scale=2)
    c.line(x0, y1, x1, y1, BLACK, thickness=2)
    c.line(x0, y0, x0, y1, BLACK, thickness=2)
    c.text(10, (y0 + y1) // 2 - 20, "FIT %", BLACK, scale=2)

    n = len(items)
    plot_w = x1 - x0
    bar_gap = 12
    bar_w = max(10, (plot_w - bar_gap * (n + 1)) // n)
    x = x0 + bar_gap

    baseline_val = next((v for (lbl, v) in items if lbl == "baseline"), None)
    if baseline_val is not None:
        yb = int(y1 - (baseline_val / 100.0) * (y1 - y0))
        c.line(x0, yb, x1, yb, DARK_GRAY, thickness=3)
        c.text(x0 + 10, yb - 26, f"baseline = {baseline_val:.1f}%", DARK_GRAY, scale=2)

    for label, val in items:
        bar_h = int((val / 100.0) * (y1 - y0))
        c.fill_rect(x, y1 - bar_h, x + bar_w, y1 - 1, BLUE)
        c.text(x, y1 + 18, label, BLACK, scale=2)
        c.text(x, y1 - bar_h - 26, f"{val:.1f}%", DARK_GRAY, scale=2)
        x += bar_w + bar_gap

    ppm = OUT_DIR / "_tmp_fit.ppm"
    jpg = OUT_DIR / "fit_percentage.jpg"
    c.save_ppm(ppm)
    run_convert(ppm, jpg, quality=92)
    ppm.unlink(missing_ok=True)


def table_jpeg(
    title: str,
    headers: list[str],
    rows: list[list[str]],
    out_name: str,
) -> None:
    # Simple grid table.
    scale = 2
    cell_h = 18 * scale
    pad_x = 10 * scale

    # Estimate column widths by text length.
    def text_w(s: str) -> int:
        return (len(s) * 6 + 2) * scale

    col_widths = [text_w(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            col_widths[i] = max(col_widths[i], text_w(cell))
    col_widths = [w + pad_x * 2 for w in col_widths]

    table_w = sum(col_widths) + 2
    table_h = (len(rows) + 1) * cell_h + 2

    w = max(1200, table_w + 160)
    h = max(500, table_h + 160)
    c = Canvas(w, h)
    c.text(40, 20, title, BLACK, scale=3)

    x0, y0 = 80, 90
    # Header background.
    c.fill_rect(x0, y0, x0 + table_w, y0 + cell_h, RGB(240, 240, 240))

    # Grid lines + content.
    x = x0
    for col_w in col_widths:
        c.line(x, y0, x, y0 + table_h, BLACK, thickness=2)
        x += col_w
    c.line(x0 + table_w, y0, x0 + table_w, y0 + table_h, BLACK, thickness=2)

    for r in range(len(rows) + 2):
        y = y0 + r * cell_h
        c.line(x0, y, x0 + table_w, y, BLACK, thickness=2)

    # Header text.
    x = x0
    for i, htxt in enumerate(headers):
        c.text(x + pad_x, y0 + 6, htxt, BLACK, scale=2)
        x += col_widths[i]

    # Rows.
    for ri, row in enumerate(rows):
        y = y0 + (ri + 1) * cell_h
        x = x0
        for ci, cell in enumerate(row):
            c.text(x + pad_x, y + 6, cell, BLACK, scale=2)
            x += col_widths[ci]

    ppm = OUT_DIR / f"_tmp_{out_name}.ppm"
    jpg = OUT_DIR / f"{out_name}.jpg"
    c.save_ppm(ppm)
    run_convert(ppm, jpg, quality=92)
    ppm.unlink(missing_ok=True)


def main() -> None:
    if not (DATA_DIR / "class_scale_agg.csv").exists() or not (DATA_DIR / "optimality_agg.csv").exists():
        raise SystemExit(
            "Missing overleaf/data/*.csv. Run: python3 overleaf/build_overleaf_assets.py"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    class_scale = read_csv(DATA_DIR / "class_scale_agg.csv")
    optimality = read_csv(DATA_DIR / "optimality_agg.csv")

    # Figures.
    time_analysis_jpeg(class_scale)
    time_analysis_linear_100000_jpeg(class_scale)
    quality_analysis_jpeg(optimality)
    fit_percentage_scenarios_jpeg(optimality)

    # Tables (as images).
    # Class scale table.
    cs_rows = []
    for r in class_scale:
        cs_rows.append(
            [
                r["classes"],
                r["runs"],
                f"{float(r['scheduling_seconds_mean']):.3f}",
                f"{float(r['scheduling_seconds_stdev']):.3f}",
                f"{float(r['optimality_mean']):.3f}",
            ]
        )
    table_jpeg(
        "TABLE: RUNTIME SCALING (MEAN OVER SEEDS 100-500)",
        ["Classes", "Runs", "Mean time (s)", "Stdev (s)", "Mean quality"],
        cs_rows,
        "class_scale_table",
    )

    # Optimality scenario table.
    opt_rows = []
    for r in optimality:
        opt_rows.append(
            [
                r["case"].replace("_", " "),
                r["runs"],
                f"{float(r['optimality_mean']):.3f}",
                f"{float(r['optimality_min']):.3f}",
                f"{float(r['optimality_max']):.3f}",
            ]
        )
    table_jpeg(
        "TABLE: SOLUTION QUALITY BY SCENARIO (MEAN OVER SEEDS 100-500)",
        ["Scenario", "Runs", "Mean", "Min", "Max"],
        opt_rows,
        "optimality_table",
    )

    # Write a tiny index.
    (OUT_DIR / "README.txt").write_text(
        "\n".join(
            [
                "Upload these JPEGs to Overleaf and include them with \\\\includegraphics{...}:",
                "- overleaf/jpeg/time_analysis.jpg",
                "- overleaf/jpeg/quality_analysis.jpg",
                "- overleaf/jpeg/class_scale_table.jpg",
                "- overleaf/jpeg/optimality_table.jpg",
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    # Ensure ImageMagick is available.
    if not any(Path(p).joinpath("convert").exists() for p in os.getenv("PATH", "").split(os.pathsep)):
        raise SystemExit("ImageMagick 'convert' not found on PATH.")
    main()
