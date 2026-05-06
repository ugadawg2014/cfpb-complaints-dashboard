# Data

This directory is intentionally empty in the repository.

The dashboard pulls complaint data **live** from the CFPB Search API on every
refresh. No raw data files are committed. See [`m-code/01_complaints_api.m`](../m-code/01_complaints_api.m)
for the ingestion query and [`docs/setup.md`](../docs/setup.md) for how to run it.

If you want a static snapshot for offline work, the bulk download is at:

- CSV: <https://files.consumerfinance.gov/ccdb/complaints.csv.zip>
- JSON: <https://files.consumerfinance.gov/ccdb/complaints.json.zip>

Place the unzipped CSV in this folder; `.gitignore` will keep it out of commits.
