// ============================================================
// Fact_Visit - Visit Fact Table
// Based on actual 'public visits' table schema from Power BI
// Total Records: 36,041 visits
// 
// INFLUENCER SEGREGATION (per PRD.MD):
// - "Influencer" visits are actually Engineers (managed by BDO)
// - Contractor visits use contractor_id (managed by CRO)
// ============================================================

let
    // Reference the existing 'public visits' table in Power BI
    // This connects to the semantic model's existing data source
    Source = #"public visits",
    
    // ---- Select Core Columns from actual schema ----
    SelectedColumns = Table.SelectColumns(Source, {
        "id", "visit_type", "created_by_id", "create_by_name", "visit_date_time", 
        "feedback", "visit_photo", "product_photo", "visit_category_id",
        "visit_phase_id", "visit_stage_id", "status", "followup_date",
        // Client ID columns (one populated based on visit_type)
        "potential_site_id", "retailer_id", "dealer_id", 
        "engineer_id", "contractor_id", "ihb_registration_id", "head_mason_id",
        "site_manager_id", "organization_id",
        // Territory info
        "territory_id", "territory_name", "role_level",
        // Metadata
        "origin", "delete_status", "created_at", "updated_at"
    }),
    
    // ---- Create Unified ClientKey ----
    // Maps the appropriate ID column based on visit_type
    // Visit Types: Sites (13,235), Influencer (7,114), Dealer (5,587), 
    //              Retailer (4,020), IHB (3,807), General Sites (2,278)
    // 
    // INFLUENCER SEGREGATION (per PRD):
    // - Influencer visits with engineer_id → "Engineer" (BDO manages)
    // - Influencer visits with contractor_id → "Contractor" (CRO manages Partners)
    WithClientType = Table.AddColumn(SelectedColumns, "ClientType", each 
        if [visit_type] = "Sites" then "Site"
        else if [visit_type] = "Retailer" then "Retailer"
        else if [visit_type] = "Dealer" then "Dealer"
        else if [visit_type] = "Influencer" then 
            // INFLUENCER SEGREGATION: Check which ID is populated
            if [engineer_id] <> null then "Engineer"       // BDO manages Engineers
            else if [contractor_id] <> null then "Contractor"  // CRO manages Partners/Contractors
            else "Influencer"  // Fallback for uncategorized Influencers
        else if [visit_type] = "IHB" then "IHB"
        else if [visit_type] = "General Sites" then "General"
        else "Unknown", 
        type text
    ),
    
    // Use ClientType directly (no need for secondary check)
    WithContractorCheck = Table.AddColumn(WithClientType, "ClientType_Final", each 
        [ClientType],
        type text
    ),
    
    // Extract the appropriate client ID based on visit type
    WithClientID = Table.AddColumn(WithContractorCheck, "ClientID", each 
        if [ClientType_Final] = "Site" then [potential_site_id]
        else if [ClientType_Final] = "Retailer" then [retailer_id]
        else if [ClientType_Final] = "Dealer" then [dealer_id]
        else if [ClientType_Final] = "Engineer" then [engineer_id]  // Engineers managed by BDO
        else if [ClientType_Final] = "Contractor" then [contractor_id]  // Contractors/Partners managed by CRO
        else if [ClientType_Final] = "IHB" then [ihb_registration_id]
        else null,
        Int64.Type
    ),
    
    // Add Responsible Role based on client type (for filtering/RLS)
    WithResponsibleRole = Table.AddColumn(WithClientID, "ResponsibleRole", each 
        if [ClientType_Final] = "Site" then "BDO"
        else if [ClientType_Final] = "Engineer" then "BDO"
        else if [ClientType_Final] = "Contractor" then "CRO"
        else if [ClientType_Final] = "Retailer" then "SR"
        else if [ClientType_Final] = "Dealer" then "CRO"
        else if [ClientType_Final] = "IHB" then "CRO,BDO"
        else "All",
        type text
    ),
    
    // Create composite ClientKey to match Dim_Client
    WithClientKey = Table.AddColumn(WithResponsibleRole, "ClientKey", each 
        if [ClientID] <> null then [ClientType_Final] & "-" & Text.From([ClientID])
        else null,
        type text
    ),
    
    // Remove the intermediate ClientType column, use ClientType_Final
    RemovedIntermediate = Table.RemoveColumns(WithClientKey, {"ClientType"}),
    RenamedClientType = Table.RenameColumns(RemovedIntermediate, {{"ClientType_Final", "ClientType"}}),
    
    // ---- Add Quality Metrics ----
    // Photo Compliance (1 if visit_photo exists, 0 otherwise)
    WithPhotoFlag = Table.AddColumn(RenamedClientType, "HasPhoto", each 
        if [visit_photo] <> null and [visit_photo] <> "" then 1 else 0,
        Int64.Type
    ),
    
    // Product Photo Captured
    WithProductPhotoFlag = Table.AddColumn(WithPhotoFlag, "HasProductPhoto", each 
        if [product_photo] <> null and [product_photo] <> "" then 1 else 0,
        Int64.Type
    ),
    
    // Feedback Provided (1 if feedback exists, 0 otherwise)
    WithFeedbackFlag = Table.AddColumn(WithProductPhotoFlag, "HasFeedback", each 
        if [feedback] <> null and [feedback] <> "" then 1 else 0,
        Int64.Type
    ),
    
    // Territory Captured (1 if territory_id exists, 0 otherwise)
    WithTerritoryFlag = Table.AddColumn(WithFeedbackFlag, "HasTerritory", each 
        if [territory_id] <> null then 1 else 0,
        Int64.Type
    ),
    
    // ---- Extract Date Key for Dim_Date join ----
    WithDateKey = Table.AddColumn(WithTerritoryFlag, "DateKey", each 
        Date.From([visit_date_time]),
        type date
    ),
    
    // ---- Rename ID column ----
    RenamedColumns = Table.RenameColumns(WithDateKey, {
        {"id", "VisitID"},
        {"created_by_id", "EmployeeID"},
        {"create_by_name", "EmployeeName"},
        {"visit_category_id", "VisitCategoryID"},
        {"visit_phase_id", "VisitPhaseID"},
        {"visit_stage_id", "VisitStageID"},
        {"role_level", "RoleLevel"}
    }),
    
    // ---- Remove individual client ID columns (now unified) ----
    CleanedColumns = Table.RemoveColumns(RenamedColumns, {
        "potential_site_id", "retailer_id", "dealer_id", 
        "engineer_id", "contractor_id", "ihb_registration_id", 
        "head_mason_id", "site_manager_id"
    }),
    
    // ---- Filter out deleted records ----
    ActiveRecords = Table.SelectRows(CleanedColumns, each [delete_status] = "NO"),
    
    // ---- Reorder Columns ----
    ReorderedColumns = Table.ReorderColumns(ActiveRecords, {
        "VisitID", "DateKey", "EmployeeID", "EmployeeName", "RoleLevel",
        "ClientKey", "ClientType", "ClientID", "ResponsibleRole", "visit_type", 
        "VisitCategoryID", "VisitPhaseID", "VisitStageID", "status",
        "feedback", "visit_photo", "product_photo",
        "HasPhoto", "HasProductPhoto", "HasFeedback", "HasTerritory",
        "territory_id", "territory_name", "followup_date",
        "origin", "visit_date_time", "created_at", "updated_at"
    }),
    
    // ---- Set Data Types ----
    TypedTable = Table.TransformColumnTypes(ReorderedColumns, {
        {"VisitID", Int64.Type},
        {"DateKey", type date},
        {"EmployeeID", Int64.Type},
        {"EmployeeName", type text},
        {"RoleLevel", Int64.Type},
        {"ClientKey", type text},
        {"ClientType", type text},
        {"ClientID", Int64.Type},
        {"ResponsibleRole", type text},
        {"visit_type", type text},
        {"VisitCategoryID", Int64.Type},
        {"VisitPhaseID", Int64.Type},
        {"VisitStageID", Int64.Type},
        {"status", type text},
        {"feedback", type text},
        {"visit_photo", type text},
        {"product_photo", type text},
        {"HasPhoto", Int64.Type},
        {"HasProductPhoto", Int64.Type},
        {"HasFeedback", Int64.Type},
        {"HasTerritory", Int64.Type},
        {"territory_id", Int64.Type},
        {"territory_name", type text},
        {"followup_date", type datetime},
        {"origin", type text},
        {"visit_date_time", type datetime},
        {"created_at", type datetime},
        {"updated_at", type datetime}
    })
in
    TypedTable
