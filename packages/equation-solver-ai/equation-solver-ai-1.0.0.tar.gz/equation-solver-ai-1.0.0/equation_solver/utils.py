"""
工具函数模块

包含：
1. 表达式预处理
2. 图像处理函数
3. 其他辅助功能
"""

import sympy as sp
import re
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

def preprocess_expression(expr_str):
    """
    预处理表达式字符串
    
    参数:
    expr_str - 原始表达式字符串
    
    返回:
    processed - 处理后的表达式字符串
    """
    # 替换虚数单位和根号表示
    expr_str = expr_str.replace('^', '**')
    expr_str = expr_str.replace('√', 'sqrt')
    
    # 处理数字和sqrt之间的连接问题
    expr_str = re.sub(r'(\d+)(sqrt)', r'\1*\2', expr_str)
    
    # 处理数字和字母之间的连接问题
    expr_str = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr_str)
    
    # 处理函数调用
    expr_str = re.sub(r'(sqrt|exp|log|sin|cos|tan)(\d+)', r'\1(\2)', expr_str)
    
    # 处理缺少括号的sqrt
    expr_str = re.sub(r'sqrt([^\d\(])', r'sqrt(\1', expr_str)
    
    # 处理虚数在sqrt函数内
    expr_str = re.sub(r'sqrt([^\d\(]?i)', r'sqrt(\1)', expr_str)
    
    # 处理虚数与sqrt相乘
    expr_str = re.sub(r'(i)(sqrt)', r'\1*\2', expr_str)
    
    return expr_str

def expr_to_image(expr, prefix="", index=1, zoom_level=1.0):
    """
    将表达式转换为图像
    
    参数:
    expr - 表达式
    prefix - 前缀文本 (如"解1")
    index - 解的索引
    zoom_level - 缩放级别
    
    返回:
    ImageTk.PhotoImage对象
    """
    width, height = 6 * zoom_level, 0.8 * zoom_level
    
    fig = Figure(figsize=(width, height), dpi=100)
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    latex_text = f"{prefix} {index}: ${sp.latex(expr)}$" if prefix else f"${sp.latex(expr)}$"
    ax.text(0.02, 0.5, latex_text, 
           fontsize=14*zoom_level, 
           verticalalignment='center')
    
    fig.tight_layout(pad=0)
    return fig_to_image(fig)

def fig_to_image(fig):
    """
    将matplotlib图形转换为PIL图像
    
    参数:
    fig - matplotlib Figure对象
    
    返回:
    PIL.Image对象
    """
    canvas = FigureCanvas(fig)
    canvas.draw()
    w, h = canvas.get_width_height()
    buf = canvas.buffer_rgba()
    image = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'RGBA', 0, 1)
    return image

def calc_approx_value(expr):
    """
    计算表达式的近似值
    
    参数:
    expr - 表达式
    
    返回:
    float - 近似值
    """
    return sp.N(expr)