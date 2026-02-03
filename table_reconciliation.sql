-- Purpose:
--   Identify rows that exist in one table but do not exist in another
--   based on a shared primary key.
--
-- How It Works:
--   - Perform a LEFT JOIN from Table A to Table B on the primary key
--   - Rows from Table A with no matching key in Table B will have NULLs
--     on the Table B side
--   - Filtering on NULL identifies non-matching records
--
-- Requirements:
--   - Two tables with a comparable primary key
--   - Primary key values should be unique in both tables for accurate results
--
-- Common Use Cases:
--   - Data reconciliation between source and target tables
--   - Validating ETL / replication completeness
--   - Identifying missing or dropped records
--
-- Notes:
--   - Direction matters: swapping Table A and Table B changes the result
--   - For large tables, ensure the join key is indexed or clustered
--   - Can be adapted to FULL OUTER JOIN for bidirectional comparison

SELECT *
FROM Table_A A
LEFT JOIN Table_B B
    ON A.Primary_Key = B.Primary_Key
WHERE B.Primary_Key IS NULL;
