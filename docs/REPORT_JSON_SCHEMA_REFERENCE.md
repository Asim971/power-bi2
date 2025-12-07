# Power BI report.json Schema Reference

**Version**: 1.0  
**Research Date**: December 2, 2025  
**Format**: Power BI Report Definition Language (PBIR)  
**Reference**: BMDSalesReport.Report/report.json analysis

---

## TABLE OF CONTENTS

1. [report.json Overview](#section-1-reportjson-overview)
2. [Root-Level Schema](#section-2-root-level-schema)
3. [Sections (Pages)](#section-3-sections-pages)
4. [Visual Containers](#section-4-visual-containers)
5. [Visual Types & Projections](#section-5-visual-types--projections)
6. [Themes & Resources](#section-6-themes--resources)
7. [Filters & Slicers](#section-7-filters--slicers)
8. [Interactions & Drill-Through](#section-8-interactions--drill-through)
9. [BMD Sales Real Examples](#section-9-bmd-sales-real-examples)
10. [Best Practices](#section-10-best-practices)

---

## SECTION 1: report.json OVERVIEW

### 1.1 What is report.json?

**report.json** is the metadata definition file for Power BI reports containing:

- **Report configuration** (version, themes, settings)
- **Page definitions** (sections with layout information)
- **Visual containers** (charts, tables, cards, etc.)
- **Data projections** (which columns/measures used)
- **Interactions** (cross-filtering, drill-through)
- **Resource packages** (themes, images, custom visuals)
- **Filters & slicers** (page-level and visual-level)

### 1.2 File Location

```
ReportName.Report/
├── definition.pbir             ← Alternative format (newer)
├── report.json                 ← JSON schema (our focus)
└── StaticResources/
    └── SharedResources/
        ├── BaseThemes/         ← Base Power BI themes
        │   └── CY25SU11.json
        └── CustomThemes/       ← Custom organization themes
            └── BMD_Sales_WOW_Theme.json
```

---

## SECTION 2: ROOT-LEVEL SCHEMA

### 2.1 Root Structure

```json
{
  "config": "{...}",                    // Report configuration (JSON string)
  "layoutOptimization": 0,              // 0 or 1 (optimization level)
  "resourcePackages": [...],            // Themes and resources
  "sections": [...],                    // Page definitions
  "filters": "[]",                      // Global filters (JSON string)
  "version": "5.x.x"                    // Report version (implicit in config)
}
```

### 2.2 Config Object (Nested JSON String)

```json
{
  "config": "{
    \"version\": \"5.68\",
    \"themeCollection\": {
      \"baseTheme\": {
        \"name\": \"CY25SU11\",
        \"type\": 2,
        \"version\": {
          \"visual\": \"2.4.0\",
          \"report\": \"3.0.0\",
          \"page\": \"2.3.0\"
        }
      },
      \"customTheme\": {
        \"name\": \"BMD_Sales_WOW_Theme\",
        \"type\": 2,
        \"version\": {
          \"visual\": \"2.4.0\",
          \"report\": \"3.0.0\",
          \"page\": \"2.3.0\"
        }
      }
    },
    \"activeSectionIndex\": 0,
    \"defaultDrillFilterOtherVisuals\": true,
    \"linguisticSchemaSyncVersion\": 0,
    \"settings\": {
      \"useNewFilterPaneExperience\": true,
      \"allowChangeFilterTypes\": true,
      \"useStylableVisualContainerHeader\": true,
      \"queryLimitOption\": 6,
      \"useEnhancedTooltips\": true,
      \"exportDataMode\": 1,
      \"useDefaultAggregateDisplayName\": true
    },
    \"objects\": {
      \"section\": [...],
      \"outspacePane\": [...]
    }
  }"
}
```

**Key Config Properties**:

| Property | Meaning | Values |
|----------|---------|--------|
| `version` | Report version | "5.x.x" format |
| `baseTheme` | Default theme from Power BI | CY25SU11, CY24WOW, etc. |
| `customTheme` | Custom organization theme | Name from themes folder |
| `activeSectionIndex` | Default page on open | 0 = first page |
| `queryLimitOption` | Result row limit | 1-6 (10K, 50K, 100K, 500K, etc.) |
| `useEnhancedTooltips` | Modern tooltips | true/false |
| `exportDataMode` | Allow data export | 0=off, 1=on, 2=summarized |

---

## SECTION 3: SECTIONS (PAGES)

### 3.1 Section Structure

```json
{
  "sections": [
    {
      "config": "{...}",                // Section-level config
      "displayName": "Executive Command Center",
      "displayOption": 1,               // 1=visible, 0=hidden
      "filters": "[]",                  // Page-level filters
      "height": 720.00,                 // Pixel height
      "name": "page_executive",         // Programmatic name
      "visualContainers": [...]         // All visuals on page
    }
  ]
}
```

### 3.2 Section Config (Nested JSON String)

```json
{
  "config": "{
    \"objects\": {
      \"background\": [{
        \"properties\": {
          \"color\": {
            \"solid\": {
              \"color\": {
                \"expr\": {
                  \"ThemeDataColor\": {
                    \"ColorId\": 0,
                    \"Percent\": 0
                  }
                }
              }
            }
          }
        }
      }],
      \"pageAlignment\": [{
        \"properties\": {
          \"alignment\": {
            \"expr\": {
              \"Literal\": {
                \"Value\": \"'Center'\"
              }
            }
          }
        }
      }]
    }
  }"
}
```

### 3.3 Page Types

| Type | Use Case |
|------|----------|
| **Standard Page** | Regular report page with visuals |
| **Blank Page** | For custom layouts or infographics |
| **Mobile Layout** | Mobile-optimized version (same page, different layout) |
| **Bookmark-Linked** | Triggered by bookmark navigation |

---

## SECTION 4: VISUAL CONTAINERS

### 4.1 Visual Container Structure

```json
{
  "config": "{...}",        // Visual definition (nested JSON)
  "filters": "[]",          // Visual-level filters
  "height": 200.00,         // Pixel height
  "width": 400.00,          // Pixel width
  "x": 20.00,               // X position from left
  "y": 260.00,              // Y position from top
  "z": 8000.00              // Z-order (layering)
}
```

### 4.2 Visual Config (Nested JSON String)

```json
{
  "config": "{
    \"name\": \"chart_visits_trend\",
    \"layouts\": [{
      \"id\": 0,
      \"position\": {
        \"x\": 20,
        \"y\": 260,
        \"z\": 8000,
        \"width\": 610,
        \"height\": 220
      }
    }],
    \"singleVisual\": {
      \"visualType\": \"lineChart\",
      \"projections\": {
        \"Category\": [{
          \"queryRef\": \"Dim_Date.Date\",
          \"active\": true
        }],
        \"Y\": [
          {\"queryRef\": \"Fact_Visit.Total_Visits\"},
          {\"queryRef\": \"Fact_Order.Total_Orders\"}
        ]
      },
      \"prototypeQuery\": {...},
      \"drillFilterOtherVisuals\": true,
      \"objects\": {...},
      \"vcObjects\": {...}
    }
  }"
}
```

---

## SECTION 5: VISUAL TYPES & PROJECTIONS

### 5.1 Common Visual Types

| Visual Type | Description | Use Case |
|-------------|-------------|----------|
| `card` | Single metric display | KPIs (Total Visits, Revenue) |
| `lineChart` | Trends over time | Performance trends, time series |
| `barChart` | Category comparisons | Sales by territory, visits by role |
| `columnChart` | Vertical bars | Similar to bar, alternative view |
| `donutChart` | Circular segments | Mix/composition (client types) |
| `pieChart` | Circular pie slices | Part-to-whole relationships |
| `scatterChart` | X-Y scatter plot | Correlations (quality vs visits) |
| `table` | Tabular data | Detailed data, drill-down |
| `matrix` | Pivot table | Multi-dimensional analysis |
| `funnel` | Funnel diagram | Conversion stages (Visit→Order) |
| `gauge` | Radial gauge | Progress toward goal |
| `filledMap` | Geographic heatmap | Regional performance |
| `ribbon` | Ranked categories over time | Top performers, rank changes |
| `textbox` | Text labels | Annotations, titles |
| `shape` | Geometric shapes | Design elements |
| `image` | Embedded image | Logos, backgrounds |
| `button` | Interactive button | Navigation, filters |
| `slicerNumerical` | Number range slicer | Filter numeric ranges |
| `slicerDropdown` | Dropdown filter | Single/multiple select |

### 5.2 Projections (Data Binding)

**Projections** define how data columns map to visual roles (axes, legend, size, color, etc.):

```json
{
  "projections": {
    "Category": [{
      "queryRef": "Dim_Territory.Zone",
      "active": true
    }],
    "Y": [{
      "queryRef": "Fact_Visit.Total_Visits",
      "active": true
    }],
    "X": [{
      "queryRef": "Dim_Date.Date",
      "active": true
    }],
    "Color": [{
      "queryRef": "Fact_Visit.IsHighQuality",
      "active": true
    }]
  }
}
```

**Common Projection Roles**:

| Role | Visual Type | Meaning |
|------|------------|---------|
| **Category** | Most visuals | X-axis categories or legend groups |
| **Y** | Line, Bar, Scatter | Y-axis values or height |
| **X** | Scatter | X-axis values |
| **Size** | Bubble, Scatter | Bubble/point size mapping |
| **Color** | Most visuals | Color saturation or category |
| **Legend** | Pie, Donut | Legend items |
| **Values** | Table, Matrix | Cell values |
| **Rows** | Matrix | Row dimension |
| **Columns** | Matrix | Column dimension |
| **GradientValue** | Map | Heatmap intensity |

### 5.3 Objects (Visual Properties)

```json
{
  "objects": {
    "legend": [{
      "properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "position": {"expr": {"Literal": {"Value": "'Right'"}}},
        "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
      }
    }],
    "lineStyles": [{
      "properties": {
        "strokeWidth": {"expr": {"Literal": {"Value": "3D"}}}
      }
    }],
    "labels": [{
      "properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1F4E79'"}}}}},
        "fontSize": {"expr": {"Literal": {"Value": "14D"}}}
      }
    }]
  },
  "vcObjects": {
    "title": [{
      "properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "text": {"expr": {"Literal": {"Value": "'Performance Trend'"}}},
        "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1F4E79'"}}}}},
        "fontSize": {"expr": {"Literal": {"Value": "14D"}}}
      }
    }],
    "background": [{
      "properties": {
        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}
      }
    }],
    "border": [{
      "properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E2E8F0'"}}}}},
        "radius": {"expr": {"Literal": {"Value": "8D"}}}
      }
    }]
  }
}
```

---

## SECTION 6: THEMES & RESOURCES

### 6.1 Resource Packages

```json
{
  "resourcePackages": [
    {
      "resourcePackage": {
        "disabled": false,
        "items": [
          {
            "name": "BMD_Sales_WOW_Theme",
            "path": "CustomThemes/BMD_Sales_WOW_Theme.json",
            "type": 201
          },
          {
            "name": "CY25SU11",
            "path": "BaseThemes/CY25SU11.json",
            "type": 202
          }
        ],
        "name": "SharedResources",
        "type": 2
      }
    }
  ]
}
```

**Resource Types**:
- **Type 201**: Custom theme
- **Type 202**: Base theme
- **Type 203**: Custom visual
- **Type 204**: Image/static resource

### 6.2 Theme Structure

**Example: BMD_Sales_WOW_Theme.json**

```json
{
  "name": "BMD Sales WOW",
  "dataColors": [
    "#1F4E79",    // Primary blue
    "#3BB273",    // Success green
    "#F2C811",    // Warning yellow
    "#E74856",    // Error red
    "#00BCF2",    // Information blue
    "#44546A",    // Gray
    "#7FBA00",    // Alternative green
    "#FFB900"     // Alternative yellow
  ],
  "background": {"color": "#FFFFFF"},
  "foreground": {"color": "#333333"},
  "tableAccent": {"color": "#1F4E79"},
  "fonts": {
    "base": {
      "fontFamilies": ["Segoe UI", "Arial", "sans-serif"]
    }
  }
}
```

---

## SECTION 7: FILTERS & SLICERS

### 7.1 Page-Level Filters

```json
{
  "filters": "[{
    \"name\": \"RegionFilter\",
    \"type\": \"Advanced\",
    \"targets\": [{
      \"table\": \"Dim_Territory\",
      \"column\": \"RegionName\"
    }],
    \"filterType\": 0,
    \"defaultValue\": \"North\"
  }]"
}
```

### 7.2 Slicer Visual (Interactive Filter)

```json
{
  "config": "{
    \"name\": \"slicer_territory\",
    \"singleVisual\": {
      \"visualType\": \"slicerDropdown\",
      \"projections\": {
        \"Values\": [{
          \"queryRef\": \"Dim_Territory.Zone\"
        }]
      },
      \"objects\": {
        \"selection\": [{
          \"properties\": {
            \"mode\": {\"expr\": {\"Literal\": {\"Value\": \"'Single'\"}}}
          }
        }]
      }
    }
  }"
}
```

---

## SECTION 8: INTERACTIONS & DRILL-THROUGH

### 8.1 Cross-Filtering

```json
{
  "drillFilterOtherVisuals": true    // Enable filtering between visuals
}
```

When a user clicks a data point in one visual, other visuals automatically filter.

### 8.2 Drill-Through Page

```json
{
  "drillThroughTarget": {
    "targetPageName": "detail_page",
    "targetPageId": 2,
    "passthrough": [{
      "sourceColumn": "Fact_Visit.ClientKey",
      "targetColumn": "Dim_Client.ClientKey"
    }]
  }
}
```

### 8.3 Bookmarks (Save-State)

```json
{
  "bookmarks": [{
    "name": "HighQualityFilter",
    "displayName": "High Quality Visits",
    "description": "Shows only visits with quality score > 85",
    "state": {
      "filters": [...]  // Filter state at time of bookmark creation
    }
  }]
}
```

---

## SECTION 9: BMD SALES REAL EXAMPLES

### 9.1 KPI Card Visual

```json
{
  "config": "{
    \"name\": \"kpi_visits\",
    \"layouts\": [{
      \"id\": 0,
      \"position\": {\"x\": 20, \"y\": 90, \"z\": 3000, \"width\": 300, \"height\": 150}
    }],
    \"singleVisual\": {
      \"visualType\": \"card\",
      \"projections\": {
        \"Values\": [{\"queryRef\": \"Fact_Visit.Total_Visits\"}]
      },
      \"objects\": {
        \"labels\": [{
          \"properties\": {
            \"fontSize\": {\"expr\": {\"Literal\": {\"Value\": \"28D\"}}},
            \"color\": {\"solid\": {\"color\": {\"expr\": {\"Literal\": {\"Value\": \"'#1F4E79'\"}}}}}
          }
        }]
      },
      \"vcObjects\": {
        \"title\": [{
          \"properties\": {
            \"text\": {\"expr\": {\"Literal\": {\"Value\": \"'Total Visits'\"}}},
            \"fontSize\": {\"expr\": {\"Literal\": {\"Value\": \"14D\"}}}
          }
        }]
      }
    }
  }"
}
```

### 9.2 Line Chart (Trend)

```json
{
  "config": "{
    \"name\": \"chart_visits_trend\",
    \"singleVisual\": {
      \"visualType\": \"lineChart\",
      \"projections\": {
        \"Category\": [{\"queryRef\": \"Dim_Date.Date\"}],
        \"Y\": [
          {\"queryRef\": \"Fact_Visit.Total_Visits\"},
          {\"queryRef\": \"Fact_Order.Total_Orders\"}
        ]
      }
    }
  }"
}
```

### 9.3 Donut Chart (Mix)

```json
{
  "config": "{
    \"name\": \"chart_client_mix\",
    \"singleVisual\": {
      \"visualType\": \"donutChart\",
      \"projections\": {
        \"Category\": [{\"queryRef\": \"Fact_Visit.ClientType\"}],
        \"Y\": [{\"queryRef\": \"Fact_Visit.Total_Visits\"}]
      },
      \"objects\": {
        \"slices\": [{
          \"properties\": {
            \"innerRadiusRatio\": {\"expr\": {\"Literal\": {\"Value\": \"55D\"}}}
          }
        }]
      }
    }
  }"
}
```

### 9.4 Funnel Chart (Conversion)

```json
{
  "config": "{
    \"name\": \"quick_funnel\",
    \"singleVisual\": {
      \"visualType\": \"funnel\",
      \"projections\": {
        \"Category\": [{\"queryRef\": \"Fact_Order.StatusGroup\"}],
        \"Y\": [{\"queryRef\": \"Fact_Order.Total_Orders\"}]
      }
    }
  }"
}
```

---

## SECTION 10: BEST PRACTICES

### 10.1 Performance Optimization

1. **Limit visuals per page** — Max 10-15 visuals (more = slower loading)
2. **Use slicers** — Let users filter rather than show all data
3. **Set query limits** — Use `queryLimitOption: 6` (100K rows max)
4. **Minimize cross-filtering** — Only between relevant visuals
5. **Use aggregations** — Sum/count rather than raw data

### 10.2 UX/Design Best Practices

1. **Logical layout** — Group related visuals together
2. **Consistent colors** — Use theme colors for branding
3. **Clear titles** — Every visual needs meaningful title
4. **Readable fonts** — Minimum 12pt for labels
5. **Mobile-friendly** — Test on mobile devices
6. **Accessible** — Use high-contrast colors, alt-text

### 10.3 Common Mistakes to Avoid

| Mistake | Solution |
|---------|----------|
| Too many visuals per page | Spread across multiple pages |
| Overlapping visuals | Use Z-order layering carefully |
| Poor color contrast | Use accessible color palettes |
| Missing titles/labels | Document every visual |
| Hardcoded colors | Use theme-referenced colors |
| Inconsistent interactions | Plan cross-filtering strategy |

---

## APPENDIX A: DATA TYPES IN Expressions

```json
{
  "Literal": {"Value": "'text value'"}        // String
}

{
  "Literal": {"Value": "123"}                 // Number
}

{
  "Literal": {"Value": "true"}                // Boolean
}

{
  "Literal": {"Value": "'2025-12-02'"}        // Date
}

{
  "Literal": {"Value": "3.14D"}               // Decimal
}

{
  "ThemeDataColor": {"ColorId": 0, "Percent": 0}  // Theme color reference
}

{
  "SourceRef": {"Source": "v"},               // Query source reference
  "Property": "ColumnName"
}
```

---

## APPENDIX B: USEFUL RESOURCES

- **Power BI Report JSON Schema**: (Part of Power BI REST API docs)
- **Visual Reference**: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-types-for-reports-and-q-and-a
- **M Language (Power Query)**: https://learn.microsoft.com/en-us/powerquery-m/power-query-m-function-reference
- **DAX Reference**: https://learn.microsoft.com/en-us/dax/dax-function-reference

---

**Document Complete**

