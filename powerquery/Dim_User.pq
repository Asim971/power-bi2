// ============================================================
// Dim_User - Employee Dimension
// Based on actual 'public users' table schema
// Includes Role lookup only (no territory joins to avoid duplicates)
// Two tracks: ORG (SR/ASM/ZSM) and BMD (BDO/CRO)
// 
// SCHEMA NOTES (Nov 2025):
// - users.id is the PRIMARY KEY (unique)
// - users.delete_status = "NO" (text)
// - role table has: id, name, level, department, designation
// - Territory info comes from users table directly (zone_id, region_id, area_id)
// ============================================================

let
    // Reference the existing tables
    UsersSource = #"public users",
    RolesSource = #"public role",
    
    // ---- Select Core Columns from users ----
    SelectedColumns = Table.SelectColumns(UsersSource, {
        "id", "name", "email", "phone_number", "role_id", 
        "zone_id", "region_id", "area_id", "bd_territory_id",
        "user_designation", "line_manager",
        "delete_status", "created_at", "updated_at"
    }),
    
    // ---- Filter Active Users ----
    ActiveUsers = Table.SelectRows(SelectedColumns, each [delete_status] = "NO"),
    
    // ---- Join with Role table to get role details (1:1 relationship) ----
    WithRoleJoin = Table.NestedJoin(
        ActiveUsers, {"role_id"},
        RolesSource, {"id"},
        "RoleData", JoinKind.LeftOuter
    ),
    
    WithRoleExpanded = Table.ExpandTableColumn(
        WithRoleJoin, "RoleData",
        {"name", "level", "department", "designation"},
        {"RoleName", "RoleLevel", "Department", "RoleDesignation"}
    ),
    
    // ---- Rename Core Columns ----
    RenamedColumns = Table.RenameColumns(WithRoleExpanded, {
        {"id", "UserID"},
        {"name", "EmployeeName"},
        {"email", "EmployeeEmail"},
        {"phone_number", "EmployeePhone"},
        {"role_id", "RoleID"},
        {"zone_id", "ZoneID"},
        {"region_id", "RegionID"},
        {"area_id", "AreaID"},
        {"bd_territory_id", "BDTerritoryID"},
        {"user_designation", "Designation"},
        {"line_manager", "LineManager"}
    }),
    
    // ---- Add EmployeeID alias for Fact_Visit compatibility ----
    WithEmployeeID = Table.AddColumn(RenamedColumns, "EmployeeID", each [UserID], Int64.Type),
    
    // ---- Add Department Track ----
    WithTrack = Table.AddColumn(WithEmployeeID, "DepartmentTrack", each 
        if [Department] = "BMD" then "Business Development"
        else if [Department] = "ORG" then "Sales Organization"
        else "Other",
        type text
    ),
    
    // ---- Add Role Category based on PRD ----
    WithRoleCategory = Table.AddColumn(WithTrack, "RoleCategory", each 
        if [RoleName] = "SR" then "Field Sales"
        else if [RoleName] = "ASM" then "Area Management"
        else if [RoleName] = "ZSM" then "Zonal Management"
        else if [RoleName] = "BDO" then "Business Development"
        else if [RoleName] = "CRO" then "Customer Relations"
        else if [RoleName] = "AGM" or [RoleName] = "GM / DGM" then "Executive"
        else if Text.Contains([RoleName] ?? "", "ADMIN") then "Admin"
        else "Other",
        type text
    ),
    
    // ---- Add Is Field Role Flag ----
    WithFieldFlag = Table.AddColumn(WithRoleCategory, "IsFieldRole", each 
        if [RoleName] = "SR" or [RoleName] = "BDO" or [RoleName] = "CRO" then 1 else 0,
        Int64.Type
    ),
    
    // ---- Add Management Level ----
    WithMgmtLevel = Table.AddColumn(WithFieldFlag, "ManagementLevel", each 
        if [RoleLevel] >= 2040 and [RoleLevel] <= 2060 then "Field"
        else if [RoleLevel] >= 2020 and [RoleLevel] < 2040 then "Middle Management"
        else if [RoleLevel] >= 1030 and [RoleLevel] <= 1040 then "Field (BD)"
        else if [RoleLevel] < 1030 then "Senior Management"
        else "Other",
        type text
    ),
    
    // ---- Set Data Types ----
    TypedTable = Table.TransformColumnTypes(WithMgmtLevel, {
        {"UserID", Int64.Type},
        {"EmployeeID", Int64.Type},
        {"EmployeeName", type text},
        {"EmployeeEmail", type text},
        {"EmployeePhone", type text},
        {"RoleID", Int64.Type},
        {"ZoneID", Int64.Type},
        {"RegionID", Int64.Type},
        {"AreaID", Int64.Type},
        {"BDTerritoryID", Int64.Type},
        {"Designation", type text},
        {"LineManager", type text},
        {"RoleName", type text},
        {"RoleLevel", Int64.Type},
        {"Department", type text},
        {"RoleDesignation", type text},
        {"DepartmentTrack", type text},
        {"RoleCategory", type text},
        {"IsFieldRole", Int64.Type},
        {"ManagementLevel", type text},
        {"created_at", type datetime},
        {"updated_at", type datetime}
    }),
    
    // ---- Remove delete_status ----
    CleanedTable = Table.RemoveColumns(TypedTable, {"delete_status"})
in
    CleanedTable
