# Functional Requirements Document

**Project**: BMD Sales Eco System – Visit Performance Dashboards  
**Version**: 1.0  
**Date**: TBD

## 1. Purpose

The purpose of this FRD is to define the functional requirements for three Visit Performance Dashboards within the BMD Sales Eco System:

- Clients Dashboard
- Influencers Dashboard
- Customers Dashboard

Each dashboard will provide a consistent, visual summary of visit activity and performance KPIs, filtered by time, geography, company, and employees.

## 2. Scope

### 2.1 In Scope

- Design and implementation of three dashboards sharing the same layout, components, and behaviour.
- Aggregation and visualization of visit data captured from mobile / web forms.
- Global filters for:
  - Date range (Daily, WTD, MTD, YTD)
  - Location (Area, Zone, Territory)
  - Company (ACL, AIL)
  - Employee name
- KPI tiles and charts as per the wireframe.
- Role-based access to data (row-level security).
- Basic drill-down capability from charts to tabular detail (where specified).

### 2.2 Out of Scope

- Creation or modification of visit-capture forms.
- Data entry UI for master data (employees, locations, entities).
- Advanced analytics (predictions, AI-based insights) beyond defined KPIs.
- Complex custom date ranges (unless added later as an enhancement).

## 3. Users and Roles

### 3.1 Primary User Roles

- Sales Representatives / Field Staff (SR/CRO/BDO, etc.)
- Area Sales Managers (ASM)
- Regional / Zonal Managers (RSM/ZSM)
- Head Office / Sales Leadership
- MIS / Analytics Team

### 3.2 Access Behaviour

- **FR-1**: An SR/CRO/BDO must see only their own visit data.
- **FR-2**: An ASM must see visit data for all direct and indirect reportees within their territory/area.
- **FR-3**: RSM, ZSM, and Head Office must see data for all employees within their defined span (region/zone/national).
- **FR-4**: The MIS / Analytics team may be granted unrestricted access for audit and analysis.

Row-level security will be implemented based on the reporting hierarchy stored in the employee master.

## 4. Dashboard Overview

### 4.1 Dashboards

- **Clients Dashboard**: Includes visit data tagged to Dealers and Retailers.
- **Influencers Dashboard**: Includes visit data tagged to Engineers, Masons, Other Influencers.
- **Customers Dashboard**: Includes visit data tagged to Sites and IHB.

### 4.2 Layout (Common to All Dashboards)

From top to bottom:

1. Global Filter Bar
2. KPI Tiles
3. Charts section:
   - Visit Trend (line chart)
   - MoM Comparison (bar chart)
   - Visit by Location (horizontal bar chart)
   - Top 10 Performers (funnel / ranking chart)
   - Additional Location Breakdown Chart (vertical bar chart)
   - Bottom 10 Performers (inverted funnel / ranking chart)

## 5. Data Requirements

### 5.1 Source Data – Visit Fact

Each visit record must contain at least:

- Visit ID
- Visit Date & Time
- Employee ID
- Employee Designation
- Company Code (ACL / AIL)
- Location Hierarchy:
  - Territory
  - Zone
  - Area




Entity Type (Dealer, Retailer, Engineer, Mason, Other Influencer, Site, IHB, etc.)


Entity ID (Dealer ID, Influencer ID, Site ID, etc.)


Any additional attributes required for drill-down (e.g., visit purpose).


5.2 Master Data


Employee Master


Employee ID, Name, Designation


Reporting manager


Location assignment / role




Location Master


Territory, Zone, Area codes and names


Hierarchical relationships




Entity Masters


Clients (Dealers/Retailers)


Influencers (Engineers/Masons/Others)


Customers (Sites, IHB)


Attributes: ID, Name, Type, Address, etc.




5.3 Data Refresh


FR-5: Dashboards must update with new data according to a defined data refresh schedule (minimum once per day; configurable).


FR-6: Last data refresh timestamp must be visible somewhere on the dashboard.



6. Global Filters (Functional Requirements)
All global filters apply to every KPI and chart on the active dashboard.
6.1 Date Filter


Control: Radio buttons (Daily, WTD, MTD, YTD).


FR-7: Exactly one option must be selected at any time.


FR-8: Default selection is configurable (proposed: MTD).


FR-9: Definitions:


Daily: Single calendar date (default = current date).


WTD: From the start of the current week (Monday) to current date.


MTD: From the 1st day of the current calendar month to current date.


YTD: From the start of the current financial year to current date.




FR-10: For Daily view, where charts require multiple time points (e.g., Visit Trend), system may show intra-day buckets (hourly) or fallback to last N days as per design decision.


6.2 Location Filter


Control: Radio buttons for Location Level + dynamic dropdown for values.


FR-11: Location level options: Area, Zone, Territory.


FR-12: When a level is selected, the values dropdown must list all locations of that level visible to the logged-in user’s access region.


FR-13: User can select one or more locations (multi-select).


FR-14: Default behaviour: “All locations” for the chosen level.


FR-15: All metrics and charts aggregate data for the selected locations only.


6.3 Company Filter


Control: Checkboxes ACL, AIL.


FR-16: Both companies are selected by default.


FR-17: User may select one or both. At least one must always be selected.


FR-18: All metrics and charts must be filtered only to visits belonging to selected companies.


6.4 Employee Filter


Control: Dropdown (multi-select) with search.


FR-19: Default value = “All Employees” within user’s access scope.


FR-20: Dropdown must list employees who have at least one visit in the data (or from employee master if you prefer).


FR-21: When one or more employees are selected, all metrics and charts must be restricted to visits done by these employees only.


6.5 Entity-Type Context per Dashboard


FR-22: Each dashboard automatically filters data to relevant entity types:


Clients: Dealer, Retailer


Influencers: Engineer, Mason, Other Influencer


Customers: Site, IHB




FR-23 (Optional): Each dashboard may include an internal toggle to further filter within its category (e.g., Dealer vs Retailer).



7. KPI Tiles
7.1 Total Visit


Label: “Total Visit”.


FR-24: Display a single numeric value.


FR-25: Calculation:

Total visits = Count of visit records satisfying all active filters (date, location, company, employee, dashboard-specific entity type).



FR-26: Value should be formatted with thousand separators.


7.2 Average Visit


Label: “Average Visit”.


FR-27: Display a single numeric value.


FR-28: Calculation (chosen definition – can be adjusted, but must be documented):

Average Visit = (Total visits) / (Number of unique employees with at least one visit in the filtered period).



FR-29: If denominator is zero (no employees with visits), display 0 or “–” and avoid division error.


FR-30: Rounding rules: round to nearest integer (or 1 decimal place – to be finalised).



8. Charts (Functional Requirements)
8.1 Visit Trend (Line Chart)


Title: “Visit Trend”.


FR-31: Type – multi-series line chart.


FR-32: X-axis represents time buckets:


For WTD / MTD / YTD: Month or Week (to be finalised; default: Month for >30 days).




FR-33: Y-axis represents number of visits.


FR-34: Each series represents Employee Designation (e.g., CE, SE, HN, etc.), or other agreed dimension.


FR-35: For each time bucket, system sums visits for that designation under current filters.


FR-36: Chart must include a legend, allowing users to show/hide individual series.


FR-37: Hover tooltip must display: Time bucket, Designation, Visit count.


8.2 Month-on-Month (MoM) Comparison (Bar Chart)


Title: “MoM”.


FR-38: Type – clustered vertical bar chart.


FR-39: X-axis: locations at the chosen level (Area / Zone / Territory).


FR-40: Y-axis: total number of visits.


FR-41: For each location, two bars must be shown:


Previous calendar month visits.


Current calendar month visits.




FR-42: All other filters (company, employee, entity type) apply to both months.


FR-43: Tooltip must display: Location, Month, Visit count.


FR-44: Optional: visual demarcation (e.g., vertical dashed separator) between months as per wireframe.


8.3 Visit by Location (Horizontal Bar Chart)


Title: “Visit (Location)”.


FR-45: Type – horizontal bar chart.


FR-46: Y-axis: locations (of selected level).


FR-47: X-axis: total number of visits in filtered period.


FR-48: Bars must be sorted in descending order of visit count.


FR-49: If number of locations exceeds a defined threshold (e.g., 10), chart must support scroll or show top N with option to expand.


8.4 Top 10 Performers (Funnel / Ranking Chart)


Title: “Top 10 Performers”.


FR-50: Display a ranking of top 10 employees based on visit count for the selected filters.


FR-51: Each funnel layer (or bar) corresponds to one employee.


FR-52: For each employee, display:


Employee Name


Optional: Designation / Location


Visit count




FR-53: Ranking must be sorted in descending order of visit count.


FR-54: If fewer than 10 employees are available, show only available employees.


FR-55: Clicking an employee (if implemented) should open a detail view listing that employee’s visits within the filter context.


8.5 Additional Location Breakdown Chart (Vertical Bar)


Working Title: “Visit Distribution (Sub-location)” (final business label to be decided).


FR-56: Type – vertical bar chart.


FR-57: X-axis: sub-locations or groups (e.g., A1, A2, A3, A4).


FR-58: Y-axis: total number of visits.


FR-59: This chart provides finer-grain distribution than “Visit (Location)” and should be aligned with business-decided hierarchy (e.g., areas within zone, or territories within area).


FR-60: Sorting and tooltip behaviour similar to other location charts.


(If instead used as Actual vs Target visits by location, the FRs will be updated to include two series: Target, Actual.)
8.6 Bottom 10 Performers (Inverted Funnel / Ranking Chart)


Title: “Bottom 10 Performers”.


FR-61: Display a ranking of bottom 10 employees based on visit count.


FR-62: Each funnel layer (or bar) corresponds to one employee.


FR-63: Ranking sorted in ascending order of visit count.


FR-64: Business decision required: whether to:


Include employees with zero visits, or


Include only employees with at least one visit.
The chosen rule must be consistently applied and documented.




FR-65: Tooltip and optional drill-down behaviour same as Top 10 chart.



9. Per-Dashboard Specific Requirements
9.1 Clients Dashboard


FR-66: Data restricted to visits whose entity type is Dealer or Retailer.


FR-67: (Optional) Include an internal filter:


Entity Type: Dealer, Retailer, Both.




FR-68: Any drill-down views must show:


Client ID, Client Name, Client Type (Dealer/Retailer), Location, Visit Date, Employee, and any other relevant fields.




9.2 Influencers Dashboard


FR-69: Data restricted to visits whose entity type is Engineer, Mason, or Other Influencer.


FR-70: (Optional) Internal filter: Influencer Type (Engineer / Mason / Other).


FR-71: Drill-down records must show:


Influencer ID & Name, Type, Location, Visit Date, Employee, etc.




9.3 Customers Dashboard


FR-72: Data restricted to visits whose entity type is Site or IHB.


FR-73: (Optional) Internal filter: Entity Type (Site / IHB / Both).


FR-74: Drill-down records must show:


Site/IHB ID, Name/Project, Location, Visit Date, Employee, and relevant project attributes.





10. Drill-down and Export


FR-75: From ranking charts (Top 10 / Bottom 10 / Visit by Location), user should be able to click on a bar/layer to open a detail table.


FR-76: The detail table must inherit all active filters and additionally filter by the clicked dimension (employee or location).


FR-77: Detail table columns should include at minimum:


Visit Date


Employee Name & ID


Entity Name & Type


Location


Company


Visit ID (for technical reference)




FR-78: Provide an Export to Excel/CSV option for the detail table (if supported by the BI platform).



11. Non-Functional Requirements
11.1 Performance


FR-79: Dashboard initial load time should not exceed X seconds for typical usage (business to specify; recommended ≤ 10 seconds).


FR-80: Filter changes should refresh visuals within Y seconds (recommended ≤ 5 seconds).


11.2 Usability


FR-81: All filters and chart titles must be clearly labelled and consistent across dashboards.


FR-82: The date and filter context must be visible at all times.


FR-83: Tooltips should be concise and informative.


FR-84: Number formats should be localised (thousand separators, no unnecessary decimals).


11.3 Security


FR-85: Implement authentication integrated with the main BMD Sales Eco System.


FR-86: Implement row-level security as described in Section 3.2.


FR-87: Audit logs for data access may be maintained as per organisational policy.


11.4 Reliability


FR-88: Dashboard must handle scenarios of missing or partial data gracefully (show “No data available” where applicable).


FR-89: On data refresh failure, display last successful refresh date/time and a warning message to MIS team (if feasible).



12. Assumptions and Open Points


A1: The underlying data model (fact tables and dimension tables) will be designed or adjusted to support the required aggregations.


A2: Employee hierarchy, location hierarchy, and entity master data are maintained and accurate.


A3: Financial year start month for YTD is agreed (e.g., April).


OP1: Final choice of time granularity for Visit Trend (Month vs Week).


OP2: Exact behaviour and metric for the “Additional Location Breakdown” chart (pure visits vs target comparison).


OP3: Decision regarding inclusion of zero-visit employees in Bottom 10 Performers.



If you want, I can now:


Add a data model section (fact/dimension tables & sample columns), or


Convert this FRD into a formatted Word/PowerPoint/Confluence-ready template with numbering and table of contents.

