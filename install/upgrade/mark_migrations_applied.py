import sys
from pathlib import Path

# Da das Skript in install/upgrade/ liegt, gehen wir drei Ebenen nach oben ins Projekt-Root
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import psycopg2

def main() -> None:
    from histarchexplorer import app

    conn = psycopg2.connect(
        dbname=app.config['DATABASE_NAME'],
        user=app.config['DATABASE_USER'],
        password=app.config['DATABASE_PASS'],
        host=app.config['DATABASE_HOST'],
        port=app.config['DATABASE_PORT']
    )

    # We want to just create the migrations table and insert the pending versions.
    try:
        with conn:
            with conn.cursor() as cursor:
                # Ensure the table exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tng.schema_migrations (
                        version VARCHAR(50) PRIMARY KEY,
                        applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)

                # Mark versions 0.1.0 to 0.5.0 as applied
                versions = ['0.1.0', '0.2.0', '0.3.0', '0.4.0', '0.5.0']
                for v in versions:
                    cursor.execute("""
                        INSERT INTO tng.schema_migrations (version)
                        VALUES (%s)
                        ON CONFLICT (version) DO NOTHING;
                    """, (v,))
                    print(f"Marked {v} as applied.")

        print("Done. You should no longer see 'Database upgrade required!'.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
