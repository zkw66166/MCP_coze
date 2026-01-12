#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业相关 API
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException
from typing import List
import sqlite3

router = APIRouter()

# 数据库路径
DB_PATH = "database/financial.db"
TAX_DB_PATH = "database/tax_incentives.db"


@router.get("/companies")
async def list_companies() -> List[dict]:
    """
    获取所有企业列表
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM companies ORDER BY id")
        companies = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        conn.close()
        return companies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取企业列表失败: {str(e)}")


@router.get("/companies/{company_id}")
async def get_company(company_id: int) -> dict:
    """
    获取单个企业详情
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM companies WHERE id = ?", (company_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"企业 ID {company_id} 不存在")
        
        return {"id": row[0], "name": row[1]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取企业详情失败: {str(e)}")


@router.get("/statistics")
async def get_statistics() -> dict:
    """
    获取数据库统计信息
    """
    stats = {
        "companies": 0,
        "tax_policies": 0,
        "financial_records": 0
    }
    
    try:
        # 统计企业数量
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM companies")
        stats["companies"] = cursor.fetchone()[0]
        
        # 统计财务记录数量
        cursor.execute("SELECT COUNT(*) FROM financial_metrics")
        stats["financial_records"] = cursor.fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"财务数据库统计失败: {e}")
    
    try:
        # 统计税收优惠政策数量
        conn = sqlite3.connect(TAX_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tax_incentives")
        stats["tax_policies"] = cursor.fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"税收政策数据库统计失败: {e}")
    
    return stats
