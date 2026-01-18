# 财务数据查询系统 - 业务维护手册

> 本手册面向财务人员和系统管理员，说明如何维护财务数据查询系统。

---

## 一、系统概述

财务数据查询系统用于查询企业财务数据，支持：

- 利润表、资产负债表、现金流量表
- 增值税、企业所得税、印花税申报数据
- 发票数据（进项/销项）
- 各类财务比率计算

---

## 二、企业选择说明

> **重要提示**：企业通过前端下拉列表选择，确保名称唯一性。
> 企业别名表为历史遗留功能，**无需维护**。

新增企业时：

1. 在 `companies` 表中添加企业信息
2. 刷新前端页面，新企业将出现在下拉列表中

---

## 三、财务数据录入

### 3.1 数据表说明

| 数据表 | 说明 | 期间粒度 |
|--------|------|----------|
| `income_statements` | 利润表 | 季度 |
| `balance_sheets` | 资产负债表 | 季度 |
| `cash_flow_statements` | 现金流量表 | 季度 |
| `vat_returns` | 增值税申报 | 月度 |
| `tax_returns_income` | 企业所得税 | 年度 |
| `invoices` | 发票数据 | 按张 |
| `financial_metrics` | 预计算指标 | 季度 |

### 3.2 录入注意事项

1. **必填字段**：company_id, period_year, period_quarter (或 period_month)
2. **金额单位**：统一使用"元"，不带单位符号
3. **期间对齐**：确保同一期间数据完整

---

## 四、指标别名配置

### 4.1 为什么需要配置别名？

用户可能用不同方式表述同一指标：

- "营业收入" = "收入" = "营收" = "总收入"

系统需要将这些表述映射到数据库字段 `total_revenue`。

### 4.2 如何添加指标别名

1. 打开配置文件：`config/metrics_config.json`
2. 找到对应数据表的 `fields` 节点
3. 添加或修改别名列表

**示例**：为"营业收入"添加新别名"销售额"

```json
"total_revenue": {
  "aliases": ["营业收入", "收入", "营收", "总收入", "销售额"],  // ← 添加新别名
  "unit": "元",
  "category": "收入"
}
```

1. 保存文件 → **自动生效**（无需重启）

---

## 五、新增财务指标

### 5.1 数据库已有字段

如果数据库表中已有该字段，只需添加别名配置即可。

### 5.2 需要计算的指标

使用公式配置：

```json
"formulas": {
  "新指标名称": {
    "expression": "field_a / field_b * 100",
    "source_table": "income_statements",
    "unit": "%",
    "aliases": ["新指标", "新指标别名"]
  }
}
```

### 5.3 需要直接添加字段

1. 修改数据库表结构，添加新字段
2. 在 `metrics_config.json` 中添加对应别名配置
3. 运行 `python tools/update_financial_config.py` 检查配置完整性

---

## 六、系统管理员维护指南

### 6.1 定期维护流程

```
步骤1: python tools/update_financial_config.py  ← 检查未配置字段
步骤2: 审核报告,手动补充别名配置
步骤3: 运行 python test_financial_query.py 验证
```

### 6.2 配置文件说明

| 文件 | 用途 | 修改频率 |
|------|------|----------|
| `config/metrics_config.json` | 指标别名、公式、查询设置 | 常用 |
| `config/schema_mappings.json` | 表名/字段值中文映射 | 较少 |
| `config/business_glossary.json` | 业务术语补充 | 较少 |

### 6.3 热更新配置

所有配置文件支持热更新：

1. 修改 JSON 文件
2. 保存
3. 下次查询自动加载新配置

**无需重启服务！**

### 6.4 配置备份与回滚

备份目录：`config/backups/`

每次运行维护脚本会自动备份。

回滚方法：

```bash
copy config\backups\metrics_config_YYYYMMDD_HHMMSS.json config\metrics_config.json
```

---

## 七、常见问题

### Q1: 用户反馈"查不到某个指标"

**排查步骤**：

1. 确认数据库中是否有该指标数据
2. 检查 `metrics_config.json` 中是否有对应别名
3. 如无，添加别名配置

### Q2: 配置修改后未生效

**排查步骤**：

1. 确认 JSON 格式正确（无语法错误）
2. 检查文件保存时间是否更新
3. 运行测试脚本验证

### Q3: 需要新增数据表

**步骤**：

1. 创建数据库表
2. 在 `metrics_config.json` 的 `tables` 下添加新表配置
3. 配置各字段的别名
4. 检查 `excluded_tables` 中是否错误排除了新表

---

## 八、配置文件快速参考

### query_settings 节点

```json
{
  "query_settings": {
    "all_periods_keywords": ["多少", "数据", "金额", ...],  // 触发全期查询
    "comparison_keywords": ["增长", "对比", "趋势", ...],   // 触发对比分析
    "aggregation_tables": ["income_statements", ...]        // 需要聚合的流量表
  }
}
```

### 字段配置模板

```json
{
  "字段名": {
    "aliases": ["别名1", "别名2"],
    "unit": "元",
    "category": "分类"
  }
}
```

### 公式配置模板

```json
{
  "指标名": {
    "expression": "计算公式",
    "source_table": "数据来源表",
    "unit": "单位",
    "precomputed": "预计算字段名(可选)"
  }
}
```

---

*本手册旨在帮助业务人员和管理员维护财务数据查询系统，确保查询准确性。*
