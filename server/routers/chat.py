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

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator

# 导入现有模块
from modules.intent_classifier import IntentClassifier
from modules.db_query import TaxIncentiveQuery
from modules.deepseek_client import DeepSeekClient
from modules.financial_query import FinancialQuery

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
            conn = sqlite3.connect("database/financial.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM companies WHERE id = ?", (company_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                company = {"id": row[0], "name": row[1]}
        
        # 路由逻辑
        if not enable_routing:
            # 禁用路由，直接使用 Coze API
            yield send_event("route", {"path": "coze"})
            async for chunk in stream_coze_response(question):
                yield chunk
            return
        
        # 意图识别
        intent = classifier.classify(question)
        
        # 特殊处理：如果分类器认为是"other"（通常因为缺自主体），
        # 但用户在UI选择了公司且问题包含财务关键词，则修正为财务查询
        # 注意：这不会覆盖已识别出的 "tax_incentive" 意图
        if intent == "other" and company and has_financial_keywords(question):
            intent = "financial_data"
            
        # 发送路由事件
        path_name = "financial" if intent == "financial_data" else intent
        yield send_event("route", {"path": path_name, "company": company["name"] if company else None})
        
        if intent == "financial_data":
            # 财务数据查询
            async for chunk in stream_financial_response(question, company, financial_query, deepseek, show_chart, response_mode):
                yield chunk
        elif intent == "tax_incentive":
            # 税收优惠查询
            async for chunk in stream_tax_response(question, db_query, deepseek):
                yield chunk
        else:
            # Coze API
            async for chunk in stream_coze_response(question):
                yield chunk
    
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
                    if comparison_result and comparison_result.get('has_comparison'):
                        # 对比分析：为每个指标发送复合图表数据
                        comparisons = comparison_result.get('comparisons', [])
                        print(f"📊 发送 {len(comparisons)} 个复合图表数据到前端")
                        
                        for comp in comparisons:
                            periods = comp.get('periods', [])
                            if len(periods) < 2:
                                continue
                            
                            # 构建图表数据（复用原有逻辑）
                            labels = []
                            values = []
                            growth_amounts = []
                            growth_rates = []
                            
                            prev_val = None
                            for period in periods:
                                year, quarter, val, unit = period
                                label = f"{year}" + (f"Q{quarter}" if quarter else "")
                                labels.append(label)
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
                            
                            chart_data = {
                                "chartType": "combo",
                                "title": f"{company['name']} {comp['metric']}对比",
                                "labels": labels,
                                "datasets": [
                                    {
                                        "type": "bar",
                                        "label": "增长额(万)",
                                        "data": growth_amounts,
                                        "yAxisID": "y",
                                        "backgroundColor": "rgba(54, 162, 235, 0.8)",
                                        "borderColor": "rgba(54, 162, 235, 1)"
                                    },
                                    {
                                        "type": "line",
                                        "label": "增长率(%)",
                                        "data": growth_rates,
                                        "yAxisID": "y1",
                                        "borderColor": "rgba(255, 159, 64, 1)",
                                        "backgroundColor": "rgba(255, 159, 64, 0.2)",
                                        "tension": 0.1
                                    }
                                ],
                                "options": {
                                    "scales": {
                                        "y": {"type": "linear", "position": "left", "title": {"display": True, "text": "增长额(万)"}},
                                        "y1": {"type": "linear", "position": "right", "title": {"display": True, "text": "增长率(%)"}, "grid": {"drawOnChartArea": False}}
                                    }
                                }
                            }
                            yield send_event("chart", chart_data)
                            await asyncio.sleep(0.01)
                    else:
                        # 普通查询：柱状图
                        labels = []
                        values = []
                        for r in results:
                            year = r.get('year', '')
                            quarter = r.get('quarter')
                            label = f"{year}年" + (f"Q{quarter}" if quarter else "")
                            labels.append(label)
                            values.append(r.get('value', 0) or 0)
                        
                        metric_name = results[0].get('metric_name', '数据') if results else '数据'
                        chart_data = {
                            "chartType": "bar",
                            "title": f"{company['name']} {metric_name}",
                            "labels": labels,
                            "datasets": [{"label": metric_name, "data": values}]
                        }
                        yield send_event("chart", chart_data)
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
async def chat_stream(request: ChatRequest):
    """
    智能对话 API（SSE 流式输出）
    
    - 自动识别意图并路由到对应模块
    - 支持税收优惠查询、财务数据查询、通用咨询
    - 返回 SSE 流式响应
    """
    return StreamingResponse(
        generate_sse_response(
            question=request.question,
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
