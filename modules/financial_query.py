#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业财务数据查询模块
支持企业名称容错匹配、时间范围提取、指标识别和Text-to-SQL

V2.0 重构版:
- 使用 MetricsLoader 从外部配置文件加载指标映射
- 支持数据库Schema自动发现
- 更易于维护和扩展
"""

import sqlite3
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 数据库路径
DB_PATH = 'database/financial.db'


class FinancialQuery:
    """企业财务数据查询"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        # 缓存企业和别名信息
        self._companies_cache = None
        self._aliases_cache = None
        
        # === V2.0: 使用 MetricsLoader 动态加载配置 ===
        self._metrics_loader = None
        self._metrics_map = None
        self._formulas = None
    
    @property
    def metrics_loader(self):
        """延迟加载 MetricsLoader"""
        if self._metrics_loader is None:
            try:
                from modules.metrics_loader import MetricsLoader
                self._metrics_loader = MetricsLoader(db_path=self.db_path)
            except ImportError:
                print("⚠️  无法导入 MetricsLoader,使用空配置")
                self._metrics_loader = None
        return self._metrics_loader
    
    @property
    def metrics_map(self) -> Dict[str, Tuple[str, str]]:
        """获取指标映射(从外部配置加载)"""
        if self._metrics_map is None:
            if self.metrics_loader:
                self._metrics_map = self.metrics_loader.get_metrics_map()
            else:
                self._metrics_map = {}
        return self._metrics_map
    
    @property
    def formulas(self) -> Dict:
        """获取公式定义(从外部配置加载)"""
        if self._formulas is None:
            if self.metrics_loader:
                self._formulas = self.metrics_loader.get_formulas()
            else:
                self._formulas = {}
        return self._formulas
    
    def reload_config(self):
        """重新加载配置(当配置文件更新后调用)"""
        if self.metrics_loader:
            self.metrics_loader.reload()
        self._metrics_map = None
        self._formulas = None
        print("✅ 配置已重新加载")

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _load_companies(self):
        """加载企业缓存"""
        if self._companies_cache is None:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM companies')
            self._companies_cache = {row['id']: row['name'] for row in cursor.fetchall()}
            conn.close()
        return self._companies_cache
    
    def _load_aliases(self):
        """加载别名缓存"""
        if self._aliases_cache is None:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT company_id, alias FROM company_aliases')
            self._aliases_cache = {}
            for row in cursor.fetchall():
                self._aliases_cache[row['alias']] = row['company_id']
            conn.close()
        return self._aliases_cache
    
    def search(self, question: str) -> Tuple[Optional[List[Dict]], Optional[Dict], str]:
        """
        主查询入口
        
        Args:
            question: 用户问题
        
        Returns:
            (查询结果, 企业信息, 状态)
            状态: "success", "company_not_found", "no_data", "error"
        """
        # 1. 识别企业
        company = self.match_company(question)
        if not company:
            return None, None, "company_not_found"
        
        print(f"🏢 匹配企业: {company['name']} (ID: {company['id']})")
        
        # 2. 提取时间范围
        time_range = self.extract_time_range(question)
        print(f"📅 时间范围: {time_range}")
        
        # 3. 识别指标
        metrics = self.extract_metrics(question)
        print(f"📊 识别指标: {metrics}")
        
        # 4. 执行查询
        results = self.execute_query(company['id'], time_range, metrics, question)
        
        if not results:
            return None, company, "no_data"
        
        return results, company, "success"
    
    def match_company(self, question: str) -> Optional[Dict]:
        """
        企业名称容错匹配
        
        Args:
            question: 用户问题
        
        Returns:
            企业信息字典 {'id': ..., 'name': ...} 或 None
        """
        companies = self._load_companies()
        aliases = self._load_aliases()
        
        # 策略1: 从别名表精确匹配(按长度降序,优先匹配长的)
        sorted_aliases = sorted(aliases.keys(), key=len, reverse=True)
        for alias in sorted_aliases:
            if alias in question:
                company_id = aliases[alias]
                return {'id': company_id, 'name': companies.get(company_id)}
        
        # 策略2: 从企业全名匹配
        sorted_companies = sorted(companies.items(), key=lambda x: len(x[1]), reverse=True)
        for company_id, name in sorted_companies:
            if name in question:
                return {'id': company_id, 'name': name}
        
        # 策略3: 模糊匹配(去掉常见后缀)
        for company_id, name in sorted_companies:
            # 去掉后缀后匹配
            short = name.replace('有限公司', '').replace('有限责任公司', '').replace('公司', '').replace('厂', '')
            if short and len(short) >= 2 and short in question:
                return {'id': company_id, 'name': name}
        
        # 策略4: 使用DeepSeek智能识别(如果上述都失败)
        return self._extract_company_with_llm(question)
    
    def _extract_company_with_llm(self, question: str) -> Optional[Dict]:
        """使用DeepSeek提取企业名称"""
        try:
            from modules.deepseek_client import DeepSeekClient
            
            companies = self._load_companies()
            company_list = ', '.join(companies.values())
            
            deepseek = DeepSeekClient()
            prompt = f"""请从以下问题中识别企业名称,并匹配到已知企业列表。

用户问题: {question}

已知企业列表: {company_list}

要求:
1. 如果问题中提到了企业名称(可能是简称),请匹配到完整企业名称
2. 只返回匹配的完整企业名称,不要其他内容
3. 如果无法匹配,返回"无法识别"

请直接返回企业名称或"无法识别"。"""
            
            messages = [{"role": "user", "content": prompt}]
            response = deepseek.chat_completion(messages, stream=False, temperature=0.3)
            response = response.strip()
            
            if response and response != "无法识别":
                # 在企业列表中查找匹配
                for company_id, name in companies.items():
                    if response in name or name in response:
                        return {'id': company_id, 'name': name}
            
            return None
            
        except Exception as e:
            print(f"⚠️  DeepSeek企业识别失败: {e}")
            return None
    
    def extract_time_range(self, question: str) -> Dict:
        """
        提取时间范围(多时间段支持版)
        
        支持的格式:
        - 单年: "2023", "2023年", "23年"
        - 多年: "2023、2024", "2022-2024", "2022到2024年"
        - 单季度: "一季度", "Q1"
        - 多季度: "Q1、Q2", "一季度和二季度"
        - 月份: "一月", "1月"
        - 对比: "增长", "对比", "比较", "vs", "变化"
        
        Returns:
            {
                'year': 2023,              # 主年份(兼容旧逻辑)
                'years': [2023, 2024],     # 多年份列表(新)
                'quarter': 1,              # 主季度(兼容旧逻辑)
                'quarters': [1, 2],        # 多季度列表(新)
                'month': 3,                # 可选
                'is_full_year': False,     # 是否全年
                'is_comparison': True      # 是否对比分析(新)
            }
        """
        result = {}
        current_year = datetime.now().year
        
        # === 从配置加载关键词（支持热更新）===
        query_settings = {}
        if self.metrics_loader:
            config = self.metrics_loader.load_config()
            query_settings = config.get('query_settings', {})
        
        # 全期查询关键词
        all_periods_keywords = query_settings.get('all_periods_keywords', [
            "多少", "是多少", "数据", "金额", "查询", 
            "增长", "增减", "增加", "减少", 
            "变动", "改变", "变化", "趋势", "情况"
        ])
        has_all_periods_keyword = any(kw in question for kw in all_periods_keywords)
        
        # === 检测对比分析意图 ===
        comparison_keywords = query_settings.get('comparison_keywords', [
            '增长', '对比', '比较', 'vs', '变化', '趋势', '同比', '环比', '差异', '变动'
        ])
        result['is_comparison'] = any(kw in question for kw in comparison_keywords)
        
        # === 提取年份(支持多个) ===
        years = []
        has_explicit_time = False  # 标记是否有明确指定时间
        
        # 辅助函数: 将2位数年份转换为4位数
        def to_full_year(short_year: int) -> int:
            return 2000 + short_year if short_year <= 60 else 1900 + short_year
        
        # 模式1: 4位数-4位数年份范围 (如 2022-2024, 2022至2024)
        range_match = re.search(r'(\d{4})[—\-~至到](\d{4})年?', question)
        if range_match:
            start_year = int(range_match.group(1))
            end_year = int(range_match.group(2))
            if 1990 <= start_year <= 2060 and 1990 <= end_year <= 2060:
                years = list(range(start_year, end_year + 1))
                result['is_comparison'] = True
                has_explicit_time = True
        
        # 模式2: 2位数-2位数年份范围 (如 21-23 → 2021-2023)
        if not years:
            range_match_2_2 = re.search(r'(?<!\d)(\d{2})[—\-~至到](\d{2})(?!\d)', question)
            if range_match_2_2:
                start_short = int(range_match_2_2.group(1))
                end_short = int(range_match_2_2.group(2))
                start_year = to_full_year(start_short)
                end_year = to_full_year(end_short)
                if 1990 <= start_year <= 2060 and 1990 <= end_year <= 2060:
                    years = list(range(start_year, end_year + 1))
                    result['is_comparison'] = True
                    has_explicit_time = True
        
        # 模式3: 4位数-2位数年份范围 (如 2021-24 → 2021-2024)
        if not years:
            range_match_4_2 = re.search(r'(\d{4})[—\-~至到](\d{2})(?!\d)', question)
            if range_match_4_2:
                start_year = int(range_match_4_2.group(1))
                end_short = int(range_match_4_2.group(2))
                end_year = to_full_year(end_short)
                if 1990 <= start_year <= 2060 and 1990 <= end_year <= 2060:
                    years = list(range(start_year, end_year + 1))
                    result['is_comparison'] = True
                    has_explicit_time = True
        
        # 模式4: 多个四位数年份 (如 2023、2024, 2023和2024)
        if not years:
            multi_match = re.findall(r'(\d{4})年?', question)
            if multi_match:
                years = [int(y) for y in multi_match if 1990 <= int(y) <= 2060]
                years = sorted(set(years))  # 去重并排序
                has_explicit_time = bool(years)
        
        # 模式X: 两位数列表 (如 "22、23年", "21,22年")
        if not years:
            # 匹配类似 "22、23" 或 "21,22" 后面跟着 "年" 的情况
            # 先找包含分隔符的两位数串
            list_match = re.search(r'((?:\d{2}[、，,])+\d{2})年', question)
            if list_match:
                year_str = list_match.group(1)
                # 分割并提取
                parts = re.split(r'[、，,]', year_str)
                for p in parts:
                    if p.isdigit():
                        y = to_full_year(int(p))
                        if 1990 <= y <= 2060:
                            years.append(y)
                years = sorted(set(years))
                has_explicit_time = bool(years)

        # 模式5: 两位数年份+年字 (如 23年、24年 → 2023、2024)
        if not years:
            short_match = re.findall(r'(?<!\d)(\d{2})年', question)
            if short_match:
                for y in short_match:
                    yi = int(y)
                    full_year = to_full_year(yi)
                    if 1990 <= full_year <= 2060:
                        years.append(full_year)
                years = sorted(set(years))
                has_explicit_time = bool(years)
        
        # 模式6: 独立四位数字 (如 2023利润率)
        if not years:
            standalone = re.findall(r'(?<!\d)(\d{4})(?!\d)', question)
            if standalone:
                years = [int(y) for y in standalone if 1990 <= int(y) <= 2060]
                has_explicit_time = bool(years)

        # 模式7: 两位数范围 (如 "22-25" -> 2022-2025, "22-25年")
        # 必须确保不与上面的 "2022-25" 冲突
        if not years:
            # 优先匹配带'年'的: "22-25年"
            range_short_year = re.search(r'(?<!\d)(\d{2})[—\-](\d{2})年', question)
            # 或者是无单位的: "22-25"
            if not range_short_year:
                range_short_year = re.search(r'(?<!\d)(\d{2})[—\-](\d{2})(?!\d)', question)
            
            if range_short_year:
                s = int(range_short_year.group(1))
                e = int(range_short_year.group(2))
                # 简单的合法性检查: start < end, 且都在合理年份区间
                sy = to_full_year(s)
                ey = to_full_year(e)
                if 1990 <= sy <= 2060 and 1990 <= ey <= 2060 and sy <= ey:
                    years = list(range(sy, ey + 1))
                    result['is_comparison'] = True
                    has_explicit_time = True
        
        # 设置结果
        if len(years) > 1:
            result['years'] = years
            result['year'] = years[0]  # 兼容旧逻辑
            result['is_comparison'] = True
        elif len(years) == 1:
            result['year'] = years[0]
            result['years'] = years
        else:
            # 没有指定年份时的处理
            if has_all_periods_keyword:
                # 包含优先关键词时,查询所有期间的数据
                result['query_all_periods'] = True
                result['year'] = None
                result['years'] = []
                result['is_comparison'] = True  # 全期查询默认视为对比分析
                print(f"📅 检测到全期查询关键词,将查询所有期间数据")
            else:
                # 默认当前年份
                result['year'] = current_year
                result['years'] = [current_year]
        
        # === 提取季度(支持多个) ===
        cn_num = {'一': 1, '二': 2, '三': 3, '四': 4, '1': 1, '2': 2, '3': 3, '4': 4}
        quarters = []
        
        # 模式1: Q1、Q2 或 Q1和Q2
        q_matches = re.findall(r'[Qq]([1234])', question)
        if q_matches:
            quarters = [int(q) for q in q_matches]
        
        # 模式2: 一季度、二季度 等
        if not quarters:
            cn_matches = re.findall(r'第?([一二三四1234])季度?', question)
            if cn_matches:
                quarters = [cn_num.get(q, int(q) if q.isdigit() else None) for q in cn_matches]
                quarters = [q for q in quarters if q is not None]
        
        # 设置结果
        if len(quarters) > 1:
            result['quarters'] = sorted(set(quarters))
            result['quarter'] = quarters[0]  # 兼容旧逻辑
            result['is_comparison'] = True
        elif len(quarters) == 1:
            result['quarter'] = quarters[0]
            result['quarters'] = quarters
        
        # === 提取月份 ===
        cn_month = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
                    '七': 7, '八': 8, '九': 9, '十': 10, '十一': 11, '十二': 12}
        
        # 月份范围
        range_match = re.search(r'(\d{1,2})[—\-~至到](\d{1,2})月', question)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if 1 <= start <= 12 and 1 <= end <= 12:
                result['start_month'] = start
                result['end_month'] = end
        elif 'quarters' not in result and 'quarter' not in result:
            # 单月份
            month_match = re.search(r'(\d{1,2})月份?', question)
            if month_match:
                month = int(month_match.group(1))
                if 1 <= month <= 12:
                    result['month'] = month
        
        # === 判断是否全年 ===
        if '全年' in question or '年度' in question:
            result['is_full_year'] = True
        elif 'quarter' not in result and 'quarters' not in result and 'month' not in result and 'start_month' not in result:
            result['is_full_year'] = True
        
        return result
    
    def _extract_metric_name_from_question(self, question: str) -> str:
        """从问题中智能提取指标名称"""
        import re
        
        # 常见的指标模式
        metric_patterns = [
            r'的([^的]{2,8}(?:金额|总额|数量|税额|费用|收入|成本|利润))$',
            r'的([^的]{2,8}(?:金额|总额|数量|税额|费用|收入|成本|利润))',
            r'([发票采购销售进项销项]{2}(?:金额|总额|数量|税额))',
            r'((?:总|合计)?(?:金额|税额|数量))',
        ]
        
        for pattern in metric_patterns:
            match = re.search(pattern, question)
            if match:
                return match.group(1)
        
        # 回退：使用简单提取
        if '发票' in question:
            if '总金额' in question or '金额' in question:
                return '发票总金额'
            elif '税额' in question:
                return '发票税额'
            elif '数量' in question:
                return '发票数量'
        
        return '查询结果'
    
    def extract_metrics(self, question: str) -> List[str]:
        """提取用户询问的指标"""
        found_metrics = []
        
        # 合并metrics_map和formulas的所有关键词
        all_metrics = list(self.metrics_map.keys()) + list(self.formulas.keys())
        
        # 按关键词长度降序匹配(优先匹配长的)
        sorted_metrics = sorted(set(all_metrics), key=len, reverse=True)
        
        for metric_name in sorted_metrics:
            if metric_name in question:
                # 检查是否为已找到指标的子串(避免重复,如找到了'企业所得税'就不应再找'所得税')
                is_substring = False
                for existing in found_metrics:
                    if metric_name in existing:
                        is_substring = True
                        break
                
                if not is_substring:
                    found_metrics.append(metric_name)
        
        # 不再使用默认值 - 如果没找到指标，返回空列表
        # 由execute_query决定是否使用Text-to-SQL或返回无数据
        return found_metrics
    
    def execute_query(self, company_id: int, time_range: Dict, metrics: List[str], 
                       question: str = None) -> List[Dict]:
        """
        执行查询(三层策略)
        1. 预计算指标:直接从financial_metrics或原表查询
        2. 公式计算:使用公式库动态计算
        3. Text-to-SQL回退:使用DeepSeek生成SQL
        
        注意: 当问题包含复杂条件(如seller_name过滤)时,优先使用Text-to-SQL
        """
        # === 全面启用 Text-to-SQL ===
        # 所有非公式指标查询，优先使用Text-to-SQL
        try:
            from modules.text_to_sql import get_text_to_sql_engine
            engine = get_text_to_sql_engine()
            
            years = time_range.get('years', [time_range.get('year')])
            years = [y for y in years if y is not None]
            quarter = time_range.get('quarter')
            
            # 记录查询尝试
            if question:
                print(f"🤖 尝试Text-to-SQL: {question}")
                sql_results, status = engine.query(question, company_id, years, quarter)
                
                if status == "success" and sql_results:
                    results = []
                    # 从问题中智能提取指标名 (仅作为备用)
                    metric_name = metrics[0] if metrics else self._extract_metric_name_from_question(question)
                    
                    for row in sql_results:
                        year = row.get('period_year') or row.get('year')
                        # BUG FIX: Do not default to 1. If quarter is missing, it's likely Annual data.
                        qtr = row.get('period_quarter') or row.get('quarter')
                        
                        # 遍历所有字段,提取多个指标
                        excluded_fields = ('period_year', 'period_quarter', 'period_month', 
                                         'year', 'quarter', 'company_id', 'month')
                        
                        for k, v in row.items():
                            if k not in excluded_fields:
                                if isinstance(v, (int, float)) and v is not None:
                                    # 优先使用列名(别名)作为指标名
                                    current_metric = k if k != 'value' else (metrics[0] if metrics else k)
                                    
                                    results.append({
                                        'metric_name': current_metric,
                                        'year': year,
                                        'quarter': qtr,
                                        'value': v,
                                        'unit': '元' # 默认单位
                                    })
                    print(f"✅ Text-to-SQL成功: 提取到 {len(results)} 个数据点")
                    return results
                else:
                    print(f"⚠️  Text-to-SQL未返回结果或验证失败: {status}")
        except Exception as e:
            print(f"❌ Text-to-SQL执行异常: {e}")
        
        # === 以下为旧逻辑保留 (仅作为公式计算的数据源支持) ===
        # 注意: 纯指标查询不应走到这里，除非Text-to-SQL彻底失败。
        # 但按照"All-in"策略，我们主要依赖上面的块。
        # 如果Text-to-SQL失败，我们直接返回空列表不再fallback，
        # 或者仅保留公式计算部分。
        
        # 暂时返回空，或根据需要抛出错误
        return []
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        results = []
        
        for metric_name in metrics:
            # === 策略1: 检查metrics_map(预计算/原始数据) ===
            if metric_name in self.metrics_map:
                table, field = self.metrics_map[metric_name]
                
                # 检查是否为特殊item_query
                if table.startswith('__item_query__'):
                    query_name = table.replace('__item_query__', '')
                    result = self._query_item(cursor, company_id, time_range, query_name, metric_name)
                    results.extend(result)
                    continue
                
                result = self._query_direct(cursor, company_id, time_range, table, field, metric_name)
                results.extend(result)
                continue
            
            # === 策略2: 检查公式库 ===
            if metric_name in self.formulas:
                formula_info = self.formulas[metric_name]
                
                # 如果有预计算字段,优先使用预计算
                if 'precomputed' in formula_info:
                    precomputed_field = formula_info['precomputed']
                    result = self._query_direct(cursor, company_id, time_range, 
                                               'financial_metrics', precomputed_field, metric_name)
                    # 检查是否有有效数据(非NULL)
                    has_valid_data = any(r['value'] is not None for r in result) if result else False
                    if has_valid_data:
                        results.extend(result)
                        print(f"📊 使用预计算字段: {precomputed_field}")
                        continue
                    else:
                        print(f"📊 预计算字段为空,尝试公式计算")
                
                # 使用公式计算
                result = self._calculate_with_formula(cursor, company_id, time_range, 
                                                     metric_name, formula_info)
                if result:
                    results.extend(result)
                    print(f"🧮 使用公式计算: {metric_name}")
                continue
            
            # === 策略3: Text-to-SQL回退 ===
            # 当指标未配置时,使用LLM动态生成SQL
            print(f"🤖 尝试Text-to-SQL: {metric_name}")
            try:
                from modules.text_to_sql import get_text_to_sql_engine
                engine = get_text_to_sql_engine()
                
                # 构建原始问题
                years = time_range.get('years', [time_range.get('year')])
                years = [y for y in years if y is not None]
                quarter = time_range.get('quarter')
                
                # 使用指标名作为问题
                sql_results, status = engine.query(metric_name, company_id, years, quarter)
                
                if status == "success" and sql_results:
                    # 转换结果格式
                    for row in sql_results:
                        # 尝试提取标准字段
                        year = row.get('period_year') or row.get('year')
                        qtr = row.get('period_quarter') or row.get('quarter') or row.get('period_month') or 1
                        value = None
                        # 查找第一个数值字段作为value
                        for k, v in row.items():
                            if k not in ('period_year', 'period_quarter', 'period_month', 'year', 'quarter', 'company_id'):
                                if isinstance(v, (int, float)) and v is not None:
                                    value = v
                                    break
                        
                        if year and value is not None:
                            results.append({
                                'metric_name': metric_name,
                                'year': year,
                                'quarter': qtr,
                                'value': value,
                                'unit': '元'
                            })
                    print(f"✅ Text-to-SQL成功: {len(sql_results)} 条记录")
                else:
                    print(f"⚠️  Text-to-SQL无结果: {status}")
            except Exception as e:
                print(f"⚠️  Text-to-SQL失败: {e}")
        
        conn.close()
        return results
    
    def _query_direct(self, cursor, company_id: int, time_range: Dict, 
                     table: str, field: str, metric_name: str) -> List[Dict]:
        """直接查询预计算或原始数据(支持多时间段)"""
        results = []
        
        conditions = [f"company_id = {company_id}"]
        
        # === 检查是否为全期查询 ===
        query_all = time_range.get('query_all_periods', False)
        
        if not query_all:
            # === 处理年份(支持多年) ===
            years = time_range.get('years', [time_range.get('year')])
            # 过滤掉None值
            years = [y for y in years if y is not None]
            if len(years) > 1:
                # 多年份查询
                years_str = ','.join(str(y) for y in years)
                conditions.append(f"period_year IN ({years_str})")
            elif years:
                conditions.append(f"period_year = {years[0]}")
            
            # === 处理季度(支持多季度) ===
            quarters = time_range.get('quarters', [time_range.get('quarter')] if time_range.get('quarter') else None)
            if quarters and len(quarters) > 1:
                # 多季度查询
                quarters_str = ','.join(str(q) for q in quarters)
                conditions.append(f"period_quarter IN ({quarters_str})")
            elif quarters and quarters[0]:
                conditions.append(f"period_quarter = {quarters[0]}")
            elif 'month' in time_range:
                conditions.append(f"period_month = {time_range['month']}")
            elif 'start_month' in time_range and 'end_month' in time_range:
                # 月份范围需要特殊处理
                if table == 'income_statements':
                    result = self._query_month_range(
                        cursor, company_id, time_range['year'],
                        time_range['start_month'], time_range['end_month'],
                        field, metric_name
                    )
                    if result:
                        return [result]
                    return []
        # 全期查询时不添加年份/季度条件,查询该企业所有存在的数据
        
        where_clause = ' AND '.join(conditions)
        
        # 判断是否需要聚合(对流量型数据进行求和,如税额、收入等)
        # 资产负债表等存量数据不需要求和(通常取期末值)
        # 从配置加载（支持热更新）
        aggregation_tables = ['income_statements', 'tax_reports', 'tax_returns_income', 
                              'vat_returns', 'cash_flow_statements', 'tax_return_stamp_items']
        if self.metrics_loader:
            config = self.metrics_loader.load_config()
            query_settings = config.get('query_settings', {})
            aggregation_tables = query_settings.get('aggregation_tables', aggregation_tables)
        should_aggregate = table in aggregation_tables
        
        # 构建查询语句
        if should_aggregate:
            query = f"""
                SELECT period_year, period_quarter, SUM({field}) as value
                FROM {table}
                WHERE {where_clause}
                GROUP BY period_year, period_quarter
                ORDER BY period_year, period_quarter
            """
        else:
            query = f"""
                SELECT period_year, period_quarter, {field} as value
                FROM {table}
                WHERE {where_clause}
                ORDER BY period_year, period_quarter
            """
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                results.append({
                    'metric_name': metric_name,
                    'year': row['period_year'],
                    'quarter': row['period_quarter'],
                    'value': row['value'],
                    'unit': self._get_unit(metric_name)
                })
        except Exception as e:
            print(f"⚠️  查询错误 ({metric_name}): {e}")
        
        return results
    
    def _query_item(self, cursor, company_id: int, time_range: Dict,
                   query_name: str, metric_name: str) -> List[Dict]:
        """查询item_query类型(key-value结构的表,如tax_return_income_items)"""
        results = []
        
        # 获取item_query配置
        if self.metrics_loader:
            item_queries = self.metrics_loader.get_item_queries()
        else:
            return results
        
        if query_name not in item_queries:
            print(f"⚠️  未找到item_query配置: {query_name}")
            return results
        
        config = item_queries[query_name]
        table = config.get('table')
        join_table = config.get('join_table')
        join_condition = config.get('join_condition')
        item_name_field = config.get('item_name_field')
        item_name_value = config.get('item_name_value')
        filter_field = config.get('filter_field')  # 新增:条件过滤字段
        filter_value = config.get('filter_value')  # 新增:条件过滤值
        value_field = config.get('value_field', 'amount')
        aggregate = config.get('aggregate', 'SUM')  # 新增:聚合函数(SUM/COUNT)
        company_field = config.get('company_field')
        year_field = config.get('year_field')
        quarter_field = config.get('quarter_field')
        month_field = config.get('month_field')  # 支持月度表(如vat_returns)
        unit = config.get('unit', '元')
        
        # 确定时间粒度字段(优先季度,其次月份)
        period_field = quarter_field or month_field
        
        # 构建条件
        conditions = [f"{company_field} = {company_id}"]
        
        # 处理年份
        years = time_range.get('years', [time_range.get('year')])
        years = [y for y in years if y is not None]
        if years:
            if len(years) > 1:
                years_str = ','.join(str(y) for y in years)
                conditions.append(f"{year_field} IN ({years_str})")
            else:
                conditions.append(f"{year_field} = {years[0]}")
        
        # 处理季度(如果有季度字段且查询中指定了季度)
        if quarter_field:
            quarters = time_range.get('quarters', [time_range.get('quarter')] if time_range.get('quarter') else None)
            if quarters and quarters[0]:
                if len(quarters) > 1:
                    quarters_str = ','.join(str(q) for q in quarters)
                    conditions.append(f"{quarter_field} IN ({quarters_str})")
                else:
                    conditions.append(f"{quarter_field} = {quarters[0]}")
        
        # 处理item_name过滤(如果适用)
        if item_name_field and item_name_value:
            conditions.append(f"{table}.{item_name_field} = '{item_name_value}'")
        
        # 处理filter条件过滤(如发票类型)
        if filter_field and filter_value:
            conditions.append(f"{filter_field} = '{filter_value}'")
        
        where_clause = ' AND '.join(conditions)
        
        # 构建聚合表达式
        if aggregate == 'COUNT':
            agg_expr = f"COUNT({value_field})"
        else:
            agg_expr = f"SUM({value_field})"
        
        # 构建查询
        if join_table and join_condition:
            # 需要JOIN
            if period_field:
                # 有时间粒度字段(季度或月度)
                query = f"""
                    SELECT {year_field} as period_year, {period_field} as period_quarter, 
                           {agg_expr} as value
                    FROM {table}
                    JOIN {join_table} ON {join_condition}
                    WHERE {where_clause}
                    GROUP BY {year_field}, {period_field}
                    ORDER BY {year_field}, {period_field}
                """
            else:
                # 只按年度汇总
                query = f"""
                    SELECT {year_field} as period_year, 1 as period_quarter, 
                           {agg_expr} as value
                    FROM {table}
                    JOIN {join_table} ON {join_condition}
                    WHERE {where_clause}
                    GROUP BY {year_field}
                    ORDER BY {year_field}
                """
        else:
            # 无需JOIN(如invoices表)
            if period_field:
                query = f"""
                    SELECT {year_field} as period_year, {period_field} as period_quarter, 
                           {agg_expr} as value
                    FROM {table}
                    WHERE {where_clause}
                    GROUP BY {year_field}, {period_field}
                    ORDER BY {year_field}, {period_field}
                """
            else:
                query = f"""
                    SELECT {year_field} as period_year, 1 as period_quarter, 
                           {agg_expr} as value
                    FROM {table}
                    WHERE {where_clause}
                    GROUP BY {year_field}
                    ORDER BY {year_field}
                """
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                results.append({
                    'metric_name': metric_name,
                    'year': row['period_year'],
                    'quarter': row['period_quarter'],
                    'value': row['value'],
                    'unit': unit
                })
            
            print(f"📊 item_query查询成功: {query_name}, 结果数: {len(results)}")
        except Exception as e:
            print(f"⚠️  item_query查询错误 ({query_name}): {e}")
        
        return results
    
    def _calculate_with_formula(self, cursor, company_id: int, time_range: Dict,
                                metric_name: str, formula_info: Dict) -> List[Dict]:
        """使用公式库计算指标(支持多时间段)"""
        results = []
        
        formula = formula_info['formula']
        table = formula_info['table']
        unit = formula_info['unit']
        
        conditions = [f"company_id = {company_id}"]
        
        # === 检查是否为全期查询 ===
        query_all = time_range.get('query_all_periods', False)
        
        if not query_all:
            # === 处理年份(支持多年) ===
            years = time_range.get('years', [time_range.get('year')])
            # 过滤掉None值
            years = [y for y in years if y is not None]
            if len(years) > 1:
                years_str = ','.join(str(y) for y in years)
                conditions.append(f"period_year IN ({years_str})")
            elif years:
                conditions.append(f"period_year = {years[0]}")
            
            # === 处理季度(支持多季度) ===
            quarters = time_range.get('quarters', [time_range.get('quarter')] if time_range.get('quarter') else None)
            if quarters and len(quarters) > 1:
                quarters_str = ','.join(str(q) for q in quarters)
                conditions.append(f"period_quarter IN ({quarters_str})")
            elif quarters and quarters[0]:
                conditions.append(f"period_quarter = {quarters[0]}")
        
        where_clause = ' AND '.join(conditions)
        
        query = f"""
            SELECT period_year, period_quarter, {formula} as value
            FROM {table}
            WHERE {where_clause}
            ORDER BY period_year, period_quarter
        """
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                results.append({
                    'metric_name': metric_name,
                    'year': row['period_year'],
                    'quarter': row['period_quarter'],
                    'value': row['value'],
                    'unit': unit
                })
        except Exception as e:
            print(f"⚠️  公式计算错误 ({metric_name}): {e}")
        
        return results
    
    def _query_month_range(self, cursor, company_id: int, year: int, 
                           start_month: int, end_month: int,
                           field: str, metric_name: str) -> Optional[Dict]:
        """查询月份范围的汇总数据"""
        # 对于需要汇总的字段(如收入),计算总和
        # 注意:实际数据可能按季度存储,需要按比例计算
        
        query = f"""
            SELECT SUM({field}) as total
            FROM income_statements
            WHERE company_id = ?
            AND period_year = ?
            AND period_quarter IN (
                SELECT DISTINCT period_quarter FROM income_statements
                WHERE company_id = ? AND period_year = ?
            )
        """
        
        try:
            # 简化处理:根据月份范围确定涉及的季度
            quarters = set()
            for month in range(start_month, end_month + 1):
                quarters.add((month - 1) // 3 + 1)
            
            cursor.execute(f"""
                SELECT SUM({field}) as total
                FROM income_statements
                WHERE company_id = ?
                AND period_year = ?
                AND period_quarter IN ({','.join(map(str, quarters))})
            """, (company_id, year))
            
            row = cursor.fetchone()
            if row and row['total']:
                return {
                    'metric_name': f"{start_month}-{end_month}月{metric_name}",
                    'year': year,
                    'quarter': f"{start_month}-{end_month}月",
                    'value': row['total'],
                    'unit': self._get_unit(metric_name)
                }
        except Exception as e:
            print(f"⚠️  月份范围查询错误: {e}")
        
        return None
    
    def _get_unit(self, metric_name: str) -> str:
        """获取指标单位"""
        if '率' in metric_name or 'ROA' in metric_name or 'ROE' in metric_name:
            return '%'
        elif '天数' in metric_name:
            return '天'
        elif '周转' in metric_name and '天' not in metric_name:
            return '次/年'
        elif '比率' in metric_name or '倍数' in metric_name:
            return '倍'
        else:
            return '元'
    
    def calculate_comparison(self, results: List[Dict], time_range: Dict) -> Dict:
        """
        计算对比分析结果
        
        Args:
            results: 查询结果列表
            time_range: 时间范围(包含is_comparison标志)
        
        Returns:
            {
                'has_comparison': True,
                'comparisons': [
                    {
                        'metric': '利润率',
                        'periods': [(2023, Q1, 10%), (2024, Q1, 12%)],
                        'change': 2,          # 变化额
                        'change_pct': 20,     # 变化百分比
                        'trend': 'up'         # up/down/stable
                    }
                ]
            }
        """
        if not time_range.get('is_comparison') or len(results) < 2:
            return {'has_comparison': False, 'comparisons': []}
        
        # 按指标名称分组
        metrics_data = {}
        for r in results:
            metric = r['metric_name']
            if metric not in metrics_data:
                metrics_data[metric] = []
            metrics_data[metric].append(r)
        
        comparisons = []
        for metric, data in metrics_data.items():
            if len(data) < 2:
                continue
            
            # 按年份和季度排序
            data.sort(key=lambda x: (x['year'], x.get('quarter', 0)))
            
            # 过滤掉None值
            valid_data = [d for d in data if d['value'] is not None]
            if len(valid_data) < 2:
                continue
            
            # 计算第一个和最后一个时间点的差异
            first = valid_data[0]
            last = valid_data[-1]
            
            first_val = first['value']
            last_val = last['value']
            
            # 计算变化额和百分比
            change = last_val - first_val
            change_pct = (change / first_val * 100) if first_val and first_val != 0 else None
            
            # 判断趋势
            if change_pct is not None:
                if change_pct > 1:
                    trend = 'up'
                elif change_pct < -1:
                    trend = 'down'
                else:
                    trend = 'stable'
            else:
                trend = 'unknown'
            
            comparisons.append({
                'metric': metric,
                'periods': [(d['year'], d.get('quarter'), d['value'], d['unit']) for d in valid_data],
                'first_period': (first['year'], first.get('quarter')),
                'last_period': (last['year'], last.get('quarter')),
                'first_value': first_val,
                'last_value': last_val,
                'change': change,
                'change_pct': change_pct,
                'trend': trend,
                'unit': first['unit']
            })
        
        return {
            'has_comparison': len(comparisons) > 0,
            'comparisons': comparisons
        }
    
    def format_comparison(self, comparison_result: Dict, company: Dict) -> str:
        """格式化对比分析结果（表格格式）"""
        if not comparison_result.get('has_comparison'):
            return ""
        
        comparisons = comparison_result['comparisons']
        output = f"\n\n📈 **{company['name']} 对比分析**：\n\n"
        
        # 判断是否需要表格（期间数 >= 4 或指标数 > 1）
        total_periods = sum(len(c['periods']) for c in comparisons)
        use_table = total_periods >= 4 or len(comparisons) > 1
        
        if use_table:
            # 表格格式
            output += "| 指标 | 起始值 | 最终值 | 变化额 | 增长率 | 趋势 |\n"
            output += "|------|--------|--------|--------|--------|------|\n"
            
            for comp in comparisons:
                metric = comp['metric']
                first = comp['first_period']
                last = comp['last_period']
                first_val = comp['first_value']
                last_val = comp['last_value']
                change = comp['change']
                change_pct = comp['change_pct']
                trend = comp['trend']
                unit = comp['unit']
                
                first_str = f"{first[0]}年" + (f"Q{first[1]}" if first[1] else "")
                last_str = f"{last[0]}年" + (f"Q{last[1]}" if last[1] else "")
                
                # 格式化数值
                first_val_str = self._format_value(first_val, unit)
                last_val_str = self._format_value(last_val, unit)
                # 格式化变化额（带正负号）
                if change is not None and unit == '元':
                    if abs(change) >= 100000000:
                        change_str = f"{change/100000000:+.2f}亿"
                    elif abs(change) >= 10000:
                        change_str = f"{change/10000:+.2f}万"
                    else:
                        change_str = f"{change:+.2f}"
                elif change is not None:
                    change_str = f"{change:+.2f}{unit}"
                else:
                    change_str = "-"
                pct_str = f"{change_pct:+.1f}%" if change_pct is not None else "-"
                
                # 趋势图标
                trend_icon = "📈" if trend == 'up' else ("📉" if trend == 'down' else "➡️")
                
                output += f"| {metric} | {first_str}: {first_val_str} | {last_str}: {last_val_str} | {change_str} | {pct_str} | {trend_icon} |\n"
            
            # 如果有详细数据，添加明细表格（含环比增长）
            if any(len(c['periods']) > 2 for c in comparisons):
                output += "\n**各期详细数据**：\n\n"
                for comp in comparisons:
                    if len(comp['periods']) > 2:
                        output += f"*{comp['metric']}*：\n"
                        output += "| 期间 | 数值 | 增长额 | 增长率 |\n|------|------|--------|--------|\n"
                        prev_val = None
                        for period in comp['periods']:
                            year, q, val, u = period
                            q_str = f"Q{q}" if q else ""
                            val_str = self._format_value(val, u)
                            
                            # 计算环比增长（与上一期对比）
                            if prev_val is not None and prev_val != 0 and val is not None:
                                growth = val - prev_val
                                growth_pct = (growth / abs(prev_val)) * 100
                                growth_str = self._format_change(growth, u)
                                pct_str = f"{growth_pct:+.2f}%"
                            else:
                                growth_str = "n/a"
                                pct_str = "n/a"
                            
                            output += f"| {year}年{q_str} | {val_str} | {growth_str} | {pct_str} |\n"
                            prev_val = val
                        output += "\n"
        else:
            # 列表格式（原有逻辑，用于简单对比）
            for comp in comparisons:
                metric = comp['metric']
                first = comp['first_period']
                last = comp['last_period']
                change = comp['change']
                change_pct = comp['change_pct']
                trend = comp['trend']
                unit = comp['unit']
                
                first_str = f"{first[0]}年" + (f"Q{first[1]}" if first[1] else "")
                last_str = f"{last[0]}年" + (f"Q{last[1]}" if last[1] else "")
                
                trend_icon = "📈" if trend == 'up' else ("📉" if trend == 'down' else "➡️")
                
                output += f"- **{metric}**: {first_str} → {last_str}\n"
                output += f"  - 变化额: {change:+.2f}{unit} {trend_icon}\n"
                if change_pct is not None:
                    output += f"  - 增长率: {change_pct:+.2f}%\n"
        
        return output
    
    def format_results(self, results: List[Dict], company: Dict) -> str:
        """
        格式化查询结果
        当指标 > 1 或期间 >= 4 时使用表格格式
        """
        if not results:
            return f"📊 {company['name']} 暂无相关数据"
        
        # 统计不同指标和期间
        metrics = set(r['metric_name'] for r in results)
        periods = set((r['year'], r.get('quarter')) for r in results)
        
        # 判断是否使用表格格式
        use_table = len(metrics) > 1 or len(periods) >= 4
        
        output = f"📊 **{company['name']}** 财务数据：\n\n"
        
        if use_table:
            # 表格格式
            output += self._format_as_table(results, metrics, periods)
        else:
            # 列表格式（原有逻辑）
            output += self._format_as_list(results)
        
        return output
    
    def _format_value(self, value, unit: str) -> str:
        """格式化数值"""
        if value is None:
            return "暂无数据"
        
        if unit == '元':
            if abs(value) >= 100000000:
                return f"{value/100000000:.2f}亿"
            elif abs(value) >= 10000:
                return f"{value/10000:.2f}万"
            else:
                return f"{value:.2f}"
        else:
            return f"{value:.2f}{unit}"
    
    def _format_change(self, change, unit: str) -> str:
        """格式化增长额（带正负号）"""
        if change is None:
            return "n/a"
        
        if unit == '元':
            if abs(change) >= 100000000:
                return f"{change/100000000:+.2f}亿"
            elif abs(change) >= 10000:
                return f"{change/10000:+.2f}万"
            else:
                return f"{change:+.2f}"
        else:
            return f"{change:+.2f}{unit}"
    
    def _format_as_table(self, results: List[Dict], metrics: set, periods: set) -> str:
        """生成表格格式输出"""
        # 按期间排序
        sorted_periods = sorted(periods, key=lambda x: (x[0], x[1] or 0))
        sorted_metrics = sorted(metrics)
        
        # 构建数据矩阵
        data_matrix = {}
        units = {}
        for r in results:
            period_key = (r['year'], r.get('quarter'))
            metric = r['metric_name']
            data_matrix[(period_key, metric)] = r['value']
            units[metric] = r['unit']
        
        # 生成表头
        header = "| 期间 |"
        separator = "|------|"
        for metric in sorted_metrics:
            header += f" {metric} |"
            separator += "--------|"
        output = header + "\n" + separator + "\n"
        
        # 生成数据行
        for period in sorted_periods:
            year, quarter = period
            period_str = f"{year}年" + (f"Q{quarter}" if quarter else "")
            row = f"| {period_str} |"
            
            for metric in sorted_metrics:
                value = data_matrix.get((period, metric))
                unit = units.get(metric, '元')
                formatted = self._format_value(value, unit)
                row += f" {formatted} |"
            
            output += row + "\n"
        
        return output
    
    def _format_as_list(self, results: List[Dict]) -> str:
        """生成列表格式输出（原有逻辑）"""
        output = ""
        for result in results:
            value = result['value']
            unit = result['unit']
            
            # 格式化数值
            if unit == '元' and value:
                if abs(value) >= 100000000:
                    formatted_value = f"{value/100000000:.2f}亿元"
                elif abs(value) >= 10000:
                    formatted_value = f"{value/10000:.2f}万元"
                else:
                    formatted_value = f"{value:.2f}元"
            elif value is not None:
                formatted_value = f"{value:.2f}{unit}"
            else:
                formatted_value = "暂无数据"
            
            period = f"{result['year']}年"
            if result.get('quarter'):
                if isinstance(result['quarter'], int):
                    period += f"Q{result['quarter']}"
                else:
                    period += str(result['quarter'])
            
            output += f"- **{result['metric_name']}** ({period}): {formatted_value}\n"
        
        return output


# 测试代码
if __name__ == '__main__':
    q = FinancialQuery()
    
    test_questions = [
        "ABC公司2023年销售额是多少",
        "123制造厂2024年第一季度毛利率",
        "太空科技2023年全年净利润",
        "环球机械2023年存货周转率",
    ]
    
    print("=" * 60)
    print("测试财务查询模块")
    print("=" * 60)
    
    for question in test_questions:
        print(f"\n问题: {question}")
        results, company, status = q.search(question)
        
        if status == "company_not_found":
            print("❌ 未找到企业")
        elif status == "no_data":
            print(f"📊 {company['name']} 暂无相关数据")
        else:
            print(q.format_results(results, company))
