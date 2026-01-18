#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
财务指标别名自动生成脚本
功能:
1. 扫描数据库，发现未配置别名的字段
2. 调用大模型(DeepSeek)为每个字段建议中文别名
3. 自动更新 metrics_config.json
4. 生成变更报告供管理员审核

使用方法:
    python tools/auto_generate_aliases.py [--dry-run] [--table TABLE_NAME]
    
参数:
    --dry-run     只生成报告，不实际修改配置
    --table       只处理指定表
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
REPORT_PATH = PROJECT_ROOT / "tools" / "alias_generation_report.md"
LOG_PATH = PROJECT_ROOT / "tools" / "alias_generation.log"


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
        log("配置文件不存在，跳过备份")
        return None
    
    CONFIG_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = CONFIG_BACKUP_DIR / f"metrics_config_{timestamp}.json"
    
    shutil.copy(CONFIG_PATH, backup_path)
    log(f"已备份配置到: {backup_path}")
    
    return backup_path


def load_config() -> dict:
    """加载当前配置"""
    if not CONFIG_PATH.exists():
        return {"tables": {}, "version": "2.1.0"}
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config: dict):
    """保存配置"""
    config["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    log(f"已保存配置到: {CONFIG_PATH}")


def get_unconfigured_fields(config: dict, target_table: str = None) -> dict:
    """获取未配置别名的字段"""
    from modules.metrics_loader import MetricsLoader
    
    loader = MetricsLoader()
    all_unconfigured = loader.get_unconfigured_fields()
    
    if target_table:
        return {target_table: all_unconfigured.get(target_table, [])}
    
    return all_unconfigured


def get_table_description(table_name: str) -> str:
    """获取表描述（用于LLM上下文）"""
    descriptions = {
        "income_statements": "利润表，包含营业收入、成本、费用、利润等",
        "balance_sheets": "资产负债表，包含资产、负债、所有者权益等",
        "cash_flow_statements": "现金流量表，包含经营/投资/筹资活动现金流",
        "financial_metrics": "预计算的财务指标，包含各类比率和周转率",
        "invoices": "发票数据，包含进项和销项发票",
        "tax_returns_income": "企业所得税年度申报数据",
        "tax_return_income_items": "企业所得税申报明细项目",
        "vat_returns": "增值税月度申报数据",
        "vat_return_items": "增值税申报明细项目",
        "tax_return_stamp_items": "印花税明细项目",
        "payroll_summaries": "薪酬汇总数据",
        "account_balances": "科目余额数据"
    }
    return descriptions.get(table_name, f"{table_name}表")


def generate_aliases_with_llm(table_name: str, field_names: list) -> dict:
    """使用大模型生成中文别名"""
    if not field_names:
        return {}
    
    suggestions = {}
    
    try:
        from modules.llm_client import call_deepseek
        
        table_desc = get_table_description(table_name)
        
        prompt = f"""你是一个财务数据专家。请为以下数据库字段生成中文别名，用于财务数据查询系统。

## 数据库表
- 表名: {table_name}
- 表描述: {table_desc}

## 需要配置别名的字段
{chr(10).join(f'- {field}' for field in field_names)}

## 要求
1. 每个字段提供1-3个中文别名
2. 别名应该是财务人员常用的专业术语
3. 别名应该简洁、准确
4. 如果字段用途不明确，可以根据字段名推断

## 输出格式 (JSON)
```json
{{
    "字段名1": {{
        "aliases": ["别名1", "别名2"],
        "unit": "元",
        "category": "分类"
    }},
    "字段名2": {{
        "aliases": ["别名1"],
        "unit": "%",
        "category": "比率"
    }}
}}
```

unit可选值: 元, %, 次/年, 天, 倍, 个, 张
category可选值: 收入, 成本, 费用, 利润, 资产, 负债, 权益, 税费, 现金流, 比率, 其他

请只返回JSON，不要其他内容。"""

        log(f"正在为 {table_name} 的 {len(field_names)} 个字段生成别名...")
        
        response = call_deepseek(prompt, max_tokens=1500)
        
        if response:
            # 提取JSON
            import re
            # 尝试匹配```json...```块
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接匹配JSON对象
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    json_str = json_match.group()
                else:
                    log(f"无法从LLM响应中提取JSON: {response[:200]}", "WARNING")
                    return {}
            
            suggestions = json.loads(json_str)
            log(f"成功生成 {len(suggestions)} 个字段的别名")
            
    except json.JSONDecodeError as e:
        log(f"JSON解析错误: {e}", "ERROR")
    except ImportError:
        log("无法导入 llm_client，使用回退逻辑", "WARNING")
        # 回退：基于字段名生成简单别名
        for field in field_names:
            suggestions[field] = {
                "aliases": [field.replace('_', '')],
                "unit": "元",
                "category": "其他"
            }
    except Exception as e:
        log(f"LLM调用失败: {e}", "ERROR")
    
    return suggestions


def merge_suggestions_to_config(config: dict, table_name: str, suggestions: dict) -> int:
    """将建议合并到配置"""
    if table_name not in config.get("tables", {}):
        config.setdefault("tables", {})[table_name] = {"description": get_table_description(table_name), "fields": {}}
    
    table_config = config["tables"][table_name]
    if "fields" not in table_config:
        table_config["fields"] = {}
    
    added_count = 0
    for field_name, field_config in suggestions.items():
        if field_name not in table_config["fields"]:
            table_config["fields"][field_name] = field_config
            added_count += 1
    
    return added_count


def generate_report(unconfigured: dict, suggestions: dict, added_count: int, 
                   backup_path: Path, dry_run: bool) -> str:
    """生成报告"""
    report_lines = [
        "# 指标别名自动生成报告",
        "",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**模式**: {'仅预览（未修改配置）' if dry_run else '已更新配置'}",
        f"**配置备份**: {backup_path}" if backup_path else "",
        "",
        "---",
        "",
    ]
    
    if not unconfigured or all(len(fields) == 0 for fields in unconfigured.values()):
        report_lines.extend([
            "## 配置完整",
            "",
            "✅ 所有数据库字段都已配置中文别名，无需更新。"
        ])
    else:
        report_lines.extend([
            f"## 处理结果",
            "",
            f"- 扫描未配置字段: {sum(len(f) for f in unconfigured.values())} 个",
            f"- LLM生成别名: {sum(len(s) for s in suggestions.values())} 个",
            f"- 新增配置: {added_count} 个",
            "",
            "## 生成的别名详情",
            "",
        ])
        
        for table_name, table_suggestions in suggestions.items():
            if table_suggestions:
                report_lines.append(f"### {table_name}")
                report_lines.append("")
                report_lines.append("| 字段名 | 别名 | 单位 | 分类 |")
                report_lines.append("|--------|------|------|------|")
                
                for field_name, field_config in table_suggestions.items():
                    aliases = ", ".join(field_config.get("aliases", []))
                    unit = field_config.get("unit", "元")
                    category = field_config.get("category", "其他")
                    report_lines.append(f"| `{field_name}` | {aliases} | {unit} | {category} |")
                
                report_lines.append("")
    
    report_lines.extend([
        "---",
        "",
        "## 下一步操作",
        "",
    ])
    
    if dry_run:
        report_lines.extend([
            "1. 审核以上生成的别名",
            "2. 确认无误后，运行不带 `--dry-run` 参数的命令更新配置",
            "3. 配置更新后自动生效",
        ])
    else:
        report_lines.extend([
            "1. ⚠️ **请审核生成的别名是否准确**",
            "2. 如需调整，编辑 `config/metrics_config.json`",
            "3. 配置修改后自动热更新生效",
            "4. 如需回滚，从备份目录恢复配置文件",
        ])
    
    report_content = "\n".join(report_lines)
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_content


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="财务指标别名自动生成工具")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不修改配置")
    parser.add_argument("--table", type=str, help="只处理指定表")
    args = parser.parse_args()
    
    print("=" * 60)
    print("财务指标别名自动生成工具")
    print("=" * 60)
    
    if args.dry_run:
        log("模式: 仅预览（dry-run）")
    
    # 1. 检查数据库
    if not DB_PATH.exists():
        log(f"❌ 数据库文件不存在: {DB_PATH}", "ERROR")
        return 1
    
    # 2. 加载配置
    config = load_config()
    log(f"当前配置版本: {config.get('version', 'unknown')}")
    
    # 3. 获取未配置字段
    log("扫描数据库...")
    unconfigured = get_unconfigured_fields(config, args.table)
    
    total_fields = sum(len(fields) for fields in unconfigured.values())
    log(f"发现 {total_fields} 个未配置别名的字段")
    
    if total_fields == 0:
        log("✅ 所有字段都已配置，无需生成")
        return 0
    
    # 4. 备份配置（非dry-run模式）
    backup_path = None
    if not args.dry_run:
        backup_path = backup_config()
    
    # 5. 使用LLM生成别名
    all_suggestions = {}
    for table_name, fields in unconfigured.items():
        if fields:
            suggestions = generate_aliases_with_llm(table_name, fields)
            if suggestions:
                all_suggestions[table_name] = suggestions
    
    # 6. 合并到配置
    added_count = 0
    if not args.dry_run and all_suggestions:
        for table_name, suggestions in all_suggestions.items():
            added_count += merge_suggestions_to_config(config, table_name, suggestions)
        
        if added_count > 0:
            save_config(config)
            log(f"✅ 已添加 {added_count} 个字段配置")
    
    # 7. 生成报告
    report = generate_report(unconfigured, all_suggestions, added_count, backup_path, args.dry_run)
    
    print("\n" + "=" * 60)
    print("生成报告")
    print("=" * 60)
    print(report)
    print("\n" + "=" * 60)
    print(f"报告已保存到: {REPORT_PATH}")
    
    if not args.dry_run and added_count > 0:
        print("\n⚠️ 请审核生成的别名配置是否准确!")
    
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
