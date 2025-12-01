// ============================================================
// Dim_VisitCategory - Visit Category Dimension
// Based on actual 'public visit_categories' table from Power BI
// 9 visit categories discovered from the source system
// ============================================================

let
    // Reference the existing 'public visit_categories' table in Power BI
    Source = #"public visit_categories",
    
    // ---- Select Core Columns from actual schema ----
    SelectedColumns = Table.SelectColumns(Source, {
        "id", "category_name", "delete_status"
    }),
    
    // ---- Filter Active Categories ----
    ActiveCategories = Table.SelectRows(SelectedColumns, each [delete_status] = "NO"),
    
    // ---- Rename Columns ----
    RenamedColumns = Table.RenameColumns(ActiveCategories, {
        {"id", "VisitCategoryID"},
        {"category_name", "CategoryName"}
    }),
    
    // ---- Add Category Type Grouping ----
    // Categories: Potential Sites, Dealer, Retailer, IHB, 
    //             Conversion Visit, Head Mason, Engineer, Contractor, Site Manager
    WithCategoryGroup = Table.AddColumn(RenamedColumns, "CategoryGroup", each 
        if [CategoryName] = "Potential Sites" then "Site Development"
        else if [CategoryName] = "Conversion Visit" then "Conversion"
        else if [CategoryName] = "Dealer" or [CategoryName] = "Retailer" then "Channel Partner"
        else if [CategoryName] = "IHB" then "Direct Customer"
        else if [CategoryName] = "Head Mason" or [CategoryName] = "Engineer" or 
                [CategoryName] = "Contractor" or [CategoryName] = "Site Manager" then "Influencer"
        else "Other",
        type text
    ),
    
    // ---- Add Is Influencer Flag ----
    WithInfluencerFlag = Table.AddColumn(WithCategoryGroup, "IsInfluencer", each 
        if [CategoryGroup] = "Influencer" then 1 else 0,
        Int64.Type
    ),
    
    // ---- Add Sort Order ----
    WithSortOrder = Table.AddColumn(WithInfluencerFlag, "CategorySortOrder", each [VisitCategoryID], Int64.Type),
    
    // ---- Remove delete_status column ----
    CleanedColumns = Table.RemoveColumns(WithSortOrder, {"delete_status"}),
    
    // ---- Set Data Types ----
    TypedTable = Table.TransformColumnTypes(CleanedColumns, {
        {"VisitCategoryID", Int64.Type},
        {"CategoryName", type text},
        {"CategoryGroup", type text},
        {"IsInfluencer", Int64.Type},
        {"CategorySortOrder", Int64.Type}
    })
in
    TypedTable
