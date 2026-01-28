#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务模块
提供用户认证、密码验证、JWT token 生成和验证功能
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path

import bcrypt
from jose import JWTError, jwt

# JWT 配置
SECRET_KEY = "your-secret-key-change-in-production-2024"  # 生产环境应使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

# 数据库路径
DB_PATH = Path(__file__).parent.parent.parent / "database" / "users.db"


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
    return conn


def hash_password(password: str) -> str:
    """
    使用 bcrypt 加密密码
    
    Args:
        password: 明文密码
        
    Returns:
        加密后的密码哈希
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    验证密码是否正确
    
    Args:
        password: 明文密码
        password_hash: 存储的密码哈希
        
    Returns:
        密码是否匹配
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT access token
    
    Args:
        data: 要编码到 token 中的数据
        expires_delta: token 过期时间，默认为 ACCESS_TOKEN_EXPIRE_MINUTES
        
    Returns:
        JWT token 字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """
    验证 JWT token 并返回解码后的数据
    
    Args:
        token: JWT token 字符串
        
    Returns:
        解码后的 token 数据，如果验证失败返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    验证用户凭据
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        用户信息字典（不包含密码），如果验证失败返回 None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 查询用户
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )
        user = cursor.fetchone()
        
        if not user:
            return None
        
        # 验证密码
        if not verify_password(password, user['password_hash']):
            return None
        
        # 更新最后登录时间
        cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user['id'],)
        )
        conn.commit()
        
        # 返回用户信息（不包含密码）
        return {
            'id': user['id'],
            'username': user['username'],
            'user_type': user['user_type'],
            'display_name': user['display_name'],
            'email': user['email']
        }
        
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """
    根据用户 ID 获取用户信息
    
    Args:
        user_id: 用户 ID
        
    Returns:
        用户信息字典（不包含密码），如果用户不存在返回 None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM users WHERE id = ? AND is_active = 1",
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            return None
        
        return {
            'id': user['id'],
            'username': user['username'],
            'user_type': user['user_type'],
            'display_name': user['display_name'],
            'email': user['email']
        }
        
    finally:
        conn.close()

def get_all_users() -> list:
    """获取所有用户列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, user_type, display_name, email, created_at, last_login, is_active FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        return [dict(user) for user in users]
    finally:
        conn.close()


def create_user(user_data: dict) -> dict:
    """创建新用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        password_hash = hash_password(user_data['password'])
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, user_type, display_name, email, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_data['username'],
                password_hash,
                user_data['user_type'],
                user_data.get('display_name', user_data['username']),
                user_data.get('email'),
                user_data.get('is_active', 1)
            )
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        # 获取新创建的用户
        cursor.execute(
            "SELECT id, username, user_type, display_name, email, created_at, last_login, is_active FROM users WHERE id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        return dict(user)
    except sqlite3.IntegrityError:
        raise ValueError("用户名已存在")
    finally:
        conn.close()


def update_user(user_id: int, user_data: dict) -> dict:
    """更新用户信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        fields = []
        values = []
        
        if 'password' in user_data and user_data['password']:
            fields.append("password_hash = ?")
            values.append(hash_password(user_data['password']))
            
        if 'display_name' in user_data:
            fields.append("display_name = ?")
            values.append(user_data['display_name'])
            
        if 'user_type' in user_data:
            fields.append("user_type = ?")
            values.append(user_data['user_type'])
            
        if 'email' in user_data:
            fields.append("email = ?")
            values.append(user_data['email'])
            
        if 'is_active' in user_data:
            fields.append("is_active = ?")
            values.append(user_data['is_active'])
            
        if not fields:
            return get_user_by_id(user_id)
            
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        values.append(user_id)
        
        cursor.execute(query, tuple(values))
        conn.commit()
        
        return get_user_by_id(user_id)
    finally:
        conn.close()


def delete_user(user_id: int) -> bool:
    """删除用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
