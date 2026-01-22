# 企业画像 (Enterprise Profile) 技术实现文档

## 1. 系统架构概述

企业画像功能旨在为用户提供企业全方位的经营状况分析，涵盖基本信息、财务状况、税务风险、研发创新等14个维度。

### 1.1 技术栈

- **前端**: React (`CompanyProfile.jsx`), Chart.js (可视化)
- **后端**: FastAPI (`routers/company_profile.py`), APScheduler (定时计算)
- **数据库**: SQLite (`financial.db`)

### 1.2 数据流向

1. **API请求**: 前端发起 `GET /api/company-profile/{id}/full` 请求。
2. **数据聚合**: 后端 `company_profile.py` 调用多个内部函数，分别查询不同的数据库表。
3. **计算与加工**: 部分指标（如增长率、集中度）在查询时进行二次计算或评分。
4. **响应返回**: 聚合后的JSON数据返回给前端进行渲染。

---

## 2. 数据来源详细说明

企业画像数据主要分为**基础数据**（Raw Data）、**计算指标**（Calculated Metrics）和**业务档案数据**（Business Profile Data）三类。

### 2.1 基础数据 (Raw Data)

此类数据直接来源于企业的财务报表和纳税申报表，通常通过ETL流程导入。

| 数据模块 | 主要来源表 | 关键字段 |
| :--- | :--- | :--- |
| **企业基本信息** | `companies` | 企业名称、信用代码、法人、注册资本、行业 |
| **股东信息** | `shareholders` | 股东名称、持股比例、股东类型 |
| **对外投资** | `investments` | 被投企业名、投资比例、投资金额 |
| **资产负债表** | `balance_sheets` | 资产总额、负债总额、所有者权益、流动资产等 |
| **利润表** | `income_statements` | 营业收入、净利润、销售费用、管理费用等 |
| **现金流量表** | `cash_flow_statements` | 经营/投资/筹资活动现金净流量 |
| **发票数据** | `invoices` | 发票类型(进/销)、金额、开票日期 |
| **纳税申报** | `tax_returns_vat`<br>`tax_returns_income` | 增值税额、所得税额 |

### 2.2 计算指标 (Calculated Metrics)

此类数据由定时任务基于基础数据计算得出，存储在 `financial_metrics` 表中，以提高查询性能。

| 指标名称 | 来源表 | 计算公式/逻辑 |
| :--- | :--- | :--- |
| **毛利率** | `income_statements` | `(营业收入 - 营业成本) / 营业收入 * 100%` |
| **净利率** | `income_statements` | `净利润 / 营业收入 * 100%` |
| **资产负债率** | `balance_sheets` | `负债总额 / 资产总额 * 100%` |
| **流动比率** | `balance_sheets` | `流动资产 / 流动负债` |
| **速动比率** | `balance_sheets` | `(流动资产 - 存货) / 流动负债` |
| **总资产周转率** | `income_s` + `balance_s` | `营业收入 / 平均资产总额` |
| **营收增长率** | `income_statements` | `(本期营收 - 上期营收) / 上期营收 * 100%` |
| **客户集中度** | `customer_analysis` | `TOP5客户销售额 / 客户总销售额 * 100%` |
| **供应商集中度** | `supplier_analysis` | `TOP5供应商采购额 / 供应商总采购额 * 100%` |

### 2.3 业务档案数据 (Business Profile Data)

此类数据描述企业的非财务特征（如研发、合规、ESG），目前通过脚本 `generate_profile_data_v2.py` 模拟生成或从外部系统同步。

| 数据模块 | 来源表 | 数据更新方式 |
| :--- | :--- | :--- |
| **资质认证** | `company_certifications` | 外部同步 / 脚本生成 |
| **人员结构** | `employee_structure` | HR系统同步 / 脚本生成 |
| **研发创新** | `rd_innovation` | 研发管理系统 / 脚本生成 |
| **跨境业务** | `cross_border_business` | 关务系统 / 脚本生成 |
| **银行关系** | `bank_relations` | 银企直连 / 手工录入 |
| **合规评估** | `compliance_summary` | 风险控制系统聚合 |
| **数字化能力** | `digital_capability` | IT审计录入 |
| **ESG指标** | `esg_indicators` | ESG报告录入 |
| **政策匹配** | `policy_eligibility` | 政策库规则匹配生成 |
| **特殊业务** | `special_business` | 业务系统同步 |

---

## 3. 数据更新方法

系统采用**定时计算**与**手动触发**相结合的数据更新机制。

### 3.1 财务指标自动计算 (Scheduled Calculation)

- **机制**: 基于APScheduler的定时任务。
- **频率**: 每日凌晨 02:00 执行。
- **执行逻辑**: 调用 `database.calculate_metrics.calculate_all_metrics()`。
    1. 遍历所有企业和已有的财务报表期间（季度/年度）。
    2. 如果存在当期及上期（用于计算增长率和平均值）的基础数据，则执行计算公式。
    3. 将计算结果写入或更新至 `financial_metrics` 表。
- **代码位置**: `server/scheduler.py`, `database/calculate_metrics.py`

### 3.2 手动触发计算 (Manual Trigger)

- **场景**: 当财务报表刚刚导入或修正后，需要立即刷新指标时使用。
- **API接口**: `POST /api/admin/metrics/recalculate`
- **参数**:
  - `company_ids`: 指定企业ID列表（可选，默认全部）。
  - `year`: 指定年份（可选，默认全部）。
- **前端入口**: 企业画像页面的 "刷新指标" 按钮。

### 3.3 业务档案数据更新 (Data Injection)

- **机制**: 目前为模拟脚本注入，生产环境应为ETL同步。
- **脚本**: `database/generate_profile_data_v2.py`
- **操作**: 运行该脚本会清空并重新生成 `company_certifications` 等10个业务档案表的数据。
- **扩展建议**: 生产环境中应由 `server/etl/sync_profile_data.py` (需开发) 定时从其它业务系统拉取数据。

---

## 4. 指标评价体系

系统对关键指标预设了评价阈值，用于在前端显示颜色标记（绿/蓝/黄/红）。

**评价逻辑位置**: `server/routers/company_profile.py -> evaluate_metric`

| 指标 | 优秀 (Green) | 良好 (Blue) | 一般 (Yellow) | 风险 (Red) |
| :--- | :--- | :--- | :--- | :--- |
| **资产负债率** | ≤ 40% | ≤ 60% | ≤ 80% | > 80% |
| **毛利率** | ≥ 40% | ≥ 25% | ≥ 15% | < 15% |
| **净利率** | ≥ 15% | ≥ 8% | ≥ 3% | < 3% |
| **流动比率** | ≥ 2.0 | ≥ 1.5 | ≥ 1.0 | < 1.0 |
| **营收增长率** | ≥ 30% | ≥ 10% | ≥ 0% | < 0% |
| **税负率** | 3-8% | 8-12% | 12-15% | > 15% |

---

## 5. 待优化项

1. **数据一致性**: 目前 `financial_metrics` 与 `income_statements` 存在部分字段冗余，需确保更新同步。
2. **客户/供应商分析**: `customer_analysis` 目前缺乏自动生成逻辑，建议增加从 `invoices` 表聚合生成 `customer_analysis` 的ETL任务。
