import sqlite3

conn = sqlite3.connect('d:/MyProjects/MCP_coze/database/users.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM chat_messages WHERE user_id = '123' ORDER BY created_at DESC LIMIT 10")
rows = cursor.fetchall()
print(f"Found {len(rows)} messages for user_id='123':")
for row in rows:
    print(row)
conn.close()
