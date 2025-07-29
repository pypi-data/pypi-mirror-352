"""
Tests for example modules (simple mock modules for testing).
サンプルモジュールのテスト（テスト用の簡単なモックモジュール）。
"""

from typing import Dict, Any, List
from flexify.core import Module, ParamInfo


class MockCalculatorModule(Module):
    """Mock calculator module for testing."""
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        operation = session.get("operation", "add")
        a = session.get("a", 0)
        b = session.get("b", 0)
        
        if operation == "add":
            result = a + b
        elif operation == "multiply":
            result = a * b
        elif operation == "sqrt":
            result = a ** 0.5
        elif operation == "invalid_operation":
            raise ValueError("Invalid operation for testing")
        else:
            result = 0
        
        session["result"] = result
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        return [
            ParamInfo(name="operation", type=str, required=False, default="add"),
            ParamInfo(name="a", type=float, required=True),
            ParamInfo(name="b", type=float, required=False, default=0),
            ParamInfo(name="result", type=float, required=False, default=None)
        ]


class MockTextModule(Module):
    """Mock text module for testing."""
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        text = session.get("text", "")
        operation = session.get("operation", "upper")
        
        if operation == "upper":
            session["transformed_text"] = text.upper()
        elif operation == "lower":
            session["transformed_text"] = text.lower()
        else:
            session["transformed_text"] = text
        
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        return [
            ParamInfo(name="text", type=str, required=True),
            ParamInfo(name="operation", type=str, required=False, default="upper"),
            ParamInfo(name="transformed_text", type=str, required=False, default="")
        ]