import sqlite3
import os

DB_PATH = 'database/tax_incentives.db'

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    print(f"📦 Migrating database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column already exists (idempotency)
        cursor.execute("PRAGMA table_info(tax_incentives)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'incentive_items' in columns:
            print("⚠️  Column 'incentive_items' already exists. Skipping rename.")
        elif 'project_name' in columns:
            print("🔄 Renaming column 'project_name' to 'incentive_items'...")
            cursor.execute("ALTER TABLE tax_incentives RENAME COLUMN project_name TO incentive_items")
        else:
            print("❌ Column 'project_name' not found!")
            return

        # Recreate FTS table and triggers
        print("🔄 Recreating FTS table and triggers...")
        
        # Drop old FTS and triggers
        cursor.execute("DROP TABLE IF EXISTS tax_incentives_fts")
        cursor.execute("DROP TRIGGER IF EXISTS tax_incentives_ai")
        cursor.execute("DROP TRIGGER IF EXISTS tax_incentives_ad")
        cursor.execute("DROP TRIGGER IF EXISTS tax_incentives_au")

        # Create new FTS table
        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS tax_incentives_fts USING fts5(
            tax_type,
            incentive_items,
            qualification,
            detailed_rules,
            legal_basis,
            explanation,
            keywords,
            content='tax_incentives',
            content_rowid='id'
        )
        """)

        # Populate FTS table
        print("🔄 Populating FTS table...")
        cursor.execute("""
        INSERT INTO tax_incentives_fts(rowid, tax_type, incentive_items, qualification, detailed_rules, legal_basis, explanation, keywords)
        SELECT id, tax_type, incentive_items, qualification, detailed_rules, legal_basis, explanation, keywords FROM tax_incentives
        """)

        # Recreate triggers
        print("🔄 Creating new triggers...")
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS tax_incentives_ai AFTER INSERT ON tax_incentives BEGIN
            INSERT INTO tax_incentives_fts(rowid, tax_type, incentive_items, qualification, detailed_rules, legal_basis, explanation, keywords)
            VALUES (new.id, new.tax_type, new.incentive_items, new.qualification, new.detailed_rules, new.legal_basis, new.explanation, new.keywords);
        END
        """)

        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS tax_incentives_ad AFTER DELETE ON tax_incentives BEGIN
            DELETE FROM tax_incentives_fts WHERE rowid = old.id;
        END
        """)

        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS tax_incentives_au AFTER UPDATE ON tax_incentives BEGIN
            DELETE FROM tax_incentives_fts WHERE rowid = old.id;
            INSERT INTO tax_incentives_fts(rowid, tax_type, incentive_items, qualification, detailed_rules, legal_basis, explanation, keywords)
            VALUES (new.id, new.tax_type, new.incentive_items, new.qualification, new.detailed_rules, new.legal_basis, new.explanation, new.keywords);
        END
        """)

        conn.commit()
        print("✅ Migration completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
