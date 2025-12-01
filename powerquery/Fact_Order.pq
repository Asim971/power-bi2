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
    SelectedColumns = Table.SelectColumns(Source, {
        "id", "order_status", "order_type", "order_category", "delivery_method",
        "site_id", "dealer_id", "retailer_id", "bazaar_id", "project_conversion_id",
        "total_amount", "stage", "delivery_address",
        "is_engineer_eligible", "is_partner_eligible",
        "memo_photo", "feedback", "created_at", "updated_at"
    }),
    
    // ---- Get User ID from Visits table (via site_id linkage) ----
    // Create lookup table from visits: site_id -> created_by_id
    VisitsSource = #"public visits",
    VisitUserLookup = Table.SelectColumns(
        Table.Distinct(
            Table.SelectColumns(VisitsSource, {"potential_site_id", "created_by_id"})
        ),
        {"potential_site_id", "created_by_id"}
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
        {"total_amount", "TotalAmount"},
        {"stage", "Stage"},
        {"delivery_address", "DeliveryAddress"},
        {"is_engineer_eligible", "IsEngineerEligible"},
        {"is_partner_eligible", "IsPartnerEligible"},
        {"memo_photo", "MemoPhoto"},
        {"feedback", "Feedback"}
    }),
    
    // ---- Join with Visit Lookup to get UserID (CreatedBy) ----
    // This links orders to the user who created the associated site visit
    WithUserLookup = Table.NestedJoin(
        RenamedColumns, {"SiteID"},
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
    
    // ---- Set Data Types ----
    TypedTable = Table.TransformColumnTypes(WithMemoPhotoFlag, {
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
        {"TotalAmount", type text},  // Stored as text in source
        {"Stage", type text},
        {"DeliveryAddress", type text},
        {"IsEngineerEligible", type logical},
        {"IsPartnerEligible", type logical},
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
    
    // ---- Reorder Columns ----
    ReorderedColumns = Table.ReorderColumns(WithNumericAmount, {
        "OrderID", "OrderDateKey", "UserID", "ClientKey", 
        "SiteID", "DealerID", "RetailerID", "BazaarID", "ProjectConversionID",
        "OrderStatus", "StatusGroup", "OrderType", "OrderCategory",
        "DeliveryMethod", "DeliveryAddress", "Stage",
        "TotalAmount", "IsConverted", "HasMemoPhoto",
        "IsEngineerEligible", "IsPartnerEligible",
        "MemoPhoto", "Feedback",
        "created_at", "updated_at"
    })
in
    ReorderedColumns
