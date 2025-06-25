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
-- Name: config; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.config (
    id integer NOT NULL,
    name jsonb,
    description jsonb,
    address jsonb,
    config_class integer,
    email text,
    orcid_id text,
    image text,
    website text,
    legal_notice jsonb,
    imprint jsonb
);


ALTER TABLE tng.config OWNER TO openatlas;

--
-- Name: config_classes; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.config_classes (
    id integer NOT NULL,
    name text,
    description text
);


ALTER TABLE tng.config_classes OWNER TO openatlas;

--
-- Name: config_classes_id_seq; Type: SEQUENCE; Schema: tng; Owner: openatlas
--

CREATE SEQUENCE tng.config_classes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tng.config_classes_id_seq OWNER TO openatlas;

--
-- Name: config_classes_id_seq; Type: SEQUENCE OWNED BY; Schema: tng; Owner: openatlas
--

ALTER SEQUENCE tng.config_classes_id_seq OWNED BY tng.config_classes.id;


--
-- Name: config_id_seq; Type: SEQUENCE; Schema: tng; Owner: openatlas
--

CREATE SEQUENCE tng.config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tng.config_id_seq OWNER TO openatlas;

--
-- Name: config_id_seq; Type: SEQUENCE OWNED BY; Schema: tng; Owner: openatlas
--

ALTER SEQUENCE tng.config_id_seq OWNED BY tng.config.id;


--
-- Name: config_properties; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.config_properties (
    id integer NOT NULL,
    name jsonb,
    name_inv jsonb,
    description jsonb,
    domain integer,
    range integer
);


ALTER TABLE tng.config_properties OWNER TO openatlas;

--
-- Name: config_properties_id_seq; Type: SEQUENCE; Schema: tng; Owner: openatlas
--

CREATE SEQUENCE tng.config_properties_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tng.config_properties_id_seq OWNER TO openatlas;

--
-- Name: config_properties_id_seq; Type: SEQUENCE OWNED BY; Schema: tng; Owner: openatlas
--

ALTER SEQUENCE tng.config_properties_id_seq OWNED BY tng.config_properties.id;


--
-- Name: entities; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.entities (
    id integer DEFAULT nextval('tng.config_id_seq'::regclass) NOT NULL,
    name jsonb,
    description jsonb,
    address jsonb,
    type integer,
    email text,
    orcid_id text,
    image text,
    website text,
    legal_notice jsonb,
    imprint jsonb
);


ALTER TABLE tng.entities OWNER TO openatlas;

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
-- Name: relationship_labels; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.relationship_labels (
    id integer DEFAULT nextval('tng.config_properties_id_seq'::regclass) NOT NULL,
    name jsonb,
    name_inv jsonb,
    domain_type_id integer,
    range_type_id integer
);


ALTER TABLE tng.relationship_labels OWNER TO openatlas;

--
-- Name: settings; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.settings (
    id integer NOT NULL,
    index_img text,
    index_map integer,
    img_map text,
    greyscale boolean,
    shown_entities text[],
    shown_types text[],
    hidden_entities text[],
    hidden_types text[],
    shown_ids text[],
    hidden_ids text[]
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
-- Name: types; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.types (
    id integer DEFAULT nextval('tng.config_classes_id_seq'::regclass) NOT NULL,
    name text
);


ALTER TABLE tng.types OWNER TO openatlas;

--
-- Name: config id; Type: DEFAULT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.config ALTER COLUMN id SET DEFAULT nextval('tng.config_id_seq'::regclass);


--
-- Name: config_classes id; Type: DEFAULT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.config_classes ALTER COLUMN id SET DEFAULT nextval('tng.config_classes_id_seq'::regclass);


--
-- Name: config_properties id; Type: DEFAULT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.config_properties ALTER COLUMN id SET DEFAULT nextval('tng.config_properties_id_seq'::regclass);


--
-- Name: links id; Type: DEFAULT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.links ALTER COLUMN id SET DEFAULT nextval('tng.links_id_seq'::regclass);


--
-- Name: maps id; Type: DEFAULT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.maps ALTER COLUMN id SET DEFAULT nextval('tng.maps_id_seq'::regclass);


--
-- Name: settings id; Type: DEFAULT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.settings ALTER COLUMN id SET DEFAULT nextval('tng.settings_id_seq'::regclass);


--
-- Data for Name: config; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

COPY tng.config (id, name, description, address, config_class, email, orcid_id, image, website, legal_notice, imprint) FROM stdin;
2	{"de": "Stefan Eichert", "en": "Stefan Eichert"}	\N	\N	2	\N	\N	\N	\N	\N	\N
3	{"de": "Lisa Aldrian", "en": "Lisa Aldrian"}	\N	\N	2	\N	\N	\N	\N	\N	\N
4	{"de": "David Ruß", "en": "David Ruß"}	\N	\N	2	\N	\N	\N	\N	\N	\N
5	{"de": "Projektleitung", "en": "Principal Investigator"}	\N	\N	3	\N	\N	\N	\N	\N	\N
6	{"de": "Hauptkoordinator", "en": "Main Coordinator"}	\N	\N	3	\N	\N	\N	\N	\N	\N
7	{"de": "Forscher", "en": "Researcher"}	\N	\N	3	\N	\N	\N	\N	\N	\N
8	{"de": "Softwareentwickler", "en": "Software Developer"}	\N	\N	3	\N	\N	\N	\N	\N	\N
9	{"de": "Design & Programmierung", "en": "Design & Programming"}	\N	\N	3	\N	\N	\N	\N	\N	\N
10	{"de": "Archäologe", "en": "Archaeologist"}	\N	\N	3	\N	\N	\N	\N	\N	\N
11	{"de": "Anthropologe", "en": "Anthropologist"}	\N	\N	3	\N	\N	\N	\N	\N	\N
12	{"de": "Datenaufnahme", "en": "Data Acquisition"}	\N	\N	3	\N	\N	\N	\N	\N	\N
13	{"de": "Historiker", "en": "Historian"}	\N	\N	3	\N	\N	\N	\N	\N	\N
14	{"de": "Sponsor", "en": "Sponsor"}	\N	\N	3	https://example.example	\N	\N	\N	\N	\N
15	{"de": "Partner", "en": "Partner"}	\N	\N	3	https://example.example	\N	\N	\N	\N	\N
17	{"de": "RELIC", "en": "RELIC"}	\N	\N	1	\N	\N	\N	\N	\N	\N
18	{"de": "REPLICO", "en": "REPLICO"}	\N	\N	1	\N	\N	\N	\N	\N	\N
20	{"de": "Universität Wien", "en": "University of Vienna"}	{"de": "Die Wiener Uni", "en": "Viennese university"}	{"de": "Universitätsring 1\\r\\n1010 Wien", "en": "Universitätsring 1\\r\\n1010 Vienna"}	4	uni@univie.ac.at	\N	https://www.univie.ac.at/fileadmin/templates/Startseite/assets/uni_logo_220@2x.jpg	https://www.univie.ac.at/	{}	{}
1	{"de": "HistArchExplorer ", "en": "HistArchExplorer "}	{"de": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.  \\r\\n\\r\\nDuis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.  \\r\\n\\r\\nUt wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.  \\r\\n\\r\\nNam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.  \\r\\n\\r\\nDuis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis.   \\r\\n\\r\\nAt vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam"}	{}	5	\N	\N	\N	http://127.0.0.1:5000/	{"de": "Ich auch nicht"}	{"de": "Hab ich keins"}
21	{"de": "Austrian Centre for Digital Humanities", "en": "Austrian Centre for Digital Humanities & Cultural Heritage"}	{"de": "Digitale Geisteswissenschaften"}	{"de": "Bäckerstraße 13\\r\\n1010 Wien"}	4	ACDH-CH-Office@oeaw.ac.at	\N	https://www.oeaw.ac.at/fileadmin/oeaw/institutstemplate/acdh/img/acdh-ch-logo96.png	https://www.oeaw.ac.at/acdh/acdh-ch-home	{}	{}
22	{"de": "Nina Brundke", "en": "Nina Richards"}	{"de": "Beste Anthropologin", "en": "Best anthropologist! "}	{"en": "Burgring 7"}	2	nina@richards.us	\N	\N	\N	{}	{}
23	{"de": "Physiotherapeut"}	{}	{}	3	\N	\N	\N	\N	{}	{}
19	{"de": "NHM", "en": "NHM_"}	{"de": "Naturhistorisches Museum"}	{"de": "Burgring 7"}	4	\N	\N	https://nhm.at/jart/prj3/nhm-resp/resources/images/logo.svg	https://nhm.at/	{}	{}
24	{"de": "FH Wien"}	{}	{}	4	\N	\N	\N	\N	{}	{}
16	{"de": "THANADOS", "en": "THANADOS"}	{}	{}	1	\N	\N	\N	https://thanados.net/	{}	{}
\.


--
-- Data for Name: config_classes; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

COPY tng.config_classes (id, name, description) FROM stdin;
1	project	\N
2	person	\N
3	role	\N
4	institution	\N
5	main-project	\N
6	language_code	\N
\.


--
-- Data for Name: config_properties; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

COPY tng.config_properties (id, name, name_inv, description, domain, range) FROM stdin;
1	{"de": "hat Mitglied", "en": "has member"}	{"de": "ist Mitglied von", "en": "is member of"}	\N	1	2
2	{"de": "hat Zugehörigkeit", "en": "has affiliation"}	{"de": "ist Zugehörigkeit von", "en": "is affiliation of"}	\N	2	4
3	{"de": "hat Kernmitglied", "en": "has core member"}	{"de": "ist Kernmitglied von", "en": "is core member of"}	\N	5	2
4	{"de": "hat Kerninstitution", "en": "has core institution"}	{"de": "ist Kerninstitution von", "en": "is core institution of"}	\N	5	4
5	{"de": "hat Institution", "en": "has institution"}	{"de": "ist Institution von", "en": "is institution of"}	\N	1	4
\.


--
-- Data for Name: entities; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

COPY tng.entities (id, name, description, address, type, email, orcid_id, image, website, legal_notice, imprint) FROM stdin;
2	{"de": "Stefan Eichert", "en": "Stefan Eichert"}	\N	\N	2	\N	\N	\N	\N	\N	\N
3	{"de": "Lisa Aldrian", "en": "Lisa Aldrian"}	\N	\N	2	\N	\N	\N	\N	\N	\N
4	{"de": "David Ruß", "en": "David Ruß"}	\N	\N	2	\N	\N	\N	\N	\N	\N
5	{"de": "Projektleitung", "en": "Principal Investigator"}	\N	\N	3	\N	\N	\N	\N	\N	\N
6	{"de": "Hauptkoordinator", "en": "Main Coordinator"}	\N	\N	3	\N	\N	\N	\N	\N	\N
7	{"de": "Forscher", "en": "Researcher"}	\N	\N	3	\N	\N	\N	\N	\N	\N
8	{"de": "Softwareentwickler", "en": "Software Developer"}	\N	\N	3	\N	\N	\N	\N	\N	\N
9	{"de": "Design & Programmierung", "en": "Design & Programming"}	\N	\N	3	\N	\N	\N	\N	\N	\N
10	{"de": "Archäologe", "en": "Archaeologist"}	\N	\N	3	\N	\N	\N	\N	\N	\N
11	{"de": "Anthropologe", "en": "Anthropologist"}	\N	\N	3	\N	\N	\N	\N	\N	\N
12	{"de": "Datenaufnahme", "en": "Data Acquisition"}	\N	\N	3	\N	\N	\N	\N	\N	\N
13	{"de": "Historiker", "en": "Historian"}	\N	\N	3	\N	\N	\N	\N	\N	\N
14	{"de": "Sponsor", "en": "Sponsor"}	\N	\N	3	https://example.example	\N	\N	\N	\N	\N
15	{"de": "Partner", "en": "Partner"}	\N	\N	3	https://example.example	\N	\N	\N	\N	\N
17	{"de": "RELIC", "en": "RELIC"}	\N	\N	1	\N	\N	\N	\N	\N	\N
18	{"de": "REPLICO", "en": "REPLICO"}	\N	\N	1	\N	\N	\N	\N	\N	\N
20	{"de": "Universität Wien", "en": "University of Vienna"}	{"de": "Die Wiener Uni", "en": "Viennese university"}	{"de": "Universitätsring 1\\r\\n1010 Wien", "en": "Universitätsring 1\\r\\n1010 Vienna"}	4	uni@univie.ac.at	\N	https://www.univie.ac.at/fileadmin/templates/Startseite/assets/uni_logo_220@2x.jpg	https://www.univie.ac.at/	{}	{}
1	{"de": "HistArchExplorer ", "en": "HistArchExplorer "}	{"de": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.  \\r\\n\\r\\nDuis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.  \\r\\n\\r\\nUt wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.  \\r\\n\\r\\nNam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.  \\r\\n\\r\\nDuis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis.   \\r\\n\\r\\nAt vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam"}	{}	5	\N	\N	\N	http://127.0.0.1:5000/	{"de": "Ich auch nicht"}	{"de": "Hab ich keins"}
21	{"de": "Austrian Centre for Digital Humanities", "en": "Austrian Centre for Digital Humanities & Cultural Heritage"}	{"de": "Digitale Geisteswissenschaften"}	{"de": "Bäckerstraße 13\\r\\n1010 Wien"}	4	ACDH-CH-Office@oeaw.ac.at	\N	https://www.oeaw.ac.at/fileadmin/oeaw/institutstemplate/acdh/img/acdh-ch-logo96.png	https://www.oeaw.ac.at/acdh/acdh-ch-home	{}	{}
22	{"de": "Nina Brundke", "en": "Nina Richards"}	{"de": "Beste Anthropologin", "en": "Best anthropologist! "}	{"en": "Burgring 7"}	2	nina@richards.us	\N	\N	\N	{}	{}
23	{"de": "Physiotherapeut"}	{}	{}	3	\N	\N	\N	\N	{}	{}
19	{"de": "NHM", "en": "NHM_"}	{"de": "Naturhistorisches Museum"}	{"de": "Burgring 7"}	4	\N	\N	https://nhm.at/jart/prj3/nhm-resp/resources/images/logo.svg	https://nhm.at/	{}	{}
24	{"de": "FH Wien"}	{}	{}	4	\N	\N	\N	\N	{}	{}
16	{"de": "THANADOS", "en": "THANADOS"}	{}	{}	1	\N	\N	\N	https://thanados.net/	{}	{}
\.


--
-- Data for Name: links; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

COPY tng.links (id, domain_id, range_id, property, attribute, sortorder) FROM stdin;
1	1	22	3	5	1
2	22	19	2	11	2
3	22	21	2	5	3
4	16	22	1	12	4
5	18	22	1	5	5
6	17	22	1	10	6
7	3	19	2	8	7
8	3	24	2	23	8
9	17	3	1	12	9
10	1	3	3	8	10
11	4	19	2	10	11
12	18	4	1	13	12
13	17	4	1	10	13
14	1	4	3	12	14
15	2	19	2	5	15
16	2	19	2	10	16
17	2	19	2	8	17
18	16	2	1	5	18
19	16	2	1	8	19
20	1	2	3	5	20
21	4	20	2	13	21
22	16	20	5	14	22
23	3	24	2	14	23
24	3	24	2	23	24
\.


--
-- Data for Name: maps; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

COPY tng.maps (id, name, display_name, tilestring, sortorder) FROM stdin;
1	OpenStreetMap	Open Street Map	L.tileLayer(\n            "https://tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'});	1
\.


--
-- Data for Name: relationship_labels; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

COPY tng.relationship_labels (id, name, name_inv, domain_type_id, range_type_id) FROM stdin;
1	{"de": "hat Mitglied", "en": "has member"}	{"de": "ist Mitglied von", "en": "is member of"}	1	2
2	{"de": "hat Zugehörigkeit", "en": "has affiliation"}	{"de": "ist Zugehörigkeit von", "en": "is affiliation of"}	2	4
3	{"de": "hat Kernmitglied", "en": "has core member"}	{"de": "ist Kernmitglied von", "en": "is core member of"}	5	2
4	{"de": "hat Kerninstitution", "en": "has core institution"}	{"de": "ist Kerninstitution von", "en": "is core institution of"}	5	4
5	{"de": "hat Institution", "en": "has institution"}	{"de": "ist Institution von", "en": "is institution of"}	1	4
\.


--
-- Data for Name: settings; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

COPY tng.settings (id, index_img, index_map, img_map, greyscale, shown_entities, shown_types, hidden_entities, hidden_types, shown_ids, hidden_ids) FROM stdin;
1	/static/images/index_map_bg/Blank_map_of_Europe_central_network.png	1	map	f	{person,group,artifact,human_remains,acquisition,event,activity,creation,move,production,modification,place,stratigraphic_unit,feature,source,bibliography,external_reference,edition,file}	\N	{group,stratigraphic_unit,source,external_reference}	\N	\N	\N
\.


--
-- Data for Name: types; Type: TABLE DATA; Schema: tng; Owner: openatlas
--

COPY tng.types (id, name) FROM stdin;
1	project
2	person
4	institution
5	main-project
6	language_code
3	attribute
\.


--
-- Name: config_classes_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.config_classes_id_seq', 6, true);


--
-- Name: config_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.config_id_seq', 24, true);


--
-- Name: config_properties_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.config_properties_id_seq', 5, true);


--
-- Name: links_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.links_id_seq', 24, true);


--
-- Name: maps_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.maps_id_seq', 1, true);


--
-- Name: settings_id_seq; Type: SEQUENCE SET; Schema: tng; Owner: openatlas
--

SELECT pg_catalog.setval('tng.settings_id_seq', 1, true);


--
-- Name: types config_classes_pkey; Type: CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.types
    ADD CONSTRAINT config_classes_pkey PRIMARY KEY (id);


--
-- Name: entities config_pkey; Type: CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.entities
    ADD CONSTRAINT config_pkey PRIMARY KEY (id);


--
-- Name: relationship_labels config_properties_pkey; Type: CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.relationship_labels
    ADD CONSTRAINT config_properties_pkey PRIMARY KEY (id);


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
-- Name: config delete_links_trigger; Type: TRIGGER; Schema: tng; Owner: openatlas
--

CREATE TRIGGER delete_links_trigger BEFORE DELETE ON tng.config FOR EACH ROW EXECUTE FUNCTION tng.delete_links_on_config_delete();


--
-- Name: entities delete_links_trigger; Type: TRIGGER; Schema: tng; Owner: openatlas
--

CREATE TRIGGER delete_links_trigger BEFORE DELETE ON tng.entities FOR EACH ROW EXECUTE FUNCTION tng.delete_links_on_config_delete();


--
-- Name: entities config_config_classes_fk; Type: FK CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.entities
    ADD CONSTRAINT config_config_classes_fk FOREIGN KEY (type) REFERENCES tng.types(id);


--
-- Name: relationship_labels relationship_labels_domain_id_fkey; Type: FK CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.relationship_labels
    ADD CONSTRAINT relationship_labels_domain_id_fkey FOREIGN KEY (domain_type_id) REFERENCES tng.types(id) NOT VALID;


--
-- Name: relationship_labels relationship_labels_range_id_fkey; Type: FK CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.relationship_labels
    ADD CONSTRAINT relationship_labels_range_id_fkey FOREIGN KEY (range_type_id) REFERENCES tng.types(id) NOT VALID;


--
-- PostgreSQL database dump complete
--

