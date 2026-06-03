CREATE TABLE tng.publications (
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title text NOT NULL,
    authors text,
    year integer,
    publication_type text,
    doi text,
    url text,
    file_id integer
);

CREATE TABLE tng.publication_entities (
    publication_id integer NOT NULL,
    entity_id integer NOT NULL,
    PRIMARY KEY (publication_id, entity_id)
);

ALTER TABLE ONLY tng.publications
    ADD CONSTRAINT publications_file_id_fkey FOREIGN KEY (file_id) REFERENCES tng.files(id) ON DELETE SET NULL;

ALTER TABLE ONLY tng.publication_entities
    ADD CONSTRAINT publication_entities_publication_id_fkey FOREIGN KEY (publication_id) REFERENCES tng.publications(id) ON DELETE CASCADE;

ALTER TABLE ONLY tng.publication_entities
    ADD CONSTRAINT publication_entities_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES tng.entities(id) ON DELETE CASCADE;

ALTER TABLE tng.publications OWNER TO openatlas;
ALTER TABLE tng.publication_entities OWNER TO openatlas;

GRANT ALL ON TABLE tng.publications TO openatlas;
GRANT ALL ON TABLE tng.publication_entities TO openatlas;
