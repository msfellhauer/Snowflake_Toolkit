# GX Generic Data Health Model

Author: Mark S. Fellhauer, D.Mgt, MBA  
Platform: Snowflake Snowpark (Python)

---

## Overview

The GX Generic Data Health Model is a standardized production-ready
data validation framework designed to evaluate structural integrity,
freshness, and operational stability of Snowflake tables and views.

This model enforces governance-level validation logic and is designed
to operate across any dataset with configurable column mappings.

---

## Health Rules Enforced

### 1. 7-Day Scope Filter
All validations operate only on the most recent 7 days of data,
based on SNAPSHOT_DATE.

---

### 2. Freshness Validation
Data must contain records at least as recent as yesterday.

Failure Condition:
- Max(SNAPSHOT_DATE) < yesterday

---

### 3. Load Stability Detection

Two checks:

**Absolute Load Check**
- Row count < MIN_EXPECTED_ROWS

**Relative Load Check**
- Latest day load < 70% of prior-day average

---

### 4. Completeness Rule (Post-Cutoff Closed Records)

If:
CLOSE_DATE >= 2018-01-01

Then the following fields must NOT be NULL:

- PRIMARY_KEY
- ORG_UNIT
- AMOUNT
- APPLICATION_DATE
- RATE

---

### 5. Org-Unit Attribution Rule

If either:
- CLOSE_DATE is not null
- SUBMIT_DATE is not null

Then:
- ORG_UNIT must not be null

---

## Configuration

Edit the configuration section at the top of the script:

```python
DB = "YOUR_DATABASE"
SCHEMA = "YOUR_SCHEMA"
OBJECT_NAME = "YOUR_VIEW_OR_TABLE"
