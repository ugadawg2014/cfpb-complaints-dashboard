# Setup

## Prerequisites

- **Power BI Desktop** (free) — <https://powerbi.microsoft.com/desktop/>
- **Python 3.10+** for the slicing helper
- ~15 GB free disk for the source + sliced CSVs

## One-time data prep

1. Download the bulk CFPB Consumer Complaint database:
   - <https://files.consumerfinance.gov/ccdb/complaints.csv.zip> (~1.7 GB)
2. Unzip into a working directory (this project assumes `D:\CFPB_complaints\`):
   - `complaints.csv` (~8.4 GB unzipped)
3. Slice to a 5-year window so Power BI can refresh comfortably:
python scripts/slice_complaints.py --cutoff 2021-05-01

Output: `D:\CFPB_complaints\complaints_recent.csv` (~6.5 GB, ~12.8M rows).
Run takes 5–10 minutes.

## Open the report

1. Open `pbix/cfpb-complaints.pbix` in Power BI Desktop.
2. The `Complaints` query reads `D:\CFPB_complaints\complaints_recent.csv`.
If you saved your sliced CSV elsewhere, open Power Query Editor → Complaints
query → first step → update `SourcePath` to your file.
3. **Home → Refresh.** First refresh takes 3–5 minutes for ~12.8M rows.

## Refresh strategy

- **During development:** drop the `--cutoff` to a more recent date (e.g.
`2024-01-01`) for faster iteration, then bump it back before publishing
screenshots.
- **For fresher data:** re-download the bulk ZIP from CFPB, re-run the slicer,
refresh Power BI. CFPB updates daily but a 2–4 week cadence is fine for
most analytical questions.

## Working directory vs repo

Large data files (`complaints.csv`, `complaints_recent.csv`) live outside the
repo at `D:\CFPB_complaints\` and are gitignored. The repo contains code,
documentation, and (optionally) the .pbix.
