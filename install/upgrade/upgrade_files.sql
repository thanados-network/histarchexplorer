-- Create files table
CREATE TABLE IF NOT EXISTS tng.files (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    filename TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created TIMESTAMP DEFAULT NOW()
);

-- Migrate logos
INSERT INTO tng.files (type, filename, is_default, is_active)
SELECT 'logo', filename, is_default, is_active FROM tng.logos;

-- Update file_licenses to use file_id
ALTER TABLE tng.file_licenses ADD COLUMN file_id INTEGER REFERENCES tng.files(id) ON DELETE CASCADE;

UPDATE tng.file_licenses fl
SET file_id = f.id
FROM tng.files f
WHERE fl.filename = f.filename AND f.type = 'logo';

-- Drop old constraint on filename and add new one on file_id
ALTER TABLE tng.file_licenses DROP CONSTRAINT IF EXISTS file_licenses_filename_key;
ALTER TABLE tng.file_licenses DROP CONSTRAINT IF EXISTS file_licenses_pkey;

-- We keep filename for now as a backup or drop it?
-- If we drop it, we must ensure all licenses have file_id.
-- Any license without file_id (orphan) will be lost or needs to be deleted.
DELETE FROM tng.file_licenses WHERE file_id IS NULL;

ALTER TABLE tng.file_licenses DROP COLUMN filename;
ALTER TABLE tng.file_licenses ADD PRIMARY KEY (file_id);

-- Drop old logos table
DROP TABLE IF EXISTS tng.logos;

GRANT USAGE, SELECT ON SEQUENCE tng.files_id_seq TO openatlas;
ALTER TABLE tng.files_id_seq OWNER TO openatlas;
