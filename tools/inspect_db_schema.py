import sqlite3

conn = sqlite3.connect('database/financial.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cursor.fetchall()]

print("=" * 60)
print("Tables in financial.db:")
print("=" * 60)
for t in tables:
    if not t.startswith('sqlite_'):
        print(f"\n[{t}]")
        cursor.execute(f"PRAGMA table_info({t})")
        cols = cursor.fetchall()
        for c in cols:
            print(f"  {c[1]:30} ({c[2]})")
        # count rows
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"  --> Total rows: {count}")

conn.close()
