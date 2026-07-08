-- Create files table
CREATE TABLE IF NOT EXISTS tng.files (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    filename TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created TIMESTAMP DEFAULT NOW()
);

-- Migrate logos only if logos table exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'tng' AND table_name = 'logos') THEN
        INSERT INTO tng.files (type, filename, is_default, is_active)
        SELECT 'logo', filename, is_default, is_active FROM tng.logos
        ON CONFLICT DO NOTHING;
    END IF;
END $$;

-- Update file_licenses to use file_id
ALTER TABLE tng.file_licenses ADD COLUMN IF NOT EXISTS file_id INTEGER REFERENCES tng.files(id) ON DELETE CASCADE;

-- Perform the update only if filename column still exists in file_licenses
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.columns WHERE table_schema = 'tng' AND table_name = 'file_licenses' AND column_name = 'filename') THEN
        UPDATE tng.file_licenses fl
        SET file_id = f.id
        FROM tng.files f
        WHERE fl.filename = f.filename AND f.type = 'logo' AND fl.file_id IS NULL;
    END IF;
END $$;

-- Drop old constraints and add new PK on file_id
DO $$
BEGIN
    -- Drop PK if it's on filename
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints tc 
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name 
        WHERE tc.table_schema = 'tng' AND tc.table_name = 'file_licenses' 
        AND tc.constraint_type = 'PRIMARY KEY' AND kcu.column_name = 'filename'
    ) THEN
        ALTER TABLE tng.file_licenses DROP CONSTRAINT file_licenses_pkey;
    END IF;

    ALTER TABLE tng.file_licenses DROP CONSTRAINT IF EXISTS file_licenses_filename_key;
    
    -- Ensure filename column exists before trying to drop it
    IF EXISTS (SELECT FROM information_schema.columns WHERE table_schema = 'tng' AND table_name = 'file_licenses' AND column_name = 'filename') THEN
        DELETE FROM tng.file_licenses WHERE file_id IS NULL;
        ALTER TABLE tng.file_licenses DROP COLUMN filename;
    END IF;

    -- Add PK on file_id if not already there
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints tc 
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name 
        WHERE tc.table_schema = 'tng' AND tc.table_name = 'file_licenses' 
        AND tc.constraint_type = 'PRIMARY KEY' AND kcu.column_name = 'file_id'
    ) THEN
        ALTER TABLE tng.file_licenses ADD PRIMARY KEY (file_id);
    END IF;
END $$;

-- Drop old logos table
DROP TABLE IF EXISTS tng.logos;

-- Sequence permissions
GRANT USAGE, SELECT ON SEQUENCE tng.files_id_seq TO openatlas;
ALTER TABLE tng.files_id_seq OWNER TO openatlas;
