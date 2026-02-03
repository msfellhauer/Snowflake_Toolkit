-- Purpose:
--   Identify duplicate rows in a table based on a specified primary key.
--
-- How It Works:
--   - Group rows by the primary key
--   - Count the number of occurrences per key
--   - Filter to keys that appear more than once
--
-- Requirements:
--   - A column (or set of columns) that should uniquely identify each row
--
-- Output:
--   - primary_key: the duplicated key value
--   - cnt: number of times the key appears in the table
--
-- Common Use Cases:
--   - Data quality validation
--   - Verifying primary key constraints after loads or merges
--   - Detecting upstream source issues
--
-- Notes:
--   - Replace primary_key with multiple columns for composite keys
--   - High duplicate counts often indicate missing deduplication logic
--   - Consider adding constraints or checks upstream if duplicates persist


-- duplicated items

SELECT
    primary_key,
    COUNT(*) AS cnt
FROM Table_A
GROUP BY primary_key
HAVING COUNT(*) > 1;

-- Full duplicate row

SELECT A.*
FROM Table_A A
JOIN (
    SELECT primary_key
    FROM Table_A
    GROUP BY primary_key
    HAVING COUNT(*) > 1
) d
    ON A.primary_key = d.primary_key
ORDER BY A.primary_key;


