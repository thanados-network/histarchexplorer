--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13 (Debian 15.13-0+deb12u1)
-- Dumped by pg_dump version 15.13 (Debian 15.13-0+deb12u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY tng.properties DROP CONSTRAINT IF EXISTS relationship_labels_range_id_fkey;
ALTER TABLE IF EXISTS ONLY tng.properties DROP CONSTRAINT IF EXISTS relationship_labels_domain_id_fkey;
ALTER TABLE IF EXISTS ONLY tng.entities DROP CONSTRAINT IF EXISTS entities_class_id_fkey;
DROP TRIGGER IF EXISTS delete_links_trigger ON tng.entities;
ALTER TABLE IF EXISTS ONLY tng.settings DROP CONSTRAINT IF EXISTS settings_pkey;
ALTER TABLE IF EXISTS ONLY tng.maps DROP CONSTRAINT IF EXISTS maps_pkey;
ALTER TABLE IF EXISTS ONLY tng.links DROP CONSTRAINT IF EXISTS links_pkey;
ALTER TABLE IF EXISTS ONLY tng.entities DROP CONSTRAINT IF EXISTS entities_pkey;
ALTER TABLE IF EXISTS ONLY tng.properties DROP CONSTRAINT IF EXISTS config_properties_pkey;
ALTER TABLE IF EXISTS ONLY tng.classes DROP CONSTRAINT IF EXISTS config_classes_pkey;
ALTER TABLE IF EXISTS tng.settings ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS tng.maps ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS tng.settings_id_seq;
DROP TABLE IF EXISTS tng.settings;
DROP TABLE IF EXISTS tng.properties;
DROP SEQUENCE IF EXISTS tng.maps_id_seq;
DROP TABLE IF EXISTS tng.maps;
DROP SEQUENCE IF EXISTS tng.links_id_seq;
DROP TABLE IF EXISTS tng.links;
DROP TABLE IF EXISTS tng.entities;
DROP TABLE IF EXISTS tng.classes;
DROP FUNCTION IF EXISTS tng.getdates(first timestamp without time zone, last timestamp without time zone, comment text);
DROP FUNCTION IF EXISTS tng.delete_links_on_config_delete();
DROP SCHEMA IF EXISTS tng;
--
-- Name: tng; Type: SCHEMA; Schema: -; Owner: openatlas
--

CREATE SCHEMA tng;


ALTER SCHEMA tng OWNER TO openatlas;

--
-- Name: delete_links_on_config_delete(); Type: FUNCTION; Schema: tng; Owner: openatlas
--

CREATE FUNCTION tng.delete_links_on_config_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            DELETE FROM tng.links WHERE domain_id = OLD.id OR range_id =
            OLD.id;
            RETURN OLD;
        END;
        $$;


ALTER FUNCTION tng.delete_links_on_config_delete() OWNER TO openatlas;

--
-- Name: getdates(timestamp without time zone, timestamp without time zone, text); Type: FUNCTION; Schema: tng; Owner: openatlas
--

CREATE FUNCTION tng.getdates(first timestamp without time zone, last timestamp without time zone, comment text) RETURNS text
    LANGUAGE plpgsql
    AS $$
        DECLARE
            return_date TEXT;
        BEGIN
            CASE
                WHEN comment LIKE '-%' THEN
                    -- Use the comment as a negative year with leading zeros
                    SELECT TO_CHAR(comment::INTEGER, 'FM000000000') INTO return_date;
                ELSE
                    -- Use the date logic
                    SELECT TO_CHAR(LEAST(first, last), 'FM00000YYYY-MM-DD') INTO return_date;
                CASE WHEN EXTRACT(YEAR FROM (LEAST(first, last)::DATE)) < 1 THEN SELECT '-' || return_date INTO return_date; ELSE NULL; END CASE;
            END CASE;

            RETURN return_date;
        END;
        $$;


ALTER FUNCTION tng.getdates(first timestamp without time zone, last timestamp without time zone, comment text) OWNER TO openatlas;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: classes; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.classes (
    id integer NOT NULL,
    name text
);


ALTER TABLE tng.classes OWNER TO openatlas;

--
-- Name: classes_id_seq; Type: SEQUENCE; Schema: tng; Owner: openatlas
--

ALTER TABLE tng.classes ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tng.classes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: entities; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.entities (
    id integer NOT NULL,
    name jsonb,
    description jsonb,
    address jsonb,
    class_id integer,
    email text,
    orcid_id text,
    image text,
    website text,
    legal_notice jsonb,
    imprint jsonb,
    case_study_type_id integer
);


ALTER TABLE tng.entities OWNER TO openatlas;

--
-- Name: entities_id_seq; Type: SEQUENCE; Schema: tng; Owner: openatlas
--

ALTER TABLE tng.entities ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tng.entities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: links; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.links (
    id integer NOT NULL,
    domain_id integer,
    range_id integer,
    property integer,
    attribute integer,
    sortorder integer
);


ALTER TABLE tng.links OWNER TO openatlas;

--
-- Name: links_id_seq; Type: SEQUENCE; Schema: tng; Owner: openatlas
--

CREATE SEQUENCE tng.links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tng.links_id_seq OWNER TO openatlas;

--
-- Name: links_id_seq; Type: SEQUENCE OWNED BY; Schema: tng; Owner: openatlas
--

ALTER SEQUENCE tng.links_id_seq OWNED BY tng.links.id;


--
-- Name: links_id_seq1; Type: SEQUENCE; Schema: tng; Owner: openatlas
--

ALTER TABLE tng.links ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tng.links_id_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: maps; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.maps (
    id integer NOT NULL,
    name text,
    display_name text,
    tilestring text,
    sortorder integer
);


ALTER TABLE tng.maps OWNER TO openatlas;

--
-- Name: maps_id_seq; Type: SEQUENCE; Schema: tng; Owner: openatlas
--

CREATE SEQUENCE tng.maps_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tng.maps_id_seq OWNER TO openatlas;

--
-- Name: maps_id_seq; Type: SEQUENCE OWNED BY; Schema: tng; Owner: openatlas
--

ALTER SEQUENCE tng.maps_id_seq OWNED BY tng.maps.id;


--
-- Name: properties; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.properties (
    id integer NOT NULL,
    name jsonb,
    name_inv jsonb,
    domain_type_id integer,
    range_type_id integer
);


ALTER TABLE tng.properties OWNER TO openatlas;

--
-- Name: properties_id_seq; Type: SEQUENCE; Schema: tng; Owner: openatlas
--

ALTER TABLE tng.properties ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tng.properties_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: settings; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.settings (
    id integer NOT NULL,
    index_img text,
    index_map integer,
    img_map text,
    greyscale boolean,
    shown_classes text[],
    shown_types text[],
    hidden_classes text[],
    hidden_types text[],
    shown_ids text[],
    hidden_ids text[],
    case_study_type_id integer
);


ALTER TABLE tng.settings OWNER TO openatlas;

--
-- Name: settings_id_seq; Type: SEQUENCE; Schema: tng; Owner: openatlas
--

CREATE SEQUENCE tng.settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tng.settings_id_seq OWNER TO openatlas;

--
-- Name: settings_id_seq; Type: SEQUENCE OWNED BY; Schema: tng; Owner: openatlas
--

ALTER SEQUENCE tng.settings_id_seq OWNED BY tng.settings.id;


--
-- Name: maps id; Type: DEFAULT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.maps ALTER COLUMN id SET DEFAULT nextval('tng.maps_id_seq'::regclass);


--
-- Name: settings id; Type: DEFAULT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.settings ALTER COLUMN id SET DEFAULT nextval('tng.settings_id_seq'::regclass);


--
-- Data for Name: classes; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.classes (id, name) OVERRIDING SYSTEM VALUE VALUES
	(1, 'project'),
	(2, 'person'),
	(4, 'institution'),
	(5, 'main-project'),
	(6, 'language_code'),
	(3, 'attribute');


--
-- Data for Name: entities; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.entities (id, name, description, address, class_id, email, orcid_id, image, website, legal_notice, imprint, case_study_type_id) OVERRIDING SYSTEM VALUE VALUES
	(2, '{"de": "Stefan Eichert", "en": "Stefan Eichert"}', NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(3, '{"de": "Lisa Aldrian", "en": "Lisa Aldrian"}', NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(4, '{"de": "David Ruß", "en": "David Ruß"}', NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(5, '{"de": "Projektleitung", "en": "Principal Investigator"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(6, '{"de": "Hauptkoordinator", "en": "Main Coordinator"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(7, '{"de": "Forscher", "en": "Researcher"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(8, '{"de": "Softwareentwickler", "en": "Software Developer"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(9, '{"de": "Design & Programmierung", "en": "Design & Programming"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(10, '{"de": "Archäologe", "en": "Archaeologist"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(11, '{"de": "Anthropologe", "en": "Anthropologist"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(12, '{"de": "Datenaufnahme", "en": "Data Acquisition"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(13, '{"de": "Historiker", "en": "Historian"}', NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(14, '{"de": "Sponsor", "en": "Sponsor"}', NULL, NULL, 3, 'https://example.example', NULL, NULL, NULL, NULL, NULL, NULL),
	(15, '{"de": "Partner", "en": "Partner"}', NULL, NULL, 3, 'https://example.example', NULL, NULL, NULL, NULL, NULL, NULL),
	(20, '{"de": "Universität Wien", "en": "University of Vienna"}', '{"de": "Die Wiener Uni", "en": "Viennese university"}', '{"de": "Universitätsring 1\r\n1010 Wien", "en": "Universitätsring 1\r\n1010 Vienna"}', 4, 'uni@univie.ac.at', NULL, 'https://www.univie.ac.at/fileadmin/templates/Startseite/assets/uni_logo_220@2x.jpg', 'https://www.univie.ac.at/', '{}', '{}', NULL),
	(1, '{"de": "HistArchExplorer ", "en": "HistArchExplorer "}', '{"de": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.  \r\n\r\nDuis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.  \r\n\r\nUt wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.  \r\n\r\nNam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.  \r\n\r\nDuis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis.   \r\n\r\nAt vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam"}', '{}', 5, NULL, NULL, NULL, 'http://127.0.0.1:5000/', '{"de": "Ich auch nicht"}', '{"de": "Hab ich keins"}', NULL),
	(21, '{"de": "Austrian Centre for Digital Humanities", "en": "Austrian Centre for Digital Humanities & Cultural Heritage"}', '{"de": "Digitale Geisteswissenschaften"}', '{"de": "Bäckerstraße 13\r\n1010 Wien"}', 4, 'ACDH-CH-Office@oeaw.ac.at', NULL, 'https://www.oeaw.ac.at/fileadmin/oeaw/institutstemplate/acdh/img/acdh-ch-logo96.png', 'https://www.oeaw.ac.at/acdh/acdh-ch-home', '{}', '{}', NULL),
	(22, '{"de": "Nina Brundke", "en": "Nina Richards"}', '{"de": "Beste Anthropologin", "en": "Best anthropologist! "}', '{"en": "Burgring 7"}', 2, 'nina@richards.us', NULL, NULL, NULL, '{}', '{}', NULL),
	(23, '{"de": "Physiotherapeut"}', '{}', '{}', 3, NULL, NULL, NULL, NULL, '{}', '{}', NULL),
	(19, '{"de": "NHM", "en": "NHM_"}', '{"de": "Naturhistorisches Museum"}', '{"de": "Burgring 7"}', 4, NULL, NULL, 'https://nhm.at/jart/prj3/nhm-resp/resources/images/logo.svg', 'https://nhm.at/', '{}', '{}', NULL),
	(24, '{"de": "FH Wien"}', '{}', '{}', 4, NULL, NULL, NULL, NULL, '{}', '{}', NULL),
	(17, '{"de": "RELIC", "en": "RELIC"}', '{}', '{}', 1, NULL, NULL, NULL, NULL, '{}', '{}', 221174),
	(16, '{"de": "THANADOS", "en": "THANADOS"}', '{}', '{}', 1, NULL, NULL, NULL, 'https://thanados.net/', '{}', '{}', 181731),
	(18, '{"de": "REPLICO", "en": "REPLICO"}', '{}', '{}', 1, NULL, NULL, NULL, NULL, '{}', '{}', 221174);


--
-- Data for Name: links; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.links (id, domain_id, range_id, property, attribute, sortorder) OVERRIDING SYSTEM VALUE VALUES
	(1, 1, 22, 3, 5, 1),
	(2, 22, 19, 2, 11, 2),
	(3, 22, 21, 2, 5, 3),
	(4, 16, 22, 1, 12, 4),
	(5, 18, 22, 1, 5, 5),
	(6, 17, 22, 1, 10, 6),
	(7, 3, 19, 2, 8, 7),
	(8, 3, 24, 2, 23, 8),
	(9, 17, 3, 1, 12, 9),
	(10, 1, 3, 3, 8, 10),
	(11, 4, 19, 2, 10, 11),
	(12, 18, 4, 1, 13, 12),
	(13, 17, 4, 1, 10, 13),
	(14, 1, 4, 3, 12, 14),
	(15, 2, 19, 2, 5, 15),
	(16, 2, 19, 2, 10, 16),
	(17, 2, 19, 2, 8, 17),
	(20, 1, 2, 3, 5, 20),
	(21, 4, 20, 2, 13, 21),
	(22, 16, 20, 5, 14, 22),
	(23, 3, 24, 2, 14, 23),
	(24, 3, 24, 2, 23, 24),
	(25, 1, 2, 3, 23, 25),
	(27, 3, 21, 2, 23, 26),
	(28, 1, 24, 4, 23, 27),
	(29, 1, 2, 3, 23, 28);


--
-- Data for Name: maps; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.maps (id, name, display_name, tilestring, sortorder) VALUES
	(1, 'OpenStreetMap', 'Open Street Map', 'L.tileLayer(
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 19, attribution: ''&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors''});', 1);


--
-- Data for Name: properties; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.properties (id, name, name_inv, domain_type_id, range_type_id) OVERRIDING SYSTEM VALUE VALUES
	(1, '{"de": "hat Mitglied", "en": "has member"}', '{"de": "ist Mitglied von", "en": "is member of"}', 1, 2),
	(2, '{"de": "hat Zugehörigkeit", "en": "has affiliation"}', '{"de": "ist Zugehörigkeit von", "en": "is affiliation of"}', 2, 4),
	(3, '{"de": "hat Kernmitglied", "en": "has core member"}', '{"de": "ist Kernmitglied von", "en": "is core member of"}', 5, 2),
	(4, '{"de": "hat Kerninstitution", "en": "has core institution"}', '{"de": "ist Kerninstitution von", "en": "is core institution of"}', 5, 4),
	(5, '{"de": "hat Institution", "en": "has institution"}', '{"de": "ist Institution von", "en": "is institution of"}', 1, 4);


--
-- Data for Name: settings; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

INSERT INTO tng.settings (id, index_img, index_map, img_map, greyscale, shown_classes, shown_types, hidden_classes, hidden_types, shown_ids, hidden_ids, case_study_type_id) VALUES
	(1, '/static/images/index_map_bg/Blank_map_of_Europe_central_network.png', 1, 'map', true, '{artifact,human_remains,acquisition,event,activity,creation,move,production,modification,place,stratigraphic_unit,feature,source,bibliography,external_reference,edition,file}', NULL, '{group,stratigraphic_unit,source,external_reference}', NULL, NULL, NULL, 8240);


--
-- Name: classes_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.classes_id_seq', 1, false);


--
-- Name: entities_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.entities_id_seq', 29, true);


--
-- Name: links_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.links_id_seq', 29, true);


--
-- Name: links_id_seq1; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.links_id_seq1', 32, true);


--
-- Name: maps_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.maps_id_seq', 1, true);


--
-- Name: properties_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.properties_id_seq', 1, false);


--
-- Name: settings_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.settings_id_seq', 1, true);


--
-- Name: classes config_classes_pkey; Type: CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.classes
    ADD CONSTRAINT config_classes_pkey PRIMARY KEY (id);


--
-- Name: properties config_properties_pkey; Type: CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.properties
    ADD CONSTRAINT config_properties_pkey PRIMARY KEY (id);


--
-- Name: entities entities_pkey; Type: CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.entities
    ADD CONSTRAINT entities_pkey PRIMARY KEY (id);


--
-- Name: links links_pkey; Type: CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.links
    ADD CONSTRAINT links_pkey PRIMARY KEY (id);


--
-- Name: maps maps_pkey; Type: CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.maps
    ADD CONSTRAINT maps_pkey PRIMARY KEY (id);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);


--
-- Name: entities delete_links_trigger; Type: TRIGGER; Schema: tng; Owner: openatlas
--

CREATE TRIGGER delete_links_trigger BEFORE DELETE ON tng.entities FOR EACH ROW EXECUTE FUNCTION tng.delete_links_on_config_delete();


--
-- Name: entities entities_class_id_fkey; Type: FK CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.entities
    ADD CONSTRAINT entities_class_id_fkey FOREIGN KEY (class_id) REFERENCES tng.classes(id) NOT VALID;


--
-- Name: properties relationship_labels_domain_id_fkey; Type: FK CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.properties
    ADD CONSTRAINT relationship_labels_domain_id_fkey FOREIGN KEY (domain_type_id) REFERENCES tng.classes(id) NOT VALID;


--
-- Name: properties relationship_labels_range_id_fkey; Type: FK CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.properties
    ADD CONSTRAINT relationship_labels_range_id_fkey FOREIGN KEY (range_type_id) REFERENCES tng.classes(id) NOT VALID;


--
-- PostgreSQL database dump complete
--

