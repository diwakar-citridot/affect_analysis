-- =============================================================================
-- Svarupa — migration: companion CMS -> assistant_v1 normalized schema
-- Source: svarupa_companion_v2.svarupa_dimension_merged / svarupa_concept_merged
-- Target: svarupa_assistant_v1.svarupa_dimensions / svarupa_concepts
--
-- Companion is treated as the source of truth: svarupa_concepts is FULLY
-- REPLACED for the 17 mapped dimensions (cascades svarupa_concept_descriptions).
-- Concept overview = companion balanced/neutral, non_spiritual description.
-- name / sanskrit_term = Title-Cased companion slug.
--
-- Companion dimension -> target dimension_id mapping:
--   paths_of_engagement->10  chakras->6  seven_layers_of_consciousness->4
--   tridosha->15  cyclical_evolution_of_consciousness->13  trigunas->2
--   jyotish_shastra->18  pancha_koshas->5  manasika_prakriti->3  nadis->6
--   pancha_mahabhutas->1  phenomenological_dimensions->7  prana_vayus->6
--   samskaras->12  sthayibhavas->8  svabhava_svadharma->16  vyabhicaribhavas->9
--   ashtanga_yoga->11  yuga_cycles->14
--   (chakras + nadis + prana_vayus merge into D6; samskaras -> D12)
-- =============================================================================
SET NAMES utf8mb4;

START TRANSACTION;

-- -----------------------------------------------------------------------------
-- svarupa_dimensions — ensure the 17 mapped dimensions exist (idempotent).
-- The target registry is authoritative; this re-asserts canonical values.
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_assistant_v1.svarupa_dimensions
    (dimension_id, slug, name, sanskrit_term, family, is_reserved, notes)
VALUES
    (1, 'pancha_mahabhutas', 'Five Great Elements', 'Pañca Mahābhūtas', 'Constitutional', 0, NULL),
    (2, 'trigunas', 'Three Gunas', 'Triguṇa — Sattva·Rajas·Tamas', 'Constitutional', 0, NULL),
    (3, 'manasika_prakriti', 'Sixteen Faces of Mind', 'Mānasika Prakṛti', 'Constitutional', 0, NULL),
    (4, 'seven_layers_of_consciousness', 'Seven Layers of Consciousness', 'Sapta Bhūmikā / Planes', 'Consciousness', 0, NULL),
    (5, 'pancha_koshas', 'Five Sheaths', 'Pañca Kośa', 'Consciousness', 0, NULL),
    (6, 'subtle_energies', 'Subtle Energies', 'Prāṇa Vāyus · Chakras · Nāḍīs', 'Consciousness', 0, 'Merges vāyus, chakras, nāḍīs'),
    (7, 'phenomenology', 'Phenomenological Dimensions', 'Phenomenology of Experience', 'Phenomenological', 0, NULL),
    (8, 'sthayibhavas', 'Nine Enduring Emotions', 'Sthāyībhāvas', 'Affective', 0, NULL),
    (9, 'vyabhicaribhavas', 'Thirty-Three Transient States', 'Vyabhicārībhāvas', 'Affective', 0, NULL),
    (10, 'paths_of_engagement', 'Paths of Engagement', 'Karma · Jñāna · Rāja · Bhakti', 'Path & Practice', 0, NULL),
    (11, 'ashtanga_yoga', 'Eightfold Refinement', 'Aṣṭāṅga Yoga', 'Path & Practice', 0, NULL),
    (12, 'architecture_of_inner_life', 'Architecture of Inner Life', 'Karma · Saṁskāra · Vāsanā · Eṣaṇā', 'Karmic & Temporal', 0, NULL),
    (13, 'cyclical_evolution_of_consciousness', 'Cyclical Evolution of Consciousness', 'Kāla Chakra (individual)', 'Karmic & Temporal', 0, NULL),
    (14, 'yuga_cycles', 'Yuga Cycles', 'Yuga (collective time)', 'Karmic & Temporal', 0, NULL),
    (15, 'tridosha', 'Tridosha', 'Vāta · Pitta · Kapha', 'Constitutional', 0, NULL),
    (16, 'svabhava_svadharma', 'Inner Nature & Its Law', 'Svabhāva & Svadharma', 'Karmic & Temporal', 0, NULL),
    (18, 'jyotish_shastra', 'Science of Cosmic Light', 'Jyotiṣ Śāstra', 'Cosmological', 0, NULL)
AS new
ON DUPLICATE KEY UPDATE
    slug          = new.slug,
    name          = new.name,
    sanskrit_term = new.sanskrit_term,
    family        = new.family,
    notes         = new.notes;

-- -----------------------------------------------------------------------------
-- svarupa_concepts — full replace for the mapped dimensions.
-- DELETE cascades to svarupa_concept_descriptions for these dimensions.
-- -----------------------------------------------------------------------------
DELETE FROM svarupa_assistant_v1.svarupa_concepts WHERE dimension_id IN (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,18);

-- target dimension 1 (5 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 1, 'air', 'Air', 'Air', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 11 AND x.concept = 'air'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 11 AND x.concept = 'air'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 1, 'earth', 'Earth', 'Earth', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 11 AND x.concept = 'earth'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 11 AND x.concept = 'earth'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 1, 'ether', 'Ether', 'Ether', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 11 AND x.concept = 'ether'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 11 AND x.concept = 'ether'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 1, 'fire', 'Fire', 'Fire', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 11 AND x.concept = 'fire'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 11 AND x.concept = 'fire'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 1, 'water', 'Water', 'Water', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 11 AND x.concept = 'water'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 11 AND x.concept = 'water'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;

-- target dimension 2 (3 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 2, 'rajas', 'Rajas', 'Rajas', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 6 AND x.concept = 'rajas'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 6 AND x.concept = 'rajas'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 2, 'sattva', 'Sattva', 'Sattva', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 6 AND x.concept = 'sattva'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 6 AND x.concept = 'sattva'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 2, 'tamas', 'Tamas', 'Tamas', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 6 AND x.concept = 'tamas'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 6 AND x.concept = 'tamas'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;

-- target dimension 3 (16 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'aindra_sattva', 'Aindra Sattva', 'Aindra Sattva', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'aindra_sattva'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'aindra_sattva'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'asura_rajasika', 'Asura Rajasika', 'Asura Rajasika', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'asura_rajasika'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'asura_rajasika'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'brahma_sattva', 'Brahma Sattva', 'Brahma Sattva', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'brahma_sattva'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'brahma_sattva'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'gandharva_sattva', 'Gandharva Sattva', 'Gandharva Sattva', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'gandharva_sattva'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'gandharva_sattva'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'kubera_sattva', 'Kubera Sattva', 'Kubera Sattva', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'kubera_sattva'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'kubera_sattva'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'matsya_tamasa', 'Matsya Tamasa', 'Matsya Tamasa', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'matsya_tamasa'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'matsya_tamasa'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 6;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'paishacha_rajasika', 'Paishacha Rajasika', 'Paishacha Rajasika', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'paishacha_rajasika'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'paishacha_rajasika'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 7;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'pashu_tamasa', 'Pashu Tamasa', 'Pashu Tamasa', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'pashu_tamasa'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'pashu_tamasa'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 8;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'preta_rajasika', 'Preta Rajasika', 'Preta Rajasika', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'preta_rajasika'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'preta_rajasika'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 9;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'rakshasa_rajasika', 'Rakshasa Rajasika', 'Rakshasa Rajasika', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'rakshasa_rajasika'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'rakshasa_rajasika'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 10;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'rishi_sattva', 'Rishi Sattva', 'Rishi Sattva', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'rishi_sattva'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'rishi_sattva'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 11;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'sarpa_rajasika', 'Sarpa Rajasika', 'Sarpa Rajasika', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'sarpa_rajasika'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'sarpa_rajasika'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 12;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'shakuni_rajasika', 'Shakuni Rajasika', 'Shakuni Rajasika', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'shakuni_rajasika'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'shakuni_rajasika'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 13;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'vanaspati_tamasa', 'Vanaspati Tamasa', 'Vanaspati Tamasa', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'vanaspati_tamasa'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'vanaspati_tamasa'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 14;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'varuna_sattva', 'Varuna Sattva', 'Varuna Sattva', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'varuna_sattva'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'varuna_sattva'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 15;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 3, 'yama_sattva', 'Yama Sattva', 'Yama Sattva', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'yama_sattva'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 9 AND x.concept = 'yama_sattva'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 16;

-- target dimension 4 (7 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 4, 'cosmic', 'Cosmic', 'Cosmic', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'cosmic'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'cosmic'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 4, 'dreaming', 'Dreaming', 'Dreaming', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'dreaming'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'dreaming'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 4, 'sleeping', 'Sleeping', 'Sleeping', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'sleeping'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'sleeping'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 4, 'supreme_love', 'Supreme Love', 'Supreme Love', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'supreme_love'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'supreme_love'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 4, 'transcendental', 'Transcendental', 'Transcendental', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'transcendental'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'transcendental'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 4, 'unity', 'Unity', 'Unity', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'unity'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'unity'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 6;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 4, 'waking', 'Waking', 'Waking', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'waking'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 3 AND x.concept = 'waking'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 7;

-- target dimension 5 (5 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 5, 'anandamaya_kosha', 'Anandamaya Kosha', 'Anandamaya Kosha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 8 AND x.concept = 'anandamaya_kosha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 8 AND x.concept = 'anandamaya_kosha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 5, 'annamaya_kosha', 'Annamaya Kosha', 'Annamaya Kosha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 8 AND x.concept = 'annamaya_kosha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 8 AND x.concept = 'annamaya_kosha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 5, 'manomaya_kosha', 'Manomaya Kosha', 'Manomaya Kosha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 8 AND x.concept = 'manomaya_kosha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 8 AND x.concept = 'manomaya_kosha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 5, 'pranamaya_kosha', 'Pranamaya Kosha', 'Pranamaya Kosha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 8 AND x.concept = 'pranamaya_kosha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 8 AND x.concept = 'pranamaya_kosha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 5, 'vijnanamaya_kosha', 'Vijnanamaya Kosha', 'Vijnanamaya Kosha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 8 AND x.concept = 'vijnanamaya_kosha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 8 AND x.concept = 'vijnanamaya_kosha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;

-- target dimension 6 (25 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'ajna', 'Ajna', 'Ajna', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'ajna'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'ajna'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'anahata', 'Anahata', 'Anahata', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'anahata'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'anahata'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'manipuraka', 'Manipuraka', 'Manipuraka', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'manipuraka'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'manipuraka'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'muladhara', 'Muladhara', 'Muladhara', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'muladhara'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'muladhara'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'sahasrara', 'Sahasrara', 'Sahasrara', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'sahasrara'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'sahasrara'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'svadhisthana', 'Svadhisthana', 'Svadhisthana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'svadhisthana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'svadhisthana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 6;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'vishuddhi', 'Vishuddhi', 'Vishuddhi', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'vishuddhi'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 2 AND x.concept = 'vishuddhi'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 7;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'alambusha', 'Alambusha', 'Alambusha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'alambusha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'alambusha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 8;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'gandhari', 'Gandhari', 'Gandhari', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'gandhari'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'gandhari'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 9;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'hastijihva', 'Hastijihva', 'Hastijihva', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'hastijihva'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'hastijihva'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 10;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'ida', 'Ida', 'Ida', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'ida'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'ida'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 11;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'kuhu', 'Kuhu', 'Kuhu', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'kuhu'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'kuhu'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 12;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'payaswini', 'Payaswini', 'Payaswini', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'payaswini'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'payaswini'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 13;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'pingala', 'Pingala', 'Pingala', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'pingala'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'pingala'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 14;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'pusha', 'Pusha', 'Pusha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'pusha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'pusha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 15;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'saraswati', 'Saraswati', 'Saraswati', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'saraswati'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'saraswati'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 16;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'shankhini', 'Shankhini', 'Shankhini', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'shankhini'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'shankhini'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 17;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'varuni', 'Varuni', 'Varuni', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'varuni'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'varuni'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 18;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'visvodhari', 'Visvodhari', 'Visvodhari', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'visvodhari'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'visvodhari'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 19;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'yasasvini', 'Yasasvini', 'Yasasvini', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'yasasvini'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 10 AND x.concept = 'yasasvini'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 20;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'apana', 'Apana', 'Apana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 13 AND x.concept = 'apana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 13 AND x.concept = 'apana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 21;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'prana', 'Prana', 'Prana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 13 AND x.concept = 'prana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 13 AND x.concept = 'prana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 22;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'samana', 'Samana', 'Samana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 13 AND x.concept = 'samana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 13 AND x.concept = 'samana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 23;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'udana', 'Udana', 'Udana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 13 AND x.concept = 'udana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 13 AND x.concept = 'udana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 24;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 6, 'vyana', 'Vyana', 'Vyana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 13 AND x.concept = 'vyana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 13 AND x.concept = 'vyana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 25;

-- target dimension 7 (9 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 7, 'agency', 'Agency', 'Agency', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'agency'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'agency'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 7, 'arousal', 'Arousal', 'Arousal', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'arousal'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'arousal'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 7, 'clarity', 'Clarity', 'Clarity', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'clarity'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'clarity'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 7, 'orientation', 'Orientation', 'Orientation', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'orientation'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'orientation'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 7, 'relational_quality', 'Relational Quality', 'Relational Quality', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'relational_quality'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'relational_quality'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 7, 'self_location', 'Self Location', 'Self Location', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'self_location'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'self_location'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 6;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 7, 'somatic_presence', 'Somatic Presence', 'Somatic Presence', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'somatic_presence'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'somatic_presence'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 7;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 7, 'temporal', 'Temporal', 'Temporal', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'temporal'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'temporal'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 8;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 7, 'valence', 'Valence', 'Valence', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'valence'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 12 AND x.concept = 'valence'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 9;

-- target dimension 8 (9 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 8, 'bhaya', 'Bhaya', 'Bhaya', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'bhaya'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'bhaya'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 8, 'hasa', 'Hasa', 'Hasa', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'hasa'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'hasa'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 8, 'jugupsa', 'Jugupsa', 'Jugupsa', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'jugupsa'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'jugupsa'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 8, 'krodha', 'Krodha', 'Krodha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'krodha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'krodha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 8, 'rati', 'Rati', 'Rati', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'rati'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'rati'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 8, 'sama', 'Sama', 'Sama', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'sama'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'sama'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 6;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 8, 'soka', 'Soka', 'Soka', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'soka'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'soka'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 7;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 8, 'utsaha', 'Utsaha', 'Utsaha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'utsaha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'utsaha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 8;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 8, 'vismaya', 'Vismaya', 'Vismaya', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'vismaya'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 15 AND x.concept = 'vismaya'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 9;

-- target dimension 9 (33 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'alasya', 'Alasya', 'Alasya', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'alasya'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'alasya'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'amarsha', 'Amarsha', 'Amarsha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'amarsha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'amarsha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'apasmara', 'Apasmara', 'Apasmara', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'apasmara'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'apasmara'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'asuya', 'Asuya', 'Asuya', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'asuya'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'asuya'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'autsukya', 'Autsukya', 'Autsukya', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'autsukya'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'autsukya'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'avahittha', 'Avahittha', 'Avahittha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'avahittha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'avahittha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 6;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'avega', 'Avega', 'Avega', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'avega'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'avega'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 7;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'capalata', 'Capalata', 'Capalata', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'capalata'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'capalata'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 8;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'cinta', 'Cinta', 'Cinta', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'cinta'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'cinta'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 9;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'dainya', 'Dainya', 'Dainya', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'dainya'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'dainya'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 10;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'dhrti', 'Dhrti', 'Dhrti', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'dhrti'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'dhrti'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 11;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'garva', 'Garva', 'Garva', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'garva'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'garva'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 12;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'glani', 'Glani', 'Glani', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'glani'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'glani'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 13;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'harsa', 'Harsa', 'Harsa', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'harsa'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'harsa'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 14;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'jadata', 'Jadata', 'Jadata', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'jadata'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'jadata'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 15;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'mada', 'Mada', 'Mada', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'mada'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'mada'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 16;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'marana', 'Marana', 'Marana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'marana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'marana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 17;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'mati', 'Mati', 'Mati', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'mati'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'mati'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 18;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'moha', 'Moha', 'Moha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'moha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'moha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 19;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'nidra', 'Nidra', 'Nidra', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'nidra'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'nidra'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 20;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'nirveda', 'Nirveda', 'Nirveda', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'nirveda'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'nirveda'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 21;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'sanka', 'Sanka', 'Sanka', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'sanka'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'sanka'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 22;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'smrti', 'Smrti', 'Smrti', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'smrti'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'smrti'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 23;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'srama', 'Srama', 'Srama', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'srama'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'srama'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 24;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'supta', 'Supta', 'Supta', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'supta'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'supta'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 25;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'trasa', 'Trasa', 'Trasa', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'trasa'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'trasa'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 26;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'ugrata', 'Ugrata', 'Ugrata', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'ugrata'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'ugrata'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 27;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'unmada', 'Unmada', 'Unmada', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'unmada'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'unmada'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 28;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'vibodha', 'Vibodha', 'Vibodha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'vibodha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'vibodha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 29;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'visada', 'Visada', 'Visada', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'visada'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'visada'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 30;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'vitarka', 'Vitarka', 'Vitarka', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'vitarka'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'vitarka'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 31;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'vrida', 'Vrida', 'Vrida', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'vrida'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'vrida'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 32;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 9, 'vyadhi', 'Vyadhi', 'Vyadhi', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'vyadhi'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 17 AND x.concept = 'vyadhi'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 33;

-- target dimension 10 (4 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 10, 'bhakti', 'Bhakti', 'Bhakti', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 1 AND x.concept = 'bhakti'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 1 AND x.concept = 'bhakti'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 10, 'jnana', 'Jnana', 'Jnana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 1 AND x.concept = 'jnana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 1 AND x.concept = 'jnana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 10, 'karma', 'Karma', 'Karma', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 1 AND x.concept = 'karma'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 1 AND x.concept = 'karma'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 10, 'yoga', 'Yoga', 'Yoga', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 1 AND x.concept = 'yoga'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 1 AND x.concept = 'yoga'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;

-- target dimension 11 (8 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 11, 'asana', 'Asana', 'Asana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'asana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'asana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 11, 'dharana', 'Dharana', 'Dharana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'dharana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'dharana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 11, 'dhyana', 'Dhyana', 'Dhyana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'dhyana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'dhyana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 11, 'niyama', 'Niyama', 'Niyama', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'niyama'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'niyama'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 11, 'pranayama', 'Pranayama', 'Pranayama', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'pranayama'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'pranayama'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 11, 'pratyahara', 'Pratyahara', 'Pratyahara', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'pratyahara'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'pratyahara'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 6;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 11, 'samadhi', 'Samadhi', 'Samadhi', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'samadhi'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'samadhi'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 7;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 11, 'yama', 'Yama', 'Yama', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'yama'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 18 AND x.concept = 'yama'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 8;

-- target dimension 12 (12 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'deha_vasana', 'Deha Vasana', 'Deha Vasana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'deha_vasana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'deha_vasana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'jiveshana', 'Jiveshana', 'Jiveshana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'jiveshana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'jiveshana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'kama_vasana', 'Kama Vasana', 'Kama Vasana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'kama_vasana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'kama_vasana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'kriyamana_karma', 'Kriyamana Karma', 'Kriyamana Karma', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'kriyamana_karma'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'kriyamana_karma'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'loka_vasana', 'Loka Vasana', 'Loka Vasana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'loka_vasana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'loka_vasana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'lokeshana', 'Lokeshana', 'Lokeshana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'lokeshana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'lokeshana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 6;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'prarabdha_karma', 'Prarabdha Karma', 'Prarabdha Karma', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'prarabdha_karma'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'prarabdha_karma'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 7;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'putreshana', 'Putreshana', 'Putreshana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'putreshana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'putreshana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 8;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'sanchita_karma', 'Sanchita Karma', 'Sanchita Karma', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'sanchita_karma'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'sanchita_karma'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 9;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'shastra_vasana', 'Shastra Vasana', 'Shastra Vasana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'shastra_vasana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'shastra_vasana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 10;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'subha_vasana', 'Subha Vasana', 'Subha Vasana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'subha_vasana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'subha_vasana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 11;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 12, 'vitteshana', 'Vitteshana', 'Vitteshana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'vitteshana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 14 AND x.concept = 'vitteshana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 12;

-- target dimension 13 (4 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 13, 'ascent_from_experience', 'Ascent From Experience', 'Ascent From Experience', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 5 AND x.concept = 'ascent_from_experience'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 5 AND x.concept = 'ascent_from_experience'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 13, 'ascent_to_awareness', 'Ascent To Awareness', 'Ascent To Awareness', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 5 AND x.concept = 'ascent_to_awareness'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 5 AND x.concept = 'ascent_to_awareness'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 13, 'descent_from_awareness', 'Descent From Awareness', 'Descent From Awareness', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 5 AND x.concept = 'descent_from_awareness'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 5 AND x.concept = 'descent_from_awareness'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 13, 'descent_to_experience', 'Descent To Experience', 'Descent To Experience', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 5 AND x.concept = 'descent_to_experience'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 5 AND x.concept = 'descent_to_experience'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;

-- target dimension 14 (10 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 14, 'dwapara_yuga_dwapara_soul', 'Dwapara Yuga Dwapara Soul', 'Dwapara Yuga Dwapara Soul', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'dwapara_yuga_dwapara_soul'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'dwapara_yuga_dwapara_soul'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 14, 'dwapara_yuga_satya_soul', 'Dwapara Yuga Satya Soul', 'Dwapara Yuga Satya Soul', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'dwapara_yuga_satya_soul'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'dwapara_yuga_satya_soul'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 14, 'dwapara_yuga_treta_soul', 'Dwapara Yuga Treta Soul', 'Dwapara Yuga Treta Soul', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'dwapara_yuga_treta_soul'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'dwapara_yuga_treta_soul'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 14, 'kali_yuga_dwapara_soul', 'Kali Yuga Dwapara Soul', 'Kali Yuga Dwapara Soul', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'kali_yuga_dwapara_soul'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'kali_yuga_dwapara_soul'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 14, 'kali_yuga_kali_soul', 'Kali Yuga Kali Soul', 'Kali Yuga Kali Soul', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'kali_yuga_kali_soul'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'kali_yuga_kali_soul'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 14, 'kali_yuga_satya_soul', 'Kali Yuga Satya Soul', 'Kali Yuga Satya Soul', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'kali_yuga_satya_soul'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'kali_yuga_satya_soul'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 6;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 14, 'kali_yuga_treta_soul', 'Kali Yuga Treta Soul', 'Kali Yuga Treta Soul', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'kali_yuga_treta_soul'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'kali_yuga_treta_soul'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 7;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 14, 'satya_yuga_satya_soul', 'Satya Yuga Satya Soul', 'Satya Yuga Satya Soul', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'satya_yuga_satya_soul'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'satya_yuga_satya_soul'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 8;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 14, 'treta_yuga_satya_soul', 'Treta Yuga Satya Soul', 'Treta Yuga Satya Soul', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'treta_yuga_satya_soul'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'treta_yuga_satya_soul'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 9;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 14, 'treta_yuga_treta_soul', 'Treta Yuga Treta Soul', 'Treta Yuga Treta Soul', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'treta_yuga_treta_soul'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 19 AND x.concept = 'treta_yuga_treta_soul'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 10;

-- target dimension 15 (3 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 15, 'kapha', 'Kapha', 'Kapha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 4 AND x.concept = 'kapha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 4 AND x.concept = 'kapha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 15, 'pitta', 'Pitta', 'Pitta', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 4 AND x.concept = 'pitta'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 4 AND x.concept = 'pitta'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 15, 'vata', 'Vata', 'Vata', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 4 AND x.concept = 'vata'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 4 AND x.concept = 'vata'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;

-- target dimension 16 (8 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 16, 'jnana', 'Jnana', 'Jnana', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'jnana'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'jnana'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 16, 'kshatriya', 'Kshatriya', 'Kshatriya', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'kshatriya'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'kshatriya'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 16, 'mental', 'Mental', 'Mental', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'mental'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'mental'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 16, 'physical', 'Physical', 'Physical', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'physical'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'physical'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 16, 'psychic', 'Psychic', 'Psychic', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'psychic'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'psychic'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 16, 'shudra', 'Shudra', 'Shudra', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'shudra'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'shudra'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 6;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 16, 'vaishya', 'Vaishya', 'Vaishya', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'vaishya'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'vaishya'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 7;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 16, 'vital', 'Vital', 'Vital', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'vital'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 16 AND x.concept = 'vital'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 8;

-- target dimension 18 (9 concepts)
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 18, 'budha', 'Budha', 'Budha', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'budha'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'budha'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 1;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 18, 'chandra', 'Chandra', 'Chandra', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'chandra'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'chandra'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 2;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 18, 'guru', 'Guru', 'Guru', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'guru'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'guru'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 3;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 18, 'ketu', 'Ketu', 'Ketu', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'ketu'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'ketu'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 4;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 18, 'mangala', 'Mangala', 'Mangala', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'mangala'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'mangala'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 5;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 18, 'rahu', 'Rahu', 'Rahu', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'rahu'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'rahu'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 6;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 18, 'sani', 'Sani', 'Sani', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'sani'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'sani'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 7;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 18, 'sukra', 'Sukra', 'Sukra', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'sukra'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'sukra'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 8;
INSERT INTO svarupa_assistant_v1.svarupa_concepts
    (dimension_id, slug, name, sanskrit_term, description, sort_order)
SELECT 18, 'surya', 'Surya', 'Surya', COALESCE(
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'surya'
        AND x.perspective = 'non_spiritual'
        AND x.status IN ('neutral','balanced','medium')
      ORDER BY FIELD(x.status,'neutral','balanced','medium') LIMIT 1),
    (SELECT x.description FROM svarupa_companion_v2.svarupa_concept_merged x
      WHERE x.dimension_id = 7 AND x.concept = 'surya'
        AND x.perspective = 'non_spiritual'
      ORDER BY x.id LIMIT 1)
  ), 9;

COMMIT;

-- Sanity checks (uncomment to run):
-- SELECT dimension_id, COUNT(*) FROM svarupa_assistant_v1.svarupa_concepts GROUP BY dimension_id ORDER BY dimension_id;
-- SELECT COUNT(*) AS concepts_with_overview FROM svarupa_assistant_v1.svarupa_concepts WHERE description IS NOT NULL;
