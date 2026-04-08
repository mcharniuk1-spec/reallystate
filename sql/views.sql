-- Materialized views for property analytics and duplicate detection.
-- Apply after schema.sql; refresh periodically via cron or after bulk ingestion.

-- v_property_analytics: aggregated stats per city/district/intent/category/source
CREATE MATERIALIZED VIEW IF NOT EXISTS v_property_analytics AS
SELECT
    cl.city,
    cl.district,
    cl.listing_intent,
    cl.property_category,
    cl.source_name,
    sr.tier,
    count(*)                                     AS listing_count,
    count(*) FILTER (WHERE cl.removed_at IS NULL) AS active_count,
    round(avg(cl.price)::numeric, 2)             AS avg_price,
    round(min(cl.price)::numeric, 2)             AS min_price,
    round(max(cl.price)::numeric, 2)             AS max_price,
    round(avg(cl.price_per_sqm)::numeric, 2)     AS avg_price_per_sqm,
    round(avg(cl.area_sqm)::numeric, 1)          AS avg_area_sqm,
    round(avg(cl.rooms)::numeric, 1)             AS avg_rooms,
    count(*) FILTER (WHERE cl.image_urls != '[]'::jsonb) AS with_photos,
    count(*) FILTER (WHERE cl.description IS NOT NULL AND cl.description != '') AS with_description,
    min(cl.first_seen)                           AS earliest_seen,
    max(cl.last_seen)                            AS latest_seen
FROM canonical_listing cl
LEFT JOIN source_registry sr ON sr.source_name = cl.source_name
GROUP BY cl.city, cl.district, cl.listing_intent, cl.property_category, cl.source_name, sr.tier
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_v_property_analytics_pk
  ON v_property_analytics (city, district, listing_intent, property_category, source_name);


-- v_duplicate_candidates: pairs of listings with same city + similar address + similar price + similar area
CREATE MATERIALIZED VIEW IF NOT EXISTS v_duplicate_candidates AS
SELECT
    a.reference_id  AS ref_a,
    b.reference_id  AS ref_b,
    a.source_name   AS source_a,
    b.source_name   AS source_b,
    a.city,
    a.address_text  AS address_a,
    b.address_text  AS address_b,
    a.price         AS price_a,
    b.price         AS price_b,
    a.area_sqm      AS area_a,
    b.area_sqm      AS area_b,
    CASE WHEN a.price > 0 AND b.price > 0
         THEN round(abs(a.price - b.price) / greatest(a.price, b.price) * 100, 1)
         ELSE NULL END AS price_diff_pct,
    CASE WHEN a.area_sqm > 0 AND b.area_sqm > 0
         THEN round(abs(a.area_sqm - b.area_sqm) / greatest(a.area_sqm, b.area_sqm) * 100, 1)
         ELSE NULL END AS area_diff_pct
FROM canonical_listing a
JOIN canonical_listing b
  ON a.city IS NOT NULL
 AND a.city = b.city
 AND a.reference_id < b.reference_id
 AND a.removed_at IS NULL
 AND b.removed_at IS NULL
 AND a.address_text IS NOT NULL
 AND b.address_text IS NOT NULL
 AND lower(trim(a.address_text)) = lower(trim(b.address_text))
WHERE
    (a.price IS NULL OR b.price IS NULL
     OR abs(a.price - b.price) / greatest(a.price, b.price, 1) < 0.15)
AND (a.area_sqm IS NULL OR b.area_sqm IS NULL
     OR abs(a.area_sqm - b.area_sqm) / greatest(a.area_sqm, b.area_sqm, 1) < 0.15)
WITH DATA;

CREATE INDEX IF NOT EXISTS idx_v_duplicate_candidates_city ON v_duplicate_candidates (city);
