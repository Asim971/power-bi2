# Client Location Mapping Documentation

## Overview

This document describes how the 5 client types map to geographic locations in the BMD Sales system.

## Location Hierarchy

```
Zone (ZoneID)
  └── Region (RegionID)
        └── Area (AreaID)
              └── Territory (TerritoryID)
                    └── Bazaar (bazaar_id)
                          └── Upazilla (upazilla_id)
                                └── District (district_id)
```

## Client Types and Location Keys

| Client Type | Source Table | Count | Primary Location Key | Location Path |
|-------------|--------------|-------|---------------------|---------------|
| **Site** | `potential_site` | 10,070 | `bazaar_id` | bazaar → upazilla → district → zone |
| **Retailer** | `retailers` | 3,130 | `bazaar_id` | bazaar → upazilla → district → zone |
| **IHB** | `ihb_registration` | 11,231 | `bazaar_id` | bazaar → upazilla → district → zone |
| **Dealer** | `dealers` | 947 | `district_name_text` | Text only (no ID join) |
| **Influencer** | `engineers` | 2,361 | None | No location - use visit location |

## Detailed Mappings

### 1. Sites (Potential Sites)

**Source:** `public potential_site`

**Location Columns:**
- `bazaar_id` - Primary location key (populated)
- `territory_id` - NULL in data
- `bd_territory_id` - NULL in data
- `area_id` - NULL in data

**Join Path:**
```
potential_site.bazaar_id 
  → bazaars.id 
    → bazaars.upazilla_id 
      → upazilla.id 
        → upazilla.district_id 
          → districts.id
```

### 2. Retailers

**Source:** `public retailers`

**Location Columns:**
- `bazaar_id` - Primary location key (populated)
- `bazaar_name` - NULL (text field not populated)
- `dealer_id` - Link to parent dealer

**Join Path:**
```
retailers.bazaar_id 
  → bazaars.id 
    → bazaars.upazilla_id 
      → upazilla.id
```

### 3. IHB (Individual House Builders)

**Source:** `public ihb_registration`

**Location Columns:**
- `bazaar_id` - Primary location key (populated)
- `end_user` - Flag (YES/NO)

**Join Path:**
```
ihb_registration.bazaar_id 
  → bazaars.id 
    → bazaars.upazilla_id
```

### 4. Dealers

**Source:** `public dealers`

**Location Columns:**
- `district_name` - NULL
- `district_name_text` - Text value (no ID for join)
- `upazilla_names_text` - Comma-separated text (no IDs)
- `nation_name` / `nation_name_text` - Country text

**Issues:**
- Dealers have **text-only location data**
- No `district_id` or `upazilla_id` for proper joins
- Cannot be linked to zone hierarchy via IDs

**Workaround:** Use text matching or rely on retailer locations (retailers belong to dealers)

### 5. Influencers (Engineers)

**Source:** `public engineers`

**Location Columns:**
- None

**Issues:**
- Engineers table has **no location columns**
- Must derive location from visit records
- `consultancy_firm` can provide some context

**Workaround:** Join to visits to get location from visit records

## Key Tables for Location

### Bazaars Table (`public bazaars`)

Primary location link table with full hierarchy:

| Column | Description |
|--------|-------------|
| `id` | Primary key |
| `bazaar_name` | Bazaar name |
| `upazilla_id` | FK to upazilla |
| `upazilla_name` | Denormalized upazilla name |
| `district_id` | FK to districts |
| `district_name` | Denormalized district name |
| `zone_id` | FK to zone |
| `zone_name` | Denormalized zone name |
| `assigned_sr/asm/zsm` | Assigned salespeople |

### Upazilla Table (`public upazilla`)

| Column | Description |
|--------|-------------|
| `id` | Primary key |
| `upazilla_name` | Upazilla name |
| `district_id` | FK to districts |
| `zone_id` | FK to zone |
| `territory_name` | Associated territory |
| `assigned_sr/asm/zsm` | Assigned salespeople |

### Districts Table (`public districts`)

| Column | Description |
|--------|-------------|
| `id` | Primary key |
| `district_name` | District name |
| `zone_id` | FK to zone |
| `zone_name` | Denormalized zone name |
| `division_id` | FK to division |

### Territory Table (`public territory`)

SR/ASM Territory for ORG track:

| Column | Description |
|--------|-------------|
| `id` | Primary key |
| `name` | Territory name |
| `zone_id` | FK to zone |
| `region_id` | FK to region |
| `area_id` | FK to area |
| `upazilla_names` | Comma-separated upazilla names |
| `bd_territory_names` | Comma-separated BD territory names |

### BD Territory Table (`public bd_territory`)

BDO/CRO Territory for BMD track:

| Column | Description |
|--------|-------------|
| `id` | Primary key |
| `bd_territory_name` | BD Territory name |
| `upazilla_id` | FK to upazilla (mostly NULL) |
| `district_id` | FK to districts (mostly NULL) |

## RLS Implications

### For Sites, Retailers, IHB
- Can filter by `ZoneID`, `UpazillaID`, `DistrictID`
- Use `HasLocationData = true` to identify records with location

### For Dealers
- Cannot use ID-based RLS
- Must use text matching on `DistrictName` or `UpazillaName`

### For Influencers
- No direct location filtering
- Must join to visits table for location-based RLS

## Dim_Client Output Schema

| Column | Type | Description |
|--------|------|-------------|
| `ClientKey` | text | Composite key: `ClientType-ClientID` |
| `ClientID` | int | Original ID from source table |
| `ClientName` | text | Client/Project/Shop name |
| `ClientType` | text | Site/Retailer/Dealer/Influencer/IHB |
| `SubType` | text | Site type, engineer type, end_user flag |
| `ClientCategory` | text | Prospect/Channel Partner/Influencer/End Customer |
| `BazaarName` | text | Bazaar name (if available) |
| `UpazillaID` | int | Upazilla ID for joins |
| `UpazillaName` | text | Upazilla name |
| `DistrictID` | int | District ID for joins |
| `DistrictName` | text | District name |
| `ZoneID` | int | Zone ID for joins |
| `ZoneName` | text | Zone name |
| `HasLocationData` | bool | Flag if location is available |

## Data Quality Notes

1. **Bazaar IDs are reliable** - Sites, Retailers, IHB all have populated bazaar_id
2. **Denormalized names often NULL** - Must join to lookup tables for names
3. **Dealers have text-only location** - Cannot join by ID
4. **Engineers have no location** - Must use visit context
5. **BD Territory upazilla_id mostly NULL** - Cannot link BDO/CRO to upazilla hierarchy
