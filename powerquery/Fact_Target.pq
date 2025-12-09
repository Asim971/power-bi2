let
    // Get date range from Fact_Visit
    MinDate = List.Min(Fact_Visit[DateKey]),
    MaxDate = List.Max(Fact_Visit[DateKey]),
    
    // Generate date list
    DateList = List.Dates(MinDate, Duration.Days(MaxDate - MinDate) + 1, #duration(1, 0, 0, 0)),
    
    // Get distinct UserIDs
    UserList = List.Distinct(Dim_User[UserID]),
    
    // Entity groups with their targets
    EntityTargets = Table.FromRecords({
        [EntityGroup = "Customers", DailyTarget = 10],
        [EntityGroup = "Consumers", DailyTarget = 5],
        [EntityGroup = "Influencers", DailyTarget = 10]
    }),
    
    // Create date table
    DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"DateKey"}, null, ExtraValues.Error),
    DateTableTyped = Table.TransformColumnTypes(DateTable, {{"DateKey", type date}}),
    
    // Create user table
    UserTable = Table.FromList(UserList, Splitter.SplitByNothing(), {"UserID"}, null, ExtraValues.Error),
    UserTableTyped = Table.TransformColumnTypes(UserTable, {{"UserID", Int64.Type}}),
    
    // Cross join all three
    DateUser = Table.AddColumn(DateTableTyped, "UserData", each UserTableTyped),
    DateUserExpanded = Table.ExpandTableColumn(DateUser, "UserData", {"UserID"}, {"UserID"}),
    
    DateUserEntity = Table.AddColumn(DateUserExpanded, "EntityData", each EntityTargets),
    Result = Table.ExpandTableColumn(DateUserEntity, "EntityData", {"EntityGroup", "DailyTarget"}, {"EntityGroup", "DailyTarget"}),
    
    // Set column types
    FinalTable = Table.TransformColumnTypes(Result, {
        {"DateKey", type date},
        {"UserID", Int64.Type},
        {"EntityGroup", type text},
        {"DailyTarget", Int64.Type}
    })
in
    FinalTable
