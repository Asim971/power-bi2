# Power BI Data Model - BMD Sales Cross-Role Visit Reporting

## Star Schema Overview

```
                                    ┌─────────────────┐
                                    │   Dim_Date      │
                                    │   (Date PK)     │
                                    └────────┬────────┘
                                             │
    ┌─────────────────┐              ┌───────┴───────┐              ┌─────────────────┐
    │  Dim_Client     │              │               │              │  Dim_User       │
    │  (ClientKey PK) │◄─────────────┤  Fact_Visit   ├─────────────►│  (UserID PK)    │
    └─────────────────┘              │               │              └────────┬────────┘
                                     └───────┬───────┘                       │
                                             │                               │
              ┌──────────────────────────────┼──────────────────────────────┐│
              │                              │                              ││
    ┌─────────┴─────────┐          ┌─────────┴─────────┐          ┌─────────┴┴────────┐
    │ Dim_VisitCategory │          │  Dim_VisitPhase   │          │  Dim_Territory    │
    │ (VisitCategoryID) │          │  (VisitPhaseID)   │          │  (AreaID PK)      │
    └───────────────────┘          └─────────┬─────────┘          └───────────────────┘
                                             │
                                   ┌─────────┴─────────┐
                                   │  Dim_VisitStage   │
                                   │  (VisitStageID)   │
                                   └───────────────────┘

                                    ┌─────────────────┐
                                    │   Dim_Date      │
                                    └────────┬────────┘
                                             │
    ┌─────────────────┐              ┌───────┴───────┐              ┌─────────────────┐
    │  Dim_Client     │◄─────────────┤  Fact_Order   ├─────────────►│  Dim_User       │
    │  (ClientKey PK) │              │               │              │  (UserID PK)    │
    └─────────────────┘              └───────────────┘              └─────────────────┘
```

---

## Table Definitions

### Fact Tables

#### Fact_Visit
| Column | Data Type | Description |
|--------|-----------|-------------|
| VisitID | Number | Primary Key - Unique visit identifier |
| DateKey | Text | Foreign Key to Dim_Date (format: YYYYMMDD) |
| EmployeeID | Number | Foreign Key to Dim_User.UserID |
| ClientKey | Text | Foreign Key to Dim_Client (composite: ClientType-ClientID) |
| ClientID | Number | Original client ID from source |
| ClientType | Text | Type of client (Site, Retailer, IHB, Dealer, Engineer, Contractor) |
| VisitCategoryID | Number | Foreign Key to Dim_VisitCategory |
| VisitPhaseID | Number | Foreign Key to Dim_VisitPhase |
| VisitStageID | Number | Foreign Key to Dim_VisitStage |
| ResponsibleRole | Text | Role name responsible for this visit |
| visit_type | Text | Type of visit |
| status | Text | Visit status |
| territory_id | Number | Territory ID where visit occurred |
| territory_name | Text | Territory name |
| RoleLevel | Number | Role hierarchy level of visiting employee |
| HasPhoto | Number | Flag: 1 = has photo, 0 = no photo |
| HasProductPhoto | Number | Flag: 1 = has product photo, 0 = no product photo |
| HasFeedback | Number | Flag: 1 = has feedback, 0 = no feedback |
| HasTerritory | Number | Flag: 1 = has territory, 0 = no territory |

**Source:** `#"public visits"` filtered by `delete_status = "NO"`

---

#### Fact_Order
| Column | Data Type | Description |
|--------|-----------|-------------|
| OrderID | Number | Primary Key - Unique order identifier |
| OrderDateKey | Text | Foreign Key to Dim_Date (format: YYYYMMDD) |
| UserID | Number | Foreign Key to Dim_User.UserID |
| ClientKey | Text | Foreign Key to Dim_Client (composite: ClientType-ClientID) |
| SiteID | Number | Site identifier |
| DealerID | Number | Dealer identifier |
| RetailerID | Number | Retailer identifier |
| BazaarID | Number | Bazaar identifier |
| OrderStatus | Text | Current order status |
| StatusGroup | Text | Grouped status category |
| OrderType | Text | Type of order |
| OrderCategory | Text | Order category |
| DeliveryMethod | Text | Delivery method used |
| Stage | Text | Order stage |
| TotalAmount | Number | Order total amount (converted from text) |
| IsConverted | Number | Flag: 1 = converted, 0 = not converted |
| HasMemoPhoto | Number | Flag: 1 = has memo photo, 0 = no memo photo |
| IsEngineerEligible | Boolean | True if engineer eligible for reward |
| IsPartnerEligible | Boolean | True if partner eligible for reward |

**Source:** `#"public user_orders"` joined with visits for UserID lookup

---

### Dimension Tables

#### Dim_Date
| Column | Data Type | Description |
|--------|-----------|-------------|
| DateKey | Text | Surrogate key (YYYYMMDD format) |
| Date | Date | **Primary Key** - Calendar date |
| Year | Number | Calendar year |
| Quarter | Number | Calendar quarter (1-4) |
| Month | Number | Calendar month (1-12) |
| MonthName | Text | Full month name |
| Day | Number | Day of month |
| DayOfWeek | Number | Day of week (1-7) |
| DayName | Text | Day name |
| WeekOfYear | Number | Week number in year |
| FiscalYear | Number | Fiscal year (July-June) |
| FiscalQuarter | Number | Fiscal quarter |
| FiscalMonth | Number | Fiscal month |
| IsToday | Number | Flag: 1 = today, 0 = not today |
| IsCurrentWeek | Number | Flag: 1 = current week |
| IsCurrentMonth | Number | Flag: 1 = current month |
| IsWeekend | Number | Flag: 1 = weekend day |
| IsHoliday | Number | Flag: 1 = holiday |

**Range:** 2023-01-01 to 2026-12-31  
**Fiscal Year:** July 1 - June 30

---

#### Dim_Client
| Column | Data Type | Description |
|--------|-----------|-------------|
| ClientKey | Text | **Primary Key** - Composite (ClientType + "-" + ClientID) |
| ClientID | Number | Original client ID from source |
| ClientName | Text | Client/business name |
| ClientType | Text | Client type (Site, Retailer, IHB, Dealer, Engineer, Contractor) |
| SubType | Text | Client sub-type classification |
| ClientCategory | Text | Client category |
| ResponsibleRole | Text | Role responsible for this client |
| ResponsibleRoleRLS | Text | Role for Row-Level Security filtering |
| BazaarID | Number | Associated bazaar identifier |
| TerritoryName | Text | Territory name |
| AreaName | Text | Area name |

**Client Types (6):**
- Site (from `potential_site`)
- Retailer (from `retailers`)
- IHB (from `ihb_registration`)
- Dealer (from `dealers`)
- Engineer (from `engineers`)
- Contractor (from `contractor`)

---

#### Dim_User
| Column | Data Type | Description |
|--------|-----------|-------------|
| UserID | Number | **Primary Key** |
| EmployeeID | Number | Employee ID (same as UserID, for FK compatibility) |
| EmployeeName | Text | Full name of employee |
| EmployeeEmail | Text | Email address |
| RoleID | Number | Role identifier |
| RoleName | Text | Role name |
| RoleLevel | Number | Role hierarchy level |
| RoleDesignation | Text | Role designation title |
| Department | Text | Department name |
| DepartmentTrack | Text | Computed: Corporate vs Field |
| RoleCategory | Text | Computed role category |
| ZoneID | Number | Zone identifier |
| RegionID | Number | Region identifier |
| AreaID | Number | Area identifier (FK to Dim_Territory) |
| BDTerritoryID | Number | BD Territory identifier |
| TerritoryID | Number | Territory identifier |
| IsFieldRole | Number | Flag: 1 = field role, 0 = corporate |
| ManagementLevel | Text | Management level classification |

**Source:** `#"public users"` joined with `#"public role"`, `users_territory`, `users_bd_territory`

---

#### Dim_Territory
| Column | Data Type | Description |
|--------|-----------|-------------|
| TerritoryKey | Text | Composite key (Zone-Region-Area) |
| AreaID | Number | **Primary Key** - Area identifier |
| AreaName | Text | Area name |
| RegionID | Number | Region identifier |
| RegionName | Text | Region name |
| ZoneID | Number | Zone identifier |
| ZoneName | Text | Zone name |
| AssignedZSM | Text | Assigned Zone Sales Manager |
| AssignedGM | Text | Assigned General Manager |
| AssignedAGM | Text | Assigned Assistant General Manager |
| AssignedASM | Text | Assigned Area Sales Manager |

**Hierarchy:** Zone → Region → Area  
**Source:** `#"public areas"` filtered by `delete_status = "NO"`

---

#### Dim_VisitCategory
| Column | Data Type | Description |
|--------|-----------|-------------|
| VisitCategoryID | Number | **Primary Key** |
| CategoryName | Text | Category display name |
| CategoryGroup | Text | Category grouping |
| IsInfluencer | Number | Flag: 1 = influencer category |

**Categories (9):**
- Potential Sites
- Dealer
- Retailer
- IHB
- Conversion Visit
- Head Mason
- Engineer
- Contractor
- Site Manager

**Source:** `#"public visit_categories"`

---

#### Dim_VisitPhase
| Column | Data Type | Description |
|--------|-----------|-------------|
| VisitPhaseID | Number | **Primary Key** |
| PhaseName | Text | Phase display name |
| PhaseDescription | Text | Phase description |
| PhaseSortOrder | Number | Sort order for display |

**Record Count:** 2 phases  
**Source:** `#"public visit_phases"`

---

#### Dim_VisitStage
| Column | Data Type | Description |
|--------|-----------|-------------|
| VisitStageID | Number | **Primary Key** |
| StageName | Text | Stage display name |
| StageDescription | Text | Stage description |
| VisitPhaseID | Number | Foreign Key to Dim_VisitPhase |
| ParentStageID | Number | Self-reference for stage hierarchy |
| StageCategory | Text | Stage category grouping |
| IsSubStage | Number | Flag: 1 = sub-stage |

**Record Count:** 78 stages  
**Source:** `#"public visit_stages"`

---

## Relationship Definitions

### Active Relationships

| # | From Table | From Column | To Table | To Column | Cardinality | Cross-Filter |
|---|------------|-------------|----------|-----------|-------------|--------------|
| 1 | Fact_Visit | DateKey | Dim_Date | DateKey | Many:1 | Single |
| 2 | Fact_Visit | EmployeeID | Dim_User | UserID | Many:1 | Single |
| 3 | Fact_Visit | ClientKey | Dim_Client | ClientKey | Many:1 | Single |
| 4 | Fact_Visit | VisitCategoryID | Dim_VisitCategory | VisitCategoryID | Many:1 | Single |
| 5 | Fact_Visit | VisitPhaseID | Dim_VisitPhase | VisitPhaseID | Many:1 | Single |
| 6 | Fact_Visit | VisitStageID | Dim_VisitStage | VisitStageID | Many:1 | Single |
| 7 | Fact_Order | OrderDateKey | Dim_Date | DateKey | Many:1 | Single |
| 8 | Fact_Order | UserID | Dim_User | UserID | Many:1 | Single |
| 9 | Fact_Order | ClientKey | Dim_Client | ClientKey | Many:1 | Single |
| 10 | Dim_User | AreaID | Dim_Territory | AreaID | Many:1 | Single |

### Inactive/Optional Relationships

| # | From Table | From Column | To Table | To Column | Cardinality | Notes |
|---|------------|-------------|----------|-----------|-------------|-------|
| 11 | Dim_VisitStage | VisitPhaseID | Dim_VisitPhase | VisitPhaseID | Many:1 | Snowflake - use USERELATIONSHIP() if needed |

### Relationship Notes

1. **Shared Dimensions:** `Dim_Date`, `Dim_Client`, and `Dim_User` are shared between `Fact_Visit` and `Fact_Order` fact tables
2. **Role-Playing Dimension:** `Dim_Date` serves as the date dimension for both visit dates and order dates
3. **Snowflake Pattern:** `Dim_VisitStage.VisitPhaseID → Dim_VisitPhase.VisitPhaseID` - This relationship is OPTIONAL. Since `Fact_Visit` already connects to both `Dim_VisitPhase` and `Dim_VisitStage` directly, the stage-to-phase relationship creates ambiguity. Keep it inactive or remove it.
4. **Primary Keys:** 
   - `Dim_VisitStage.VisitStageID` is the PK (unique)
   - `Dim_VisitStage.VisitPhaseID` is a FK (NOT unique - multiple stages per phase)

---

## Row-Level Security (RLS) Configuration

### Security Roles

| Role Name | Table | Filter Expression |
|-----------|-------|-------------------|
| ZSM | Dim_Territory | [ZoneName] = USERPRINCIPALNAME() |
| RSM | Dim_Territory | [RegionName] = USERPRINCIPALNAME() |
| ASM | Dim_Territory | [AreaName] = USERPRINCIPALNAME() |
| Field Role | Dim_Client | [ResponsibleRoleRLS] = USERPRINCIPALNAME() |

### RLS-Enabled Columns

- `Dim_Client.ResponsibleRoleRLS` - Used for client-level security
- `Fact_Visit.ResponsibleRole` - Used for visit-level filtering
- `Dim_User.RoleLevel` - Used for management hierarchy filtering

---

## Computed Columns & Flags Summary

### Quality Flags (Fact_Visit)
| Flag | Values | Usage |
|------|--------|-------|
| HasPhoto | 0/1 | Visit photo documentation compliance |
| HasProductPhoto | 0/1 | Product photo documentation compliance |
| HasFeedback | 0/1 | Feedback submission compliance |
| HasTerritory | 0/1 | Territory assignment tracking |

### Order Flags (Fact_Order)
| Flag | Values | Usage |
|------|--------|-------|
| IsConverted | 0/1 | Conversion tracking |
| HasMemoPhoto | 0/1 | Memo photo documentation |
| IsEngineerEligible | Boolean | Engineer reward eligibility |
| IsPartnerEligible | Boolean | Partner reward eligibility |

### User Computed Columns (Dim_User)
| Column | Logic |
|--------|-------|
| DepartmentTrack | Corporate vs Field classification |
| RoleCategory | Role grouping for analysis |
| IsFieldRole | 1 if field-based role, 0 if corporate |
| ManagementLevel | Management tier classification |

### Date Computed Columns (Dim_Date)
| Column | Logic |
|--------|-------|
| IsToday | Date = TODAY() |
| IsCurrentWeek | Current week flag |
| IsCurrentMonth | Current month flag |
| FiscalYear | July-June fiscal year |
| FiscalQuarter | Fiscal quarter (Q1 = Jul-Sep) |
| FiscalMonth | Fiscal month number (1 = July) |

---

## Additional Tables

### UserZoneMapping (Security Table)
Used for dynamic RLS based on user-zone assignments.

### Fact_ProjectConversion
Project conversion tracking fact table.

### Dim_Client_Complex
Extended client dimension with additional attributes.

---

## Data Refresh Schedule

| Table Type | Refresh Frequency | Notes |
|------------|-------------------|-------|
| Fact Tables | Daily | Incremental refresh recommended |
| Dim_Date | Static | Pre-generated 2023-2026 |
| Dim_Client | Daily | Client master data |
| Dim_User | Daily | Employee/role changes |
| Dim_Territory | Weekly | Territory structure changes |
| Dim_VisitCategory | Monthly | Category definitions |
| Dim_VisitPhase | Monthly | Phase definitions |
| Dim_VisitStage | Monthly | Stage definitions |

---

## Database Connection

- **Server:** 172.17.19.21
- **Database:** bmdsalesdb
- **Type:** PostgreSQL
- **Power BI Dataset ID:** 3477f170-bf61-42a4-b7a6-4414d7bf8881
