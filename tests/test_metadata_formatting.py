import csv
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_metadata_tsv_cells_have_no_surrounding_whitespace():
    violations = []
    for path in sorted((ROOT / "metadata").glob("*.tsv")):
        with path.open(encoding="utf-8", newline="") as tsv_file:
            for row_number, row in enumerate(
                csv.reader(tsv_file, delimiter="\t"), start=1
            ):
                for column_number, cell in enumerate(row, start=1):
                    if cell != cell.strip():
                        violations.append(
                            f"{path.name}:{row_number}:{column_number}: {cell!r}"
                        )

    assert not violations, (
        "Metadata TSV cells have leading or trailing whitespace:\n"
        + "\n".join(violations)
    )
