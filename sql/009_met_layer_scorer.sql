-- Metaphor (MET) layer scorer registry + concept applicability.
--
-- Primary dimensions per 31-Dimension Technical Specification §2.4 / §7.6:
--   D1  Five Great Elements (Pañca Mahābhūtas)
--   D5  Five Sheaths (Pañca Kośa)
--   D6  Subtle Energies
--   D15 Tridosha (Vāta · Pitta · Kapha)
--
-- Usage:
--   mysql ... < sql/009_met_layer_scorer.sql

SET NAMES utf8mb4;

START TRANSACTION;

-- MET concept_layer for primary dimensions (all concepts currently in those dims)
INSERT INTO svarupa_concept_layer (dimension_id, concept_id, layer_code, role)
SELECT c.dimension_id, c.concept_id, 'MET', 'primary'
  FROM svarupa_concepts c
 WHERE c.dimension_id IN (1, 5, 6, 15)
   AND NOT EXISTS (
    SELECT 1 FROM svarupa_concept_layer cl
     WHERE cl.concept_id = c.concept_id AND cl.layer_code = 'MET'
 );

DELETE sc FROM svarupa_layer_scorer_concept sc
  JOIN svarupa_layer_scorer s ON s.scorer_id = sc.scorer_id
 WHERE s.layer_code = 'MET';

DELETE FROM svarupa_layer_scorer WHERE layer_code = 'MET';

INSERT INTO svarupa_layer_scorer
    (layer_code, dimension_id, scorer_slug, scorer_kind, data_ref, pole_map_ref,
     modulator_ref, emits_signals, sort_order)
VALUES
    ('MET', 1, 'met_elements', 'field_native', 'field/met_llm_primary.v1.json',
     'pole_maps/met_d1_poles.v1.json', NULL, 1, 1),
    ('MET', 5, 'met_kosha', 'field_native', 'field/met_llm_primary.v1.json',
     'pole_maps/met_d5_poles.v1.json', NULL, 1, 2),
    ('MET', 6, 'met_energies', 'field_native', 'field/met_llm_primary.v1.json',
     'pole_maps/met_d6_poles.v1.json', NULL, 1, 3),
    ('MET', 15, 'met_tridosha', 'field_native', 'field/met_llm_primary.v1.json',
     'pole_maps/met_d15_poles.v1.json', NULL, 1, 4);

INSERT INTO svarupa_layer_scorer_concept (scorer_id, concept_id)
SELECT s.scorer_id, cl.concept_id
  FROM svarupa_layer_scorer s
  JOIN svarupa_concept_layer cl
    ON cl.layer_code = s.layer_code AND cl.dimension_id = s.dimension_id
 WHERE s.layer_code = 'MET';

COMMIT;
