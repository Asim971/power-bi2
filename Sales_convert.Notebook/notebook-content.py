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

# ============================================================
# Fabric Notebook: Export Semantic Model tables -> Lakehouse Delta tables
# FIXED: handles empty tables by supplying schema; continues on errors
# ============================================================

import re
import pandas as pd
import sempy.fabric as fabric

from pyspark.sql.types import (
    StructType, StructField,
    StringType, LongType, IntegerType, DoubleType, BooleanType,
    TimestampType, DateType, DecimalType, BinaryType
)

# ----------------------------
# CONFIG
# ----------------------------
SEMANTIC_MODEL = "BMD_sales"
MODEL_WORKSPACE = None          # set workspace name or ID if semantic model isn't in the same workspace context
TARGET_PREFIX = "sm_"
OVERWRITE = True

EXPORT_ALL = True
TABLES_TO_EXPORT = ["public user_orders", "public project_conversion", "Fact_ProjectConversion"]

# Optional: exclude typical PBIX helper tables
EXCLUDE_PATTERNS = [
    r"^LocalDateTable_", r"^DateTableTemplate_", r"^Label_",
    r"^LastRefresh_", r"^TranslatedReportLabels$", r"^ActionsMeasures$",
    r"^VisualsEmptyStateMeasures$", r"^Measure$", r"^_Metrics$"
]

# ----------------------------
# Helpers
# ----------------------------
def should_exclude(name: str) -> bool:
    return any(re.search(p, name) for p in EXCLUDE_PATTERNS)

def safe_table_name(name: str) -> str:
    n = re.sub(r"[^0-9a-zA-Z_]", "_", name)
    n = re.sub(r"_+", "_", n).strip("_")
    if re.match(r"^[0-9]", n):
        n = f"t_{n}"
    return n.lower()

def clean_col_name(c: str) -> str:
    c2 = re.sub(r"[^0-9a-zA-Z_]", "_", c)
    c2 = re.sub(r"_+", "_", c2).strip("_")
    return c2

def clean_column_names_sdf(sdf):
    for c in sdf.columns:
        new_c = clean_col_name(c)
        if new_c and new_c != c:
            sdf = sdf.withColumnRenamed(c, new_c)
    return sdf

def pbi_to_spark_type(pbi_type: str):
    """Best-effort mapping from semantic model data types -> Spark types."""
    if not pbi_type:
        return StringType()

    t = str(pbi_type).strip().lower()

    # Common Power BI / Vertipaq / SemPy labels
    if t in ["string", "text"]:
        return StringType()
    if t in ["int64", "long", "bigint"]:
        return LongType()
    if t in ["int32", "int", "integer"]:
        return IntegerType()
    if t in ["double", "float"]:
        return DoubleType()
    if t in ["decimal", "currency", "fixed decimal number"]:
        # If precision/scale known, update here; else keep a safe default
        return DecimalType(38, 18)
    if t in ["boolean", "bool", "logical"]:
        return BooleanType()
    if t in ["datetime", "timestamp", "date/time"]:
        return TimestampType()
    if t in ["date"]:
        return DateType()
    if t in ["binary"]:
        return BinaryType()

    # fallback
    return StringType()

# ----------------------------
# 1) Build column metadata map (for empty-table schema)
# ----------------------------
cols_df = fabric.list_columns(dataset=SEMANTIC_MODEL, workspace=MODEL_WORKSPACE) if MODEL_WORKSPACE else fabric.list_columns(dataset=SEMANTIC_MODEL)

# Try to detect column names in the metadata DF robustly
# Common outputs contain: Table Name, Column Name, Data Type
table_col = "Table Name" if "Table Name" in cols_df.columns else ("Table" if "Table" in cols_df.columns else None)
col_col   = "Column Name" if "Column Name" in cols_df.columns else ("Column" if "Column" in cols_df.columns else None)
type_col  = "Data Type" if "Data Type" in cols_df.columns else ("Type" if "Type" in cols_df.columns else None)

if not (table_col and col_col):
    raise ValueError(f"Could not find required columns in fabric.list_columns() output. Columns seen: {list(cols_df.columns)}")

def build_schema_for_table(table_name: str) -> StructType:
    tmeta = cols_df[cols_df[table_col] == table_name]
    if tmeta.shape[0] == 0:
        # As a fallback, if metadata isn't available, write a single dummy column.
        return StructType([StructField("empty_table", StringType(), True)])

    fields = []
    for _, r in tmeta.iterrows():
        raw_c = str(r[col_col])
        spark_c = clean_col_name(raw_c) or "col"
        spark_t = pbi_to_spark_type(r[type_col] if type_col else None)
        fields.append(StructField(spark_c, spark_t, True))

    # Remove duplicates if cleaning caused collisions
    seen = set()
    deduped = []
    for f in fields:
        name = f.name
        if name in seen:
            i = 2
            new_name = f"{name}_{i}"
            while new_name in seen:
                i += 1
                new_name = f"{name}_{i}"
            deduped.append(StructField(new_name, f.dataType, True))
            seen.add(new_name)
        else:
            deduped.append(f)
            seen.add(name)

    return StructType(deduped)

# ----------------------------
# 2) Get tables from semantic model
# ----------------------------
tables_df = fabric.list_tables(SEMANTIC_MODEL, workspace=MODEL_WORKSPACE) if MODEL_WORKSPACE else fabric.list_tables(SEMANTIC_MODEL)

tbl_name_col = "Name" if "Name" in tables_df.columns else tables_df.columns[0]
tables_all = [t for t in tables_df[tbl_name_col].tolist() if isinstance(t, str)]
tables_all = sorted(set(tables_all))  # dedupe

tables = [t for t in tables_all if not should_exclude(t)]

if not EXPORT_ALL:
    missing = sorted(set(TABLES_TO_EXPORT) - set(tables))
    if missing:
        raise ValueError(f"Not found in semantic model '{SEMANTIC_MODEL}': {missing}")
    tables = TABLES_TO_EXPORT

print(f"Exporting {len(tables)} tables from semantic model '{SEMANTIC_MODEL}'")

# ----------------------------
# 3) Export loop
# ----------------------------
mode = "overwrite" if OVERWRITE else "append"
ok, skipped = [], []

for t in tables:
    try:
        print(f"\nReading semantic model table: {t}")

        pdf = fabric.read_table(SEMANTIC_MODEL, t, workspace=MODEL_WORKSPACE) if MODEL_WORKSPACE else fabric.read_table(SEMANTIC_MODEL, t)

        # Handle empty result sets explicitly (Spark can't infer schema from empty) :contentReference[oaicite:3]{index=3}
        if pdf is None or (isinstance(pdf, pd.DataFrame) and pdf.shape[0] == 0):
            print(f"⚠️ Table '{t}' returned 0 rows. Creating empty Spark DF with schema from metadata.")
            schema = build_schema_for_table(t)
            sdf = spark.createDataFrame([], schema=schema)
        else:
            sdf = spark.createDataFrame(pdf)

        sdf = clean_column_names_sdf(sdf)

        target = safe_table_name(f"{TARGET_PREFIX}{SEMANTIC_MODEL}_{t}")
        print(f"Writing Lakehouse Delta table: {target} (mode={mode})")

        writer = (
            sdf.write.format("delta")
            .mode(mode)
        )

        # If overwriting, keep schema aligned
        if OVERWRITE:
            writer = writer.option("overwriteSchema", "true")

        writer.saveAsTable(target)

        cnt = spark.table(target).count()
        print(f"✅ {target}: {cnt:,} rows")
        ok.append((t, target, cnt))

    except Exception as e:
        print(f"❌ Skipping '{t}' due to error: {repr(e)}")
        skipped.append((t, repr(e)))

print("\n================ SUMMARY ================")
print(f"✅ Exported: {len(ok)}")
print(f"❌ Skipped:  {len(skipped)}")
if skipped:
    print("\nSkipped tables:")
    for t, err in skipped[:25]:
        print(f" - {t}: {err}")
    if len(skipped) > 25:
        print(f" ... and {len(skipped) - 25} more")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
