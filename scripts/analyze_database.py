#!/usr/bin/env python3
"""
Database.xlsx Analysis Script
Analyzes the database tables to validate:
1. mainOrganizationName derivation from organization table
2. MT division logic for ACL vs AIL
3. ClientKey generation for different client types
4. UserID population from potential_site
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Path to the database file
DB_FILE = Path(__file__).parent.parent / "chat_history" / "Database.xlsx"

def load_all_sheets(file_path):
    """Load all sheets from the Excel file"""
    xl = pd.ExcelFile(file_path)
    sheets = {}
    print(f"📊 Found {len(xl.sheet_names)} sheets in Database.xlsx:")
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet)
        sheets[sheet] = df
        print(f"   - {sheet}: {len(df)} rows, {len(df.columns)} columns")
    return sheets

def analyze_organization(sheets):
    """Analyze organization table for mainOrganizationName fix"""
    print("\n" + "="*60)
    print("🏢 ORGANIZATION TABLE ANALYSIS")
    print("="*60)
    
    if 'organization' in sheets:
        org = sheets['organization']
        print(f"\nColumns: {list(org.columns)}")
        print(f"\nOrganization data:")
        print(org[['id', 'organization_name']].to_string() if 'organization_name' in org.columns else org.head())
        
        # Check for expected organizations
        print("\n✓ Expected mappings:")
        print("  - organization_id=1 → 'ANWAR CEMENT LTD' (ACL)")
        print("  - organization_id=2 → 'ANWAR ISPAT LTD' (AIL)")
        print("  - organization_id=NULL → 'AGI Group' (BD employees)")
        
        return org
    else:
        print("❌ 'organization' sheet not found!")
        print(f"   Available sheets: {list(sheets.keys())}")
        return None

def analyze_project_conversion(sheets):
    """Analyze project_conversion table for MT division and ClientKey issues"""
    print("\n" + "="*60)
    print("📈 PROJECT_CONVERSION TABLE ANALYSIS")
    print("="*60)
    
    # Try different possible sheet names
    pc_names = ['project_conversion', 'public project_conversion', 'public_project_conversion']
    pc = None
    for name in pc_names:
        if name in sheets:
            pc = sheets[name]
            break
    
    if pc is None:
        print("❌ 'project_conversion' sheet not found!")
        print(f"   Available sheets: {list(sheets.keys())}")
        return None
    
    print(f"\nColumns: {list(pc.columns)}")
    print(f"Total rows: {len(pc)}")
    
    # Check for site_id 1797 specifically (the problem case)
    if 'site_id' in pc.columns:
        site_1797 = pc[pc['site_id'] == 1797]
        print(f"\n🔍 Site ID 1797 Analysis (Problem Case):")
        print(f"   Records found: {len(site_1797)}")
        if len(site_1797) > 0:
            print(site_1797.to_string())
    
    # Check organization_id distribution
    if 'organization_id' in pc.columns:
        print(f"\n📊 Organization ID Distribution:")
        print(pc['organization_id'].value_counts(dropna=False))
    
    return pc

def analyze_order_items(sheets):
    """Analyze order_items for MT division validation"""
    print("\n" + "="*60)
    print("📦 ORDER_ITEMS TABLE ANALYSIS (MT Division)")
    print("="*60)
    
    # Try different possible sheet names
    oi_names = ['order_items', 'public order_items', 'public_order_items']
    oi = None
    for name in oi_names:
        if name in sheets:
            oi = sheets[name]
            break
    
    if oi is None:
        print("❌ 'order_items' sheet not found!")
        print(f"   Available sheets: {list(sheets.keys())}")
        return None
    
    print(f"\nColumns: {list(oi.columns)}")
    print(f"Total rows: {len(oi)}")
    
    # Check unit_type distribution
    if 'unit_type' in oi.columns:
        print(f"\n📊 Unit Type Distribution:")
        print(oi['unit_type'].value_counts(dropna=False))
    
    # Look for project_conversion_id to link with site_id 1797
    if 'project_conversion_id' in oi.columns:
        print(f"\n📊 Sample order_items data:")
        print(oi.head(10).to_string())
    
    return oi

def analyze_potential_site(sheets):
    """Analyze potential_site for ClientKey types and UserID"""
    print("\n" + "="*60)
    print("🏗️ POTENTIAL_SITE TABLE ANALYSIS (ClientKey & UserID)")
    print("="*60)
    
    # Try different possible sheet names
    ps_names = ['potential_site', 'public potential_site', 'public_potential_site']
    ps = None
    for name in ps_names:
        if name in sheets:
            ps = sheets[name]
            break
    
    if ps is None:
        print("❌ 'potential_site' sheet not found!")
        print(f"   Available sheets: {list(sheets.keys())}")
        return None
    
    print(f"\nColumns: {list(ps.columns)}")
    print(f"Total rows: {len(ps)}")
    
    # Check for client type columns
    client_cols = ['contractor_id', 'engineer_id', 'head_mason_id', 'site_manager_id', 
                   'ihb_registration_id', 'uncovered_retailer_id', 'created_by_id']
    
    print(f"\n📊 Client Type Column Analysis:")
    for col in client_cols:
        if col in ps.columns:
            non_null = ps[col].notna().sum()
            print(f"   {col}: {non_null} non-null values ({non_null/len(ps)*100:.1f}%)")
        else:
            print(f"   {col}: ❌ COLUMN NOT FOUND")
    
    # Check site_id 1797
    if 'id' in ps.columns:
        site_1797 = ps[ps['id'] == 1797]
        print(f"\n🔍 Site ID 1797 in potential_site:")
        if len(site_1797) > 0:
            print(site_1797.to_string())
        else:
            print("   Not found")
    
    return ps

def analyze_orders(sheets):
    """Analyze orders table for UserID columns"""
    print("\n" + "="*60)
    print("📋 ORDERS TABLE ANALYSIS (UserID Source)")
    print("="*60)
    
    # Try different possible sheet names
    o_names = ['orders', 'public orders', 'public_orders', 'user_orders']
    o = None
    for name in o_names:
        if name in sheets:
            o = sheets[name]
            break
    
    if o is None:
        print("❌ 'orders' sheet not found!")
        print(f"   Available sheets: {list(sheets.keys())}")
        return None
    
    print(f"\nColumns: {list(o.columns)}")
    print(f"Total rows: {len(o)}")
    
    # Check for UserID source columns
    user_cols = ['created_by', 'created_by_id', 'user_id', 'users_id', 'updated_by', 'updated_by_id']
    
    print(f"\n📊 UserID Source Column Analysis:")
    for col in user_cols:
        if col in o.columns:
            non_null = o[col].notna().sum()
            print(f"   {col}: {non_null} non-null values ({non_null/len(o)*100:.1f}%)")
        else:
            print(f"   {col}: ❌ COLUMN NOT FOUND")
    
    return o

def analyze_territory(sheets):
    """Analyze territory table for mainOrganizationName"""
    print("\n" + "="*60)
    print("🗺️ TERRITORY TABLE ANALYSIS")
    print("="*60)
    
    # Try different possible sheet names
    t_names = ['territory', 'public territory', 'public_territory']
    t = None
    for name in t_names:
        if name in sheets:
            t = sheets[name]
            break
    
    if t is None:
        print("❌ 'territory' sheet not found!")
        print(f"   Available sheets: {list(sheets.keys())}")
        return None
    
    print(f"\nColumns: {list(t.columns)}")
    print(f"Total rows: {len(t)}")
    
    # Check organization_id distribution
    if 'organization_id' in t.columns:
        print(f"\n📊 Organization ID Distribution in Territory:")
        print(t['organization_id'].value_counts(dropna=False))
    
    return t

def validate_mt_calculation(sheets):
    """Validate MT calculation for ACL vs AIL"""
    print("\n" + "="*60)
    print("⚖️ MT CALCULATION VALIDATION")
    print("="*60)
    
    # Get order_items and project_conversion
    oi = None
    pc = None
    
    for name in sheets:
        if 'order_items' in name.lower():
            oi = sheets[name]
        if 'project_conversion' in name.lower():
            pc = sheets[name]
    
    if oi is None or pc is None:
        print("❌ Cannot validate - missing order_items or project_conversion")
        return
    
    # Try to link and calculate
    if 'project_conversion_id' in oi.columns and 'qty' in oi.columns:
        print("\n📊 Order Items Quantity Analysis:")
        
        # Group by project_conversion_id
        qty_by_pc = oi.groupby('project_conversion_id').agg({
            'qty': 'sum'
        }).reset_index()
        
        print(f"   Total unique conversions with items: {len(qty_by_pc)}")
        print(f"   Sample quantities:")
        print(qty_by_pc.head(10).to_string())
        
        # Check for site 1797 specifically
        if 'organization_id' in pc.columns and 'site_id' in pc.columns:
            # Get conversion IDs for site 1797
            site_1797_conversions = pc[pc['site_id'] == 1797]
            if len(site_1797_conversions) > 0:
                conv_ids = site_1797_conversions['id'].tolist() if 'id' in site_1797_conversions.columns else []
                
                print(f"\n🔍 Site 1797 Conversion IDs: {conv_ids}")
                
                # Get order items for these conversions
                site_items = oi[oi['project_conversion_id'].isin(conv_ids)]
                if len(site_items) > 0:
                    total_qty = site_items['qty'].sum()
                    print(f"   Total qty: {total_qty}")
                    print(f"   Expected MT (ACL, /20): {total_qty / 20}")
                    print(f"\n   Order items details:")
                    print(site_items.to_string())

def main():
    print("🔍 DATABASE.XLSX ANALYSIS FOR POWER BI SEMANTIC MODEL FIXES")
    print("="*60)
    
    if not DB_FILE.exists():
        print(f"❌ File not found: {DB_FILE}")
        return
    
    print(f"📂 Loading: {DB_FILE}")
    sheets = load_all_sheets(DB_FILE)
    
    # Run all analyses
    analyze_organization(sheets)
    analyze_project_conversion(sheets)
    analyze_order_items(sheets)
    analyze_potential_site(sheets)
    analyze_orders(sheets)
    analyze_territory(sheets)
    validate_mt_calculation(sheets)
    
    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
