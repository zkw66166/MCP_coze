
import sqlite3
import os

def run_sql_script(script_path, db_path):
    print(f"Executing {script_path} on {db_path}...")
    
    if not os.path.exists(script_path):
        print(f"Error: Script file not found: {script_path}")
        return
        
    if not os.path.exists(db_path):
        print(f"Error: Database file not found: {db_path}")
        return

    with open(script_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.executescript(sql_script)
        conn.commit()
        print("SQL script executed successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = 'database/financial.db'
    script_path = 'database/redesign_vat.sql'
    run_sql_script(script_path, db_path)
