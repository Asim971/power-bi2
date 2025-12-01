// ============================================================
// Dim_Client_Simple - Unified Client Dimension (Simplified)
// No complex joins - uses direct columns from source tables
// 
// Client Types (6 per PRD):
// 1. Sites (potential_site) - BDO managed
// 2. Retailers - SR managed
// 3. IHB (ihb_registration) - CRO/BDO managed
// 4. Dealers - CRO managed
// 5. Engineers - BDO managed
// 6. Contractors - CRO managed
// 
// SCHEMA NOTES (Nov 2025):
// - Retailers: is_deleted = "NO" (text)
// - Dealers: is_deleted = "NO" (text)
// - IHB, Engineers, Contractors: no delete column
// ============================================================

let
    // ============================================================
    // 1. SITES (potential_site)
    // ============================================================
    SitesSource = #"public potential_site",
    SitesFiltered = Table.SelectRows(SitesSource, each [delete_status] = "NO"),
    SitesBase = Table.SelectColumns(SitesFiltered, {
        "id", "project_name", "bazaar_id", "site_type", "territory_name", "area_name"
    }),
    SitesFinal = Table.AddColumn(SitesBase, "ClientType", each "Site", type text),
    SitesFinal2 = Table.AddColumn(SitesFinal, "ResponsibleRole", each "BDO", type text),
    SitesRenamed = Table.RenameColumns(SitesFinal2, {
        {"id", "ClientID"}, 
        {"project_name", "ClientName"}, 
        {"site_type", "SubType"},
        {"bazaar_id", "BazaarID"},
        {"territory_name", "TerritoryName"},
        {"area_name", "AreaName"}
    }),
    SitesClean = Table.SelectColumns(SitesRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole", "BazaarID", "TerritoryName", "AreaName"
    }),

    // ============================================================
    // 2. RETAILERS
    // ============================================================
    RetailersSource = #"public retailers",
    RetailersFiltered = Table.SelectRows(RetailersSource, each [is_deleted] = "NO"),
    RetailersBase = Table.SelectColumns(RetailersFiltered, {"id", "name", "shop_name", "bazaar_id"}),
    RetailersFinal = Table.AddColumn(RetailersBase, "ClientType", each "Retailer", type text),
    RetailersFinal2 = Table.AddColumn(RetailersFinal, "SubType", each null, type text),
    RetailersFinal3 = Table.AddColumn(RetailersFinal2, "ResponsibleRole", each "SR", type text),
    RetailersFinal4 = Table.AddColumn(RetailersFinal3, "TerritoryName", each null, type text),
    RetailersFinal5 = Table.AddColumn(RetailersFinal4, "AreaName", each null, type text),
    RetailersRenamed = Table.RenameColumns(RetailersFinal5, {
        {"id", "ClientID"}, {"name", "ClientName"}, {"bazaar_id", "BazaarID"}
    }),
    RetailersClean = Table.SelectColumns(RetailersRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole", "BazaarID", "TerritoryName", "AreaName"
    }),

    // ============================================================
    // 3. IHB (ihb_registration) - No delete column
    // ============================================================
    IHBSource = #"public ihb_registration",
    IHBBase = Table.SelectColumns(IHBSource, {"id", "bazaar_id", "end_user"}),
    IHBFinal = Table.AddColumn(IHBBase, "ClientType", each "IHB", type text),
    IHBFinal2 = Table.AddColumn(IHBFinal, "ClientName", each "IHB-" & Text.From([id]), type text),
    IHBFinal3 = Table.AddColumn(IHBFinal2, "SubType", each [end_user], type text),
    IHBFinal4 = Table.AddColumn(IHBFinal3, "ResponsibleRole", each "CRO,BDO", type text),
    IHBFinal5 = Table.AddColumn(IHBFinal4, "TerritoryName", each null, type text),
    IHBFinal6 = Table.AddColumn(IHBFinal5, "AreaName", each null, type text),
    IHBRenamed = Table.RenameColumns(IHBFinal6, {{"id", "ClientID"}, {"bazaar_id", "BazaarID"}}),
    IHBClean = Table.SelectColumns(IHBRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole", "BazaarID", "TerritoryName", "AreaName"
    }),

    // ============================================================
    // 4. DEALERS
    // ============================================================
    DealersSource = #"public dealers",
    DealersFiltered = Table.SelectRows(DealersSource, each [is_deleted] = "NO"),
    DealersBase = Table.SelectColumns(DealersFiltered, {"id", "name", "shop_name", "district_name_text"}),
    DealersFinal = Table.AddColumn(DealersBase, "ClientType", each "Dealer", type text),
    DealersFinal2 = Table.AddColumn(DealersFinal, "SubType", each null, type text),
    DealersFinal3 = Table.AddColumn(DealersFinal2, "ResponsibleRole", each "CRO", type text),
    DealersFinal4 = Table.AddColumn(DealersFinal3, "BazaarID", each null, Int64.Type),
    DealersFinal5 = Table.AddColumn(DealersFinal4, "TerritoryName", each null, type text),
    DealersFinal6 = Table.AddColumn(DealersFinal5, "AreaName", each [district_name_text], type text),
    DealersRenamed = Table.RenameColumns(DealersFinal6, {{"id", "ClientID"}, {"name", "ClientName"}}),
    DealersClean = Table.SelectColumns(DealersRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole", "BazaarID", "TerritoryName", "AreaName"
    }),

    // ============================================================
    // 5. ENGINEERS - No delete column
    // ============================================================
    EngineersSource = #"public engineers",
    EngineersBase = Table.SelectColumns(EngineersSource, {"id", "engineer_type", "consultancy_firm"}),
    EngineersFinal = Table.AddColumn(EngineersBase, "ClientType", each "Engineer", type text),
    EngineersFinal2 = Table.AddColumn(EngineersFinal, "ClientName", each 
        if [consultancy_firm] <> null and [consultancy_firm] <> "" then [consultancy_firm] 
        else "Engineer-" & Text.From([id]), type text),
    EngineersFinal3 = Table.AddColumn(EngineersFinal2, "SubType", each [engineer_type], type text),
    EngineersFinal4 = Table.AddColumn(EngineersFinal3, "ResponsibleRole", each "BDO", type text),
    EngineersFinal5 = Table.AddColumn(EngineersFinal4, "BazaarID", each null, Int64.Type),
    EngineersFinal6 = Table.AddColumn(EngineersFinal5, "TerritoryName", each null, type text),
    EngineersFinal7 = Table.AddColumn(EngineersFinal6, "AreaName", each null, type text),
    EngineersRenamed = Table.RenameColumns(EngineersFinal7, {{"id", "ClientID"}}),
    EngineersClean = Table.SelectColumns(EngineersRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole", "BazaarID", "TerritoryName", "AreaName"
    }),

    // ============================================================
    // 6. CONTRACTORS - No delete column
    // ============================================================
    ContractorSource = #"public contractor",
    ContractorBase = Table.SelectColumns(ContractorSource, {"id"}),
    ContractorFinal = Table.AddColumn(ContractorBase, "ClientType", each "Contractor", type text),
    ContractorFinal2 = Table.AddColumn(ContractorFinal, "ClientName", each "Partner-" & Text.From([id]), type text),
    ContractorFinal3 = Table.AddColumn(ContractorFinal2, "SubType", each "Partner", type text),
    ContractorFinal4 = Table.AddColumn(ContractorFinal3, "ResponsibleRole", each "CRO", type text),
    ContractorFinal5 = Table.AddColumn(ContractorFinal4, "BazaarID", each null, Int64.Type),
    ContractorFinal6 = Table.AddColumn(ContractorFinal5, "TerritoryName", each null, type text),
    ContractorFinal7 = Table.AddColumn(ContractorFinal6, "AreaName", each null, type text),
    ContractorRenamed = Table.RenameColumns(ContractorFinal7, {{"id", "ClientID"}}),
    ContractorClean = Table.SelectColumns(ContractorRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole", "BazaarID", "TerritoryName", "AreaName"
    }),

    // ============================================================
    // COMBINE ALL CLIENT TYPES
    // ============================================================
    AllClients = Table.Combine({
        SitesClean, 
        RetailersClean, 
        IHBClean,
        DealersClean, 
        EngineersClean,
        ContractorClean
    }),

    // ============================================================
    // FINAL PROCESSING
    // ============================================================
    
    // Create Composite Key (ClientType + ClientID) for uniqueness
    WithCompositeKey = Table.AddColumn(AllClients, "ClientKey", 
        each [ClientType] & "-" & Text.From([ClientID]), type text),
    
    // Add Client Category
    WithCategory = Table.AddColumn(WithCompositeKey, "ClientCategory", each 
        if [ClientType] = "Site" then "Prospect"
        else if [ClientType] = "Dealer" or [ClientType] = "Retailer" then "Channel Partner"
        else if [ClientType] = "Engineer" then "Influencer-Technical"
        else if [ClientType] = "Contractor" then "Influencer-Partner"
        else if [ClientType] = "IHB" then "End Customer"
        else "Other",
        type text
    ),
    
    // Add RLS Role
    WithResponsibleRoleRLS = Table.AddColumn(WithCategory, "ResponsibleRoleRLS", each 
        if [ClientType] = "Site" then "BDO"
        else if [ClientType] = "Engineer" then "BDO"
        else if [ClientType] = "Contractor" then "CRO"
        else if [ClientType] = "Retailer" then "SR"
        else if [ClientType] = "Dealer" then "CRO"
        else if [ClientType] = "IHB" then "CRO,BDO"
        else "All",
        type text
    ),
    
    // Reorder Columns
    ReorderedColumns = Table.ReorderColumns(WithResponsibleRoleRLS, {
        "ClientKey", "ClientID", "ClientName", "ClientType", "SubType", "ClientCategory",
        "ResponsibleRole", "ResponsibleRoleRLS", "BazaarID", "TerritoryName", "AreaName"
    }),
    
    // Set Data Types
    TypedTable = Table.TransformColumnTypes(ReorderedColumns, {
        {"ClientKey", type text},
        {"ClientID", Int64.Type},
        {"ClientName", type text},
        {"ClientType", type text},
        {"SubType", type text},
        {"ClientCategory", type text},
        {"ResponsibleRole", type text},
        {"ResponsibleRoleRLS", type text},
        {"BazaarID", Int64.Type},
        {"TerritoryName", type text},
        {"AreaName", type text}
    })
in
    TypedTable
