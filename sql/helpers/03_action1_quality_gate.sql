-- Action1 quality gate for the seven priority scrape sources.
-- Run when PostgreSQL is available:
-- psql "$DATABASE_URL" -f sql/helpers/03_action1_quality_gate.sql

\echo 'Action1 source totals'
select
  source_name,
  count(*) as listings,
  count(*) filter (where description is not null and length(description) >= 160) as useful_descriptions,
  count(*) filter (where price is not null and price > 0) as numeric_prices,
  count(*) filter (where area_sqm is not null and area_sqm >= 2) as plausible_areas,
  count(*) filter (where coalesce(array_length(image_urls, 1), 0) = 1) as one_photo_rows,
  count(*) filter (where latitude is not null and longitude is not null) as geo_rows
from canonical_listing
where source_name in ('Address.bg', 'BulgarianProperties', 'Homes.bg', 'imot.bg', 'LUXIMMO', 'property.bg', 'SUPRIMMO')
group by source_name
order by source_name;

\echo 'Hard geospatial failures: outside coarse Bulgaria bounding box'
select
  reference_id,
  source_name,
  listing_url,
  city,
  district,
  latitude,
  longitude,
  price,
  currency
from canonical_listing
where source_name in ('Address.bg', 'BulgarianProperties', 'Homes.bg', 'imot.bg', 'LUXIMMO', 'property.bg', 'SUPRIMMO')
  and latitude is not null
  and longitude is not null
  and not (latitude between 41.0 and 44.5 and longitude between 22.0 and 29.5)
order by source_name, reference_id
limit 200;

\echo 'Border spillover suspects: coordinates near Romania/Turkey/Greece that need map review'
select
  reference_id,
  source_name,
  listing_url,
  city,
  district,
  latitude,
  longitude
from canonical_listing
where source_name in ('Address.bg', 'BulgarianProperties', 'Homes.bg', 'imot.bg', 'LUXIMMO', 'property.bg', 'SUPRIMMO')
  and latitude is not null
  and longitude is not null
  and (
    latitude > 44.20
    or latitude < 41.15
    or longitude < 22.25
    or longitude > 28.75
  )
order by latitude desc, longitude
limit 200;

\echo 'Content-quality failures'
select
  reference_id,
  source_name,
  listing_url,
  title,
  length(coalesce(description, '')) as description_chars,
  price,
  area_sqm,
  city,
  district,
  coalesce(array_length(image_urls, 1), 0) as image_url_count
from canonical_listing
where source_name in ('Address.bg', 'BulgarianProperties', 'Homes.bg', 'imot.bg', 'LUXIMMO', 'property.bg', 'SUPRIMMO')
  and (
    description is null
    or length(description) < 160
    or price = 0
    or (area_sqm is not null and area_sqm > 0 and area_sqm < 2)
    or city is null
    or coalesce(array_length(image_urls, 1), 0) = 1
  )
order by source_name, reference_id
limit 500;
