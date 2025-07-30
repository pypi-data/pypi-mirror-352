import pandas as pd
import numpy as np
import ast
import logging

class SpectralCalculator:
    """光谱特征计算器，支持公式解析"""
    
    def __init__(self, data: pd.DataFrame, tris_coeff: pd.DataFrame = None):
        """
        初始化计算器
        
        Args:
            data: 光谱数据
            tris_coeff: 三刺激值系数表
        """
        self.logger = logging.getLogger(__name__)
        self.data = data  # 存储光谱数据
        self.columns = set(data.columns.astype(float))  # 记录所有波长
        self.tris_coeff = tris_coeff  # 三刺激值系数表
        
        # 支持的函数
        self.functions = {
            'sum': self._sum,
            'mean': self._mean,
            'abs': self._abs,
            'ref': self._ref,  # 获取单个波段的反射率
            'tris': self._tris  # 计算三刺激值
        }

    def evaluate(self, expression: str) -> pd.Series:
        """解析并计算表达式"""
        try:
            return self._eval(ast.parse(expression, mode='eval').body)
        except Exception as e:
            self.logger.error(f"表达式 '{expression}' 计算失败: {e}", exc_info=True)
            raise ValueError(f"表达式 '{expression}' 计算失败: {e}")

    def _eval(self, node):
        """递归解析表达式"""
        if isinstance(node, ast.BinOp):  # 处理二元运算 + - * /
            left = self._eval(node.left)
            right = self._eval(node.right)
            
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                return left / right
            else:
                self.logger.error(f"不支持的运算符: {type(node.op).__name__}")
                raise ValueError(f"不支持的运算符: {type(node.op).__name__}")
                
        elif isinstance(node, ast.Call):  # 处理函数调用
            func_name = node.func.id.lower()
            if func_name not in self.functions:
                self.logger.error(f"不支持的函数: {func_name}")
                raise ValueError(f"不支持的函数: {func_name}")
                
            # 处理tris函数，它需要一个特殊的字符参数
            if func_name == 'tris':
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Name):
                    self.logger.error("tris() 需要一个参数 'x', 'y' 或 'z'")
                    raise ValueError("tris() 需要一个参数 'x', 'y' 或 'z'")
                arg = node.args[0].id  # 获取参数名
                return self.functions[func_name](arg)
                
            # 处理其他函数
            args = [self._eval(arg) for arg in node.args]
            return self.functions[func_name](*args)
            
        elif isinstance(node, ast.Num):  # 处理直接的数字
            return node.n
            
        elif isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
            
        elif isinstance(node, ast.Name):  # 处理变量名
            var_name = node.id
            try:
                # 尝试将变量名转为波长值
                band = float(var_name)
                if band in self.columns:
                    return self.data[band]
                else:
                    nearest_band = min(self.columns, key=lambda x: abs(x - band))
                    self.logger.warning(f"波长 {band} 不存在，使用最接近的波长 {nearest_band}")
                    return self.data[nearest_band]
            except ValueError:
                # 如果不是数字，可能是 x, y, z
                if var_name in ['x', 'y', 'z']:
                    return var_name
                else:
                    self.logger.error(f"无效的变量名: {var_name}")
                    raise ValueError(f"无效的变量名: {var_name}")
                    
        else:
            self.logger.error(f"不支持的表达式类型: {type(node).__name__}")
            raise ValueError(f"不支持的表达式类型: {type(node).__name__}")

    def _sum(self, start_band, end_band):
        """计算波段范围内的和"""
        start_band = float(start_band)
        end_band = float(end_band)
        
        if start_band not in self.columns and end_band not in self.columns:
            self.logger.error(f"波段范围 {start_band}-{end_band} 无效")
            raise ValueError(f"波段范围 {start_band}-{end_band} 无效")
            
        cols = [col for col in self.data.columns if start_band <= float(col) <= end_band]
        if not cols:
            self.logger.error(f"波段范围 {start_band}-{end_band} 内没有数据")
            raise ValueError(f"波段范围 {start_band}-{end_band} 内没有数据")
            
        return self.data[cols].sum(axis=1)

    def _mean(self, start_band, end_band):
        """计算波段范围内的均值"""
        start_band = float(start_band)
        end_band = float(end_band)
        
        if start_band not in self.columns and end_band not in self.columns:
            self.logger.error(f"波段范围 {start_band}-{end_band} 无效")
            raise ValueError(f"波段范围 {start_band}-{end_band} 无效")
            
        cols = [col for col in self.data.columns if start_band <= float(col) <= end_band]
        if not cols:
            self.logger.error(f"波段范围 {start_band}-{end_band} 内没有数据")
            raise ValueError(f"波段范围 {start_band}-{end_band} 内没有数据")
            
        return self.data[cols].mean(axis=1)

    def _abs(self, value):
        """计算绝对值"""
        return abs(value)

    def _ref(self, band):
        """获取指定波段的反射率"""
        band = float(band)
        
        if band in self.columns:
            return self.data[band]
        else:
            # 找最接近的波段
            nearest_band = min(self.columns, key=lambda x: abs(x - band))
            self.logger.warning(f"波长 {band} 不存在，使用最接近的波长 {nearest_band}")
            return self.data[nearest_band]

    def _tris(self, channel):
        """计算三刺激值"""
        if channel not in ["x", "y", "z"]:
            self.logger.error(f"tris() 参数必须是 'x', 'y' 或 'z'，收到: {channel}")
            raise ValueError("tris() 参数必须是 'x', 'y' 或 'z'")
            
        if self.tris_coeff is None or self.tris_coeff.empty:
            self.logger.error("未加载三刺激值系数表")
            raise ValueError("未加载三刺激值系数表")
            
        index = {"x": 0, "y": 1, "z": 2}[channel]  # 选择对应的系数行
        coef = self.tris_coeff.iloc[index]  # 取出三刺激值系数
        
        # 选取需要的波段范围
        valid_bands = [col for col in self.data.columns 
                       if col in coef.index or float(col) in coef.index]
        if not valid_bands:
            self.logger.error("当前光谱数据与三刺激值系数表波段不匹配")
            raise ValueError("当前光谱数据与三刺激值系数表波段不匹配")
            
        # 计算三刺激值
        result = pd.Series(0.0, index=self.data.index)
        for band in valid_bands:
            if band in coef.index:
                coef_value = coef[band]
            else:
                coef_value = coef[float(band)]
            result += self.data[band] * coef_value
            
        return result 