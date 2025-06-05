DROP SCHEMA IF EXISTS tng CASCADE;
CREATE SCHEMA IF NOT EXISTS tng;

CREATE TABLE IF NOT EXISTS tng.maps
(
    id
    SERIAL
    PRIMARY
    KEY,
    name
    TEXT,
    display_name
    TEXT,
    tilestring
    TEXT,
    sortorder
    INT
);

INSERT INTO tng.maps (name, display_name, tilestring, sortorder)
VALUES ('OpenStreetMap', 'Open Street Map', 'L.tileLayer(
              "https://tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 19, attribution: ''&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors''});', 1);

CREATE TABLE IF NOT EXISTS tng.config
(
    id
    SERIAL
    PRIMARY
    KEY,
    name
    JSONB,
    description
    JSONB,
    address
    JSONB,
    config_class
    INT,
    email
    TEXT,
    orcid_id
    TEXT,
    image
    TEXT,
    website
    TEXT,
    legal_notice
    JSONB,
    imprint
    JSONB
);

CREATE TABLE IF NOT EXISTS tng.links
(
    id
    SERIAL
    PRIMARY
    KEY,
    domain_id
    INT,
    range_id
    INT,
    property
    INT,
    attribute
    INT,
    sortorder
    INT
);

CREATE TABLE IF NOT EXISTS tng.config_classes
(
    id
    SERIAL
    PRIMARY
    KEY,
    name
    TEXT,
    description
    TEXT
);

CREATE TABLE IF NOT EXISTS tng.config_properties
(
    id
    SERIAL
    PRIMARY
    KEY,
    name
    JSONB,
    name_inv
    JSONB,
    description
    JSONB,
    domain
    INT,
    range
    INT
);

ALTER TABLE tng.config
    ADD CONSTRAINT config_config_classes_fk FOREIGN KEY (
                                                         config_class) REFERENCES tng.config_classes (id);
ALTER TABLE tng.links
    ADD CONSTRAINT links_config_properties_fk FOREIGN KEY (property)
        REFERENCES tng.config_properties (id);
ALTER TABLE tng.links
    ADD CONSTRAINT links_config_fk_domain FOREIGN KEY (domain_id)
        REFERENCES tng.config (id);
ALTER TABLE tng.links
    ADD CONSTRAINT links_config_fk_range FOREIGN KEY (range_id)
        REFERENCES tng.config (id);
ALTER TABLE tng.links
    ADD CONSTRAINT links_config_fk_role FOREIGN KEY (attribute)
        REFERENCES tng.config (id);

CREATE
OR REPLACE FUNCTION tng.delete_links_on_config_delete()
              RETURNS trigger
              LANGUAGE plpgsql
          AS
          $function$
BEGIN
DELETE
FROM tng.links
WHERE domain_id = OLD.id
   OR range_id =
      OLD.id;
RETURN OLD;
END;
          $function$;

CREATE TRIGGER delete_links_trigger
    BEFORE DELETE
    ON tng.config
    FOR EACH ROW
    EXECUTE FUNCTION tng.delete_links_on_config_delete();

INSERT INTO tng.config_classes (name)
VALUES ('project');
INSERT INTO tng.config_classes (name)
VALUES ('person');
INSERT INTO tng.config_classes (name)
VALUES ('role');
INSERT INTO tng.config_classes (name)
VALUES ('institution');
INSERT INTO tng.config_classes (name)
VALUES ('main-project');
INSERT INTO tng.config_classes (name)
VALUES ('language_code');

INSERT INTO tng.config_properties (name, name_inv, domain, range)
VALUES ('{"de": "hat Mitglied", "en": "has member"}'::jsonb, '{"de": "ist Mitglied von", "en": "is member of"}'::jsonb,
        (SELECT id FROM tng.config_classes WHERE name = 'project'),
        (SELECT id FROM tng.config_classes WHERE name = 'person'));

INSERT INTO tng.config_properties (name, name_inv, domain, range)
VALUES ('{"de": "hat Zugehörigkeit", "en": "has affiliation"}'::jsonb, '{"de": "ist Zugehörigkeit von", "en": "is affiliation of"}'::jsonb, (SELECT id FROM tng.config_classes WHERE name = 'person'), (SELECT id FROM tng.config_classes WHERE name = 'institution'));

INSERT INTO tng.config_properties (name, name_inv, domain, range)
VALUES ('{"de": "hat Kernmitglied", "en": "has core member"}'::jsonb, '{"de": "ist Kernmitglied von", "en": "is core member of"}'::jsonb,
        (SELECT id
         FROM tng.config_classes
         WHERE name =
               'main-project'), (SELECT id FROM tng.config_classes WHERE name = 'person'));

INSERT INTO tng.config_properties (name, name_inv, domain, range)
VALUES ('{"de": "hat Kerninstitution", "en": "has core institution"}'::jsonb, '{"de": "ist Kerninstitution von", "en": "is core institution of"}'::jsonb,
        (SELECT id
         FROM tng.config_classes
         WHERE name =
               'main-project'), (SELECT id
                                 FROM tng.config_classes
                                 WHERE name = 'institution'));

INSERT INTO tng.config_properties (name, name_inv, domain, range)
VALUES ('{"de": "hat Institution", "en": "has institution"}'::jsonb, '{"de": "ist Institution von", "en": "is institution of"}'::jsonb,
        (SELECT id FROM tng.config_classes WHERE name = 'project'),
        (SELECT id
         FROM tng.config_classes
         WHERE name =
               'institution'));

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Hauptprojekt", "en": "Main Project"}'::jsonb,
        (SELECT id from tng.config_classes WHERE name = 'main-project'),
        NULL, NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Stefan Eichert", "en": "Stefan Eichert"}'::jsonb,
        (SELECT id from tng.config_classes WHERE name = 'person'), NULL,
        NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Lisa Aldrian", "en": "Lisa Aldrian"}'::jsonb,
        (SELECT id from tng.config_classes WHERE name = 'person'), NULL,
        NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "David Ruß", "en": "David Ruß"}'::jsonb, (SELECT id
                                                          from tng.config_classes
                                                          WHERE name = 'person'), NULL, NULL, NULL,
        NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Projektleitung", "en": "Principal Investigator"}'::jsonb, (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Hauptkoordinator", "en": "Main Coordinator"}'::jsonb, (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Forscher", "en": "Researcher"}'::jsonb, (SELECT id
                                                          from tng.config_classes
                                                          WHERE name = 'role'), NULL, NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Softwareentwickler", "en": "Software Developer"}'::jsonb, (SELECT id
                                                                            from tng.config_classes
                                                                            WHERE name =
                                                                                  'role'), NULL, NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Design & Programmierung", "en": "Design & Programming"}'::jsonb, (SELECT id
                                                                                   from tng.config_classes
                                                                                   WHERE name
                                                                                             = 'role'), NULL, NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Archäologe", "en": "Archaeologist"}'::jsonb,
        (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL,
        NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Anthropologe", "en": "Anthropologist"}'::jsonb,
        (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL,
        NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Datenaufnahme", "en": "Data Acquisition"}'::jsonb,
        (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL,
        NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Historiker", "en": "Historian"}'::jsonb, (SELECT id
                                                           from tng.config_classes
                                                           WHERE name = 'role'), NULL, NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Sponsor", "en": "Sponsor"}'::jsonb, (SELECT id
                                                      from tng.config_classes
                                                      WHERE name = 'role'), NULL, NULL,
        'https://example.example', NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Partner", "en": "Partner"}'::jsonb, (SELECT id
                                                      from tng.config_classes
                                                      WHERE name = 'role'), NULL, NULL,
        'https://example.example', NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "THANADOS", "en": "THANADOS"}'::jsonb, (SELECT id
                                                        from tng.config_classes
                                                        WHERE name = 'project'), NULL, NULL, NULL,
        NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "RELIC", "en": "RELIC"}'::jsonb, (SELECT id
                                                  from tng.config_classes
                                                  WHERE name = 'project'), NULL, NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "REPLICO", "en": "REPLICO"}'::jsonb, (SELECT id
                                                      from tng.config_classes
                                                      WHERE name = 'project'), NULL, NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "NHM", "en": "NHM"}'::jsonb, (SELECT id from tng.config_classes WHERE name = 'institution'), NULL, NULL, NULL,
        NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"de": "Universität Wien", "en": "University of Vienna"}'::jsonb, (SELECT id
                                                                            from tng.config_classes
                                                                            WHERE name =
                                                                                  'institution'), NULL, NULL, NULL, NULL);

INSERT INTO tng.config (name, config_class, description, address,
                        email, website)
VALUES ('{"en": "Austrian Centre for Digital Humanities & Cultural Heritage"}'::jsonb, (SELECT id
                                                                                        from tng.config_classes
                                                                                        WHERE name =
                                                                                              'institution'), NULL, NULL, NULL, NULL);


CREATE TABLE IF NOT EXISTS tng.settings
(
    id
    SERIAL
    PRIMARY
    KEY,
    index_img
    TEXT,
    index_map
    INT,
    img_map
    TEXT,
    greyscale
    BOOLEAN,
    shown_entities
    JSONB, --classes
    shown_types
    JSONB, --types
    hidden_entities
    JSONB, --classes
    hidden_types
    JSONB, --types
    shown_ids
    JSONB, --ids
    hidden_ids
    JSONB  --ids
);

INSERT INTO tng.settings (index_img, index_map, img_map, greyscale,
                          shown_entities)
VALUES ('/static/images/index_map_bg/Blank_map_of_Europe_central_network.png', 1, 'image', TRUE, '[]'::JSONB)


create function tng.getdates(first timestamp without time zone, last timestamp without time zone, comment text) returns text
    language plpgsql
          as
          $$
DECLARE
return_date TEXT;
BEGIN
CASE
                  WHEN comment LIKE '-%' THEN
                      -- Use the comment as a negative year with leading zeros
SELECT TO_CHAR(comment::INTEGER, 'FM000000000')
INTO return_date;
ELSE
                      -- Use the date logic
SELECT TO_CHAR(LEAST(first, last), 'FM00000YYYY-MM-DD')
INTO return_date;
CASE WHEN EXTRACT(YEAR FROM (LEAST(first, last)::DATE)) < 1 THEN
SELECT '-' || return_date
INTO return_date;
ELSE NULL;
END CASE;
END
CASE;

RETURN return_date;
END;
          $$;