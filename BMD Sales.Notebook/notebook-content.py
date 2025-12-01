# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "d3cfe56a-4276-4098-9570-e29cff91e8f3",
# META       "default_lakehouse_name": "BMD_Sales",
# META       "default_lakehouse_workspace_id": "276a43e7-e0e3-4366-9ac1-40d1bf52182f",
# META       "known_lakehouses": [
# META         {
# META           "id": "d3cfe56a-4276-4098-9570-e29cff91e8f3"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# Run this in a notebook cell (might already be installed in your environment)
!pip install psycopg2-binary pandas


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import psycopg2
import getpass

host = "172.17.19.21"
port = 5432
dbname = "bmdsalesdb"
user = "debuguser"

password = getpass.getpass("Enter PostgreSQL password:3s8W2M6ezU7JhM6D ")

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    print("✅ Connected successfully")
except Exception as e:
    print("❌ Connection failed:")
    print(e)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import pandas as pd

query = """
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
"""

try:
    tables_df = pd.read_sql(query, conn)
    display(tables_df)  # in Jupyter / Microsoft notebooks this shows a nice table
except Exception as e:
    print("❌ Failed to fetch tables:")
    print(e)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
