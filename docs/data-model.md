# Data Model

## Tables

| Table | Source | Grain | Notes |
|---|---|---|---|
| `Complaints` | CFPB API | One row per complaint | Pulled live, last 90 days |
| `Date` | Generated in M | One row per day | Built with `List.Dates`; needed for time-intelligence DAX |

## Ingestion strategy: why local-baseline, not live-refresh

I evaluated three ingestion strategies before settling on a manual bulk-CSV
slice as the v1 ingestion layer. Documenting the trade-offs here because
"why we chose this" is more important than "what we did."

### Option 1: CFPB Search API (`/search/api/v1/`)
**Rejected.** The API caps pagination at `from + size ≤ 10,000`. Faceting the
request by state to keep each chunk under the cap surfaced inconsistent
behavior — Alabama queries paginated past 10k on dates that should return
~100 rows. Aggressive call patterns also surface 429 rate limits. The API is
designed for narrow ad-hoc queries, not bulk ingestion.

### Option 2: Bulk CSV ZIP via Power Query (`Web.Contents` + custom unzip)
**Deferred to v2.** The bulk CSV is ~1.7 GB compressed, ~8.4 GB uncompressed.
End-to-end refresh would be 10–20 minutes per refresh. Acceptable for a
published live report; punishing during dashboard iteration. Also requires
a custom `UnzipContents` M function (~80 LOC).

### Option 3: Local CSV slice (selected for v1)
**Selected.** Manual download of the bulk ZIP, slice to a 5-year window with
`scripts/slice_complaints.py`, point Power BI at the local file. Refresh in
Power BI takes 3–5 minutes. Trade-off: data freshness depends on manual
re-cut cadence (target: every 2–4 weeks).

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
