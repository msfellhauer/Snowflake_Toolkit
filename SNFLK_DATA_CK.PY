/**************************************************************************************************
SNOWFLAKE NOTEBOOK WORKFLOW
Data Quality Validation Framework

Purpose:
1. Set database + schema
2. Create isolated test table (safety layer from PROD)
3. Validate date freshness (yesterday check)
4. Perform NULL column analysis
5. Visualize NULL distribution

This is designed to run inside a Snowflake Notebook (Snowpark Python).
**************************************************************************************************/

# ================================================================================================
# 1️⃣ INITIALIZE SESSION
# ================================================================================================

from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import functions as F
from snowflake.snowpark.functions import col, to_date, current_date, dateadd, lit, max as sf_max
import pandas as pd
import matplotlib.pyplot as plt

session = get_active_session()

# ================================================================================================
# 2️⃣ SET DATABASE + SCHEMA
# ================================================================================================

session.sql("USE DATABASE MY_DATABASE").collect()
session.sql("USE SCHEMA MY_SCHEMA").collect()

# ================================================================================================
# 3️⃣ CREATE TEST TABLE (ISOLATION LAYER FROM PROD)
# ================================================================================================

session.sql("""
CREATE OR REPLACE TABLE MY_DATABASE.MY_SCHEMA.TEST_TABLE AS
SELECT *
FROM MY_DATABASE.MY_SCHEMA.PROD_TABLE
""").collect()

TABLE_NAME = "MY_DATABASE.MY_SCHEMA.TEST_TABLE"

# ================================================================================================
# 4️⃣ DATE FRESHNESS CHECK (EXPECTED = YESTERDAY)
# ================================================================================================

GROUP_COLS = ["DATE_COLUMN_1", "DATE_COLUMN_2"]  # <-- Replace with actual date columns

df = session.table(TABLE_NAME)

yesterday = dateadd("day", lit(-1), current_date())

checks = []

for c in GROUP_COLS:
    agg_df = df.agg(sf_max(to_date(col(c))).alias("MAX_DATE_FOUND"))

    decorated = (
        agg_df
        .with_column("FIELD_NAME", lit(c))
        .with_column("EXPECTED_DATE", yesterday)
        .select("FIELD_NAME", "MAX_DATE_FOUND", "EXPECTED_DATE")
        .filter(col("MAX_DATE_FOUND") != yesterday)
    )

    checks.append(decorated)

if checks:
    field_issues = checks[0]
    for x in checks[1:]:
        field_issues = field_issues.union_all(x)

    print("Date Freshness Issues:")
    field_issues.show()
else:
    print("No date columns provided for validation.")

# ================================================================================================
# 5️⃣ NULL VALUE ANALYSIS (COLUMN-LEVEL DATA QUALITY CHECK)
# ================================================================================================

df = session.table(TABLE_NAME)

null_count_exprs = [
    F.sum(F.iff(F.col(c).is_null(), F.lit(1), F.lit(0))).alias(c)
    for c in df.columns
]

null_counts_row = df.agg(*null_count_exprs).collect()[0].as_dict()

pdf = (
    pd.DataFrame(
        {
            "FIELD_NAME": list(null_counts_row.keys()),
            "NULL_COUNT": [int(v) if v is not None else 0 for v in null_counts_row.values()]
        }
    )
    .sort_values("NULL_COUNT", ascending=False)
)

print("Top NULL Columns:")
print(pdf.head(20))

# ================================================================================================
# 6️⃣ VISUALIZATION — FULL NULL DISTRIBUTION
# ================================================================================================

plt.figure(figsize=(16, 6))
plt.bar(pdf["FIELD_NAME"], pdf["NULL_COUNT"])
plt.xticks(rotation=90)
plt.title("NULL Count per Field\nMY_DATABASE.MY_SCHEMA.TEST_TABLE")
plt.xlabel("Field Name")
plt.ylabel("Number of NULL Values")
plt.tight_layout()
plt.show()

# ================================================================================================
# 7️⃣ OPTIONAL — TOP 30 NULL OFFENDERS
# ================================================================================================

top_n = 30
top_pdf = pdf.head(top_n)

plt.figure(figsize=(16, 6))
plt.bar(top_pdf["FIELD_NAME"], top_pdf["NULL_COUNT"])
plt.xticks(rotation=90)
plt.title(f"Top {top_n} Fields with Most NULL Values")
plt.xlabel("Field Name")
plt.ylabel("Number of NULL Values")
plt.tight_layout()
plt.show()

print("Data Quality Workflow Complete.")