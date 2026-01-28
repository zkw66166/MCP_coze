#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
聊天对话 API - 支持 SSE 流式输出
"""

import sys
import os
import json
import time
import asyncio
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import sqlite3
from datetime import datetime


from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator

# 导入现有模块
from modules.intent_classifier import IntentClassifier
from modules.db_query import TaxIncentiveQuery
from modules.deepseek_client import DeepSeekClient
from modules.financial_query import FinancialQuery

# 认证依赖项
from server.routers.auth import get_current_user

router = APIRouter()

# Coze API 配置（从原 coze_chat.py 迁移）
PAT_TOKEN = "pat_6IkhWiD17bW1qZmXHzeKPPU2YZzBQG8OlqyUyUSXlEFIGBPfOYlTsPK5VHjUSPz8"
BOT_ID = "7592905400907989034"
USER_ID = "123"

# 全局模块实例（延迟初始化）
_classifier = None
_db_query = None
_deepseek = None
_financial_query = None

# 数据库路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
USERS_DB_PATH = os.path.join(BASE_DIR, "database", "users.db")
FINANCIAL_DB_PATH = os.path.join(BASE_DIR, "database", "financial.db")

def save_message(user_id: str, role: str, content: str, type: str = 'text'):
    """保存消息到数据库"""
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_messages (user_id, role, content, type) VALUES (?, ?, ?, ?)",
            (user_id, role, content, type)
        )
        conn.commit()
    except Exception as e:
        print(f"Error saving message: {e}")
    finally:
        if conn:
            conn.close()

def get_chat_history(user_id: str, limit: int = 50):
    """获取聊天历史 (主窗口消息，过滤已删除的)"""
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM chat_messages WHERE user_id = ? AND visible_in_chat = 1 ORDER BY created_at ASC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting history: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_history_items(user_id: str, limit: int = 50):
    """获取历史记录列表 (侧边栏，过滤已删除的)"""
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT content FROM chat_messages WHERE user_id = ? AND role = 'user' AND visible_in_history = 1 ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        return [row['content'] for row in rows]
    except Exception as e:
        print(f"Error getting history items: {e}")
        return []
    finally:
        if conn:
            conn.close()

def delete_user_history(user_id: str, message_ids: Optional[list] = None, target: str = "chat"):
    """删除聊天历史 (软删除)
    
    Args:
        user_id: 用户ID
        message_ids: 要删除的消息ID列表，为空则删除全部
        target: "chat" 删除主窗口消息, "history" 删除侧边栏历史记录
    """
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        
        # 确定要更新的字段
        if target == "history":
            visibility_column = "visible_in_history"
        else:
            visibility_column = "visible_in_chat"
        
        if message_ids:
            # Soft delete specific messages
            placeholders = ','.join('?' for _ in message_ids)
            cursor.execute(
                f"UPDATE chat_messages SET {visibility_column} = 0 WHERE user_id = ? AND id IN ({placeholders})",
                (user_id, *message_ids)
            )
        else:
            # Soft delete all
            cursor.execute(f"UPDATE chat_messages SET {visibility_column} = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting history: {e}")
    finally:
        if conn:
            conn.close()

def delete_history_by_content(user_id: str, content_list: list):
    """按内容删除历史记录 (用于侧边栏删除)"""
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        for content in content_list:
            cursor.execute(
                "UPDATE chat_messages SET visible_in_history = 0 WHERE user_id = ? AND role = 'user' AND content = ?",
                (user_id, content)
            )
        conn.commit()
    except Exception as e:
        print(f"Error deleting history by content: {e}")
    finally:
        if conn:
            conn.close()


def get_modules():
    """获取或初始化模块实例"""
    global _classifier, _db_query, _deepseek, _financial_query
    
    if _classifier is None:
        _classifier = IntentClassifier(use_llm=True)
        _db_query = TaxIncentiveQuery()
        _deepseek = DeepSeekClient()
        _financial_query = FinancialQuery()
    
    return _classifier, _db_query, _deepseek, _financial_query


class ChatRequest(BaseModel):
    """聊天请求模型"""
    question: str
    company_id: Optional[int] = None
    enable_routing: bool = True
    show_chart: bool = True  # 新增: 是否显示图表
    response_mode: str = "detailed"  # 新增: 回答模式 (detailed/concise)


class ChatResponse(BaseModel):
    """非流式聊天响应"""
    content: str
    source: str  # "tax_incentive", "financial", "coze"


# 财务关键词列表（从 coze_chat.py 迁移）
FINANCIAL_KEYWORDS = [
    # 利润表相关
    "销售额", "收入", "营业收入", "营收", "总收入",
    "利润", "净利润", "营业利润", "毛利", "利润总额", "税前利润",
    "成本", "营业成本", "销售成本", "主营业务成本",
    "费用", "销售费用", "管理费用", "财务费用", "行政费用", "利息费用",
    "税金及附加", "附加税", "所得税费用", "所得税", "企业所得税",
    
    # 资产负债表相关
    "资产", "总资产", "资产总额", "负债", "总负债", "负债总额",
    "权益", "所有者权益", "净资产", "股东权益",
    "存货", "库存", "应收账款", "应付账款",
    "流动资产", "流动负债", "现金", "银行存款",
    
    # 财务指标相关
    "毛利率", "净利率", "净利润率", "利润率",
    "资产负债率", "负债率", "流动比率", "速动比率",
    "ROA", "ROE", "roa", "roe", "总资产收益率", "净资产收益率",
    "周转率", "周转天数", "存货周转率", "应收账款周转率",
    "增长率", "营收增长率", "利润增长率",
    
    # 纳税相关
    "应纳税额", "税负率", "增值税税负", "增值税", "所得税额",
    
    # 通用查询词
    "多少", "是多少", "数据", "金额", "查询", "增长", "变化", "趋势", "情况"
]


def has_financial_keywords(question: str) -> bool:
    """检查问题是否包含财务关键词"""
    return any(kw in question for kw in FINANCIAL_KEYWORDS)


async def generate_sse_response(
    question: str, 
    user_id: str,
    company_id: Optional[int] = None,
    enable_routing: bool = True,
    show_chart: bool = True,
    response_mode: str = "detailed"
) -> AsyncGenerator[str, None]:
    """
    生成 SSE 流式响应
    
    Yields:
        SSE 格式的消息: "data: {json}\n\n"
    """
    classifier, db_query, deepseek, financial_query = get_modules()
    
    def send_event(event_type: str, data: dict) -> str:
        """格式化 SSE 事件"""
        return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    
    def send_content(content: str) -> str:
        """发送内容片段"""
        return send_event("message", {"content": content})
    

    try:
        # 发送开始事件
        yield send_event("start", {"status": "processing"})
        
        # 获取公司信息
        company = None
        if company_id:
            import sqlite3
            conn = sqlite3.connect(FINANCIAL_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM companies WHERE id = ?", (company_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                company = {"id": row[0], "name": row[1]}
        # 4. 保存完整的 AI 回答
        # (此时 stream_financial_response 等已执行完毕，我们需要一种机制捕获产生的内容)
        # 由于是流式返回，上面的生成器已经在 yield 内容。
        # 我们需要在生成器内部收集完整内容，或者在 yield 之后保存。
        # 这里为了简单，我们修改生成器函数，让它们负责保存，或者使用一个累加器。
        
        # 更好的方式：重新设计 stream_functions 让它们返回完整内容，
        # 但这里是 generator。
        # 方案：在各个 internal stream 函数中维护 full_content 并保存。
        # 鉴于代码结构，我们在本函数(generate_sse_response)无法直接获取子生成器的累积内容，
        # 除非子生成器 yield 特殊事件或者我们传入 callback。
        
        # 让我们把 save_message 逻辑放在 start event 之后 (保存用户问题)
        save_message(user_id, "user", question)
        
        full_response_content = ""

        # 路由逻辑-修改为捕获内容
        if not enable_routing:
             # Coze API
            yield send_event("route", {"path": "coze"})
            async for chunk in stream_coze_response(question):
                # 解析 chunk 获取 content
                # chunk 格式: "event: message\ndata: {"content": "..."}\n\n"
                if "content" in chunk:
                    try:
                        # 简单的字符串提取，健壮性一般但有效
                        import re
                        match = re.search(r'"content":\s*"(.*)"\}', chunk)
                        if match:
                             # 这种提取对转义字符处理不好，最好解析 JSON
                             pass
                        # Better: re-parse json
                        lines = chunk.strip().split('\n')
                        for line in lines:
                            if line.startswith('data:'):
                                data = json.loads(line[5:])
                                if 'content' in data:
                                    full_response_content += data['content']
                    except:
                        pass
                yield chunk
        else:
            # ... 现有逻辑 ...
            # 为了捕获内容，我们需要包装一下 yield
            
            # 定义一个内部生成器来代理 iterate
            async def content_capturer(generator):
                nonlocal full_response_content
                async for chunk in generator:
                    # 尝试解析 content 用于保存
                    # chunk 可能是 message, route, chart, summary 等
                    try:
                        lines = chunk.strip().split('\n')
                        event_type = None
                        for line in lines:
                            if line.startswith('event:'):
                                event_type = line[6:].strip()
                            if line.startswith('data:'):
                                data = json.loads(line[5:])
                                if event_type == 'message' and 'content' in data:
                                    full_response_content += data['content']
                                elif event_type == 'summary' and 'content' in data:
                                    full_response_content += f"\n\n**总结**:\n{data['content']}"
                                # Chart 数据比较复杂，暂时只保存文本描述或特殊标记
                                # 如果要保存图表，需要在 database 增加字段或者把 chart json 存入 content
                                elif event_type == 'chart':
                                    # 将图表数据作为特殊标记存入文本，或者后续前端解析
                                    # 这里简单记录 [图表] 占位符，或者保存 raw json
                                    # 为了前端能恢复，最好保存 raw json 到 content (mixin) 
                                    # 或者 数据库区分 type
                                    # 简单起见：我们将 chart data json 序列化追加到 content，
                                    # 并用特殊分隔符，或者前端依靠 content 里的 markdown。
                                    # 但 chart 是结构化数据。
                                    # 修改 chat_messages 表结构支持 json data 最好，
                                    # 但现在表只有 content (text).
                                    # 让我们把 Chart JSON append 到 content 后面，用特殊标记包裹
                                    # <CHART_DATA>json</CHART_DATA>
                                    full_response_content += f"\n\n<CHART_DATA>{json.dumps(data, ensure_ascii=False)}</CHART_DATA>\n\n"
                    except:
                        pass
                    yield chunk

            # 意图识别
            intent = classifier.classify(question)
            
            # ... (省略中间重复代码, 只在此处做逻辑分支) ...
            if intent == "other" and company and has_financial_keywords(question):
                intent = "financial_data"
                
            path_name = "financial" if intent == "financial_data" else intent
            yield send_event("route", {"path": path_name, "company": company["name"] if company else None})
            
            if intent == "financial_data":
                async for chunk in content_capturer(stream_financial_response(question, company, financial_query, deepseek, show_chart, response_mode)):
                    yield chunk
            elif intent == "tax_incentive":
                async for chunk in content_capturer(stream_tax_response(question, db_query, deepseek)):
                    yield chunk
            else:
                async for chunk in content_capturer(stream_coze_response(question)):
                    yield chunk

        # Generation Complete: Save Assistant Message
        if full_response_content:
            save_message(user_id, "assistant", full_response_content)

    except Exception as e:
        yield send_event("error", {"message": str(e)})
    
    finally:
        yield send_event("done", {"status": "completed"})


async def stream_tax_response(
    question: str, 
    db_query: TaxIncentiveQuery, 
    deepseek: DeepSeekClient
) -> AsyncGenerator[str, None]:
    """流式返回税收优惠查询结果"""
    
    def send_content(content: str) -> str:
        return f"event: message\ndata: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
    
    # 查询数据库
    results, total_count, query_intent = db_query.search(question, limit=20)
    
    if not results:
        yield send_content("📊 **本地知识库查询结果**\n\n")
        yield send_content("未找到相关税收优惠政策。\n\n")
        yield send_content("💡 **建议**:\n")
        yield send_content("1. 尝试使用更具体的关键词\n")
        yield send_content("2. 咨询税务专业人士\n")
        return
    
    # 显示统计信息
    yield send_content("📊 **本地知识库查询结果**\n\n")
    
    if total_count > len(results):
        yield send_content(f"知识库共有 **{total_count}** 条相关政策,以下展示前 **{len(results)}** 条:\n\n")
        yield send_content("💡 *如需查看更多,请使用更具体的关键词缩小范围*\n\n")
    else:
        yield send_content(f"找到 **{total_count}** 条相关政策:\n\n")
    
    # 构建结果文本
    results_text = ""
    is_detailed = len(results) <= 10
    
    for idx, result in enumerate(results, 1):
        results_text += f"### 政策 {idx}\n"
        results_text += f"- **税种**: {result.get('tax_type', 'N/A')}\n"
        results_text += f"- **优惠项目**: {result.get('project_name', 'N/A')}\n"
        results_text += f"- **优惠方式**: {result.get('incentive_method', 'N/A')}\n"
        
        if result.get('qualification'):
            qual = result['qualification']
            if is_detailed or query_intent == "condition":
                if len(qual) > 500:
                    qual = qual[:500] + "..."
            else:
                if len(qual) > 100:
                    qual = qual[:100] + "..."
            results_text += f"- **认定条件**: {qual}\n"
        
        if result.get('detailed_rules'):
            rules = result['detailed_rules']
            if is_detailed:
                if len(rules) > 800:
                    rules = rules[:800] + "..."
            else:
                if len(rules) > 150:
                    rules = rules[:150] + "..."
            results_text += f"- **具体规定**: {rules}\n"
        
        if result.get('legal_basis'):
            basis = result['legal_basis']
            if is_detailed:
                if len(basis) > 400:
                    basis = basis[:400] + "..."
            else:
                if len(basis) > 100:
                    basis = basis[:100] + "..."
            results_text += f"- **法律依据**: {basis}\n"
        
        results_text += "\n"
    
    # 构建 DeepSeek prompt
    if query_intent == "condition":
        prompt = f"""请根据以下税收优惠政策数据,回答用户问题,须包含具体优惠规定、优惠方式、法律依据等关键信息,**重点突出优惠认定条件、申请要求、所需资料等**。

用户问题: {question}

政策数据:
{results_text}

要求:
1. 用清晰的Markdown格式回答
2. **重点突出优惠认定条件、申请要求、所需资料等**
3. 如有多个政策,分别说明各自的条件和要求
4. 语言简洁专业,易于理解
5. 如果需要更详细信息,建议咨询税务专业人士

请直接回答,不要重复问题。"""
    else:
        prompt = f"""请根据以下税收优惠政策数据,回答用户问题。

用户问题: {question}

政策数据:
{results_text}

要求:
1. 用清晰的Markdown格式回答
2. 突出关键信息(优惠比例、适用条件、具体优惠规定、法律依据等)
3. 如有多个政策,简要说明它们的区别和适用场景
4. 语言简洁专业,易于理解
5. 如果需要更详细信息,建议咨询税务专业人士

请直接回答,不要重复问题。"""
    
    messages = [{"role": "user", "content": prompt}]
    
    # 流式输出 DeepSeek 响应
    for chunk in deepseek.chat_completion(messages, stream=True):
        if chunk:
            yield send_content(chunk)
            await asyncio.sleep(0.01)
    
    # 添加数据来源标识
    yield send_content("\n\n---\n")
    yield send_content("*数据来源: 本地税收优惠政策数据库*\n")


async def stream_financial_response(
    question: str,
    company: Optional[dict],
    financial_query: FinancialQuery,
    deepseek: DeepSeekClient,
    show_chart: bool = True,
    response_mode: str = "detailed"
) -> AsyncGenerator[str, None]:
    """流式返回财务数据查询结果"""
    
    def send_content(content: str) -> str:
        return f"event: message\ndata: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
    
    def send_event(event_type: str, data: dict) -> str:
        return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    
    try:
        if company:
            # 使用前端选中的公司
            time_range = financial_query.extract_time_range(question)
            metrics = financial_query.extract_metrics(question)
            results = financial_query.execute_query(company['id'], time_range, metrics, question)
            
            if not results:
                yield send_content("📊 **企业财务数据查询**\n\n")
                yield send_content(f"📋 {company['name']} 暂无相关数据\n")
                return
            
            status = "success"
        else:
            # 从问题中匹配公司
            results, company, status = financial_query.search(question)
        
        if status == "company_not_found":
            yield send_content("📊 **企业财务数据查询**\n\n")
            yield send_content("❌ 未找到该企业,请检查企业名称是否正确。\n\n")
            yield send_content("💡 **系统中的企业包括**:\n")
            for name in financial_query._load_companies().values():
                yield send_content(f"- {name}\n")
            return
        
        if status == "no_data" or not results:
            yield send_content("📊 **企业财务数据查询**\n\n")
            yield send_content(f"📋 {company['name']} 暂无相关数据\n")
            return
        
        # 显示标题
        yield send_content("📊 **企业财务数据查询**\n\n")
        
        # === 检查是否需要提示默认平均值 ===
        # 条件: 1.数据是按年分组(结果中没有quarter) 2.指标是比率类 3.问题中没有明确指明"平均"等词
        try:
            has_ratio = False
            is_annual = True
            
            # 检查是否包含比率指标
            for r in results:
                m_name = r.get('metric_name', '')
                # 简单判断: 包含"率", "比", "burden", "margin"等
                if any(x in m_name for x in ["率", "比", "burden", "margin"]):
                    has_ratio = True
                
                # 检查是否包含季度信息 (如果任一行有季度且不为None/0，则不是纯年度)
                q = r.get('quarter') or r.get('period_quarter')
                if q:
                    is_annual = False
            
            # 检查问题关键词
            explicit_keywords = ["平均", "最大", "最小", "每季", "季度", "明细", "趋势", "detail", "avg", "max", "min"]
            has_explicit_intent = any(kw in question for kw in explicit_keywords)
            
            if has_ratio and is_annual and not has_explicit_intent:
                warning_msg = "💡 *系统提示: 用户没有明确提示比率指标是查询明细还是平均值、最大值等统计值，系统默认计算平均值；如果希望更精确查询，请给出明确提示*\n\n"
                yield send_content(warning_msg)
                
        except Exception as w_e:
            print(f"Warning logic error: {w_e}")

        # === 1. 生成表格 (详细/标准模式) ===
        if response_mode in ["detailed", "standard"]:
            formatted = financial_query.format_results(results, company)
            yield send_content(formatted)
        
        # === 2. 生成图表 (仅详细模式) ===
        comparison_result = None
        if response_mode == "detailed":
            # 对比分析计算
            time_range = financial_query.extract_time_range(question)
            if time_range.get('is_comparison'):
                comparison_result = financial_query.calculate_comparison(results, time_range)
                if comparison_result.get('has_comparison'):
                    formatted_comparison = financial_query.format_comparison(comparison_result, company)
                    yield send_content(formatted_comparison)
            
            # 发送图表数据 (仅当开启显示且数据足够时)
            if len(results) >= 2:
                try:
                    # 1. 整理数据：按 metric 分组
                    metrics_map = {} # metric -> { (year, q) -> value }
                    all_periods = set()
                    
                    for r in results:
                        m = r['metric_name']
                        p = (r['year'], r.get('quarter'))
                        all_periods.add(p)
                        if m not in metrics_map:
                            metrics_map[m] = {}
                        metrics_map[m][p] = r['value']
                    
                    # 排序 periods
                    sorted_periods = sorted(list(all_periods), key=lambda x: (x[0], x[1] or 0))
                    labels = []
                    for year, quarter in sorted_periods:
                        labels.append(f"{year}年" + (f"Q{quarter}" if quarter else ""))
                    
                    unique_metrics = list(metrics_map.keys())
                    
                    # 2. 决策：单指标 vs 多指标
                    if len(unique_metrics) == 1:
                        # === 单指标：使用详细对比图表 (Combo Chart) ===
                        metric = unique_metrics[0]
                        values = []
                        growth_amounts = []
                        growth_rates = []
                        
                        prev_val = None
                        for p in sorted_periods:
                            val = metrics_map[metric].get(p)
                            values.append(val or 0)
                            
                            if prev_val is not None and prev_val != 0 and val is not None:
                                growth = val - prev_val
                                growth_pct = (growth / abs(prev_val)) * 100
                                growth_wan = growth / 10000 if abs(growth) >= 10000 else growth
                                growth_amounts.append(round(growth_wan, 2))
                                growth_rates.append(round(growth_pct, 2))
                            else:
                                growth_amounts.append(None)
                                growth_rates.append(None)
                            
                            prev_val = val
                        
                        # 如果有对比信息(growth_rates不全为None)，使用Combo图，否则普通Bar图
                        if any(g is not None for g in growth_rates):
                            chart_data = {
                                "chartType": "combo",
                                "title": f"{company['name']} {metric}趋势分析",
                                "labels": labels,
                                "datasets": [
                                    {
                                        "type": "bar",
                                        "label": metric,  # 显示原始指标名
                                        "data": values,   # 显示原始数值
                                        "yAxisID": "y",
                                        "backgroundColor": "rgba(54, 162, 235, 0.8)",
                                        "borderColor": "rgba(54, 162, 235, 1)"
                                    },
                                    {
                                        "type": "bar",
                                        "label": "增长率(%)",
                                        "data": growth_rates,
                                        "yAxisID": "y1",
                                        "borderColor": "rgba(255, 159, 64, 1)",
                                        "backgroundColor": "rgba(255, 159, 64, 0.7)", # Slightly more opaque for bar
                                    }
                                ],
                                "options": {
                                    "scales": {
                                        "y": {"type": "linear", "position": "left", "title": {"display": True, "text": metric}}, 
                                        "y1": {"type": "linear", "position": "right", "title": {"display": True, "text": "增长率(%)"}, "grid": {"drawOnChartArea": False}}
                                    }
                                }
                            }
                        else:
                            chart_data = {
                                "chartType": "bar",
                                "title": f"{company['name']} {metric}",
                                "labels": labels,
                                "datasets": [{"label": metric, "data": values}]
                            }
                        yield send_event("chart", chart_data)
                        
                    else:
                        # === 多指标：发送两个图表 (绝对值对比 + 增长率对比) ===
                        # 限制指标数量，防止由于宽表导致图表不可读 (e.g. top 5)
                        top_metrics = unique_metrics[:5] 
                        
                        colors = [
                            "rgba(54, 162, 235, 0.8)", "rgba(255, 99, 132, 0.8)", 
                            "rgba(255, 206, 86, 0.8)", "rgba(75, 192, 192, 0.8)", 
                            "rgba(153, 102, 255, 0.8)"
                        ]
                        
                        border_colors = [
                            "rgba(54, 162, 235, 1)", "rgba(255, 99, 132, 1)", 
                            "rgba(255, 206, 86, 1)", "rgba(75, 192, 192, 1)", 
                            "rgba(153, 102, 255, 1)"
                        ]
                        
                        # === 图表1: 绝对值对比 (柱状图) ===
                        value_datasets = []
                        for idx, metric in enumerate(top_metrics):
                            data_points = []
                            for p in sorted_periods:
                                val = metrics_map[metric].get(p, 0)
                                data_points.append(val or 0)
                            
                            value_datasets.append({
                                "type": "bar",
                                "label": metric,
                                "data": data_points,
                                "backgroundColor": colors[idx % len(colors)],
                                "borderColor": border_colors[idx % len(border_colors)],
                                "borderWidth": 1
                            })
                        
                        chart1_data = {
                            "chartType": "bar",
                            "title": f"{company['name']} 指标绝对值对比 ({len(top_metrics)}/{len(unique_metrics)})",
                            "labels": labels,
                            "datasets": value_datasets
                        }
                        yield send_event("chart", chart1_data)
                        
                        # === 图表2: 增长率对比 (柱状图) ===
                        growth_datasets = []
                        for idx, metric in enumerate(top_metrics):
                            growth_rates = []
                            prev_val = None
                            
                            for p in sorted_periods:
                                val = metrics_map[metric].get(p)
                                
                                if prev_val is not None and prev_val != 0 and val is not None:
                                    growth_pct = ((val - prev_val) / abs(prev_val)) * 100
                                    growth_rates.append(round(growth_pct, 2))
                                else:
                                    growth_rates.append(None)
                                
                                prev_val = val
                            
                            growth_datasets.append({
                                "type": "bar",
                                "label": metric,
                                "data": growth_rates,
                                "backgroundColor": colors[idx % len(colors)],
                                "borderColor": border_colors[idx % len(border_colors)],
                                "borderWidth": 1
                            })
                        
                        chart2_data = {
                            "chartType": "bar",
                            "title": f"{company['name']} 指标增长率对比 (%) ({len(top_metrics)}/{len(unique_metrics)})",
                            "labels": labels,
                            "datasets": growth_datasets,
                            "options": {
                                "scales": {
                                    "y": {
                                        "ticks": {
                                            "callback": "function(value) { return value + '%'; }"
                                        }
                                    }
                                }
                            }
                        }
                        yield send_event("chart", chart2_data)
                        
                except Exception as e:
                    print(f"⚠️ 图表数据发送失败: {e}")

        # === 3. 分析总结 (详细/标准模式) ===
        if response_mode in ["detailed", "standard"]:
            if len(results) > 2:
                yield send_event("summary", {"content": "\n**分析总结**:\n"})
                results_text = financial_query.format_results(results, company) # 重新获取格式化文本
                prompt = f"""请根据以下企业财务数据,简要分析总结。用户问题: {question}
数据:
{results_text}
要求: 根据返回的数据量大小,用5-20句话总结数据特点和趋势，分析可能存在的风险; 如有明显趋势变化,简要分析可能原因；如有两个或两个以上指标且相互可以对比分析，则需分析是否存在背离。不要重复原始数据。"""
                
                messages = [{"role": "user", "content": prompt}]
                for chunk in deepseek.chat_completion(messages, stream=True):
                    if chunk:
                        yield send_event("summary", {"content": chunk})
                        await asyncio.sleep(0.01)
        
        # === 4. 简报模式 (Concise) ===
        elif response_mode == "concise":
            # 仅生成自然语言总结，无表格无图表
            
            # 将 results 转换为简化文本供 LLM 阅读
            raw_data_text = f"企业: {company['name']}\n数据:\n"
            for r in results:
                metric = r.get('metric_name')
                year = r.get('year')
                qtr = r.get('quarter')
                val = r.get('value')
                unit = r.get('unit', '元')
                if qtr:
                    time_label = f"{year}年Q{qtr}"
                else:
                    time_label = f"{year}年"
                
                # 简单数值格式化
                if val is not None and isinstance(val, (int, float)):
                    if abs(val) > 100000000:
                        val_str = f"{val/100000000:.2f}亿"
                    elif abs(val) > 10000:
                        val_str = f"{val/10000:.2f}万"
                    else:
                        val_str = f"{val:.2f}"
                else:
                    val_str = str(val)
                
                raw_data_text += f"- {time_label} {metric}: {val_str} {unit}\n"
            
            prompt = f"""请根据以下财务查询结果，直接回答用户问题。

用户问题: {question}

查询到的原始数据:
{raw_data_text}

要求:
根据返回的数据量大小,用5-20句话总结数据特点和趋势，分析可能存在的风险; 如有明显趋势变化,简要分析可能原因；如有两个或两个以上指标且相互可以对比分析，则需分析是否存在背离。
**不要使用表格** ；控制篇幅，便于移动端查看。

请直接回答。"""
            
            messages = [{"role": "user", "content": prompt}]
            
            # 流式输出总结
            for chunk in deepseek.chat_completion(messages, stream=True):
                if chunk:
                    yield send_content(chunk)
                    await asyncio.sleep(0.01)

        # 添加数据来源标识
        yield send_content("\n\n---\n")
        yield send_content("*数据来源: 企业财务数据库*\n")
    
    except Exception as e:
        yield send_content(f"\n\n⚠️ 查询出错: {str(e)}\n")



def parse_sse_line(line: str):
    """解析 SSE 行"""
    line = line.strip()
    if not line:
        return None, None
    if line.startswith('event:'):
        return line[6:].strip(), None
    if line.startswith('data:'):
        try:
            return None, json.loads(line[5:].strip())
        except:
            return None, None
    return None, None


async def stream_coze_response(question: str) -> AsyncGenerator[str, None]:
    """流式调用 Coze API"""
    
    def send_content(content: str) -> str:
        return f"event: message\ndata: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
    
    headers = {
        "Authorization": f"Bearer {PAT_TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "text/event-stream",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {
        "bot_id": BOT_ID,
        "user_id": USER_ID,
        "stream": True,
        "auto_save_history": True,
        "additional_messages": [{"role": "user", "content": question, "content_type": "text"}],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(
            "https://api.coze.cn/v3/chat",
            headers=headers,
            json=payload,
            stream=True,
            timeout=180,
            verify=False
        )
        
        if response.status_code != 200:
            yield send_content(f"❌ API 错误: {response.status_code}\n")
            return
        
        current_event = None
        for chunk in response.iter_content(chunk_size=1024):
            if not chunk:
                continue
            
            chunk_str = chunk.decode('utf-8', errors='ignore')
            lines = chunk_str.split('\n')
            
            for line in lines:
                event_type, data = parse_sse_line(line)
                if event_type:
                    current_event = event_type
                if data and current_event == "conversation.message.delta":
                    if data.get("role") == "assistant" and data.get("type") == "answer":
                        content = data.get("content", "")
                        if content:
                            yield send_content(content)
                            await asyncio.sleep(0.01)
    
    except Exception as e:
        yield send_content(f"❌ 请求失败: {str(e)}\n")


@router.post("/chat")
async def chat_stream(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    智能对话 API（SSE 流式输出）
    
    - 自动识别意图并路由到对应模块
    - 支持税收优惠查询、财务数据查询、通用咨询
    - 返回 SSE 流式响应
    """
    user_id = str(current_user['id'])
    return StreamingResponse(
        generate_sse_response(
            question=request.question,
            user_id=user_id,
            company_id=request.company_id,
            enable_routing=request.enable_routing,
            show_chart=request.show_chart,
            response_mode=request.response_mode
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/chat/sync")
async def chat_sync(request: ChatRequest) -> ChatResponse:
    """
    同步对话 API（非流式，用于测试）
    """
    classifier, db_query, deepseek, financial_query = get_modules()
    
    # 简化版同步响应
    intent = classifier.classify(request.question)
    
    if intent == "tax_incentive":
        results, total_count, _ = db_query.search(request.question, limit=5)
        if results:
            content = f"找到 {total_count} 条相关税收优惠政策。"
        else:
            content = "未找到相关税收优惠政策。"
        return ChatResponse(content=content, source="tax_incentive")
    
    elif intent == "financial_data":
        results, company, status = financial_query.search(request.question)
        if status == "success" and results:
            if request.response_mode == "concise":
                # 简略模式：只返回简短总结
                content = f"已找到 {company['name']} 的相关数据，共有 {len(results)} 条记录。"
            else:
                content = financial_query.format_results(results, company)
        else:
            content = "未找到相关财务数据。"
        return ChatResponse(content=content, source="financial")
    
    else:
        content = "请使用流式 API (/api/chat) 获取完整回答。"
        return ChatResponse(content=content, source="coze")


@router.get("/chat/history")
async def get_history_api(limit: int = 50, current_user: dict = Depends(get_current_user)):
    """获取聊天历史 (主窗口消息)"""
    user_id = str(current_user['id'])
    return get_chat_history(user_id, limit)


@router.get("/chat/history-items")
async def get_history_items_api(limit: int = 50, current_user: dict = Depends(get_current_user)):
    """获取历史记录列表 (侧边栏)"""
    user_id = str(current_user['id'])
    return get_history_items(user_id, limit)


class DeleteHistoryRequest(BaseModel):
    message_ids: Optional[list] = None
    delete_all: bool = False
    target: str = "chat"  # "chat" for main window, "history" for sidebar
    content_list: Optional[list] = None  # For deleting by content


@router.delete("/chat/history")
async def delete_history_api(request: DeleteHistoryRequest, current_user: dict = Depends(get_current_user)):
    """删除聊天历史 (软删除)"""
    user_id = str(current_user['id'])
    
    # 如果是按内容删除 (侧边栏)
    if request.content_list:
        delete_history_by_content(user_id, request.content_list)
        return {"status": "success"}
    
    # 按ID或全部删除
    if request.delete_all:
        delete_user_history(user_id, target=request.target)
    elif request.message_ids:
        delete_user_history(user_id, request.message_ids, target=request.target)
    return {"status": "success"}
