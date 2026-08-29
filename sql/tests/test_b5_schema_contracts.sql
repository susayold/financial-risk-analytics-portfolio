-- B5T08/B5T12: inspect schemas and lineage fields.
SELECT table_schema, table_name, column_name, data_type
FROM information_schema.columns
WHERE (table_schema='mart' AND table_name IN ('mart_credit_pricing_enriched','mart_rejected_context'))
ORDER BY table_name, ordinal_position;
