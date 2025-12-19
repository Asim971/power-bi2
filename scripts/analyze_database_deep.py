#!/usr/bin/env python3
"""
Database.xlsx Deep Analysis Script - Validate TMDL Fixes
"""

import pandas as pd
import numpy as np
from pathlib import Path

DB_FILE = Path(__file__).parent.parent / "chat_history" / "Database.xlsx"

def load_sheets():
    xl = pd.ExcelFile(DB_FILE)
    return {sheet: pd.read_excel(xl, sheet_name=sheet) for sheet in xl.sheet_names}

def deep_analysis():
    print("="*70)
    print("🔬 DEEP ANALYSIS FOR TMDL FIX VALIDATION")
    print("="*70)
    
    sheets = load_sheets()
    
    # 1. ORGANIZATION MAPPING VALIDATION
    print("\n" + "="*70)
    print("1️⃣ ORGANIZATION MAPPING VALIDATION")
    print("="*70)
    
    org = sheets.get('organization')
    if org is not None:
        print("\n✅ Organization Table:")
        print(org[['id', 'organization_name', 'delete_status']].to_string())
        
        # Mapping check
        print("\n📋 Company Code Mapping:")
        for _, row in org.iterrows():
            org_id = row['id']
            org_name = row['organization_name']
            if org_id == 1:
                print(f"   org_id={org_id} → '{org_name}' → CompanyCode='ACL' ✓")
            elif org_id == 2:
                print(f"   org_id={org_id} → '{org_name}' → CompanyCode='AIL' ✓")
            else:
                print(f"   org_id={org_id} → '{org_name}' → CompanyCode='Unknown'")
    
    # 2. MT DIVISION VALIDATION - Check unit_type distribution
    print("\n" + "="*70)
    print("2️⃣ MT DIVISION VALIDATION")
    print("="*70)
    
    order_items = sheets.get('order_items')
    project_conversion = sheets.get('project_conversion')
    
    if order_items is not None and project_conversion is not None:
        print("\n📊 Unit Type Distribution in order_items:")
        print(order_items['unit_type'].value_counts(dropna=False))
        
        # Join order_items with project_conversion to get organization_id
        pc_cols = project_conversion[['id', 'organization_id', 'site_id']].copy()
        pc_cols.columns = ['project_conversion_id', 'organization_id', 'site_id']
        
        merged = order_items.merge(pc_cols, on='project_conversion_id', how='left')
        
        print("\n📊 Unit Type by Organization:")
        unit_by_org = merged.groupby(['organization_id', 'unit_type']).agg({
            'qty': ['count', 'sum']
        }).reset_index()
        unit_by_org.columns = ['organization_id', 'unit_type', 'count', 'total_qty']
        print(unit_by_org.to_string())
        
        # Simulate MT calculation
        print("\n⚖️ MT Calculation Simulation:")
        print("   Rule: ACL (org_id=1) → qty/20, AIL (org_id=2) → qty as-is")
        
        def calc_mt(row):
            if row['organization_id'] == 1:  # ACL
                return row['qty'] / 20
            else:  # AIL
                return row['qty']
        
        merged['qty_in_mt_new'] = merged.apply(calc_mt, axis=1)
        
        # Group by organization
        mt_by_org = merged.groupby('organization_id').agg({
            'qty': 'sum',
            'qty_in_mt_new': 'sum'
        }).reset_index()
        mt_by_org.columns = ['organization_id', 'total_qty_raw', 'total_qty_mt']
        
        print("\n📊 MT Totals by Organization:")
        for _, row in mt_by_org.iterrows():
            org_id = row['organization_id']
            raw = row['total_qty_raw']
            mt = row['total_qty_mt']
            company = 'ACL' if org_id == 1 else 'AIL' if org_id == 2 else 'Unknown'
            division = '/20' if org_id == 1 else 'as-is'
            print(f"   {company} (org_id={org_id}): {raw:.0f} raw qty → {mt:.2f} MT ({division})")
        
        # Check specific problem cases
        print("\n🔍 Checking for ACL items with unit_type='MT' (potential issue):")
        acl_mt_items = merged[(merged['organization_id'] == 1) & (merged['unit_type'] == 'MT')]
        if len(acl_mt_items) > 0:
            print(f"   Found {len(acl_mt_items)} ACL items with unit_type='MT'")
            print(f"   Total raw qty: {acl_mt_items['qty'].sum():.0f}")
            print(f"   With NEW logic (always /20): {acl_mt_items['qty'].sum()/20:.2f} MT")
            print(f"   Sample records:")
            print(acl_mt_items[['id', 'qty', 'unit_type', 'sku_name', 'organization_id']].head(10).to_string())
        else:
            print("   No ACL items with unit_type='MT' found")
    
    # 3. CLIENT TYPE ANALYSIS
    print("\n" + "="*70)
    print("3️⃣ CLIENT TYPE ANALYSIS (potential_site)")
    print("="*70)
    
    potential_site = sheets.get('potential_site')
    if potential_site is not None:
        client_cols = ['contractor_id', 'engineer_id', 'head_mason_id', 'site_manager_id', 'ihb_id']
        
        print("\n📊 Client Type Column Availability:")
        for col in client_cols:
            if col in potential_site.columns:
                non_null = potential_site[col].notna().sum()
                print(f"   ✓ {col}: {non_null} non-null ({non_null/len(potential_site)*100:.1f}%)")
            else:
                print(f"   ❌ {col}: NOT FOUND")
        
        # Simulate ClientKey generation
        print("\n📊 ClientKey Distribution Simulation:")
        
        def get_client_type(row):
            if pd.notna(row.get('contractor_id')):
                return 'Contractor'
            elif pd.notna(row.get('engineer_id')):
                return 'Engineer'
            elif pd.notna(row.get('head_mason_id')):
                return 'HeadMason'
            elif pd.notna(row.get('site_manager_id')):
                return 'SiteManager'
            elif pd.notna(row.get('ihb_id')):
                return 'IHB'
            else:
                return 'Site'
        
        potential_site['ClientType_Simulated'] = potential_site.apply(get_client_type, axis=1)
        print(potential_site['ClientType_Simulated'].value_counts())
    
    # 4. USER_ORDERS FOR USERID
    print("\n" + "="*70)
    print("4️⃣ USER_ORDERS TABLE (UserID Source)")
    print("="*70)
    
    user_orders = sheets.get('user_orders')
    if user_orders is not None:
        print(f"\nTotal rows: {len(user_orders)}")
        print(f"Columns: {list(user_orders.columns)}")
        
        # Check for user-related columns
        user_cols = ['created_by', 'created_by_id', 'user_id', 'users_id', 'updated_by', 'updated_by_id']
        print("\n📊 UserID Source Columns:")
        for col in user_cols:
            if col in user_orders.columns:
                non_null = user_orders[col].notna().sum()
                print(f"   ✓ {col}: {non_null} non-null ({non_null/len(user_orders)*100:.1f}%)")
            else:
                print(f"   ❌ {col}: NOT FOUND")
        
        # Check project_conversion_id link
        if 'project_conversion_id' in user_orders.columns:
            linked = user_orders['project_conversion_id'].notna().sum()
            print(f"\n   project_conversion_id linked: {linked} records")
    
    # 5. CHECK potential_site.created_by for UserID fallback
    print("\n" + "="*70)
    print("5️⃣ POTENTIAL_SITE UserID Fallback (created_by)")
    print("="*70)
    
    if potential_site is not None:
        if 'created_by' in potential_site.columns:
            non_null = potential_site['created_by'].notna().sum()
            print(f"   ✓ created_by: {non_null} non-null ({non_null/len(potential_site)*100:.1f}%)")
            print(f"   Sample values: {potential_site['created_by'].dropna().head(10).tolist()}")
        else:
            print("   ❌ created_by: NOT FOUND")
        
        # Check for created_by_id
        if 'created_by_id' in potential_site.columns:
            non_null = potential_site['created_by_id'].notna().sum()
            print(f"   ✓ created_by_id: {non_null} non-null ({non_null/len(potential_site)*100:.1f}%)")
    
    # 6. TERRITORY + ORGANIZATION JOIN VALIDATION
    print("\n" + "="*70)
    print("6️⃣ TERRITORY → ORGANIZATION JOIN VALIDATION")
    print("="*70)
    
    territory = sheets.get('territory')
    if territory is not None and org is not None:
        # Simulate the join
        territory_with_org = territory.merge(
            org[['id', 'organization_name']], 
            left_on='organization_id', 
            right_on='id',
            how='left',
            suffixes=('', '_org')
        )
        
        # Fill NULL with 'AGI Group'
        territory_with_org['mainOrganizationName'] = territory_with_org['organization_name'].fillna('AGI Group')
        
        print("\n📊 mainOrganizationName Distribution:")
        print(territory_with_org['mainOrganizationName'].value_counts())
        
        print("\n📋 Sample territory with organization:")
        print(territory_with_org[['id', 'name', 'organization_id', 'mainOrganizationName']].head(10).to_string())
    
    print("\n" + "="*70)
    print("✅ DEEP ANALYSIS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    deep_analysis()
