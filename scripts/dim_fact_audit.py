"""
Dim and Fact Tables Comprehensive Audit Script
================================================
Audits all Dimension and Fact tables in the BMD Sales semantic model
against the Fabric SQL endpoint source tables.

Author: Generated for BMD Sales Model
Date: December 2025
"""

import pyodbc
from azure.identity import AzureCliCredential
import struct

# Fabric SQL endpoint connection
SERVER = "namszb3yfzwe7jrxyxgifsnf2a-45bwuj7d4btehgwbidi36uqyf4.datawarehouse.fabric.microsoft.com"
DATABASE = "BMD_Sales"
TABLE_PREFIX = "sm_bmd_sales_"

def get_connection():
    """Get connection using Azure AD authentication"""
    credential = AzureCliCredential()
    token = credential.get_token("https://database.windows.net//.default")
    token_bytes = token.token.encode('utf-16-le')
    token_struct = struct.pack('<I', len(token_bytes)) + token_bytes
    
    conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={SERVER};Database={DATABASE};"
    conn = pyodbc.connect(conn_str, attrs_before={1256: token_struct})
    return conn

def run_query(conn, query, description=""):
    """Run a query and return results"""
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()
        return columns, results
    except Exception as e:
        print(f"ERROR in {description}: {e}")
        return None, None

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_results(columns, results, max_rows=10):
    if not columns or not results:
        print("  No results or error")
        return
    
    # Print header
    header = " | ".join(f"{col:20s}" for col in columns[:5])
    print(f"  {header}")
    print("  " + "-" * 100)
    
    # Print rows
    for row in results[:max_rows]:
        row_str = " | ".join(f"{str(val)[:20]:20s}" for val in row[:5])
        print(f"  {row_str}")
    
    if len(results) > max_rows:
        print(f"  ... and {len(results) - max_rows} more rows")

# =============================================================================
# 1. Dim_Site Audit
# =============================================================================
def audit_dim_site(conn):
    print_section("1. DIM_SITE AUDIT")
    
    # 1.1 Basic counts
    print("\n--- 1.1 Row Counts ---")
    _, results = run_query(conn, f"""
        SELECT 
            (SELECT COUNT(*) FROM {TABLE_PREFIX}public_potential_site) AS source_total,
            (SELECT COUNT(*) FROM {TABLE_PREFIX}public_potential_site WHERE UPPER(delete_status) IN ('NO', 'N', '0', 'FALSE') OR delete_status IS NULL) AS source_active
    """, "Site counts")
    if results:
        print(f"  Source Total: {results[0][0]}, Active (not deleted): {results[0][1]}")
        print("  Expected Dim_Site rows: ~{0}".format(results[0][1]))
    
    # 1.2 FK Integrity - EngineerID
    print("\n--- 1.2 FK: EngineerID -> Dim_Engineer (public client where type=ENGINEER) ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as orphan_count
        FROM {TABLE_PREFIX}public_potential_site ps
        WHERE ps.engineer_id IS NOT NULL
        AND ps.engineer_id NOT IN (
            SELECT id FROM {TABLE_PREFIX}public_client WHERE client_type = 'ENGINEER'
        )
    """, "Engineer FK check")
    if results:
        count = results[0][0]
        status = "✅ PASS" if count == 0 else f"⚠️ WARNING: {count} orphan records"
        print(f"  EngineerID integrity: {status}")
    
    # 1.3 FK Integrity - ContractorID
    print("\n--- 1.3 FK: ContractorID -> Dim_Contractor (public client where type=CONTRACTOR) ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as orphan_count
        FROM {TABLE_PREFIX}public_potential_site ps
        WHERE ps.contractor_id IS NOT NULL
        AND ps.contractor_id NOT IN (
            SELECT id FROM {TABLE_PREFIX}public_client WHERE client_type = 'CONTRACTOR'
        )
    """, "Contractor FK check")
    if results:
        count = results[0][0]
        status = "✅ PASS" if count == 0 else f"⚠️ WARNING: {count} orphan records"
        print(f"  ContractorID integrity: {status}")
    
    # 1.4 FK Integrity - BazaarID
    print("\n--- 1.4 FK: BazaarID -> Dim_Bazaar (public bazaars) ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as orphan_count
        FROM {TABLE_PREFIX}public_potential_site ps
        WHERE ps.bazaar_id IS NOT NULL
        AND ps.bazaar_id NOT IN (
            SELECT id FROM {TABLE_PREFIX}public_bazaars
        )
    """, "Bazaar FK check")
    if results:
        count = results[0][0]
        status = "✅ PASS" if count == 0 else f"⚠️ WARNING: {count} orphan records"
        print(f"  BazaarID integrity: {status}")
    
    # 1.5 Status distribution
    print("\n--- 1.5 Status Distribution ---")
    cols, results = run_query(conn, f"""
        SELECT status, COUNT(*) as cnt
        FROM {TABLE_PREFIX}public_potential_site
        WHERE UPPER(delete_status) IN ('NO', 'N', '0', 'FALSE') OR delete_status IS NULL
        GROUP BY status
        ORDER BY cnt DESC
    """, "Status distribution")
    print_results(cols, results)
    
    # 1.6 ConvertedSiteStatus distribution
    print("\n--- 1.6 Converted Site Status Distribution ---")
    cols, results = run_query(conn, f"""
        SELECT converted_site_status, COUNT(*) as cnt
        FROM {TABLE_PREFIX}public_potential_site
        WHERE UPPER(delete_status) IN ('NO', 'N', '0', 'FALSE') OR delete_status IS NULL
        GROUP BY converted_site_status
        ORDER BY cnt DESC
    """, "Converted status distribution")
    print_results(cols, results)

# =============================================================================
# 2. Dim_User Audit
# =============================================================================
def audit_dim_user(conn):
    print_section("2. DIM_USER AUDIT")
    
    # 2.1 Basic counts
    print("\n--- 2.1 Row Counts ---")
    _, results = run_query(conn, f"""
        SELECT 
            (SELECT COUNT(*) FROM {TABLE_PREFIX}public_users) AS source_total,
            (SELECT COUNT(*) FROM {TABLE_PREFIX}public_users WHERE delete_status = 'NO') AS source_active
    """, "User counts")
    if results:
        print(f"  Source Total: {results[0][0]}, Active: {results[0][1]}")
    
    # 2.2 FK: role_id -> public role
    print("\n--- 2.2 FK: role_id -> public role ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as orphan_count
        FROM {TABLE_PREFIX}public_users u
        WHERE u.role_id IS NOT NULL
        AND u.role_id NOT IN (SELECT id FROM {TABLE_PREFIX}public_role)
    """, "Role FK check")
    if results:
        count = results[0][0]
        status = "✅ PASS" if count == 0 else f"⚠️ WARNING: {count} orphan records"
        print(f"  role_id integrity: {status}")
    
    # 2.3 FK: organization_id -> public organization
    print("\n--- 2.3 FK: organization_id -> public organization (NULL allowed for BDO/CRO) ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as orphan_count
        FROM {TABLE_PREFIX}public_users u
        WHERE u.organization_id IS NOT NULL
        AND u.organization_id NOT IN (SELECT id FROM {TABLE_PREFIX}public_organization)
    """, "Organization FK check")
    if results:
        count = results[0][0]
        status = "✅ PASS" if count == 0 else f"⚠️ WARNING: {count} orphan records"
        print(f"  organization_id integrity: {status}")
    
    # 2.4 Users with NULL organization_id (expected for BDO/CRO)
    print("\n--- 2.4 Users with NULL organization_id (BDO/CRO roles) ---")
    cols, results = run_query(conn, f"""
        SELECT r.name as role_name, COUNT(*) as cnt
        FROM {TABLE_PREFIX}public_users u
        LEFT JOIN {TABLE_PREFIX}public_role r ON u.role_id = r.id
        WHERE u.organization_id IS NULL AND u.delete_status = 'NO'
        GROUP BY r.name
        ORDER BY cnt DESC
    """, "NULL org users")
    print_results(cols, results)
    
    # 2.5 Role distribution
    print("\n--- 2.5 Role Distribution ---")
    cols, results = run_query(conn, f"""
        SELECT r.name as role_name, r.department, COUNT(*) as user_count
        FROM {TABLE_PREFIX}public_users u
        JOIN {TABLE_PREFIX}public_role r ON u.role_id = r.id
        WHERE u.delete_status = 'NO'
        GROUP BY r.name, r.department
        ORDER BY user_count DESC
    """, "Role distribution")
    print_results(cols, results)
    
    # 2.6 Territory assignment check (ORG track)
    print("\n--- 2.6 Territory Assignment (users_territory bridge) ---")
    _, results = run_query(conn, f"""
        SELECT 
            (SELECT COUNT(DISTINCT users_id) FROM {TABLE_PREFIX}public_users_territory) as users_with_territory,
            (SELECT COUNT(*) FROM {TABLE_PREFIX}public_users WHERE delete_status = 'NO') as total_active_users
    """, "Territory assignment")
    if results:
        print(f"  Users with territory assignment: {results[0][0]} / {results[0][1]} active users")

# =============================================================================
# 3. Dim_Territory Audit
# =============================================================================
def audit_dim_territory(conn):
    print_section("3. DIM_TERRITORY AUDIT")
    
    # 3.1 Basic counts
    print("\n--- 3.1 Row Counts ---")
    _, results = run_query(conn, f"""
        SELECT 
            (SELECT COUNT(*) FROM {TABLE_PREFIX}public_territory) AS source_total,
            (SELECT COUNT(*) FROM {TABLE_PREFIX}public_territory WHERE delete_status = 'NO') AS source_active
    """, "Territory counts")
    if results:
        print(f"  Source Total: {results[0][0]}, Active: {results[0][1]}")
    
    # 3.2 FK: organization_id -> public organization
    print("\n--- 3.2 FK: organization_id -> public organization ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as orphan_count
        FROM {TABLE_PREFIX}public_territory t
        WHERE t.organization_id IS NOT NULL
        AND t.organization_id NOT IN (SELECT id FROM {TABLE_PREFIX}public_organization)
    """, "Org FK check")
    if results:
        count = results[0][0]
        status = "✅ PASS" if count == 0 else f"⚠️ WARNING: {count} orphan records"
        print(f"  organization_id integrity: {status}")
    
    # 3.3 Hierarchy check
    print("\n--- 3.3 Geographic Hierarchy Distribution ---")
    cols, results = run_query(conn, f"""
        SELECT zone_name, COUNT(*) as territory_count
        FROM {TABLE_PREFIX}public_territory
        WHERE delete_status = 'NO'
        GROUP BY zone_name
        ORDER BY territory_count DESC
    """, "Zone distribution")
    print_results(cols, results)

# =============================================================================
# 4. Dim_Bazaar Audit
# =============================================================================
def audit_dim_bazaar(conn):
    print_section("4. DIM_BAZAAR AUDIT")
    
    # 4.1 Basic counts
    print("\n--- 4.1 Row Counts ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as total FROM {TABLE_PREFIX}public_bazaars
    """, "Bazaar counts")
    if results:
        print(f"  Source Total: {results[0][0]}")
        print("  Note: Dim_Bazaar adds 1 'National' row (BazaarID=-1) for Dealers/Engineers/Contractors")
    
    # 4.2 Check bd_territory_bazaars bridge
    print("\n--- 4.2 BD Territory -> Bazaar Links (bd_territory_bazaars) ---")
    _, results = run_query(conn, f"""
        SELECT 
            COUNT(*) as total_links,
            COUNT(DISTINCT bd_territory_id) as distinct_bd_territories,
            COUNT(DISTINCT bazaar_id) as distinct_bazaars
        FROM {TABLE_PREFIX}public_bd_territory_bazaars
    """, "BD Territory Bazaar links")
    if results:
        print(f"  Total links: {results[0][0]}, Distinct BD Territories: {results[0][1]}, Distinct Bazaars: {results[0][2]}")
    
    # 4.3 Check territory_bazaar_list bridge
    print("\n--- 4.3 Territory -> Bazaar Links (territory_bazaar_list) ---")
    _, results = run_query(conn, f"""
        SELECT 
            COUNT(*) as total_links,
            COUNT(DISTINCT territory_id) as distinct_territories,
            COUNT(DISTINCT bazaar_list_id) as distinct_bazaars
        FROM {TABLE_PREFIX}public_territory_bazaar_list
    """, "Territory Bazaar links")
    if results:
        print(f"  Total links: {results[0][0]}, Distinct Territories: {results[0][1]}, Distinct Bazaars: {results[0][2]}")
    
    # 4.4 Bazaars without BD territory link
    print("\n--- 4.4 Bazaars without BD Territory Link (potential issue) ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as orphan_count
        FROM {TABLE_PREFIX}public_bazaars b
        WHERE b.id NOT IN (
            SELECT bazaar_id FROM {TABLE_PREFIX}public_bd_territory_bazaars
        )
    """, "Orphan bazaars")
    if results:
        count = results[0][0]
        status = "✅ PASS" if count == 0 else f"ℹ️ INFO: {count} bazaars without BD territory link"
        print(f"  {status}")

# =============================================================================
# 5. Dim_BDTerritory Audit
# =============================================================================
def audit_dim_bd_territory(conn):
    print_section("5. DIM_BDTERRITORY AUDIT")
    
    # 5.1 Basic counts
    print("\n--- 5.1 Row Counts ---")
    _, results = run_query(conn, f"""
        SELECT 
            (SELECT COUNT(*) FROM {TABLE_PREFIX}public_bd_territory) AS source_total,
            (SELECT COUNT(*) FROM {TABLE_PREFIX}public_bd_territory WHERE delete_status = 'NO') AS source_active
    """, "BD Territory counts")
    if results:
        print(f"  Source Total: {results[0][0]}, Active: {results[0][1]}")
    
    # 5.2 User assignment (users_bd_territory bridge)
    print("\n--- 5.2 User Assignment (users_bd_territory bridge) ---")
    _, results = run_query(conn, f"""
        SELECT 
            COUNT(*) as total_links,
            COUNT(DISTINCT users_id) as distinct_users,
            COUNT(DISTINCT bd_territory_id) as distinct_bd_territories
        FROM {TABLE_PREFIX}public_users_bd_territory
    """, "BD Territory user links")
    if results:
        print(f"  Total links: {results[0][0]}, Distinct Users: {results[0][1]}, Distinct BD Territories: {results[0][2]}")
    
    # 5.3 BD Territories without users
    print("\n--- 5.3 BD Territories without User Assignment ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as orphan_count
        FROM {TABLE_PREFIX}public_bd_territory t
        WHERE t.delete_status = 'NO'
        AND t.id NOT IN (
            SELECT bd_territory_id FROM {TABLE_PREFIX}public_users_bd_territory
        )
    """, "BD Territory without users")
    if results:
        count = results[0][0]
        status = "✅ PASS" if count == 0 else f"ℹ️ INFO: {count} BD territories without user assignment"
        print(f"  {status}")

# =============================================================================
# 6. Dim_Engineer Audit
# =============================================================================
def audit_dim_engineer(conn):
    print_section("6. DIM_ENGINEER AUDIT")
    
    # 6.1 Basic counts
    print("\n--- 6.1 Row Counts ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as engineer_count
        FROM {TABLE_PREFIX}public_client
        WHERE client_type = 'ENGINEER'
    """, "Engineer counts")
    if results:
        print(f"  Engineers in source (public client where client_type='ENGINEER'): {results[0][0]}")
    
    # 6.2 Engineers with sites
    print("\n--- 6.2 Engineers Assigned to Sites ---")
    _, results = run_query(conn, f"""
        SELECT 
            COUNT(DISTINCT ps.engineer_id) as engineers_with_sites,
            COUNT(*) as total_site_assignments
        FROM {TABLE_PREFIX}public_potential_site ps
        WHERE ps.engineer_id IS NOT NULL
        AND (UPPER(delete_status) IN ('NO', 'N', '0', 'FALSE') OR delete_status IS NULL)
    """, "Engineers with sites")
    if results:
        print(f"  Engineers with sites: {results[0][0]}, Total site assignments: {results[0][1]}")
    
    # 6.3 Engineers with eligible orders (is_engineer_eligible=true, boolean in Fabric)
    print("\n--- 6.3 Engineers with Eligible Orders (is_engineer_eligible=true) ---")
    _, results = run_query(conn, f"""
        SELECT 
            COUNT(*) as eligible_orders,
            COUNT(DISTINCT uo.site_id) as distinct_sites
        FROM {TABLE_PREFIX}public_user_orders uo
        WHERE uo.is_engineer_eligible = 1
    """, "Engineer eligible orders")
    if results:
        print(f"  Engineer-eligible orders: {results[0][0]}, Distinct sites: {results[0][1]}")

# =============================================================================
# 7. Dim_Contractor Audit
# =============================================================================
def audit_dim_contractor(conn):
    print_section("7. DIM_CONTRACTOR AUDIT")
    
    # 7.1 Basic counts
    print("\n--- 7.1 Row Counts ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as contractor_count
        FROM {TABLE_PREFIX}public_client
        WHERE client_type = 'CONTRACTOR'
    """, "Contractor counts")
    if results:
        print(f"  Contractors in source (public client where client_type='CONTRACTOR'): {results[0][0]}")
    
    # 7.2 Contractors with sites
    print("\n--- 7.2 Contractors Assigned to Sites ---")
    _, results = run_query(conn, f"""
        SELECT 
            COUNT(DISTINCT ps.contractor_id) as contractors_with_sites,
            COUNT(*) as total_site_assignments
        FROM {TABLE_PREFIX}public_potential_site ps
        WHERE ps.contractor_id IS NOT NULL
        AND (UPPER(delete_status) IN ('NO', 'N', '0', 'FALSE') OR delete_status IS NULL)
    """, "Contractors with sites")
    if results:
        print(f"  Contractors with sites: {results[0][0]}, Total site assignments: {results[0][1]}")
    
    # 7.3 Contractors with eligible orders (is_partner_eligible, boolean in Fabric)
    print("\n--- 7.3 Partner-Eligible Orders (is_partner_eligible=true) ---")
    _, results = run_query(conn, f"""
        SELECT 
            COUNT(*) as eligible_orders,
            COUNT(DISTINCT uo.site_id) as distinct_sites
        FROM {TABLE_PREFIX}public_user_orders uo
        WHERE uo.is_partner_eligible = 1
    """, "Partner eligible orders")
    if results:
        print(f"  Partner-eligible orders: {results[0][0]}, Distinct sites: {results[0][1]}")

# =============================================================================
# 8. Dim_Client_Simple Audit
# =============================================================================
def audit_dim_client_simple(conn):
    print_section("8. DIM_CLIENT_SIMPLE AUDIT")
    
    # 8.1 Client type distribution
    print("\n--- 8.1 Client Type Distribution ---")
    cols, results = run_query(conn, f"""
        SELECT client_type, COUNT(*) as cnt
        FROM {TABLE_PREFIX}public_client
        GROUP BY client_type
        ORDER BY cnt DESC
    """, "Client type distribution")
    print_results(cols, results)
    
    # 8.2 EntityGroup mapping check
    print("\n--- 8.2 EntityGroup Mapping (6 types expected) ---")
    print("  Expected mapping:")
    print("  - DEALER -> Customers")
    print("  - RETAILER -> Customers")
    print("  - POTENTIAL_SITE/IHB_REGISTRATION -> Consumers")
    print("  - ENGINEER -> Influencers")
    print("  - CONTRACTOR -> Influencers")
    print("  - HEAD_MASON -> Influencers")
    
    # 8.3 Note about client table structure
    print("\n--- 8.3 Client Table Structure Note ---")
    print("  Note: public_client does NOT have bazaar_id column")
    print("  Bazaar links are through entity-specific tables (IHB, Contractor, etc.)")
    print("  Each client type may have different source tables for geographic info")

# =============================================================================
# 9. Fact_Visit Audit
# =============================================================================
def audit_fact_visit(conn):
    print_section("9. FACT_VISIT AUDIT")
    
    # 9.1 Basic counts
    print("\n--- 9.1 Row Counts ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as total_visits
        FROM {TABLE_PREFIX}public_visits
    """, "Visit counts")
    if results:
        print(f"  Total visits in source: {results[0][0]}")
    
    # 9.2 FK: created_by_id -> Dim_User (visits use created_by_id, not employee_id)
    print("\n--- 9.2 FK: created_by_id -> Dim_User (public users) ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as orphan_count
        FROM {TABLE_PREFIX}public_visits v
        WHERE v.created_by_id IS NOT NULL
        AND v.created_by_id NOT IN (SELECT id FROM {TABLE_PREFIX}public_users)
    """, "Visit employee FK check")
    if results:
        count = results[0][0]
        status = "✅ PASS" if count == 0 else f"⚠️ WARNING: {count} orphan records"
        print(f"  created_by_id integrity: {status}")
    
    # 9.3 Entity-based client references (visits link via entity_name + entity_record_id)
    print("\n--- 9.3 Visit Entity Distribution (client references) ---")
    cols, results = run_query(conn, f"""
        SELECT entity_name, COUNT(*) as cnt
        FROM {TABLE_PREFIX}public_visits
        GROUP BY entity_name
        ORDER BY cnt DESC
    """, "Visit entity distribution")
    print_results(cols, results)
    
    # 9.4 Visits by month
    print("\n--- 9.4 Visits by Month (recent) ---")
    cols, results = run_query(conn, f"""
        SELECT 
            FORMAT(CAST(visit_date_time AS DATE), 'yyyy-MM') as month,
            COUNT(*) as visit_count
        FROM {TABLE_PREFIX}public_visits
        WHERE visit_date_time IS NOT NULL
        GROUP BY FORMAT(CAST(visit_date_time AS DATE), 'yyyy-MM')
        ORDER BY month DESC
    """, "Visits by month")
    print_results(cols, results, 6)
    
    # 9.5 GPS capture rate (using latitude/longitude columns)
    print("\n--- 9.5 GPS Capture Analysis ---")
    _, results = run_query(conn, f"""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) as with_gps,
            ROUND(100.0 * SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) as gps_rate
        FROM {TABLE_PREFIX}public_visits
    """, "GPS analysis")
    if results:
        print(f"  Total: {results[0][0]}, With GPS: {results[0][1]}, GPS Rate: {results[0][2]}%")
    
    # 9.6 Territory coverage
    print("\n--- 9.6 Territory Coverage ---")
    _, results = run_query(conn, f"""
        SELECT 
            COUNT(DISTINCT territory_id) as territories_with_visits,
            (SELECT COUNT(*) FROM {TABLE_PREFIX}public_territory WHERE delete_status = 'NO') as total_territories
        FROM {TABLE_PREFIX}public_visits
        WHERE territory_id IS NOT NULL
    """, "Territory coverage")
    if results:
        print(f"  Territories with visits: {results[0][0]} / {results[0][1]} total")

# =============================================================================
# 10. Fact_UserOrders Audit
# =============================================================================
def audit_fact_user_orders(conn):
    print_section("10. FACT_USERORDERS AUDIT")
    
    # 10.1 Basic counts
    print("\n--- 10.1 Row Counts ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as total_orders
        FROM {TABLE_PREFIX}public_user_orders
    """, "Order counts")
    if results:
        print(f"  Total orders in source: {results[0][0]}")
    
    # 10.2 FK: site_id -> Dim_Site
    print("\n--- 10.2 FK: site_id -> Dim_Site (public potential_site) ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as orphan_count
        FROM {TABLE_PREFIX}public_user_orders uo
        WHERE uo.site_id IS NOT NULL
        AND uo.site_id NOT IN (SELECT id FROM {TABLE_PREFIX}public_potential_site)
    """, "Order site FK check")
    if results:
        count = results[0][0]
        status = "✅ PASS" if count == 0 else f"⚠️ WARNING: {count} orphan records"
        print(f"  site_id integrity: {status}")
    
    # 10.3 FK: bazaar_id -> Dim_Bazaar
    print("\n--- 10.3 FK: bazaar_id -> Dim_Bazaar (public bazaars) ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as orphan_count
        FROM {TABLE_PREFIX}public_user_orders uo
        WHERE uo.bazaar_id IS NOT NULL
        AND uo.bazaar_id NOT IN (SELECT id FROM {TABLE_PREFIX}public_bazaars)
    """, "Order bazaar FK check")
    if results:
        count = results[0][0]
        status = "✅ PASS" if count == 0 else f"⚠️ WARNING: {count} orphan records"
        print(f"  bazaar_id integrity: {status}")
    
    # 10.4 Order status distribution
    print("\n--- 10.4 Order Status Distribution ---")
    cols, results = run_query(conn, f"""
        SELECT order_status, COUNT(*) as cnt
        FROM {TABLE_PREFIX}public_user_orders
        GROUP BY order_status
        ORDER BY cnt DESC
    """, "Order status distribution")
    print_results(cols, results)
    
    # 10.5 Disbursement eligibility analysis (booleans are True/False in Fabric)
    print("\n--- 10.5 Disbursement Eligibility Analysis ---")
    _, results = run_query(conn, f"""
        SELECT 
            SUM(CASE WHEN is_engineer_eligible = 1 THEN 1 ELSE 0 END) as engineer_eligible,
            SUM(CASE WHEN is_partner_eligible = 1 THEN 1 ELSE 0 END) as partner_eligible,
            COUNT(*) as total
        FROM {TABLE_PREFIX}public_user_orders
    """, "Eligibility analysis")
    if results:
        print(f"  Engineer Eligible: {results[0][0]}, Partner Eligible: {results[0][1]}, Total: {results[0][2]}")
    
    # 10.6 Total amount analysis
    print("\n--- 10.6 Total Amount Analysis ---")
    _, results = run_query(conn, f"""
        SELECT 
            COUNT(*) as orders_with_amount,
            SUM(TRY_CAST(total_amount AS FLOAT)) as total_sum,
            AVG(TRY_CAST(total_amount AS FLOAT)) as avg_amount
        FROM {TABLE_PREFIX}public_user_orders
        WHERE total_amount IS NOT NULL AND total_amount != ''
    """, "Amount analysis")
    if results:
        print(f"  Orders with amount: {results[0][0]}, Total Sum: {results[0][1]}, Avg: {results[0][2]}")

# =============================================================================
# 11. Bridge Tables Audit
# =============================================================================
def audit_bridge_tables(conn):
    print_section("11. BRIDGE TABLES AUDIT")
    
    # 11.1 Bridge_UserBazaar (derived from users_bd_territory + bd_territory_bazaars)
    print("\n--- 11.1 Bridge_UserBazaar Logic Check ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(DISTINCT CONCAT(ubt.users_id, '-', btb.bazaar_id)) as expected_rows
        FROM {TABLE_PREFIX}public_users_bd_territory ubt
        JOIN {TABLE_PREFIX}public_bd_territory_bazaars btb ON ubt.bd_territory_id = btb.bd_territory_id
    """, "User-Bazaar bridge")
    if results:
        print(f"  Expected Bridge_UserBazaar rows (UserID-BazaarID pairs): {results[0][0]}")
    
    # 11.2 Bridge_UserTerritory (users_territory bridge)
    print("\n--- 11.2 Bridge_UserTerritory (users_territory) ---")
    _, results = run_query(conn, f"""
        SELECT 
            COUNT(*) as total_links,
            COUNT(DISTINCT users_id) as distinct_users,
            COUNT(DISTINCT territory_id) as distinct_territories
        FROM {TABLE_PREFIX}public_users_territory
    """, "User-Territory bridge")
    if results:
        print(f"  Total: {results[0][0]}, Distinct Users: {results[0][1]}, Distinct Territories: {results[0][2]}")
    
    # 11.3 Users in both bridges (ORG and BMD)
    print("\n--- 11.3 Users with Both Territory Types (ORG + BMD) ---")
    _, results = run_query(conn, f"""
        SELECT COUNT(*) as dual_track_users
        FROM (
            SELECT DISTINCT users_id FROM {TABLE_PREFIX}public_users_territory
        ) t
        WHERE users_id IN (
            SELECT DISTINCT users_id FROM {TABLE_PREFIX}public_users_bd_territory
        )
    """, "Dual track users")
    if results:
        print(f"  Users with both ORG territory and BD territory: {results[0][0]}")

# =============================================================================
# Main Execution
# =============================================================================
def main():
    print("\n" + "=" * 80)
    print("  BMD SALES MODEL - DIM/FACT TABLES COMPREHENSIVE AUDIT")
    print("  Fabric SQL Endpoint: " + SERVER[:50] + "...")
    print("=" * 80)
    
    try:
        conn = get_connection()
        print("\n✅ Connected to Fabric SQL endpoint successfully\n")
        
        # Run all audits
        audit_dim_site(conn)
        audit_dim_user(conn)
        audit_dim_territory(conn)
        audit_dim_bazaar(conn)
        audit_dim_bd_territory(conn)
        audit_dim_engineer(conn)
        audit_dim_contractor(conn)
        audit_dim_client_simple(conn)
        audit_fact_visit(conn)
        audit_fact_user_orders(conn)
        audit_bridge_tables(conn)
        
        # Summary
        print_section("AUDIT SUMMARY")
        print("""
  TABLES AUDITED:
  ✓ Dim_Site - Site dimension (potential_site source)
  ✓ Dim_User - Employee dimension (users source)
  ✓ Dim_Territory - Geographic hierarchy (territory source)
  ✓ Dim_Bazaar - Bazaar dimension (bazaars source)
  ✓ Dim_BDTerritory - BD Territory dimension (bd_territory source)
  ✓ Dim_Engineer - Engineer dimension (client where type=ENGINEER)
  ✓ Dim_Contractor - Contractor dimension (client where type=CONTRACTOR)
  ✓ Dim_Client_Simple - All clients unified dimension
  ✓ Fact_Visit - Visit fact table (visits source)
  ✓ Fact_UserOrders - User orders fact table (user_orders source)
  ✓ Bridge Tables - UserBazaar, UserTerritory
        """)
        
        conn.close()
        print("\n✅ Audit completed successfully!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
