import requests
import json
import sys
import time

# -------------------------- 基础配置 --------------------------
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
requests.packages.urllib3.disable_warnings()

# -------------------------- 配置信息 --------------------------
PAT_TOKEN = "pat_6IkhWiD17bW1qZmXHzeKPPU2YZzBQG8OlqyUyUSXlEFIGBPfOYlTsPK5VHjUSPz8"
BOT_ID = "7592559564151668742"
USER_ID = "123"

def raw_stream_debug(question: str, timeout=120):
    """
    完全原始的调试：打印所有接收到的内容，不做任何过滤
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
            {
                "role": "user",
                "content": question,
                "content_type": "text"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    print(f"\n🔍 问题：{question}")
    print(f"⏱️  超时时间：{timeout}秒")
    print("=" * 80)
    print("完全原始调试模式")
    print("=" * 80)

    try:
        response = requests.post(
            "https://api.coze.cn/v3/chat",
            headers=headers,
            json=payload,
            stream=True,
            timeout=timeout,
            verify=False
        )

        print(f"\n📊 HTTP状态码：{response.status_code}")
        print(f"📊 Content-Type：{response.headers.get('Content-Type', 'N/A')}")
        print("=" * 80)
        print("📡 开始接收原始数据...")
        print("=" * 80)

        line_count = 0
        total_bytes = 0
        sample_lines = []  # 保存前50行用于分析

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                total_bytes += len(chunk)
                chunk_str = chunk.decode('utf-8', errors='ignore')
                
                # 按行分割
                lines = chunk_str.split('\n')
                for line in lines:
                    line_count += 1
                    
                    # 保存前50行
                    if len(sample_lines) < 50:
                        sample_lines.append(f"Line {line_count}: {line}")
                    
                    # 打印每行的前200字符（避免输出太多）
                    line_preview = line[:200] if len(line) > 200 else line
                    print(f"[{line_count:04d}] {line_preview}")
                    
                    # 如果行太长，添加省略标记
                    if len(line) > 200:
                        print(f"       ... (总{len(line)}字符)")

        print("\n" + "=" * 80)
        print(f"✅ 接收完成")
        print(f"   总行数：{line_count}")
        print(f"   总字节数：{total_bytes}")
        print("=" * 80)

        print("\n" + "=" * 80)
        print("📋 前50行（重新展示，便于分析）")
        print("=" * 80)
        for i, line in enumerate(sample_lines):
            print(line)

        # 尝试分析数据格式
        print("\n" + "=" * 80)
        print("🔍 数据格式分析")
        print("=" * 80)
        
        print("\n检查是否有SSE格式标记...")
        has_data_prefix = any('data:' in line for line in sample_lines)
        has_event_prefix = any('event:' in line for line in sample_lines)
        
        print(f"  包含 'data:' 前缀：{has_data_prefix}")
        print(f"  包含 'event:' 前缀：{has_event_prefix}")

        # 检查是否包含JSON
        print("\n检查是否包含JSON数据...")
        for i, line in enumerate(sample_lines):
            if '{' in line and '}' in line:
                print(f"  第{i+1}行可能是JSON：{line[:100]}...")
                try:
                    # 尝试提取并解析JSON
                    json_str = line
                    if 'data:' in line:
                        json_str = line.split('data:')[1].strip()
                    if json_str:
                        data = json.loads(json_str)
                        print(f"    ✅ 成功解析JSON：")
                        print(f"    {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                        break
                except:
                    print(f"    ❌ JSON解析失败")
                    continue

    except requests.exceptions.Timeout:
        print("\n" + "=" * 80)
        print("⚠️ 请求超时")
        print("=" * 80)
        print(f"💡 建议增加超时时间（当前：{timeout}秒）")
    
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ 异常：{str(e)}")
        print("=" * 80)
        import traceback
        traceback.print_exc()

def test_different_timeout():
    """
    测试不同的超时时间
    """
    question = "加计扣除政策有哪些"
    
    print("\n" + "=" * 80)
    print("测试不同的超时时间")
    print("=" * 80)
    
    for timeout in [30, 60, 120, 180]:
        print(f"\n\n{'='*80}")
        print(f"测试超时时间：{timeout}秒")
        print(f"{'='*80}")
        raw_stream_debug(question, timeout=timeout)
        time.sleep(2)

# -------------------------- 主程序 --------------------------
if __name__ == "__main__":
    print("=" * 80)
    print("扣子智能体对话工具 - 完全原始调试版")
    print("=" * 80)

    # 使用较长的超时时间
    raw_stream_debug("加计扣除政策有哪些", timeout=180)
    
    # 如果需要测试不同的超时时间，取消下面的注释
    # test_different_timeout()
