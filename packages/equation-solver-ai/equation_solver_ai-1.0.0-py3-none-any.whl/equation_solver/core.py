"""
核心方程求解功能

包含：
1. 方程解析与求解
2. 表达式简化与数值计算
3. 解的表示与处理
"""

import sympy as sp
from sympy import sympify, simplify, solve, latex, N
import re
import hashlib

class EquationSolver:
    """
    方程求解器核心类
    
    功能：
    - 解析用户输入的系数
    - 构建方程表达式
    - 求解方程
    - 处理解的表示
    """
    
    def __init__(self):
        self.x = sp.Symbol('x')
        self.solution_cache = []
        self.ai_cache = {}
    
    def parse_input(self, inputs):
        """
        解析用户输入的系数
        
        参数:
        inputs - 系数字典，格式为:
            {
                "x⁴": 系数值,
                "x³": 系数值,
                "x²": 系数值,
                "x": 系数值,
                "常数项": 系数值
            }
            
        返回:
        系数列表 [a, b, c, d, e] 对应 ax⁴ + bx³ + cx² + dx + e
        """
        coefficients = []
        for key in ["x⁴", "x³", "x²", "x", "常数项"]:
            value = inputs.get(key, "").strip()
            if not value:
                coefficients.append(sp.Integer(0))
            else:
                try:
                    coefficients.append(sympify(value))
                except Exception:
                    raise ValueError(f"无效输入：{key}")
        return coefficients
    
    def build_equation(self, coefficients):
        """
        根据系数构建方程
        
        参数:
        coefficients - 系数列表 [a, b, c, d, e]
        
        返回:
        (equation, degree) - 方程表达式和方程次数
        """
        a, b, c, d, e = coefficients
        equation = (
            a * self.x**4 + 
            b * self.x**3 + 
            c * self.x**2 + 
            d * self.x + 
            e
        )
        
        # 计算方程的最高次数
        degree = next((4 - i for i, coeff in enumerate(coefficients) if coeff != 0), 0)
        
        return equation, degree
    
    def solve_equation(self, equation):
        """
        求解方程
        
        参数:
        equation - 方程表达式
        
        返回:
        solutions - 解列表
        """
        try:
            solutions = solve(equation, self.x)
            return solutions
        except Exception as e:
            raise RuntimeError(f"求解错误: {str(e)}")
    
    def process_solutions(self, solutions):
        """
        处理解，准备用于显示
        
        参数:
        solutions - 解列表
        
        返回:
        processed - 处理后的解列表，每个元素为(simplified_expr, base_size)
        """
        processed = []
        for sol in solutions:
            simplified = simplify(sol)
            base_size = self.calc_base_size(simplified)
            processed.append((simplified, base_size))
        return processed
    
    def calc_base_size(self, expr):
        """
        计算表达式的基本显示尺寸
        
        参数:
        expr - 表达式
        
        返回:
        (width, height) - 基本尺寸
        """
        latex_str = latex(expr)
        length = len(re.findall(r'\w', latex_str))
        width = min(6 + (length / 10) * 2, 12)
        return (width, 0.8)
    
    def get_cache_key(self, coefficients):
        """
        生成缓存键 - 使用系数的哈希值
        
        参数:
        coefficients - 系数列表
        
        返回:
        cache_key - 缓存键字符串
        """
        coeff_str = "|".join(str(float(N(coeff))) for coeff in coefficients)
        return hashlib.md5(coeff_str.encode()).hexdigest()
    
    def clear_cache(self):
        """清空缓存"""
        self.solution_cache = []
        self.ai_cache = {}