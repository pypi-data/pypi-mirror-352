"""
Mathematical operation example modules.
数学演算のサンプルモジュール。
"""

from typing import Dict, Any, List
import math
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from flexify.core import Module, ParamInfo


class CalculatorModule(Module):
    """
    Module that performs basic arithmetic operations.
    基本的な算術演算を実行するモジュール。
    
    Supports operations: add, subtract, multiply, divide, power, sqrt
    サポートする操作: add, subtract, multiply, divide, power, sqrt
    """
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform arithmetic operation.
        算術演算を実行します。
        """
        operation = session.get("operation", "add")
        # Convert to float to handle both int and float inputs
        a = float(session.get("a", 0))
        b = float(session.get("b", 0))
        
        try:
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    session["error"] = "Division by zero"
                    result = None
                else:
                    result = a / b
            elif operation == "power":
                result = a ** b
            elif operation == "sqrt":
                if a < 0:
                    session["error"] = "Cannot calculate square root of negative number"
                    result = None
                else:
                    result = math.sqrt(a)
            else:
                session["error"] = f"Unknown operation: {operation}"
                result = None
            
            if result is not None:
                session["result"] = result
                session["error"] = ""
            
        except Exception as e:
            session["error"] = str(e)
            session["result"] = None
        
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        """
        Get parameter information for CalculatorModule.
        CalculatorModuleのパラメータ情報を取得します。
        """
        return [
            ParamInfo(
                name="operation",
                type=str,
                required=False,
                default="add",
                description="Operation: add, subtract, multiply, divide, power, sqrt"
            ),
            ParamInfo(
                name="a",
                type=float,
                required=True,
                description="First operand"
            ),
            ParamInfo(
                name="b",
                type=float,
                required=False,
                default=0,
                description="Second operand (not used for sqrt)"
            ),
            ParamInfo(
                name="result",
                type=float,
                required=False,
                default=None,
                description="Output: Calculation result"
            ),
            ParamInfo(
                name="error",
                type=str,
                required=False,
                default="",
                description="Output: Error message if any"
            )
        ]


class StatisticsModule(Module):
    """
    Module that calculates statistical measures from a list of numbers.
    数値リストから統計指標を計算するモジュール。
    """
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate statistics from number list.
        数値リストから統計を計算します。
        """
        numbers = session.get("numbers", [])
        
        if not numbers:
            session.update({
                "count": 0,
                "sum": 0,
                "mean": 0,
                "min": None,
                "max": None,
                "range": 0,
                "variance": 0,
                "std_dev": 0
            })
            return session
        
        # Basic statistics
        count = len(numbers)
        total = sum(numbers)
        mean = total / count
        minimum = min(numbers)
        maximum = max(numbers)
        value_range = maximum - minimum
        
        # Variance and standard deviation
        variance = sum((x - mean) ** 2 for x in numbers) / count
        std_dev = math.sqrt(variance)
        
        # Update session
        session.update({
            "count": count,
            "sum": total,
            "mean": round(mean, 4),
            "min": minimum,
            "max": maximum,
            "range": value_range,
            "variance": round(variance, 4),
            "std_dev": round(std_dev, 4)
        })
        
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        """
        Get parameter information for StatisticsModule.
        StatisticsModuleのパラメータ情報を取得します。
        """
        return [
            ParamInfo(
                name="numbers",
                type=list,
                required=True,
                description="List of numbers to analyze"
            ),
            ParamInfo(
                name="count",
                type=int,
                required=False,
                default=0,
                description="Output: Number of values"
            ),
            ParamInfo(
                name="sum",
                type=float,
                required=False,
                default=0,
                description="Output: Sum of all values"
            ),
            ParamInfo(
                name="mean",
                type=float,
                required=False,
                default=0,
                description="Output: Average value"
            ),
            ParamInfo(
                name="min",
                type=float,
                required=False,
                default=None,
                description="Output: Minimum value"
            ),
            ParamInfo(
                name="max",
                type=float,
                required=False,
                default=None,
                description="Output: Maximum value"
            ),
            ParamInfo(
                name="range",
                type=float,
                required=False,
                default=0,
                description="Output: Range (max - min)"
            ),
            ParamInfo(
                name="variance",
                type=float,
                required=False,
                default=0,
                description="Output: Variance"
            ),
            ParamInfo(
                name="std_dev",
                type=float,
                required=False,
                default=0,
                description="Output: Standard deviation"
            )
        ]


class FibonacciModule(Module):
    """
    Module that generates Fibonacci sequence.
    フィボナッチ数列を生成するモジュール。
    """
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Fibonacci sequence up to n terms.
        n項までのフィボナッチ数列を生成します。
        """
        n = session.get("n", 10)
        
        if n <= 0:
            session["sequence"] = []
            session["nth_value"] = None
        elif n == 1:
            session["sequence"] = [0]
            session["nth_value"] = 0
        elif n == 2:
            session["sequence"] = [0, 1]
            session["nth_value"] = 1
        else:
            sequence = [0, 1]
            for i in range(2, n):
                sequence.append(sequence[i-1] + sequence[i-2])
            session["sequence"] = sequence
            session["nth_value"] = sequence[-1]
        
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        """
        Get parameter information for FibonacciModule.
        FibonacciModuleのパラメータ情報を取得します。
        """
        return [
            ParamInfo(
                name="n",
                type=int,
                required=False,
                default=10,
                description="Number of Fibonacci terms to generate"
            ),
            ParamInfo(
                name="sequence",
                type=list,
                required=False,
                default=[],
                description="Output: Fibonacci sequence"
            ),
            ParamInfo(
                name="nth_value",
                type=int,
                required=False,
                default=None,
                description="Output: The nth Fibonacci number"
            )
        ]