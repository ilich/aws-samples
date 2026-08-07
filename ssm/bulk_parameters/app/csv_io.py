import csv
from collections.abc import Iterable
from pathlib import Path

from app.models import ParameterRecord, ParameterType

FIELD_NAMES = ["name", "value", "type", "keep"]


def write_csv(path: Path, records: Iterable[ParameterRecord]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES)
        writer.writeheader()
        for record in sorted(records, key=lambda r: r.name):
            writer.writerow(
                {"name": record.name, "value": record.value, "type": record.type.value, "keep": str(record.keep)}
            )


def read_csv(path: Path) -> list[ParameterRecord]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            ParameterRecord(
                name=row["name"],
                value=row["value"],
                type=ParameterType(row["type"]),
                keep=row.get("keep", "True") == "True",
            )
            for row in reader
        ]
