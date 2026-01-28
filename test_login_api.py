#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试登录 API
验证认证功能是否正常工作
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """测试登录功能"""
    print("=" * 60)
    print("测试登录 API")
    print("=" * 60)
    
    # 测试用户
    test_users = [
        {"username": "enterprise", "password": "123456", "type": "企业用户"},
        {"username": "accounting", "password": "123456", "type": "事务所用户"},
        {"username": "group", "password": "123456", "type": "集团用户"},
    ]
    
    for user in test_users:
        print(f"\n测试 {user['type']} 登录...")
        
        # 登录请求
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": user["username"], "password": user["password"]}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 登录成功")
            print(f"   Token: {data['access_token'][:50]}...")
            print(f"   用户信息: {json.dumps(data['user'], ensure_ascii=False, indent=2)}")
            
            # 测试获取当前用户信息
            token = data['access_token']
            me_response = requests.get(
                f"{BASE_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if me_response.status_code == 200:
                me_data = me_response.json()
                print(f"✅ 获取用户信息成功: {json.dumps(me_data, ensure_ascii=False)}")
            else:
                print(f"❌ 获取用户信息失败: {me_response.status_code}")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   错误: {response.text}")
    
    # 测试错误密码
    print(f"\n测试错误密码...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "enterprise", "password": "wrongpassword"}
    )
    
    if response.status_code == 401:
        print(f"✅ 正确拒绝错误密码")
    else:
        print(f"❌ 应该返回 401，实际返回: {response.status_code}")
    
    # 测试不存在的用户
    print(f"\n测试不存在的用户...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "nonexistent", "password": "123456"}
    )
    
    if response.status_code == 401:
        print(f"✅ 正确拒绝不存在的用户")
    else:
        print(f"❌ 应该返回 401，实际返回: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_login()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
        print("   运行命令: python -m uvicorn server.main:app --reload")
