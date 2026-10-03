import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "Data" / "CSV" / "footwear_dataset.csv"
OUTPUT_FILE = ROOT / "Data" / "CSV" / "footwear_dataset_repaired.csv"

EXPECTED_COLUMNS = 10

HEADER = [
    "RecordNo", "Type", "Person", "Scenario",
    "FSR1", "FSR2", "FSR3", "FSR4",
    "Temperature", "LoggedAt",
]

RECORD_START = re.compile(r"(\d+),(RAW|AVG10),")


def split_joined_line(line):
    matches = list(RECORD_START.finditer(line))
    if len(matches) <= 1:
        return [line]

    records = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(line)
        records.append(line[start:end])
    return records


def is_valid_record(row):
    if len(row) != EXPECTED_COLUMNS:
        return False
    try:
        int(row[0])
    except ValueError:
        return False
    if row[1] not in ("RAW", "AVG10"):
        return False
    return bool(row[2].strip()) and bool(row[3].strip())


def main():
    repaired_records = []
    malformed_records = []

    with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
        lines = f.readlines()

    print("=== DATASET REPAIR ===")
    print(f"Input: {INPUT_FILE}")
    print(f"Original physical data lines: {len(lines) - 1}")

    for line_number, raw_line in enumerate(lines[1:], start=2):
        line = raw_line.strip()
        if not line:
            continue

        for record in split_joined_line(line):
            try:
                row = next(csv.reader([record]))
            except Exception:
                malformed_records.append((line_number, record))
                continue

            if is_valid_record(row):
                repaired_records.append(row)
            else:
                malformed_records.append((line_number, record))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(repaired_records)

    print(f"Repaired logical records: {len(repaired_records)}")
    print(f"Skipped malformed records: {len(malformed_records)}")
    print(f"Output: {OUTPUT_FILE}")

    if malformed_records:
        print("\\nMalformed records:")
        for line_number, record in malformed_records[:20]:
            print(f"Line {line_number}: {record}")


if __name__ == "__main__":
    main()
