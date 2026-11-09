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


def test_metadata_tsv_headers_and_rows_are_well_formed():
    violations = []
    for path in sorted((ROOT / "metadata").glob("*.tsv")):
        with path.open(encoding="utf-8", newline="") as tsv_file:
            reader = csv.reader(tsv_file, delimiter="\t", strict=True)
            try:
                rows = list(reader)
            except csv.Error as error:
                violations.append(
                    f"{path.name}:{reader.line_num}: malformed TSV: {error}"
                )
                continue

        if not rows:
            violations.append(f"{path.name}: missing header")
            continue

        header = rows[0]
        if any(not column for column in header):
            violations.append(f"{path.name}: header contains an empty column name")
        duplicate_columns = sorted(
            column for column in set(header) if header.count(column) > 1
        )
        if duplicate_columns:
            violations.append(
                f"{path.name}: duplicate header columns: {', '.join(duplicate_columns)}"
            )

        for row_number, row in enumerate(rows[1:], start=2):
            if len(row) != len(header):
                violations.append(
                    f"{path.name}:{row_number}: expected {len(header)} columns, "
                    f"found {len(row)}"
                )

    assert not violations, (
        "Metadata TSV structure is invalid:\n" + "\n".join(violations)
    )
