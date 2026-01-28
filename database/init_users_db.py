#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化用户数据库
创建 users.db 并插入测试用户数据
"""

import sqlite3
import os
from pathlib import Path
import bcrypt

# 数据库路径
DB_DIR = Path(__file__).parent
DB_PATH = DB_DIR / "users.db"


def hash_password(password: str) -> str:
    """使用 bcrypt 加密密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def init_database():
    """初始化数据库和表结构"""
    print(f"📁 数据库路径: {DB_PATH}")
    
    # 如果数据库已存在，先删除
    if DB_PATH.exists():
        print("⚠️  数据库已存在，将被覆盖...")
        DB_PATH.unlink()
    
    # 创建数据库连接
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK(user_type IN ('enterprise', 'accounting', 'group')),
            display_name TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    print("✅ 用户表创建成功")
    
    # 插入测试用户
    test_users = [
        {
            'username': 'enterprise',
            'password': '123456',
            'user_type': 'enterprise',
            'display_name': '企业用户',
            'email': 'enterprise@example.com'
        },
        {
            'username': 'accounting',
            'password': '123456',
            'user_type': 'accounting',
            'display_name': '事务所用户',
            'email': 'accounting@example.com'
        },
        {
            'username': 'group',
            'password': '123456',
            'user_type': 'group',
            'display_name': '集团用户',
            'email': 'group@example.com'
        }
    ]
    
    for user in test_users:
        password_hash = hash_password(user['password'])
        cursor.execute("""
            INSERT INTO users (username, password_hash, user_type, display_name, email)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user['username'],
            password_hash,
            user['user_type'],
            user['display_name'],
            user['email']
        ))
        print(f"✅ 创建测试用户: {user['username']} ({user['display_name']})")
    
    conn.commit()
    
    # 验证数据
    cursor.execute("SELECT id, username, user_type, display_name FROM users")
    users = cursor.fetchall()
    
    print("\n📊 数据库中的用户:")
    print("-" * 60)
    for user in users:
        print(f"ID: {user[0]}, 用户名: {user[1]}, 类型: {user[2]}, 显示名: {user[3]}")
    print("-" * 60)
    
    conn.close()
    print(f"\n✅ 数据库初始化完成: {DB_PATH}")


if __name__ == "__main__":
    init_database()
