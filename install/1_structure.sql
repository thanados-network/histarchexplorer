--
-- PostgreSQL database dump
--

\restrict dz1x6pwX1VIeNm6adxfaL0df5pWoOSmjsqBCWm8Z39H2cKDy3BOcyJdZcwSgrgg

-- Dumped from database version 17.8 (Debian 17.8-0+deb13u1)
-- Dumped by pg_dump version 17.8 (Debian 17.8-0+deb13u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY tng.properties DROP CONSTRAINT IF EXISTS relationship_labels_range_id_fkey;
ALTER TABLE IF EXISTS ONLY tng.properties DROP CONSTRAINT IF EXISTS relationship_labels_domain_id_fkey;
ALTER TABLE IF EXISTS ONLY tng.file_licenses DROP CONSTRAINT IF EXISTS file_licenses_license_id_fkey;
ALTER TABLE IF EXISTS ONLY tng.file_licenses DROP CONSTRAINT IF EXISTS file_licenses_file_id_fkey;
ALTER TABLE IF EXISTS ONLY tng.entities DROP CONSTRAINT IF EXISTS entities_class_id_fkey;
DROP TRIGGER IF EXISTS delete_links_trigger ON tng.entities;
ALTER TABLE IF EXISTS ONLY tng.system_settings DROP CONSTRAINT IF EXISTS system_settings_pkey;
ALTER TABLE IF EXISTS ONLY tng.maps DROP CONSTRAINT IF EXISTS maps_pkey;
ALTER TABLE IF EXISTS ONLY tng.links DROP CONSTRAINT IF EXISTS links_pkey;
ALTER TABLE IF EXISTS ONLY tng.licenses DROP CONSTRAINT IF EXISTS licenses_spdx_id_key;
ALTER TABLE IF EXISTS ONLY tng.licenses DROP CONSTRAINT IF EXISTS licenses_pkey;
ALTER TABLE IF EXISTS ONLY tng.files DROP CONSTRAINT IF EXISTS files_pkey;
ALTER TABLE IF EXISTS ONLY tng.file_licenses DROP CONSTRAINT IF EXISTS file_licenses_pkey;
ALTER TABLE IF EXISTS ONLY tng.entities DROP CONSTRAINT IF EXISTS entities_pkey;
ALTER TABLE IF EXISTS ONLY tng.properties DROP CONSTRAINT IF EXISTS config_properties_pkey;
ALTER TABLE IF EXISTS ONLY tng.classes DROP CONSTRAINT IF EXISTS config_classes_pkey;
ALTER TABLE IF EXISTS tng.maps ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS tng.licenses ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS tng.files ALTER COLUMN id DROP DEFAULT;
DROP TABLE IF EXISTS tng.system_settings;
DROP TABLE IF EXISTS tng.properties;
DROP SEQUENCE IF EXISTS tng.maps_id_seq;
DROP TABLE IF EXISTS tng.maps;
DROP SEQUENCE IF EXISTS tng.links_id_seq;
DROP TABLE IF EXISTS tng.links;
DROP SEQUENCE IF EXISTS tng.licenses_id_seq;
DROP TABLE IF EXISTS tng.licenses;
DROP SEQUENCE IF EXISTS tng.files_id_seq;
DROP TABLE IF EXISTS tng.files;
DROP TABLE IF EXISTS tng.file_licenses;
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
    case_study_type_id integer,
    acronym text,
    license_id integer
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
-- Name: file_licenses; Type: TABLE; Schema: tng; Owner: bkoschicek
--

CREATE TABLE tng.file_licenses (
    license_id integer,
    attribution text,
    file_id integer NOT NULL
);


ALTER TABLE tng.file_licenses OWNER TO bkoschicek;

--
-- Name: files; Type: TABLE; Schema: tng; Owner: bkoschicek
--

CREATE TABLE tng.files (
    id integer NOT NULL,
    type text NOT NULL,
    filename text NOT NULL,
    is_default boolean DEFAULT false,
    is_active boolean DEFAULT true,
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE tng.files OWNER TO bkoschicek;

--
-- Name: files_id_seq; Type: SEQUENCE; Schema: tng; Owner: bkoschicek
--

CREATE SEQUENCE tng.files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tng.files_id_seq OWNER TO bkoschicek;

--
-- Name: files_id_seq; Type: SEQUENCE OWNED BY; Schema: tng; Owner: bkoschicek
--

ALTER SEQUENCE tng.files_id_seq OWNED BY tng.files.id;


--
-- Name: licenses; Type: TABLE; Schema: tng; Owner: bkoschicek
--

CREATE TABLE tng.licenses (
    id integer NOT NULL,
    spdx_id character varying(50) NOT NULL,
    uri character varying(255) NOT NULL,
    label character varying(255) NOT NULL,
    category character varying(20) NOT NULL,
    CONSTRAINT licenses_category_check CHECK (((category)::text = ANY ((ARRAY['LICENSE'::character varying, 'STATEMENT'::character varying])::text[])))
);


ALTER TABLE tng.licenses OWNER TO bkoschicek;

--
-- Name: licenses_id_seq; Type: SEQUENCE; Schema: tng; Owner: bkoschicek
--

CREATE SEQUENCE tng.licenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tng.licenses_id_seq OWNER TO bkoschicek;

--
-- Name: licenses_id_seq; Type: SEQUENCE OWNED BY; Schema: tng; Owner: bkoschicek
--

ALTER SEQUENCE tng.licenses_id_seq OWNED BY tng.licenses.id;


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


ALTER SEQUENCE tng.links_id_seq OWNER TO openatlas;

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


ALTER SEQUENCE tng.maps_id_seq OWNER TO openatlas;

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
-- Name: system_settings; Type: TABLE; Schema: tng; Owner: openatlas
--

CREATE TABLE tng.system_settings (
    key text NOT NULL,
    value jsonb NOT NULL
);


ALTER TABLE tng.system_settings OWNER TO openatlas;

--
-- Name: files id; Type: DEFAULT; Schema: tng; Owner: bkoschicek
--

ALTER TABLE ONLY tng.files ALTER COLUMN id SET DEFAULT nextval('tng.files_id_seq'::regclass);


--
-- Name: licenses id; Type: DEFAULT; Schema: tng; Owner: bkoschicek
--

ALTER TABLE ONLY tng.licenses ALTER COLUMN id SET DEFAULT nextval('tng.licenses_id_seq'::regclass);


--
-- Name: maps id; Type: DEFAULT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.maps ALTER COLUMN id SET DEFAULT nextval('tng.maps_id_seq'::regclass);


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
-- Name: file_licenses file_licenses_pkey; Type: CONSTRAINT; Schema: tng; Owner: bkoschicek
--

ALTER TABLE ONLY tng.file_licenses
    ADD CONSTRAINT file_licenses_pkey PRIMARY KEY (file_id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: tng; Owner: bkoschicek
--

ALTER TABLE ONLY tng.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: licenses licenses_pkey; Type: CONSTRAINT; Schema: tng; Owner: bkoschicek
--

ALTER TABLE ONLY tng.licenses
    ADD CONSTRAINT licenses_pkey PRIMARY KEY (id);


--
-- Name: licenses licenses_spdx_id_key; Type: CONSTRAINT; Schema: tng; Owner: bkoschicek
--

ALTER TABLE ONLY tng.licenses
    ADD CONSTRAINT licenses_spdx_id_key UNIQUE (spdx_id);


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
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: tng; Owner: openatlas
--

ALTER TABLE ONLY tng.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (key);


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
-- Name: file_licenses file_licenses_file_id_fkey; Type: FK CONSTRAINT; Schema: tng; Owner: bkoschicek
--

ALTER TABLE ONLY tng.file_licenses
    ADD CONSTRAINT file_licenses_file_id_fkey FOREIGN KEY (file_id) REFERENCES tng.files(id) ON DELETE CASCADE;


--
-- Name: file_licenses file_licenses_license_id_fkey; Type: FK CONSTRAINT; Schema: tng; Owner: bkoschicek
--

ALTER TABLE ONLY tng.file_licenses
    ADD CONSTRAINT file_licenses_license_id_fkey FOREIGN KEY (license_id) REFERENCES tng.licenses(id) ON DELETE SET NULL;


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
-- Name: COLUMN entities.license_id; Type: ACL; Schema: tng; Owner: openatlas
--

GRANT UPDATE(license_id) ON TABLE tng.entities TO openatlas;


--
-- Name: TABLE file_licenses; Type: ACL; Schema: tng; Owner: bkoschicek
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE tng.file_licenses TO openatlas;


--
-- Name: TABLE files; Type: ACL; Schema: tng; Owner: bkoschicek
--

GRANT ALL ON TABLE tng.files TO openatlas;


--
-- Name: SEQUENCE files_id_seq; Type: ACL; Schema: tng; Owner: bkoschicek
--

GRANT SELECT,USAGE ON SEQUENCE tng.files_id_seq TO openatlas;


--
-- Name: TABLE licenses; Type: ACL; Schema: tng; Owner: bkoschicek
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE tng.licenses TO openatlas;


--
-- Name: SEQUENCE licenses_id_seq; Type: ACL; Schema: tng; Owner: bkoschicek
--

GRANT SELECT,USAGE ON SEQUENCE tng.licenses_id_seq TO openatlas;


--
-- PostgreSQL database dump complete
--

\unrestrict dz1x6pwX1VIeNm6adxfaL0df5pWoOSmjsqBCWm8Z39H2cKDy3BOcyJdZcwSgrgg

