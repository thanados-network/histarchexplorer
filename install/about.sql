DROP SCHEMA IF EXISTS tng CASCADE;
CREATE SCHEMA IF NOT EXISTS tng;

CREATE TABLE IF NOT EXISTS tng.config
(
    id           SERIAL PRIMARY KEY,
    name         TEXT,
    description  TEXT,
    address      TEXT,
    config_class INT,
    email        TEXT,
    orcid_id     TEXT,
    image        TEXT,
    website      TEXT,
    language     TEXT DEFAULT 'en'
);

CREATE TABLE IF NOT EXISTS tng.links
(
    id        SERIAL PRIMARY KEY,
    domain_id INT,
    range_id  INT,
    property  INT,
    attribute INT
);

CREATE TABLE IF NOT EXISTS tng.config_classes
(
    id          SERIAL PRIMARY KEY,
    name        TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS tng.config_properties
(
    id          SERIAL PRIMARY KEY,
    name        TEXT,
    name_inv    TEXT,
    description TEXT,
    domain      INT,
    range       INT
);

ALTER TABLE tng.config
    ADD CONSTRAINT config_config_classes_fk FOREIGN KEY (config_class) REFERENCES tng.config_classes (id);
ALTER TABLE tng.links
    ADD CONSTRAINT links_config_properties_fk FOREIGN KEY (property) REFERENCES tng.config_properties (id);
ALTER TABLE tng.links
    ADD CONSTRAINT links_config_fk_domain FOREIGN KEY (domain_id) REFERENCES tng.config (id);
ALTER TABLE tng.links
    ADD CONSTRAINT links_config_fk_range FOREIGN KEY (range_id) REFERENCES tng.config (id);
ALTER TABLE tng.links
    ADD CONSTRAINT links_config_fk_role FOREIGN KEY (attribute) REFERENCES tng.config (id);

CREATE OR REPLACE FUNCTION tng.delete_links_on_config_delete()
    RETURNS trigger
    LANGUAGE plpgsql
AS
$function$
BEGIN
    DELETE FROM tng.links WHERE domain_id = OLD.id OR range_id = OLD.id;
    RETURN OLD;
END;
$function$;

CREATE TRIGGER delete_links_trigger
    BEFORE DELETE
    ON tng.config
    FOR EACH ROW
EXECUTE FUNCTION tng.delete_links_on_config_delete();

INSERT INTO tng.config_classes (name) VALUES ('main_project');
INSERT INTO tng.config_classes (name) VALUES ('project');
INSERT INTO tng.config_classes (name) VALUES ('person');
INSERT INTO tng.config_classes (name) VALUES ('role');
INSERT INTO tng.config_classes (name) VALUES ('institution');
INSERT INTO tng.config_classes (name) VALUES ('language_code');

INSERT INTO tng.config_properties (name) VALUES ('has member');
INSERT INTO tng.config_properties (name) VALUES ('has affiliation');
INSERT INTO tng.config_properties (name) VALUES ('has translation');

INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('Max Mustermann', (SELECT id from tng.config_classes WHERE name = 'person'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('John Doe', (SELECT id from tng.config_classes WHERE name = 'person'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('Jane Doe', (SELECT id from tng.config_classes WHERE name = 'person'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');

INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('principial investigator', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('main coordinator', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('project researcher', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('software developer', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('design & programming', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('archaeologist', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('anthropologist', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('data acquisition', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('historian', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');

INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('sponsor', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('partner', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, 'https://example.exampe');


INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('THANADOS', (SELECT id from tng.config_classes WHERE name = 'main_project'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('RELIC', (SELECT id from tng.config_classes WHERE name = 'main_project'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('REPLICO', (SELECT id from tng.config_classes WHERE name = 'main_project'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');

INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('NHM', (SELECT id from tng.config_classes WHERE name = 'institution'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('University of Vienna', (SELECT id from tng.config_classes WHERE name = 'institution'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');
INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('Austrian Centre for Digital Humanities & Cultural Heritage', (SELECT id from tng.config_classes WHERE name = 'institution'), NULL, NULL, 'example@example.exampe', 'https://example.exampe');



INSERT INTO tng.links (domain_id,range_id,property,"attribute") VALUES
	 (52,57,2,NULL),
	 (53,57,2,NULL),
	 (41,35,1,NULL),
	 (41,56,1,NULL),
	 (53,112,2,NULL),
	 (52,112,2,NULL),
	 (35,112,2,72);




