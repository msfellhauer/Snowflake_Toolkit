-- Purpose:
--   Summarize recent Snowflake task executions by task, showing the
--   most recent scheduled run time and its resulting state.
--
-- Snowflake Objects:
--   INFORMATION_SCHEMA.TASK_HISTORY
--
-- What This Answers:
--   - When did each task last run?
--   - What was the state of its most recent execution?
--
-- Key Logic:
--   - MAX_BY(state, Scheduled_Time) returns the task state associated
--     with the latest scheduled execution.
--   - MAX(Scheduled_Time) identifies the most recent run per task.
--   - GROUP BY ALL aggregates results at the task name level.
--
-- Filters:
--   - Time window limited to the last 7 days.
--   - Results restricted to a single schema.
--
-- Notes:
--   - Uses Snowflake-specific functions (MAX_BY, TASK_HISTORY).
--   - TASK_HISTORY is time-bound; increasing the range may impact performance.
--   - Completed_Time may be NULL for tasks that have not finished.
--   - Requires appropriate privileges to view task metadata.
--
-- Common Uses:
--   - Verifying task health after failures or deploys
--   - Identifying stale or non-running tasks
--   - Quick operational check of scheduled pipelines

SELECT
    Name,
    Completed_Time,
    MAX_BY(state, Scheduled_Time) AS Last_State,
    MAX(Scheduled_Time) AS Last_Scheduled_Time
FROM TABLE(
    INFORMATION_SCHEMA.TASK_HISTORY(
        SCHEDULED_TIME_RANGE_START => DATEADD('DAY', -7, CURRENT_TIMESTAMP())
    )
)
WHERE SCHEMA_NAME = 'MY_SCHEMA'
GROUP BY ALL
ORDER BY
    Last_Scheduled_Time,
    Completed_Time DESC;
