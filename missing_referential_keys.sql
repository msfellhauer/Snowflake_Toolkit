-- Purpose:
--   Find child table rows with no corresponding parent. This query is especially helpful 
--   when dealing with layered data. Data that comes from the Silver to gold layer to see if 
--   there are missing rows within the overall dataset. 

SELECT *
FROM child_table C
LEFT JOIN parent_table P
    ON C.parent_id = P.parent_id
WHERE P.parent_id IS NULL;
