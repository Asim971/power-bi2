// ============================================================
// Dim_Territory - Geographic Hierarchy Dimension
// Based on actual 'public areas' table schema from Power BI
// Zone → Region → Area hierarchy for Bangladesh
// ============================================================

let
    // Reference the existing 'public areas' table in Power BI
    Source = #"public areas",
    
    // ---- Select Core Columns from actual schema ----
    SelectedColumns = Table.SelectColumns(Source, {
        "id", "name", "zone_id", "zone_name", "region_id", "region_name",
        "nation_id", "nation_name", "organization_id",
        "assigned_zsm", "assigned_gm", "assigned_agm", "assigned_asm",
        "delete_status"
    }),
    
    // ---- Filter Active Areas ----
    ActiveAreas = Table.SelectRows(SelectedColumns, each [delete_status] = "NO"),
    
    // ---- Rename Columns ----
    RenamedColumns = Table.RenameColumns(ActiveAreas, {
        {"id", "AreaID"},
        {"name", "AreaName"},
        {"zone_id", "ZoneID"},
        {"zone_name", "ZoneName"},
        {"region_id", "RegionID"},
        {"region_name", "RegionName"},
        {"nation_id", "NationID"},
        {"nation_name", "NationName"},
        {"organization_id", "OrganizationID"},
        {"assigned_zsm", "AssignedZSM"},
        {"assigned_gm", "AssignedGM"},
        {"assigned_agm", "AssignedAGM"},
        {"assigned_asm", "AssignedASM"}
    }),
    
    // ---- Create Territory Key ----
    WithTerritoryKey = Table.AddColumn(RenamedColumns, "TerritoryKey", each 
        Text.From([ZoneID]) & "-" & Text.From([RegionID]) & "-" & Text.From([AreaID]),
        type text
    ),
    
    // ---- Create Full Path for Hierarchy ----
    WithFullPath = Table.AddColumn(WithTerritoryKey, "TerritoryPath", each 
        (if [ZoneName] <> null then [ZoneName] else "Unknown") & " > " & 
        (if [RegionName] <> null then [RegionName] else "Unknown") & " > " & 
        (if [AreaName] <> null then [AreaName] else "Unknown"),
        type text
    ),
    
    // ---- Add Zone Sort Order (for consistent display) ----
    WithZoneSort = Table.AddColumn(WithFullPath, "ZoneSortOrder", each 
        if [ZoneID] <> null then [ZoneID] else 999,
        Int64.Type
    ),
    
    // ---- Set Data Types ----
    TypedTable = Table.TransformColumnTypes(WithZoneSort, {
        {"TerritoryKey", type text},
        {"AreaID", Int64.Type},
        {"AreaName", type text},
        {"ZoneID", Int64.Type},
        {"ZoneName", type text},
        {"RegionID", Int64.Type},
        {"RegionName", type text},
        {"NationID", Int64.Type},
        {"NationName", type text},
        {"OrganizationID", Int64.Type},
        {"AssignedZSM", type text},
        {"AssignedGM", type text},
        {"AssignedAGM", type text},
        {"AssignedASM", type text},
        {"TerritoryPath", type text},
        {"ZoneSortOrder", Int64.Type}
    }),
    
    // ---- Reorder Columns ----
    ReorderedColumns = Table.ReorderColumns(TypedTable, {
        "TerritoryKey", 
        "ZoneID", "ZoneName", "ZoneSortOrder",
        "RegionID", "RegionName",
        "AreaID", "AreaName",
        "NationID", "NationName", "OrganizationID",
        "TerritoryPath",
        "AssignedZSM", "AssignedGM", "AssignedAGM", "AssignedASM"
    })
in
    ReorderedColumns
