"""
数学方程求解器包

该包提供了一元1~4次方程的求解功能，支持：
1. 传统数学求解
2. AI辅助求解
3. 本地模型服务器管理

主要模块：
- core: 核心求解功能
- ai: AI求解相关功能
- server: 本地模型服务器管理
- utils: 工具函数
- exceptions: 自定义异常
"""

from .core import EquationSolver
from .ai import AISolver
from .server import ModelServer
from .utils import preprocess_expression

__version__ = "1.0.0"
__all__ = ["EquationSolver", "AISolver", "ModelServer", "preprocess_expression"]
