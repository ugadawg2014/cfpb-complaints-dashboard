// CFPB Consumer Complaint Database — live API ingestion
// Source: https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/
// Pulls complaints filed in the last `DaysBack` days, paginated 1000 rows per call.

let
    // ─── Parameters ─────────────────────────────────────────
    DaysBack  = 90,
    PageSize  = 1000,    // CFPB API caps at 1000

    StartDate = Date.ToText(
        Date.AddDays(Date.From(DateTime.LocalNow()), -DaysBack),
        "yyyy-MM-dd"
    ),

    BaseUrl = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/",

    KeepColumns = {
        "complaint_id",
        "date_received",
        "date_sent_to_company",
        "product",
        "sub_product",
        "issue",
        "sub_issue",
        "company",
        "company_response",
        "company_public_response",
        "state",
        "zip_code",
        "submitted_via",
        "tags",
        "timely",
        "consumer_disputed",
        "consumer_consent_provided"
    },

    // ─── Page fetcher ──────────────────────────────────────
    GetPage = (offset as number) =>
        let
            QueryString =
                "format=csv"
                & "&size=" & Text.From(PageSize)
                & "&frm=" & Text.From(offset)
                & "&date_received_min=" & StartDate
                & "&no_aggs=true"
                & "&no_highlight=true",

            Response = Web.Contents(
                BaseUrl,
                [
                    Query = [],
                    RelativePath = "?" & QueryString
                ]
            ),

            Csv = Csv.Document(
                Response,
                [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
            ),
            Promoted = Table.PromoteHeaders(Csv, [PromoteAllScalars = true])
        in
            Promoted,

    // ─── Walk pages until one comes back empty ─────────────
    Pages = List.Generate(
        () => [Offset = 0, Page = GetPage(0)],
        each Table.RowCount([Page]) > 0,
        each [
            Offset = [Offset] + PageSize,
            Page   = GetPage([Offset] + PageSize)
        ],
        each [Page]
    ),

    Combined = Table.Combine(Pages),

    // ─── Drop heavy columns we don't need (narrative, etc.) ──
    Trimmed = Table.SelectColumns(
        Combined,
        List.Intersect({KeepColumns, Table.ColumnNames(Combined)})
    ),

    // ─── Type the columns ─────────────────────────────────
    Typed = Table.TransformColumnTypes(Trimmed, {
        {"complaint_id",               Int64.Type},
        {"date_received",              type date},
        {"date_sent_to_company",       type date},
        {"product",                    type text},
        {"sub_product",                type text},
        {"issue",                      type text},
        {"sub_issue",                  type text},
        {"company",                    type text},
        {"company_response",           type text},
        {"company_public_response",    type text},
        {"state",                      type text},
        {"zip_code",                   type text},
        {"submitted_via",              type text},
        {"tags",                       type text},
        {"timely",                     type logical},
        {"consumer_disputed",          type text},
        {"consumer_consent_provided",  type text}
    })
in
    Typed
