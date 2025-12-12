// ============================================================
// Fact_ProjectConversion - Project Conversion Fact Table
// Source: public project_conversion (836 records)
// 
// PURPOSE:
// Tracks the conversion journey from Site visit to Order
// Links Engineers/Contractors to conversion rewards
// 
// KEY FIELDS (from ERD analysis):
// - order_status, delivery_method
// - loyalty_of_engineer, loyalty_of_contractor (reward eligibility)
// - assigned_sr, assigned_cro, assigned_bdo, assigned_asm (role assignments)
// - site_id, engineer_id, dealer_id, retailer_id, bazaar_id
// ============================================================

let
    // Reference the existing 'public project_conversion' table in Power BI
    Source = #"public project_conversion",
    
    // ---- Get Available Columns ----
    AllColumns = Table.ColumnNames(Source),
    
    // ---- Define Expected Columns (based on ERD) ----
    ExpectedCoreColumns = {
        "id", "order_status", "delivery_method", "delete_status",
        "organization_id",
        "site_id", "engineer_id", "dealer_id", "retailer_id", "bazaar_id",
        "created_at", "updated_at"
    },
    
    // ---- Define Optional Columns ----
    OptionalColumns = {
        "loyalty_of_engineer", "loyalty_of_contractor",
        "assigned_sr", "assigned_cro", "assigned_bdo", "assigned_asm",
        "total_amount", "stage", "feedback"
    },
    
    // ---- Select Available Columns ----
    AvailableColumns = List.Select(
        ExpectedCoreColumns & OptionalColumns, 
        each List.Contains(AllColumns, _)
    ),
    
    SelectedColumns = Table.SelectColumns(Source, AvailableColumns),
    
    // ---- Rename Core Columns ----
    RenamedColumns = Table.RenameColumns(SelectedColumns, {
        {"id", "ConversionID"},
        {"order_status", "OrderStatus"},
        {"delivery_method", "DeliveryMethod"},
        {"organization_id", "OrganizationID"},
        {"site_id", "SiteID"},
        {"bazaar_id", "BazaarID"}
    }, MissingField.Ignore),

    // Ensure OrganizationID exists even if the source column is missing
    WithOrganizationID = if Table.HasColumns(RenamedColumns, "OrganizationID")
        then RenamedColumns
        else Table.AddColumn(RenamedColumns, "OrganizationID", each null, Int64.Type),
    
    // ---- Conditionally Rename Optional Columns ----
    WithRenames1 = if Table.HasColumns(WithOrganizationID, "engineer_id") 
        then Table.RenameColumns(WithOrganizationID, {{"engineer_id", "EngineerID"}})
        else WithOrganizationID,
    
    WithRenames2 = if Table.HasColumns(WithRenames1, "dealer_id") 
        then Table.RenameColumns(WithRenames1, {{"dealer_id", "DealerID"}})
        else WithRenames1,
    
    WithRenames3 = if Table.HasColumns(WithRenames2, "retailer_id") 
        then Table.RenameColumns(WithRenames2, {{"retailer_id", "RetailerID"}})
        else WithRenames2,
    
    WithRenames4 = if Table.HasColumns(WithRenames3, "loyalty_of_engineer") 
        then Table.RenameColumns(WithRenames3, {{"loyalty_of_engineer", "EngineerLoyalty"}})
        else WithRenames3,
    
    WithRenames5 = if Table.HasColumns(WithRenames4, "loyalty_of_contractor") 
        then Table.RenameColumns(WithRenames4, {{"loyalty_of_contractor", "ContractorLoyalty"}})
        else WithRenames4,
    
    FinalRenames = WithRenames5,
    
    // ---- Check if loyalty columns exist (evaluate once) ----
    HasEngineerLoyalty = Table.HasColumns(FinalRenames, "EngineerLoyalty"),
    HasContractorLoyalty = Table.HasColumns(FinalRenames, "ContractorLoyalty"),
    
    // ---- Filter out deleted records ----
    ActiveRecords =
        if Table.HasColumns(FinalRenames, "delete_status") then
            Table.SelectRows(
                FinalRenames,
                each
                    let
                        ds = try Text.Upper(Text.From([delete_status])) otherwise null
                    in
                        ds = null or ds = "NO"
            )
        else
            FinalRenames,

    // ---- Company Code (ACL/AIL) ----
    WithCompanyCode = Table.AddColumn(ActiveRecords, "CompanyCode", each
        if [OrganizationID] = 1 then "ACL"
        else if [OrganizationID] = 2 then "AIL"
        else "Unknown",
        type text
    ),
    
    // ---- Extract Date Key ----
    WithDateKey = Table.AddColumn(WithCompanyCode, "ConversionDateKey", each 
        Date.From([created_at]),
        type date
    ),
    
    // ---- Create Client Key (Site is primary for conversions) ----
    WithClientKey = Table.AddColumn(WithDateKey, "ClientKey", each 
        "Site-" & Text.From([SiteID]),
        type text
    ),
    
    // ---- Delivery Type Classification ----
    // Per PRD: "Factory DN" = Retail Delivery, "General Delivery" = CRO visit required
    WithDeliveryType = Table.AddColumn(WithClientKey, "DeliveryType", each 
        if [DeliveryMethod] = "Retail Delivery" then "Factory DN"
        else if [DeliveryMethod] = "General Delivery" then "General Delivery"
        else [DeliveryMethod],
        type text
    ),
    
    // ---- Conversion Status Group ----
    WithStatusGroup = Table.AddColumn(WithDeliveryType, "StatusGroup", each 
        if Text.Upper([OrderStatus]) = "PENDING" then "Pending"
        else if Text.Upper([OrderStatus]) = "APPROVED" or Text.Upper([OrderStatus]) = "COMPLETED" then "Converted"
        else if Text.Upper([OrderStatus]) = "CANCELLED" then "Cancelled"
        else "Other",
        type text
    ),
    
    // ---- Is Converted Flag ----
    WithConvertedFlag = Table.AddColumn(WithStatusGroup, "IsConverted", each 
        if [StatusGroup] = "Converted" then 1 else 0,
        Int64.Type
    ),
    
    // ---- Engineer Eligible for Reward ----
    WithEngineerReward = Table.AddColumn(WithConvertedFlag, "IsEngineerRewardEligible", each 
        if HasEngineerLoyalty and [IsConverted] = 1 and [EngineerLoyalty] = true then 1 else 0,
        Int64.Type
    ),
    
    // ---- Contractor Eligible for Reward ----
    WithContractorReward = Table.AddColumn(WithEngineerReward, "IsContractorRewardEligible", each 
        if HasContractorLoyalty and [IsConverted] = 1 and [ContractorLoyalty] = true then 1 else 0,
        Int64.Type
    ),
    
    // ---- Set Data Types ----
    TypedTable = Table.TransformColumnTypes(WithContractorReward, {
        {"ConversionID", Int64.Type},
        {"OrderStatus", type text},
        {"DeliveryMethod", type text},
        {"OrganizationID", Int64.Type},
        {"CompanyCode", type text},
        {"SiteID", Int64.Type},
        {"BazaarID", Int64.Type},
        {"ConversionDateKey", type date},
        {"ClientKey", type text},
        {"DeliveryType", type text},
        {"StatusGroup", type text},
        {"IsConverted", Int64.Type},
        {"IsEngineerRewardEligible", Int64.Type},
        {"IsContractorRewardEligible", Int64.Type},
        {"created_at", type datetime},
        {"updated_at", type datetime}
    })
in
    TypedTable
