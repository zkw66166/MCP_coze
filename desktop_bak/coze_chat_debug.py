import requests
import json
import sys

# -------------------------- 基础配置 --------------------------
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
requests.packages.urllib3.disable_warnings()

# -------------------------- 你的核心参数 --------------------------
PAT_TOKEN = "pat_6IkhWiD17bW1qZmXHzeKPPU2YZzBQG8OlqyUyUSXlEFIGBPfOYlTsPK5VHjUSPz8"
BOT_ID = "7592559564151668742"
API_URL = "https://api.coze.cn/v3/chat"
USER_ID = "123"

def debug_chat(question: str):
    """
    调试版本：打印所有原始数据
    """
    headers = {
        "Authorization": f"Bearer {PAT_TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "text/event-stream",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    payload = {
        "bot_id": BOT_ID,
        "user_id": USER_ID,
        "stream": True,
        "auto_save_history": True,
        "additional_messages": [
            {"role": "user", "content": question, "content_type": "text"}
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }

    try:
        print(f"\n🔍 正在查询：{question}")
        print("=" * 80)
        print("📡 开始接收 SSE 流数据：")
        print("-" * 80)
        
        response = requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=60, verify=False)
        
        print(f"HTTP Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print("-" * 80)
        
        if response.status_code != 200:
            print(f"❌ 调用失败：{response.text[:500]}")
            return
        
        # 打印所有接收到的原始数据
        line_count = 0
        for line in response.iter_lines():
            if line:
                line_count += 1
                line_str = line.decode('utf-8')
                print(f"[Line {line_count}] {line_str}")
                
                # 尝试解析 JSON
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str == '[DONE]':
                        print("✅ [DONE] 标记收到，流结束")
                        break
                    
                    try:
                        data = json.loads(data_str)
                        print(f"    → 解析成功: {json.dumps(data, ensure_ascii=False, indent=4)[:500]}")
                    except json.JSONDecodeError as e:
                        print(f"    → JSON 解析失败: {e}")
        
        print("-" * 80)
        print(f"✅ 共接收 {line_count} 行数据")
    
    except Exception as e:
        print(f"❌ 运行异常：{str(e)}")
        import traceback
        traceback.print_exc()

# 测试
if __name__ == "__main__":
    debug_chat("加计扣除政策有哪些")
