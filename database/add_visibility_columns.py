#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Migration script to add visibility flags to chat_messages table.
This enables separate management of sidebar history vs chat messages.
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_DB_PATH = os.path.join(BASE_DIR, "database", "users.db")

def migrate():
    print(f"Connecting to {USERS_DB_PATH}")
    conn = sqlite3.connect(USERS_DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(chat_messages)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'visible_in_history' not in columns:
        print("Adding column: visible_in_history")
        cursor.execute("ALTER TABLE chat_messages ADD COLUMN visible_in_history INTEGER DEFAULT 1")
    else:
        print("Column visible_in_history already exists")
    
    if 'visible_in_chat' not in columns:
        print("Adding column: visible_in_chat")
        cursor.execute("ALTER TABLE chat_messages ADD COLUMN visible_in_chat INTEGER DEFAULT 1")
    else:
        print("Column visible_in_chat already exists")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
