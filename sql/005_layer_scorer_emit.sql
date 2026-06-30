-- Layer scorer registry: which dimensions a layer scores and emits as DimensionalSignals.
--
--   svarupa_layer_scorer         dimension-level scorer config (FK -> dimensions, layer)
--   svarupa_layer_scorer_concept  output vocabulary per scorer (FK -> concepts, scorer)
--
-- Applicability (which concepts AFF may assess) remains in svarupa_concept_layer.
-- Emit intersection at runtime: concept_layer affinity ∩ scorer.emits_signals.
--
-- Usage:
--   mysql ... < sql/005_layer_scorer_emit.sql
-- Or: python scripts/seed_aff_layer_scorers.py

SET NAMES utf8mb4;

-- -----------------------------------------------------------------------------
-- svarupa_concept_layer (create if missing — companion migration may have created it)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS svarupa_concept_layer (
    dimension_id TINYINT UNSIGNED NOT NULL,
    concept_id   INT UNSIGNED     NOT NULL,
    layer_code   VARCHAR(8)       NOT NULL,
    created_at   TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (concept_id, layer_code),
    KEY ix_concept_layer_dimension (dimension_id),
    KEY ix_concept_layer_layer (layer_code),
    CONSTRAINT fk_concept_layer_dimension FOREIGN KEY (dimension_id)
        REFERENCES svarupa_dimensions (dimension_id) ON DELETE CASCADE,
    CONSTRAINT fk_concept_layer_concept FOREIGN KEY (concept_id)
        REFERENCES svarupa_concepts (concept_id) ON DELETE CASCADE,
    CONSTRAINT fk_concept_layer_layer FOREIGN KEY (layer_code)
        REFERENCES svarupa_layer (layer_code) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- svarupa_layer_scorer
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS svarupa_layer_scorer (
    scorer_id       SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    layer_code      VARCHAR(8)        NOT NULL,
    dimension_id    TINYINT UNSIGNED  NOT NULL,
    scorer_slug     VARCHAR(64)       NOT NULL,
    scorer_kind     ENUM('field_native', 'hypothesis_bridge') NOT NULL,
    data_ref        VARCHAR(191)      NOT NULL,
    pole_map_ref    VARCHAR(191)      NULL,
    modulator_ref   VARCHAR(191)      NULL,
    emits_signals   TINYINT(1)        NOT NULL DEFAULT 1,
    sort_order      TINYINT UNSIGNED  NOT NULL DEFAULT 0,
    created_at      TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (scorer_id),
    UNIQUE KEY uq_layer_scorer_dim (layer_code, dimension_id),
    KEY ix_scorer_layer (layer_code),
    CONSTRAINT fk_scorer_dimension FOREIGN KEY (dimension_id)
        REFERENCES svarupa_dimensions (dimension_id) ON DELETE CASCADE,
    CONSTRAINT fk_scorer_layer FOREIGN KEY (layer_code)
        REFERENCES svarupa_layer (layer_code) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- svarupa_layer_scorer_concept — FK-linked output vocabulary per scorer
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS svarupa_layer_scorer_concept (
    scorer_id   SMALLINT UNSIGNED NOT NULL,
    concept_id  INT UNSIGNED      NOT NULL,
    created_at  TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (scorer_id, concept_id),
    KEY ix_scorer_concept_concept (concept_id),
    CONSTRAINT fk_scorer_concept_scorer FOREIGN KEY (scorer_id)
        REFERENCES svarupa_layer_scorer (scorer_id) ON DELETE CASCADE,
    CONSTRAINT fk_scorer_concept_concept FOREIGN KEY (concept_id)
        REFERENCES svarupa_concepts (concept_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

START TRANSACTION;

DELETE sc FROM svarupa_layer_scorer_concept sc
  JOIN svarupa_layer_scorer s ON s.scorer_id = sc.scorer_id
 WHERE s.layer_code = 'AFF';

DELETE FROM svarupa_layer_scorer WHERE layer_code = 'AFF';

INSERT INTO svarupa_layer_scorer
    (layer_code, dimension_id, scorer_slug, scorer_kind, data_ref, pole_map_ref,
     modulator_ref, emits_signals, sort_order)
VALUES
    ('AFF', 2, 'guna_field', 'field_native', 'field/guna_synthesis.v1.json',
     'pole_maps/d2_poles.v1.json', NULL, 1, 1),
    ('AFF', 8, 'hyp2sthayi', 'hypothesis_bridge', 'bridge/hyp2sthayi.v2.json',
     'pole_maps/d8_poles.v1.json', 'bridge/guna_families.v1.json', 1, 2),
    ('AFF', 9, 'hyp2vyabhi', 'hypothesis_bridge', 'bridge/hyp2vyabhi.v2.json',
     NULL, 'bridge/guna_families.v1.json', 1, 3),
    ('AFF', 22, 'brahmavihara_tone', 'field_native', 'field/guna_synthesis.v1.json',
     NULL, NULL, 0, 4),
    ('AFF', 24, 'daivi_asuri_tone', 'field_native', 'field/guna_synthesis.v1.json',
     NULL, NULL, 0, 5);

INSERT INTO svarupa_layer_scorer_concept (scorer_id, concept_id)
SELECT s.scorer_id, cl.concept_id
  FROM svarupa_layer_scorer s
  JOIN svarupa_concept_layer cl
    ON cl.layer_code = s.layer_code AND cl.dimension_id = s.dimension_id
 WHERE s.layer_code = 'AFF';

COMMIT;

-- Verify:
-- SELECT s.dimension_id, d.slug, s.scorer_slug, s.emits_signals, COUNT(sc.concept_id) AS n_concepts
--   FROM svarupa_layer_scorer s
--   JOIN svarupa_dimensions d ON d.dimension_id = s.dimension_id
--   LEFT JOIN svarupa_layer_scorer_concept sc ON sc.scorer_id = s.scorer_id
--  WHERE s.layer_code = 'AFF'
--  GROUP BY s.scorer_id
--  ORDER BY s.sort_order;
