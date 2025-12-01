# BMD Sales Report - Power BI Implementation Guide

## Overview

This folder contains the complete Power BI report definition for the **BMD Sales Cross-Role Visit Reporting** system with 6 pages:

1. **Executive Command Center** - Real-time KPIs, AI insights for Leadership/NSM
2. **Territory Intelligence** - Zone→Region→Area hierarchy with interactive map
3. **Quality Scorecard** - Photo/GPS/Feedback rates with gamified leaderboards
4. **Conversion Journey** - 60-day Site→Order tracking funnel
5. **Order Analytics** - Factory DN vs General Delivery tracking
6. **My Performance Hub** - Role-personalized dashboard for BDO/CRO/SR

## Files Structure

```
BMDSalesReport.pbip                    # Power BI Project file
BMDSalesReport.Report/
├── .platform                          # Fabric platform metadata
├── definition/
│   ├── report.json                    # Main report configuration
│   └── pages/
│       ├── ExecutiveCommandCenter.json
│       ├── TerritoryIntelligence.json
│       ├── QualityScorecard.json
│       ├── ConversionFunnel.json
│       ├── OrderAnalytics.json
│       └── MyPerformance.json
└── StaticResources/
    └── SharedResources/
        └── BaseThemes/
            └── BMDSalesTheme.json     # Custom theme with BMD colors
```

## Option 1: Connect Workspace to Git (Recommended)

The easiest way to deploy these report definitions is through **Fabric Git Integration**:

### Prerequisites
- Azure DevOps or GitHub repository
- Fabric Admin enabled Git integration in tenant settings
- Workspace Admin permissions

### Steps

1. **Create Git Repository**
   ```bash
   # Initialize a new repo or use existing
   git init bmd-sales-fabric
   cd bmd-sales-fabric
   ```

2. **Copy Report Files**
   ```bash
   # Copy the BMDSalesReport.Report folder to your repo
   cp -r /path/to/BMDSalesReport.Report ./
   ```

3. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add BMD Sales Report definition"
   git push origin main
   ```

4. **Connect Workspace to Git**
   - Open Power BI Service → Workspace → Settings → Git integration
   - Connect to your Azure DevOps/GitHub repo
   - Select the branch and folder containing the report
   - Click "Connect and sync"

5. **Update from Git**
   - Once connected, click "Update all" to pull the report definition
   - The report will be created/updated in the workspace

## Option 2: Power BI Desktop Manual Build

If Git integration isn't available, build the report manually in Power BI Desktop:

### Step 1: Create New Report

1. Open Power BI Desktop
2. Connect to the existing dataset:
   - **Power BI Service** → Get Data → Power BI datasets
   - Select workspace: `BMD_Sales`
   - Select dataset: `BMD_Sales` (ID: 3477f170-bf61-42a4-b7a6-4414d7bf8881)

### Step 2: Apply Theme

1. View → Themes → Browse for themes
2. Select `BMDSalesTheme.json` from the StaticResources folder

### Step 3: Create Pages

Create 6 pages with the following names:
- Executive Command Center
- Territory Intelligence
- Quality Scorecard
- Conversion Journey
- Order Analytics
- My Performance Hub

### Step 4: Add Visuals (Per Page)

Refer to the page JSON files for exact visual specifications. Key visual types:

| Page | Visuals |
|------|---------|
| Executive Command Center | 5 KPI Cards, Line Chart, Filled Map, Donut, Bar Chart, Funnel, 3 Slicers |
| Territory Intelligence | Filled Map, Matrix/Table, 3 Slicers |
| Quality Scorecard | 3 Gauge Charts, Clustered Bar, Table, Line Chart, 3 Slicers |
| Conversion Funnel | 7 KPI Cards, Funnel Chart, Clustered Bar, Column Chart, 3 Slicers |
| Order Analytics | 7 KPI Cards, Area Chart, Donut, Clustered Bar, Multi-row Card, Table, 4 Slicers |
| My Performance Hub | 6 KPI Cards, Donut, Line Chart, Multi-row Card, Clustered Bar |

### Step 5: Publish

1. File → Publish → Publish to Power BI
2. Select workspace: `BMD_Sales`
3. Replace existing report or create new

## Option 3: REST API Clone from Template

If you have an existing template report, use the UpdateReportContent API:

```bash
# Get access token
TOKEN=$(az account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv)

# Clone report content from template
curl -X POST "https://api.powerbi.com/v1.0/myorg/groups/276a43e7-e0e3-4366-9ac1-40d1bf52182f/reports/dcd4d7a3-e911-49e1-847a-1feb594f1616/UpdateReportContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sourceReport": {
      "sourceReportId": "<TEMPLATE_REPORT_ID>",
      "sourceWorkspaceId": "<TEMPLATE_WORKSPACE_ID>"
    },
    "sourceType": "ExistingReport"
  }'
```

## Required DAX Measures

Ensure these measures exist in your semantic model (from `dax/*.dax` files):

### Visit Measures
- `[Total Visits]`
- `[Site Visits]`
- `[Engineer Visits]`
- `[Contractor Visits]`
- `[Conversion Rate 60D %]`
- `[Visit Quality Score]`
- `[Photo Capture %]`
- `[GPS Capture %]`
- `[Feedback Rate %]`
- `[Target Achievement %]`

### Order Measures
- `[Total Orders]`
- `[Total Order Amount]`
- `[Avg Order Value]`
- `[Factory DN Orders]`
- `[General Delivery Orders]`
- `[Completed Orders]`
- `[Order Complete Rate]`
- `[Engineer Reward Eligible Orders]`
- `[Partner Reward Eligible Orders]`
- `[Engineer Eligible %]`
- `[Partner Eligible %]`

### Conversion Measures
- `[Total Conversions]`
- `[Avg Days to Convert]`
- `[Both Eligible Orders]`

## Color Reference

| Purpose | Hex Code | Usage |
|---------|----------|-------|
| Primary Brand | #0066CC | Headers, primary actions |
| Positive/Good | #2ECC71 | Targets met, growth |
| Warning | #F39C12 | Approaching threshold |
| Negative/Alert | #E74C3C | Below target, errors |
| Site | #1ABC9C | Site visits/orders |
| Engineer | #3498DB | Engineer visits (BDO) |
| Contractor | #9B59B6 | Contractor visits (CRO) |
| Dealer | #E67E22 | Dealer visits |
| Retailer | #E91E63 | Retailer visits (SR) |
| Factory DN | #2C3E50 | Retail Delivery orders |
| General Delivery | #8E44AD | General Delivery orders |

## Workspace Details

| Property | Value |
|----------|-------|
| Workspace ID | 276a43e7-e0e3-4366-9ac1-40d1bf52182f |
| Dataset ID | 3477f170-bf61-42a4-b7a6-4414d7bf8881 |
| Report ID | dcd4d7a3-e911-49e1-847a-1feb594f1616 |
| Capacity | Premium (3854b89a-448f-4097-b61e-88d984d9e5c4) |

## Troubleshooting

### Report won't load
- Verify dataset ID matches the connected semantic model
- Check that all referenced measures exist
- Ensure user has Build permission on the dataset

### Visuals show errors
- Verify table and column names match exactly
- Check measure syntax in DAX files
- Confirm relationships are set up correctly

### Theme not applying
- Re-import the theme JSON file
- Check for JSON syntax errors
- Apply theme to report, not just visuals

## Next Steps

1. ✅ Connect workspace to Git
2. ✅ Pull report definition from Git
3. ⬜ Test all 6 pages load correctly
4. ⬜ Verify RLS filtering on My Performance page
5. ⬜ Configure mobile layout
6. ⬜ Set up scheduled refresh

---

**Created:** December 2025  
**Version:** 1.0  
**Author:** Power BI Report Authoring Tool
