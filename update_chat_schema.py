import sqlite3
import os

DB_PATH = 'database/users.db'

def update_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_messages'")
    if cursor.fetchone():
        print("Table 'chat_messages' already exists.")
    else:
        print("Creating table 'chat_messages'...")
        cursor.execute('''
            CREATE TABLE chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL, -- 'user' or 'assistant'
                content TEXT NOT NULL,
                type TEXT DEFAULT 'text', -- 'text', 'chart', 'summary'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Add index for faster queries by user
        cursor.execute("CREATE INDEX idx_chat_user_id ON chat_messages(user_id)")
        print("Table created successfully.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    update_schema()
