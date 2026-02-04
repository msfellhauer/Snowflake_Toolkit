-- Purpose:
--   Identify tasks that exceeded expected runtime. This gives insight into overall runtime, and shows how long a 
--   particular task takes to complete. 
-- Notes:
--   - Runtime = Completed_Time - Scheduled_Time
SELECT
    Name,
    Scheduled_Time,
    Completed_Time,
    DATEDIFF('SECOND', Scheduled_Time, Completed_Time) AS Runtime_Seconds
FROM TABLE(
    INFORMATION_SCHEMA.TASK_HISTORY(
        SCHEDULED_TIME_RANGE_START => DATEADD('DAY', -7, CURRENT_TIMESTAMP())
    )
)
WHERE SCHEMA_NAME = '<SCHEMA_NAME>'
ORDER BY Runtime_Seconds DESC;
