#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
财务指标自动添加脚本
功能:
1. 输入指标名称（如"毛利率"、"资产负债率"）
2. 调用大模型分析并生成计算公式
3. 自动添加到 metrics_config.json
4. 可选：在 financial_metrics 表中添加预计算字段

使用方法:
    python tools/auto_add_metric.py "毛利率"
    python tools/auto_add_metric.py "资产负债率" --add-column
    python tools/auto_add_metric.py --interactive

参数:
    指标名称        要添加的指标中文名称
    --add-column   同时在数据库中添加预计算字段
    --interactive  交互模式，逐步确认
    --dry-run      仅预览，不实际修改
"""

import sqlite3
import json
import sys
import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 文件路径
DB_PATH = PROJECT_ROOT / "database" / "financial.db"
CONFIG_PATH = PROJECT_ROOT / "config" / "metrics_config.json"
CONFIG_BACKUP_DIR = PROJECT_ROOT / "config" / "backups"
LOG_PATH = PROJECT_ROOT / "tools" / "auto_add_metric.log"


def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(log_line + "\n")


def backup_config() -> Path:
    """备份当前配置文件"""
    if not CONFIG_PATH.exists():
        return None
    
    CONFIG_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = CONFIG_BACKUP_DIR / f"metrics_config_{timestamp}.json"
    shutil.copy(CONFIG_PATH, backup_path)
    log(f"已备份配置到: {backup_path}")
    return backup_path


def load_config() -> dict:
    """加载当前配置"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config: dict):
    """保存配置"""
    config["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    log(f"已保存配置")


def get_available_fields() -> dict:
    """获取数据库中可用的字段"""
    from modules.metrics_loader import MetricsLoader
    loader = MetricsLoader()
    
    config = loader.load_config()
    available = {}
    
    # 从配置获取已配置的字段及其别名
    for table_name, table_config in config.get('tables', {}).items():
        fields = table_config.get('fields', {})
        for field_name, field_config in fields.items():
            aliases = field_config.get('aliases', [])
            available[field_name] = {
                'table': table_name,
                'aliases': aliases,
                'unit': field_config.get('unit', '元')
            }
    
    return available


def analyze_metric_with_llm(metric_name: str, available_fields: dict) -> dict:
    """使用大模型分析指标并生成公式"""
    
    # 构建可用字段描述
    fields_desc = []
    for field, info in available_fields.items():
        aliases_str = ', '.join(info['aliases'][:3]) if info['aliases'] else field
        fields_desc.append(f"- {field} ({aliases_str}) [表: {info['table']}]")
    
    fields_text = '\n'.join(fields_desc[:50])  # 限制数量
    
    try:
        from modules.llm_client import call_deepseek
        
        prompt = f"""你是一个财务专家。请分析以下财务指标，并生成计算公式。

## 要分析的指标
{metric_name}

## 数据库中可用的字段
{fields_text}

## 任务
1. 分析"{metric_name}"的标准计算公式
2. 使用上述可用字段构建表达式
3. 确定数据来源表
4. 提供指标别名

## 输出格式 (JSON)
```json
{{
    "metric_name": "{metric_name}",
    "expression": "字段A / 字段B * 100",
    "source_table": "income_statements",
    "unit": "%",
    "aliases": ["{metric_name}", "别名1", "别名2"],
    "description": "指标含义说明",
    "precomputed_field": "建议的数据库字段名(snake_case)"
}}
```

注意:
- expression中使用数据库字段名(英文)
- 如果是比率类指标，结果乘以100并设置unit为"%"
- precomputed_field使用snake_case命名

请只返回JSON，不要其他内容。"""

        log(f"正在分析指标: {metric_name}")
        response = call_deepseek(prompt, max_tokens=800)
        
        if response:
            import re
            # 提取JSON
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    json_str = json_match.group()
                else:
                    log(f"无法从LLM响应中提取JSON", "ERROR")
                    return None
            
            result = json.loads(json_str)
            log(f"LLM分析完成")
            return result
            
    except ImportError:
        log("无法导入 llm_client，使用预设模板", "WARNING")
        return get_preset_formula(metric_name)
    except json.JSONDecodeError as e:
        log(f"JSON解析错误: {e}", "ERROR")
        return None
    except Exception as e:
        log(f"LLM调用失败: {e}", "ERROR")
        return get_preset_formula(metric_name)
    
    return None


def get_preset_formula(metric_name: str) -> dict:
    """预设的常用指标公式"""
    presets = {
        "毛利率": {
            "expression": "(total_revenue - cost_of_sales) / total_revenue * 100",
            "source_table": "income_statements",
            "unit": "%",
            "aliases": ["毛利率", "销售毛利率"],
            "description": "毛利润占营业收入的比例",
            "precomputed_field": "gross_profit_margin"
        },
        "净利率": {
            "expression": "net_profit / total_revenue * 100",
            "source_table": "income_statements",
            "unit": "%",
            "aliases": ["净利率", "销售净利率", "净利润率"],
            "description": "净利润占营业收入的比例",
            "precomputed_field": "net_profit_margin"
        },
        "资产负债率": {
            "expression": "total_liabilities / total_assets * 100",
            "source_table": "balance_sheets",
            "unit": "%",
            "aliases": ["资产负债率", "负债率", "债务比率"],
            "description": "总负债占总资产的比例",
            "precomputed_field": "debt_to_asset_ratio"
        },
        "流动比率": {
            "expression": "current_assets_total / current_liabilities_total",
            "source_table": "balance_sheets",
            "unit": "倍",
            "aliases": ["流动比率", "流动资产比率"],
            "description": "流动资产与流动负债的比率",
            "precomputed_field": "current_ratio"
        },
        "速动比率": {
            "expression": "(current_assets_total - inventory) / current_liabilities_total",
            "source_table": "balance_sheets",
            "unit": "倍",
            "aliases": ["速动比率", "酸性测试比率"],
            "description": "速动资产与流动负债的比率",
            "precomputed_field": "quick_ratio"
        },
        "权益乘数": {
            "expression": "total_assets / total_equity",
            "source_table": "balance_sheets",
            "unit": "倍",
            "aliases": ["权益乘数", "股东权益乘数"],
            "description": "总资产与股东权益的比率",
            "precomputed_field": "equity_multiplier"
        },
        "营业利润率": {
            "expression": "operating_profit / total_revenue * 100",
            "source_table": "income_statements",
            "unit": "%",
            "aliases": ["营业利润率", "经营利润率"],
            "description": "营业利润占营业收入的比例",
            "precomputed_field": "operating_profit_margin"
        },
        "增值税税负率": {
            "expression": "vat_payable / total_revenue * 100",
            "source_table": "vat_returns",
            "unit": "%",
            "aliases": ["增值税税负率", "增值税税负", "VAT税负"],
            "description": "增值税占营业收入的比例",
            "precomputed_field": "vat_burden_rate"
        }
    }
    
    if metric_name in presets:
        result = presets[metric_name].copy()
        result["metric_name"] = metric_name
        return result
    
    # 未找到预设，返回模板
    return {
        "metric_name": metric_name,
        "expression": "TODO: 请手动填写公式",
        "source_table": "income_statements",
        "unit": "%",
        "aliases": [metric_name],
        "description": f"{metric_name}指标",
        "precomputed_field": metric_name.replace(' ', '_').lower()
    }


def add_formula_to_config(config: dict, formula_info: dict) -> bool:
    """将公式添加到配置"""
    if 'formulas' not in config:
        config['formulas'] = {}
    
    metric_name = formula_info['metric_name']
    
    # 检查是否已存在
    if metric_name in config['formulas']:
        log(f"指标 '{metric_name}' 已存在于配置中", "WARNING")
        return False
    
    # 添加公式
    config['formulas'][metric_name] = {
        "expression": formula_info['expression'],
        "source_table": formula_info['source_table'],
        "unit": formula_info['unit'],
        "aliases": formula_info.get('aliases', [metric_name]),
        "description": formula_info.get('description', ''),
        "precomputed": formula_info.get('precomputed_field')
    }
    
    log(f"已添加公式: {metric_name}")
    return True


def add_column_to_database(formula_info: dict) -> bool:
    """在数据库中添加预计算字段"""
    field_name = formula_info.get('precomputed_field')
    if not field_name:
        log("未指定预计算字段名", "WARNING")
        return False
    
    # 预计算字段添加到 financial_metrics 表
    table_name = "financial_metrics"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        if field_name in existing_columns:
            log(f"字段 '{field_name}' 已存在于 {table_name}", "WARNING")
            conn.close()
            return False
        
        # 添加字段
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {field_name} REAL")
        conn.commit()
        conn.close()
        
        log(f"已在 {table_name} 表添加字段: {field_name}")
        return True
        
    except Exception as e:
        log(f"添加数据库字段失败: {e}", "ERROR")
        return False


def interactive_mode():
    """交互模式"""
    print("\n" + "=" * 60)
    print("财务指标自动添加工具 - 交互模式")
    print("=" * 60)
    
    metric_name = input("\n请输入要添加的指标名称: ").strip()
    if not metric_name:
        print("指标名称不能为空")
        return 1
    
    # 分析指标
    available_fields = get_available_fields()
    formula_info = analyze_metric_with_llm(metric_name, available_fields)
    
    if not formula_info:
        print("无法分析指标，请手动配置")
        return 1
    
    # 显示分析结果
    print("\n" + "-" * 40)
    print("LLM分析结果:")
    print("-" * 40)
    print(f"指标名称: {formula_info['metric_name']}")
    print(f"计算公式: {formula_info['expression']}")
    print(f"数据来源表: {formula_info['source_table']}")
    print(f"单位: {formula_info['unit']}")
    print(f"别名: {', '.join(formula_info.get('aliases', []))}")
    print(f"说明: {formula_info.get('description', '')}")
    print(f"预计算字段: {formula_info.get('precomputed_field', 'N/A')}")
    print("-" * 40)
    
    # 确认
    confirm = input("\n是否将此指标添加到配置? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return 0
    
    # 备份并添加
    backup_config()
    config = load_config()
    
    if add_formula_to_config(config, formula_info):
        save_config(config)
        print(f"\n✅ 指标 '{metric_name}' 已添加到配置")
    
    # 询问是否添加数据库字段
    add_col = input("\n是否在数据库中添加预计算字段? (y/n): ").strip().lower()
    if add_col == 'y':
        if add_column_to_database(formula_info):
            print(f"✅ 已添加数据库字段: {formula_info.get('precomputed_field')}")
        else:
            print("⚠️ 数据库字段添加失败，请手动处理")
    
    print("\n⚠️ 请审核配置是否正确，配置已自动生效")
    return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="财务指标自动添加工具")
    parser.add_argument("metric_name", nargs='?', help="要添加的指标名称")
    parser.add_argument("--add-column", action="store_true", help="同时添加数据库预计算字段")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不修改")
    args = parser.parse_args()
    
    print("=" * 60)
    print("财务指标自动添加工具")
    print("=" * 60)
    
    # 交互模式
    if args.interactive or not args.metric_name:
        return interactive_mode()
    
    metric_name = args.metric_name
    log(f"处理指标: {metric_name}")
    
    # 分析指标
    available_fields = get_available_fields()
    formula_info = analyze_metric_with_llm(metric_name, available_fields)
    
    if not formula_info:
        log("无法分析指标", "ERROR")
        return 1
    
    # 显示结果
    print("\n分析结果:")
    print(json.dumps(formula_info, ensure_ascii=False, indent=2))
    
    if args.dry_run:
        log("dry-run模式，不修改配置")
        return 0
    
    # 备份并添加
    backup_config()
    config = load_config()
    
    if add_formula_to_config(config, formula_info):
        save_config(config)
        log(f"✅ 指标 '{metric_name}' 已添加")
    
    # 添加数据库字段
    if args.add_column:
        add_column_to_database(formula_info)
    
    print("\n⚠️ 请审核配置是否正确")
    return 0


if __name__ == "__main__":
    sys.exit(main())
