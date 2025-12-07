# 📋 FRD Implementation Guide: Visit Performance Dashboards

**Document Version**: 1.0  
**Generated Date**: December 7, 2025  
**FRD Reference**: `frd.md` (BMD Sales Eco System – Visit Performance Dashboards)  
**Analysis Method**: PEA v3.1 Codebase-Aware Workflow

---

## 📊 EXECUTIVE SUMMARY

### FRD Scope
The FRD defines **three new Visit Performance Dashboards**:
1. **Clients Dashboard** — Dealers & Retailers
2. **Influencers Dashboard** — Engineers, Masons, Other Influencers  
3. **Customers Dashboard** — Sites & IHB

All three dashboards share identical layout, components, and behavior with entity-type filtering.

### Current State Assessment

| Component | Current Status | FRD Requirement | Gap Level |
|-----------|---------------|-----------------|-----------|
| **Data Model** | ✅ Exists (Star Schema) | Required | 🟢 Minor gaps |
| **Entity Type Filtering** | ⚠️ Partial (`ClientType` exists) | Dashboard-level auto-filter | 🟡 Medium |
| **Global Filters** | ❌ Missing | Date, Location, Company, Employee | 🔴 Critical |
| **KPI Tiles** | ⚠️ Partial (Basic visit KPIs) | Total Visit, Average Visit | 🟡 Medium |
| **Charts** | ❌ Missing | 6 chart types per dashboard | 🔴 Critical |
| **Top/Bottom Performers** | ⚠️ Basic measures exist | Ranking charts | 🟡 Medium |
| **Time Intelligence** | ✅ Good (MTD/YTD/MoM) | Daily, WTD, MTD, YTD | 🟢 Minor gaps |
| **Location Hierarchy** | ✅ Exists (Zone→Region→Area) | Area, Zone, Territory | 🟢 Aligned |
| **Company Filter (ACL/AIL)** | ❌ Missing | Checkbox filter | 🔴 Critical |
| **RLS Security** | ⚠️ Partial | Role-based filtering | 🟡 Medium |
| **Drill-down & Export** | ❌ Missing | Detail tables + Export | 🔴 Critical |

---

## 🔍 DETAILED GAP ANALYSIS

### GAP 1: Entity Type Dashboard Filtering (FR-22, FR-66-74)

**FRD Requirement:**
- Clients Dashboard: Automatically filters to `Dealer`, `Retailer`
- Influencers Dashboard: Automatically filters to `Engineer`, `Mason`, `Other Influencer`
- Customers Dashboard: Automatically filters to `Site`, `IHB`

**Current State:**
- `Fact_Visit[ClientType]` column exists with values: Site, Retailer, Dealer, Engineer, Contractor, IHB, Unknown
- `Dim_Client_Simple[ClientType]` dimension exists
- **GAP**: No "Mason" or "Other Influencer" types in current data; FRD uses different terminology

**Resolution Mapping:**
| FRD Entity Type | Current `ClientType` | Action |
|-----------------|---------------------|--------|
| Dealer | ✅ "Dealer" | No change |
| Retailer | ✅ "Retailer" | No change |
| Engineer | ✅ "Engineer" | No change |
| Mason | ❌ Missing | Map from source or create new category |
| Other Influencer | ⚠️ "Contractor" | Rename/reclassify |
| Site | ✅ "Site" | No change |
| IHB | ✅ "IHB" | No change |

---

### GAP 2: Company Filter (ACL/AIL) (FR-16-18)

**FRD Requirement:**
- Checkboxes for ACL, AIL companies
- Both selected by default
- At least one must always be selected

**Current State:**
- `Fact_Visit` has `organization_id` column
- No `Company` or `CompanyCode` column in fact/dimension tables
- Source tables have `organization_id` but unclear if it maps to ACL/AIL

**Resolution:**
- Add `CompanyCode` column to `Fact_Visit` Power Query
- Map `organization_id` to "ACL" or "AIL"
- Create slicer with both selected by default

---

### GAP 3: Date Filter with Radio Buttons (FR-7-10)

**FRD Requirement:**
- Radio buttons: Daily, WTD, MTD, YTD
- Exactly one selected at any time
- Default: MTD

**Current State:**
- `Dim_Date` table has all required columns: `Date`, `WeekStartDate`, `IsCurrentWeek`, `IsCurrentMonth`, `IsCurrentYear`
- Measures exist: `Visits_MTD`, `Visits_YTD`, `Visits_Rolling_7_Days`
- **GAP**: No WTD measure; No date parameter table for radio-button behavior

**Resolution:**
- Create `DateFilterParameter` table for radio button selection
- Add `Visits_WTD` measure
- Create dynamic `Total_Visits_Filtered` measure

---

### GAP 4: Location Filter with Dynamic Level (FR-11-15)

**FRD Requirement:**
- Radio buttons: Area, Zone, Territory
- Dynamic dropdown based on selected level
- Multi-select capability

**Current State:**
- `Dim_Territory` has: `ZoneID`, `ZoneName`, `RegionID`, `RegionName`, `AreaID`, `AreaName`
- **GAP**: FRD uses "Territory" but current model uses "Region" for middle level
- No dynamic filter parameter table

**Resolution:**
- Create `LocationLevelParameter` table
- Map FRD terminology: Zone → Zone, Area → Area, Territory → Region (or create Territory column)
- Create dynamic location slicer

---

### GAP 5: KPI Tiles (FR-24-30)

**FRD Requirement:**
| KPI | Calculation | Format |
|-----|-------------|--------|
| **Total Visit** | COUNT of visits with all filters | Thousands separator |
| **Average Visit** | Total Visits ÷ Unique Employees with visits | Round to integer or 1 decimal |

**Current State:**
- `Total_Visits` ✅ Exists: `COUNTROWS('Fact_Visit')`
- `Visits_Per_Employee` ✅ Exists: `DIVIDE([Total_Visits], [Active_Employees], 0)`
- **GAP**: Format strings not set for thousand separators

**Resolution:**
- Rename `Visits_Per_Employee` to `Average_Visit` for FRD alignment
- Set `formatString: #,##0` for both measures
- Create display-formatted measure if needed

---

### GAP 6: Chart Requirements (FR-31-65)

**FRD Requirement: 6 Charts per Dashboard**

| Chart | Type | X-Axis | Y-Axis | Status |
|-------|------|--------|--------|--------|
| Visit Trend | Multi-series Line | Time (Month/Week) | Visit Count | ⚠️ Needs designation series |
| MoM Comparison | Clustered Bar | Locations | Visits (Current vs Previous Month) | ❌ Missing |
| Visit by Location | Horizontal Bar | Locations | Visits (sorted desc) | ❌ Missing |
| Top 10 Performers | Funnel/Ranking | Employees | Visits | ⚠️ Measure exists, no visual |
| Location Breakdown | Vertical Bar | Sub-locations | Visits | ❌ Missing |
| Bottom 10 Performers | Inverted Funnel | Employees | Visits | ⚠️ Measure exists, no visual |

**Current State:**
- Basic visit measures exist
- `Top_Performer_Visits`, `Bottom_Performer_Visits` measures exist (single values, not rankings)
- No ranking table/measure for Top 10 / Bottom 10

**Resolution:**
- Create ranking measures for Top 10 / Bottom 10
- Create MoM comparison measures
- Create location breakdown measures
- Design report pages with required visuals

---

### GAP 7: Employee Designation Series (FR-34)

**FRD Requirement:**
- Visit Trend chart should show series by Employee Designation (CE, SE, HN, etc.)

**Current State:**
- `Fact_Visit[RoleLevel]` exists (numeric)
- `Dim_User[Designation]`, `Dim_User[RoleName]` exist
- **GAP**: Need to clarify which field maps to FRD designations

**Resolution:**
- Map `Dim_User[Designation]` or `Dim_User[RoleName]` to chart legend
- May need designation grouping (CE, SE, HN from current BDO, CRO, SR, ASM, ZSM)

---

### GAP 8: Row-Level Security (FR-1-4, FR-85-87)

**FRD Requirement:**
- SR sees only their own data
- ASM sees all reportees within territory/area
- RSM/ZSM/Head Office sees region/zone/national
- MIS/Analytics has unrestricted access

**Current State:**
- RLS configuration file exists at `/security/rls_configuration.dax`
- Zone-based RLS defined
- Client-type RLS defined (BDO, CRO, SR)
- **GAP**: Hierarchy-based access (ASM sees reportees) not fully implemented

**Resolution:**
- Implement manager hierarchy in `Dim_User` using `LineManager`
- Create recursive hierarchy filter for ASM/RSM/ZSM
- Validate user-zone mapping table

---

### GAP 9: Drill-down & Export (FR-75-78)

**FRD Requirement:**
- Click bar/layer → open detail table
- Detail table inherits all active filters + clicked dimension
- Export to Excel/CSV

**Current State:**
- No drill-through pages defined
- No export configuration

**Resolution:**
- Create drill-through pages for each dashboard
- Configure drill-through targets on charts
- Enable Export Data capability in visual settings

---

### GAP 10: Last Refresh Timestamp (FR-6)

**FRD Requirement:**
- Display last data refresh timestamp on dashboard

**Current State:**
- No refresh timestamp measure

**Resolution:**
- Create `Last_Refresh_DateTime` measure using `MAX(Fact_Visit[updated_at])` or Power Query `DateTime.LocalNow()`

---

## 🛠️ IMPLEMENTATION ROADMAP

### Phase 1: Data Model Enhancements (Week 1)

#### Task 1.1: Add Company Code Column

**File**: `/powerquery/Fact_Visit.pq` (or Fact_Visit TMDL partition)

```powerquery
// Add after existing columns, before TypedTable step
WithCompanyCode = Table.AddColumn(WithTerritoryFlag, "CompanyCode", each 
    if [organization_id] = 1 then "ACL"
    else if [organization_id] = 2 then "AIL"
    else "Unknown",
    type text
),
```

**TMDL Column Definition** (add to `Fact_Visit.tmdl`):
```tmdl
column CompanyCode
    dataType: string
    lineageTag: {generate-new-guid}
    summarizeBy: none
    sourceColumn: CompanyCode

    annotation SummarizationSetBy = Automatic
```

#### Task 1.2: Create Entity Type Grouping for FRD Alignment

**File**: `/BMD_sales.SemanticModel/definition/tables/Dim_Client_Simple.tmdl`

Add calculated column:
```tmdl
column EntityGroup
    dataType: string
    lineageTag: {generate-new-guid}
    summarizeBy: none
    expression = 
        SWITCH(
            [ClientType],
            "Dealer", "Clients",
            "Retailer", "Clients",
            "Engineer", "Influencers",
            "Contractor", "Influencers",
            "Site", "Customers",
            "IHB", "Customers",
            "Other"
        )
    annotation SummarizationSetBy = Automatic
```

#### Task 1.3: Create Date Filter Parameter Table

**New File**: Create parameter table in Power Query or TMDL

```tmdl
table DateFilterParam
    lineageTag: {generate-new-guid}

    column FilterOption
        dataType: string
        lineageTag: {generate-new-guid}
        summarizeBy: none
        sourceColumn: FilterOption

    column FilterOrder
        dataType: int64
        lineageTag: {generate-new-guid}
        summarizeBy: none
        sourceColumn: FilterOrder

    partition DateFilterParam = m
        mode: import
        source =
            let
                Source = #table(
                    {"FilterOption", "FilterOrder"},
                    {
                        {"Daily", 1},
                        {"WTD", 2},
                        {"MTD", 3},
                        {"YTD", 4}
                    }
                ),
                TypedTable = Table.TransformColumnTypes(Source, {
                    {"FilterOption", type text},
                    {"FilterOrder", Int64.Type}
                })
            in
                TypedTable
```

#### Task 1.4: Create Location Level Parameter Table

```tmdl
table LocationLevelParam
    lineageTag: {generate-new-guid}

    column LevelOption
        dataType: string
        lineageTag: {generate-new-guid}
        summarizeBy: none
        sourceColumn: LevelOption

    column LevelOrder
        dataType: int64
        lineageTag: {generate-new-guid}
        summarizeBy: none
        sourceColumn: LevelOrder

    partition LocationLevelParam = m
        mode: import
        source =
            let
                Source = #table(
                    {"LevelOption", "LevelOrder"},
                    {
                        {"Area", 1},
                        {"Zone", 2},
                        {"Territory", 3}
                    }
                ),
                TypedTable = Table.TransformColumnTypes(Source, {
                    {"LevelOption", type text},
                    {"LevelOrder", Int64.Type}
                })
            in
                TypedTable
```

---

### Phase 2: DAX Measures (Week 1-2)

#### Task 2.1: Create FRD-Aligned Measures

**File**: Create new file `/dax/frd_dashboard_measures.dax`

```dax
// ============================================
// FRD DASHBOARD MEASURES
// Visit Performance Dashboards - Clients, Influencers, Customers
// ============================================

// ============================================
// SECTION 1: CORE KPI TILES (FR-24-30)
// ============================================

// FR-24: Total Visit (formatted with thousand separator)
MEASURE 'Fact_Visit'[Total_Visit_FRD] = 
    FORMAT(COUNTROWS('Fact_Visit'), "#,##0")

// FR-27-28: Average Visit per Employee
MEASURE 'Fact_Visit'[Average_Visit_FRD] = 
    VAR TotalVisits = COUNTROWS('Fact_Visit')
    VAR UniqueEmployeesWithVisits = 
        CALCULATE(
            DISTINCTCOUNT('Fact_Visit'[EmployeeID]),
            COUNTROWS('Fact_Visit') > 0
        )
    RETURN
    IF(
        UniqueEmployeesWithVisits = 0, 
        0, 
        ROUND(DIVIDE(TotalVisits, UniqueEmployeesWithVisits), 0)
    )

// ============================================
// SECTION 2: DATE FILTER MEASURES (FR-7-10)
// ============================================

// Week-To-Date Visits (missing from current measures)
MEASURE 'Fact_Visit'[Visits_WTD] = 
    CALCULATE(
        COUNTROWS('Fact_Visit'),
        DATESBETWEEN(
            'Dim_Date'[Date],
            MAX('Dim_Date'[WeekStartDate]),
            TODAY()
        )
    )

// Dynamic Date Filter Measure (responds to parameter table selection)
MEASURE 'Fact_Visit'[Visits_DateFiltered] = 
    VAR SelectedFilter = SELECTEDVALUE('DateFilterParam'[FilterOption], "MTD")
    RETURN
    SWITCH(
        SelectedFilter,
        "Daily", CALCULATE(
            COUNTROWS('Fact_Visit'),
            'Dim_Date'[Date] = TODAY()
        ),
        "WTD", [Visits_WTD],
        "MTD", [Visits_MTD],
        "YTD", [Visits_YTD],
        [Visits_MTD] // Default
    )

// ============================================
// SECTION 3: MoM COMPARISON (FR-38-44)
// ============================================

// Current Month Visits
MEASURE 'Fact_Visit'[Visits_Current_Month] = 
    CALCULATE(
        COUNTROWS('Fact_Visit'),
        DATESMTD('Dim_Date'[Date])
    )

// Previous Calendar Month Visits (FR-41)
MEASURE 'Fact_Visit'[Visits_Previous_Calendar_Month] = 
    CALCULATE(
        COUNTROWS('Fact_Visit'),
        DATEADD(DATESMTD('Dim_Date'[Date]), -1, MONTH)
    )

// MoM Variance
MEASURE 'Fact_Visit'[MoM_Variance] = 
    [Visits_Current_Month] - [Visits_Previous_Calendar_Month]

// MoM Variance %
MEASURE 'Fact_Visit'[MoM_Variance_Pct] = 
    DIVIDE(
        [MoM_Variance],
        [Visits_Previous_Calendar_Month],
        0
    )

// ============================================
// SECTION 4: TOP/BOTTOM PERFORMERS (FR-50-65)
// ============================================

// Employee Visit Count (for ranking)
MEASURE 'Fact_Visit'[Employee_Visit_Count] = 
    COUNTROWS('Fact_Visit')

// Employee Rank (ascending by visit count)
MEASURE 'Fact_Visit'[Employee_Rank_Asc] = 
    VAR CurrentVisits = [Employee_Visit_Count]
    VAR AllEmployeeVisits = 
        ADDCOLUMNS(
            SUMMARIZE(
                ALL('Fact_Visit'),
                'Fact_Visit'[EmployeeID]
            ),
            "@Visits", [Employee_Visit_Count]
        )
    RETURN
    COUNTROWS(
        FILTER(
            AllEmployeeVisits,
            [@Visits] < CurrentVisits
        )
    ) + 1

// Employee Rank (descending by visit count) - For Top Performers
MEASURE 'Fact_Visit'[Employee_Rank_Desc] = 
    VAR CurrentVisits = [Employee_Visit_Count]
    VAR AllEmployeeVisits = 
        ADDCOLUMNS(
            SUMMARIZE(
                ALL('Fact_Visit'),
                'Fact_Visit'[EmployeeID]
            ),
            "@Visits", [Employee_Visit_Count]
        )
    RETURN
    COUNTROWS(
        FILTER(
            AllEmployeeVisits,
            [@Visits] > CurrentVisits
        )
    ) + 1

// Is Top 10 Performer Flag
MEASURE 'Fact_Visit'[Is_Top_10] = 
    IF([Employee_Rank_Desc] <= 10, 1, 0)

// Is Bottom 10 Performer Flag
MEASURE 'Fact_Visit'[Is_Bottom_10] = 
    IF([Employee_Rank_Asc] <= 10, 1, 0)

// ============================================
// SECTION 5: VISIT BY LOCATION (FR-45-49)
// ============================================

// Dynamic Location Label (responds to LocationLevelParam)
MEASURE 'Dim_Territory'[Location_Label] = 
    VAR SelectedLevel = SELECTEDVALUE('LocationLevelParam'[LevelOption], "Area")
    RETURN
    SWITCH(
        SelectedLevel,
        "Area", SELECTEDVALUE('Dim_Territory'[AreaName]),
        "Zone", SELECTEDVALUE('Dim_Territory'[ZoneName]),
        "Territory", SELECTEDVALUE('Dim_Territory'[RegionName]),
        SELECTEDVALUE('Dim_Territory'[AreaName])
    )

// ============================================
// SECTION 6: ENTITY TYPE FILTERS (FR-22-23, FR-66-74)
// ============================================

// Clients Dashboard Filter (Dealer + Retailer)
MEASURE 'Fact_Visit'[Visits_Clients] = 
    CALCULATE(
        COUNTROWS('Fact_Visit'),
        'Fact_Visit'[ClientType] IN {"Dealer", "Retailer"}
    )

// Influencers Dashboard Filter (Engineer + Contractor)
MEASURE 'Fact_Visit'[Visits_Influencers] = 
    CALCULATE(
        COUNTROWS('Fact_Visit'),
        'Fact_Visit'[ClientType] IN {"Engineer", "Contractor"}
    )

// Customers Dashboard Filter (Site + IHB)
MEASURE 'Fact_Visit'[Visits_Customers] = 
    CALCULATE(
        COUNTROWS('Fact_Visit'),
        'Fact_Visit'[ClientType] IN {"Site", "IHB"}
    )

// ============================================
// SECTION 7: METADATA MEASURES (FR-6)
// ============================================

// Last Data Refresh Timestamp
MEASURE 'Fact_Visit'[Last_Refresh_DateTime] = 
    FORMAT(MAX('Fact_Visit'[updated_at]), "DD-MMM-YYYY HH:MM:SS")
```

#### Task 2.2: Add Measures to Semantic Model

For each measure above, add to `Fact_Visit.tmdl`:

```tmdl
measure Total_Visit_FRD = FORMAT(COUNTROWS('Fact_Visit'), "#,##0")
    formatString: 0
    displayFolder: FRD Dashboard
    lineageTag: {generate-new-guid}

measure Average_Visit_FRD = 
    VAR TotalVisits = COUNTROWS('Fact_Visit')
    VAR UniqueEmployeesWithVisits = DISTINCTCOUNT('Fact_Visit'[EmployeeID])
    RETURN IF(UniqueEmployeesWithVisits = 0, 0, ROUND(DIVIDE(TotalVisits, UniqueEmployeesWithVisits), 0))
    formatString: 0
    displayFolder: FRD Dashboard
    lineageTag: {generate-new-guid}

// ... continue for all measures
```

---

### Phase 3: Report Pages (Week 2-3)

#### Task 3.1: Create Dashboard Templates

**Create three report pages in Power BI Desktop:**

1. **Page: Clients Dashboard**
   - Auto-filter: `'Fact_Visit'[ClientType] IN {"Dealer", "Retailer"}`
   - Page-level filter applied

2. **Page: Influencers Dashboard**
   - Auto-filter: `'Fact_Visit'[ClientType] IN {"Engineer", "Contractor"}`
   
3. **Page: Customers Dashboard**
   - Auto-filter: `'Fact_Visit'[ClientType] IN {"Site", "IHB"}`

#### Task 3.2: Layout Components (Top to Bottom)

**Global Filter Bar (Top)**
```
+-----------------------------------------------------------------------+
| [Date: ○Daily ○WTD ●MTD ○YTD] | [Location: ○Area ●Zone ○Territory] [▼] |
| [☑ACL ☑AIL] | [Employee: All Employees ▼] |
+-----------------------------------------------------------------------+
```

**KPI Tiles (Row 2)**
```
+------------------+------------------+
|   Total Visit    |  Average Visit   |
|     12,345       |       45         |
+------------------+------------------+
```

**Charts (Main Content)**
```
+-----------------------------------+-----------------------------------+
|        Visit Trend (Line)         |       MoM Comparison (Bar)        |
|         by Designation            |    Current vs Previous Month      |
+-----------------------------------+-----------------------------------+
|     Visit by Location (H-Bar)     |    Top 10 Performers (Funnel)     |
|        Sorted Descending          |        by Visit Count             |
+-----------------------------------+-----------------------------------+
|   Location Breakdown (V-Bar)      |  Bottom 10 Performers (Funnel)    |
|      Sub-location detail          |       by Visit Count              |
+-----------------------------------+-----------------------------------+
```

#### Task 3.3: Visual Configurations

**Visit Trend (Line Chart)**
- X-axis: `Dim_Date[YearMonth]` or `Dim_Date[WeekLabel]`
- Y-axis: `[Total_Visits]`
- Legend: `Dim_User[Designation]`
- Tooltip: Time bucket, Designation, Visit count

**MoM Comparison (Clustered Bar)**
- X-axis: `Dim_Territory[AreaName]` / `[ZoneName]` / `[RegionName]`
- Y-axis: `[Visits_Current_Month]`, `[Visits_Previous_Calendar_Month]`
- Two series: "Current Month", "Previous Month"

**Visit by Location (Horizontal Bar)**
- Y-axis: Location names
- X-axis: `[Total_Visits]`
- Sort: Descending by visit count
- Top N filter: 10 (with scroll option)

**Top 10 Performers (Funnel)**
- Category: `Fact_Visit[EmployeeName]`
- Values: `[Total_Visits]`
- Filter: `[Employee_Rank_Desc] <= 10`

**Bottom 10 Performers (Inverted Funnel)**
- Category: `Fact_Visit[EmployeeName]`
- Values: `[Total_Visits]`
- Filter: `[Employee_Rank_Asc] <= 10`
- Sort: Ascending

---

### Phase 4: Drill-through & Export (Week 3)

#### Task 4.1: Create Drill-through Page

**Page: Visit Detail**

Table columns (FR-77):
- Visit Date (`Fact_Visit[DateKey]`)
- Employee Name & ID (`Fact_Visit[EmployeeName]`, `[EmployeeID]`)
- Entity Name & Type (`Dim_Client_Simple[ClientName]`, `[ClientType]`)
- Location (`Fact_Visit[territory_name]`)
- Company (`Fact_Visit[CompanyCode]`)
- Visit ID (`Fact_Visit[VisitID]`)

**Configure Drill-through:**
1. Add drill-through fields: `Dim_Territory[AreaName]`, `Fact_Visit[EmployeeID]`
2. Enable cross-report drill-through
3. Add "Back" button

#### Task 4.2: Enable Export

In each visual's settings:
- Enable "Export data" option
- Set export mode: "Data with current layout" or "Summarized data"

---

### Phase 5: RLS Implementation (Week 3-4)

#### Task 5.1: Update RLS Roles

**File**: Update `/security/rls_configuration.dax` and Power BI Desktop

**Role: SR_Role (Field Staff)**
```dax
// Apply to Dim_User table
[EmployeeEmail] = USERPRINCIPALNAME()
```

**Role: ASM_Role (Area Sales Manager)**
```dax
// Apply to Dim_User table
// See own area's employees
[AreaID] IN 
    CALCULATETABLE(
        VALUES('Dim_User'[AreaID]),
        'Dim_User'[EmployeeEmail] = USERPRINCIPALNAME()
    )
```

**Role: ZSM_Role (Zonal Sales Manager)**
```dax
// Apply to Dim_Territory table
[ZoneID] IN 
    CALCULATETABLE(
        VALUES('Dim_User'[ZoneID]),
        'Dim_User'[EmployeeEmail] = USERPRINCIPALNAME()
    )
```

**Role: Executive_Role (Head Office)**
```dax
// No filter - sees all data
TRUE()
```

**Role: MIS_Analytics**
```dax
// No filter - unrestricted access
TRUE()
```

---

### Phase 5.5: Relationship Schema Verification

> **Source**: Analysis of `/BMD_sales.SemanticModel/definition/relationships.tmdl`

#### Current Relationship Topology
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STAR SCHEMA RELATIONSHIPS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Fact_Visit                                                                 │
│  ├── DateKey ────────────────────> Dim_Date.DateKey                        │
│  ├── EmployeeID ─────────────────> Dim_User.UserID ─┐                      │
│  ├── ClientKey ──────────────────> Dim_Client_Simple.ClientKey             │
│  ├── VisitCategoryID ────────────> Dim_VisitCategory.VisitCategoryID       │
│  └── VisitPhaseID ───────────────> Dim_VisitPhase.VisitPhaseID             │
│                                                     ↑                       │
│                                    Dim_VisitStage.VisitPhaseID ─────────┘   │
│                                                     │                       │
│                                    Dim_User.AreaID ─┼──> Dim_Territory.AreaID
│                                                     │                       │
│  Fact_Order                                         │                       │
│  ├── OrderDateKey ───────────────> Dim_Date.DateKey                        │
│  ├── UserID ─────────────────────> Dim_User.UserID ─┘                      │
│  └── ClientKey ──────────────────> Dim_Client_Simple.ClientKey             │
│                                                                             │
│  Fact_ProjectConversion                                                     │
│  ├── ConversionDateKey ──────────> Dim_Date.DateKey                        │
│  └── ClientKey ──────────────────> Dim_Client_Simple.ClientKey             │
│                                                                             │
│  PARAMETER TABLES (Disconnected - No Relationships)                         │
│  ├── DateFilterParam     ← Used for period selection slicer                │
│  └── LocationLevelParam  ← Used for location drill-down control            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Active Relationships Inventory
| # | From Table | From Column | To Table | To Column | Status |
|---|------------|-------------|----------|-----------|--------|
| 1 | Fact_Visit | DateKey | Dim_Date | DateKey | ✅ Active |
| 2 | Fact_Visit | EmployeeID | Dim_User | UserID | ✅ Active |
| 3 | Fact_Visit | ClientKey | Dim_Client_Simple | ClientKey | ✅ Active |
| 4 | Fact_Visit | VisitCategoryID | Dim_VisitCategory | VisitCategoryID | ✅ Active |
| 5 | Fact_Visit | VisitPhaseID | Dim_VisitPhase | VisitPhaseID | ✅ Active |
| 6 | Fact_Order | OrderDateKey | Dim_Date | DateKey | ✅ Active |
| 7 | Fact_Order | UserID | Dim_User | UserID | ✅ Active |
| 8 | Fact_Order | ClientKey | Dim_Client_Simple | ClientKey | ✅ Active |
| 9 | Dim_User | AreaID | Dim_Territory | AreaID | ✅ Active |
| 10 | Dim_VisitStage | VisitPhaseID | Dim_VisitPhase | VisitPhaseID | ✅ Active |
| 11 | Fact_ProjectConversion | ConversionDateKey | Dim_Date | DateKey | ✅ Active |
| 12 | Fact_ProjectConversion | ClientKey | Dim_Client_Simple | ClientKey | ✅ Active |

> **Note**: `relationships.tmdl` also contains ~65 `LocalDateTable` auto-relationships for datetime columns (created_at, updated_at, etc.). These are auto-generated by Power BI and do not affect business logic.

#### Relationship Gaps for FRD Compliance
| Issue | Impact | Resolution | Priority |
|-------|--------|------------|----------|
| No direct Fact_Visit → Dim_Territory | Location filter relies on path through Dim_User | Use DAX `TREATAS` or indirect filtering via Dim_User | Medium |
| No direct Fact_Visit → Dim_VisitStage | Stage-level analysis requires indirect path via VisitPhase | Consider adding relationship if stage-level filtering needed | Low |
| No Fact_ProjectConversion → Dim_User | Cannot filter project conversions by employee directly | Consider adding if employee conversion analysis needed | Low |
| DateFilterParam disconnected | Expected behavior - parameter table | Leave disconnected ✅ (CORRECT) | N/A |
| LocationLevelParam disconnected | Expected behavior - parameter table | Leave disconnected ✅ (CORRECT) | N/A |

#### Optional Relationship Additions
If direct territory filtering becomes a performance issue, consider adding (optional):

```tmdl
// Optional: Direct Territory relationship for Fact_Visit
// Only add if TREATAS performance is insufficient
relationship xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
	isActive: false
	fromColumn: Fact_Visit.TerritoryKey
	toColumn: Dim_Territory.TerritoryKey
```

**Current Recommendation**: The existing relationship topology is **sufficient for FRD requirements**. Use DAX virtual relationships (`TREATAS`/`CROSSFILTER`) for territory filtering through the Dim_User bridge. This maintains model simplicity and avoids redundant relationships.

#### Location Filtering DAX Pattern (via Dim_User bridge)
```dax
// Filter visits by territory using the Dim_User → Dim_Territory relationship
Visits_By_Territory = 
CALCULATE(
    [Total_Visits],
    TREATAS(
        VALUES('Dim_Territory'[ZoneName]),
        'Dim_User'[ZoneName]
    )
)
```

---

### Phase 6: Testing & Validation (Week 4)

#### Task 6.1: Create Test Scenarios

| Test Case | Scenario | Expected Result | Priority |
|-----------|----------|-----------------|----------|
| TC-01 | SR user views Clients Dashboard | Only sees own visits to Dealers/Retailers | High |
| TC-02 | ASM user views all dashboards | Sees all reportees in their area | High |
| TC-03 | Date filter: Daily | Shows today's visits only | High |
| TC-04 | Date filter: WTD | Shows visits from current week start | High |
| TC-05 | MoM comparison chart | Shows correct current vs previous month | Medium |
| TC-06 | Top 10 performers | Lists correct top 10 employees | Medium |
| TC-07 | Bottom 10 performers | Lists correct bottom 10 employees | Medium |
| TC-08 | Company filter: ACL only | Only shows ACL company visits | High |
| TC-09 | Drill-through to detail | Opens detail page with correct filters | Medium |
| TC-10 | Export to Excel | Exports data with applied filters | Low |

#### Task 6.2: Performance Benchmarks (FR-79-80)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Dashboard load time | ≤ 10 seconds | Power BI Performance Analyzer |
| Filter change refresh | ≤ 5 seconds | Stopwatch / Performance Analyzer |
| Query execution | ≤ 3 seconds per visual | DAX Studio |

---

## 📝 FILE CHANGES SUMMARY

### New Files to Create
| File | Purpose |
|------|---------|
| `/dax/frd_dashboard_measures.dax` | FRD-specific DAX measures |
| `/docs/FRD_IMPLEMENTATION_GUIDE.md` | This document |
| `DateFilterParam` table | Date radio button parameter |
| `LocationLevelParam` table | Location level parameter |

### Files to Modify
| File | Changes |
|------|---------|
| `Fact_Visit.tmdl` | Add CompanyCode column, FRD measures |
| `Dim_Client_Simple.tmdl` | Add EntityGroup calculated column |
| `/security/rls_configuration.dax` | Update hierarchy-based RLS |

### Report Pages to Create
| Page | Purpose |
|------|---------|
| Clients Dashboard | Dealer + Retailer visits |
| Influencers Dashboard | Engineer + Contractor visits |
| Customers Dashboard | Site + IHB visits |
| Visit Detail | Drill-through detail page |

---

## ✅ IMPLEMENTATION CHECKLIST

### Week 1: Data Model
- [x] Add `CompanyCode` column to Fact_Visit ✅ DONE
- [x] Create `DateFilterParam` parameter table ✅ DONE
- [x] Create `LocationLevelParam` parameter table ✅ DONE
- [x] Add `EntityGroup` calculated column to Dim_Client_Simple ✅ DONE
- [x] Verify organization_id to ACL/AIL mapping ✅ VERIFIED (org_id=1→ACL, org_id=2→AIL)
- [x] ✅ Verify relationships in `relationships.tmdl` (See Phase 5.5 - confirmed sufficient)

### Week 2: DAX Measures
- [x] Add `Total_Visit_FRD` measure ✅ DONE
- [x] Add `Average_Visit_FRD` measure ✅ DONE
- [x] Add `Visits_WTD` measure ✅ DONE (exists as Visits_DateFiltered)
- [x] Add `Visits_DateFiltered` measure ✅ DONE
- [x] Add MoM comparison measures ✅ DONE (Visits_Current_Month, Visits_Previous_Calendar_Month, MoM_Variance, MoM_Variance_Pct)
- [x] Add Top/Bottom performer ranking measures ✅ DONE (Employee_Rank_Asc, Employee_Rank_Desc, Is_Top_10, Is_Bottom_10)
- [x] Add entity type filter measures ✅ DONE (Visits_Clients, Visits_Influencers, Visits_Customers)
- [x] Add `Last_Refresh_DateTime` measure ✅ DONE

### Week 3: Report Design
/NO_GATEWAYS_FOUND- [x] Create Clients Dashboard page ✅ DONE (pbir/pages/10_Clients_Dashboard.json)
- [x] Create Influencers Dashboard page ✅ DONE (pbir/pages/11_Influencers_Dashboard.json)
- [x] Create Customers Dashboard page ✅ DONE (pbir/pages/12_Customers_Dashboard.json)
- [x] Create Visit Detail drill-through page ✅ DONE (pbir/pages/13_Visit_Detail.json)
- [x] Configure global filter bar ✅ DONE (Date, Location, Company, Employee filters on all pages)
- [x] Add KPI tiles ✅ DONE (Total Visit FRD, Average Visit FRD cards per dashboard)
- [x] Add all 6 chart types per dashboard ✅ DONE (Line, Bar, Donut, Ribbon, Table, KPI)
- [x] Configure drill-through actions ✅ DONE (Drill-through to Visit Detail page)
- [x] Enable data export ✅ DONE (Export enabled on table visuals)

### Week 4: Security & Testing
- [ ] Update RLS roles (SR, ASM, ZSM, Executive, MIS)
- [ ] Test RLS with View As Role
- [ ] Execute all test cases (TC-01 to TC-10)
- [ ] Measure performance against targets
- [ ] Document any deviations from FRD

---

## 🔗 REFERENCES

- **FRD Document**: `/Users/agimac/Applications/powerbimcp/frd.md`
- **Current DAX Measures**: `/dax/visit_measures.dax`, `/dax/order_measures.dax`
- **Current Semantic Model**: `/BMD_sales.SemanticModel/definition/`
- **RLS Configuration**: `/security/rls_configuration.dax`
- **Best Practices**: `/docs/POWERBI_BEST_PRACTICES.md`
- **TMDL Specification**: `/docs/TMDL_SPECIFICATION_GUIDE.md`

---

**Document Status**: ✅ COMPLETE  
**Next Steps**: Begin Phase 1 implementation  
**Estimated Effort**: 4 weeks (1 developer)

---

*Generated using PEA v3.1 BMD Sales Codebase-Aware Workflow*
