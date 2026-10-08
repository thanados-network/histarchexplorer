-- Add vocabulary filters, widget title and navigation, preserving choices.
INSERT INTO tng.system_settings (key, value)
VALUES
    ('vocabulary_include_ids', '[]'::jsonb),
    ('vocabulary_exclude_ids', '[]'::jsonb),
    ('vocabulary_title', '""'::jsonb),
    ('menu_management',
     '{"vocabulary": {"show": true, "page_type": "default"}}'::jsonb)
ON CONFLICT (key) DO NOTHING;

UPDATE tng.system_settings
SET value = value ||
    '{"vocabulary": {"show": true, "page_type": "default"}}'::jsonb
WHERE key = 'menu_management'
    AND jsonb_typeof(value) = 'object'
    AND NOT (value ? 'vocabulary');
