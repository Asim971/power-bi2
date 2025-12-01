# Role & Territory Mapping Analysis

## Role Hierarchy (from Database)

### Two Department Tracks

| Track | Code | Roles | Focus Area |
|-------|------|-------|------------|
| **Business Development** | BMD | BDO, CRO, BD_LEAD, BD_INCHARGE | Sites, Engineers, IHB, Potential Sites |
| **Sales Organization** | ORG | SR, ASM, ZSM, AGM, GM | Retailers, Orders, Stock |

### Complete Role Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ROLE HIERARCHY                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  EXECUTIVE LEVEL                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Level 1000: SUPER_ADMIN (1 user) - Full system access                  │ │
│  │ Level 1010: BMD_ADMIN (13 users) - BMD department admin                │ │
│  │ Level 2010: COMPANY_ADMIN (27 users) - Organization admin              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  MANAGEMENT LEVEL                                                            │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Level 1015: BD_LEAD (3 users) - Business Development Lead              │ │
│  │ Level 1020: BD_INCHARGE (7 users) - BD Incharge                        │ │
│  │ Level 2020: GM/DGM (0 users) - General Manager                         │ │
│  │ Level 2030: AGM (3 users) - Assistant General Manager                  │ │
│  │ Level 2040: ZSM (11 users) - Zonal Sales Manager                       │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  FIELD LEVEL (PRD Actors)                                                    │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │   BMD Track                      ORG Track                              │ │
│  │   ───────────                    ──────────                             │ │
│  │   Level 1030: BDO (57 users)     Level 2050: ASM (15 users)            │ │
│  │   Level 1040: CRO (59 users)     Level 2060: SR (186 users)            │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### PRD Actor Mapping

| PRD Actor | Role ID | Role Name | Department | User Count |
|-----------|---------|-----------|------------|------------|
| SR | 11 | SR | ORG | 186 |
| ASM | 10 | ASM | ORG | 15 |
| BDO | 3 | BDO | BMD | 57 |
| CRO | 4 | CRO | BMD | 59 |
| CRM | 2 | BMD_ADMIN | BMD | 13 |

---

## Territory Mapping Structure

### Geographic Hierarchy (ORG Track - SR/ASM/ZSM)

```
Nation (Bangladesh)
  └── Zone (e.g., Dhaka Division)
       └── Region (e.g., Dhaka North)
            └── Area (e.g., Gulshan)
                 └── Territory (e.g., Gulshan-01)
                      └── Upazilla (sub-district)
```

### Territory Tables

| Table | Purpose | Records |
|-------|---------|---------|
| `public zone` | Zone definitions | - |
| `public region` | Region definitions | - |
| `public areas` | Area definitions (Dim_Territory source) | 130+ |
| `public territory` | Territory details with assignments | 186 |
| `public bd_territory` | BD-specific territories (Upazilla level) | 56 |
| `public upazilla` | Sub-district definitions | - |
| `public districts` | District definitions | - |
| `public divisions` | Division definitions | - |

---

## User-Territory Mapping Tables

### 1. Direct Assignment (users table)
SR users have direct zone/region/area in `public users`:
```
users.zone_id → Zone
users.region_id → Region  
users.area_id → Area
```

### 2. SR Territory Mapping (users_territory)
```sql
users_territory.users_id → users.id
users_territory.territory_id → territory.id
```
- **186 records** - One per SR
- SR users are assigned to specific territories

### 3. BDO/CRO Territory Mapping (users_bd_territory)
```sql
users_bd_territory.users_id → users.id
users_bd_territory.bd_territory_id → bd_territory.id
```
- **279 records** - Multiple territories per BDO/CRO
- BDO/CRO users can have multiple BD territories

---

## Key Differences by Role

| Role | Zone/Region/Area | Territory Mapping | BD Territory |
|------|-----------------|-------------------|--------------|
| **SR** | ✅ Direct in users | via `users_territory` | ❌ Not used |
| **ASM** | ✅ Direct in users | via area_id | ❌ Not used |
| **ZSM** | ✅ Direct in users (zone only) | N/A | ❌ Not used |
| **BDO** | ❌ NULL | ❌ Not used | via `users_bd_territory` |
| **CRO** | ❌ NULL | ❌ Not used | via `users_bd_territory` |

---

## Power BI Relationship Model

```
                                    ┌─────────────┐
                                    │ public role │
                                    │   (id)      │
                                    └──────┬──────┘
                                           │1
                                           │
                                    ┌──────┴──────┐
                                    │             │
                              ┌─────┴─────┐       │
                              │Dim_User   │       │
                              │(UserID)   │       │
                              │(RoleID)───┘       │
                              │(ZoneID)           │
                              │(AreaID)           │
                              └─────┬─────┘       
                                    │             
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
      ┌───────┴───────┐     ┌───────┴───────┐     ┌───────┴───────┐
      │users_territory│     │users_bd_terr  │     │ Dim_Territory │
      │(users_id)     │     │(users_id)     │     │ (AreaID)      │
      │(territory_id) │     │(bd_terr_id)   │     │ (ZoneID)      │
      └───────┬───────┘     └───────┬───────┘     └───────────────┘
              │                     │
      ┌───────┴───────┐     ┌───────┴───────┐
      │ territory     │     │ bd_territory  │
      │ (id)          │     │ (id)          │
      └───────────────┘     └───────────────┘
```

---

## Reporting Implications

### For RLS (Row-Level Security)

| Role | Filter By |
|------|-----------|
| SR | `users_territory.territory_id` or `users.area_id` |
| ASM | `users.area_id` (multiple SRs report to one ASM) |
| ZSM | `users.zone_id` (all users in zone) |
| BDO/CRO | `users_bd_territory.bd_territory_id` |
| Admin | No filter (all data) |

### For GPS Deviation Analysis

- **SR visits**: Compare visit `territory_id` with user's assigned `territory_id` from `users_territory`
- **BDO/CRO visits**: Compare visit location with `bd_territory` assignments from `users_bd_territory`

---

## Sample Data Patterns

### SR User Example
```json
{
  "UserID": 127,
  "Name": "Saiful Islam",
  "RoleID": 11,  // SR
  "ZoneID": 4,
  "RegionID": 10,
  "AreaID": 11,
  "BDTerritoryID": null,  // Not used for SR
  "MappedTerritoryID": 15  // From users_territory
}
```

### BDO User Example
```json
{
  "UserID": 7,
  "Name": "S.M Omar",
  "RoleID": 3,  // BDO
  "ZoneID": null,      // Not used for BDO
  "RegionID": null,    // Not used for BDO
  "AreaID": null,      // Not used for BDO
  "BDTerritoryIDs": [1, 2, 5]  // Multiple from users_bd_territory
}
```
