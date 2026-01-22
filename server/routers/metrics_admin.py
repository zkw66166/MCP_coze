#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业画像指标管理 API
提供手动触发计算、查看任务状态等功能
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from server.scheduler import get_scheduler

router = APIRouter()
logger = logging.getLogger(__name__)


# =============================================================================
# 数据模型
# =============================================================================

class TriggerCalculationRequest(BaseModel):
    """手动触发计算请求"""
    company_ids: Optional[List[int]] = None  # 企业ID列表，None表示全部
    year: Optional[int] = None  # 年份，None表示所有年份


class CalculationResponse(BaseModel):
    """计算响应"""
    status: str
    message: str
    triggered_at: str
    scope: Dict[str, Any]


class SchedulerStatusResponse(BaseModel):
    """调度器状态响应"""
    is_running: bool
    jobs: List[Dict[str, Any]]
    server_time: str


# =============================================================================
# API 端点
# =============================================================================

@router.post("/admin/metrics/recalculate", response_model=CalculationResponse)
async def trigger_recalculate(
    request: TriggerCalculationRequest,
    background_tasks: BackgroundTasks
):
    """
    手动触发企业画像指标重新计算
    
    - **company_ids**: 指定企业ID列表，为空则计算全部企业
    - **year**: 指定年份，为空则计算所有年份
    
    计算任务将在后台异步执行，不会阻塞API响应
    """
    try:
        scheduler = get_scheduler()
        
        # 在后台异步执行计算
        background_tasks.add_task(
            scheduler.trigger_manual_calculation,
            company_ids=request.company_ids,
            year=request.year
        )
        
        logger.info(f"手动触发计算任务: companies={request.company_ids}, year={request.year}")
        
        return CalculationResponse(
            status="success",
            message="指标计算任务已在后台启动，预计2-5分钟后完成",
            triggered_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            scope={
                "companies": request.company_ids or "全部企业",
                "year": request.year or "所有年份"
            }
        )
    
    except Exception as e:
        logger.error(f"触发计算任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"触发计算任务失败: {str(e)}")


@router.get("/admin/metrics/scheduler-status", response_model=SchedulerStatusResponse)
async def get_scheduler_status():
    """
    获取调度器状态
    
    返回调度器是否运行中、当前任务列表及下次执行时间
    """
    try:
        scheduler = get_scheduler()
        
        return SchedulerStatusResponse(
            is_running=scheduler.is_running,
            jobs=scheduler.get_job_info(),
            server_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    except Exception as e:
        logger.error(f"获取调度器状态失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取调度器状态失败: {str(e)}")


@router.post("/admin/metrics/start-scheduler")
async def start_scheduler_endpoint():
    """
    启动调度器
    
    手动启动定时计算调度器（通常在应用启动时自动执行）
    """
    try:
        scheduler = get_scheduler()
        
        if scheduler.is_running:
            return {
                "status": "already_running",
                "message": "调度器已在运行中"
            }
        
        scheduler.start()
        
        return {
            "status": "success",
            "message": "调度器已启动",
            "jobs": scheduler.get_job_info()
        }
    
    except Exception as e:
        logger.error(f"启动调度器失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"启动调度器失败: {str(e)}")


@router.post("/admin/metrics/stop-scheduler")
async def stop_scheduler_endpoint():
    """
    停止调度器
    
    手动停止定时计算调度器
    """
    try:
        scheduler = get_scheduler()
        
        if not scheduler.is_running:
            return {
                "status": "already_stopped",
                "message": "调度器未运行"
            }
        
        scheduler.stop()
        
        return {
            "status": "success",
            "message": "调度器已停止"
        }
    
    except Exception as e:
        logger.error(f"停止调度器失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"停止调度器失败: {str(e)}")
