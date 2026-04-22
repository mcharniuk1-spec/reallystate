-- Sample join: stored media metadata + canonical listing (adjust LIMIT as needed).
SELECT
  lm.media_id,
  lm.listing_reference_id,
  lm.ordering,
  lm.url,
  lm.storage_key,
  lm.mime_type,
  lm.width,
  lm.height,
  lm.file_size,
  lm.download_status,
  cl.listing_url,
  cl.city,
  cl.price,
  cl.currency
FROM listing_media lm
JOIN canonical_listing cl ON cl.reference_id = lm.listing_reference_id
ORDER BY lm.listing_reference_id, lm.ordering
LIMIT 50;
