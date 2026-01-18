#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
财务指标配置自动更新脚本
功能:
1. 扫描 financial.db，发现未配置别名的新字段
2. 调用大模型建议中文别名
3. 生成配置更新建议报告
4. 可选：自动追加到 metrics_config.json

使用方法:
    python tools/update_financial_config.py
"""

import sqlite3
import json
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 文件路径
DB_PATH = PROJECT_ROOT / "database" / "financial.db"
CONFIG_PATH = PROJECT_ROOT / "config" / "metrics_config.json"
CONFIG_BACKUP_DIR = PROJECT_ROOT / "config" / "backups"
REPORT_PATH = PROJECT_ROOT / "tools" / "financial_config_update_report.md"
LOG_PATH = PROJECT_ROOT / "tools" / "financial_config_update.log"


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


def load_current_config() -> dict:
    """加载当前配置"""
    if not CONFIG_PATH.exists():
        return {}
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def discover_unconfigured_fields() -> dict:
    """发现未配置别名的字段"""
    from modules.metrics_loader import MetricsLoader
    
    loader = MetricsLoader()
    unconfigured = loader.get_unconfigured_fields()
    
    return unconfigured


def suggest_aliases_with_llm(table_name: str, field_names: list) -> dict:
    """使用大模型建议中文别名"""
    suggestions = {}
    
    try:
        from modules.llm_client import call_deepseek
        
        prompt = f"""请为以下数据库字段建议中文别名（用于财务数据查询系统）。

数据库表：{table_name}
字段列表：{', '.join(field_names)}

请按以下JSON格式返回（仅返回JSON，不要其他内容）：
{{
    "字段名1": ["别名1", "别名2"],
    "字段名2": ["别名1"]
}}

注意：
- 别名应该是财务人员常用的中文术语
- 每个字段可以有多个别名
- 如果字段用途不明确，返回空列表 []
"""

        response = call_deepseek(prompt, max_tokens=500)
        
        if response:
            # 尝试解析JSON
            import re
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group())
                
    except Exception as e:
        log(f"LLM建议别名失败: {e}", "WARNING")
    
    return suggestions


def validate_config() -> list:
    """验证配置文件"""
    from modules.metrics_loader import MetricsLoader
    
    loader = MetricsLoader()
    errors = loader.validate_config()
    
    return errors


def generate_report(unconfigured: dict, suggestions: dict, backup_path: Path) -> str:
    """生成更新报告"""
    report_lines = [
        "# 财务指标配置更新报告",
        "",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**配置备份**: {backup_path}",
        "",
        "---",
        "",
    ]
    
    if not unconfigured:
        report_lines.extend([
            "## 配置完整",
            "",
            "✅ 所有数据库字段都已配置中文别名，无需更新。"
        ])
    else:
        report_lines.extend([
            "## 未配置别名的字段",
            "",
        ])
        
        total = 0
        for table_name, fields in unconfigured.items():
            report_lines.append(f"### {table_name}")
            report_lines.append("")
            
            for field in fields:
                suggested = suggestions.get(table_name, {}).get(field, [])
                if suggested:
                    report_lines.append(f"- `{field}` → 建议别名: {', '.join(suggested)}")
                else:
                    report_lines.append(f"- `{field}` → (需手动配置)")
                total += 1
            
            report_lines.append("")
        
        report_lines.append(f"共 {total} 个字段需要配置")
    
    # 添加验证结果
    errors = validate_config()
    if errors:
        report_lines.extend([
            "",
            "## 配置验证问题",
            "",
        ])
        for error in errors:
            report_lines.append(f"- ⚠️ {error}")
    
    report_lines.extend([
        "",
        "---",
        "",
        "## 下一步操作",
        "",
        "1. 审核以上建议的别名是否准确",
        "2. 手动编辑 `config/metrics_config.json` 添加别名",
        "3. 配置修改后自动热更新生效",
        "",
        "> 如需回滚，请从备份目录恢复配置文件",
    ])
    
    report_content = "\n".join(report_lines)
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_content


def main():
    """主函数"""
    print("=" * 60)
    print("财务指标配置更新工具")
    print("=" * 60)
    
    # 1. 检查数据库
    if not DB_PATH.exists():
        log(f"❌ 数据库文件不存在: {DB_PATH}", "ERROR")
        return 1
    
    # 2. 备份配置
    backup_path = backup_config()
    
    # 3. 发现未配置字段
    log("扫描数据库schema...")
    unconfigured = discover_unconfigured_fields()
    
    total_fields = sum(len(fields) for fields in unconfigured.values())
    log(f"发现 {total_fields} 个未配置别名的字段")
    
    # 4. 使用LLM建议别名
    suggestions = {}
    if unconfigured:
        log("使用LLM分析并建议别名...")
        for table_name, fields in unconfigured.items():
            if len(fields) > 0:
                table_suggestions = suggest_aliases_with_llm(table_name, fields)
                if table_suggestions:
                    suggestions[table_name] = table_suggestions
    
    # 5. 生成报告
    report = generate_report(unconfigured, suggestions, backup_path)
    
    print("\n" + "=" * 60)
    print("配置更新报告")
    print("=" * 60)
    print(report)
    print("\n" + "=" * 60)
    print(f"报告已保存到: {REPORT_PATH}")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
