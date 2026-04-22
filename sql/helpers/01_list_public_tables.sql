-- List all user tables in public schema with estimated row counts (pg_class.reltuples).
SELECT
  c.relname AS table_name,
  c.reltuples::bigint AS estimate_rows
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind = 'r'
ORDER BY c.relname;
