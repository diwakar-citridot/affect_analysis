-- Fix AFF rows in svarupa_concept_layer (Multi-Axis Affect Analysis applicability).
--
-- Spec affinity dimensions: {2, 8, 9, 22, 24}
--   D2  Triguṇa (contributing)
--   D8  Sthāyībhāvas (primary)
--   D9  Vyabhicārībhāvas (primary)
--   D22 Brahmavihāras (contributing)
--   D24 Daivī/Āsurī Sampat (contributing)
--
-- Removes erroneous AFF tags (e.g. D5 Pañca Kośa, D6 subtle energies, D15 doṣa)
-- and re-tags every concept in the spec dimensions. Dimensions with no concepts
-- yet (D22/D24) simply produce zero rows.
--
-- Usage:
--   mysql -u ... -p your_database < sql/004_fix_aff_concept_layer.sql
-- Or: python scripts/fix_aff_concept_layer.py [--dry-run]

START TRANSACTION;

DELETE FROM svarupa_concept_layer
 WHERE layer_code = 'AFF';

INSERT INTO svarupa_concept_layer (dimension_id, concept_id, layer_code)
SELECT c.dimension_id, c.concept_id, 'AFF'
  FROM svarupa_concepts c
 WHERE c.dimension_id IN (2, 8, 9, 22, 24)
 ORDER BY c.dimension_id, c.sort_order, c.slug;

COMMIT;

-- Verify (optional):
-- SELECT cl.dimension_id, d.slug AS dimension_slug, COUNT(*) AS n_concepts
--   FROM svarupa_concept_layer cl
--   JOIN svarupa_dimensions d ON d.dimension_id = cl.dimension_id
--  WHERE cl.layer_code = 'AFF'
--  GROUP BY cl.dimension_id, d.slug
--  ORDER BY cl.dimension_id;
