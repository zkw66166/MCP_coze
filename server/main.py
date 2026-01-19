#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
税务智能咨询 API - FastAPI 后端
基于现有 PyQt6 应用的 Web 化版本
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.routers import chat, companies, company_profile, data_management

# 创建 FastAPI 应用
app = FastAPI(
    title="税务智能咨询 API",
    description="支持税收优惠查询、企业财务分析和通用税务咨询",
    version="1.0.0"
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api", tags=["聊天"])
app.include_router(companies.router, prefix="/api", tags=["企业"])
app.include_router(company_profile.router, prefix="/api", tags=["企业画像"])
app.include_router(data_management.router)


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "message": "税务智能咨询 API 正在运行",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """API 健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
