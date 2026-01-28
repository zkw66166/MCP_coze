#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证路由
提供登录、登出、获取当前用户等 API 端点
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional

from server.services.auth_service import (
    authenticate_user,
    create_access_token,
    verify_token,
    get_user_by_id
)

router = APIRouter()
security = HTTPBearer()


# 请求/响应模型
class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    user_type: str
    display_name: Optional[str]
    email: Optional[str]


# 依赖项：获取当前用户
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    从 JWT token 中获取当前用户
    用作依赖项注入到需要认证的端点
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录
    
    验证用户名和密码，返回 JWT token
    """
    user = authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建 access token
    access_token = create_access_token(data={"sub": str(user['id'])})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/auth/logout")
async def logout():
    """
    用户登出
    
    由于使用 JWT，登出主要在客户端完成（删除 token）
    此端点主要用于日志记录或其他服务端操作
    """
    return {"message": "登出成功"}


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前登录用户信息
    
    需要在请求头中提供有效的 JWT token
    """
    return current_user
