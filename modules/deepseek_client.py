#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek API客户端模块
功能:
1. 封装DeepSeek-V3 API调用
2. 支持流式和非流式响应
3. 错误处理和重试机制
"""

import requests
import json
import time
from typing import Iterator, Optional, List, Dict, Union


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str = "sk-7acc54f78466478f9fb3f9ad5e1154fe"):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com"
        self.model = "deepseek-chat"  # DeepSeek-V3
        self.max_retries = 3
        self.timeout = 60
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Union[str, Iterator[str]]:
        """
        调用DeepSeek聊天完成API
        
        Args:
            messages: 消息列表,格式 [{"role": "user", "content": "..."}]
            stream: 是否使用流式响应
            temperature: 温度参数(0-2)
            max_tokens: 最大token数
        
        Returns:
            非流式: 返回完整响应字符串
            流式: 返回生成器,逐块返回内容
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # 重试逻辑
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    stream=stream,
                    timeout=self.timeout
                )
                
                # 检查HTTP状态码
                if response.status_code != 200:
                    error_msg = f"API错误 {response.status_code}: {response.text}"
                    if attempt < self.max_retries - 1:
                        print(f"⚠️  {error_msg}, 重试中...")
                        time.sleep(2 ** attempt)  # 指数退避
                        continue
                    else:
                        raise Exception(error_msg)
                
                # 返回结果
                if stream:
                    return self._handle_stream(response)
                else:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
            
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    print(f"⚠️  请求超时, 重试中...")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise Exception("API请求超时")
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"⚠️  请求失败: {str(e)}, 重试中...")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise
    
    def _handle_stream(self, response) -> Iterator[str]:
        """
        处理流式响应
        
        Args:
            response: requests响应对象
        
        Yields:
            逐块返回内容
        """
        try:
            for line in response.iter_lines():
                if not line:
                    continue
                
                line_str = line.decode('utf-8')
                
                # 跳过注释行
                if line_str.startswith(':'):
                    continue
                
                # 解析SSE格式
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    
                    # 检查结束标记
                    if data_str == '[DONE]':
                        break
                    
                    try:
                        data = json.loads(data_str)
                        
                        # 提取内容
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                yield delta['content']
                    
                    except json.JSONDecodeError:
                        # 忽略无法解析的行
                        continue
        
        except Exception as e:
            print(f"❌ 流式响应处理错误: {str(e)}")
            raise
    
    def classify_intent(self, question: str) -> str:
        """
        使用DeepSeek进行意图分类
        
        Args:
            question: 用户问题
        
        Returns:
            "tax_incentive" 或 "other"
        """
        prompt = f"""请判断以下问题是否关于"税收优惠政策"。

问题: {question}

判断标准:
- 如果问题涉及税收减免、免征、优惠、抵扣、退税、补贴等内容,返回"tax_incentive"
- 如果问题涉及具体的税收优惠政策、优惠条件、优惠比例等,返回"tax_incentive"
- 其他税法问题(如税务申报、发票管理、税法解释等)返回"other"

请只返回"tax_incentive"或"other",不要有其他内容。"""
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.chat_completion(messages, stream=False, temperature=0.3)
            response = response.strip().lower()
            
            if "tax_incentive" in response:
                return "tax_incentive"
            else:
                return "other"
        
        except Exception as e:
            print(f"⚠️  意图识别失败: {str(e)}, 默认路由到Coze")
            return "other"  # 失败时默认使用Coze
    
    def format_query_results(self, question: str, results: List[Dict]) -> str:
        """
        使用DeepSeek格式化数据库查询结果
        
        Args:
            question: 用户问题
            results: 数据库查询结果列表
        
        Returns:
            格式化后的Markdown文本
        """
        # 构建结果摘要
        results_text = ""
        for idx, result in enumerate(results, 1):
            results_text += f"\n### 政策 {idx}\n"
            results_text += f"- **税种**: {result.get('tax_type', 'N/A')}\n"
            results_text += f"- **优惠项目**: {result.get('incentive_items', 'N/A')}\n"
            results_text += f"- **优惠方式**: {result.get('incentive_method', 'N/A')}\n"
            
            if result.get('qualification'):
                results_text += f"- **认定条件**: {result['qualification']}\n"
            
            if result.get('detailed_rules'):
                results_text += f"- **具体规定**: {result['detailed_rules']}\n"
            
            if result.get('legal_basis'):
                results_text += f"- **法律依据**: {result['legal_basis']}\n"
            
            results_text += "\n"
        
        # 构建prompt
        prompt = f"""请根据以下税收优惠政策数据,回答用户问题。

用户问题: {question}

政策数据:
{results_text}

要求:
1. 用清晰的Markdown格式回答
2. 突出关键信息(优惠比例、适用条件、法律依据等)
3. 如有多个政策,分条列出并说明区别
4. 语言简洁专业,易于理解
5. 如果政策数据不完整,说明建议咨询税务专业人士

请直接回答,不要重复问题。"""
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            # 使用非流式响应(简化处理)
            response = self.chat_completion(messages, stream=False, temperature=0.7)
            return response
        
        except Exception as e:
            # 降级方案:返回原始数据
            print(f"⚠️  结果格式化失败: {str(e)}, 使用原始数据")
            return f"查询到 {len(results)} 条相关政策:\n\n{results_text}"


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("DeepSeek API客户端测试")
    print("=" * 60)
    
    client = DeepSeekClient()
    
    # 测试1: 意图识别
    print("\n【测试1: 意图识别】")
    test_questions = [
        "高新技术企业有哪些增值税优惠?",
        "什么是增值税专用发票?",
        "小微企业所得税减免政策是什么?",
        "如何进行税务申报?"
    ]
    
    for q in test_questions:
        intent = client.classify_intent(q)
        print(f"  问题: {q}")
        print(f"  意图: {intent}\n")
    
    # 测试2: 非流式响应
    print("\n【测试2: 非流式响应】")
    messages = [{"role": "user", "content": "请用一句话介绍DeepSeek"}]
    response = client.chat_completion(messages, stream=False)
    print(f"  响应: {response}\n")
    
    # 测试3: 流式响应
    print("\n【测试3: 流式响应】")
    messages = [{"role": "user", "content": "请简要介绍中国的税收体系"}]
    print("  响应: ", end="", flush=True)
    for chunk in client.chat_completion(messages, stream=True):
        print(chunk, end="", flush=True)
    print("\n")
    
    print("=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)
