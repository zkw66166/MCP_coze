# 企业画像功能技术文档（详细版）

> **文档版本**: v1.0  
> **最后更新**: 2026-01-22  
> **适用系统**: 税务智能咨询平台 - 企业画像模块

---

## 目录

1. [系统架构](#1-系统架构)
2. [前端实现](#2-前端实现)
3. [后端API详解](#3-后端api详解)
4. [数据库设计](#4-数据库设计)
5. [14个画像模块详解](#5-14个画像模块详解)
6. [数据更新机制](#6-数据更新机制)
7. [指标计算逻辑](#7-指标计算逻辑)
8. [评价体系](#8-评价体系)
9. [附录](#9-附录)

---

## 1. 系统架构

### 1.1 技术栈

| 层级 | 技术 | 文件位置 |
|:---|:---|:---|
| **前端** | React 18 + Chart.js | `frontend/src/components/CompanyProfile.jsx` |
| **后端** | FastAPI + Python 3.9+ | `server/routers/company_profile.py` |
| **数据库** | SQLite 3 | `database/financial.db` |
| **调度器** | APScheduler | `server/scheduler.py` |
| **计算引擎** | Python | `database/calculate_metrics.py` |

### 1.2 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (React)                         │
│  CompanyProfile.jsx - 企业画像主组件                          │
│  └─ 14个子模块可视化组件 (图表、表格、进度条等)                 │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    后端API层 (FastAPI)                        │
│  /api/company-profile/{id}/full - 完整画像数据                │
│  /api/company-profile/{id}/basic - 基本信息                   │
│  /api/company-profile/{id}/financial - 财务摘要               │
│  ... (共14个子模块API)                                        │
└────────────────────┬────────────────────────────────────────┘
                     │ SQL查询
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   数据库层 (SQLite)                           │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │ 基础数据表    │ 计算指标表    │ 业务档案表    │             │
│  ├──────────────┼──────────────┼──────────────┤             │
│  │ companies    │ financial_   │ employee_    │             │
│  │ balance_     │   metrics    │   structure  │             │
│  │   sheets     │ customer_    │ rd_          │             │
│  │ income_      │   analysis   │   innovation │             │
│  │   statements │ supplier_    │ compliance_  │             │
│  │ invoices     │   analysis   │   summary    │             │
│  │ tax_returns  │              │ ... (10个表) │             │
│  └──────────────┴──────────────┴──────────────┘             │
└────────────────────▲────────────────────────────────────────┘
                     │
                     │ 定时计算 (每日02:00)
                     │
┌─────────────────────────────────────────────────────────────┐
│                  调度与计算层                                  │
│  scheduler.py - APScheduler定时任务                           │
│  calculate_metrics.py - 财务指标计算引擎                      │
│  generate_profile_data_v2.py - 业务档案数据生成               │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 数据流向

```
用户请求 → 前端组件 → API路由 → 数据聚合 → SQL查询 → 返回JSON → 前端渲染
   ↑                                                            │
   └────────────────── 手动刷新指标 ←──────────────────────────┘
                           │
                           ▼
                    POST /api/admin/metrics/recalculate
                           │
                           ▼
                    后台异步计算任务
                           │
                           ▼
                    更新 financial_metrics 表
```

---

## 2. 前端实现

### 2.1 主组件结构

**文件**: `frontend/src/components/CompanyProfile.jsx`

```javascript
function CompanyProfile({ selectedCompanyId, companies }) {
    const [year, setYear] = useState(2024);
    const [profile, setProfile] = useState(null);
    
    // 数据加载
    useEffect(() => {
        const loadProfile = async () => {
            const response = await fetch(
                `/api/company-profile/${companyId}/full?year=${year}`
            );
            const data = await response.json();
            setProfile(data);
        };
        loadProfile();
    }, [companyId, year]);
    
    // 渲染14个模块...
}
```

### 2.2 可视化组件

| 组件名 | 用途 | 使用的图表类型 |
|:---|:---|:---|
| `PieChart` | 资产结构、税种构成 | Chart.js Pie |
| `BarChart` | 负债与权益对比 | Chart.js Bar |
| `LineChart` | 多年趋势分析 | Chart.js Line |
| `ProgressBar` | 财务能力评分 | 自定义CSS进度条 |
| `OrgTree` | 股权结构树 | 自定义CSS树状图 |
| `CompactMetric` | 单行指标展示 | 自定义组件 |

---

## 3. 后端API详解

### 3.1 API端点总览

**文件**: `server/routers/company_profile.py`

| 端点 | 方法 | 功能 | 返回数据 |
|:---|:---|:---|:---|
| `/company-profile/{id}/full` | GET | 获取完整14模块画像 | 聚合JSON |
| `/company-profile/{id}/basic` | GET | 企业基本信息 | 工商信息 |
| `/company-profile/{id}/shareholders` | GET | 股东信息 | 股东列表 |
| `/company-profile/{id}/financial` | GET | 财务摘要 | 财务指标 |
| `/company-profile/{id}/tax` | GET | 税务摘要 | 税负数据 |
| `/company-profile/{id}/customers` | GET | TOP客户分析 | 客户集中度 |
| `/company-profile/{id}/suppliers` | GET | TOP供应商分析 | 供应商集中度 |
| `/company-profile/{id}/growth` | GET | 成长性指标 | 增长率 |
| `/company-profile/{id}/cashflow` | GET | 现金流摘要 | 三大现金流 |

---

## 4. 数据库设计

### 4.1 基础数据表 (Raw Data Tables)

| 表名 | 用途 | 主要字段 | 数据来源 |
|:---|:---|:---|:---|
| `companies` | 企业主表 | id, name, credit_code | 工商系统 |
| `balance_sheets` | 资产负债表 | total_assets, total_liabilities | 财务系统 |
| `income_statements` | 利润表 | total_revenue, net_profit | 财务系统 |
| `tax_returns_vat` | 增值税申报 | gen_tax_payable_current | 电子税务局 |
| `invoices` | 发票明细 | invoice_type, amount | 税控系统 |

### 4.2 计算指标表

| 表名 | 用途 | 计算频率 |
|:---|:---|:---|
| `financial_metrics` | 27个财务指标 | 每日02:00 |
| `customer_analysis` | 客户分析 | 手动生成 |
| `supplier_analysis` | 供应商分析 | 手动生成 |

---

## 5. 14个画像模块详解

### 5.1 企业身份画像

**数据来源**: `companies`, `company_certifications`

**核心指标**:
- 企业名称、法人、注册资本
- 资质认证(高新技术企业、ISO认证等)

### 5.2 股权与治理画像

**数据来源**: `shareholders`, `investments`

**核心指标**:
- 股东结构、持股比例
- 对外投资情况

### 5.3 财务画像

**数据来源**: `financial_metrics`, `balance_sheets`, `income_statements`

**核心指标**:
- 盈利能力: 毛利率、净利率、ROA、ROE
- 偿债能力: 资产负债率、流动比率、速动比率
- 运营效率: 总资产周转率、应收账款周转天数
- 成长能力: 营收增长率、利润增长率

### 5.4 税务画像

**数据来源**: `tax_returns_vat`, `tax_returns_income`

**核心指标**:
- 增值税税负率
- 企业所得税税负率
- 综合税负率

### 5.5 研发创新画像

**数据来源**: `rd_innovation`

**核心指标**:
- 研发投入强度
- 专利总数(发明、实用新型、外观设计)
- 软件著作权数量

---

## 6. 数据更新机制

### 6.1 定时自动计算

**调度器**: APScheduler  
**执行时间**: 每日凌晨 02:00  
**计算引擎**: `database/calculate_metrics.py`

**执行流程**:
1. 获取所有企业列表
2. 获取所有已有的利润表期间
3. 对每个期间执行27个指标的计算
4. 写入/更新 financial_metrics 表

### 6.2 手动触发计算

**API端点**: `POST /api/admin/metrics/recalculate`

**请求参数**:
```json
{
  "company_ids": [1, 2, 3],
  "year": 2024
}
```

---

## 7. 指标计算逻辑

### 7.1 盈利能力指标

#### 毛利率
```
毛利率 = (营业收入 - 营业成本) / 营业收入 × 100%
```

**评价标准**:
- ≥ 40%: 优秀
- ≥ 25%: 良好
- ≥ 15%: 一般
- < 15%: 较低

#### 净利率
```
净利率 = 净利润 / 营业收入 × 100%
```

### 7.2 偿债能力指标

#### 资产负债率
```
资产负债率 = 负债总额 / 资产总额 × 100%
```

**评价标准**:
- ≤ 40%: 优秀
- ≤ 60%: 稳健
- ≤ 80%: 偏高
- > 80%: 风险

#### 流动比率
```
流动比率 = 流动资产 / 流动负债
```

### 7.3 成长能力指标

#### 营收增长率
```
营收增长率 = (本年营收 - 上年营收) / 上年营收 × 100%
```

**评价标准**:
- ≥ 30%: 高速增长
- ≥ 10%: 稳定增长
- ≥ 0%: 平稳
- < 0%: 下降

---

## 8. 评价体系

### 8.1 评价标准汇总

| 指标类型 | 指标名 | 优秀 | 良好 | 一般 | 风险 |
|:---|:---|:---|:---|:---|:---|
| **盈利能力** | 毛利率 | ≥40% | ≥25% | ≥15% | <15% |
| | 净利率 | ≥15% | ≥8% | ≥3% | <3% |
| **偿债能力** | 资产负债率 | ≤40% | ≤60% | ≤80% | >80% |
| | 流动比率 | ≥2.0 | ≥1.5 | ≥1.0 | <1.0 |
| **成长能力** | 营收增长率 | ≥30% | ≥10% | ≥0% | <0% |
| **税负** | 增值税税负率 | ≤2% | 2-5% | 5-8% | >8% |

### 8.2 颜色编码系统

| 颜色 | 含义 | CSS类 |
|:---|:---|:---|
| 绿色 | 优秀/正常 | eval-green |
| 蓝色 | 良好/稳健 | eval-blue |
| 黄色 | 一般/警示 | eval-yellow |
| 红色 | 风险/异常 | eval-red |

---

## 9. 附录

### 9.1 数据库表完整清单

| 序号 | 表名 | 类型 | 说明 |
|:---|:---|:---|:---|
| 1 | companies | 基础 | 企业主表 |
| 2 | balance_sheets | 基础 | 资产负债表 |
| 3 | income_statements | 基础 | 利润表 |
| 4 | financial_metrics | 计算 | 27个财务指标 |
| 5 | customer_analysis | 计算 | 客户分析 |
| 6 | rd_innovation | 档案 | 研发创新 |
| 7 | compliance_summary | 档案 | 合规评估 |

### 9.2 API端点完整清单

| 端点 | 方法 | 功能 |
|:---|:---|:---|
| /api/company-profile/{id}/full | GET | 获取完整14模块画像 |
| /api/company-profile/{id}/basic | GET | 企业基本信息 |
| /api/company-profile/{id}/financial | GET | 财务摘要 |
| /api/admin/metrics/recalculate | POST | 手动触发计算 |

---

**文档结束**
