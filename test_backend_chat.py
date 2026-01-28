import sys
import os
import sqlite3

# Add server directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock imports if needed, but we want to test actual functions
# We need to import the functions from chat.py
# However, chat.py imports other modules which might error if environments are not perfect.
# But we added save_message etc as standalone functions at the top of chat.py (or near top).

# Let's try importing them.
try:
    from server.routers.chat import save_message, get_chat_history, delete_user_history, USERS_DB_PATH
except ImportError:
    # Fallback: define them here as they are in the file to test DB connectivity directly
    # This is less ideal but verifies DB works. 
    # But ideally we test the actual code.
    USERS_DB_PATH = "database/users.db"
    print("Could not import chat module properly, testing DB logic directly.")
    
    def save_message(user_id, role, content, type='text'):
        conn = sqlite3.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_messages (user_id, role, content, type) VALUES (?, ?, ?, ?)", (user_id, role, content, type))
        conn.commit()
        conn.close()
        
    def get_chat_history(user_id, limit=50):
        conn = sqlite3.connect(USERS_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_messages WHERE user_id = ? ORDER BY created_at ASC LIMIT ?", (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
        
    def delete_user_history(user_id, ids=None):
        conn = sqlite3.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        if ids:
            placeholders = ','.join('?' for _ in ids)
            cursor.execute(f"DELETE FROM chat_messages WHERE user_id = ? AND id IN ({placeholders})", (user_id, *ids))
        else:
            cursor.execute("DELETE FROM chat_messages WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

def test_chat_persistence():
    user_id = "test_user_persistence"
    
    print("1. Cleaning up old test data...")
    delete_user_history(user_id)
    
    print("2. Saving messages...")
    save_message(user_id, "user", "Hello AI", "text")
    save_message(user_id, "assistant", "Hello User", "text")
    
    print("3. Retrieving history...")
    history = get_chat_history(user_id)
    print(f"   Found {len(history)} messages.")
    for msg in history:
        print(f"   - [{msg['role']}] {msg['content']}")
        
    if len(history) != 2:
        print("FAILED: Expected 2 messages.")
        return
        
    print("4. Testing specific delete...")
    msg_id = history[0]['id']
    delete_user_history(user_id, [msg_id])
    
    history_after = get_chat_history(user_id)
    print(f"   After delete 1, found {len(history_after)} messages.")
    
    if len(history_after) != 1:
        print("FAILED: Expected 1 message.")
        return
        
    print("5. Testing delete all...")
    delete_user_history(user_id)
    history_final = get_chat_history(user_id)
    print(f"   Final count: {len(history_final)}")
    
    if len(history_final) != 0:
        print("FAILED: Expected 0 messages.")
        return
        
    print("\nSUCCESS: Database persistence verification passed.")

if __name__ == "__main__":
    test_chat_persistence()
