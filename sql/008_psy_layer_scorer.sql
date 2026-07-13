-- Psycholinguistic (PSY) layer scorer registry + concept applicability.
--
-- Primary dimensions per 31-Dimension Technical Specification §2.4 / §7.5 / §22.4:
--   D2  Three Gunas (co-primary with AFF — linguistic form / coherence)
--   D12 Architecture of Inner Life (co-primary with NAR — rumination / loop markers)
--   D17 Three Lenses (sole primary — attribution locus in language)
--
-- Usage:
--   mysql ... < sql/008_psy_layer_scorer.sql

SET NAMES utf8mb4;

START TRANSACTION;

-- Ensure PSY layer code exists
INSERT INTO svarupa_layer (layer_code, name)
SELECT 'PSY', 'Psycholinguistic'
  FROM DUAL
 WHERE NOT EXISTS (SELECT 1 FROM svarupa_layer WHERE layer_code = 'PSY');

-- Ensure D17 exists in the dimension registry (FK parent for concepts below)
INSERT INTO svarupa_dimensions
    (dimension_id, slug, name, sanskrit_term, family, is_reserved, notes)
SELECT 17, 'three_lenses', 'Three Lenses',
       'Adhibhautika · Adhidaivika · Ādhyātmika', 'Perceptual & Epistemic', 0, NULL
  FROM DUAL
 WHERE NOT EXISTS (SELECT 1 FROM svarupa_dimensions WHERE dimension_id = 17);

-- Ensure D17 concepts exist
INSERT INTO svarupa_concepts (dimension_id, slug, name, sort_order)
SELECT v.dimension_id, v.slug, v.name, v.sort_order
  FROM (
    SELECT 17 AS dimension_id, 'the_adhibhautika_perspective' AS slug,
           'The Adhibhautika Perspective' AS name, 1 AS sort_order
    UNION ALL SELECT 17, 'the_adhidaivika_perspective', 'The Adhidaivika Perspective', 2
    UNION ALL SELECT 17, 'the_adhyatmika_perspective', 'The Ādhyātmika Perspective', 3
  ) v
 WHERE NOT EXISTS (
    SELECT 1 FROM svarupa_concepts c
     WHERE c.dimension_id = v.dimension_id AND c.slug = v.slug
 );

-- PSY concept_layer: D2 primary gunas only
INSERT INTO svarupa_concept_layer (dimension_id, concept_id, layer_code, role)
SELECT c.dimension_id, c.concept_id, 'PSY', 'primary'
  FROM svarupa_concepts c
 WHERE c.dimension_id = 2
   AND c.slug IN ('sattva', 'rajas', 'tamas')
   AND NOT EXISTS (
    SELECT 1 FROM svarupa_concept_layer cl
     WHERE cl.concept_id = c.concept_id AND cl.layer_code = 'PSY'
 );

UPDATE svarupa_concept_layer cl
  JOIN svarupa_concepts c ON c.concept_id = cl.concept_id
   SET cl.role = 'primary'
 WHERE cl.layer_code = 'PSY'
   AND c.dimension_id = 2
   AND c.slug IN ('sattva', 'rajas', 'tamas');

-- PSY concept_layer: D12 (Architecture of Inner Life)
INSERT INTO svarupa_concept_layer (dimension_id, concept_id, layer_code, role)
SELECT c.dimension_id, c.concept_id, 'PSY', 'primary'
  FROM svarupa_concepts c
 WHERE c.dimension_id = 12
   AND NOT EXISTS (
    SELECT 1 FROM svarupa_concept_layer cl
     WHERE cl.concept_id = c.concept_id AND cl.layer_code = 'PSY'
 );

UPDATE svarupa_concept_layer cl
  JOIN svarupa_concepts c ON c.concept_id = cl.concept_id
   SET cl.role = 'primary'
 WHERE cl.layer_code = 'PSY'
   AND c.dimension_id = 12;

-- PSY concept_layer: D17 Three Lenses
INSERT INTO svarupa_concept_layer (dimension_id, concept_id, layer_code, role)
SELECT c.dimension_id, c.concept_id, 'PSY', 'primary'
  FROM svarupa_concepts c
 WHERE c.dimension_id = 17
   AND c.slug IN (
        'the_adhibhautika_perspective',
        'the_adhidaivika_perspective',
        'the_adhyatmika_perspective'
   )
   AND NOT EXISTS (
    SELECT 1 FROM svarupa_concept_layer cl
     WHERE cl.concept_id = c.concept_id AND cl.layer_code = 'PSY'
 );

UPDATE svarupa_concept_layer cl
  JOIN svarupa_concepts c ON c.concept_id = cl.concept_id
   SET cl.role = 'primary'
 WHERE cl.layer_code = 'PSY'
   AND c.dimension_id = 17
   AND c.slug IN (
        'the_adhibhautika_perspective',
        'the_adhidaivika_perspective',
        'the_adhyatmika_perspective'
   );

DELETE sc FROM svarupa_layer_scorer_concept sc
  JOIN svarupa_layer_scorer s ON s.scorer_id = sc.scorer_id
 WHERE s.layer_code = 'PSY';

DELETE FROM svarupa_layer_scorer WHERE layer_code = 'PSY';

INSERT INTO svarupa_layer_scorer
    (layer_code, dimension_id, scorer_slug, scorer_kind, data_ref, pole_map_ref,
     modulator_ref, emits_signals, sort_order)
VALUES
    ('PSY', 2, 'psy_gunas', 'field_native', 'field/psy_llm_primary.v1.json',
     'pole_maps/psy_d2_poles.v1.json', NULL, 1, 1),
    ('PSY', 12, 'psy_inner_life', 'field_native', 'field/psy_llm_primary.v1.json',
     'pole_maps/psy_d12_poles.v1.json', NULL, 1, 2),
    ('PSY', 17, 'psy_three_lenses', 'field_native', 'field/psy_llm_primary.v1.json',
     'pole_maps/psy_d17_poles.v1.json', NULL, 1, 3);

INSERT INTO svarupa_layer_scorer_concept (scorer_id, concept_id)
SELECT s.scorer_id, cl.concept_id
  FROM svarupa_layer_scorer s
  JOIN svarupa_concept_layer cl
    ON cl.layer_code = s.layer_code AND cl.dimension_id = s.dimension_id
 WHERE s.layer_code = 'PSY';

COMMIT;
