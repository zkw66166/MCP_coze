#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户管理路由
提供用户增删改查 API 端点
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from server.services.auth_service import (
    get_all_users,
    create_user,
    update_user,
    delete_user,
    get_user_by_id
)
from server.routers.auth import get_current_user

router = APIRouter()

# 请求/响应模型
class UserCreate(BaseModel):
    username: str
    password: str
    user_type: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[int] = 1

class UserUpdate(BaseModel):
    password: Optional[str] = None
    user_type: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[int] = None

class UserInfo(BaseModel):
    id: int
    username: str
    user_type: str
    display_name: Optional[str]
    email: Optional[str]
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    is_active: int

    class Config:
        orm_mode = True 
        # 这里实际上字典也可以工作，FastAPI足够聪明

@router.get("/users", response_model=List[UserInfo])
async def list_users(current_user: dict = Depends(get_current_user)):
    """获取所有用户列表"""
    # 这里可以添加权限检查，例如只允许管理员访问
    return get_all_users()

@router.post("/users", response_model=UserInfo)
async def create_new_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    """创建新用户"""
    try:
        new_user = create_user(user.dict())
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/users/{user_id}", response_model=UserInfo)
async def update_existing_user(user_id: int, user: UserUpdate, current_user: dict = Depends(get_current_user)):
    """更新用户"""
    existing = get_user_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="用户不存在")
        
    updated = update_user(user_id, user.dict(exclude_unset=True))
    return updated

@router.delete("/users/{user_id}")
async def delete_existing_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """删除用户"""
    # 防止自杀
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail="不能删除当前登录用户")
        
    success = delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"message": "删除成功"}
