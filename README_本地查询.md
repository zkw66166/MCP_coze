# MCP本地数据库查询功能 - 使用指南

## 快速开始

### 1. 环境准备

```bash
# 确保已安装依赖
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
# 首次使用需初始化数据库
python database/init_db.py
```

### 3. 配置API密钥

在`modules/deepseek_client.py`中配置DeepSeek API密钥:

```python
DEEPSEEK_API_KEY = "your_api_key_here"
```

### 4. 启动应用

```bash
python coze_chat.py
```

---

## 功能特性

### ✅ 智能路由

- **税收优惠问题** → 本地数据库查询
- **其他税法问题** → Coze知识库查询
- **自动判断**: 无需手动选择

### ✅ AI增强查询

- **税种推理**: 自动识别税种(如"税前扣除"→企业所得税)
- **项目提取**: 智能提取500+种优惠项目
- **意图识别**: 区分条件查询和一般查询
- **结果归纳**: DeepSeek智能总结

### ✅ 精准过滤

- **税种过滤**: 精确匹配税种
- **实体过滤**: 集成电路企业16条(vs全部90条)
- **意图导向**: 条件查询突出认定条件

---

## 使用示例

### 示例1: 企业类型查询

```
问: 集成电路企业有哪些优惠政策?
答: 
📊 数据库共有16条相关政策,以下展示前16条:
1. 集成电路及相关企业
2. 集成电路设计企业
...
```

### 示例2: 产品服务查询

```
问: 粮食企业有哪些增值税优惠?
答:
📊 找到1条相关政策:
1. 粮食和食用植物油 - 免征
```

### 示例3: 地区查询

```
问: 海南自贸港企业所得税优惠
答:
📊 找到3条相关政策:
1. 海南自由贸易港
2. 海南鼓励类产业企业
...
```

### 示例4: 条件查询

```
问: 高新技术企业认定条件是什么?
答:
(突出显示优惠认定条件字段)
```

---

## 测试脚本

### 测试实体过滤

```bash
python test_entity_filter.py
```

### 测试AI项目提取

```bash
python test_ai_project_extraction.py
```

### 测试总数显示

```bash
python test_count_display.py
```

### 测试意图识别

```bash
python test_intent.py
```

---

## 常见问题

### Q1: 修改代码后不生效?

**A**: 需要重启GUI程序才能加载最新代码

### Q2: 查询结果为0?

**A**: 检查:

1. 数据库是否初始化
2. 关键词是否正确
3. 查看控制台日志

### Q3: DeepSeek API调用失败?

**A**: 检查:

1. API密钥是否正确
2. 网络连接是否正常
3. 查看错误日志

### Q4: 查询速度慢?

**A**:

1. 本地查询通常<2秒
2. AI归纳需要3-5秒
3. 可以调整limit减少结果数

---

## 项目结构

```
MCP_coze/
├── coze_chat.py              # 主程序(含路由逻辑)
├── database/
│   ├── init_db.py            # 数据库初始化
│   └── tax_incentives.db     # SQLite数据库
├── modules/
│   ├── deepseek_client.py    # DeepSeek API客户端
│   ├── intent_classifier.py  # 意图分类器
│   ├── db_query.py           # 数据库查询模块
│   └── __init__.py
├── data_source/
│   └── 税收优惠政策一览表(coze).xlsx
└── test_*.py                 # 测试脚本
```

---

## 核心配置

### 路由开关

在`coze_chat.py`中:

```python
# 启用智能路由
enable_routing = True

# 禁用路由(仅使用Coze)
enable_routing = False
```

### 查询限制

在`coze_chat.py`中:

```python
# 修改返回结果数量
results, total, intent = self.db_query.search(question, limit=20)
```

### 意图关键词

在`modules/intent_classifier.py`中:

```python
# 添加新的优惠关键词
self.incentive_keywords = [
    "优惠", "减免", "免征", ...
]
```

---

## 数据更新

### 更新政策数据

1. 更新Excel文件: `data_source/税收优惠政策一览表(coze).xlsx`
2. 重新初始化数据库: `python database/init_db.py`
3. 重启应用

### 增量更新

```python
# 在init_db.py中添加增量更新逻辑
def update_policies(new_data):
    # 检查是否存在
    # 存在则更新,不存在则插入
    pass
```

---

## 性能优化建议

### 1. 数据库优化

- 添加索引: `CREATE INDEX idx_tax_type ON tax_incentives(tax_type)`
- 定期VACUUM: `VACUUM`

### 2. 查询优化

- 减少limit: `limit=10`代替`limit=50`
- 使用缓存: 缓存常见查询结果

### 3. AI调用优化

- 减少字段长度: 限制每个字段200字符
- 批量处理: 一次调用处理多个结果

---

## 技术支持

### 文档

- [技术文档](./技术文档.md): 详细实现方法和避坑指南
- [实施走查](./walkthrough.md): 完整实施过程记录

### 联系方式

- 项目地址: d:\MyProjects\MCP_coze
- 创建时间: 2026-01-09

---

**版本**: v1.0  
**最后更新**: 2026-01-09
