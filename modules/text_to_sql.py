#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Text-to-SQL 引擎
功能:
1. 使用DeepSeek动态生成SQL
2. SQL安全验证
3. 执行并返回结果
"""

import sqlite3
import re
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class TextToSQLEngine:
    """Text-to-SQL引擎 - 使用LLM动态生成SQL查询"""
    
    def __init__(self, db_path: str = None):
        """
        初始化
        
        Args:
            db_path: 数据库路径
        """
        base_dir = Path(__file__).parent.parent
        self.db_path = db_path or str(base_dir / 'database' / 'financial.db')
        
        # 缓存最近的SQL查询
        self._sql_cache = {}
        self._max_cache_size = 100
        
        # DeepSeek客户端(延迟加载)
        self._deepseek = None
        
        # Schema Provider(延迟加载)
        self._schema_provider = None
    
    @property
    def deepseek(self):
        """延迟加载DeepSeek客户端"""
        if self._deepseek is None:
            try:
                from modules.deepseek_client import DeepSeekClient
            except ModuleNotFoundError:
                from deepseek_client import DeepSeekClient
            self._deepseek = DeepSeekClient()
        return self._deepseek
    
    @property
    def schema_provider(self):
        """延迟加载SchemaProvider"""
        if self._schema_provider is None:
            try:
                from modules.schema_provider import SchemaProvider
            except ModuleNotFoundError:
                from schema_provider import SchemaProvider
            self._schema_provider = SchemaProvider(db_path=self.db_path)
        return self._schema_provider
    
    def generate_sql(self, question: str, company_id: int, 
                     years: List[int], quarter: int = None) -> Optional[str]:
        """
        使用LLM生成SQL查询
        
        Args:
            question: 用户问题
            company_id: 企业ID
            years: 年份列表
            quarter: 季度(可选)
        
        Returns:
            生成的SQL语句,如果失败返回None
        """
        # 检查缓存
        cache_key = self._get_cache_key(question, company_id, years, quarter)
        if cache_key in self._sql_cache:
            print(f"📦 使用缓存的SQL")
            return self._sql_cache[cache_key]
        
        # 构建Prompt
        prompt = self._build_prompt(question, company_id, years, quarter)
        
        # 调用DeepSeek
        messages = [
            {"role": "system", "content": "你是SQL生成专家。只返回SQL语句,不要有任何其他解释文字。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.deepseek.chat_completion(
                messages, 
                stream=False, 
                temperature=0.3,  # 低温度提高确定性
                max_tokens=500
            )
            
            # 提取SQL
            sql = self._extract_sql(response)
            
            if sql and self.validate_sql(sql):
                # 缓存
                self._cache_sql(cache_key, sql)
                print(f"✅ 生成SQL: {sql[:100]}...")
                return sql
            else:
                print(f"⚠️  SQL验证失败: {sql}")
                return None
                
        except Exception as e:
            print(f"⚠️  SQL生成失败: {e}")
            return None
    
    def _build_prompt(self, question: str, company_id: int, 
                      years: List[int], quarter: int = None) -> str:
        """构建LLM提示"""
        # 获取Schema描述
        schema_desc = self.schema_provider.get_schema_description()
        
        # 获取业务术语
        glossary = self.schema_provider.format_glossary_for_prompt()
        
        # 构建年份条件
        if len(years) == 1:
            year_condition = f"period_year = {years[0]}"
        else:
            year_condition = f"period_year IN ({','.join(str(y) for y in years)})"
        
        # 构建季度条件
        quarter_condition = ""
        if quarter:
            quarter_condition = f" AND period_quarter = {quarter}"
        
        prompt = f"""根据用户问题生成SQLite查询语句。

## 数据库Schema
{schema_desc}

## 业务术语映射
{glossary}

## 必须遵守的约束
1. 只生成SELECT语句
2. 必须包含 company_id = {company_id} 条件
3. 必须包含 {year_condition} 条件{quarter_condition}
4. 使用SUM()对金额进行汇总
5. 按period_year分组
6. 如果涉及多个指标，请作为多个列查询，并为每列使用有意义的别名(AS '别名')
7. 只返回SQL语句,不要有任何解释

## 用户问题
{question}

## 请生成SQL:"""
        
        return prompt
    
    def _extract_sql(self, response: str) -> Optional[str]:
        """从LLM响应中提取SQL"""
        if not response:
            return None
        
        # 清理响应
        sql = response.strip()
        
        # 移除markdown代码块
        if sql.startswith("```"):
            lines = sql.split("\n")
            sql_lines = []
            in_code = False
            for line in lines:
                if line.startswith("```"):
                    in_code = not in_code
                    continue
                if in_code or not line.startswith("```"):
                    sql_lines.append(line)
            sql = "\n".join(sql_lines).strip()
        
        # 移除sql前缀
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()
        
        return sql
    
    def validate_sql(self, sql: str) -> bool:
        """
        验证SQL安全性
        
        Args:
            sql: SQL语句
        
        Returns:
            True如果安全,False否则
        """
        if not sql:
            return False
        
        sql_upper = sql.upper().strip()
        
        # 只允许SELECT
        if not sql_upper.startswith("SELECT"):
            print(f"⚠️  拒绝非SELECT语句")
            return False
        
        # 禁止危险关键字
        dangerous_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
            'TRUNCATE', 'EXEC', 'EXECUTE', '--', ';--', 'UNION SELECT'
        ]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                print(f"⚠️  检测到危险关键字: {keyword}")
                return False
        
        # 检查是否包含company_id条件
        if 'COMPANY_ID' not in sql_upper:
            print(f"⚠️  缺少company_id条件")
            return False
        
        return True
    
    def execute_sql(self, sql: str, limit: int = 1000) -> Tuple[List[Dict], Optional[str]]:
        """
        安全执行SQL
        
        Args:
            sql: SQL语句
            limit: 结果数量限制
        
        Returns:
            (结果列表, 错误信息)
        """
        if not self.validate_sql(sql):
            return [], "SQL验证失败"
        
        # 添加LIMIT
        if "LIMIT" not in sql.upper():
            sql = f"{sql.rstrip(';')} LIMIT {limit}"
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 设置超时
            cursor.execute("PRAGMA busy_timeout = 5000")
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            # 转换为字典列表
            results = []
            for row in rows:
                results.append(dict(row))
            
            conn.close()
            
            print(f"📊 SQL执行成功,返回 {len(results)} 条记录")
            return results, None
            
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️  SQL执行错误: {error_msg}")
            return [], error_msg
    
    def query(self, question: str, company_id: int, 
              years: List[int], quarter: int = None) -> Tuple[List[Dict], str]:
        """
        完整的Text-to-SQL查询流程
        
        Args:
            question: 用户问题
            company_id: 企业ID
            years: 年份列表
            quarter: 季度(可选)
        
        Returns:
            (结果列表, 状态信息)
        """
        # 生成SQL
        sql = self.generate_sql(question, company_id, years, quarter)
        
        if not sql:
            return [], "SQL生成失败"
        
        # 执行SQL
        results, error = self.execute_sql(sql)
        
        if error:
            return [], f"SQL执行错误: {error}"
        
        if not results:
            return [], "查询无结果"
        
        return results, "success"
    
    def _get_cache_key(self, question: str, company_id: int, 
                       years: List[int], quarter: int) -> str:
        """生成缓存键"""
        content = f"{question}|{company_id}|{sorted(years)}|{quarter}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _cache_sql(self, key: str, sql: str):
        """缓存SQL"""
        if len(self._sql_cache) >= self._max_cache_size:
            # 移除最早的缓存
            oldest_key = next(iter(self._sql_cache))
            del self._sql_cache[oldest_key]
        self._sql_cache[key] = sql


# 全局单例
_engine_instance = None

def get_text_to_sql_engine() -> TextToSQLEngine:
    """获取全局TextToSQLEngine实例"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = TextToSQLEngine()
    return _engine_instance


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("TextToSQLEngine 测试")
    print("=" * 60)
    
    engine = TextToSQLEngine()
    
    # 测试用例
    test_cases = [
        ("ABC公司2023年采购发票金额", 5, [2023], None),
        ("2022-2024年销售发票税额", 5, [2022, 2023, 2024], None),
    ]
    
    for question, company_id, years, quarter in test_cases:
        print(f"\n--- 测试: {question} ---")
        results, status = engine.query(question, company_id, years, quarter)
        print(f"状态: {status}")
        print(f"结果数: {len(results)}")
        if results:
            print(f"首条: {results[0]}")
