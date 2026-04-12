from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path


DEFAULT_DURATION_BLOCKS = (2, 3, 6)
DEFAULT_DURATION_WEIGHTS = (0.45, 0.4, 0.15)
DEFAULT_CREDIT_HOURS = (2, 3, 4)
DEFAULT_CREDIT_HOUR_WEIGHTS = (0.15, 0.55, 0.30)
DEFAULT_MIN_ROOMS_PER_BUILDING = 2


@dataclass(frozen=True)
class BuildingTemplate:
    building_id: int
    college: str
    building_name: str


@dataclass(frozen=True)
class ClassRecord:
    class_id: int
    college: str
    department: str
    paired_class_id: int
    credit_hours: int
    day_frequency: int


# Representative academic/student-use buildings based on official Bryn Mawr
# and Haverford campus/facilities pages.
BUILDING_TEMPLATES = (
    BuildingTemplate(1, "B", "Dalton"),
    BuildingTemplate(2, "B", "Park"),
    BuildingTemplate(3, "B", "Goodhart"),
    BuildingTemplate(4, "B", "Guild"),
    BuildingTemplate(5, "B", "Bettws"),

    BuildingTemplate(6, "H", "Stokes"),
    BuildingTemplate(7, "H", "Sharpless"),
    BuildingTemplate(8, "H", "Hilles"),
    BuildingTemplate(9, "H", "Chase"),
    BuildingTemplate(10, "H", "Roberts"),
)

DEPARTMENTS_BY_COLLEGE = {
    "B": ("CS", "Biology", "Physics", "English", "Art", "Sociology", "Philosophy"),
    "H": ("History", "Econ", "Math", "Chem", "Political", "Music", "Psychology"),
}

COLLEGE_ORDER = tuple(DEPARTMENTS_BY_COLLEGE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate structured registrar constraints with fixed buildings, or "
            "upgrade a legacy constraints file by adding durations."
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
            "Legacy constraints file to upgrade. When this is set, the script "
            "keeps the old format and adds a random duration to each class row."
        ),
    )
    parser.add_argument(
        "--legacy-format",
        action="store_true",
        help=(
            "Generate the older Rooms/Classes/Teachers format from scratch. "
            "If omitted, fresh generation uses the new Buildings/Rooms/Classes layout."
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
        default=30,
        help=(
            "How many rooms to make. In structured mode, these rooms are "
            "distributed across the fixed buildings. Default: 30."
        ),
    )
    parser.add_argument(
        "--min-rooms-per-building",
        type=int,
        default=DEFAULT_MIN_ROOMS_PER_BUILDING,
        help=(
            "Minimum number of rooms to assign to every building in structured "
            f"mode. Default: {DEFAULT_MIN_ROOMS_PER_BUILDING}."
        ),
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
        default=6,
        help="Smallest room size to generate. Default: 6.",
    )
    parser.add_argument(
        "--max-room-capacity",
        type=int,
        default=120,
        help="Largest room size to generate. Default: 120.",
    )
    parser.add_argument(
        "--credit-hours",
        default="2,3,4",
        help=(
            "Allowed credit-hour values for structured generation, separated by commas. "
            "Default: 2,3,4."
        ),
    )
    parser.add_argument(
        "--credit-hour-weights",
        default="0.15,0.55,0.30",
        help=(
            "Relative odds for picking each credit-hour value during structured "
            "generation. This should line up with --credit-hours. "
            "Default: 0.15,0.55,0.30."
        ),
    )
    parser.add_argument(
        "--duration-blocks",
        default="2,3,6",
        help=(
            "Allowed class lengths in 30-minute blocks, separated by commas. "
            "Only used with --input or --legacy-format. Default: 2,3,6."
        ),
    )
    parser.add_argument(
        "--duration-weights",
        default="0.45,0.4,0.15",
        help=(
            "Relative odds for picking each class length. This should line up "
            "with --duration-blocks. Only used with --input or --legacy-format. "
            "Default: 0.45,0.4,0.15."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed, if you want the same output every time.",
    )
    parser.add_argument(
    "--student-pref",
    help="Where to write student preference file.",
    )
    parser.add_argument(
    "--students",
    type=int,
    default=None,
    help="Number of students (default: 2 * num_classes).",
    )

    return parser.parse_args()


def parse_csv_ints(raw: str) -> tuple[int, ...]:
    values = tuple(int(piece.strip()) for piece in raw.split(",") if piece.strip())
    if not values:
        raise ValueError("Give at least one positive whole number.")
    if any(value <= 0 for value in values):
        raise ValueError("Values have to be positive whole numbers.")
    return values


def parse_csv_floats(raw: str) -> tuple[float, ...]:
    values = tuple(float(piece.strip()) for piece in raw.split(",") if piece.strip())
    if not values:
        raise ValueError("Give at least one weight.")
    if any(value < 0 for value in values):
        raise ValueError("Weights can't be negative.")
    if sum(values) == 0:
        raise ValueError("At least one weight has to be bigger than zero.")
    return values


def choose_weighted_value(
    rng: random.Random, values: tuple[int, ...], weights: tuple[float, ...]
) -> int:
    return rng.choices(values, weights=weights, k=1)[0]


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
        duration = choose_weighted_value(rng, duration_blocks, duration_weights)
        lines.append(f"{class_id}\t{teacher_id}\t{duration}")

    return lines


def distribute_rooms_across_buildings(
    num_rooms: int, min_rooms_per_building: int, rng: random.Random
) -> list[int]:
    if min_rooms_per_building <= 0:
        raise ValueError("Minimum rooms per building must be positive.")

    minimum_total_rooms = len(BUILDING_TEMPLATES) * min_rooms_per_building
    if num_rooms < minimum_total_rooms:
        raise ValueError(
            "You need at least "
            f"{minimum_total_rooms} rooms so each fixed building gets "
            f"{min_rooms_per_building} rooms."
        )

    room_counts = [min_rooms_per_building] * len(BUILDING_TEMPLATES)
    for _ in range(num_rooms - minimum_total_rooms):
        room_counts[rng.randrange(len(BUILDING_TEMPLATES))] += 1
    return room_counts


def choose_day_frequency(credit_hours: int, rng: random.Random) -> int:
    if credit_hours <= 2:
        return rng.choices((1, 2), weights=(0.35, 0.65), k=1)[0]
    return rng.choices((2, 3), weights=(0.45, 0.55), k=1)[0]


def choose_pair_colleges(num_pairs: int, rng: random.Random) -> list[str]:
    base_count = num_pairs // len(COLLEGE_ORDER)
    pair_colleges = []
    for college in COLLEGE_ORDER:
        pair_colleges.extend([college] * base_count)

    remainder = num_pairs % len(COLLEGE_ORDER)
    if remainder:
        pair_colleges.extend(rng.sample(list(COLLEGE_ORDER), k=remainder))

    rng.shuffle(pair_colleges)
    return pair_colleges


def generate_class_records(
    num_classes: int,
    credit_hour_values: tuple[int, ...],
    credit_hour_weights: tuple[float, ...],
    rng: random.Random,
) -> list[ClassRecord]:
    if num_classes <= 0:
        raise ValueError("The number of classes must be positive.")
    if num_classes % 2 != 0:
        raise ValueError(
            "The number of classes has to be even, since each teacher gets exactly two classes."
        )

    num_pairs = num_classes // 2
    shuffled_class_ids = list(range(1, num_classes + 1))
    rng.shuffle(shuffled_class_ids)

    records: dict[int, ClassRecord] = {}
    for pair_index, college in enumerate(choose_pair_colleges(num_pairs, rng)):
        class_id_a = shuffled_class_ids[2 * pair_index]
        class_id_b = shuffled_class_ids[2 * pair_index + 1]
        department = rng.choice(DEPARTMENTS_BY_COLLEGE[college])
        credit_hours = choose_weighted_value(rng, credit_hour_values, credit_hour_weights)

        records[class_id_a] = ClassRecord(
            class_id=class_id_a,
            college=college,
            department=department,
            paired_class_id=class_id_b,
            credit_hours=credit_hours,
            day_frequency=choose_day_frequency(credit_hours, rng),
        )
        records[class_id_b] = ClassRecord(
            class_id=class_id_b,
            college=college,
            department=department,
            paired_class_id=class_id_a,
            credit_hours=credit_hours,
            day_frequency=choose_day_frequency(credit_hours, rng),
        )

    return [records[class_id] for class_id in sorted(records)]


def build_structured_constraints(
    class_times: int,
    num_rooms: int,
    num_classes: int,
    min_room_capacity: int,
    max_room_capacity: int,
    min_rooms_per_building: int,
    credit_hour_values: tuple[int, ...],
    credit_hour_weights: tuple[float, ...],
    rng: random.Random,
) -> list[str]:
    if class_times <= 0:
        raise ValueError("Class times must be positive.")
    if min_room_capacity <= 0 or max_room_capacity <= 0:
        raise ValueError("Room sizes must be positive.")
    if min_room_capacity > max_room_capacity:
        raise ValueError("The minimum room size can't be bigger than the maximum room size.")

    room_counts = distribute_rooms_across_buildings(
        num_rooms=num_rooms,
        min_rooms_per_building=min_rooms_per_building,
        rng=rng,
    )
    class_records = generate_class_records(
        num_classes=num_classes,
        credit_hour_values=credit_hour_values,
        credit_hour_weights=credit_hour_weights,
        rng=rng,
    )

    lines = [
        f"Class Times\t{class_times}",
        f"Buildings\t{len(BUILDING_TEMPLATES)}",
    ]

    for building, room_count in zip(BUILDING_TEMPLATES, room_counts):
        lines.append(
            f"{building.building_id}\t{building.college}\t{building.building_name}\t{room_count}"
        )

    lines.extend(
        [
            f"Rooms\t{num_rooms}",
        ]
    )

    room_id = 1
    for building, room_count in zip(BUILDING_TEMPLATES, room_counts):
        for _ in range(room_count):
            capacity = rng.randint(min_room_capacity, max_room_capacity)
            lines.append(f"{room_id}\t{building.building_id}\t{capacity}")
            room_id += 1

    lines.extend(
        [
            f"Classes\t{num_classes}",
            f"Teachers\t{num_classes // 2}",
        ]
    )

    for record in class_records:
        lines.append(
            f"{record.class_id}\t{record.college}\t{record.department}\t"
            f"{record.paired_class_id}\t{record.credit_hours}\t{record.day_frequency}"
        )

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
            duration = choose_weighted_value(rng, duration_blocks, duration_weights)
            output_lines.append(f"{class_id}\t{teacher_id}\t{duration}")
            teachers_seen += 1
            if teachers_expected is not None and teachers_seen >= teachers_expected * 2:
                teacher_section = False
            continue

        output_lines.append(raw_line)

    return output_lines

def generate_student_preferences(num_students: int, num_classes: int, rng: random.Random) -> list[str]:
    if num_students <= 0:
        raise ValueError("Number of students must be positive.")
    if num_classes < 4:
        raise ValueError("Need at least 4 classes for preferences.")

    lines = [f"Students\t{num_students}"]

    class_pool = list(range(1, num_classes + 1))

    for student_id in range(1, num_students + 1):
        prefs = rng.sample(class_pool, 4)  # 4 unique classes
        lines.append(f"{student_id}\t{prefs[0]}\t{prefs[1]}\t{prefs[2]}\t{prefs[3]}")

    return lines


def main() -> None:
    args = parse_args()

    duration_blocks = parse_csv_ints(args.duration_blocks)
    duration_weights = parse_csv_floats(args.duration_weights)
    if len(duration_blocks) != len(duration_weights):
        raise ValueError("The number of class lengths has to match the number of weights.")

    credit_hour_values = parse_csv_ints(args.credit_hours)
    credit_hour_weights = parse_csv_floats(args.credit_hour_weights)
    if len(credit_hour_values) != len(credit_hour_weights):
        raise ValueError("The number of credit-hour values has to match the number of weights.")

    rng = random.Random(args.seed)
    output_path = Path(args.output)

    if args.input:
        lines = upgrade_existing_constraints(
            input_path=Path(args.input),
            duration_blocks=duration_blocks,
            duration_weights=duration_weights,
            rng=rng,
        )
    elif args.legacy_format:
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
    else:
        lines = build_structured_constraints(
            class_times=args.class_times,
            num_rooms=args.rooms,
            num_classes=args.classes,
            min_room_capacity=args.min_room_capacity,
            max_room_capacity=args.max_room_capacity,
            min_rooms_per_building=args.min_rooms_per_building,
            credit_hour_values=credit_hour_values,
            credit_hour_weights=credit_hour_weights,
            rng=rng,
        )


    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n")

    num_students = args.students if args.students is not None else args.classes * 2
    student_lines = generate_student_preferences(
        num_students=num_students,
        num_classes=args.classes,
        rng=rng,
    )

    if args.student_pref:
        student_path = Path(args.student_pref)
        student_path.parent.mkdir(parents=True, exist_ok=True)
        student_path.write_text("\n".join(student_lines) + "\n")

if __name__ == "__main__":
    main()
