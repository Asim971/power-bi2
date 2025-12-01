#!/usr/bin/env python3
"""
Power BI Report Builder using REST API
BMD Sales Cross-Role Visit Reporting

This script provides utilities for:
1. Executing DAX queries against the semantic model
2. Exporting/importing reports
3. Managing workspaces and datasets

Dataset ID: 3477f170-bf61-42a4-b7a6-4414d7bf8881
"""

import json
import subprocess
import requests
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


# Configuration
DATASET_ID = "3477f170-bf61-42a4-b7a6-4414d7bf8881"
API_BASE = "https://api.powerbi.com/v1.0/myorg"


@dataclass
class PowerBIConfig:
    """Power BI API Configuration"""
    dataset_id: str = DATASET_ID
    api_base: str = API_BASE
    workspace_id: Optional[str] = None  # Set if using workspace-specific API


def get_access_token() -> str:
    """Get Azure AD access token for Power BI API using Azure CLI"""
    try:
        result = subprocess.run(
            ["az", "account", "get-access-token", 
             "--resource", "https://analysis.windows.net/powerbi/api",
             "--query", "accessToken", "-o", "tsv"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting token: {e.stderr}")
        raise


def get_headers(token: str) -> Dict[str, str]:
    """Get API request headers"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


# =============================================================================
# DAX Query Execution
# =============================================================================

def execute_dax_query(query: str, config: PowerBIConfig = PowerBIConfig()) -> Dict[str, Any]:
    """
    Execute a DAX query against the semantic model.
    
    Args:
        query: DAX query string (EVALUATE statement)
        config: PowerBI configuration
    
    Returns:
        Query results as dictionary
    """
    token = get_access_token()
    
    # API endpoint
    if config.workspace_id:
        url = f"{config.api_base}/groups/{config.workspace_id}/datasets/{config.dataset_id}/executeQueries"
    else:
        url = f"{config.api_base}/datasets/{config.dataset_id}/executeQueries"
    
    # Request body
    body = {
        "queries": [{"query": query}],
        "serializerSettings": {
            "includeNulls": True
        }
    }
    
    response = requests.post(url, headers=get_headers(token), json=body)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return {"error": response.text}


# =============================================================================
# Dataset & Workspace Operations
# =============================================================================

def list_datasets(workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all datasets in workspace or personal workspace"""
    token = get_access_token()
    
    if workspace_id:
        url = f"{API_BASE}/groups/{workspace_id}/datasets"
    else:
        url = f"{API_BASE}/datasets"
    
    response = requests.get(url, headers=get_headers(token))
    
    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        print(f"Error: {response.text}")
        return []


def list_workspaces() -> List[Dict[str, Any]]:
    """List all workspaces the user has access to"""
    token = get_access_token()
    url = f"{API_BASE}/groups"
    
    response = requests.get(url, headers=get_headers(token))
    
    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        print(f"Error: {response.text}")
        return []


def get_dataset_info(dataset_id: str = DATASET_ID, workspace_id: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed dataset information"""
    token = get_access_token()
    
    if workspace_id:
        url = f"{API_BASE}/groups/{workspace_id}/datasets/{dataset_id}"
    else:
        url = f"{API_BASE}/datasets/{dataset_id}"
    
    response = requests.get(url, headers=get_headers(token))
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return {}


# =============================================================================
# Report Operations
# =============================================================================

def list_reports(workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all reports in workspace"""
    token = get_access_token()
    
    if workspace_id:
        url = f"{API_BASE}/groups/{workspace_id}/reports"
    else:
        url = f"{API_BASE}/reports"
    
    response = requests.get(url, headers=get_headers(token))
    
    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        print(f"Error: {response.text}")
        return []


def clone_report(
    source_report_id: str,
    target_name: str,
    target_workspace_id: Optional[str] = None,
    target_dataset_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Clone an existing report with optional rebinding to new dataset.
    
    This is the recommended way to create a new report programmatically:
    1. Create a template report in Power BI Desktop
    2. Publish to workspace
    3. Clone and rebind to production datasets
    """
    token = get_access_token()
    url = f"{API_BASE}/reports/{source_report_id}/Clone"
    
    body = {"name": target_name}
    if target_workspace_id:
        body["targetWorkspaceId"] = target_workspace_id
    if target_dataset_id:
        body["targetModelId"] = target_dataset_id
    
    response = requests.post(url, headers=get_headers(token), json=body)
    
    if response.status_code in [200, 202]:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return {}


def export_report_to_file(
    report_id: str,
    file_path: str,
    workspace_id: Optional[str] = None
) -> bool:
    """Export report to .pbix file (for Premium/PPU workspaces only)"""
    token = get_access_token()
    
    if workspace_id:
        url = f"{API_BASE}/groups/{workspace_id}/reports/{report_id}/Export"
    else:
        url = f"{API_BASE}/reports/{report_id}/Export"
    
    response = requests.get(url, headers=get_headers(token))
    
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Report exported to {file_path}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def import_pbix(
    file_path: str,
    report_name: str,
    workspace_id: str,
    name_conflict: str = "CreateOrOverwrite"
) -> Dict[str, Any]:
    """
    Import a .pbix file to Power BI workspace.
    
    Args:
        file_path: Path to .pbix file
        report_name: Name for the report in Power BI
        workspace_id: Target workspace ID
        name_conflict: CreateOrOverwrite, Abort, or Overwrite
    """
    token = get_access_token()
    url = f"{API_BASE}/groups/{workspace_id}/imports?datasetDisplayName={report_name}&nameConflict={name_conflict}"
    
    with open(file_path, "rb") as f:
        files = {"file": (f"{report_name}.pbix", f, "application/octet-stream")}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code in [200, 202]:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return {}


# =============================================================================
# Test DAX Queries for the Report
# =============================================================================

# These are the main queries for the Executive Command Center page
EXECUTIVE_DASHBOARD_QUERIES = {
    "total_visits": """
DEFINE
    MEASURE Fact_Visit[Total Visits] = COUNTROWS(Fact_Visit)
EVALUATE
SUMMARIZECOLUMNS(
    "Total Visits", [Total Visits]
)
""",
    
    "total_orders": """
DEFINE
    MEASURE Fact_Order[Total Orders] = COUNTROWS(Fact_Order)
EVALUATE
SUMMARIZECOLUMNS(
    "Total Orders", [Total Orders]
)
""",
    
    "quality_metrics": """
DEFINE
    MEASURE Fact_Visit[Photo Rate] = 
        DIVIDE(
            COUNTROWS(FILTER(Fact_Visit, Fact_Visit[HasPhoto] = TRUE())),
            COUNTROWS(Fact_Visit),
            0
        )
    MEASURE Fact_Visit[GPS Rate] = 
        DIVIDE(
            COUNTROWS(FILTER(Fact_Visit, Fact_Visit[HasGPS] = TRUE())),
            COUNTROWS(Fact_Visit),
            0
        )
    MEASURE Fact_Visit[Feedback Rate] = 
        DIVIDE(
            COUNTROWS(FILTER(Fact_Visit, Fact_Visit[HasFeedback] = TRUE())),
            COUNTROWS(Fact_Visit),
            0
        )
EVALUATE
SUMMARIZECOLUMNS(
    "Photo Rate", [Photo Rate],
    "GPS Rate", [GPS Rate],
    "Feedback Rate", [Feedback Rate]
)
""",
    
    "zone_performance": """
DEFINE
    MEASURE Fact_Visit[Total Visits] = COUNTROWS(Fact_Visit)
    MEASURE Fact_Order[Total Orders] = COUNTROWS(Fact_Order)
    MEASURE Fact_Visit[Conversion Rate] = 
        DIVIDE([Total Orders], [Total Visits], 0)
EVALUATE
SUMMARIZECOLUMNS(
    Dim_Territory[ZoneName],
    "Visits", [Total Visits],
    "Orders", [Total Orders],
    "Conversion Rate", [Conversion Rate]
)
ORDER BY [Total Visits] DESC
""",
    
    "client_type_distribution": """
DEFINE
    MEASURE Fact_Visit[Total Visits] = COUNTROWS(Fact_Visit)
EVALUATE
SUMMARIZECOLUMNS(
    Dim_Client[ClientType],
    "Visits", [Total Visits]
)
ORDER BY [Visits] DESC
"""
}


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Main CLI interface for Power BI operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Power BI Report Builder CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List workspaces
    subparsers.add_parser("workspaces", help="List all workspaces")
    
    # List datasets
    datasets_parser = subparsers.add_parser("datasets", help="List datasets")
    datasets_parser.add_argument("--workspace", "-w", help="Workspace ID")
    
    # List reports
    reports_parser = subparsers.add_parser("reports", help="List reports")
    reports_parser.add_argument("--workspace", "-w", help="Workspace ID")
    
    # Execute DAX
    dax_parser = subparsers.add_parser("dax", help="Execute DAX query")
    dax_parser.add_argument("--query", "-q", help="DAX query to execute")
    dax_parser.add_argument("--preset", "-p", choices=list(EXECUTIVE_DASHBOARD_QUERIES.keys()),
                           help="Use preset query")
    
    # Dataset info
    info_parser = subparsers.add_parser("info", help="Get dataset info")
    info_parser.add_argument("--dataset", "-d", default=DATASET_ID, help="Dataset ID")
    
    args = parser.parse_args()
    
    if args.command == "workspaces":
        workspaces = list_workspaces()
        print("\n=== Power BI Workspaces ===")
        for ws in workspaces:
            print(f"  {ws.get('name')}: {ws.get('id')}")
    
    elif args.command == "datasets":
        datasets = list_datasets(args.workspace)
        print("\n=== Datasets ===")
        for ds in datasets:
            print(f"  {ds.get('name')}: {ds.get('id')}")
    
    elif args.command == "reports":
        reports = list_reports(args.workspace)
        print("\n=== Reports ===")
        for rpt in reports:
            print(f"  {rpt.get('name')}: {rpt.get('id')}")
    
    elif args.command == "dax":
        query = args.query or EXECUTIVE_DASHBOARD_QUERIES.get(args.preset)
        if query:
            result = execute_dax_query(query)
            print(json.dumps(result, indent=2))
        else:
            print("Please provide --query or --preset")
    
    elif args.command == "info":
        info = get_dataset_info(args.dataset)
        print(json.dumps(info, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
