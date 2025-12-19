#!/usr/bin/env python3
"""
Fabric SQL Endpoint Audit Script
Uses Azure AD authentication (already logged in via Azure CLI)
Audits PUBLIC source tables and their relationships

Table naming convention in Fabric: sm_bmd_sales_<table_name>
"""

import pyodbc
import struct
from azure.identity import AzureCliCredential

# Fabric SQL Endpoint connection details
SERVER = "namszb3yfzwe7jrxyxgifsnf2a-45bwuj7d4btehgwbidi36uqyf4.datawarehouse.fabric.microsoft.com"
DATABASE = "BMD_Sales"
PORT = 1433

# Table name prefix in Fabric
PREFIX = "sm_bmd_sales_"

def get_azure_token():
    """Get Azure AD token using Azure CLI credential"""
    credential = AzureCliCredential()
    token = credential.get_token("https://database.windows.net/.default")
    token_bytes = token.token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    return token_struct

def connect_fabric():
    """Connect to Fabric SQL Endpoint using Azure AD token"""
    print("🔐 Getting Azure AD token from Azure CLI...")
    token_struct = get_azure_token()
    
    conn_str = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={SERVER},{PORT};"
        f"Database={DATABASE};"
        f"Encrypt=Yes;"
        f"TrustServerCertificate=Yes;"
    )
    
    print(f"🔌 Connecting to {SERVER}...")
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    conn = pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    print("✅ Connected successfully!\n")
    return conn

def audit_users_table(cursor):
    """Audit public_users table and its relationships"""
    print("=" * 80)
    print("1. PUBLIC_USERS TABLE AUDIT")
    print("=" * 80)
    
    # Basic counts
    cursor.execute(f'''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN delete_status = 'NO' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN delete_status = 'YES' THEN 1 ELSE 0 END) as deleted
        FROM [{PREFIX}public_users]
    ''')
    row = cursor.fetchone()
    print(f"Total: {row[0]}, Active: {row[1]}, Deleted: {row[2]}")
    
    # FK: role_id -> public_role
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_users] u
        WHERE u.role_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_role] r WHERE r.id = u.role_id)
    ''')
    row = cursor.fetchone()
    print(f"\n🔗 role_id → public_role: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: organization_id -> public_organization
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_users] u
        WHERE u.organization_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_organization] o WHERE o.id = u.organization_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 organization_id → public_organization: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: zone_id -> public_zone
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_users] u
        WHERE u.zone_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_zone] z WHERE z.id = u.zone_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 zone_id → public_zone: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: region_id -> public_region
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_users] u
        WHERE u.region_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_region] r WHERE r.id = u.region_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 region_id → public_region: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: area_id -> public_areas
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_users] u
        WHERE u.area_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_areas] a WHERE a.id = u.area_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 area_id → public_areas: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))

def audit_territory_table(cursor):
    """Audit public_territory table and its relationships"""
    print("\n" + "=" * 80)
    print("2. PUBLIC_TERRITORY TABLE AUDIT")
    print("=" * 80)
    
    # Basic counts
    cursor.execute(f'''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN delete_status = 'NO' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN delete_status = 'YES' THEN 1 ELSE 0 END) as deleted
        FROM [{PREFIX}public_territory]
    ''')
    row = cursor.fetchone()
    print(f"Total: {row[0]}, Active: {row[1]}, Deleted: {row[2]}")
    
    # FK: organization_id -> public_organization
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_territory] t
        WHERE t.organization_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_organization] o WHERE o.id = t.organization_id)
    ''')
    row = cursor.fetchone()
    print(f"\n🔗 organization_id → public_organization: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: zone_id -> public_zone
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_territory] t
        WHERE t.zone_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_zone] z WHERE z.id = t.zone_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 zone_id → public_zone: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: region_id -> public_region
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_territory] t
        WHERE t.region_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_region] r WHERE r.id = t.region_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 region_id → public_region: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: area_id -> public_areas
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_territory] t
        WHERE t.area_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_areas] a WHERE a.id = t.area_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 area_id → public_areas: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))

def audit_bridge_tables(cursor):
    """Audit bridge/junction tables"""
    print("\n" + "=" * 80)
    print("3. BRIDGE TABLES AUDIT")
    print("=" * 80)
    
    # users_territory bridge
    print("\n📋 public_users_territory:")
    cursor.execute(f'''
        SELECT COUNT(*) as total,
               COUNT(DISTINCT users_id) as unique_users,
               COUNT(DISTINCT territory_id) as unique_territories
        FROM [{PREFIX}public_users_territory]
    ''')
    row = cursor.fetchone()
    print(f"   Total: {row[0]}, Users: {row[1]}, Territories: {row[2]}")
    
    # Check orphans
    cursor.execute(f'''
        SELECT COUNT(*) FROM [{PREFIX}public_users_territory] ut
        WHERE NOT EXISTS (SELECT 1 FROM [{PREFIX}public_users] u WHERE u.id = ut.users_id)
    ''')
    orphan_users = cursor.fetchone()[0]
    cursor.execute(f'''
        SELECT COUNT(*) FROM [{PREFIX}public_users_territory] ut
        WHERE NOT EXISTS (SELECT 1 FROM [{PREFIX}public_territory] t WHERE t.id = ut.territory_id)
    ''')
    orphan_territories = cursor.fetchone()[0]
    print(f"   🔗 users_id orphans: {orphan_users}" + (" ⚠️" if orphan_users > 0 else " ✅"))
    print(f"   🔗 territory_id orphans: {orphan_territories}" + (" ⚠️" if orphan_territories > 0 else " ✅"))
    
    # users_bd_territory bridge
    print("\n📋 public_users_bd_territory:")
    cursor.execute(f'''
        SELECT COUNT(*) as total,
               COUNT(DISTINCT users_id) as unique_users,
               COUNT(DISTINCT bd_territory_id) as unique_bd_territories
        FROM [{PREFIX}public_users_bd_territory]
    ''')
    row = cursor.fetchone()
    print(f"   Total: {row[0]}, Users: {row[1]}, BD Territories: {row[2]}")
    
    cursor.execute(f'''
        SELECT COUNT(*) FROM [{PREFIX}public_users_bd_territory] ubt
        WHERE NOT EXISTS (SELECT 1 FROM [{PREFIX}public_users] u WHERE u.id = ubt.users_id)
    ''')
    orphan_users = cursor.fetchone()[0]
    cursor.execute(f'''
        SELECT COUNT(*) FROM [{PREFIX}public_users_bd_territory] ubt
        WHERE NOT EXISTS (SELECT 1 FROM [{PREFIX}public_bd_territory] bt WHERE bt.id = ubt.bd_territory_id)
    ''')
    orphan_bd = cursor.fetchone()[0]
    print(f"   🔗 users_id orphans: {orphan_users}" + (" ⚠️" if orphan_users > 0 else " ✅"))
    print(f"   🔗 bd_territory_id orphans: {orphan_bd}" + (" ⚠️" if orphan_bd > 0 else " ✅"))
    
    # bd_territory_bazaars bridge
    print("\n📋 public_bd_territory_bazaars:")
    cursor.execute(f'''
        SELECT COUNT(*) as total,
               COUNT(DISTINCT bd_territory_id) as unique_bd_territories,
               COUNT(DISTINCT bazaar_id) as unique_bazaars
        FROM [{PREFIX}public_bd_territory_bazaars]
    ''')
    row = cursor.fetchone()
    print(f"   Total: {row[0]}, BD Territories: {row[1]}, Bazaars: {row[2]}")
    
    cursor.execute(f'''
        SELECT COUNT(*) FROM [{PREFIX}public_bd_territory_bazaars] btb
        WHERE NOT EXISTS (SELECT 1 FROM [{PREFIX}public_bd_territory] bt WHERE bt.id = btb.bd_territory_id)
    ''')
    orphan_bd = cursor.fetchone()[0]
    cursor.execute(f'''
        SELECT COUNT(*) FROM [{PREFIX}public_bd_territory_bazaars] btb
        WHERE NOT EXISTS (SELECT 1 FROM [{PREFIX}public_bazaars] b WHERE b.id = btb.bazaar_id)
    ''')
    orphan_bazaar = cursor.fetchone()[0]
    print(f"   🔗 bd_territory_id orphans: {orphan_bd}" + (" ⚠️" if orphan_bd > 0 else " ✅"))
    print(f"   🔗 bazaar_id orphans: {orphan_bazaar}" + (" ⚠️" if orphan_bazaar > 0 else " ✅"))
    
    # territory_bazaar_list bridge
    print("\n📋 public_territory_bazaar_list:")
    cursor.execute(f'''
        SELECT COUNT(*) as total,
               COUNT(DISTINCT territory_id) as unique_territories,
               COUNT(DISTINCT bazaar_list_id) as unique_bazaars
        FROM [{PREFIX}public_territory_bazaar_list]
    ''')
    row = cursor.fetchone()
    print(f"   Total: {row[0]}, Territories: {row[1]}, Bazaars: {row[2]}")
    
    cursor.execute(f'''
        SELECT COUNT(*) FROM [{PREFIX}public_territory_bazaar_list] tbl
        WHERE NOT EXISTS (SELECT 1 FROM [{PREFIX}public_territory] t WHERE t.id = tbl.territory_id)
    ''')
    orphan_territory = cursor.fetchone()[0]
    cursor.execute(f'''
        SELECT COUNT(*) FROM [{PREFIX}public_territory_bazaar_list] tbl
        WHERE NOT EXISTS (SELECT 1 FROM [{PREFIX}public_bazaars] b WHERE b.id = tbl.bazaar_list_id)
    ''')
    orphan_bazaar = cursor.fetchone()[0]
    print(f"   🔗 territory_id orphans: {orphan_territory}" + (" ⚠️" if orphan_territory > 0 else " ✅"))
    print(f"   🔗 bazaar_list_id orphans: {orphan_bazaar}" + (" ⚠️" if orphan_bazaar > 0 else " ✅"))

def audit_bazaar_table(cursor):
    """Audit public_bazaars table"""
    print("\n" + "=" * 80)
    print("4. PUBLIC_BAZAARS TABLE AUDIT")
    print("=" * 80)
    
    cursor.execute(f'''
        SELECT COUNT(*) as total FROM [{PREFIX}public_bazaars]
    ''')
    row = cursor.fetchone()
    print(f"Total: {row[0]}")
    
    # FK: district_id -> public_districts
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_bazaars] b
        WHERE b.district_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_districts] d WHERE d.id = b.district_id)
    ''')
    row = cursor.fetchone()
    print(f"\n🔗 district_id → public_districts: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: upazilla_id -> public_upazilla
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_bazaars] b
        WHERE b.upazilla_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_upazilla] u WHERE u.id = b.upazilla_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 upazilla_id → public_upazilla: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))

def audit_bd_territory_table(cursor):
    """Audit public_bd_territory table"""
    print("\n" + "=" * 80)
    print("5. PUBLIC_BD_TERRITORY TABLE AUDIT")
    print("=" * 80)
    
    cursor.execute(f'''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN delete_status = 'NO' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN delete_status = 'YES' THEN 1 ELSE 0 END) as deleted
        FROM [{PREFIX}public_bd_territory]
    ''')
    row = cursor.fetchone()
    print(f"Total: {row[0]}, Active: {row[1]}, Deleted: {row[2]}")
    
    # FK: district_id -> public_districts
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_bd_territory] bt
        WHERE bt.district_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_districts] d WHERE d.id = bt.district_id)
    ''')
    row = cursor.fetchone()
    print(f"\n🔗 district_id → public_districts: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: upazilla_id -> public_upazilla
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_bd_territory] bt
        WHERE bt.upazilla_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_upazilla] u WHERE u.id = bt.upazilla_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 upazilla_id → public_upazilla: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))

def audit_potential_site_table(cursor):
    """Audit public_potential_site table"""
    print("\n" + "=" * 80)
    print("6. PUBLIC_POTENTIAL_SITE TABLE AUDIT")
    print("=" * 80)
    
    cursor.execute(f'''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN delete_status = 'NO' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN delete_status = 'YES' THEN 1 ELSE 0 END) as deleted
        FROM [{PREFIX}public_potential_site]
    ''')
    row = cursor.fetchone()
    print(f"Total: {row[0]}, Active: {row[1]}, Deleted: {row[2]}")
    
    # FK: bazaar_id -> public_bazaars
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_potential_site] ps
        WHERE ps.bazaar_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_bazaars] b WHERE b.id = ps.bazaar_id)
    ''')
    row = cursor.fetchone()
    print(f"\n🔗 bazaar_id → public_bazaars: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: contractor_id -> public_contractor
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_potential_site] ps
        WHERE ps.contractor_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_contractor] c WHERE c.id = ps.contractor_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 contractor_id → public_contractor: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: engineer_id -> public_engineers
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_potential_site] ps
        WHERE ps.engineer_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_engineers] e WHERE e.id = ps.engineer_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 engineer_id → public_engineers: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: employee_id -> public_users (employee_id is the user who created/owns the site)
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_potential_site] ps
        WHERE ps.employee_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_users] u WHERE u.id = ps.employee_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 employee_id → public_users: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: territory_id -> public_territory
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_potential_site] ps
        WHERE ps.territory_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_territory] t WHERE t.id = ps.territory_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 territory_id → public_territory: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: bd_territory_id -> public_bd_territory
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_potential_site] ps
        WHERE ps.bd_territory_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_bd_territory] bt WHERE bt.id = ps.bd_territory_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 bd_territory_id → public_bd_territory: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))

def audit_user_orders_table(cursor):
    """Audit public_user_orders table"""
    print("\n" + "=" * 80)
    print("7. PUBLIC_USER_ORDERS TABLE AUDIT")
    print("=" * 80)
    
    cursor.execute(f'''
        SELECT COUNT(*) as total FROM [{PREFIX}public_user_orders]
    ''')
    row = cursor.fetchone()
    print(f"Total: {row[0]}")
    
    # FK: site_id -> public_potential_site
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_user_orders] uo
        WHERE uo.site_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_potential_site] ps WHERE ps.id = uo.site_id)
    ''')
    row = cursor.fetchone()
    print(f"\n🔗 site_id → public_potential_site: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: bazaar_id -> public_bazaars
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_user_orders] uo
        WHERE uo.bazaar_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_bazaars] b WHERE b.id = uo.bazaar_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 bazaar_id → public_bazaars: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: dealer_id -> public_dealers
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_user_orders] uo
        WHERE uo.dealer_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_dealers] d WHERE d.id = uo.dealer_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 dealer_id → public_dealers: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: created_by -> public_users
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_user_orders] uo
        WHERE uo.created_by IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_users] u WHERE u.id = uo.created_by)
    ''')
    row = cursor.fetchone()
    print(f"🔗 created_by → public_users: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # Order status distribution
    cursor.execute(f'''
        SELECT order_status, COUNT(*) as cnt
        FROM [{PREFIX}public_user_orders]
        GROUP BY order_status
        ORDER BY cnt DESC
    ''')
    print("\nOrder Status Distribution:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")

def audit_visits_table(cursor):
    """Audit public_visits table"""
    print("\n" + "=" * 80)
    print("8. PUBLIC_VISITS TABLE AUDIT")
    print("=" * 80)
    
    cursor.execute(f'''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN delete_status = 'NO' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN delete_status = 'YES' THEN 1 ELSE 0 END) as deleted
        FROM [{PREFIX}public_visits]
    ''')
    row = cursor.fetchone()
    print(f"Total: {row[0]}, Active: {row[1]}, Deleted: {row[2]}")
    
    # FK: potential_site_id -> public_potential_site
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_visits] v
        WHERE v.potential_site_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_potential_site] ps WHERE ps.id = v.potential_site_id)
    ''')
    row = cursor.fetchone()
    print(f"\n🔗 potential_site_id → public_potential_site: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: created_by_id -> public_users
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_visits] v
        WHERE v.created_by_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_users] u WHERE u.id = v.created_by_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 created_by_id → public_users: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: visit_category_id -> public_visit_categories
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_visits] v
        WHERE v.visit_category_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_visit_categories] vc WHERE vc.id = v.visit_category_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 visit_category_id → public_visit_categories: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: visit_phase_id -> public_visit_phases
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_visits] v
        WHERE v.visit_phase_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_visit_phases] vp WHERE vp.id = v.visit_phase_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 visit_phase_id → public_visit_phases: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: visit_stage_id -> public_visit_stages
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_visits] v
        WHERE v.visit_stage_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_visit_stages] vs WHERE vs.id = v.visit_stage_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 visit_stage_id → public_visit_stages: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # FK: organization_id -> public_organization
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_visits] v
        WHERE v.organization_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_organization] o WHERE o.id = v.organization_id)
    ''')
    row = cursor.fetchone()
    print(f"🔗 organization_id → public_organization: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))

def audit_client_table(cursor):
    """Audit public_client table"""
    print("\n" + "=" * 80)
    print("9. PUBLIC_CLIENT TABLE AUDIT")
    print("=" * 80)
    
    cursor.execute(f'''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_deleted = 'NO' OR is_deleted IS NULL THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN is_deleted = 'YES' THEN 1 ELSE 0 END) as deleted
        FROM [{PREFIX}public_client]
    ''')
    row = cursor.fetchone()
    print(f"Total: {row[0]}, Active: {row[1]}, Deleted: {row[2]}")
    
    # FK: upazilla_id -> public_upazilla
    cursor.execute(f'''
        SELECT COUNT(*) as orphans
        FROM [{PREFIX}public_client] c
        WHERE c.upazilla_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM [{PREFIX}public_upazilla] u WHERE u.id = c.upazilla_id)
    ''')
    row = cursor.fetchone()
    print(f"\n🔗 upazilla_id → public_upazilla: {row[0]} orphan records" + (" ⚠️" if row[0] > 0 else " ✅"))
    
    # Client type distribution
    cursor.execute(f'''
        SELECT client_type, COUNT(*) as cnt
        FROM [{PREFIX}public_client]
        WHERE is_deleted = 'NO' OR is_deleted IS NULL
        GROUP BY client_type
        ORDER BY cnt DESC
    ''')
    print("\nClient Type Distribution:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")

def audit_contractor_engineer_tables(cursor):
    """Audit public_contractor and public_engineers tables"""
    print("\n" + "=" * 80)
    print("10. PUBLIC_CONTRACTOR & PUBLIC_ENGINEERS AUDIT")
    print("=" * 80)
    
    # Contractor - has different structure (no delete_status, links via potential_site)
    cursor.execute(f'''
        SELECT COUNT(*) as total FROM [{PREFIX}public_contractor]
    ''')
    row = cursor.fetchone()
    print(f"Contractors - Total: {row[0]}")
    
    # Check contractor usage in potential_site
    cursor.execute(f'''
        SELECT COUNT(DISTINCT contractor_id) as used_contractors
        FROM [{PREFIX}public_potential_site]
        WHERE contractor_id IS NOT NULL
    ''')
    row = cursor.fetchone()
    print(f"   Contractors used in potential_site: {row[0]}")
    
    # Engineers - has different structure
    cursor.execute(f'''
        SELECT COUNT(*) as total FROM [{PREFIX}public_engineers]
    ''')
    row = cursor.fetchone()
    print(f"\nEngineers - Total: {row[0]}")
    
    # Check engineer usage in potential_site
    cursor.execute(f'''
        SELECT COUNT(DISTINCT engineer_id) as used_engineers
        FROM [{PREFIX}public_potential_site]
        WHERE engineer_id IS NOT NULL
    ''')
    row = cursor.fetchone()
    print(f"   Engineers used in potential_site: {row[0]}")
    
    # Engineer type distribution
    cursor.execute(f'''
        SELECT engineer_type, COUNT(*) as cnt
        FROM [{PREFIX}public_engineers]
        GROUP BY engineer_type
        ORDER BY cnt DESC
    ''')
    print("\n   Engineer Type Distribution:")
    for row in cursor.fetchall():
        print(f"      {row[0]}: {row[1]}")

def main():
    """Main function to run all audits"""
    try:
        conn = connect_fabric()
        cursor = conn.cursor()
        
        audit_users_table(cursor)
        audit_territory_table(cursor)
        audit_bridge_tables(cursor)
        audit_bazaar_table(cursor)
        audit_bd_territory_table(cursor)
        audit_potential_site_table(cursor)
        audit_user_orders_table(cursor)
        audit_visits_table(cursor)
        audit_client_table(cursor)
        audit_contractor_engineer_tables(cursor)
        
        print("\n" + "=" * 80)
        print("✅ PUBLIC TABLES AUDIT COMPLETE")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
