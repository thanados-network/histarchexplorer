CREATE TABLE tng.predefined_filters
(
    id                integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sortorder         integer NOT NULL UNIQUE,
    label             jsonb NOT NULL DEFAULT '{}',
    description       jsonb NOT NULL DEFAULT '{}',
    icon              jsonb,
    tabs              jsonb NOT NULL DEFAULT '[]',
    filter_parameters jsonb NOT NULL DEFAULT '{}'
);

ALTER TABLE tng.predefined_filters OWNER TO openatlas;
GRANT ALL ON TABLE tng.predefined_filters TO openatlas;
GRANT USAGE, SELECT ON SEQUENCE tng.predefined_filters_id_seq TO openatlas;

INSERT INTO tng.predefined_filters
    (sortorder, label, description, icon, tabs, filter_parameters)
VALUES
    (1, '{"en": "Thanados"}',
     '{"en": "Show only entities belonging to the Thanados project."}',
     NULL, '["places", "features", "items"]',
     '{"case_study_ids": [181731], "classes": ["place", "artifact", "feature"], "include_subtypes": true, "begin_from": "0399-01-01", "include_no_begin": true, "include_no_end": true}'),
    (2, '{"en": "Churches before 1300"}',
     '{"en": "Churches before 1300"}', NULL, '["places"]',
     '{"type_ids": [285], "include_subtypes": true, "begin_to": "1251-01-01", "include_no_begin": false, "include_no_end": true}');