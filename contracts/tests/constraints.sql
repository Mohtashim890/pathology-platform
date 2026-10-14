-- Behaviour checks for schema.sql (Lesson L1.3, step 3).
-- Run after schema.sql on an EMPTY database. Lines marked "EXPECT ERROR" must fail.

-- Valid data
INSERT INTO cases (id, case_key, site, specimen_type, received_at)
VALUES ('01928f4e-6f00-7b11-8c2d-1a2b3c4d5e01', 'C16-TUMOR-001', 'camelyon16', 'lymph_node', now());

INSERT INTO slides (id, case_id, stain, object_key, checksum_sha256, status)
VALUES ('01928f4e-7a10-7c3e-9f2a-3b5d6e7f8a01', '01928f4e-6f00-7b11-8c2d-1a2b3c4d5e01', 'he',
        'raw/01928f4e-7a10-7c3e-9f2a-3b5d6e7f8a01', repeat('a', 64), 'ingested');

-- EXPECT ERROR: same checksum = duplicate slide (US-13)
INSERT INTO slides (id, case_id, stain, object_key, checksum_sha256, status)
VALUES ('01928f4e-7a10-7c3e-9f2a-3b5d6e7f8a02', '01928f4e-6f00-7b11-8c2d-1a2b3c4d5e01', 'he',
        'raw/other', repeat('a', 64), 'ingested');

-- EXPECT ERROR: unknown status value
UPDATE slides SET status = 'done' WHERE id = '01928f4e-7a10-7c3e-9f2a-3b5d6e7f8a01';

-- Two staging models, then try to make both production
INSERT INTO model_versions (id, name, version, task, onnx_key, model_card, input_mpp, tile_size, status)
VALUES ('01928e10-0000-7000-8000-00000000aa01', 'tumor-resnet18', '1.0.0', 'tumor_detection',
        'models/a/model.onnx', '{}', 0.5, 96, 'production'),
       ('01928e10-0000-7000-8000-00000000aa02', 'tumor-resnet18', '1.1.0', 'tumor_detection',
        'models/b/model.onnx', '{}', 0.5, 96, 'staging');

-- EXPECT ERROR: only one production model per task (US-21)
UPDATE model_versions SET status = 'production' WHERE id = '01928e10-0000-7000-8000-00000000aa02';

-- EXPECT ERROR: a disagreement needs a comment (US-05); also fails on the missing run
INSERT INTO pathologist_decisions (id, run_id, decided_by, decision)
VALUES ('01928f4e-b000-7000-8000-000000000001', '01928f4e-9c30-7e50-b14c-5d7e8f9a0b03', 'dr.malik', 'disagree');

-- Should list 1 case, 1 slide, 2 models
SELECT (SELECT count(*) FROM cases) AS cases,
       (SELECT count(*) FROM slides) AS slides,
       (SELECT count(*) FROM model_versions) AS models;
