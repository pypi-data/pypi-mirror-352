"""
自定义异常模块

包含：
1. 方程求解相关异常
2. AI求解相关异常
3. 服务器管理相关异常
"""

class EquationSolverError(Exception):
    """方程求解器基础异常"""
    pass

class InputError(EquationSolverError):
    """输入错误异常"""
    pass

class SolveError(EquationSolverError):
    """求解错误异常"""
    pass

class AISolveError(EquationSolverError):
    """AI求解错误异常"""
    pass

class ServerError(EquationSolverError):
    """服务器错误异常"""
    pass

class ModelNotFoundError(ServerError):
    """模型文件未找到异常"""
    pass