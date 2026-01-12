#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库Schema提供者
功能:
1. 自动发现数据库Schema
2. 生成LLM可读的Schema描述
3. 发现字段值分布(如invoice_type有哪些值)
4. 生成业务术语映射
"""

import sqlite3
import json
import os
from typing import Dict, List, Optional, Set
from pathlib import Path


class SchemaProvider:
    """数据库Schema提供者 - 为Text-to-SQL生成Schema描述"""
    
    def __init__(self, db_path: str = None, config_path: str = None):
        """
        初始化
        
        Args:
            db_path: 数据库路径
            config_path: metrics_config.json路径
        """
        base_dir = Path(__file__).parent.parent
        self.db_path = db_path or str(base_dir / 'database' / 'financial.db')
        self.config_path = config_path or str(base_dir / 'config' / 'metrics_config.json')
        self.glossary_path = str(base_dir / 'config' / 'business_glossary.json')
        
        # 缓存
        self._schema_cache = None
        self._glossary_cache = None
        self._value_distributions_cache = None
        
        # 需要发现值分布的字段(分类字段)
        self.categorical_columns = [
            ('invoices', 'invoice_type'),
            ('invoices', 'invoice_category'),
            ('tax_reports', 'tax_type'),
        ]
        
        # 排除的表
        self.excluded_tables = {
            'sqlite_sequence', 'users', 'companies', 'company_aliases'
        }
        
        # 排除的字段
        self.excluded_fields = {
            'id', 'company_id', 'created_at', 'updated_at', 'return_id'
        }
        
        # 时间字段
        self.period_fields = {
            'period_year', 'period_month', 'period_quarter', 'period',
            'period_end_date', 'report_date', 'filing_date', 'issue_date'
        }
    
    def get_schema(self) -> Dict[str, List[Dict]]:
        """
        获取数据库Schema
        
        Returns:
            {表名: [{name, type, description}, ...], ...}
        """
        if self._schema_cache is not None:
            return self._schema_cache
        
        self._schema_cache = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                if table in self.excluded_tables:
                    continue
                
                # 获取表结构
                cursor.execute(f"PRAGMA table_info({table})")
                columns = []
                for row in cursor.fetchall():
                    col_name = row[1]
                    col_type = row[2]
                    
                    columns.append({
                        'name': col_name,
                        'type': col_type,
                        'is_period': col_name in self.period_fields,
                        'is_excluded': col_name in self.excluded_fields
                    })
                
                self._schema_cache[table] = columns
            
            conn.close()
        except Exception as e:
            print(f"⚠️  Schema发现失败: {e}")
        
        return self._schema_cache
    
    def get_value_distributions(self) -> Dict[str, Dict[str, List]]:
        """
        获取分类字段的值分布
        
        Returns:
            {表名: {字段名: [值列表], ...}, ...}
        """
        if self._value_distributions_cache is not None:
            return self._value_distributions_cache
        
        self._value_distributions_cache = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for table, column in self.categorical_columns:
                try:
                    cursor.execute(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL")
                    values = [row[0] for row in cursor.fetchall()]
                    
                    if table not in self._value_distributions_cache:
                        self._value_distributions_cache[table] = {}
                    self._value_distributions_cache[table][column] = values
                except:
                    pass
            
            conn.close()
        except Exception as e:
            print(f"⚠️  值分布发现失败: {e}")
        
        return self._value_distributions_cache
    
    def get_schema_description(self) -> str:
        """
        生成LLM可读的Schema描述
        
        Returns:
            Markdown格式的Schema描述
        """
        schema = self.get_schema()
        value_distributions = self.get_value_distributions()
        
        lines = []
        
        for table, columns in sorted(schema.items()):
            # 获取表描述(从config)
            table_desc = self._get_table_description(table)
            lines.append(f"### {table}")
            if table_desc:
                lines.append(f"> {table_desc}")
            
            # 字段列表
            data_columns = [c for c in columns if not c['is_excluded'] and not c['is_period']]
            period_columns = [c for c in columns if c['is_period']]
            
            if data_columns:
                lines.append("数据字段: " + ", ".join([c['name'] for c in data_columns]))
            if period_columns:
                lines.append("时间字段: " + ", ".join([c['name'] for c in period_columns]))
            
            # 值分布
            if table in value_distributions:
                for col, values in value_distributions[table].items():
                    lines.append(f"{col}可选值: {values}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _get_table_description(self, table_name: str) -> str:
        """获取表描述"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            tables_config = config.get('tables', {})
            if table_name in tables_config:
                return tables_config[table_name].get('description', '')
        except:
            pass
        return ''
    
    def generate_glossary(self) -> Dict[str, str]:
        """
        生成业务术语映射
        
        Returns:
            {中文术语: SQL条件或表.字段, ...}
        """
        if self._glossary_cache is not None:
            return self._glossary_cache
        
        self._glossary_cache = {}
        
        # 1. 从metrics_config加载别名映射
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for table_name, table_config in config.get('tables', {}).items():
                for field_name, field_config in table_config.get('fields', {}).items():
                    aliases = field_config.get('aliases', [])
                    for alias in aliases:
                        self._glossary_cache[alias] = f"{table_name}.{field_name}"
            
            # 从item_queries加载
            for query_name, query_config in config.get('item_queries', {}).items():
                if query_name.startswith('_'):
                    continue
                aliases = query_config.get('aliases', [query_name])
                table = query_config.get('table', '')
                value_field = query_config.get('value_field', '')
                filter_field = query_config.get('filter_field')
                filter_value = query_config.get('filter_value')
                item_name_field = query_config.get('item_name_field')
                item_name_value = query_config.get('item_name_value')
                
                # 构建SQL提示
                if filter_field and filter_value:
                    sql_hint = f"{table}.{value_field} WHERE {filter_field}='{filter_value}'"
                elif item_name_field and item_name_value:
                    sql_hint = f"{table}.{value_field} WHERE {item_name_field}='{item_name_value}'"
                else:
                    sql_hint = f"{table}.{value_field}"
                
                for alias in aliases:
                    self._glossary_cache[alias] = sql_hint
        except Exception as e:
            print(f"⚠️  config加载失败: {e}")
        
        # 2. 自动发现值分布
        value_distributions = self.get_value_distributions()
        for table, columns in value_distributions.items():
            for col, values in columns.items():
                self._glossary_cache[f"{col}可选值"] = str(values)
        
        # 3. 加载手动补充
        try:
            if os.path.exists(self.glossary_path):
                with open(self.glossary_path, 'r', encoding='utf-8') as f:
                    manual_glossary = json.load(f)
                
                # 语义映射
                for term, sql in manual_glossary.get('semantic_mappings', {}).items():
                    self._glossary_cache[term] = sql
                
                # 表描述(添加到schema)
                # 暂不处理
        except Exception as e:
            print(f"⚠️  手动术语加载失败: {e}")
        
        return self._glossary_cache
    
    def format_glossary_for_prompt(self, max_items: int = 50) -> str:
        """
        格式化业务术语供Prompt使用
        
        Args:
            max_items: 最大条目数(避免prompt过长)
        
        Returns:
            格式化的术语列表
        """
        glossary = self.generate_glossary()
        
        # 优先显示语义映射(手动配置的)
        lines = []
        
        # 先加载手动配置的语义映射
        try:
            if os.path.exists(self.glossary_path):
                with open(self.glossary_path, 'r', encoding='utf-8') as f:
                    manual = json.load(f)
                for term, sql in manual.get('semantic_mappings', {}).items():
                    lines.append(f"- {term}: {sql}")
        except:
            pass
        
        # 添加值分布
        value_distributions = self.get_value_distributions()
        for table, columns in value_distributions.items():
            for col, values in columns.items():
                lines.append(f"- {table}.{col} 可选值: {values}")
        
        return "\n".join(lines[:max_items])
    
    def reload(self):
        """重新加载(清除缓存)"""
        self._schema_cache = None
        self._glossary_cache = None
        self._value_distributions_cache = None


# 全局单例
_provider_instance = None

def get_schema_provider() -> SchemaProvider:
    """获取全局SchemaProvider实例"""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = SchemaProvider()
    return _provider_instance


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("SchemaProvider 测试")
    print("=" * 60)
    
    provider = SchemaProvider()
    
    # 测试Schema发现
    schema = provider.get_schema()
    print(f"\n发现 {len(schema)} 个表:")
    for table, columns in schema.items():
        data_cols = [c['name'] for c in columns if not c['is_excluded'] and not c['is_period']]
        print(f"  - {table}: {len(data_cols)} 个数据字段")
    
    # 测试值分布
    print("\n值分布发现:")
    distributions = provider.get_value_distributions()
    for table, cols in distributions.items():
        for col, values in cols.items():
            print(f"  - {table}.{col}: {values}")
    
    # 测试业务术语
    glossary = provider.generate_glossary()
    print(f"\n业务术语数量: {len(glossary)}")
    
    # 测试Schema描述
    print("\n=== Schema描述预览 ===")
    desc = provider.get_schema_description()
    print(desc[:1000] + "..." if len(desc) > 1000 else desc)
