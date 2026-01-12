# 重要提示:需要重启GUI程序

## 问题原因

GUI程序(coze_chat.py)在启动时加载了模块,之后的代码修改不会自动生效。

## 解决方法

### 方法1: 关闭并重新启动GUI程序

1. 关闭当前运行的GUI窗口
2. 重新运行: `.\venv\Scripts\python.exe coze_chat.py`

### 方法2: 使用命令行关闭进程

```powershell
# 查找Python进程
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# 关闭进程(替换<PID>为实际进程ID)
Stop-Process -Id <PID>

# 重新启动
.\venv\Scripts\python.exe coze_chat.py
```

## 验证修复

重启后,测试以下问题应该路由到本地数据库:

- "个人所得税优惠政策有哪些"
- "印花税减免政策有哪些"
- "增值税优惠政策有哪些"

控制台会显示:

```
🔍 意图识别结果: tax_incentive
```
