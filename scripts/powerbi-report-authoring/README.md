# Power BI Report Building Guide

## 🚀 Quick Start

### Option 1: Interactive HTML Report Creator (Recommended)

1. **Get Access Token:**
   ```bash
   az account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv
   ```

2. **Open the Report Creator:**
   ```bash
   cd /Users/agimac/Applications/powerbimcp/scripts/powerbi-report-authoring
   open bmd-report-creator.html
   ```

3. **In the Browser:**
   - Paste the access token in the "Access Token" field
   - Click "Edit Existing Report" to modify the existing BMD Sales Report
   - OR Click "Create New Report" to start fresh
   - Use the Pages tab to build all 6 pages
   - Use the Visuals tab to add individual visuals

### Option 2: Command Line CLI

```bash
cd /Users/agimac/Applications/powerbimcp/scripts/powerbi-report-authoring

# List workspaces
node report-builder-cli.js workspaces

# List datasets
node report-builder-cli.js datasets 276a43e7-e0e3-4366-9ac1-40d1bf52182f

# List reports
node report-builder-cli.js reports 276a43e7-e0e3-4366-9ac1-40d1bf52182f

# View report design specification
node report-builder-cli.js design

# Show visual creation API guide
node report-builder-cli.js instructions
```

---

## 📊 Report Structure

| Page | Name | Key Visuals |
|------|------|-------------|
| 1 | Executive Command Center | 5 KPI Cards, Line Chart, Map, Donut, Bar, Funnel |
| 2 | Territory Intelligence | Interactive Map, Matrix (hierarchical) |
| 3 | Quality Scorecard | 3 Gauges, Bar Chart, Table, Line Chart |
| 4 | Conversion Journey | 7 KPIs, Funnel, Column Charts, Line Trend |
| 5 | Order Analytics | 7 KPIs, Area Chart, Donut, Bar, Detail Table |
| 6 | My Performance | Role Cards, Gauge, Performance Bar, Badges |

---

## 🔑 Configuration Values

| Setting | Value |
|---------|-------|
| **Workspace ID** | `276a43e7-e0e3-4366-9ac1-40d1bf52182f` |
| **Dataset ID** | `3477f170-bf61-42a4-b7a6-4414d7bf8881` |
| **Existing Report ID** | `dcd4d7a3-e911-49e1-847a-1feb594f1616` |
| **Dataset Name** | `BMD_sales` |
| **Report Name** | `BMD Sales Report` |

---

## 📐 Visual Types Available

| Type | Icon | Use For |
|------|------|---------|
| `card` | 🔢 | Single KPI values |
| `kpi` | 📈 | KPI with trend indicator |
| `gauge` | ⏱️ | Progress toward target |
| `funnel` | 🔻 | Stage-based conversion |
| `lineChart` | 📉 | Trends over time |
| `clusteredColumnChart` | 📊 | Category comparison |
| `clusteredBarChart` | 📶 | Horizontal comparisons |
| `donutChart` | 🍩 | Part-to-whole |
| `pieChart` | 🥧 | Simple proportions |
| `filledMap` | 🗺️ | Geographic data |
| `tableEx` | 📋 | Detail data |
| `pivotTable` | 🔲 | Matrix with hierarchy |
| `slicer` | 🎚️ | Filter controls |
| `multiRowCard` | 🃏 | Multiple data cards |
| `areaChart` | 📈 | Stacked trends |

---

## 🎨 Theme Colors

```json
{
  "Primary (Anwar Blue)": "#0066CC",
  "Success (Green)": "#2ECC71",
  "Warning (Amber)": "#F39C12",
  "Danger (Red)": "#E74C3C",
  "Site (Teal)": "#1ABC9C",
  "Engineer (Blue)": "#3498DB",
  "Contractor (Purple)": "#9B59B6",
  "Dealer (Orange)": "#E67E22",
  "Retailer (Pink)": "#E91E63",
  "IHB (Cyan)": "#00BCD4",
  "Factory DN (Navy)": "#2C3E50",
  "General Delivery (Violet)": "#8E44AD"
}
```

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `bmd-report-creator.html` | Interactive browser-based report builder |
| `report-builder-cli.js` | Node.js CLI for API operations |
| `report-builder.js` | JavaScript visual creation library |
| `index.html` | Simple embedded report interface |

---

## 🔧 Troubleshooting

### Token Expired
```bash
# Get new token
az account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv
```

### Permission Errors
- Ensure you have "Contributor" role on the workspace
- Check that dataset allows report creation

### Visual Not Creating
- Verify page is active before adding visuals
- Check browser console for detailed errors
- Ensure report is in Edit mode

---

## 📚 API Reference

### Create Visual
```javascript
const response = await page.createVisual('card', {
    x: 100,
    y: 100, 
    width: 300,
    height: 200
});
const visual = response.visual;
```

### Add Data Field
```javascript
await visual.addDataField('Values', {
    $schema: 'http://powerbi.com/product/schema#measure',
    table: 'Fact_Visit',
    measure: 'Total Visits'
});
```

### Set Visual Property
```javascript
await visual.setProperty(
    { objectName: 'title', propertyName: 'titleText' },
    { schema: 'text', value: 'My Title' }
);
```

### Save Report
```javascript
await report.save();
// or
await report.saveAs({ name: 'New Report Name' });
```

---

## 🚀 Next Steps

1. Open `bmd-report-creator.html` in browser
2. Get and paste access token
3. Click "Edit Existing Report"
4. Go to Pages tab → Click "Build All Pages"
5. Review each page in the embedded editor
6. Add data fields manually using the Fields pane
7. Save the report

The visual layouts are pre-configured based on `report_design.md`. You'll need to drag fields from the Fields pane onto the visuals to complete the data binding.
