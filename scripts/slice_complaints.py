"""Slice the CFPB bulk Consumer Complaint CSV down to a date-bounded subset.

CFPB publishes the full complaint database (~5M+ rows, ~8 GB unzipped) at
https://files.consumerfinance.gov/ccdb/complaints.csv.zip. The CFPB Search API
is capped at 10,000-result pagination, so the bulk CSV is the only practical
path to a complete dataset. This script slices that CSV down to a recent
window so Power BI can refresh comfortably.

Usage:
    python slice_complaints.py --src "D:\\CFPB_complaints\\complaints.csv" \\
                               --dst "D:\\CFPB_complaints\\complaints_recent.csv" \\
                               --cutoff 2024-05-01

Defaults assume the layout used in this project's README. Run
`python slice_complaints.py --help` for the full list of options.

No third-party packages required — uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument(
        "--src",
        type=Path,
        default=Path(r"D:\CFPB_complaints\complaints.csv"),
        help="Path to the unzipped CFPB bulk CSV (default: %(default)s)",
    )
    p.add_argument(
        "--dst",
        type=Path,
        default=Path(r"D:\CFPB_complaints\complaints_recent.csv"),
        help="Where to write the sliced CSV (default: %(default)s)",
    )
    p.add_argument(
        "--cutoff",
        type=date.fromisoformat,
        default=date(2024, 5, 1),
        help="Keep rows where Date received >= this YYYY-MM-DD (default: %(default)s)",
    )
    p.add_argument(
        "--date-column",
        default="Date received",
        help="Header name of the date column (default: %(default)s)",
    )
    return p.parse_args()


def slice_csv(src: Path, dst: Path, cutoff: date, date_column: str) -> tuple[int, int]:
    """Stream-filter `src` into `dst`, keeping rows on/after `cutoff`.

    Returns (rows_scanned, rows_kept).
    """
    # The narrative column can exceed the default csv field-size limit.
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

    with src.open("r", encoding="utf-8", newline="") as fin, \
         dst.open("w", encoding="utf-8", newline="") as fout:
        reader = csv.reader(fin)
        writer = csv.writer(fout)
        header = next(reader)
        writer.writerow(header)

        try:
            date_idx = header.index(date_column)
        except ValueError:
            raise SystemExit(
                f"Date column {date_column!r} not in header. Found: {header}"
            )

        kept = scanned = 0
        for row in reader:
            scanned += 1
            try:
                if date.fromisoformat(row[date_idx]) >= cutoff:
                    writer.writerow(row)
                    kept += 1
            except (ValueError, IndexError):
                continue
            if scanned % 500_000 == 0:
                print(f"  scanned {scanned:>10,}  kept {kept:>10,}")

        return scanned, kept


def main() -> None:
    args = parse_args()
    if not args.src.exists():
        raise SystemExit(f"Source file not found: {args.src}")
    args.dst.parent.mkdir(parents=True, exist_ok=True)

    print(f"Slicing {args.src} -> {args.dst}")
    print(f"Keeping rows with {args.date_column} >= {args.cutoff.isoformat()}")
    scanned, kept = slice_csv(args.src, args.dst, args.cutoff, args.date_column)
    print(f"Done. Scanned {scanned:,}; kept {kept:,}. Wrote {args.dst}")


if __name__ == "__main__":
    main()
