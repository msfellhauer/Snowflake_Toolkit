-- Purpose:
--   Show users/roles with access to each table. Enables you to see the permissions level on a particulat schema, giving 
--   insight into a particular items you can/ can not run.


SELECT
    grantee_name,
    privilege,
    table_name
FROM INFORMATION_SCHEMA.TABLE_PRIVILEGES
WHERE table_schema = '<SCHEMA_NAME>'
ORDER BY grantee_name;
