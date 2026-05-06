# Data Model

## Tables

| Table | Source | Grain | Notes |
|---|---|---|---|
| `Complaints` | CFPB API | One row per complaint | Pulled live, last 90 days |
| `Date` | Generated in M | One row per day | Built with `List.Dates`; needed for time-intelligence DAX |

## Relationships

- `Complaints[date_received]` → `Date[Date]` (many-to-one, single direction)

## Star schema diagram

> _To add: a diagram or screenshot of the model view from Power BI Desktop._

## Field reference

| Column | Type | Notes |
|---|---|---|
| complaint_id | Int64 | Unique key |
| date_received | date | Used as the primary fact-table date |
| date_sent_to_company | date | For computing CFPB→company handoff latency |
| product / sub_product | text | Hierarchical (e.g., "Mortgage" → "Conventional home mortgage") |
| issue / sub_issue | text | Hierarchical complaint reason |
| company | text | Named institution |
| company_response | text | Disposition (e.g., "Closed with explanation") |
| state | text | 2-letter US state code |
| zip_code | text | Often masked to 3 digits in CFPB output |
| timely | logical | Did the company respond within CFPB's SLA |
| consumer_disputed | text | Legacy field; CFPB stopped collecting in 2017 |

## Why we slice the data

CFPB's bulk CSV is the full historical complaint database since 2011 — ~5M+
rows, 8.4 GB unzipped at the time of writing. The CFPB Search API caps
pagination at the first 10,000 results, so it cannot serve as a bulk-export
endpoint either.

The pragmatic solution: download the bulk file once, slice it to a recent
window with the helper script in `scripts/slice_complaints.py`, and point
Power BI at the smaller file. The window is configurable; v1 uses the most
recent 24 months.

For a future v2, the slicing step could be replaced by Power BI's
Incremental Refresh feature (Pro license required), which would maintain
historical partitions automatically while only refreshing the most recent
slice from the bulk file.
