# PyQt6 桌面版备份

> ⚠️ **已弃用 (DEPRECATED)** - 2026-01-12

此目录包含原 PyQt6 桌面版应用的备份文件。

## 当前架构

项目已迁移到 **React + FastAPI** 架构：

| 组件 | 路径 | 说明 |
|------|------|------|
| 前端 | `frontend/` | React + Vite |
| 后端 | `server/` | FastAPI |
| 业务模块 | `modules/` | 共享业务逻辑 |

## 备份文件

- `coze_chat.py` - 主要桌面版应用
- `coze_chat - 副本1修改界面配色ok.py` - 配色修改版本

## 注意事项

1. 这些文件**不再维护**
2. 如需桌面版功能，请考虑基于当前 React 版本使用 Electron 封装
3. 备份文件中的 API Token 等配置可能已过期
