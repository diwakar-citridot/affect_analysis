-- Add role column to svarupa_concept_layer (primary vs contributing layer affinity).
--
-- Mirrors svarupa_dimension_layer.role: whether a layer is primary (●) or
-- contributing (○) for a given concept.
--
-- Usage:
--   mysql -u ... -p svarupa_assistant_v1 < sql/006_concept_layer_role.sql
-- Or: python scripts/seed_concept_layer_from_excel.py  (runs this DDL automatically)

SET NAMES utf8mb4;

-- Idempotent when run via scripts/seed_concept_layer_from_excel.py (checks information_schema first).
ALTER TABLE svarupa_concept_layer
    ADD COLUMN role ENUM('primary','contributing') NOT NULL DEFAULT 'contributing'
    AFTER layer_code;
