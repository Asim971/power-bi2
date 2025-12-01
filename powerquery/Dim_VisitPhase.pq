// ============================================================
// Dim_VisitPhase - Visit Phase Dimension
// Source: public visit_phases (2 records)
// 
// PURPOSE:
// Visit phases define the high-level stage of a visit
// Links to visit_stages for detailed stage tracking
//
// ACTUAL COLUMNS: id, name, description, delete_status, created_at, updated_at
// ============================================================

let
    // Reference the existing 'public visit_phases' table in Power BI
    Source = #"public visit_phases",
    
    // ---- Filter Active Phases ----
    ActivePhases = Table.SelectRows(Source, each [delete_status] = "NO" or [delete_status] = null),
    
    // ---- Select Columns ----
    SelectedColumns = Table.SelectColumns(ActivePhases, {"id", "name", "description"}),
    
    // ---- Rename Columns ----
    RenamedColumns = Table.RenameColumns(SelectedColumns, {
        {"id", "VisitPhaseID"},
        {"name", "PhaseName"},
        {"description", "PhaseDescription"}
    }),
    
    // ---- Add Sort Order ----
    WithSortOrder = Table.AddColumn(RenamedColumns, "PhaseSortOrder", each [VisitPhaseID], Int64.Type),
    
    // ---- Set Data Types ----
    TypedTable = Table.TransformColumnTypes(WithSortOrder, {
        {"VisitPhaseID", Int64.Type},
        {"PhaseName", type text},
        {"PhaseDescription", type text},
        {"PhaseSortOrder", Int64.Type}
    })
in
    TypedTable
