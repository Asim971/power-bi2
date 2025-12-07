# Power BI Best Practices Catalog

**Version**: 1.0  
**Research Date**: December 2, 2025  
**Source**: Microsoft Power BI Best Practices, Community Guidelines, BMD Sales Project Analysis

---

## TABLE OF CONTENTS

1. [Data Modeling Best Practices](#section-1-data-modeling-best-practices)
2. [DAX Optimization & Performance](#section-2-dax-optimization--performance)
3. [Power Query (M Language) Best Practices](#section-3-power-query-m-language-best-practices)
4. [Report Design & UX](#section-4-report-design--ux)
5. [Security & RLS](#section-5-security--rls)
6. [Performance Monitoring & Tuning](#section-6-performance-monitoring--tuning)
7. [Version Control & CI/CD](#section-7-version-control--cicd)
8. [Testing & Quality Assurance](#section-8-testing--quality-assurance)
9. [BMD Sales Specific Recommendations](#section-9-bmd-sales-specific-recommendations)

---

## SECTION 1: DATA MODELING BEST PRACTICES

### 1.1 Star Schema Design

**Pattern**: Use star schema with fact and dimension tables

```tmdl
// GOOD: Star schema structure
table 'Fact_Visit'
	// Key columns
	column VisitID (primary key)
	column DateKey (foreign key to Dim_Date)
	column EmployeeID (foreign key to Dim_User)
	column ClientKey (foreign key to Dim_Client)
	
	// Measures
	measure 'Total_Visits' = COUNTROWS('Fact_Visit')

table 'Dim_Date'
	column DateKey (primary key)
	column Date, Year, Quarter, Month, Day

table 'Dim_User'
	column EmployeeID (primary key)
	column EmployeeName, Role, ZoneID

table 'Dim_Client'
	column ClientKey (primary key)
	column ClientName, ClientType, ResponsibleRole
```

**Benefits**:
- Easy to navigate relationships
- Efficient query execution
- Simple aggregations
- Clear separation of concerns

### 1.2 Dimension Table Guidelines

| Characteristic | Recommendation |
|---|---|
| **Size** | Small-to-medium (up to 1M rows typical) |
| **Update Frequency** | Infrequently (reference data) |
| **Grain** | Atomic (one row per entity) |
| **Keys** | Use surrogate keys (integers) as primary keys |
| **Attributes** | Denormalize for analytics (2-3NF trade-offs) |

### 1.3 Fact Table Guidelines

| Characteristic | Recommendation |
|---|---|
| **Size** | Large (millions of rows common) |
| **Grain** | Atomic level (one row = one business event) |
| **Keys** | Foreign keys to all dimensions |
| **Measures** | Additive (SUM-able) values |
| **Attributes** | Minimal (move to dimensions) |

### 1.4 Partition Key Strategy (BMD Sales Context)

```tmdl
// Example: Partition Fact_Visit by year for incremental refresh
table 'Fact_Visit'
	
	partition 'Fact_Visit_2024' = m
		mode: import
		source = Table.FromRows(
			...WHERE YEAR(VisitDate) = 2024
		)
	
	partition 'Fact_Visit_2023' = m
		mode: import
		source = Table.FromRows(
			...WHERE YEAR(VisitDate) = 2023
		)
	
	partition 'Fact_Visit_2022' = m
		mode: import
		source = Table.FromRows(
			...WHERE YEAR(VisitDate) = 2022
		)
```

**Benefits**:
- Incremental refresh (only update latest partition)
- Reduced refresh time
- Better memory management
- Ability to archive older data

### 1.5 Hierarchy Design

```tmdl
// GOOD: Logical hierarchies
hierarchy 'Territory_Hierarchy'
	levels: [Zone, Region, Area, ASM]
	// Enables drill-down: Zone → Region → Area → Individual

hierarchy 'Date_Hierarchy'
	levels: [Year, Quarter, Month, Day]
	// Enables time-based drill-down

hierarchy 'Client_Hierarchy'
	levels: [ClientType, ClientGroup, IndividualClient]
	// Enables client-level analysis
```

---

## SECTION 2: DAX OPTIMIZATION & PERFORMANCE

### 2.1 Measure Design Patterns

#### Pattern 1: Simple Aggregation

```dax
// GOOD: Fast, direct aggregation
Total_Visits = COUNTROWS('Fact_Visit')

Total_Orders = SUM('Fact_Order'[Amount])
```

#### Pattern 2: Conditional Aggregation (CALCULATE)

```dax
// GOOD: Use CALCULATE for complex filtering
High_Quality_Visits = 
	CALCULATE(
		COUNTROWS('Fact_Visit'),
		'Fact_Visit'[QualityScore] >= 85
	)

// BETTER: Separate filter logic for readability
High_Quality_Visits_v2 = 
	VAR HighQualityThreshold = 85
	RETURN
		CALCULATE(
			COUNTROWS('Fact_Visit'),
			'Fact_Visit'[QualityScore] >= HighQualityThreshold
		)
```

#### Pattern 3: Time Intelligence

```dax
// GOOD: Use time intelligence functions
YTD_Orders = 
	CALCULATE(
		SUM('Fact_Order'[Amount]),
		DATESYTD(Dim_Date[Date])
	)

Previous_Month_Orders = 
	CALCULATE(
		SUM('Fact_Order'[Amount]),
		DATEADD(Dim_Date[Date], -1, MONTH)
	)

Growth_vs_Previous_Month = 
	DIVIDE(
		[Current_Month_Orders] - [Previous_Month_Orders],
		[Previous_Month_Orders],
		0
	)
```

### 2.2 Performance Optimization Rules

| Anti-Pattern | Problem | Solution |
|---|---|---|
| `SUMX(Table, ...)` on fact table | Row iteration = slow | Use `SUM()` with grouping |
| `ALL()` without filters | Removes all context | Use `ALL(Column)` for specific columns |
| Nested `CALCULATE` | Complex context | Simplify with `VAR` variables |
| `HASONEVALUE()` checks | Unclear intent | Use explicit filter context |
| `CALCULATE` in calculated columns | Computed at refresh | Move to measures (on-demand) |

### 2.3 Variable Pattern (VAR)

```dax
// GOOD: Use VAR for readability and performance
Conversion_Rate = 
	VAR TotalVisits = CALCULATE(COUNTROWS('Fact_Visit'))
	VAR ConvertedVisits = CALCULATE(COUNTROWS('Fact_ProjectConversion'))
	RETURN
		DIVIDE(ConvertedVisits, TotalVisits, 0)

// Readable, testable, cacheable
```

### 2.4 Measure Display Folder Organization

```dax
// Organize measures by folder
measure 'Total_Visits' = ...
	displayFolder: "Visit Analytics"

measure 'Unique_Clients' = ...
	displayFolder: "Visit Analytics"

measure 'Avg_Quality_Score' = ...
	displayFolder: "Quality Metrics"

measure 'Visit_Quality_Trend' = ...
	displayFolder: "Quality Metrics"

// Users see organized folder structure in field list
```

---

## SECTION 3: POWER QUERY (M LANGUAGE) BEST PRACTICES

### 3.1 Transformation Order

```m
// GOOD order of transformations:
// 1. Filter early (reduce rows)
// 2. Select columns (reduce columns)
// 3. Type conversion (set types)
// 4. Add calculations (computed columns)
// 5. Sort/Group (final organization)

let
    Source = Sql.Database("server", "database"),
    
    // Step 1: Filter
    FilteredData = Table.SelectRows(Source, 
        each [VisitDate] >= Date.FromText("2024-01-01")),
    
    // Step 2: Select columns
    SelectedColumns = Table.SelectColumns(FilteredData, 
        {"VisitID", "ClientID", "EmployeeID", "VisitDate", "Amount"}),
    
    // Step 3: Set types
    TypedData = Table.TransformColumnTypes(SelectedColumns, {
        {"VisitID", Int64.Type},
        {"ClientID", Int64.Type},
        {"EmployeeID", Int64.Type},
        {"VisitDate", type date},
        {"Amount", type number}
    }),
    
    // Step 4: Add calculated column
    WithCalculations = Table.AddColumn(TypedData, "Year", 
        each Date.Year([VisitDate]), Int64.Type),
    
    // Step 5: Return
    Result = WithCalculations
in
    Result
```

### 3.2 Error Handling Pattern

```m
// GOOD: Handle errors gracefully
let
    Source = try Sql.Database("server", "database")
        otherwise null,
    
    SafeData = if Source <> null then Source else 
        #table({"VisitID", "Amount"}, {{null, null}})
    
in
    SafeData

// Alternative: Try-otherwise with fallback
let
    Source = Table.FromWeb("http://api.example.com/data"),
    SafeSource = try Source otherwise #table({}, {})
in
    SafeSource
```

### 3.3 Performance Optimization (M Language)

#### Technique 1: Query Folding

```m
// GOOD: Pushes filtering to source
let
    Source = Sql.Database("server", "db"),
    FilteredData = Table.SelectRows(Source, 
        each [Year] = 2024 and [Status] = "Active")
in
    FilteredData
// Query folding: Filter happens in SQL, not in Power BI
```

#### Technique 2: Native SQL Query

```m
// GOOD: Use native SQL for complex queries
let
    Source = Sql.Database("server", "database",
        [Query = "SELECT * FROM visits WHERE year = 2024 AND status = 'Active'"]),
    TypedData = Table.TransformColumnTypes(Source, {
        {"VisitID", Int64.Type},
        {"Amount", type currency}
    })
in
    TypedData
// More efficient than Power Query transformations
```

### 3.4 Naming Conventions

```m
// Clear, descriptive step names
let
    GetSourceData = Sql.Database("server", "db"),
    FilterRecentData = Table.SelectRows(GetSourceData, 
        each [Date] >= Date.FromText("2024-01-01")),
    SelectRelevantColumns = Table.SelectColumns(FilterRecentData, 
        {"VisitID", "Amount", "Status"}),
    SetColumnTypes = Table.TransformColumnTypes(SelectRelevantColumns, {
        {"VisitID", Int64.Type},
        {"Amount", type currency},
        {"Status", type text}
    }),
    Result = SetColumnTypes
in
    Result
```

---

## SECTION 4: REPORT DESIGN & UX

### 4.1 Page Layout Principles

| Principle | Implementation |
|---|---|
| **Information Hierarchy** | Key metrics at top, details below |
| **Logical Grouping** | Related visuals together |
| **White Space** | 20-30% blank area for readability |
| **Consistency** | Same chart types for same metrics |
| **Accessibility** | High contrast, readable fonts |

### 4.2 Visual Selection Guidelines

| Question | Recommended Visual |
|---|---|
| How many / proportion? | Card, KPI |
| Distribution / variation? | Histogram, box plot |
| Comparison across categories? | Bar or column chart |
| Trend over time? | Line chart |
| Part-to-whole? | Pie, donut, stacked bar |
| Relationship / correlation? | Scatter plot, bubble |
| Drill-down / hierarchy? | Decomposition, tree |
| Geographic data? | Map, filled map |
| Many dimensions? | Matrix, table, ribbon |

### 4.3 Color Best Practices

```json
// GOOD: Use theme-based color palette
{
  "dataColors": [
    "#1F4E79",    // Primary (dark blue)
    "#3BB273",    // Success (green)
    "#F2C811",    // Warning (yellow)
    "#E74856",    // Error (red)
    "#00BCF2",    // Information (light blue)
    "#44546A",    // Neutral (gray)
    "#7FBA00",    // Alternative (olive)
    "#FFB900"     // Alternative (orange)
  ]
}

// DO NOT: Use many arbitrary colors
// DO NOT: Use red-green alone (colorblind issue)
// DO NOT: Use low-contrast colors
```

### 4.4 Interactivity Patterns

#### Pattern 1: Slicer Filtering

```
User selects value in slicer
↓
Report visuals filter automatically
↓
Only relevant data displayed
```

#### Pattern 2: Cross-Visual Filtering

```
User clicks data point in Chart A
↓
Chart B automatically filters to related data
↓
Context flows through relationships
```

#### Pattern 3: Drill-Through Navigation

```
User right-clicks detail in Chart
↓
Context passes to detail page
↓
Detail page shows filtered data for that item
```

---

## SECTION 5: SECURITY & RLS

### 5.1 RLS Role Design Pattern

```tmdl
// GOOD: Role-based access control
role 'BDO'
	tablePermission 'Fact_Visit'
		metadataPermission: read
		filterExpression = 
			'Dim_Client'[ResponsibleRole] IN {"BDO", "CRO,BDO"}

role 'CRO'
	tablePermission 'Fact_Visit'
		metadataPermission: read
		filterExpression = 
			'Dim_Client'[ResponsibleRole] IN {"CRO", "CRO,BDO"}

role 'Manager'
	tablePermission 'Fact_Visit'
		metadataPermission: read
		// No filter = view all (manager override)
```

### 5.2 RLS Testing Strategy

```
1. Grant user "BDO" role in Power BI Service
2. Use "View as" feature in Desktop to test role
3. Verify user cannot see CRO-restricted data
4. Verify aggregations are correct (no hidden rows)
5. Check performance (RLS adds filter overhead)
```

### 5.3 Security Audit Checklist

- [ ] All fact tables have row-level filters
- [ ] Sensitive columns hidden from users
- [ ] Role membership validated against AD groups
- [ ] RLS performance tested with large datasets
- [ ] Audit log enabled for report access
- [ ] Credentials encrypted (Azure Key Vault)

---

## SECTION 6: PERFORMANCE MONITORING & TUNING

### 6.1 Key Performance Metrics

| Metric | Target | How to Measure |
|---|---|---|
| **Report Load Time** | < 3 seconds | Browser dev tools > Network tab |
| **Query Response** | < 5 seconds | DAX Studio query analyzer |
| **Model Size** | < 1 GB | Power BI Service capacity |
| **Refresh Duration** | < 1 hour | Power BI Service refresh history |
| **Visual Render Time** | < 500ms | Browser dev tools > Performance |

### 6.2 Optimization Techniques

#### Technique 1: Aggregation Tables

```tmdl
// Pre-aggregate frequently queried metrics
table 'Fact_Visit_Summary'
	column Month, dataType: datetime
	column Zone, dataType: text
	column TotalVisits, dataType: int64
	column TotalQuality, dataType: double
	column AvgDuration, dataType: double
	
	// Index for fast lookups
	measure 'Aggregated_Visits' = SUM([TotalVisits])

// Point measures to aggregation table instead of raw data
```

#### Technique 2: Incremental Refresh

```tmdl
// Refresh only latest partition
table 'Fact_Visit'
	
	partition 'Historical' = m
		mode: import
		source = Table.FromRows(...WHERE Year < 2024)
	
	partition 'Current_Year' = m
		mode: import
		source = Table.FromRows(...WHERE Year = 2024)
		// Refresh this daily/weekly only
```

#### Technique 3: Hide Unnecessary Columns

```tmdl
column 'InternalID'
	isHidden: true          // Don't show to users

column 'ClientKey'
	isHidden: false         // Show (used for linking)
```

### 6.3 Using DAX Studio for Analysis

1. **Connect to model** → DAX Studio → Home tab
2. **Run query** → Paste DAX measure/query
3. **Analyze results** → Check query plan
4. **Identify bottlenecks** → Look for expensive operations
5. **Optimize** → Simplify CALCULATE, use SUMMARIZECOLUMNS

---

## SECTION 7: VERSION CONTROL & CI/CD

### 7.1 Git Repository Structure

```
power-bi2/
├── .gitignore
├── README.md
├── BMD_sales.SemanticModel/
│   ├── definition/
│   │   ├── model.tmdl
│   │   ├── database.tmdl
│   │   ├── relationships.tmdl
│   │   └── tables/
│   │       └── *.tmdl
│   └── definition.pbism (ignore in git)
├── BMDSalesReport.Report/
│   ├── report.json
│   ├── definition.pbir
│   └── StaticResources/
├── .vscode/
│   ├── settings.json
│   ├── launch.json
│   └── extensions-recommendations.json
└── docs/
    ├── ARCHITECTURE.md
    ├── DATAMODEL.md
    └── DEPLOYMENT.md
```

### 7.2 .gitignore Template

```
# Power BI specific
*.pbism
*.pbix
*.pbit
*.pbir-cache
*.pbiXPCF

# Python
__pycache__/
*.py[cod]
*$py.class
.env
venv/

# VS Code
.vscode/.history/
*.code-workspace

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
```

### 7.3 Commit Message Convention

```
# Format: <type>(<scope>): <subject>

feat(semantic-model): add new quality scoring measure
fix(report): correct conversion rate calculation
docs(readme): update deployment instructions
refactor(dax): optimize visit_quality measure
test(model): add RLS validation tests

# Use tags for releases
git tag -a v1.0.0 -m "Release version 1.0.0"
```

---

## SECTION 8: TESTING & QUALITY ASSURANCE

### 8.1 Model Validation Checklist

- [ ] **Relationships**: All foreign keys have active relationships
- [ ] **Keys**: All dimension tables have unique primary keys
- [ ] **Data Types**: Columns have appropriate data types
- [ ] **Naming**: Consistent naming convention (PascalCase, snake_case)
- [ ] **Measures**: All measures have clear description & display folder
- [ ] **RLS**: Test each role can access appropriate data
- [ ] **Performance**: Query execution < 5 seconds
- [ ] **Refresh**: Full model refresh completes successfully

### 8.2 Report Validation Checklist

- [ ] **Visuals**: All visuals have meaningful titles
- [ ] **Colors**: Use theme colors consistently
- [ ] **Interactions**: Cross-filtering works as expected
- [ ] **Drill-Through**: Detail pages load correct context
- [ ] **Responsiveness**: Report works on desktop and mobile
- [ ] **Accessibility**: Colors have sufficient contrast
- [ ] **Performance**: Report loads in < 3 seconds
- [ ] **Data Accuracy**: Values match expected results

### 8.3 Automated Testing with Python

```python
# Example: Validate measure calculations
import requests
import json

# Query Power BI REST API to validate measures
def validate_measure(workspace_id, dataset_id, measure_name, expected_value):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"
    
    dax_query = f"EVALUATE {{ROW(\"{measure_name}\", [{measure_name}])}}"
    
    response = requests.post(url, json={"queries": [{"query": dax_query}]})
    result = response.json()
    
    actual_value = result['results'][0]['tables'][0]['rows'][0]['values'][0]
    
    assert actual_value == expected_value, f"Expected {expected_value}, got {actual_value}"
    print(f"✓ {measure_name} = {actual_value}")

# Run validation
validate_measure(workspace_id, dataset_id, "Total_Visits", 36041)
validate_measure(workspace_id, dataset_id, "Conversion_Rate", 0.25)
```

---

## SECTION 9: BMD SALES SPECIFIC RECOMMENDATIONS

### 9.1 Data Model Optimization

**Current State**: 36,041 visits, 272 users, 48 territories

**Recommendations**:

1. **Partition Fact_Visit by Year** — Incremental refresh
   ```tmdl
   partition 'Fact_Visit_2024' = ... WHERE YEAR(VisitDate) = 2024
   partition 'Fact_Visit_2023' = ... WHERE YEAR(VisitDate) = 2023
   ```

2. **Add Aggregation Table** — Pre-compute daily visit summaries
   ```tmdl
   table 'Agg_Daily_Summary'
       columns: Date, Zone, TotalVisits, TotalQuality, TotalRevenue
   ```

3. **Optimize Territory Hierarchy** — Consider star join
   ```tmdl
   hierarchy 'Territory_Rollup'
       levels: [Zone, Region, Area, ASM]
   ```

### 9.2 DAX Measure Recommendations

**From /dax/visit_measures.dax**:

```dax
// Add YTD/MTD rolling calculations
YTD_Visits = DATESYTD(Dim_Date[Date])
MTD_Visits = DATESMTD(Dim_Date[Date])
Prior_Year_Visits = DATEADD(Dim_Date[Date], -1, YEAR)

// Add trend analysis
Visit_Trend_Pct = DIVIDE(
    [Current_Period] - [Prior_Period],
    [Prior_Period],
    0
)

// Add quality thresholds
High_Quality_Visits = CALCULATE(COUNTROWS('Fact_Visit'), [QualityScore] >= 85)
Low_Quality_Visits = CALCULATE(COUNTROWS('Fact_Visit'), [QualityScore] < 60)
```

### 9.3 Report Performance Improvements

**Current**:
- 6 main pages + navigation infrastructure
- Multiple KPI cards (5-10 per page)
- Cross-filtering enabled globally

**Recommendations**:

1. **Limit visuals per page** → Max 8-10 (currently may exceed)
2. **Add page-level slicers** → Pre-filter data before visual rendering
3. **Use aggregation tables** → For summary pages
4. **Enable drill-through** → Instead of showing all details

### 9.4 RLS Enhancement

**Current Implementation**: BDO/CRO/SR roles with ResponsibleRoleRLS filter

**Recommendations**:

1. **Add Territory-based RLS** — Filter by user's assigned zone
   ```tmdl
   filterExpression = Dim_Territory[Zone] = 
       LOOKUPVALUE(Dim_Territory[Zone], Dim_User[EmployeeID], USERPRINCIPALNAME())
   ```

2. **Add Time-based RLS** — Restrict historical access
   ```tmdl
   filterExpression = Dim_Date[Date] >= TODAY() - 365
   ```

3. **Document RLS roles** → Create RLS_DOCUMENTATION.md

---

## APPENDIX A: QUICK REFERENCE - ANTI-PATTERNS TO AVOID

| Anti-Pattern | Why Bad | Better Approach |
|---|---|---|
| Calculated column on 1M+ row table | Slow refresh, high memory | Use measure instead |
| SUMX on fact table without filtering | Row-by-row iteration = slowness | Use SUM + CALCULATE |
| Relationship without active flag | Unpredictable auto-filtering | Mark one relationship active |
| Hardcoded colors in report | Breaks theme consistency | Use theme colors |
| No RLS on sensitive fact table | Data exposure risk | Add row-level security roles |
| Measure without description | Confusing to users | Always add descriptions |
| DirectQuery on large table | Slow query performance | Use import with aggregations |
| No version control | Can't track changes | Use Git for all files |

---

## APPENDIX B: HELPFUL TOOLS & RESOURCES

### Tools
- **DAX Studio**: https://daxstudio.org/ (Query optimization)
- **Tabular Editor 3**: https://tabulareditor.com/ (TMDL editing)
- **VertiPaq Analyzer**: Included in DAX Studio (Memory analysis)
- **Power BI REST API**: Power BI Service automation

### Learning Resources
- **Microsoft Learn**: https://learn.microsoft.com/en-us/power-bi/
- **DAX Guide**: https://dax.guide/
- **Power BI Community Forum**: https://community.powerbi.com/
- **SQLBI**: https://www.sqlbi.com/ (Advanced courses)

---

**Document Complete**

