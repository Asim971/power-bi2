# Power BI Report Build Guide

## BMD Sales - Cross-Role Visit Reporting

This document provides step-by-step instructions to build the Power BI report using different methods.

---

## Quick Start Options

| Method | Difficulty | Requirements | Best For |
|--------|------------|--------------|----------|
| 🖥️ **Power BI Desktop** | Easy | Windows + PBI Desktop | Visual building, most control |
| 🐍 **Python API** | Medium | Python + Azure CLI | Automation, testing |
| 📁 **PBIR Format** | Advanced | Power BI Desktop (Preview) | DevOps, version control |

---

## Method 1: Power BI Desktop (Recommended)

### Step 1: Connect to Semantic Model

1. Open **Power BI Desktop**
2. Click **Home** → **Get Data** → **Power BI datasets**
3. Sign in with your Azure AD account
4. Select the dataset: `3477f170-bf61-42a4-b7a6-4414d7bf8881`
5. Click **Connect**

### Step 2: Import Theme

1. Click **View** → **Themes** → **Browse for themes**
2. Navigate to: `/powerbimcp/themes/BMD_Sales_Theme.json`
3. Click **Open**

### Step 3: Create Pages

Create these 6 pages in order:

#### Page 1: Executive Command Center
**Add these visuals:**

| Visual | Type | Position | Data |
|--------|------|----------|------|
| Header | Text Box | Top | "🏭 BMD SALES \| EXECUTIVE COMMAND CENTER" |
| AI Insight | Text Box | Below header | Dynamic insight text |
| KPI 1 | Card (New) | Top row | `[Total Visits]` + sparkline |
| KPI 2 | Card (New) | Top row | `[Total Orders]` + sparkline |
| KPI 3 | Card (New) | Top row | `[Total Conversions]` + sparkline |
| KPI 4 | KPI | Top row | `[Conversion Rate 60D %]` vs 5% target |
| KPI 5 | Card (New) | Top row | `[Order Amount YTD]` ৳ format |
| Performance Chart | Line Chart | Middle left | X: Date, Y: Visits/Orders/Target |
| Zone Heatmap | Filled Map | Middle right | Zone, Conversion Rate color |
| Client Mix | Donut Chart | Bottom left | ClientType, Total Visits |
| Role Performance | Clustered Bar | Bottom middle | Role, Target Achievement % |
| Quick Funnel | Funnel | Bottom right | Site→Conversion→Order→Delivered |

**Slicers:** Date (Relative), Zone, Role, Client Type

#### Page 2: Territory Intelligence
- Interactive map with drill-down: Zone → Region → Area → ASM
- Matrix table with expandable hierarchy
- Conditional formatting: 🟢 ≥5.5% | 🟡 4-5.5% | 🔴 <4%

#### Page 3: Quality Scorecard  
- 3 Gauge visuals: Photo Rate (70% target), GPS Rate (80% target), Feedback Rate (75% target)
- Quality by Client Type stacked bar
- Top Performers / Needs Improvement leaderboard
- 6-month quality trend line chart

#### Page 4: Conversion Funnel ⭐
- 7 KPI cards across top
- Large vertical funnel: Site Visits → Project Conversions → Orders → Delivered
- Reward Eligibility stacked bar (Engineer/Partner/Both)
- Delivery Method comparison (Factory DN vs General Delivery)
- Days-to-Conversion histogram with 60-day reference line
- Timeline trend chart

#### Page 5: Order Analytics ⭐
- 7 KPI cards: Orders, Total Amount, Avg Order, Factory DN, General, Engineer %, Partner %
- Stacked area: Order trend by delivery method
- Donut: Order status distribution
- Clustered bar: Order amount by Zone
- Reward dashboard cards
- Detail table with export

#### Page 6: My Performance Hub ⭐ (RLS-enabled)
- Dynamic header with role badge
- Role-specific KPI sections (BDO/CRO/SR)
- Bullet chart: Performance vs Target vs Team Average
- Gamification badges

### Step 4: Configure Interactions

1. Select the **Zone Heatmap** on Page 1
2. Click **Format** → **Edit Interactions**
3. Set **Filter** for: Performance Chart, Client Mix, Role Performance, Funnel
4. Repeat for other key visuals

### Step 5: Set Up Drill-Through

1. Create drill-through page for **Order Details**
2. Add drill-through fields: `OrderID`, `ClientKey`, `ZoneName`
3. Enable "Keep all filters"

### Step 6: Configure RLS

Go to **Modeling** → **Manage Roles**:

```dax
// BDO Role
Dim_Client[ResponsibleRoleRLS] IN {"BDO", "CRO,BDO"}

// CRO Role  
Dim_Client[ResponsibleRoleRLS] IN {"CRO", "CRO,BDO"}

// SR Role
Dim_Client[ResponsibleRoleRLS] = "SR"
```

### Step 7: Publish

1. Click **File** → **Publish** → **Publish to Power BI**
2. Select your workspace
3. Wait for upload to complete
4. Click **Open in Power BI** to verify

---

## Method 2: Python REST API

### Prerequisites

```bash
# Install requirements
pip install requests azure-cli

# Login to Azure
az login

# Verify access
az account get-access-token --resource https://analysis.windows.net/powerbi/api
```

### Execute DAX Queries

```bash
cd /Users/agimac/Applications/powerbimcp

# List workspaces
python scripts/powerbi_report_builder.py workspaces

# List datasets
python scripts/powerbi_report_builder.py datasets

# Execute sample query
python scripts/powerbi_report_builder.py dax --preset total_visits

# Custom query
python scripts/powerbi_report_builder.py dax --query "EVALUATE SUMMARIZECOLUMNS(Dim_Territory[ZoneName], \"Visits\", COUNTROWS(Fact_Visit))"
```

### Clone Existing Report

```python
from scripts.powerbi_report_builder import clone_report

# Clone a template report to new name
result = clone_report(
    source_report_id="<template-report-id>",
    target_name="BMD Sales Cross-Role Visit Report",
    target_workspace_id="<workspace-id>",
    target_dataset_id="3477f170-bf61-42a4-b7a6-4414d7bf8881"
)
print(f"New report ID: {result.get('id')}")
```

### Import PBIX File

```python
from scripts.powerbi_report_builder import import_pbix

# Upload a .pbix file
result = import_pbix(
    file_path="./exports/BMD_Sales_Report.pbix",
    report_name="BMD Sales Cross-Role Visit Report",
    workspace_id="<workspace-id>"
)
```

---

## Method 3: PBIR Format (Developer Preview)

### Enable PBIR in Power BI Desktop

1. Open **Power BI Desktop**
2. Go to **File** → **Options and settings** → **Options**
3. Navigate to **Preview features**
4. Enable **"Power BI Project (.pbip) save option"**
5. Restart Power BI Desktop

### Use Generated PBIR Files

The PBIR files in `/powerbimcp/pbir/` define the report structure:

```
pbir/
├── report.json              # Main report definition
├── pages/
│   ├── 01_Executive_Command_Center.json
│   ├── 04_Conversion_Funnel.json
│   └── 06_My_Performance_Hub.json
```

### Build from PBIR

1. Create a new folder for your project
2. Copy the PBIR structure
3. Open as Power BI Project in Desktop
4. Modify and save changes
5. Publish to workspace

---

## Validation Checklist

Before publishing, verify:

- [ ] All 6 pages created
- [ ] Theme applied consistently
- [ ] All DAX measures display correctly
- [ ] Slicers filter all visuals
- [ ] Drill-through navigation works
- [ ] RLS filtering by role
- [ ] Mobile layout configured
- [ ] Bookmarks for navigation
- [ ] Export to PDF working
- [ ] Conditional formatting applied

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Column not found" | Check PowerQuery column names match DAX references |
| RLS not filtering | Verify user email in role membership |
| Slow performance | Add aggregations, reduce visual count |
| Map not rendering | Ensure location hierarchy configured |
| Theme not applying | Reimport theme JSON file |

### Performance Tips

1. Limit visuals to 7 per page
2. Use Import mode (not DirectQuery) where possible
3. Add date hierarchy to Dim_Date
4. Create calculation groups for common patterns
5. Enable automatic aggregations

---

## Support

- **Dataset ID**: `3477f170-bf61-42a4-b7a6-4414d7bf8881`
- **API Docs**: https://learn.microsoft.com/en-us/rest/api/power-bi/
- **Theme Docs**: https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-themes
- **PBIR Docs**: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview

---

## File Reference

| File | Purpose |
|------|---------|
| `/themes/BMD_Sales_Theme.json` | Color palette, fonts, visual styles |
| `/scripts/powerbi_report_builder.py` | Python API utilities |
| `/pbir/report.json` | PBIR report definition |
| `/pbir/pages/*.json` | PBIR page definitions |
| `/dax/*.dax` | DAX measure definitions |
| `/docs/report_design.md` | Visual layout specifications |

