#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置文件自动更新脚本
功能:
1. 扫描数据库，提取所有出现的税种、实体关键词
2. 调用大模型分析新增政策，识别新税种、新实体、建议的同义词
3. 将检测到的新配置追加到 tax_query_config.json
4. 生成变更报告，通知管理员审核
5. 容错处理：备份原配置、支持回滚

使用方法:
    python tools/update_tax_config.py

执行顺序:
    此脚本应在 rebuild_fts_index.py 之后运行
"""

import sqlite3
import json
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from collections import Counter

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 文件路径
DB_PATH = PROJECT_ROOT / "database" / "tax_incentives.db"
CONFIG_PATH = PROJECT_ROOT / "config" / "tax_query_config.json"
CONFIG_BACKUP_DIR = PROJECT_ROOT / "config" / "backups"
REPORT_PATH = PROJECT_ROOT / "tools" / "config_update_report.md"
LOG_PATH = PROJECT_ROOT / "tools" / "config_update.log"
FTS_REBUILD_FILE = PROJECT_ROOT / "tools" / ".fts_last_rebuild"


def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(log_line + "\n")


def check_execution_order() -> bool:
    """检查是否已运行FTS重建脚本"""
    if not FTS_REBUILD_FILE.exists():
        log("⚠️ 未检测到FTS重建记录", "WARNING")
        log("请先运行: python tools/rebuild_fts_index.py", "WARNING")
        return False
    
    # 检查FTS重建时间是否在24小时内
    try:
        with open(FTS_REBUILD_FILE, 'r') as f:
            rebuild_time = datetime.fromisoformat(f.read().strip())
        
        hours_since = (datetime.now() - rebuild_time).total_seconds() / 3600
        
        if hours_since > 24:
            log(f"⚠️ FTS上次重建于 {hours_since:.1f} 小时前，建议先重新运行 rebuild_fts_index.py", "WARNING")
            response = input("是否继续？(y/n): ").strip().lower()
            if response != 'y':
                return False
    except Exception as e:
        log(f"无法读取FTS重建时间: {e}", "WARNING")
    
    return True


def backup_config() -> Path:
    """备份当前配置文件"""
    if not CONFIG_PATH.exists():
        log("配置文件不存在，跳过备份")
        return None
    
    CONFIG_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = CONFIG_BACKUP_DIR / f"tax_query_config_{timestamp}.json"
    
    shutil.copy(CONFIG_PATH, backup_path)
    log(f"已备份配置到: {backup_path}")
    
    return backup_path


def load_current_config() -> dict:
    """加载当前配置"""
    if not CONFIG_PATH.exists():
        return {}
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config: dict):
    """保存配置"""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    log(f"已保存配置到: {CONFIG_PATH}")


def scan_database() -> dict:
    """扫描数据库，提取所有税种和关键词"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    result = {
        "tax_types": set(),
        "entity_candidates": Counter(),
        "incentive_methods": set()
    }
    
    # 1. 提取所有税种
    cursor.execute("SELECT DISTINCT tax_type FROM tax_incentives WHERE tax_type IS NOT NULL")
    for row in cursor.fetchall():
        if row[0]:
            result["tax_types"].add(row[0].strip())
    
    # 2. 提取优惠方式
    cursor.execute("SELECT DISTINCT incentive_method FROM tax_incentives WHERE incentive_method IS NOT NULL")
    for row in cursor.fetchall():
        if row[0]:
            result["incentive_methods"].add(row[0].strip())
    
    # 3. 提取实体关键词候选（从优惠项目和关键词字段）
    cursor.execute("SELECT incentive_items, keywords FROM tax_incentives")
    for row in cursor.fetchall():
        for field in row:
            if field:
                # 简单分词
                for word in field.replace('、', ' ').replace(',', ' ').replace('，', ' ').split():
                    if 2 <= len(word) <= 8:  # 合理长度的词
                        result["entity_candidates"][word] += 1
    
    conn.close()
    
    return {
        "tax_types": list(result["tax_types"]),
        "entity_candidates": [w for w, c in result["entity_candidates"].most_common(100) if c >= 2],
        "incentive_methods": list(result["incentive_methods"])
    }


def analyze_with_llm(db_scan: dict, current_config: dict) -> dict:
    """使用大模型分析新的配置项"""
    suggestions = {
        "new_tax_types": [],
        "new_entity_keywords": [],
        "new_synonyms": {}
    }
    
    # 1. 检测新税种
    current_tax_types = set(current_config.get("tax_types", []))
    for tax_type in db_scan["tax_types"]:
        if tax_type not in current_tax_types:
            suggestions["new_tax_types"].append(tax_type)
    
    # 2. 检测新实体关键词
    current_entities = set(current_config.get("core_entity_keywords", []))
    
    # 使用LLM分析高频词是否应该加入核心实体
    try:
        from modules.llm_client import call_deepseek
        
        candidates = [w for w in db_scan["entity_candidates"] if w not in current_entities][:30]
        
        if candidates:
            prompt = f"""以下是税收优惠政策数据库中的高频词汇，请判断哪些应该作为"核心实体关键词"（如企业类型、行业、优惠对象等）。

候选词汇：
{', '.join(candidates)}

当前已有的核心实体关键词：
{', '.join(current_entities)}

请只返回应该添加为核心实体的词汇（逗号分隔），如果没有则返回"无"。"""

            response = call_deepseek(prompt, max_tokens=200)
            if response and response.strip() != "无":
                new_entities = [w.strip() for w in response.split(',') if w.strip() and len(w.strip()) >= 2]
                suggestions["new_entity_keywords"] = new_entities[:10]
                
    except Exception as e:
        log(f"LLM分析失败: {e}", "WARNING")
        # 降级：使用简单规则
        common_entity_patterns = ["企业", "公司", "个人", "科技", "技术", "产业"]
        for word in db_scan["entity_candidates"][:20]:
            if any(p in word for p in common_entity_patterns) and word not in current_entities:
                suggestions["new_entity_keywords"].append(word)
                if len(suggestions["new_entity_keywords"]) >= 5:
                    break
    
    # 3. 检测可能的同义词（使用LLM）
    if suggestions["new_entity_keywords"]:
        try:
            from modules.llm_client import call_deepseek
            
            for new_entity in suggestions["new_entity_keywords"][:5]:
                prompt = f"""请为"{new_entity}"这个税务术语提供可能的同义词或相近表述（用于搜索匹配）。

例如："小微企业"的同义词包括"小型微利"、"小微"

请只返回同义词列表（逗号分隔），如果没有则返回"无"。"""

                response = call_deepseek(prompt, max_tokens=100)
                if response and response.strip() != "无":
                    synonyms = [w.strip() for w in response.split(',') if w.strip()]
                    if synonyms:
                        suggestions["new_synonyms"][new_entity] = [new_entity] + synonyms
                        
        except Exception as e:
            log(f"同义词分析失败: {e}", "WARNING")
    
    return suggestions


def generate_report(suggestions: dict, backup_path: Path) -> str:
    """生成变更报告"""
    report_lines = [
        "# 配置更新报告",
        f"",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**配置备份**: {backup_path}",
        "",
        "---",
        "",
    ]
    
    has_changes = False
    
    # 新税种
    if suggestions["new_tax_types"]:
        has_changes = True
        report_lines.append("## 新增税种")
        report_lines.append("")
        for tax in suggestions["new_tax_types"]:
            report_lines.append(f"- {tax}")
        report_lines.append("")
    
    # 新实体关键词
    if suggestions["new_entity_keywords"]:
        has_changes = True
        report_lines.append("## 新增实体关键词")
        report_lines.append("")
        for entity in suggestions["new_entity_keywords"]:
            report_lines.append(f"- {entity}")
        report_lines.append("")
    
    # 新同义词
    if suggestions["new_synonyms"]:
        has_changes = True
        report_lines.append("## 新增同义词映射")
        report_lines.append("")
        for key, values in suggestions["new_synonyms"].items():
            report_lines.append(f"- `{key}`: {values}")
        report_lines.append("")
    
    if not has_changes:
        report_lines.append("## 无需更新")
        report_lines.append("")
        report_lines.append("未检测到需要添加的新配置项。")
    
    report_lines.extend([
        "",
        "---",
        "",
        "## 下一步操作",
        "",
        "1. 审核以上变更是否合理",
        "2. 如需修改，请编辑: `config/tax_query_config.json`",
        "3. 配置将自动热更新生效",
        "",
        "> 如需回滚，请从备份目录恢复配置文件",
    ])
    
    report_content = "\n".join(report_lines)
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_content


def apply_suggestions(config: dict, suggestions: dict) -> dict:
    """将建议应用到配置"""
    updated = False
    
    # 添加新税种
    if suggestions["new_tax_types"]:
        tax_types = config.get("tax_types", [])
        for tax in suggestions["new_tax_types"]:
            if tax not in tax_types:
                tax_types.append(tax)
                updated = True
        config["tax_types"] = tax_types
    
    # 添加新实体关键词
    if suggestions["new_entity_keywords"]:
        entities = config.get("core_entity_keywords", [])
        for entity in suggestions["new_entity_keywords"]:
            if entity not in entities:
                entities.append(entity)
                updated = True
        config["core_entity_keywords"] = entities
    
    # 添加新同义词
    if suggestions["new_synonyms"]:
        synonyms = config.get("entity_synonyms", {})
        for key, values in suggestions["new_synonyms"].items():
            if key not in synonyms:
                synonyms[key] = values
                updated = True
        config["entity_synonyms"] = synonyms
    
    # 更新时间戳
    if updated:
        config["_last_updated"] = datetime.now().strftime("%Y-%m-%d")
    
    return config


def main():
    """主函数"""
    print("=" * 60)
    print("配置文件自动更新工具")
    print("=" * 60)
    
    # 1. 检查执行顺序
    if not check_execution_order():
        return 1
    
    # 2. 检查数据库
    if not DB_PATH.exists():
        log(f"❌ 数据库文件不存在: {DB_PATH}", "ERROR")
        return 1
    
    # 3. 备份配置
    backup_path = backup_config()
    
    # 4. 加载当前配置
    current_config = load_current_config()
    log(f"当前配置: {len(current_config.get('tax_types', []))} 个税种, "
        f"{len(current_config.get('core_entity_keywords', []))} 个实体关键词")
    
    # 5. 扫描数据库
    log("扫描数据库...")
    db_scan = scan_database()
    log(f"  发现 {len(db_scan['tax_types'])} 个税种")
    log(f"  发现 {len(db_scan['entity_candidates'])} 个候选实体词")
    
    # 6. 使用LLM分析
    log("使用LLM分析新配置项...")
    suggestions = analyze_with_llm(db_scan, current_config)
    
    log(f"  新税种: {len(suggestions['new_tax_types'])} 个")
    log(f"  新实体: {len(suggestions['new_entity_keywords'])} 个")
    log(f"  新同义词: {len(suggestions['new_synonyms'])} 组")
    
    # 7. 应用建议
    if any([suggestions["new_tax_types"], suggestions["new_entity_keywords"], suggestions["new_synonyms"]]):
        updated_config = apply_suggestions(current_config.copy(), suggestions)
        save_config(updated_config)
    else:
        log("无需更新配置")
    
    # 8. 生成报告
    report = generate_report(suggestions, backup_path)
    
    print("\n" + "=" * 60)
    print("配置更新报告")
    print("=" * 60)
    print(report)
    print("\n" + "=" * 60)
    print(f"报告已保存到: {REPORT_PATH}")
    print("请审核配置变更，配置将自动热更新生效")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
