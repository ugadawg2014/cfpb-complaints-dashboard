# Setup

## Prerequisites

- **Power BI Desktop** (free) — <https://powerbi.microsoft.com/desktop/>
- An internet connection (the report pulls live from CFPB)

## Steps

1. Clone or download this repository.
2. Open `pbix/cfpb-complaints.pbix` in Power BI Desktop.
3. When prompted for credentials on the CFPB endpoint, choose:
   - **Anonymous** authentication
   - **Public** privacy level
   - Scope to `https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/`
4. Click **Refresh**. First refresh takes 5–15 minutes (the API is
   uncompressed and paginates 1000 rows per request).
5. After refresh completes, all visuals populate automatically.

## Adjusting the data window

The `DaysBack` parameter at the top of the `Complaints` query controls how
much history is pulled. Defaults to 90 days. Raise it to 365 for a full year
or drop it to 30 for fast iteration.

## Refresh strategy

- During development: keep `DaysBack` low (30) for fast iteration.
- Before publishing screenshots: bump to the desired window and refresh once.
- For a production-style live refresh, this report is compatible with Power BI
  Service scheduled refresh (requires a Pro license).
