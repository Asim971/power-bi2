// ============================================================
// Dim_Date - Date Dimension
// Standard date dimension with fiscal periods for Bangladesh
// Supports time intelligence measures
// Updated: Nov 2025 - Extended date range
// ============================================================

let
    // Configuration
    StartDate = #date(2023, 1, 1),
    EndDate = #date(2026, 12, 31),  // Extended to cover future planning
    FiscalYearStartMonth = 7,  // Bangladesh fiscal year starts July 1
    
    // Generate date list
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    DateList = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    
    // Convert to table
    TableFromList = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}, null, ExtraValues.Error),
    ChangedType = Table.TransformColumnTypes(TableFromList, {{"Date", type date}}),
    
    // ---- Core Date Attributes ----
    AddDateKey = Table.AddColumn(ChangedType, "DateKey", each Date.ToText([Date], "yyyyMMdd"), type text),
    AddYear = Table.AddColumn(AddDateKey, "Year", each Date.Year([Date]), Int64.Type),
    AddMonth = Table.AddColumn(AddYear, "Month", each Date.Month([Date]), Int64.Type),
    AddMonthName = Table.AddColumn(AddMonth, "MonthName", each Date.MonthName([Date]), type text),
    AddMonthShort = Table.AddColumn(AddMonthName, "MonthShort", each Text.Start(Date.MonthName([Date]), 3), type text),
    AddQuarter = Table.AddColumn(AddMonthShort, "Quarter", each Date.QuarterOfYear([Date]), Int64.Type),
    AddQuarterName = Table.AddColumn(AddQuarter, "QuarterName", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    AddDay = Table.AddColumn(AddQuarterName, "Day", each Date.Day([Date]), Int64.Type),
    AddDayOfWeek = Table.AddColumn(AddDay, "DayOfWeek", each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),
    AddDayName = Table.AddColumn(AddDayOfWeek, "DayName", each Date.DayOfWeekName([Date]), type text),
    AddDayShort = Table.AddColumn(AddDayName, "DayShort", each Text.Start(Date.DayOfWeekName([Date]), 3), type text),
    AddWeekOfYear = Table.AddColumn(AddDayShort, "WeekOfYear", each Date.WeekOfYear([Date]), Int64.Type),
    AddDayOfYear = Table.AddColumn(AddWeekOfYear, "DayOfYear", each Date.DayOfYear([Date]), Int64.Type),
    
    // ---- Fiscal Year Attributes (July-June for Bangladesh) ----
    AddFiscalYear = Table.AddColumn(AddDayOfYear, "FiscalYear", each 
        if Date.Month([Date]) >= FiscalYearStartMonth then Date.Year([Date]) + 1 else Date.Year([Date]), 
        Int64.Type),
    AddFiscalYearLabel = Table.AddColumn(AddFiscalYear, "FiscalYearLabel", each 
        "FY" & Text.From([FiscalYear] - 1) & "-" & Text.End(Text.From([FiscalYear]), 2), 
        type text),
    AddFiscalMonth = Table.AddColumn(AddFiscalYearLabel, "FiscalMonth", each 
        if Date.Month([Date]) >= FiscalYearStartMonth then Date.Month([Date]) - FiscalYearStartMonth + 1 
        else Date.Month([Date]) + (12 - FiscalYearStartMonth + 1), 
        Int64.Type),
    AddFiscalQuarter = Table.AddColumn(AddFiscalMonth, "FiscalQuarter", each 
        Number.RoundUp([FiscalMonth] / 3, 0), 
        Int64.Type),
    AddFiscalQuarterLabel = Table.AddColumn(AddFiscalQuarter, "FiscalQuarterLabel", each 
        "FQ" & Text.From([FiscalQuarter]), 
        type text),
    
    // ---- Week Attributes ----
    AddWeekStartDate = Table.AddColumn(AddFiscalQuarterLabel, "WeekStartDate", each 
        Date.StartOfWeek([Date], Day.Saturday),  // Bangladesh week starts Saturday
        type date),
    AddWeekEndDate = Table.AddColumn(AddWeekStartDate, "WeekEndDate", each 
        Date.EndOfWeek([Date], Day.Saturday), 
        type date),
    AddWeekLabel = Table.AddColumn(AddWeekEndDate, "WeekLabel", each 
        "W" & Text.PadStart(Text.From([WeekOfYear]), 2, "0") & "-" & Text.From([Year]), 
        type text),
    
    // ---- Month Attributes ----
    AddMonthStartDate = Table.AddColumn(AddWeekLabel, "MonthStartDate", each 
        Date.StartOfMonth([Date]), 
        type date),
    AddMonthEndDate = Table.AddColumn(AddMonthStartDate, "MonthEndDate", each 
        Date.EndOfMonth([Date]), 
        type date),
    AddYearMonth = Table.AddColumn(AddMonthEndDate, "YearMonth", each 
        Text.From([Year]) & "-" & Text.PadStart(Text.From([Month]), 2, "0"), 
        type text),
    AddYearMonthNum = Table.AddColumn(AddYearMonth, "YearMonthNum", each 
        [Year] * 100 + [Month], 
        Int64.Type),
    
    // ---- Relative Date Flags ----
    AddIsToday = Table.AddColumn(AddYearMonthNum, "IsToday", each 
        if [Date] = Date.From(DateTime.LocalNow()) then 1 else 0, 
        Int64.Type),
    AddIsCurrentWeek = Table.AddColumn(AddIsToday, "IsCurrentWeek", each 
        if Date.IsInCurrentWeek([Date]) then 1 else 0, 
        Int64.Type),
    AddIsCurrentMonth = Table.AddColumn(AddIsCurrentWeek, "IsCurrentMonth", each 
        if Date.IsInCurrentMonth([Date]) then 1 else 0, 
        Int64.Type),
    AddIsCurrentQuarter = Table.AddColumn(AddIsCurrentMonth, "IsCurrentQuarter", each 
        if Date.IsInCurrentQuarter([Date]) then 1 else 0, 
        Int64.Type),
    AddIsCurrentYear = Table.AddColumn(AddIsCurrentQuarter, "IsCurrentYear", each 
        if Date.IsInCurrentYear([Date]) then 1 else 0, 
        Int64.Type),
    AddIsPreviousMonth = Table.AddColumn(AddIsCurrentYear, "IsPreviousMonth", each 
        if Date.IsInPreviousMonth([Date]) then 1 else 0, 
        Int64.Type),
    
    // ---- Weekend/Weekday Flags ----
    // Bangladesh: Friday is weekend, Saturday is half-day
    AddIsWeekend = Table.AddColumn(AddIsPreviousMonth, "IsWeekend", each 
        if Date.DayOfWeek([Date], Day.Monday) = 4 then 1  // Friday
        else 0, 
        Int64.Type),
    AddIsWeekday = Table.AddColumn(AddIsWeekend, "IsWeekday", each 
        if [IsWeekend] = 0 then 1 else 0, 
        Int64.Type),
    
    // ---- Bangladesh Public Holidays (Major ones) ----
    AddIsHoliday = Table.AddColumn(AddIsWeekday, "IsHoliday", each 
        if Date.Month([Date]) = 2 and Date.Day([Date]) = 21 then 1  // Language Movement Day
        else if Date.Month([Date]) = 3 and Date.Day([Date]) = 26 then 1  // Independence Day
        else if Date.Month([Date]) = 4 and Date.Day([Date]) = 14 then 1  // Bengali New Year
        else if Date.Month([Date]) = 5 and Date.Day([Date]) = 1 then 1  // May Day
        else if Date.Month([Date]) = 8 and Date.Day([Date]) = 15 then 1  // National Mourning Day
        else if Date.Month([Date]) = 12 and Date.Day([Date]) = 16 then 1  // Victory Day
        else 0, 
        Int64.Type),
    AddHolidayName = Table.AddColumn(AddIsHoliday, "HolidayName", each 
        if Date.Month([Date]) = 2 and Date.Day([Date]) = 21 then "Language Movement Day"
        else if Date.Month([Date]) = 3 and Date.Day([Date]) = 26 then "Independence Day"
        else if Date.Month([Date]) = 4 and Date.Day([Date]) = 14 then "Bengali New Year"
        else if Date.Month([Date]) = 5 and Date.Day([Date]) = 1 then "May Day"
        else if Date.Month([Date]) = 8 and Date.Day([Date]) = 15 then "National Mourning Day"
        else if Date.Month([Date]) = 12 and Date.Day([Date]) = 16 then "Victory Day"
        else null, 
        type text),
    
    // ---- Sort Order Column for Month ----
    AddMonthSortOrder = Table.AddColumn(AddHolidayName, "MonthSortOrder", each 
        [Year] * 100 + [Month], 
        Int64.Type),
    
    // ---- Reorder Columns ----
    ReorderedColumns = Table.ReorderColumns(AddMonthSortOrder, {
        "DateKey", "Date", 
        "Year", "Quarter", "QuarterName", "Month", "MonthName", "MonthShort", 
        "Day", "DayOfWeek", "DayName", "DayShort", "DayOfYear", "WeekOfYear",
        "FiscalYear", "FiscalYearLabel", "FiscalQuarter", "FiscalQuarterLabel", "FiscalMonth",
        "WeekStartDate", "WeekEndDate", "WeekLabel",
        "MonthStartDate", "MonthEndDate", "YearMonth", "YearMonthNum", "MonthSortOrder",
        "IsToday", "IsCurrentWeek", "IsCurrentMonth", "IsCurrentQuarter", "IsCurrentYear", "IsPreviousMonth",
        "IsWeekend", "IsWeekday", "IsHoliday", "HolidayName"
    })
in
    ReorderedColumns
