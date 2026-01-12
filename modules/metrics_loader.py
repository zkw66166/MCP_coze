#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
财务指标配置加载器
功能:
1. 从JSON配置文件加载指标映射
2. 自动发现数据库Schema中的新字段
3. 合并配置与发现结果
4. 提供未配置字段的提示
"""

import json
import sqlite3
import os
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path


class MetricsLoader:
    """财务指标配置加载器"""
    
    def __init__(self, config_path: str = None, db_path: str = None):
        """
        初始化加载器
        
        Args:
            config_path: 配置文件路径(默认: config/metrics_config.json)
            db_path: 数据库路径(默认: database/financial.db)
        """
        base_dir = Path(__file__).parent.parent
        self.config_path = config_path or str(base_dir / 'config' / 'metrics_config.json')
        self.db_path = db_path or str(base_dir / 'database' / 'financial.db')
        
        # 缓存
        self._config = None
        self._metrics_map = None
        self._keywords = None
        self._formulas = None
        self._db_schema = None
        self._unconfigured_fields = None
    
    def load_config(self) -> Dict:
        """加载配置文件"""
        if self._config is None:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except FileNotFoundError:
                print(f"⚠️  配置文件不存在: {self.config_path}")
                self._config = {"tables": {}, "formulas": {}}
            except json.JSONDecodeError as e:
                print(f"⚠️  配置文件格式错误: {e}")
                self._config = {"tables": {}, "formulas": {}}
        return self._config
    
    def get_metrics_map(self) -> Dict[str, Tuple[str, str]]:
        """
        获取指标映射(中文别名 -> (表名, 字段名))
        
        Returns:
            {别名: (表名, 字段名), ...}
        """
        if self._metrics_map is not None:
            return self._metrics_map
        
        config = self.load_config()
        self._metrics_map = {}
        
        # 从配置文件加载常规字段映射
        for table_name, table_config in config.get('tables', {}).items():
            fields = table_config.get('fields', {})
            for field_name, field_config in fields.items():
                aliases = field_config.get('aliases', [])
                for alias in aliases:
                    # 优先使用较短的别名(如果冲突)
                    if alias not in self._metrics_map:
                        self._metrics_map[alias] = (table_name, field_name)
        
        # 从item_queries加载特殊查询的别名
        for query_name, query_config in config.get('item_queries', {}).items():
            if query_name.startswith('_'):  # 跳过描述字段
                continue
            aliases = query_config.get('aliases', [query_name])
            table = query_config.get('table', '')
            value_field = query_config.get('value_field', 'amount')
            for alias in aliases:
                if alias not in self._metrics_map:
                    # 使用特殊标记表示这是item_query
                    self._metrics_map[alias] = (f'__item_query__{query_name}', value_field)
        
        return self._metrics_map
    
    def get_keywords(self) -> List[str]:
        """
        获取所有财务关键词列表(用于意图识别)
        
        Returns:
            关键词列表
        """
        if self._keywords is not None:
            return self._keywords
        
        config = self.load_config()
        keywords_set = set()
        
        # 从所有别名收集关键词
        for table_config in config.get('tables', {}).values():
            for field_config in table_config.get('fields', {}).values():
                keywords_set.update(field_config.get('aliases', []))
        
        # 从item_queries收集关键词
        for query_name, query_config in config.get('item_queries', {}).items():
            if query_name.startswith('_'):
                continue
            keywords_set.update(query_config.get('aliases', [query_name]))
        
        # 添加通用查询关键词
        keywords_set.update(config.get('common_query_keywords', []))
        
        self._keywords = list(keywords_set)
        return self._keywords
    
    def get_item_queries(self) -> Dict:
        """
        获取特殊item_query配置(用于key-value结构的表)
        
        Returns:
            {查询名: {table, join_table, value_field, ...}, ...}
        """
        config = self.load_config()
        item_queries = {}
        for query_name, query_config in config.get('item_queries', {}).items():
            if query_name.startswith('_'):
                continue
            item_queries[query_name] = query_config
        return item_queries
    
    def get_formulas(self) -> Dict:
        """
        获取公式定义
        
        Returns:
            {公式名: {expression, source_table, unit, ...}, ...}
        """
        if self._formulas is not None:
            return self._formulas
        
        config = self.load_config()
        self._formulas = config.get('formulas', {})
        return self._formulas
    
    def get_unit(self, alias_or_field: str) -> str:
        """
        获取指标单位
        
        Args:
            alias_or_field: 别名或字段名
        
        Returns:
            单位字符串
        """
        config = self.load_config()
        
        # 尝试从配置中查找
        for table_config in config.get('tables', {}).values():
            for field_name, field_config in table_config.get('fields', {}).items():
                aliases = field_config.get('aliases', [])
                if alias_or_field in aliases or alias_or_field == field_name:
                    return field_config.get('unit', '元')
        
        # 默认单位推断
        if '率' in alias_or_field or 'ratio' in alias_or_field.lower():
            return '%'
        elif '天数' in alias_or_field or 'days' in alias_or_field.lower():
            return '天'
        elif '周转' in alias_or_field and '天' not in alias_or_field:
            return '次/年'
        elif '倍数' in alias_or_field or '比率' in alias_or_field:
            return '倍'
        else:
            return '元'
    
    def discover_db_schema(self) -> Dict[str, List[str]]:
        """
        从数据库自动发现Schema
        
        Returns:
            {表名: [字段名列表], ...}
        """
        if self._db_schema is not None:
            return self._db_schema
        
        config = self.load_config()
        excluded_tables = set(config.get('excluded_tables', []))
        excluded_fields = set(config.get('excluded_fields', []))
        period_fields = set(config.get('period_fields', []))
        
        self._db_schema = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                if table in excluded_tables:
                    continue
                
                # 获取表的字段
                cursor.execute(f"PRAGMA table_info({table})")
                fields = []
                for row in cursor.fetchall():
                    field_name = row[1]
                    if field_name not in excluded_fields and field_name not in period_fields:
                        fields.append(field_name)
                
                if fields:
                    self._db_schema[table] = fields
            
            conn.close()
        except Exception as e:
            print(f"⚠️  数据库Schema发现失败: {e}")
        
        return self._db_schema
    
    def get_unconfigured_fields(self) -> Dict[str, List[str]]:
        """
        获取未配置中文别名的字段
        
        Returns:
            {表名: [未配置字段列表], ...}
        """
        if self._unconfigured_fields is not None:
            return self._unconfigured_fields
        
        config = self.load_config()
        db_schema = self.discover_db_schema()
        
        self._unconfigured_fields = {}
        
        for table_name, db_fields in db_schema.items():
            table_config = config.get('tables', {}).get(table_name, {})
            configured_fields = set(table_config.get('fields', {}).keys())
            
            unconfigured = [f for f in db_fields if f not in configured_fields]
            if unconfigured:
                self._unconfigured_fields[table_name] = unconfigured
        
        return self._unconfigured_fields
    
    def print_unconfigured_report(self):
        """打印未配置字段报告"""
        unconfigured = self.get_unconfigured_fields()
        
        if not unconfigured:
            print("✅ 所有数据库字段都已配置中文别名")
            return
        
        print("\n" + "=" * 60)
        print("⚠️  未配置中文别名的字段")
        print("=" * 60)
        
        total = 0
        for table_name, fields in unconfigured.items():
            print(f"\n【{table_name}】")
            for field in fields:
                print(f"  - {field}")
                total += 1
        
        print(f"\n共 {total} 个字段需要配置")
        print("请在 config/metrics_config.json 中添加这些字段的中文别名")
    
    def get_table_for_field(self, field_name: str) -> Optional[str]:
        """
        获取字段所属的表
        
        Args:
            field_name: 字段名
        
        Returns:
            表名或None
        """
        db_schema = self.discover_db_schema()
        for table_name, fields in db_schema.items():
            if field_name in fields:
                return table_name
        return None
    
    def validate_config(self) -> List[str]:
        """
        验证配置文件
        
        Returns:
            错误消息列表(空列表表示验证通过)
        """
        errors = []
        config = self.load_config()
        db_schema = self.discover_db_schema()
        
        # 检查配置的表是否存在于数据库
        for table_name in config.get('tables', {}).keys():
            if table_name not in db_schema:
                errors.append(f"配置的表 '{table_name}' 不存在于数据库中")
        
        # 检查配置的字段是否存在于数据库
        for table_name, table_config in config.get('tables', {}).items():
            if table_name not in db_schema:
                continue
            db_fields = set(db_schema[table_name])
            for field_name in table_config.get('fields', {}).keys():
                if field_name not in db_fields:
                    errors.append(f"配置的字段 '{table_name}.{field_name}' 不存在于数据库中")
        
        return errors
    
    def reload(self):
        """重新加载配置(清除缓存)"""
        self._config = None
        self._metrics_map = None
        self._keywords = None
        self._formulas = None
        self._db_schema = None
        self._unconfigured_fields = None


# 全局单例
_loader_instance = None

def get_metrics_loader() -> MetricsLoader:
    """获取全局MetricsLoader实例"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = MetricsLoader()
    return _loader_instance


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("MetricsLoader 测试")
    print("=" * 60)
    
    loader = MetricsLoader()
    
    # 测试配置加载
    config = loader.load_config()
    print(f"\n配置版本: {config.get('version', 'unknown')}")
    print(f"配置表数量: {len(config.get('tables', {}))}")
    
    # 测试指标映射
    metrics_map = loader.get_metrics_map()
    print(f"\n指标映射总数: {len(metrics_map)}")
    print("示例映射:")
    samples = ['货币资金', '净利润', '经营净现金流', '增值税税负率', '平均工资']
    for s in samples:
        if s in metrics_map:
            print(f"  - {s}: {metrics_map[s]}")
    
    # 测试关键词
    keywords = loader.get_keywords()
    print(f"\n关键词总数: {len(keywords)}")
    
    # 测试数据库发现
    db_schema = loader.discover_db_schema()
    print(f"\n数据库表数量: {len(db_schema)}")
    for table, fields in db_schema.items():
        print(f"  - {table}: {len(fields)} 个字段")
    
    # 测试未配置字段
    print("\n检查未配置字段...")
    loader.print_unconfigured_report()
    
    # 测试配置验证
    errors = loader.validate_config()
    if errors:
        print("\n配置验证错误:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("\n✅ 配置验证通过")
