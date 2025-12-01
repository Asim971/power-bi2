# BMD Sales - Power BI Data Model
## Based on Actual Semantic Model Schema

### Source Tables (from Power BI Semantic Model)

| Table | Key Columns | Records |
|-------|-------------|---------|
| `public visits` | id, visit_type, created_by_id, create_by_name, visit_date_time, potential_site_id, retailer_id, dealer_id, engineer_id, ihb_registration_id, visit_category_id, territory_name, role_level, feedback, visit_photo, status | 36,041 |
| `public users` | id, name, email, phone_number, role_id, zone_id, region_id, area_id, bd_territory_id, user_designation | ~272 active |
| `public areas` | id, name, zone_id, zone_name, region_id, region_name, nation_name, assigned_zsm/gm/agm/asm | ~48 |
| `public visit_categories` | id, category_name | 9 |

---

### Visit Types Distribution

| Visit Type | Count | % of Total |
|------------|-------|------------|
| Sites | 13,235 | 36.7% |
| Influencer | 7,114 | 19.7% |
| Dealer | 5,587 | 15.5% |
| Retailer | 4,020 | 11.2% |
| IHB | 3,807 | 10.6% |
| General Sites | 2,278 | 6.3% |
| **Total** | **36,041** | **100%** |

---

### Visit Categories (9 Total)

1. Potential Sites
2. Dealer
3. Retailer
4. IHB
5. Conversion Visit
6. Head Mason
7. Engineer
8. Contractor
9. Site Manager

---

### Zones Discovered (12 Total)

| Zone ID | Zone Name |
|---------|-----------|
| 1 | South |
| 2 | Chittagong |
| 3 | Feni |
| 4 | Barisal |
| 5 | Bogura |
| 6 | Rangpur |
| 7 | Sylhet |
| 8 | Khulna |
| 9 | Dhaka |
| 10 | Mymensingh |
| 11 | Sylhet |
| 12 | Cumilla |

---

### Star Schema Design

```
                    ┌─────────────────┐
                    │   Dim_Date      │
                    │   (Generated)   │
                    └────────┬────────┘
                             │
                             │ DateKey
                             ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Dim_User      │  │   Fact_Visit    │  │   Dim_Client    │
│   (public users)│◀─│   (public visits)│─▶│   (derived)     │
└─────────────────┘  └────────┬────────┘  └─────────────────┘
        │                     │
        │ ZoneID              │ VisitCategoryID
        ▼                     ▼
┌─────────────────┐  ┌─────────────────┐
│ Dim_Territory   │  │Dim_VisitCategory│
│ (public areas)  │  │(visit_categories)│
└─────────────────┘  └─────────────────┘
```

---

### Key Relationships

| From Table | Column | To Table | Column | Cardinality |
|------------|--------|----------|--------|-------------|
| Fact_Visit | DateKey | Dim_Date | Date | Many:1 |
| Fact_Visit | EmployeeID | Dim_User | EmployeeID | Many:1 |
| Fact_Visit | ClientKey | Dim_Client | ClientKey | Many:1 |
| Fact_Visit | VisitCategoryID | Dim_VisitCategory | VisitCategoryID | Many:1 |
| Dim_User | ZoneID | Dim_Territory | ZoneID | Many:1 |

---

### Top 21 Employees by Visit Count

| Employee Name | Total Visits |
|--------------|--------------|
| Tushar Kumar Das | 422 |
| Forhad Hossain | 410 |
| Rasedul Islam | 365 |
| Maruf Ahmed | 352 |
| Md. Sangram Hosen | 350 |
| Md. Mohidul Islam | 341 |
| Nazmul Huda | 339 |
| MD MYNUDDIN | 339 |
| Md Golam Morshed | 331 |
| Md. Sohanur Rahman Khan | 329 |
| Imdaddul Haque | 326 |
| Al Mamun | 319 |
| Riad | 308 |
| Md Atikur Rahman | 305 |
| Md. Firoz Ahmed | 299 |
| Abdul Kader Akash | 297 |
| Bidan Chandra Das | 290 |
| Md.Kawsarul haque | 290 |
| Arup Sen | 289 |
| Atick Shaharier | 288 |
| Md Bayjed Hossen | 288 |

---

### Files Created

| File | Purpose |
|------|---------|
| `powerquery/Fact_Visit.pq` | Main fact table transformation |
| `powerquery/Dim_Client.pq` | Unified client dimension |
| `powerquery/Dim_User.pq` | Employee dimension |
| `powerquery/Dim_Territory.pq` | Geographic hierarchy |
| `powerquery/Dim_VisitCategory.pq` | Visit category lookup |
| `powerquery/Dim_Date.pq` | Date dimension (generated) |
| `dax/visit_measures.dax` | Core DAX measures |
| `dax/gps_deviation_measures.dax` | Territory compliance measures |
| `docs/report_design.md` | 3-page report layout |
| `security/rls_configuration.dax` | Row-level security setup |

---

### Implementation Notes

1. **No Direct PostgreSQL Connection**: Power Query references existing tables in the semantic model using `#"table name"` syntax
2. **Client Dimension Derived**: Since client master tables aren't in the model, Dim_Client is derived from unique client IDs in visits
3. **Territory Mapping**: Uses `territory_name` from visits and joins to `public areas` for zone/region hierarchy
4. **60-Day Conversion Window**: Per user decision, conversion tracking looks 60 days forward from visit date
5. **GPS Deviation**: Territory compliance compares employee's assigned zone vs visit location
