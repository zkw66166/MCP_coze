#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试调度器和手动触发API
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"


def test_scheduler_status():
    """测试调度器状态查询"""
    print("=" * 70)
    print("测试: 查询调度器状态")
    print("=" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/admin/metrics/scheduler-status")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ 调度器状态:")
        print(f"   运行中: {data['is_running']}")
        print(f"   服务器时间: {data['server_time']}")
        print(f"   任务列表:")
        for job in data['jobs']:
            print(f"     - {job['name']}")
            print(f"       下次运行: {job['next_run_time']}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_manual_trigger():
    """测试手动触发计算"""
    print("\n" + "=" * 70)
    print("测试: 手动触发指标计算")
    print("=" * 70)
    
    try:
        # 测试触发全部企业的计算
        payload = {
            "company_ids": None,  # 全部企业
            "year": None  # 所有年份
        }
        
        response = requests.post(
            f"{BASE_URL}/admin/metrics/recalculate",
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ 触发成功:")
        print(f"   状态: {data['status']}")
        print(f"   消息: {data['message']}")
        print(f"   触发时间: {data['triggered_at']}")
        print(f"   计算范围:")
        print(f"     企业: {data['scope']['companies']}")
        print(f"     年份: {data['scope']['year']}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_manual_trigger_specific():
    """测试手动触发指定企业和年份的计算"""
    print("\n" + "=" * 70)
    print("测试: 手动触发指定范围计算")
    print("=" * 70)
    
    try:
        # 测试触发特定企业和年份
        payload = {
            "company_ids": [5],  # 仅企业ID=5
            "year": 2025  # 仅2025年
        }
        
        response = requests.post(
            f"{BASE_URL}/admin/metrics/recalculate",
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ 触发成功:")
        print(f"   状态: {data['status']}")
        print(f"   消息: {data['message']}")
        print(f"   计算范围:")
        print(f"     企业: {data['scope']['companies']}")
        print(f"     年份: {data['scope']['year']}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    print("🚀 开始测试企业画像指标管理API")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   服务器: {BASE_URL}\n")
    
    # 确保服务器正在运行
    try:
        requests.get("http://localhost:8000/api/health", timeout=2)
    except requests.exceptions.RequestException:
        print("❌ 错误: FastAPI服务器未运行")
        print("   请先启动服务器: python server/main.py")
        exit(1)
    
    # 执行测试
    results = []
    results.append(("调度器状态查询", test_scheduler_status()))
    results.append(("手动触发全量计算", test_manual_trigger()))
    results.append(("手动触发指定计算", test_manual_trigger_specific()))
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status}  {test_name}")
    
    success_count = sum(1 for _, passed in results if passed)
    print(f"\n总计: {success_count}/{len(results)} 项测试通过")
    
    if success_count == len(results):
        print("\n🎉 所有测试通过!")
    else:
        print("\n⚠️ 部分测试失败，请检查日志")
