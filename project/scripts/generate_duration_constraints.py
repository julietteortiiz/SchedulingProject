from __future__ import annotations

import argparse
import random
from pathlib import Path


DEFAULT_DURATION_BLOCKS = (2, 3, 6)
DEFAULT_DURATION_WEIGHTS = (0.45, 0.4, 0.15)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Make a constraints file with class durations, or take an older "
            "constraints file and add durations to it."
        )
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Where to write the new constraints file.",
    )
    parser.add_argument(
        "--input",
        help=(
            "Older constraints file to upgrade. If you leave this out, the "
            "script makes a fresh one from scratch."
        ),
    )
    parser.add_argument(
        "--class-times",
        type=int,
        default=15,
        help="How many 30-minute blocks are available. Default: 15.",
    )
    parser.add_argument(
        "--rooms",
        type=int,
        default=10,
        help="How many rooms to make if you're generating a fresh file. Default: 10.",
    )
    parser.add_argument(
        "--classes",
        type=int,
        default=50,
        help="How many classes to make if you're generating a fresh file. Default: 50.",
    )
    parser.add_argument(
        "--min-room-capacity",
        type=int,
        default=200,
        help="Smallest room size to generate. Default: 200.",
    )
    parser.add_argument(
        "--max-room-capacity",
        type=int,
        default=900,
        help="Largest room size to generate. Default: 900.",
    )
    parser.add_argument(
        "--duration-blocks",
        default="2,3,6",
        help=(
            "Allowed class lengths in 30-minute blocks, separated by commas. "
            "Default: 2,3,6."
        ),
    )
    parser.add_argument(
        "--duration-weights",
        default="0.45,0.4,0.15",
        help=(
            "Relative odds for picking each class length. This should line up "
            "with --duration-blocks. Default: 0.45,0.4,0.15."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed, if you want the same output every time.",
    )
    return parser.parse_args()


def parse_csv_ints(raw: str) -> tuple[int, ...]:
    values = tuple(int(piece.strip()) for piece in raw.split(",") if piece.strip())
    if not values:
        raise ValueError("Give at least one class length in blocks.")
    if any(value <= 0 for value in values):
        raise ValueError("Class lengths have to be positive whole numbers.")
    return values


def parse_csv_floats(raw: str) -> tuple[float, ...]:
    values = tuple(float(piece.strip()) for piece in raw.split(",") if piece.strip())
    if not values:
        raise ValueError("Give at least one weight for the class lengths.")
    if any(value < 0 for value in values):
        raise ValueError("Weights can't be negative.")
    if sum(values) == 0:
        raise ValueError("At least one weight has to be bigger than zero.")
    return values


def choose_duration(
    rng: random.Random, duration_blocks: tuple[int, ...], duration_weights: tuple[float, ...]
) -> int:
    return rng.choices(duration_blocks, weights=duration_weights, k=1)[0]


def assign_teachers(num_classes: int, rng: random.Random) -> list[tuple[int, int]]:
    if num_classes % 2 != 0:
        raise ValueError(
            "The number of classes has to be even, since each teacher gets exactly two classes."
        )

    num_teachers = num_classes // 2
    teachers = []
    for teacher_id in range(1, num_teachers + 1):
        teachers.extend([teacher_id, teacher_id])
    rng.shuffle(teachers)

    return [(class_id, teachers[class_id - 1]) for class_id in range(1, num_classes + 1)]


def build_random_constraints(
    class_times: int,
    num_rooms: int,
    num_classes: int,
    min_room_capacity: int,
    max_room_capacity: int,
    duration_blocks: tuple[int, ...],
    duration_weights: tuple[float, ...],
    rng: random.Random,
) -> list[str]:
    if class_times <= 0:
        raise ValueError("Class times must be positive.")
    if num_rooms <= 0:
        raise ValueError("The number of rooms must be positive.")
    if num_classes <= 0:
        raise ValueError("The number of classes must be positive.")
    if min_room_capacity <= 0 or max_room_capacity <= 0:
        raise ValueError("Room sizes must be positive.")
    if min_room_capacity > max_room_capacity:
        raise ValueError("The minimum room size can't be bigger than the maximum room size.")

    lines = [f"Class Times\t{class_times}", f"Rooms\t{num_rooms}"]

    for room_id in range(1, num_rooms + 1):
        capacity = rng.randint(min_room_capacity, max_room_capacity)
        lines.append(f"{room_id}\t{capacity}")

    lines.append(f"Classes\t{num_classes}")
    lines.append(f"Teachers\t{num_classes // 2}")

    for class_id, teacher_id in assign_teachers(num_classes, rng):
        duration = choose_duration(rng, duration_blocks, duration_weights)
        lines.append(f"{class_id}\t{teacher_id}\t{duration}")

    return lines


def upgrade_existing_constraints(
    input_path: Path,
    duration_blocks: tuple[int, ...],
    duration_weights: tuple[float, ...],
    rng: random.Random,
) -> list[str]:
    source_lines = [line.rstrip("\n") for line in input_path.read_text().splitlines()]
    output_lines: list[str] = []

    teacher_section = False
    teachers_expected = None
    teachers_seen = 0

    for raw_line in source_lines:
        if not raw_line:
            continue

        parts = raw_line.split()
        header = parts[0]

        if header == "Teachers":
            teacher_section = True
            teachers_expected = int(parts[1])
            teachers_seen = 0
            output_lines.append(raw_line)
            continue

        if teacher_section:
            class_id = int(parts[0])
            teacher_id = int(parts[1])
            duration = choose_duration(rng, duration_blocks, duration_weights)
            output_lines.append(f"{class_id}\t{teacher_id}\t{duration}")
            teachers_seen += 1
            if teachers_expected is not None and teachers_seen >= teachers_expected * 2:
                teacher_section = False
            continue

        output_lines.append(raw_line)

    return output_lines


def main() -> None:
    args = parse_args()

    duration_blocks = parse_csv_ints(args.duration_blocks)
    duration_weights = parse_csv_floats(args.duration_weights)
    if len(duration_blocks) != len(duration_weights):
        raise ValueError("The number of class lengths has to match the number of weights.")

    rng = random.Random(args.seed)
    output_path = Path(args.output)

    if args.input:
        lines = upgrade_existing_constraints(
            input_path=Path(args.input),
            duration_blocks=duration_blocks,
            duration_weights=duration_weights,
            rng=rng,
        )
    else:
        lines = build_random_constraints(
            class_times=args.class_times,
            num_rooms=args.rooms,
            num_classes=args.classes,
            min_room_capacity=args.min_room_capacity,
            max_room_capacity=args.max_room_capacity,
            duration_blocks=duration_blocks,
            duration_weights=duration_weights,
            rng=rng,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
