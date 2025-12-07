# TMDL (Tabular Model Definition Language) — Complete Specification Guide

**Version**: 1.0  
**Research Date**: December 2, 2025  
**Source**: Microsoft Power BI Semantic Model Programming Models Documentation  
**Reference**: [Microsoft Learn - Semantic Model Programming Models](https://learn.microsoft.com/en-us/power-bi/developer/embedded/semantic-model-programming-models)

---

## TABLE OF CONTENTS

1. [TMDL Overview & Purpose](#section-1-tmdl-overview--purpose)
2. [TMDL Syntax Reference](#section-2-tmdl-syntax-reference)
3. [Table Definitions](#section-3-table-definitions)
4. [Column Types & Properties](#section-4-column-types--properties)
5. [Relationships](#section-5-relationships)
6. [Measures & Calculated Columns](#section-6-measures--calculated-columns)
7. [Hierarchies & Time Intelligence](#section-7-hierarchies--time-intelligence)
8. [Annotations & Metadata](#section-8-annotations--metadata)
9. [Role-Level Security (RLS)](#section-9-role-level-security-rls)
10. [Best Practices & Performance](#section-10-best-practices--performance)
11. [BMD Sales Codebase Integration](#section-11-bmd-sales-codebase-integration)

---

## SECTION 1: TMDL OVERVIEW & PURPOSE

### 1.1 What is TMDL?

**TMDL** (Tabular Model Definition Language) is a declarative, text-based language used to define Power BI semantic models (formerly called "datasets"). It represents the complete data model structure including:

- Tables & columns
- Relationships
- Measures (DAX calculations)
- Calculated columns
- Hierarchies
- Row-level security (RLS) rules
- Data types & properties
- Metadata & annotations

### 1.2 TMDL vs. Legacy Formats

| Aspect | TMDL (Modern) | PBISM (Legacy Compiled) |
|--------|---------------|-------------------------|
| **Format** | Text-based (.tmdl files) | Binary compiled (.pbism file) |
| **Readability** | Human-readable, git-friendly | Binary, not human-readable |
| **Version Control** | Excellent (line-by-line diffs) | Poor (entire binary changes) |
| **Editing** | Text editors, Tabular Editor 3 | Power BI Desktop only |
| **Validation** | Can be pre-checked | Only at compile time |
| **Maintenance** | Easy refactoring | Difficult refactoring |

### 1.3 TMDL Project Structure

```
SemanticModel/
├── definition.pbism          ← Compiled model (auto-generated from TMDL)
├── definition/
│   ├── model.tmdl            ← Main model definition
│   ├── database.tmdl         ← Database compatibility level
│   ├── relationships.tmdl    ← All table relationships
│   └── tables/               ← Individual table definitions
│       ├── Fact_Visit.tmdl
│       ├── Dim_Date.tmdl
│       ├── Dim_User.tmdl
│       └── ... other tables ...
└── .platform                 ← Platform metadata
```

---

## SECTION 2: TMDL SYNTAX REFERENCE

### 2.1 Top-Level Declarations

```tmdl
// Database-level configuration
database
	compatibilityLevel: 1600    // Power BI Premium & Pro (latest)
	
model Model                     // Model definition
	culture: en-US              // Default locale
	dataAccessOptions
		legacyRedirects         // Enable legacy redirects for compatibility
		returnErrorValuesAsNull // Treat errors as NULL
	
	// Annotations
	annotation PBI_TimeIntelligenceEnabled = 1
	annotation PBI_ProTooling = ["WebModelingEdit", "CalcGroup", "DaxQueryView_Desktop", "TMDL-Extension"]
```

### 2.2 File Structure Pattern

**model.tmdl** (Main model):
```tmdl
model Model
	culture: en-US
	defaultPowerBIDataSourceVersion: powerBI_V3
	discourageImplicitMeasures
	sourceQueryCulture: en-US
	dataAccessOptions
		legacyRedirects
		returnErrorValuesAsNull
	
	// Global annotations (query order, time intelligence, etc.)
	annotation PBI_QueryOrder = ["table1", "table2", "table3", ...]
	annotation __PBI_TimeIntelligenceEnabled = 1
	annotation PBI_ProTooling = [...]
	
	// Reference all tables
	ref table 'TableName1'
	ref table 'TableName2'
	// ... all tables ...
	
	// Optionally define roles or other model-level elements
	role 'RoleName'
		// RLS rules
```

---

## SECTION 3: TABLE DEFINITIONS

### 3.1 Basic Table Structure

```tmdl
table 'TableName'
	lineageTag: <GUID>          // Unique identifier for tracking
	
	// Column definitions
	column 'ColumnName'
		dataType: text          // text, int64, double, boolean, datetime, etc.
		lineageTag: <GUID>
		sourceColumn: "SourceName"  // Maps to source data
		dataCategory: "Uncategorized"
	
	// Data source (M language query)
	partition 'TableName' = m
		mode: import            // import or directquery
		source = Table.FromRows(
			json.Document(
				json.FromValue(...)),
			null,
			[Implementation="2.0"]
		)
	
	// Relationships
	foreignKeyColumn Dim_Date[DateKey]
	foreignKeyColumn Dim_User[EmployeeID]
	
	// Measures (aggregations)
	measure 'MeasureName' = SUM([ColumnName])
		lineageTag: <GUID>
		displayFolder: "Category"
	
	// Calculated columns
	calculatedColumn 'CalcColumnName' = [Column1] + [Column2]
	
	// Hierarchies
	hierarchy 'HierarchyName'
		levels: [Level1, Level2, Level3]
```

### 3.2 Column Data Types

```tmdl
column 'TextColumn'
	dataType: text              // String
	
column 'IntegerColumn'
	dataType: int64             // 64-bit integer
	
column 'DecimalColumn'
	dataType: double            // Floating-point number (use for currency, decimals)
	
column 'BooleanColumn'
	dataType: boolean           // True/False
	
column 'DateColumn'
	dataType: datetime          // Date and time (use for datetime fields)
	
column 'BinaryColumn'
	dataType: binary            // Binary data (images, files)
```

### 3.3 Data Categories

```tmdl
column 'GeographyColumn'
	dataCategory: City
	
column 'PercentageColumn'
	dataCategory: Percentage
	
column 'URLColumn'
	dataCategory: WebUrl
	
column 'EmailColumn'
	dataCategory: EmailAddress
	
column 'ImageColumn'
	dataCategory: ImageUrl
	
// Data categories affect Power BI's automatic features (maps, formatting, etc.)
```

### 3.4 Table Properties

```tmdl
table 'FactTable'
	lineageTag: 550e8400-e29b-41d4-a716-446655440000
	
	// Hide table from users (use for auxiliary/helper tables)
	isHidden: true
	
	// Enable refresh of data
	refreshPolicy: "Automatic"
	
	// Default summarization behavior
	defaultSummarization: none
	
	// Display folder (organizational)
	displayFolder: "Sales"
```

---

## SECTION 4: COLUMN TYPES & PROPERTIES

### 4.1 Source Columns (From Data Source)

```tmdl
column ClientType
	dataType: text
	lineageTag: 12345678-1234-1234-1234-123456789012
	sourceColumn: "ClientType"      // Maps directly to source
	dataCategory: "Uncategorized"
```

### 4.2 Calculated Columns (DAX Expression)

```tmdl
calculatedColumn 'IsNewClient' = 
	IF([DaysActive] < 30, "New", "Existing")
	lineageTag: 87654321-4321-4321-4321-210987654321
	displayFolder: "Flags"
```

### 4.3 Key Columns (Dimension/Fact Keys)

```tmdl
// Primary Key (dimension)
column ClientKey
	dataType: int64
	lineageTag: aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
	isKey: true                 // Mark as primary key
	isHidden: false             // Visible to users
	
// Foreign Key (fact table)
column 'Dim_Client[ClientKey]'
	dataType: int64
	lineageTag: bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb
	isForeignKey: true
	referencedTable: 'Dim_Client'
```

---

## SECTION 5: RELATIONSHIPS

### 5.1 Relationship Syntax

```tmdl
relationship 'Fact_Visit[EmployeeID]' to 'Dim_User[EmployeeID]'
	lineageTag: cccccccc-cccc-cccc-cccc-cccccccccccc
	fromCardinality: many
	toCardinality: one
	isActive: true              // Default relationship (used in DAX)
	relyOnReferentialIntegrity: false  // For performance
	crossFilteringBehavior: bothDirections  // How filters propagate
```

### 5.2 Cardinality Types

| Type | Meaning | Example |
|------|---------|---------|
| **many-to-one** | Multiple facts to one dimension | Many visits → One employee |
| **one-to-many** | One dimension to multiple facts | One date → Many visits |
| **one-to-one** | Unique mapping | One employee → One office |
| **many-to-many** | Complex relationships | (use bridge tables) |

### 5.3 CrossFilteringBehavior Options

```tmdl
// Single direction (most common)
crossFilteringBehavior: oneDirection    // Filters flow one way

// Bidirectional
crossFilteringBehavior: bothDirections  // Filters propagate both ways (slower)

// None
crossFilteringBehavior: none            // No automatic filtering
```

### 5.4 Real-World Example (BMD Sales)

```tmdl
// Main facts-to-dimensions relationships
relationship 'Fact_Visit[ClientKey]' to 'Dim_Client[ClientKey]'
	fromCardinality: many
	toCardinality: one
	isActive: true

relationship 'Fact_Visit[EmployeeID]' to 'Dim_User[EmployeeID]'
	fromCardinality: many
	toCardinality: one
	isActive: true

relationship 'Fact_Visit[DateKey]' to 'Dim_Date[DateKey]'
	fromCardinality: many
	toCardinality: one
	isActive: true
```

---

## SECTION 6: MEASURES & CALCULATED COLUMNS

### 6.1 Measure Definition Pattern

```tmdl
measure 'Total_Visits' =
	CALCULATE(
		COUNTROWS('Fact_Visit'),
		FILTER(ALL('Fact_Visit'), [IsActive] = TRUE)
	)
	lineageTag: dddddddd-dddd-dddd-dddd-dddddddddddd
	displayFolder: "Visit Metrics"
	formatString: "#,0"
	description: "Total number of active visits in selected context"
	isHidden: false
	
// Note: DAX expressions are embedded as text
```

### 6.2 Calculated Column Pattern

```tmdl
calculatedColumn 'Visit_Quality_Flag' =
	IF([PhotoCompliance] >= 0.9 && [FeedbackScore] >= 4, "HIGH", "LOW")
	lineageTag: eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee
	displayFolder: "Quality Metrics"
	dataType: text
```

### 6.3 Measure Best Practices

1. **Use explicit measure names** with underscores or camelCase
2. **Add displayFolder** to organize in UI
3. **Include formatString** for proper display (currency, percentage, etc.)
4. **Add description** for documentation
5. **Use CALCULATE** for complex filtering logic
6. **Avoid context row expansion** — minimize iteration

### 6.4 Calculated Column Cautions

⚠️ **Performance Impact**: Calculated columns are computed during refresh
- Use sparingly on large tables (1M+ rows)
- Consider measures instead (computed on-demand)
- Store as source data if queried frequently

---

## SECTION 7: HIERARCHIES & TIME INTELLIGENCE

### 7.1 Explicit Hierarchy Definition

```tmdl
hierarchy 'Territory_Hierarchy'
	levels: [Zone, Region, Area]
	lineageTag: ffffffff-ffff-ffff-ffff-ffffffffffff
	displayFolder: "Geography"

// Levels are ordered columns in the table
// Users can drill-down: Zone → Region → Area
```

### 7.2 Date Hierarchy (Time Intelligence)

```tmdl
table Dim_Date
	column Year
		dataType: int64
	column Quarter
		dataType: text
	column Month
		dataType: text
	column Day
		dataType: int64
	
	hierarchy 'Date_Hierarchy'
		levels: [Year, Quarter, Month, Day]
		displayFolder: "Time"

// Enables year-over-year, month-over-month calculations in Power BI
```

### 7.3 Time Intelligence DAX Functions

```dax
// Year-to-Date
YTD_Sales = CALCULATE(
	SUM([Sales]),
	DATESYTD(Dim_Date[Date])
)

// Previous month comparison
Prev_Month_Sales = CALCULATE(
	SUM([Sales]),
	DATEADD(Dim_Date[Date], -1, MONTH)
)

// Moving averages
Moving_Avg_3M = CALCULATE(
	AVERAGE([Sales]),
	DATESBETWEEN(
		Dim_Date[Date],
		EDATE(MAX(Dim_Date[Date]), -3),
		MAX(Dim_Date[Date])
	)
)
```

---

## SECTION 8: ANNOTATIONS & METADATA

### 8.1 Common Annotations

```tmdl
// Model-level annotations
annotation PBI_QueryOrder = ["table1", "table2", "table3"]
	// Define query evaluation order (useful for dependent queries)

annotation __PBI_TimeIntelligenceEnabled = 1
	// Enable Power BI's automatic time intelligence

annotation PBI_ProTooling = ["WebModelingEdit", "CalcGroup", "DaxQueryView_Desktop"]
	// Enable advanced tools in Power BI Desktop

// Table-level annotations
table 'TableName'
	annotation PBI_DisplayFolder = "Sales Data"
	annotation PBI_ViewerFolderName = "Sales"

// Column-level annotations
column ClientType
	annotation PBI_Format = "General"
	annotation PBI_DataCategory = "City"
```

### 8.2 Lineage Tags

```tmdl
// Every object gets a unique identifier for tracking changes
lineageTag: 550e8400-e29b-41d4-a716-446655440000

// Generated automatically by Power BI Desktop / Tabular Editor
// Useful for:
// - Version control (tracking which objects changed)
// - Refresh logic (knowing what to update)
// - Debugging (identifying specific object instances)
```

---

## SECTION 9: ROLE-LEVEL SECURITY (RLS)

### 9.1 RLS Role Definition

```tmdl
role 'BDO'
	description: "Business Development Officer"
	lineageTag: 11111111-1111-1111-1111-111111111111
	
	// Row-level filter
	tablePermission 'Fact_Visit'
		metadataPermission: read
		filterExpression = 'Dim_Client'[ResponsibleRole] = "BDO" || 'Dim_Client'[ResponsibleRole] = "CRO,BDO"

role 'CRO'
	description: "Commercial/Regional Officer"
	lineageTag: 22222222-2222-2222-2222-222222222222
	
	tablePermission 'Fact_Visit'
		metadataPermission: read
		filterExpression = 'Dim_Client'[ResponsibleRole] = "CRO" || 'Dim_Client'[ResponsibleRole] = "CRO,BDO"

role 'Manager'
	description: "Territory Manager (View All)"
	lineageTag: 33333333-3333-3333-3333-333333333333
	
	tablePermission 'Fact_Visit'
		metadataPermission: read
		// No filterExpression = unrestricted access
```

### 9.2 RLS Best Practices

1. **Filter at dimension level** — Apply RLS to Dim_Client, not Fact_Visit directly
2. **Use membership tables** — Link users to allowed dimensions
3. **Test role effectiveness** — Use Power BI "View as" feature
4. **Document role logic** — Add descriptions to each role
5. **Audit role changes** — Track who has access to what

---

## SECTION 10: BEST PRACTICES & PERFORMANCE

### 10.1 Naming Conventions

```tmdl
// Fact tables (uppercase prefix)
table 'Fact_Visit'
table 'Fact_Order'

// Dimension tables (uppercase prefix)
table 'Dim_Client'
table 'Dim_Date'
table 'Dim_User'

// Columns
column ClientType              // PascalCase or snake_case
column 'Is Active'             // Spaces allowed but avoided

// Measures
measure 'Total_Visits'         // Clear, descriptive
measure 'Visit_Count'
measure 'Avg_Visit_Duration'

// Hierarchies
hierarchy 'Territory_Hierarchy'
hierarchy 'Date_Hierarchy'

// Roles
role 'BDO'                      // All caps for acronyms
role 'Manager'
role 'Executive'
```

### 10.2 Performance Optimization

#### Technique 1: Summarization Tables

```tmdl
// Create pre-aggregated fact table for faster queries
table 'Fact_Visit_Summary'
	column Month, dataType: datetime
	column Zone, dataType: text
	column TotalVisits, dataType: int64
	column TotalQuality, dataType: double
	
	// Index this for quick lookups
	measure 'Visits_By_Month_Zone' = SUM([TotalVisits])
```

#### Technique 2: Hide Intermediate Columns

```tmdl
column 'InternalID'
	isHidden: true              // Don't show to users
	
column 'ClientKey'
	isHidden: false             // Show for linking
```

#### Technique 3: Reduce Calculated Columns

```dax
// ❌ AVOID: Calculated column on 1M row table
calculatedColumn 'Flag' = IF([Value] > 100, "High", "Low")

// ✅ PREFER: Measure (computed on-demand)
measure 'Count_High' = CALCULATE(COUNTROWS(Fact), [Value] > 100)
```

### 10.3 Partition Strategy (For Large Tables)

```tmdl
table 'Fact_Visit'
	// Multiple partitions for incremental refresh
	partition 'Fact_Visit_2024' = m
		mode: import
		source = Table.FromRows(...WHERE Year = 2024)
	
	partition 'Fact_Visit_2023' = m
		mode: import
		source = Table.FromRows(...WHERE Year = 2023)
```

---

## SECTION 11: BMD SALES CODEBASE INTEGRATION

### 11.1 Current BMD Sales TMDL Structure

**Location**: `/Users/agimac/Applications/powerbimcp/BMD_sales.SemanticModel/`

```
definition/
├── model.tmdl                          ← Main model definition
├── database.tmdl                       ← Compatibility: 1600 (Power BI Premium)
├── relationships.tmdl                 ← All relationships
└── tables/
    ├── Fact_Visit.tmdl                ← 36,041 visit records
    ├── Fact_Order.tmdl                ← Order analytics
    ├── Fact_ProjectConversion.tmdl    ← 60-day conversion window
    ├── Dim_Client_Simple.tmdl         ← Client dimensions (6 types)
    ├── Dim_Date.tmdl                  ← Calendar hierarchy
    ├── Dim_Territory.tmdl             ← Zone→Region→Area
    ├── Dim_User.tmdl                  ← Employees (272 records)
    ├── Dim_VisitCategory.tmdl         ← 9 visit categories
    ├── Dim_VisitPhase.tmdl            ← Visit lifecycle
    ├── Dim_VisitStage.tmdl            ← Visit stages
    ├── USER-ZONE.tmdl                 ← User-zone mapping bridge
    └── [LOCAL DATE TABLES]            ← Auto-generated by Power BI
```

### 11.2 Fact_Visit.tmdl Example Pattern

```tmdl
table 'Fact_Visit'
	lineageTag: 550e8400-e29b-41d4-a716-446655440000
	
	// Core columns
	column VisitID
		dataType: int64
		sourceColumn: "VisitID"
	
	column VisitDate
		dataType: datetime
		sourceColumn: "VisitDate"
		dataCategory: Date
	
	column EmployeeID
		dataType: int64
		sourceColumn: "EmployeeID"
	
	column ClientKey
		dataType: int64
		sourceColumn: "ClientKey"
	
	column VisitCategoryID
		dataType: int64
		sourceColumn: "VisitCategoryID"
	
	// Measures from /dax/visit_measures.dax
	measure 'Total_Visits' =
		CALCULATE(
			COUNTROWS('Fact_Visit'),
			FILTER(ALL('Fact_Visit'), [IsActive] = TRUE)
		)
		displayFolder: "Visit Analytics"
	
	measure 'Unique_Clients' =
		CALCULATE(
			DISTINCTCOUNT('Fact_Visit'[ClientKey])
		)
		displayFolder: "Visit Analytics"
	
	measure 'Visit_Quality_Score' =
		CALCULATE(
			AVERAGE('Fact_Visit'[QualityScore])
		)
		displayFolder: "Quality Metrics"
	
	// Calculated column example
	calculatedColumn 'IsHighQuality' =
		IF([QualityScore] >= 85, TRUE, FALSE)
		displayFolder: "Quality Flags"
	
	// Relationships to dimensions
	foreignKeyColumn 'Dim_Date[DateKey]'
	foreignKeyColumn 'Dim_User[EmployeeID]'
	foreignKeyColumn 'Dim_Client[ClientKey]'
	foreignKeyColumn 'Dim_VisitCategory[VisitCategoryID]'
	
	// Data source
	partition 'Fact_Visit' = m
		mode: import
		source = [M Query from Power Query]
```

### 11.3 Relationship Definitions (BMD Sales)

```tmdl
// From relationships.tmdl

relationship 'Fact_Visit[DateKey]' to 'Dim_Date[DateKey]'
	fromCardinality: many
	toCardinality: one
	isActive: true

relationship 'Fact_Visit[EmployeeID]' to 'Dim_User[EmployeeID]'
	fromCardinality: many
	toCardinality: one
	isActive: true

relationship 'Fact_Visit[ClientKey]' to 'Dim_Client_Simple[ClientKey]'
	fromCardinality: many
	toCardinality: one
	isActive: true

// Geography hierarchy relationships
relationship 'Dim_User[ZoneID]' to 'Dim_Territory[ZoneID]'
	fromCardinality: many
	toCardinality: one
	isActive: false  // Not primary

relationship 'USER-ZONE[EmployeeID]' to 'Dim_User[EmployeeID]'
	fromCardinality: many
	toCardinality: one
	isActive: true
```

### 11.4 Recommended TMDL Refactoring

1. **Consolidate DAX measures** into measure display folders
2. **Add descriptions** to all measures (for documentation)
3. **Standardize formatting strings** (currency, percentage)
4. **Document RLS roles** with complete filterExpression
5. **Create summary tables** for frequently aggregated metrics
6. **Archive LocalDateTable** entries (cleanup)

---

## APPENDIX A: TMDL GRAMMAR QUICK REFERENCE

```tmdl
database
	compatibilityLevel: <number>
	
model <ModelName>
	culture: <locale>
	sourceQueryCulture: <locale>
	discourageImplicitMeasures
	dataAccessOptions
		legacyRedirects
		returnErrorValuesAsNull
	
	annotation <AnnotationName> = <value>
	ref table <TableName>
	
	role <RoleName>
		lineageTag: <GUID>
		tablePermission <TableName>
			metadataPermission: read
			filterExpression = <DAX Expression>

table <TableName>
	lineageTag: <GUID>
	isHidden: <boolean>
	
	column <ColumnName>
		dataType: <DataType>
		lineageTag: <GUID>
		sourceColumn: "<SourceName>"
		isKey: <boolean>
		isHidden: <boolean>
		dataCategory: <Category>
	
	calculatedColumn <ColumnName> = <DAX Expression>
	
	partition <PartitionName> = m
		mode: import | directquery
		source = <M Expression>
	
	measure <MeasureName> = <DAX Expression>
		lineageTag: <GUID>
		displayFolder: "<FolderName>"
		formatString: "<Format>"
	
	hierarchy <HierarchyName>
		levels: [<Column1>, <Column2>, ...]
	
	foreignKeyColumn <ColumnName>

relationship <FromColumn> to <ToColumn>
	fromCardinality: many | one
	toCardinality: many | one
	isActive: <boolean>
	crossFilteringBehavior: oneDirection | bothDirections | none
	relyOnReferentialIntegrity: <boolean>
```

---

## APPENDIX B: USEFUL RESOURCES

- **Microsoft Learn**: https://learn.microsoft.com/en-us/power-bi/developer/embedded/semantic-model-programming-models
- **Power BI DAX Reference**: https://learn.microsoft.com/en-us/dax/dax-function-reference
- **Tabular Editor (TMDL IDE)**: https://tabulareditor.com/
- **DAX Studio (Optimization)**: https://www.daxstudio.org/
- **Power BI Best Practices**: https://learn.microsoft.com/en-us/power-bi/guidance/

---

**Document Complete**

