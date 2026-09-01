# SQL Patterns for Common Metrics

Use these canonical SQL patterns when computing standard metrics.
Replace `{schema}` with the active dataset schema.

## Conversion Rate (Event-Based)

```sql
SELECT
    COUNT(DISTINCT CASE WHEN b.user_id IS NOT NULL THEN a.user_id END) * 1.0
    / NULLIF(COUNT(DISTINCT a.user_id), 0) AS conversion_rate
FROM {schema}.events a
LEFT JOIN {schema}.events b
    ON a.user_id = b.user_id
    AND b.event_type = '{{TARGET_EVENT}}'
    AND b.timestamp >= a.timestamp
    AND b.timestamp <= a.timestamp + INTERVAL '{{WINDOW}}'
WHERE a.event_type = '{{SOURCE_EVENT}}'
    AND a.timestamp BETWEEN '{{START_DATE}}' AND '{{END_DATE}}';
```

## Revenue (Order-Based)

```sql
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_order_value,
    COUNT(DISTINCT user_id) AS purchasing_users
FROM {schema}.orders
WHERE status = 'completed'
    AND order_date BETWEEN '{{START_DATE}}' AND '{{END_DATE}}';
```

## Active Users (DAU / WAU / MAU)

```sql
SELECT
    DATE_TRUNC('{{GRANULARITY}}', timestamp) AS period,
    COUNT(DISTINCT user_id) AS active_users
FROM {schema}.events
WHERE event_type IN ({{QUALIFYING_EVENTS}})
    AND timestamp BETWEEN '{{START_DATE}}' AND '{{END_DATE}}'
GROUP BY 1
ORDER BY 1;
```

## Retention Rate (Cohort-Based)

```sql
WITH cohorts AS (
    SELECT user_id, DATE_TRUNC('{{GRANULARITY}}', signup_date) AS cohort
    FROM {schema}.users
),
activity AS (
    SELECT DISTINCT user_id, DATE_TRUNC('{{GRANULARITY}}', timestamp) AS active_period
    FROM {schema}.events
)
SELECT
    c.cohort,
    DATE_DIFF('{{GRANULARITY}}', c.cohort, a.active_period) AS period_number,
    COUNT(DISTINCT a.user_id) * 1.0
    / NULLIF(COUNT(DISTINCT c.user_id), 0) AS retention_rate
FROM cohorts c
LEFT JOIN activity a ON c.user_id = a.user_id
GROUP BY 1, 2
ORDER BY 1, 2;
```

## NPS (Net Promoter Score)

```sql
SELECT
    COUNT(CASE WHEN score >= 9 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)
    - COUNT(CASE WHEN score <= 6 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) AS nps,
    COUNT(CASE WHEN score >= 9 THEN 1 END) AS promoters,
    COUNT(CASE WHEN score BETWEEN 7 AND 8 THEN 1 END) AS passives,
    COUNT(CASE WHEN score <= 6 THEN 1 END) AS detractors,
    COUNT(*) AS total_responses
FROM {schema}.nps_responses
WHERE submitted_at BETWEEN '{{START_DATE}}' AND '{{END_DATE}}';
```

## Usage Notes
- Replace `{schema}` with the active dataset's schema prefix
- Replace `{{VARIABLE}}` placeholders with actual values
- These are starting patterns — adapt WHERE clauses and JOINs for specific data models
- Always validate output with data quality checks before drawing conclusions
