-- Narrative Arc (NAR) layer scorer registry + concept applicability.
--
-- Primary dimensions per 31-Dimension Technical Specification §7.7:
--   D10 Paths of Engagement, D12 Architecture of Inner Life, D13 Cyclical Evolution,
--   D14 Yuga Cycles, D16 Svabhāva & Svadharma, D29 Bandha & Mokṣa.
--
-- Usage:
--   mysql ... < sql/007_nar_layer_scorer.sql
-- Or: PYTHONPATH=src python scripts/seed_nar_layer_scorers.py

SET NAMES utf8mb4;

START TRANSACTION;

-- D29 concepts (when not yet present in svarupa_concepts)
INSERT INTO svarupa_concepts (dimension_id, slug, name, sort_order)
SELECT v.dimension_id, v.slug, v.name, v.sort_order
  FROM (
    SELECT 29 AS dimension_id, 'bondage' AS slug, 'Bondage (Bandha)' AS name, 1 AS sort_order
    UNION ALL SELECT 29, 'adhyasa', 'Superimposition (Adhyāsa)', 2
    UNION ALL SELECT 29, 'seeking', 'Seeking / Inquiry', 3
    UNION ALL SELECT 29, 'turning_point', 'Turning Point', 4
    UNION ALL SELECT 29, 'liberation', 'Liberation (Mokṣa)', 5
  ) v
 WHERE NOT EXISTS (
    SELECT 1 FROM svarupa_concepts c
     WHERE c.dimension_id = v.dimension_id AND c.slug = v.slug
 );

-- NAR concept_layer rows (primary role for narrative-owned dimensions)
INSERT INTO svarupa_concept_layer (dimension_id, concept_id, layer_code, role)
SELECT c.dimension_id, c.concept_id, 'NAR', 'primary'
  FROM svarupa_concepts c
 WHERE c.dimension_id IN (10, 12, 13, 14, 16, 29)
   AND NOT EXISTS (
    SELECT 1 FROM svarupa_concept_layer cl
     WHERE cl.concept_id = c.concept_id AND cl.layer_code = 'NAR'
 );

DELETE sc FROM svarupa_layer_scorer_concept sc
  JOIN svarupa_layer_scorer s ON s.scorer_id = sc.scorer_id
 WHERE s.layer_code = 'NAR';

DELETE FROM svarupa_layer_scorer WHERE layer_code = 'NAR';

INSERT INTO svarupa_layer_scorer
    (layer_code, dimension_id, scorer_slug, scorer_kind, data_ref, pole_map_ref,
     modulator_ref, emits_signals, sort_order)
VALUES
    ('NAR', 10, 'nar_paths', 'field_native', 'field/nar_llm_primary.v1.json',
     'pole_maps/nar_d10_poles.v1.json', NULL, 1, 1),
    ('NAR', 12, 'nar_inner_life', 'field_native', 'field/nar_llm_primary.v1.json',
     'pole_maps/nar_d12_poles.v1.json', NULL, 1, 2),
    ('NAR', 13, 'nar_evolution', 'field_native', 'field/nar_llm_primary.v1.json',
     'pole_maps/nar_d13_poles.v1.json', NULL, 1, 3),
    ('NAR', 14, 'nar_yuga', 'field_native', 'field/nar_llm_primary.v1.json',
     'pole_maps/nar_d14_poles.v1.json', NULL, 1, 4),
    ('NAR', 16, 'nar_svadharma', 'field_native', 'field/nar_llm_primary.v1.json',
     'pole_maps/nar_d16_poles.v1.json', NULL, 1, 5),
    ('NAR', 29, 'nar_bandha_moksha', 'field_native', 'field/nar_llm_primary.v1.json',
     'pole_maps/nar_d29_poles.v1.json', NULL, 1, 6);

INSERT INTO svarupa_layer_scorer_concept (scorer_id, concept_id)
SELECT s.scorer_id, cl.concept_id
  FROM svarupa_layer_scorer s
  JOIN svarupa_concept_layer cl
    ON cl.layer_code = s.layer_code AND cl.dimension_id = s.dimension_id
 WHERE s.layer_code = 'NAR';

COMMIT;
