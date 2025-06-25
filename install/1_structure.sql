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

ALTER TABLE IF EXISTS ONLY tng.relationship_labels DROP CONSTRAINT IF EXISTS relationship_labels_range_id_fkey;
ALTER TABLE IF EXISTS ONLY tng.relationship_labels DROP CONSTRAINT IF EXISTS relationship_labels_domain_id_fkey;
ALTER TABLE IF EXISTS ONLY tng.entities DROP CONSTRAINT IF EXISTS config_config_classes_fk;
DROP TRIGGER IF EXISTS delete_links_trigger ON tng.entities;
DROP TRIGGER IF EXISTS delete_links_trigger ON tng.config;
ALTER TABLE IF EXISTS ONLY tng.settings DROP CONSTRAINT IF EXISTS settings_pkey;
ALTER TABLE IF EXISTS ONLY tng.maps DROP CONSTRAINT IF EXISTS maps_pkey;
ALTER TABLE IF EXISTS ONLY tng.links DROP CONSTRAINT IF EXISTS links_pkey;
ALTER TABLE IF EXISTS ONLY tng.relationship_labels DROP CONSTRAINT IF EXISTS config_properties_pkey;
ALTER TABLE IF EXISTS ONLY tng.entities DROP CONSTRAINT IF EXISTS config_pkey;
ALTER TABLE IF EXISTS ONLY tng.types DROP CONSTRAINT IF EXISTS config_classes_pkey;
ALTER TABLE IF EXISTS tng.settings ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS tng.maps ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS tng.links ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS tng.config_properties ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS tng.config_classes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS tng.config ALTER COLUMN id DROP DEFAULT;
DROP TABLE IF EXISTS tng.types;
DROP SEQUENCE IF EXISTS tng.settings_id_seq;
DROP TABLE IF EXISTS tng.settings;
DROP TABLE IF EXISTS tng.relationship_labels;
DROP SEQUENCE IF EXISTS tng.maps_id_seq;
DROP TABLE IF EXISTS tng.maps;
DROP SEQUENCE IF EXISTS tng.links_id_seq;
DROP TABLE IF EXISTS tng.links;
DROP TABLE IF EXISTS tng.entities;
DROP SEQUENCE IF EXISTS tng.config_properties_id_seq;
DROP TABLE IF EXISTS tng.config_properties;
DROP SEQUENCE IF EXISTS tng.config_id_seq;
DROP SEQUENCE IF EXISTS tng.config_classes_id_seq;
DROP TABLE IF EXISTS tng.config_classes;
DROP TABLE IF EXISTS tng.config;
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

