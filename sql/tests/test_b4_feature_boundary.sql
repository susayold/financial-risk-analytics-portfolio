SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'mart'
  AND table_name = 'mart_credit_application_core'
ORDER BY ordinal_position;
