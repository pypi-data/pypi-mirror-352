"""
AI求解模块

包含：
1. AI求解请求处理
2. AI响应解析
3. 缓存管理
"""

import requests
import json
import re
from .utils import preprocess_expression
from .exceptions import AISolveError

class AISolver:
    """
    AI求解器类
    
    功能：
    - 向本地模型服务器发送请求
    - 处理流式响应
    - 解析AI返回的解
    - 管理缓存
    """
    
    def __init__(self, port=5001):
        self.port = port
        self.base_url = f"http://localhost:{port}/v1/chat/completions"
    
    def generate_ai_prompt(self, equation_latex):
        """
        生成AI请求的提示
        
        参数:
        equation_latex - 方程的LaTeX表示
        
        返回:
        messages - 包含系统提示和用户输入的列表
        """
        system_prompt = (
            "你是一个求解1元1~4次方程的机器人。"
            "要求：\n"
            "1. 直接输出方程的1~4个x值的解\n"
            "2. 可以输出根号（sqrt()）和虚数(i)\n"
            "3. 格式为x1=...,x2=...,x3=...,x4=...\n"
            "4. 不是编写代码，而是直接给出方程的解\n"
            "5. 如果只有1个或2个或3个解，则无需输出其他的x值\n"
            "6. 在<think>标签中思考过程，其他内容为答案\n"
            "7. 任何形式的相乘需要用*表示，例如2x -> 2*x"
        )
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"求解方程 {equation_latex} = 0 的x值"}
        ]
    
    def send_ai_request(self, equation_latex, max_tokens=1000, temperature=0.3):
        """
        发送AI请求（流式）
        
        参数:
        equation_latex - 方程的LaTeX表示
        max_tokens - 最大token数
        temperature - 温度参数
        
        返回:
        full_response - 完整响应字符串
        """
        headers = {"Content-Type": "application/json"}
        data = {
            "messages": self.generate_ai_prompt(equation_latex),
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        
        try:
            response = requests.post(
                self.base_url, 
                json=data, 
                headers=headers, 
                stream=True, 
                timeout=30
            )
            response.raise_for_status()
            
            full_response = ""
            for chunk in response.iter_lines():
                if chunk:
                    chunk_str = chunk.decode('utf-8').strip()
                    if chunk_str.startswith('data:'):
                        json_data = chunk_str[5:].strip()
                        if json_data != "[DONE]":
                            try:
                                data = json.loads(json_data)
                                content = data['choices'][0]['delta'].get('content', '')
                                if content:
                                    full_response += content
                            except json.JSONDecodeError:
                                pass
            return full_response
        except Exception as e:
            raise AISolveError(f"AI请求失败: {str(e)}")
    
    def parse_ai_response(self, ai_text):
        """
        解析AI响应
        
        参数:
        ai_text - AI返回的文本
        
        返回:
        {
            "clean_text": 清理后的文本,
            "think_content": 思考过程内容,
            "solutions": 解列表
        }
        """
        try:
            # 移除所有<think>标签及其内容
            filtered_text = re.sub(r'<think>.*?</think>', '', ai_text, flags=re.DOTALL)
            
            # 移除所有剩余的HTML标签
            clean_text = re.sub(r'<.*?>', '', filtered_text).strip()
            
            # 提取思考过程
            think_content = ""
            think_match = re.search(r'<think>(.*?)</think>', ai_text, re.DOTALL)
            if think_match:
                think_content = re.sub(r'<.*?>', '', think_match.group(1)).strip()
            
            # 提取解
            solutions = []
            pattern = r'x\d*\s*=\s*([^\n,]+)'
            matches = re.findall(pattern, clean_text)
            
            if not matches:
                # 尝试其他可能的解格式
                pattern = r'解为\s*：?\s*([^\n]+)'
                matches = re.findall(pattern, clean_text)
                if matches:
                    parts = matches[0].split(',')
                    solutions = [part.strip() for part in parts]
            else:
                solutions = [m.strip().rstrip('.') for m in matches]
            
            # 预处理解表达式
            processed_solutions = []
            for expr_str in solutions:
                try:
                    expr_str = preprocess_expression(expr_str)
                    processed_solutions.append(expr_str)
                except Exception as e:
                    raise AISolveError(f"表达式预处理失败: {expr_str} -> {str(e)}")
            
            return {
                "clean_text": clean_text,
                "think_content": think_content,
                "solutions": processed_solutions
            }
        except Exception as e:
            raise AISolveError(f"解析AI响应失败: {str(e)}")