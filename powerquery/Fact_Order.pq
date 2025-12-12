// ============================================================
// Fact_Order - Order Fact Table
// Links visits to orders for 60-day conversion tracking
// Based on actual 'public user_orders' schema
// User linkage via visits table (created_by_id)
// ============================================================

let
    // Reference the existing 'public user_orders' table in Power BI
    Source = #"public user_orders",
    
    // ---- Select Core Columns from actual schema ----
    // Use MissingField.UseNull to avoid refresh failures if columns are absent in a given environment.
    SelectedColumns = Table.SelectColumns(Source, {
        "id", "order_status", "order_type", "order_category", "delivery_method",
        "site_id", "dealer_id", "retailer_id", "bazaar_id", "project_conversion_id",
        "organization_id",
        "total_amount", "stage", "delivery_address",
        "is_engineer_eligible", "is_partner_eligible",
        "memo_photo", "feedback", "created_at", "updated_at"
    }, MissingField.UseNull),
    
    // ---- Get User ID from Visits table (via site_id linkage) ----
    // Create a 1-row-per-site lookup (prevents order duplication on join)
    VisitsSource = #"public visits",
    VisitsForLookup = Table.SelectColumns(
        VisitsSource,
        {"potential_site_id", "created_by_id", "created_at", "delete_status"},
        MissingField.UseNull
    ),
    VisitsActive = Table.SelectRows(
        VisitsForLookup,
        each [potential_site_id] <> null
            and [created_by_id] <> null
            and ([delete_status] = null or Text.Upper(Text.From([delete_status])) = "NO")
    ),
    VisitUserLookup = Table.Group(
        VisitsActive,
        {"potential_site_id"},
        {
            {
                "created_by_id",
                each
                    let
                        Sorted = Table.Sort(_, {{"created_at", Order.Ascending}}),
                        FirstRow = try Sorted{0} otherwise null
                    in
                        if FirstRow = null then null else FirstRow[created_by_id],
                Int64.Type
            }
        }
    ),
    
    // ---- Rename Columns ----
    RenamedColumns = Table.RenameColumns(SelectedColumns, {
        {"id", "OrderID"},
        {"order_status", "OrderStatus"},
        {"order_type", "OrderType"},
        {"order_category", "OrderCategory"},
        {"delivery_method", "DeliveryMethod"},
        {"site_id", "SiteID"},
        {"dealer_id", "DealerID"},
        {"retailer_id", "RetailerID"},
        {"bazaar_id", "BazaarID"},
        {"project_conversion_id", "ProjectConversionID"},
        {"organization_id", "OrganizationID"},
        {"total_amount", "TotalAmount"},
        {"stage", "Stage"},
        {"delivery_address", "DeliveryAddress"},
        {"is_engineer_eligible", "IsEngineerEligible"},
        {"is_partner_eligible", "IsPartnerEligible"},
        {"memo_photo", "MemoPhoto"},
        {"feedback", "Feedback"}
    }, MissingField.Ignore),

    // Ensure OrganizationID exists even if the source column is missing
    WithOrganizationID = if Table.HasColumns(RenamedColumns, "OrganizationID")
        then RenamedColumns
        else Table.AddColumn(RenamedColumns, "OrganizationID", each null, Int64.Type),

    // ---- Company Code (ACL/AIL) ----
    WithCompanyCode = Table.AddColumn(WithOrganizationID, "CompanyCode", each
        if [OrganizationID] = 1 then "ACL"
        else if [OrganizationID] = 2 then "AIL"
        else "Unknown",
        type text
    ),
    
    // ---- Join with Visit Lookup to get UserID (CreatedBy) ----
    // This links orders to the user who created the associated site visit
    WithUserLookup = Table.NestedJoin(
        WithCompanyCode, {"SiteID"},
        VisitUserLookup, {"potential_site_id"},
        "VisitUserTable", JoinKind.LeftOuter
    ),
    
    // Expand to get UserID (created_by_id from visits)
    WithUserExpanded = Table.ExpandTableColumn(
        WithUserLookup, 
        "VisitUserTable", 
        {"created_by_id"}, 
        {"UserID"}
    ),
    
    // ---- Extract Date Key ----
    WithDateKey = Table.AddColumn(WithUserExpanded, "OrderDateKey", each 
        Date.From([created_at]),
        type date
    ),
    
    // ---- Create Client Key (for Site orders) ----
    WithClientKey = Table.AddColumn(WithDateKey, "ClientKey", each 
        if [SiteID] <> null then "Site-" & Text.From([SiteID])
        else if [DealerID] <> null then "Dealer-" & Text.From([DealerID])
        else if [RetailerID] <> null then "Retailer-" & Text.From([RetailerID])
        else if [BazaarID] <> null then "Bazaar-" & Text.From([BazaarID])
        else null,
        type text
    ),
    
    // ---- Order Status Mapping (status is uppercase: PENDING, etc.) ----
    WithStatusGroup = Table.AddColumn(WithClientKey, "StatusGroup", each 
        if Text.Upper([OrderStatus]) = "PENDING" or Text.Upper([OrderStatus]) = "PROCESSING" then "Open"
        else if Text.Upper([OrderStatus]) = "COMPLETED" or Text.Upper([OrderStatus]) = "DELIVERED" then "Completed"
        else if Text.Upper([OrderStatus]) = "CANCELLED" then "Cancelled"
        else "Other",
        type text
    ),
    
    // ---- Is Converted Flag ----
    WithConvertedFlag = Table.AddColumn(WithStatusGroup, "IsConverted", each 
        if [StatusGroup] = "Completed" then 1 else 0,
        Int64.Type
    ),
    
    // ---- Has Memo Photo Flag ----
    WithMemoPhotoFlag = Table.AddColumn(WithConvertedFlag, "HasMemoPhoto", each 
        if [MemoPhoto] <> null and [MemoPhoto] <> "" then 1 else 0,
        Int64.Type
    ),

    // ---- Helper: normalize flags to logical safely (supports 0/1, true/false, and common text) ----
    AsLogicalFlag = (v as any) as nullable logical =>
        let
            n = try Number.From(v) otherwise null,
            s = if n <> null then null else (try Text.Lower(Text.From(v)) otherwise null),
            b =
                if n <> null then (n <> 0)
                else if s = null then null
                else if s = "true" or s = "t" or s = "yes" or s = "y" then true
                else if s = "false" or s = "f" or s = "no" or s = "n" then false
                else
                    let
                        nn = try Number.FromText(s) otherwise null
                    in
                        if nn = null then null else (nn <> 0)
        in
            b,

    // Normalize eligibility flags before typing to avoid PostgreSQL folding issues (integer = boolean)
    WithEligibilityFlags = Table.TransformColumns(
        WithMemoPhotoFlag,
        {
            {"IsEngineerEligible", each AsLogicalFlag(_), type nullable logical},
            {"IsPartnerEligible", each AsLogicalFlag(_), type nullable logical}
        },
        null,
        MissingField.Ignore
    ),
    
    // ---- Set Data Types ----
    TypedTable = Table.TransformColumnTypes(WithEligibilityFlags, {
        {"OrderID", Int64.Type},
        {"OrderStatus", type text},
        {"OrderType", type text},
        {"OrderCategory", type text},
        {"DeliveryMethod", type text},
        {"SiteID", Int64.Type},
        {"DealerID", Int64.Type},
        {"RetailerID", Int64.Type},
        {"BazaarID", Int64.Type},
        {"ProjectConversionID", Int64.Type},
        {"OrganizationID", Int64.Type},
        {"CompanyCode", type text},
        {"TotalAmount", type text},  // Stored as text in source
        {"Stage", type text},
        {"DeliveryAddress", type text},
        {"MemoPhoto", type text},
        {"Feedback", type text},
        {"OrderDateKey", type date},
        {"ClientKey", type text},
        {"StatusGroup", type text},
        {"IsConverted", Int64.Type},
        {"HasMemoPhoto", Int64.Type},
        {"UserID", Int64.Type},
        {"created_at", type datetime},
        {"updated_at", type datetime}
    }),
    
    // ---- Convert TotalAmount to number ----
    WithNumericAmount = Table.TransformColumns(TypedTable, {{"TotalAmount", each try Number.From(_) otherwise 0, type number}}),

    // ---- Quantity Normalization ----
    // Audit rule: ACL orders are in bags (20 bags = 1 MT), AIL orders are already in MT.
    WithTotalQuantityRaw = Table.AddColumn(WithNumericAmount, "TotalQuantityRaw", each [TotalAmount], type number),
    WithTotalQuantityMT = Table.AddColumn(WithTotalQuantityRaw, "TotalQuantityMT", each
        if [CompanyCode] = "ACL" then [TotalQuantityRaw] / 20
        else if [CompanyCode] = "AIL" then [TotalQuantityRaw]
        else null,
        type number
    ),
    
    // ---- Reorder Columns ----
    ReorderedColumns = Table.ReorderColumns(WithTotalQuantityMT, {
        "OrderID", "OrderDateKey", "UserID", "ClientKey",
        "SiteID", "DealerID", "RetailerID", "BazaarID", "ProjectConversionID",
        "OrganizationID", "CompanyCode",
        "OrderStatus", "StatusGroup", "OrderType", "OrderCategory",
        "DeliveryMethod", "DeliveryAddress", "Stage",
        "TotalAmount", "TotalQuantityRaw", "TotalQuantityMT", "IsConverted", "HasMemoPhoto",
        "IsEngineerEligible", "IsPartnerEligible",
        "MemoPhoto", "Feedback",
        "created_at", "updated_at"
    })
in
    ReorderedColumns
