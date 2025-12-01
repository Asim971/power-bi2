// ============================================================
// Dim_Client - Unified Client Dimension with Location Mapping
// Sources from master tables with Bazaar/Upazilla joins
// 
// Location Hierarchy: Zone → Region → Area → Territory → Bazaar → Upazilla → District
// 
// CLIENT LOCATION MAPPING (per PRD.MD):
// - Site:       potential_site.bazaar_id → bazaars → upazilla
// - Retailer:   retailers.bazaar_id → bazaars → upazilla  
// - IHB:        ihb_registration.bazaar_id → bazaars → upazilla
// - Dealer:     dealers (text-only district, no ID join)
// - Engineer:   engineers - Managed by BDO (no location - use visit)
// - Contractor: contractor - Partners managed by CRO (no location - use visit)
//
// INFLUENCER SEGREGATION (PRD Section 4.5):
// - BDO: Engineer Registration, Engineer Update Form
// - CRO: Partner Registration, Update Partner Form
// ============================================================

let
    // ============================================================
    // REFERENCE TABLES
    // ============================================================
    
    // Bazaars table - primary location for Sites, Retailers, IHB
    Bazaars = #"public bazaars",
    BazaarsActive = Table.SelectRows(Bazaars, each [delete_status] = "NO"),
    BazaarsLookup = Table.SelectColumns(BazaarsActive, {
        "id", "bazaar_name", "upazilla_id", "upazilla_name", 
        "district_id", "district_name", "zone_id", "zone_name"
    }),
    BazaarsRenamed = Table.RenameColumns(BazaarsLookup, {{"id", "bazaar_id_lookup"}}),
    
    // Upazilla table for additional hierarchy
    Upazilla = #"public upazilla",
    UpazillaActive = Table.SelectRows(Upazilla, each [delete_status] = "NO"),
    UpazillaLookup = Table.SelectColumns(UpazillaActive, {
        "id", "upazilla_name", "district_id", "district_name", 
        "zone_id", "zone_name", "territory_name"
    }),
    UpazillaRenamed = Table.RenameColumns(UpazillaLookup, {{"id", "upazilla_id_lookup"}}),
    
    // Districts for zone hierarchy
    Districts = #"public districts",
    DistrictsActive = Table.SelectRows(Districts, each [delete_status] = "NO"),
    DistrictsLookup = Table.SelectColumns(DistrictsActive, {
        "id", "district_name", "zone_id", "zone_name"
    }),
    DistrictsRenamed = Table.RenameColumns(DistrictsLookup, {{"id", "district_id_lookup"}}),

    // ============================================================
    // 1. SITES (potential_site) - Link via bazaar_id
    // ============================================================
    SitesSource = #"public potential_site",
    SitesFiltered = Table.SelectRows(SitesSource, each [delete_status] = "NO"),
    SitesBase = Table.SelectColumns(SitesFiltered, {
        "id", "project_name", "bazaar_id", "site_type", "status"
    }),
    
    // Join to Bazaars for location
    SitesWithBazaar = Table.NestedJoin(SitesBase, {"bazaar_id"}, BazaarsRenamed, {"bazaar_id_lookup"}, "BazaarTable", JoinKind.LeftOuter),
    SitesExpanded = Table.ExpandTableColumn(SitesWithBazaar, "BazaarTable", 
        {"bazaar_name", "upazilla_id", "district_id", "zone_id", "zone_name"}, 
        {"BazaarName", "UpazillaID", "DistrictID", "ZoneID", "ZoneName"}),
    
    // Join to Upazilla for upazilla_name
    SitesWithUpazilla = Table.NestedJoin(SitesExpanded, {"UpazillaID"}, UpazillaRenamed, {"upazilla_id_lookup"}, "UpazillaTable", JoinKind.LeftOuter),
    SitesExpandedUpazilla = Table.ExpandTableColumn(SitesWithUpazilla, "UpazillaTable", 
        {"upazilla_name"}, {"UpazillaName"}),
    
    // Join to Districts for district_name
    SitesWithDistrict = Table.NestedJoin(SitesExpandedUpazilla, {"DistrictID"}, DistrictsRenamed, {"district_id_lookup"}, "DistrictTable", JoinKind.LeftOuter),
    SitesExpandedDistrict = Table.ExpandTableColumn(SitesWithDistrict, "DistrictTable", 
        {"district_name"}, {"DistrictName"}),
    
    SitesFinal = Table.AddColumn(SitesExpandedDistrict, "ClientType", each "Site", type text),
    SitesFinal2 = Table.AddColumn(SitesFinal, "ResponsibleRole", each "BDO", type text),  // BDO manages Sites/Potential Sites
    SitesRenamed = Table.RenameColumns(SitesFinal2, {
        {"id", "ClientID"}, {"project_name", "ClientName"}, {"site_type", "SubType"}
    }),
    SitesClean = Table.SelectColumns(SitesRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole",
        "BazaarName", "UpazillaID", "UpazillaName", "DistrictID", "DistrictName", "ZoneID", "ZoneName"
    }),

    // ============================================================
    // 2. RETAILERS - Link via bazaar_id
    // Schema: is_deleted = "NO" (text, not boolean!)
    // ============================================================
    RetailersSource = #"public retailers",
    RetailersFiltered = Table.SelectRows(RetailersSource, each [is_deleted] = "NO"),
    RetailersBase = Table.SelectColumns(RetailersFiltered, {
        "id", "name", "shop_name", "bazaar_id", "dealer_id"
    }),
    
    // Join to Bazaars for location
    RetailersWithBazaar = Table.NestedJoin(RetailersBase, {"bazaar_id"}, BazaarsRenamed, {"bazaar_id_lookup"}, "BazaarTable", JoinKind.LeftOuter),
    RetailersExpanded = Table.ExpandTableColumn(RetailersWithBazaar, "BazaarTable", 
        {"bazaar_name", "upazilla_id", "district_id", "zone_id", "zone_name"}, 
        {"BazaarName", "UpazillaID", "DistrictID", "ZoneID", "ZoneName"}),
    
    // Join to Upazilla
    RetailersWithUpazilla = Table.NestedJoin(RetailersExpanded, {"UpazillaID"}, UpazillaRenamed, {"upazilla_id_lookup"}, "UpazillaTable", JoinKind.LeftOuter),
    RetailersExpandedUpazilla = Table.ExpandTableColumn(RetailersWithUpazilla, "UpazillaTable", 
        {"upazilla_name"}, {"UpazillaName"}),
    
    // Join to Districts
    RetailersWithDistrict = Table.NestedJoin(RetailersExpandedUpazilla, {"DistrictID"}, DistrictsRenamed, {"district_id_lookup"}, "DistrictTable", JoinKind.LeftOuter),
    RetailersExpandedDistrict = Table.ExpandTableColumn(RetailersWithDistrict, "DistrictTable", 
        {"district_name"}, {"DistrictName"}),
    
    RetailersFinal = Table.AddColumn(RetailersExpandedDistrict, "ClientType", each "Retailer", type text),
    RetailersFinal2 = Table.AddColumn(RetailersFinal, "SubType", each null, type text),
    RetailersFinal3 = Table.AddColumn(RetailersFinal2, "ResponsibleRole", each "SR", type text),  // SR manages Retailers
    RetailersRenamed = Table.RenameColumns(RetailersFinal3, {{"id", "ClientID"}, {"name", "ClientName"}}),
    RetailersClean = Table.SelectColumns(RetailersRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole",
        "BazaarName", "UpazillaID", "UpazillaName", "DistrictID", "DistrictName", "ZoneID", "ZoneName"
    }),

    // ============================================================
    // 3. IHB (ihb_registration) - Link via bazaar_id
    // ============================================================
    IHBSource = #"public ihb_registration",
    IHBBase = Table.SelectColumns(IHBSource, {"id", "bazaar_id", "end_user"}),
    
    // Join to Bazaars for location
    IHBWithBazaar = Table.NestedJoin(IHBBase, {"bazaar_id"}, BazaarsRenamed, {"bazaar_id_lookup"}, "BazaarTable", JoinKind.LeftOuter),
    IHBExpanded = Table.ExpandTableColumn(IHBWithBazaar, "BazaarTable", 
        {"bazaar_name", "upazilla_id", "district_id", "zone_id", "zone_name"}, 
        {"BazaarName", "UpazillaID", "DistrictID", "ZoneID", "ZoneName"}),
    
    // Join to Upazilla
    IHBWithUpazilla = Table.NestedJoin(IHBExpanded, {"UpazillaID"}, UpazillaRenamed, {"upazilla_id_lookup"}, "UpazillaTable", JoinKind.LeftOuter),
    IHBExpandedUpazilla = Table.ExpandTableColumn(IHBWithUpazilla, "UpazillaTable", 
        {"upazilla_name"}, {"UpazillaName"}),
    
    // Join to Districts
    IHBWithDistrict = Table.NestedJoin(IHBExpandedUpazilla, {"DistrictID"}, DistrictsRenamed, {"district_id_lookup"}, "DistrictTable", JoinKind.LeftOuter),
    IHBExpandedDistrict = Table.ExpandTableColumn(IHBWithDistrict, "DistrictTable", 
        {"district_name"}, {"DistrictName"}),
    
    IHBFinal = Table.AddColumn(IHBExpandedDistrict, "ClientType", each "IHB", type text),
    IHBFinal2 = Table.AddColumn(IHBFinal, "ClientName", each "IHB-" & Text.From([id]), type text),
    IHBFinal3 = Table.AddColumn(IHBFinal2, "SubType", each [end_user], type text),
    IHBFinal4 = Table.AddColumn(IHBFinal3, "ResponsibleRole", each "CRO,BDO", type text),  // Both CRO & BDO can register IHB
    IHBRenamed = Table.RenameColumns(IHBFinal4, {{"id", "ClientID"}}),
    IHBClean = Table.SelectColumns(IHBRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole",
        "BazaarName", "UpazillaID", "UpazillaName", "DistrictID", "DistrictName", "ZoneID", "ZoneName"
    }),

    // ============================================================
    // 4. DEALERS - Text-only district (no ID linkage)
    // Schema: is_deleted = "NO" (text), NOT delete_status!
    // ============================================================
    DealersSource = #"public dealers",
    DealersFiltered = Table.SelectRows(DealersSource, each [is_deleted] = "NO"),
    DealersBase = Table.SelectColumns(DealersFiltered, {
        "id", "name", "shop_name", "district_name_text", "upazilla_names_text"
    }),
    
    // Dealers have text-only location, no bazaar_id
    DealersFinal = Table.AddColumn(DealersBase, "ClientType", each "Dealer", type text),
    DealersFinal2 = Table.AddColumn(DealersFinal, "SubType", each null, type text),
    DealersFinal3 = Table.AddColumn(DealersFinal2, "ResponsibleRole", each "CRO", type text),  // CRO manages Partners/Dealers
    DealersFinal4 = Table.AddColumn(DealersFinal3, "BazaarName", each null, type text),
    DealersFinal5 = Table.AddColumn(DealersFinal4, "UpazillaID", each null, Int64.Type),
    DealersFinal6 = Table.AddColumn(DealersFinal5, "ZoneID", each null, Int64.Type),
    DealersFinal7 = Table.AddColumn(DealersFinal6, "ZoneName", each null, type text),
    DealersFinal8 = Table.AddColumn(DealersFinal7, "DistrictID", each null, Int64.Type),
    DealersRenamed = Table.RenameColumns(DealersFinal8, {
        {"id", "ClientID"}, {"name", "ClientName"}, 
        {"district_name_text", "DistrictName"}, {"upazilla_names_text", "UpazillaName"}
    }),
    DealersClean = Table.SelectColumns(DealersRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole",
        "BazaarName", "UpazillaID", "UpazillaName", "DistrictID", "DistrictName", "ZoneID", "ZoneName"
    }),

    // ============================================================
    // 5. ENGINEERS - Managed by BDO (per PRD Section 4.5)
    // PRD: BDO → Engineer Registration, Potential Sites, Engineer Update
    // ============================================================
    EngineersSource = #"public engineers",
    EngineersBase = Table.SelectColumns(EngineersSource, {"id", "engineer_type", "consultancy_firm"}),
    
    // Engineers have no location - derive from visit location
    EngineersFinal = Table.AddColumn(EngineersBase, "ClientType", each "Engineer", type text),
    EngineersFinal2 = Table.AddColumn(EngineersFinal, "ClientName", each 
        if [consultancy_firm] <> null then [consultancy_firm] else "Engineer-" & Text.From([id]), type text),
    EngineersFinal3 = Table.AddColumn(EngineersFinal2, "SubType", each 
        if [engineer_type] <> null then [engineer_type] else "General", type text),
    EngineersFinal4 = Table.AddColumn(EngineersFinal3, "ResponsibleRole", each "BDO", type text),
    EngineersFinal5 = Table.AddColumn(EngineersFinal4, "BazaarName", each null, type text),
    EngineersFinal6 = Table.AddColumn(EngineersFinal5, "UpazillaID", each null, Int64.Type),
    EngineersFinal7 = Table.AddColumn(EngineersFinal6, "UpazillaName", each null, type text),
    EngineersFinal8 = Table.AddColumn(EngineersFinal7, "DistrictID", each null, Int64.Type),
    EngineersFinal9 = Table.AddColumn(EngineersFinal8, "DistrictName", each null, type text),
    EngineersFinal10 = Table.AddColumn(EngineersFinal9, "ZoneID", each null, Int64.Type),
    EngineersFinal11 = Table.AddColumn(EngineersFinal10, "ZoneName", each null, type text),
    EngineersRenamed = Table.RenameColumns(EngineersFinal11, {{"id", "ClientID"}}),
    EngineersClean = Table.SelectColumns(EngineersRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole",
        "BazaarName", "UpazillaID", "UpazillaName", "DistrictID", "DistrictName", "ZoneID", "ZoneName"
    }),

    // ============================================================
    // 6. CONTRACTORS/PARTNERS - Managed by CRO (per PRD Section 4.4)
    // PRD: CRO → Partner Registration, Update Partner Form
    // ============================================================
    ContractorSource = #"public contractor",
    ContractorBase = Table.SelectColumns(ContractorSource, {"id", "assignedsr"}),
    
    // Contractors/Partners have no location - derive from visit location
    ContractorFinal = Table.AddColumn(ContractorBase, "ClientType", each "Contractor", type text),
    ContractorFinal2 = Table.AddColumn(ContractorFinal, "ClientName", each "Partner-" & Text.From([id]), type text),
    ContractorFinal3 = Table.AddColumn(ContractorFinal2, "SubType", each "Partner", type text),
    ContractorFinal4 = Table.AddColumn(ContractorFinal3, "ResponsibleRole", each "CRO", type text),
    ContractorFinal5 = Table.AddColumn(ContractorFinal4, "BazaarName", each null, type text),
    ContractorFinal6 = Table.AddColumn(ContractorFinal5, "UpazillaID", each null, Int64.Type),
    ContractorFinal7 = Table.AddColumn(ContractorFinal6, "UpazillaName", each null, type text),
    ContractorFinal8 = Table.AddColumn(ContractorFinal7, "DistrictID", each null, Int64.Type),
    ContractorFinal9 = Table.AddColumn(ContractorFinal8, "DistrictName", each null, type text),
    ContractorFinal10 = Table.AddColumn(ContractorFinal9, "ZoneID", each null, Int64.Type),
    ContractorFinal11 = Table.AddColumn(ContractorFinal10, "ZoneName", each null, type text),
    ContractorRenamed = Table.RenameColumns(ContractorFinal11, {{"id", "ClientID"}}),
    ContractorClean = Table.SelectColumns(ContractorRenamed, {
        "ClientID", "ClientName", "ClientType", "SubType", "ResponsibleRole",
        "BazaarName", "UpazillaID", "UpazillaName", "DistrictID", "DistrictName", "ZoneID", "ZoneName"
    }),

    // ============================================================
    // COMBINE ALL CLIENT TYPES (6 Types per PRD)
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
    
    // Add Client Category for reporting hierarchy (per PRD)
    WithCategory = Table.AddColumn(WithCompositeKey, "ClientCategory", each 
        if [ClientType] = "Site" then "Prospect"
        else if [ClientType] = "Dealer" or [ClientType] = "Retailer" then "Channel Partner"
        else if [ClientType] = "Engineer" then "Influencer-Technical"
        else if [ClientType] = "Contractor" then "Influencer-Partner"
        else if [ClientType] = "IHB" then "End Customer"
        else "Other",
        type text
    ),
    
    // Add Responsible Role for RLS (BDO manages Engineers, CRO manages Partners)
    WithResponsibleRole = Table.AddColumn(WithCategory, "ResponsibleRoleRLS", each 
        if [ClientType] = "Site" then "BDO"
        else if [ClientType] = "Engineer" then "BDO"
        else if [ClientType] = "Contractor" then "CRO"
        else if [ClientType] = "Retailer" then "SR"
        else if [ClientType] = "Dealer" then "CRO"
        else if [ClientType] = "IHB" then "CRO,BDO"  // Both can register IHB
        else "All",
        type text
    ),
    
    // Add flag for location availability (for RLS)
    WithLocationFlag = Table.AddColumn(WithResponsibleRole, "HasLocationData", each 
        [UpazillaID] <> null or [BazaarName] <> null, type logical),
    
    // Reorder Columns
    ReorderedColumns = Table.ReorderColumns(WithLocationFlag, {
        "ClientKey", "ClientID", "ClientName", "ClientType", "SubType", "ClientCategory",
        "ResponsibleRoleRLS", "BazaarName", "UpazillaID", "UpazillaName", "DistrictID", "DistrictName", 
        "ZoneID", "ZoneName", "HasLocationData"
    }),
    
    // Set Data Types
    TypedTable = Table.TransformColumnTypes(ReorderedColumns, {
        {"ClientKey", type text},
        {"ClientID", Int64.Type},
        {"ClientName", type text},
        {"ClientType", type text},
        {"SubType", type text},
        {"ClientCategory", type text},
        {"ResponsibleRoleRLS", type text},
        {"BazaarName", type text},
        {"UpazillaID", Int64.Type},
        {"UpazillaName", type text},
        {"DistrictID", Int64.Type},
        {"DistrictName", type text},
        {"ZoneID", Int64.Type},
        {"ZoneName", type text},
        {"HasLocationData", type logical}
    })
in
    TypedTable
