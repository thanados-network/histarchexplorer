-- Upgrade Script for Licenses Feature

-- 1. Create the licenses table if it doesn't exist
CREATE TABLE IF NOT EXISTS tng.licenses (
    id SERIAL PRIMARY KEY,
    spdx_id VARCHAR(50) UNIQUE NOT NULL,
    uri VARCHAR(255) NOT NULL,
    label VARCHAR(255) NOT NULL,
    category VARCHAR(20) NOT NULL CHECK (category IN ('LICENSE', 'STATEMENT'))
);

-- 2. Create or update the file_licenses table
CREATE TABLE IF NOT EXISTS tng.file_licenses (
    filename VARCHAR(255) PRIMARY KEY,
    license_id INTEGER REFERENCES tng.licenses(id) ON DELETE SET NULL,
    attribution TEXT
);
ALTER TABLE tng.file_licenses ADD COLUMN IF NOT EXISTS attribution TEXT;


-- 3. Add license_id column to the entities table if it doesn't exist
ALTER TABLE tng.entities
ADD COLUMN IF NOT EXISTS license_id INTEGER REFERENCES tng.licenses(id) ON DELETE SET NULL;

-- 4. Pre-populate with standard Creative Commons licenses
-- Using ON CONFLICT to prevent errors if the script is run multiple times
INSERT INTO tng.licenses (spdx_id, uri, label, category) VALUES
('CC-BY-4.0', 'https://creativecommons.org/licenses/by/4.0/', 'CC BY 4.0', 'LICENSE'),
('CC-BY-SA-4.0', 'https://creativecommons.org/licenses/by-sa/4.0/', 'CC BY-SA 4.0', 'LICENSE'),
('CC-BY-ND-4.0', 'https://creativecommons.org/licenses/by-nd/4.0/', 'CC BY-ND 4.0', 'LICENSE'),
('CC-BY-NC-4.0', 'https://creativecommons.org/licenses/by-nc/4.0/', 'CC BY-NC 4.0', 'LICENSE'),
('CC-BY-NC-SA-4.0', 'https://creativecommons.org/licenses/by-nc-sa/4.0/', 'CC BY-NC-SA 4.0', 'LICENSE'),
('CC-BY-NC-ND-4.0', 'https://creativecommons.org/licenses/by-nc-nd/4.0/', 'CC BY-NC-ND 4.0', 'LICENSE'),
('CC0-1.0', 'https://creativecommons.org/publicdomain/zero/1.0/', 'CC0 1.0', 'LICENSE')
ON CONFLICT (spdx_id) DO UPDATE SET label = EXCLUDED.label;

-- 5. Pre-populate with standard Rights Statements
INSERT INTO tng.licenses (spdx_id, uri, label, category) VALUES
('InC', 'http://rightsstatements.org/vocab/InC/1.0/', 'In Copyright', 'STATEMENT'),
('InC-NC', 'http://rightsstatements.org/vocab/InC-NC/1.0/', 'In Copyright - NC', 'STATEMENT'),
('InC-EDU', 'http://rightsstatements.org/vocab/InC-EDU/1.0/', 'In Copyright - EDU', 'STATEMENT'),
('NoC-NC', 'http://rightsstatements.org/vocab/NoC-NC/1.0/', 'No Copyright - NC', 'STATEMENT'),
('CNE', 'http://rightsstatements.org/vocab/CNE/1.0/', 'Copyright Not Evaluated', 'STATEMENT')
ON CONFLICT (spdx_id) DO UPDATE SET label = EXCLUDED.label;

-- 6. Grant permissions to the openatlas user
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE tng.licenses TO openatlas;
GRANT USAGE, SELECT ON SEQUENCE tng.licenses_id_seq TO openatlas;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE tng.file_licenses TO openatlas;
GRANT UPDATE(license_id) ON TABLE tng.entities TO openatlas;


-- Notify user
SELECT 'Upgrade script for licenses completed successfully.';
