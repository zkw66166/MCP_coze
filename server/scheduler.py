#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业画像指标定时计算调度器
使用 APScheduler 实现每日自动计算
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import sys
import os

# 确保可以导入项目模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 延迟导入，避免循环依赖
def get_calculate_all_metrics():
    """延迟导入calculate_all_metrics"""
    from database.calculate_metrics import calculate_all_metrics
    return calculate_all_metrics

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsScheduler:
    """企业画像指标计算调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(
            timezone='Asia/Shanghai',
            job_defaults={
                'coalesce': True,  # 合并多个堆积的任务
                'max_instances': 1,  # 同一时间只允许一个实例运行
            }
        )
        self._is_running = False
    
    def daily_calculation_job(self):
        """每日定时计算任务"""
        try:
            logger.info("=" * 60)
            logger.info("开始执行定时计算任务")
            logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            # 执行计算（延迟导入）
            calculate_all_metrics = get_calculate_all_metrics()
            calculate_all_metrics()
            
            logger.info("=" * 60)
            logger.info("✅ 定时计算任务完成")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ 定时计算任务失败: {e}", exc_info=True)
    
    def start(self):
        """启动调度器"""
        if self._is_running:
            logger.warning("调度器已在运行中")
            return
        
        try:
            # 添加每日凌晨2点的定时任务
            self.scheduler.add_job(
                func=self.daily_calculation_job,
                trigger=CronTrigger(hour=2, minute=0),
                id='daily_metrics_calculation',
                name='每日企业画像指标计算',
                replace_existing=True
            )
            
            # 启动调度器
            self.scheduler.start()
            self._is_running = True
            
            logger.info("✅ 企业画像指标调度器已启动")
            logger.info("   定时任务: 每日 02:00 执行")
            
            # 显示下次执行时间
            next_run = self.scheduler.get_job('daily_metrics_calculation').next_run_time
            logger.info(f"   下次执行: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"❌ 调度器启动失败: {e}", exc_info=True)
            raise
    
    def stop(self):
        """停止调度器"""
        if not self._is_running:
            logger.warning("调度器未运行")
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self._is_running = False
            logger.info("✅ 企业画像指标调度器已停止")
        except Exception as e:
            logger.error(f"❌ 调度器停止失败: {e}", exc_info=True)
            raise
    
    def trigger_manual_calculation(self, company_ids=None, year=None):
        """
        手动触发计算
        
        Args:
            company_ids: 企业ID列表，None表示全部企业
            year: 年份，None表示所有年份
        """
        try:
            logger.info("=" * 60)
            logger.info("手动触发计算任务")
            logger.info(f"企业范围: {company_ids if company_ids else '全部'}")
            logger.info(f"年份范围: {year if year else '所有年份'}")
            logger.info("=" * 60)
            
            # 目前 calculate_all_metrics 不支持参数过滤
            # TODO: 后续可扩展 calculate_metrics.py 支持参数化计算
            calculate_all_metrics = get_calculate_all_metrics()
            calculate_all_metrics()
            
            logger.info("✅ 手动计算任务完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 手动计算任务失败: {e}", exc_info=True)
            return False
    
    @property
    def is_running(self):
        """调度器是否运行中"""
        return self._is_running
    
    def get_job_info(self):
        """获取任务信息"""
        jobs = self.scheduler.get_jobs()
        return [{
            'id': job.id,
            'name': job.name,
            'next_run_time': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None,
            'trigger': str(job.trigger)
        } for job in jobs]


# 全局调度器实例
_scheduler_instance = None


def get_scheduler():
    """获取全局调度器实例（单例模式）"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = MetricsScheduler()
    return _scheduler_instance


def start_scheduler():
    """启动调度器（供外部调用）"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler


def stop_scheduler():
    """停止调度器（供外部调用）"""
    scheduler = get_scheduler()
    scheduler.stop()


if __name__ == "__main__":
    # 测试运行
    print("测试调度器启动...")
    scheduler = get_scheduler()
    scheduler.start()
    
    print("\n调度器信息:")
    for job in scheduler.get_job_info():
        print(f"  任务: {job['name']}")
        print(f"  下次运行: {job['next_run_time']}")
    
    print("\n按 Ctrl+C 停止...")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止调度器...")
        scheduler.stop()
        print("已退出")
