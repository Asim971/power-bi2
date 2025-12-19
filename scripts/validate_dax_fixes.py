#!/usr/bin/env python3
"""
DAX Fix Validation Script
=========================
Validates expected results for DAX measure fixes against Fabric SQL endpoint.

Issues being validated:
1. Fact_ProjectConversion removal - measures should still work without it
2. Territory counts - validate unique territories with non-null territory_id
3. Zone mismatch detection - identify visits where territory source differs

Run: python scripts/validate_dax_fixes.py
"""

import struct
from azure.identity import AzureCliCredential

# Fabric SQL Endpoint
SERVER = "namszb3yfzwe7jrxyxgifsnf2a-45bwuj7d4btehgwbidi36uqyf4.datawarehouse.fabric.microsoft.com"
DATABASE = "BMD_Sales"
TABLE_PREFIX = "sm_bmd_sales_"

def get_connection():
    """Get pyodbc connection with Azure AD token."""
    import pyodbc
    
    credential = AzureCliCredential()
    token = credential.get_token("https://database.windows.net/.default")
    token_bytes = token.token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )
    
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    conn = pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    return conn

def run_validation():
    """Run all validation queries."""
    print("=" * 60)
    print("DAX FIX VALIDATION")
    print("=" * 60)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # ================================================================
    # VALIDATION 1: Client counts without Fact_ProjectConversion
    # ================================================================
    print("\n📊 VALIDATION 1: Client Counts (for measures removing Fact_ProjectConversion)")
    print("-" * 60)
    
    # Total clients by type
    query = f"""
    SELECT 
        client_type,
        COUNT(DISTINCT id) as client_count
    FROM {TABLE_PREFIX}public_client
    WHERE is_deleted = 'NO' OR is_deleted IS NULL
    GROUP BY client_type
    ORDER BY client_count DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print("\nClient counts by type (from public_client):")
    for row in rows:
        print(f"  {row[0]}: {row[1]:,}")
    
    # ================================================================
    # VALIDATION 2: Territory counts
    # ================================================================
    print("\n📊 VALIDATION 2: Territory Counts")
    print("-" * 60)
    
    # Unique territories from visits (simulating new logic)
    query = f"""
    SELECT 
        COUNT(DISTINCT v.territory_id) as visit_territories_from_source,
        COUNT(DISTINCT COALESCE(v.territory_id, ut.territory_id)) as visit_territories_with_employee_fallback
    FROM {TABLE_PREFIX}public_visits v
    LEFT JOIN {TABLE_PREFIX}public_users_territory ut ON v.created_by_id = ut.users_id
    WHERE v.delete_status = 'NO'
    """
    cursor.execute(query)
    row = cursor.fetchone()
    print(f"\nUnique territories in visits:")
    print(f"  From source territory_id: {row[0]}")
    print(f"  With employee fallback: {row[1]}")
    
    # Territory breakdown
    query = f"""
    SELECT 
        CASE 
            WHEN v.territory_id IS NOT NULL THEN 'GPS'
            WHEN ut.territory_id IS NOT NULL THEN 'Employee'
            ELSE 'Unknown'
        END as territory_source,
        COUNT(*) as visit_count
    FROM {TABLE_PREFIX}public_visits v
    LEFT JOIN (
        SELECT users_id, MIN(territory_id) as territory_id
        FROM {TABLE_PREFIX}public_users_territory
        GROUP BY users_id
    ) ut ON v.created_by_id = ut.users_id
    WHERE v.delete_status = 'NO'
    GROUP BY 
        CASE 
            WHEN v.territory_id IS NOT NULL THEN 'GPS'
            WHEN ut.territory_id IS NOT NULL THEN 'Employee'
            ELSE 'Unknown'
        END
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"\nVisits by territory source:")
    for row in rows:
        print(f"  {row[0]}: {row[1]:,}")
    
    # ================================================================
    # VALIDATION 3: Zone mismatch detection
    # ================================================================
    print("\n📊 VALIDATION 3: Zone Mismatch Detection")
    print("-" * 60)
    
    # Check if employee's assigned territory zone matches visit territory zone
    query = f"""
    WITH VisitWithZones AS (
        SELECT 
            v.id as visit_id,
            v.created_by_id,
            v.territory_id as visit_territory_id,
            vt.zone_name as visit_zone,
            ut.territory_id as emp_territory_id,
            et.zone_name as emp_zone
        FROM {TABLE_PREFIX}public_visits v
        LEFT JOIN {TABLE_PREFIX}public_territory vt ON v.territory_id = vt.id
        LEFT JOIN (
            SELECT users_id, MIN(territory_id) as territory_id
            FROM {TABLE_PREFIX}public_users_territory
            GROUP BY users_id
        ) ut ON v.created_by_id = ut.users_id
        LEFT JOIN {TABLE_PREFIX}public_territory et ON ut.territory_id = et.id
        WHERE v.delete_status = 'NO'
    )
    SELECT 
        CASE 
            WHEN visit_zone IS NULL AND emp_zone IS NULL THEN 'Both Unknown'
            WHEN visit_zone IS NULL THEN 'Visit Zone Unknown'
            WHEN emp_zone IS NULL THEN 'Emp Zone Unknown'
            WHEN visit_zone = emp_zone THEN 'Match'
            ELSE 'Mismatch'
        END as zone_status,
        COUNT(*) as visit_count
    FROM VisitWithZones
    GROUP BY 
        CASE 
            WHEN visit_zone IS NULL AND emp_zone IS NULL THEN 'Both Unknown'
            WHEN visit_zone IS NULL THEN 'Visit Zone Unknown'
            WHEN emp_zone IS NULL THEN 'Emp Zone Unknown'
            WHEN visit_zone = emp_zone THEN 'Match'
            ELSE 'Mismatch'
        END
    ORDER BY visit_count DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"\nZone match status:")
    for row in rows:
        print(f"  {row[0]}: {row[1]:,}")
    
    # ================================================================
    # VALIDATION 4: Bazaar-linked clients (for User-Bazaar measures)
    # ================================================================
    print("\n📊 VALIDATION 4: Bazaar-Linked Client Counts")
    print("-" * 60)
    
    # Clients with bazaar assignments
    query = f"""
    SELECT 
        c.client_type,
        COUNT(CASE WHEN COALESCE(i.bazaar_id, r.bazaar_id) IS NOT NULL THEN 1 END) as with_bazaar,
        COUNT(*) as total
    FROM {TABLE_PREFIX}public_client c
    LEFT JOIN {TABLE_PREFIX}public_ihb_registration i ON c.id = i.id AND c.client_type = 'IHB_REGISTRATION'
    LEFT JOIN {TABLE_PREFIX}public_uncovered_retailer r ON c.id = r.id AND c.client_type = 'UNCOVERED_RETAILER'
    WHERE c.is_deleted = 'NO' OR c.is_deleted IS NULL
    GROUP BY c.client_type
    ORDER BY total DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"\nClients with/without bazaar by type:")
    for row in rows:
        pct = (row[1] / row[2] * 100) if row[2] > 0 else 0
        print(f"  {row[0]}: {row[1]:,} with bazaar / {row[2]:,} total ({pct:.1f}%)")
    
    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    print("""
Next Steps:
1. Review the counts above
2. Compare with expected DAX measure results
3. Apply fixes to TMDL files
    """)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_validation()
