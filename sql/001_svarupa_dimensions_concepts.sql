-- =============================================================================
-- Svarupa — Dimensions / Concepts / Concept-Descriptions schema (MySQL 8.0+)
-- =============================================================================
-- Normalized model for the 31-Dimension framework.
--
--   svarupa_dimensions            1 row per dimension (D1..D30 + D31 reserved)
--   svarupa_concepts              concepts of a dimension      (FK -> dimension)
--   svarupa_concept_descriptions  description for the triplet  (FK -> concept,
--                                 (dimension, concept, status)      FK -> status)
--
-- Supporting lookups / bridges (keep the model in 3NF, no multi-valued columns):
--   svarupa_status                canonical pole vocabulary {deficiency,balance,excess}
--   svarupa_layer                 analytical-layer codes (SEM, COT, AFF, ...)
--   svarupa_dimension_layer       dimension <-> layer affinity (primary/contributing)
--   svarupa_dimension_dependency  dimension <-> upstream dimension (self relation)
--
-- The (Dimension, concept, status) triplet is enforced by UNIQUE(concept_id,
-- status_id); the dimension is reached transitively through the concept, so it
-- is never duplicated on the description row.
--
-- Engine/charset: InnoDB + utf8mb4 throughout (Sanskrit / Devanagari content).
-- =============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS svarupa_concept_descriptions;
DROP TABLE IF EXISTS svarupa_concepts;
DROP TABLE IF EXISTS svarupa_dimension_dependency;
DROP TABLE IF EXISTS svarupa_dimension_layer;
DROP TABLE IF EXISTS svarupa_dimensions;
DROP TABLE IF EXISTS svarupa_layer;
DROP TABLE IF EXISTS svarupa_status;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- Lookup: canonical state poles (architecture spec §22 — canonicalized triple).
-- Legacy data vocabularies (balanced/excessive/deficient, positive/neutral/...)
-- map onto these three codes via `legacy_aliases`.
-- -----------------------------------------------------------------------------
CREATE TABLE svarupa_status (
    status_id      TINYINT UNSIGNED NOT NULL PRIMARY KEY,
    code           VARCHAR(16)  NOT NULL,                 -- deficiency | balance | excess
    label          VARCHAR(32)  NOT NULL,
    polarity       TINYINT      NOT NULL,                 -- -1 deficiency, 0 balance, +1 excess
    sort_order     TINYINT UNSIGNED NOT NULL DEFAULT 0,
    legacy_aliases VARCHAR(128) NULL,                     -- e.g. 'deficient,low,blocked,negative'
    UNIQUE KEY uq_status_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Lookup: analytical layers (used by the dimension<->layer affinity bridge).
-- -----------------------------------------------------------------------------
CREATE TABLE svarupa_layer (
    layer_code  VARCHAR(8)  NOT NULL PRIMARY KEY,         -- SEM, COT, AFF, PHE, PSY, MET, NAR
    name        VARCHAR(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- svarupa_dimensions — the authoritative 31-dimension registry.
-- dimension_id is the stable spec D-number (1..31). D31 is the reserved slot.
-- -----------------------------------------------------------------------------
CREATE TABLE svarupa_dimensions (
    dimension_id   TINYINT UNSIGNED NOT NULL PRIMARY KEY,  -- spec D-number (1..31)
    slug           VARCHAR(64)  NOT NULL,                  -- stable machine code
    name           VARCHAR(128) NOT NULL,                  -- English name
    sanskrit_term  VARCHAR(191) NULL,                      -- traditional term
    family         VARCHAR(64)  NOT NULL,
    is_reserved    TINYINT(1)   NOT NULL DEFAULT 0,         -- 1 = reserved/unpopulated slot
    notes          VARCHAR(255) NULL,
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_dimensions_slug (slug),
    KEY ix_dimensions_family (family)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- svarupa_dimension_layer — which layers assess a dimension (affinity matrix).
-- role: 'primary' (●) or 'contributing' (○).
-- -----------------------------------------------------------------------------
CREATE TABLE svarupa_dimension_layer (
    dimension_id TINYINT UNSIGNED NOT NULL,
    layer_code   VARCHAR(8)       NOT NULL,
    role         ENUM('primary','contributing') NOT NULL DEFAULT 'contributing',
    PRIMARY KEY (dimension_id, layer_code),
    KEY ix_dimlayer_layer (layer_code),
    CONSTRAINT fk_dimlayer_dimension FOREIGN KEY (dimension_id)
        REFERENCES svarupa_dimensions (dimension_id) ON DELETE CASCADE,
    CONSTRAINT fk_dimlayer_layer FOREIGN KEY (layer_code)
        REFERENCES svarupa_layer (layer_code) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- svarupa_dimension_dependency — upstream dimensions that condition a reading.
-- Self relation on svarupa_dimensions (registry "Depends On" column).
-- -----------------------------------------------------------------------------
CREATE TABLE svarupa_dimension_dependency (
    dimension_id            TINYINT UNSIGNED NOT NULL,
    depends_on_dimension_id TINYINT UNSIGNED NOT NULL,
    PRIMARY KEY (dimension_id, depends_on_dimension_id),
    KEY ix_dep_target (depends_on_dimension_id),
    CONSTRAINT chk_dep_not_self CHECK (dimension_id <> depends_on_dimension_id),
    CONSTRAINT fk_dep_dimension FOREIGN KEY (dimension_id)
        REFERENCES svarupa_dimensions (dimension_id) ON DELETE CASCADE,
    CONSTRAINT fk_dep_target FOREIGN KEY (depends_on_dimension_id)
        REFERENCES svarupa_dimensions (dimension_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- svarupa_concepts — the named constructs (attributes) of each dimension.
-- e.g. dimension 8 (Sthāyībhāvas) -> rati, hāsa, śoka, ...
-- -----------------------------------------------------------------------------
CREATE TABLE svarupa_concepts (
    concept_id      INT UNSIGNED     NOT NULL AUTO_INCREMENT PRIMARY KEY,
    dimension_id    TINYINT UNSIGNED NOT NULL,
    slug            VARCHAR(96)      NOT NULL,             -- machine code, unique within dimension
    name            VARCHAR(191)     NOT NULL,            -- display name
    sanskrit_term   VARCHAR(191)     NULL,
    category        VARCHAR(128)     NULL,                -- optional grouping within the dimension
    description     TEXT             NULL,                -- concept-level (status-independent) overview
    source_scripture VARCHAR(191)    NULL,
    sort_order      SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    created_at      TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_concepts_dim_slug (dimension_id, slug),
    KEY ix_concepts_dimension (dimension_id),
    CONSTRAINT fk_concepts_dimension FOREIGN KEY (dimension_id)
        REFERENCES svarupa_dimensions (dimension_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- svarupa_concept_descriptions — one row per (dimension, concept, status) triplet.
-- The dimension is reached through concept_id (no redundant FK). `description`
-- is the narrative; the optional facet columns mirror the source corpus
-- (overview / physical / emotional / mental) and remain single-valued per triplet.
-- -----------------------------------------------------------------------------
CREATE TABLE svarupa_concept_descriptions (
    description_id  BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT PRIMARY KEY,
    concept_id      INT UNSIGNED     NOT NULL,
    status_id       TINYINT UNSIGNED NOT NULL,
    description     TEXT             NOT NULL,            -- description for this triplet
    overview        TEXT             NULL,
    physical        TEXT             NULL,
    emotional       TEXT             NULL,
    mental          TEXT             NULL,
    created_at      TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_desc_concept_status (concept_id, status_id),
    KEY ix_desc_status (status_id),
    CONSTRAINT fk_desc_concept FOREIGN KEY (concept_id)
        REFERENCES svarupa_concepts (concept_id) ON DELETE CASCADE,
    CONSTRAINT fk_desc_status FOREIGN KEY (status_id)
        REFERENCES svarupa_status (status_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- SEED DATA
-- =============================================================================

-- Canonical status poles ------------------------------------------------------
INSERT INTO svarupa_status (status_id, code, label, polarity, sort_order, legacy_aliases) VALUES
    (1, 'deficiency', 'Deficiency', -1, 1, 'deficient,low,blocked,negative,under'),
    (2, 'balance',    'Balance',     0, 2, 'balanced,neutral,medium'),
    (3, 'excess',     'Excess',      1, 3, 'excessive,high,overactive,positive,over');

-- Analytical layers -----------------------------------------------------------
INSERT INTO svarupa_layer (layer_code, name) VALUES
    ('SEM', 'Semantic Resonance'),
    ('COT', 'LLM Chain-of-Thought'),
    ('AFF', 'Multi-Axis Affect'),
    ('PHE', 'Phenomenological'),
    ('PSY', 'Psycholinguistic'),
    ('MET', 'Metaphor'),
    ('NAR', 'Narrative Arc');

-- The 31 dimensions (D1..D30 documented; D31 reserved) ------------------------
INSERT INTO svarupa_dimensions (dimension_id, slug, name, sanskrit_term, family, is_reserved, notes) VALUES
    ( 1, 'pancha_mahabhutas',                  'Five Great Elements',                'Pañca Mahābhūtas',                       'Constitutional',        0, NULL),
    ( 2, 'trigunas',                           'Three Gunas',                        'Triguṇa — Sattva·Rajas·Tamas',           'Constitutional',        0, NULL),
    ( 3, 'manasika_prakriti',                  'Sixteen Faces of Mind',              'Mānasika Prakṛti',                       'Constitutional',        0, NULL),
    ( 4, 'seven_layers_of_consciousness',      'Seven Layers of Consciousness',      'Sapta Bhūmikā / Planes',                 'Consciousness',         0, NULL),
    ( 5, 'pancha_koshas',                      'Five Sheaths',                       'Pañca Kośa',                             'Consciousness',         0, NULL),
    ( 6, 'subtle_energies',                    'Subtle Energies',                    'Prāṇa Vāyus · Chakras · Nāḍīs',          'Consciousness',         0, 'Merges vāyus, chakras, nāḍīs'),
    ( 7, 'phenomenology',                      'Phenomenological Dimensions',        'Phenomenology of Experience',            'Phenomenological',      0, NULL),
    ( 8, 'sthayibhavas',                       'Nine Enduring Emotions',             'Sthāyībhāvas',                           'Affective',             0, NULL),
    ( 9, 'vyabhicaribhavas',                   'Thirty-Three Transient States',      'Vyabhicārībhāvas',                       'Affective',             0, NULL),
    (10, 'paths_of_engagement',                'Paths of Engagement',                'Karma · Jñāna · Rāja · Bhakti',          'Path & Practice',       0, NULL),
    (11, 'ashtanga_yoga',                      'Eightfold Refinement',               'Aṣṭāṅga Yoga',                           'Path & Practice',       0, NULL),
    (12, 'architecture_of_inner_life',         'Architecture of Inner Life',         'Karma · Saṁskāra · Vāsanā · Eṣaṇā',      'Karmic & Temporal',     0, NULL),
    (13, 'cyclical_evolution_of_consciousness','Cyclical Evolution of Consciousness','Kāla Chakra (individual)',               'Karmic & Temporal',     0, NULL),
    (14, 'yuga_cycles',                        'Yuga Cycles',                        'Yuga (collective time)',                 'Karmic & Temporal',     0, NULL),
    (15, 'tridosha',                           'Tridosha',                           'Vāta · Pitta · Kapha',                   'Constitutional',        0, NULL),
    (16, 'svabhava_svadharma',                 'Inner Nature & Its Law',             'Svabhāva & Svadharma',                   'Karmic & Temporal',     0, NULL),
    (17, 'three_lenses',                       'Three Lenses',                       'Adhibhautika · Adhidaivika · Ādhyātmika','Perceptual & Epistemic',0, NULL),
    (18, 'jyotish_shastra',                    'Science of Cosmic Light',            'Jyotiṣ Śāstra',                          'Cosmological',          0, NULL),
    (19, 'pancha_klesha',                      'Five Afflictions',                   'Pañca Kleśa',                            'Psychodynamic',         0, NULL),
    (20, 'pancha_vritti',                      'Five Modifications of Mind',         'Pañca Vṛtti',                            'Psychodynamic',         0, NULL),
    (21, 'antarayas',                          'The Nine Obstacles',                 'Antarāyas',                              'Psychodynamic',         0, NULL),
    (22, 'brahmaviharas',                      'Four Sublime Attitudes',             'Brahmavihāras',                          'Psychodynamic',         0, NULL),
    (23, 'sadhana_chatushtaya',                'Fourfold Qualification',             'Sādhana Chatuṣṭaya',                     'Ethical & Readiness',   0, NULL),
    (24, 'daivi_asuri_sampat',                 'Divine & Demoniacal Endowments',     'Daivī & Āsurī Sampat',                   'Ethical & Readiness',   0, NULL),
    (25, 'upasanas_vidyas',                    'Upanishadic Meditations',            'Upāsanās & Vidyās',                      'Soteriological',        0, NULL),
    (26, 'hatha_disciplines',                  'The Embodied Path',                  'Haṭha Disciplines',                      'Path & Practice',       0, NULL),
    (27, 'advaita_darshana',                   'The Non-Dual Vision',                'Advaita Darśana',                        'Soteriological',        0, NULL),
    (28, 'ways_of_knowing',                    'The Ways of Knowing',                'Pramāṇa & Jñāna',                        'Perceptual & Epistemic',0, NULL),
    (29, 'bandha_moksha',                      'Anatomy of Bondage & Liberation',    'Bandha & Mokṣa',                         'Soteriological',        0, NULL),
    (30, 'sadhana_practices',                  'Contemplative & Devotional Practice','Sādhanas',                               'Path & Practice',       0, NULL),
    (31, 'reserved_d31',                       'Reserved (D31)',                     NULL,                                     'Reserved',              1, 'Ratified open slot — registry grows by config, not redesign');

-- Primary layer affinities (registry "Primary Layer(s)") ----------------------
INSERT INTO svarupa_dimension_layer (dimension_id, layer_code, role) VALUES
    ( 1,'MET','primary'),( 1,'PHE','primary'),
    ( 2,'AFF','primary'),( 2,'PSY','primary'),
    ( 3,'COT','primary'),
    ( 4,'PHE','primary'),( 4,'COT','primary'),
    ( 5,'PHE','primary'),( 5,'MET','primary'),
    ( 6,'PHE','primary'),( 6,'MET','primary'),
    ( 7,'PHE','primary'),
    ( 8,'AFF','primary'),
    ( 9,'AFF','primary'),
    (10,'NAR','primary'),(10,'COT','primary'),
    (11,'COT','primary'),
    (12,'NAR','primary'),(12,'PSY','primary'),
    (13,'NAR','primary'),(13,'COT','primary'),
    (14,'NAR','primary'),(14,'COT','primary'),
    (15,'PHE','primary'),(15,'MET','primary'),
    (16,'NAR','primary'),(16,'COT','primary'),
    (17,'PSY','primary'),
    (18,'COT','primary'),
    (19,'COT','primary'),
    (20,'COT','primary'),
    (21,'COT','primary'),
    (22,'AFF','primary'),(22,'COT','primary'),
    (23,'COT','primary'),
    (24,'COT','primary'),(24,'AFF','primary'),
    (25,'COT','primary'),
    (26,'COT','primary'),
    (27,'COT','primary'),
    (28,'COT','primary'),
    (29,'NAR','primary'),(29,'COT','primary'),
    (30,'COT','primary');

-- Semantic Resonance is a contributing recall layer for all documented dims.
INSERT INTO svarupa_dimension_layer (dimension_id, layer_code, role)
SELECT dimension_id, 'SEM', 'contributing'
  FROM svarupa_dimensions
 WHERE is_reserved = 0;

-- Dimension dependencies (registry "Depends On") ------------------------------
INSERT INTO svarupa_dimension_dependency (dimension_id, depends_on_dimension_id) VALUES
    ( 3, 2),
    ( 5, 4),
    ( 6, 1),( 6, 5),
    ( 8, 7),
    ( 9, 8),( 9, 2),
    (10, 3),(10,16),
    (11,10),
    (13,12),
    (14,13),
    (15, 1),
    (16, 3),
    (20,19),
    (21,11),
    (25,27),
    (26, 6),(26,11),
    (28,17),
    (29,27),
    (30,25),(30,27);

-- -----------------------------------------------------------------------------
-- Example concepts + descriptions for D8 (Sthāyībhāvas — Nine Enduring Emotions).
-- The remaining concepts/descriptions are loaded from the corpus via ETL.
-- -----------------------------------------------------------------------------
INSERT INTO svarupa_concepts (dimension_id, slug, name, sanskrit_term, category, sort_order) VALUES
    (8, 'rati',     'Love / Delight',   'Rati',     'Sthāyībhāva', 1),
    (8, 'hasa',     'Mirth',            'Hāsa',     'Sthāyībhāva', 2),
    (8, 'shoka',    'Sorrow',           'Śoka',     'Sthāyībhāva', 3),
    (8, 'krodha',   'Anger',            'Krodha',   'Sthāyībhāva', 4),
    (8, 'utsaha',   'Energy / Resolve', 'Utsāha',   'Sthāyībhāva', 5),
    (8, 'bhaya',    'Fear',             'Bhaya',    'Sthāyībhāva', 6),
    (8, 'jugupsa',  'Disgust',          'Jugupsā',  'Sthāyībhāva', 7),
    (8, 'vismaya',  'Wonder',           'Vismaya',  'Sthāyībhāva', 8),
    (8, 'shama',    'Peace / Quietude', 'Śama',     'Sthāyībhāva', 9);

INSERT INTO svarupa_concept_descriptions (concept_id, status_id, description)
SELECT c.concept_id, s.status_id, t.description
  FROM (
        SELECT 'shoka' AS slug, 'balance'    AS status_code,
               'Sorrow met with presence: grief that opens the heart, honored without collapse into identity.' AS description
        UNION ALL SELECT 'shoka', 'excess',
               'Sorrow that floods the sense of self — identity-collapse, rumination, an inability to find ground.'
        UNION ALL SELECT 'shoka', 'deficiency',
               'Numbed or suppressed grief: loss is registered cognitively but the feeling is walled off.'
       ) AS t
  JOIN svarupa_concepts c ON c.dimension_id = 8 AND c.slug = t.slug
  JOIN svarupa_status   s ON s.code = t.status_code;

-- =============================================================================
-- Convenience view: the flat (dimension, concept, status, description) triplet.
-- =============================================================================
CREATE OR REPLACE VIEW v_svarupa_triplet_descriptions AS
SELECT d.dimension_id,
       d.slug          AS dimension_slug,
       d.name          AS dimension_name,
       c.concept_id,
       c.slug          AS concept_slug,
       c.name          AS concept_name,
       st.code         AS status_code,
       cd.description
  FROM svarupa_concept_descriptions cd
  JOIN svarupa_concepts   c  ON c.concept_id  = cd.concept_id
  JOIN svarupa_dimensions d  ON d.dimension_id = c.dimension_id
  JOIN svarupa_status     st ON st.status_id  = cd.status_id;
