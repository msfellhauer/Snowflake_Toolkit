"""
============================================================
GENERIC GX DATA HEALTH MODEL
Snowflake Snowpark Implementation
Author: Mark S. Fellhauer, D.Mgt, MBA

Purpose:
Performs standardized data health validation across any
Snowflake table or view.

Health Rules Enforced:
1) Scope: Last 7 days only
2) Freshness: Data must be current (>= yesterday)
3) Load stability: Detect abnormal load drops
4) Completeness (post-cutoff):
   If CLOSE_DATE >= 2018-01-01 →
       PRIMARY_KEY
       ORG_UNIT
       AMOUNT
       APPLICATION_DATE
       RATE
   must NOT be NULL
5) Org-unit attribution:
   If CLOSE_DATE OR SUBMIT_DATE exists →
       ORG_UNIT must NOT be NULL
============================================================
"""

from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import (
    col, lit, when,
    sum as sf_sum,
    max as sf_max,
    count as sf_count,
    dateadd,
    current_date,
    to_date
)
from datetime import date, timedelta


# ============================================================
# CONFIGURATION — EDIT THESE VALUES PER OBJECT
# ============================================================

DB = "YOUR_DATABASE"
SCHEMA = "YOUR_SCHEMA"
OBJECT_NAME = "YOUR_VIEW_OR_TABLE"

FULL_OBJECT = f"{DB}.{SCHEMA}.{OBJECT_NAME}"

DATE_SNAPSHOT_COL = "SNAPSHOT_DATE"
CLOSE_DATE_COL    = "CLOSE_DATE"
SUBMIT_DATE_COL   = "SUBMIT_DATE"
PRIMARY_KEY       = "RECORD_ID"

ORG_UNIT_COL      = "ORG_UNIT_ID"
AMOUNT_COL        = "AMOUNT"
APPLY_DATE_COL    = "APPLICATION_DATE"
RATE_COL          = "RATE"

CUTOFF_DATE = to_date(lit("2018-01-01"))

REQUIRED_ON_CLOSE = [
    PRIMARY_KEY,
    ORG_UNIT_COL,
    AMOUNT_COL,
    APPLY_DATE_COL,
    RATE_COL
]

MIN_EXPECTED_ROWS = 100
LOW_LOAD_RATIO = 0.70


# ============================================================
# INITIALIZATION
# ============================================================

session = get_active_session()

session.sql(f"USE DATABASE {DB}").collect()
session.sql(f"USE SCHEMA {SCHEMA}").collect()

df_7d = (
    session.table(FULL_OBJECT)
    .filter(col(DATE_SNAPSHOT_COL) >= dateadd("day", lit(-7), current_date()))
)

row_count = df_7d.count()


# ============================================================
# FRESHNESS CHECK
# ============================================================

max_snapshot_date = (
    df_7d
    .agg(sf_max(col(DATE_SNAPSHOT_COL)).alias("MAX_DT"))
    .collect()[0]["MAX_DT"]
)

expected_date = date.today() - timedelta(days=1)
is_fresh = (max_snapshot_date is not None) and (max_snapshot_date >= expected_date)


# ============================================================
# LOAD STABILITY CHECK
# ============================================================

daily_counts = (
    df_7d
    .group_by(col(DATE_SNAPSHOT_COL).alias("DT"))
    .agg(sf_count(lit(1)).alias("ROWS"))
    .sort(col("DT"))
    .collect()
)

days = [r["DT"] for r in daily_counts]
counts = [r["ROWS"] for r in daily_counts]

latest_count = counts[-1] if counts else 0
prior_counts = counts[:-1]
avg_prior = (sum(prior_counts) / len(prior_counts)) if prior_counts else None

low_load_relative = (
    avg_prior is not None and
    latest_count < LOW_LOAD_RATIO * avg_prior
)

low_load_absolute = row_count < MIN_EXPECTED_ROWS


# ============================================================
# RULE 1 — COMPLETENESS (POST-CUTOFF CLOSED RECORDS)
# ============================================================

closed_post_cutoff = df_7d.filter(
    col(CLOSE_DATE_COL).is_not_null() &
    (col(CLOSE_DATE_COL) >= CUTOFF_DATE)
)

null_checks = [
    sf_sum(
        when(col(c).is_null(), lit(1)).otherwise(lit(0))
    ).alias(f"{c}_NULLS")
    for c in REQUIRED_ON_CLOSE
]

conditional_nulls = closed_post_cutoff.agg(*null_checks).collect()[0].as_dict()
total_conditional_violations = sum(conditional_nulls.values())


# ============================================================
# RULE 2 — ORG UNIT REQUIRED WHEN SUBMITTED OR CLOSED
# ============================================================

org_unit_required = df_7d.filter(
    (
        col(CLOSE_DATE_COL).is_not_null() |
        col(SUBMIT_DATE_COL).is_not_null()
    ) &
    col(ORG_UNIT_COL).is_null()
)

org_unit_violation_count = org_unit_required.count()

org_unit_violation_sample = (
    org_unit_required
    .select(PRIMARY_KEY, CLOSE_DATE_COL, SUBMIT_DATE_COL, ORG_UNIT_COL)
    .limit(20)
    .collect()
)


# ============================================================
# FINAL VERDICT
# ============================================================

status = "✅ HEALTHY"

if not is_fresh:
    status = "❌ BROKEN — DATA NOT FRESH"
elif low_load_absolute:
    status = "❌ BROKEN — LOW DATA LOAD (ABSOLUTE)"
elif low_load_relative:
    status = "⚠️ WARNING — LOW DATA LOAD (VS PRIOR DAYS)"
elif total_conditional_violations > 0:
    status = "❌ BROKEN — CLOSED RECORDS AFTER CUTOFF MISSING REQUIRED FIELDS"
elif org_unit_violation_count > 0:
    status = "❌ BROKEN — ORG_UNIT MISSING FOR SUBMITTED OR CLOSED RECORDS"


# ============================================================
# OUTPUT
# ============================================================

print("\n================ DATA HEALTH SUMMARY ================\n")
print("OBJECT:", FULL_OBJECT)
print("STATUS:", status)

print("\n--- Volume (past 7 days) ---")
print("Row count:", row_count)

print("\n--- Freshness ---")
print("Max snapshot date:", max_snapshot_date)
print("Fresh:", is_fresh)

print("\n--- Daily Load ---")
for d, c in zip(days, counts):
    print(f"{d}: {c}")

print("\n--- Closed-After-Cutoff Completeness Violations ---")
for k, v in conditional_nulls.items():
    print(f"{k}: {v}")
print("Total violations:", total_conditional_violations)

print("\n--- Org-Unit Required Violations ---")
print("Violation count:", org_unit_violation_count)

if org_unit_violation_sample:
    print("Sample:")
    for r in org_unit_violation_sample:
        print(r.as_dict())
else:
    print("No violations found.")

print("\n=====================================================\n")
