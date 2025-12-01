// ============================================================
// Dim_VisitStage - Visit Stage Dimension
// Source: public visit_stages (78 records)
// 
// PURPOSE:
// Detailed stages within each visit phase
// Links to Dim_VisitPhase for hierarchical stage analysis
// Supports visit workflow tracking and progression analysis
//
// ACTUAL COLUMNS: id, name, description, visit_phase_id, parent_id, 
//                 delete_status, created_at, updated_at
// ============================================================

let
    // Reference the existing 'public visit_stages' table in Power BI
    Source = #"public visit_stages",
    
    // ---- Filter Active Stages ----
    ActiveStages = Table.SelectRows(Source, each [delete_status] = "NO" or [delete_status] = null),
    
    // ---- Select Columns ----
    SelectedColumns = Table.SelectColumns(ActiveStages, {"id", "name", "description", "visit_phase_id", "parent_id"}),
    
    // ---- Rename Columns ----
    RenamedColumns = Table.RenameColumns(SelectedColumns, {
        {"id", "VisitStageID"},
        {"name", "StageName"},
        {"description", "StageDescription"},
        {"visit_phase_id", "VisitPhaseID"},
        {"parent_id", "ParentStageID"}
    }),
    
    // ---- Add Sort Order ----
    WithSortOrder = Table.AddColumn(RenamedColumns, "StageSortOrder", each [VisitStageID], Int64.Type),
    
    // ---- Stage Category Grouping (based on construction stage patterns) ----
    WithStageCategory = Table.AddColumn(WithSortOrder, "StageCategory", each 
        let stageLower = Text.Lower([StageName])
        in
            if Text.Contains(stageLower, "formwork") then "Formwork"
            else if Text.Contains(stageLower, "reinforcement") then "Reinforcement"
            else if Text.Contains(stageLower, "concreting") or Text.Contains(stageLower, "casting") then "Concreting"
            else if Text.Contains(stageLower, "curing") then "Curing"
            else if Text.Contains(stageLower, "brick") or Text.Contains(stageLower, "masonry") then "Masonry"
            else if Text.Contains(stageLower, "plaster") then "Plastering"
            else if Text.Contains(stageLower, "finish") then "Finishing"
            else "General",
        type text
    ),
    
    // ---- Is Sub-Stage Flag (has parent) ----
    WithSubStageFlag = Table.AddColumn(WithStageCategory, "IsSubStage", each 
        if [ParentStageID] <> null then 1 else 0,
        Int64.Type
    ),
    
    // ---- Set Data Types ----
    TypedTable = Table.TransformColumnTypes(WithSubStageFlag, {
        {"VisitStageID", Int64.Type},
        {"StageName", type text},
        {"StageDescription", type text},
        {"VisitPhaseID", Int64.Type},
        {"ParentStageID", Int64.Type},
        {"StageSortOrder", Int64.Type},
        {"StageCategory", type text},
        {"IsSubStage", Int64.Type}
    })
in
    TypedTable
