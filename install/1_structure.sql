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

