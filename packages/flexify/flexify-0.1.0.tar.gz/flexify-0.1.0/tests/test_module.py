"""
Tests for Module abstract base class.
Module抽象基底クラスのテスト。
"""

import pytest
from typing import Dict, Any, List
from flexify.core import Module, ParamInfo, Status, FlexifyException


class TestModuleImpl(Module):
    """
    Test implementation of Module for testing purposes.
    テスト目的のModuleのテスト実装。
    """
    
    def __init__(self):
        super().__init__()
        self._should_raise_module_error = False
        self._should_raise_generic_error = False
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simple test execution that adds output_value to session.
        session に output_value を追加する単純なテスト実行。
        """
        if self._should_raise_module_error:
            raise FlexifyException("Test module error", module_name=self.__class__.__name__)
        
        if self._should_raise_generic_error:
            raise ValueError("Test generic error")
        
        input_value = session.get("input_value", 0)
        session["output_value"] = input_value * 2
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        """
        Define test parameters.
        テストパラメータを定義します。
        """
        return [
            ParamInfo(
                name="input_value",
                type=int,
                required=True,
                description="Input value to double"
            ),
            ParamInfo(
                name="output_value",
                type=int,
                required=False,
                default=0,
                description="Doubled output value"
            )
        ]


class ErrorModule(Module):
    """
    Module that raises an error for testing error handling.
    エラーハンドリングをテストするためにエラーを発生させるモジュール。
    """
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Always raises an error.
        常にエラーを発生させます。
        """
        raise ValueError("Test error")
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        """
        No parameters needed for error module.
        エラーモジュールにはパラメータは不要です。
        """
        return []


class TestModuleClass:
    """
    Test cases for Module abstract base class.
    Module抽象基底クラスのテストケース。
    """
    
    def test_module_initialization(self):
        """
        Test module initialization with PENDING status.
        PENDINGステータスでのモジュール初期化をテストします。
        """
        module = TestModuleImpl()
        assert module.status == Status.PENDING
    
    def test_execute_success(self):
        """
        Test successful module execution.
        成功するモジュール実行をテストします。
        """
        module = TestModuleImpl()
        session = {"input_value": 5}
        result = module.execute(session)
        
        assert result["output_value"] == 10
        assert "input_value" in result
    
    def test_safe_execute_success(self):
        """
        Test safe_execute with successful execution.
        成功する実行でのsafe_executeをテストします。
        """
        module = TestModuleImpl()
        session = {"input_value": 5}
        
        result = module.safe_execute(session)
        
        assert module.status == Status.SUCCESS
        assert result["output_value"] == 10
    
    def test_safe_execute_missing_required_input(self):
        """
        Test safe_execute with missing required input.
        必須入力が欠落している場合のsafe_executeをテストします。
        """
        module = TestModuleImpl()
        session = {}  # Missing required "input_value"
        
        with pytest.raises(FlexifyException) as exc_info:
            module.safe_execute(session)
        
        assert module.status == Status.FAILED
        assert "Required input 'input_value' not found" in str(exc_info.value)
        assert exc_info.value.module_name == "TestModuleImpl"
    
    def test_safe_execute_invalid_type(self):
        """
        Test safe_execute with invalid input type.
        無効な入力型でのsafe_executeをテストします。
        """
        module = TestModuleImpl()
        session = {"input_value": "not an int"}
        
        with pytest.raises(FlexifyException) as exc_info:
            module.safe_execute(session)
        
        assert module.status == Status.FAILED
        assert "invalid type" in str(exc_info.value)
    
    def test_safe_execute_error_handling(self):
        """
        Test safe_execute error handling.
        safe_executeのエラーハンドリングをテストします。
        """
        module = ErrorModule()
        session = {}
        
        with pytest.raises(FlexifyException) as exc_info:
            module.safe_execute(session)
        
        assert module.status == Status.FAILED
        assert "Unexpected error" in str(exc_info.value)
        assert exc_info.value.module_name == "ErrorModule"
        assert isinstance(exc_info.value.original_error, ValueError)
    
    def test_validate_inputs(self):
        """
        Test validate_inputs correctly validates input parameters.
        validate_inputsが入力パラメータを正しく検証することをテストします。
        """
        module = TestModuleImpl()
        
        # Test with correct input
        session = {"input_value": 42}
        module.validate_inputs(session)  # Should not raise
        
        # Test with missing input
        session = {}
        with pytest.raises(FlexifyException) as exc_info:
            module.validate_inputs(session)
        assert "Required input 'input_value' not found" in str(exc_info.value)
    
    def test_abstract_methods_not_implemented(self):
        """
        Test that abstract methods must be implemented.
        抽象メソッドが実装される必要があることをテストします。
        """
        with pytest.raises(TypeError):
            # Cannot instantiate abstract class without implementing abstract methods
            Module()
    
    def test_get_param_info(self):
        """
        Test get_param_info returns correct parameter information.
        get_param_infoが正しいパラメータ情報を返すことをテストします。
        """
        params = TestModuleImpl.get_param_info()
        
        assert len(params) == 2
        assert params[0].name == "input_value"
        assert params[0].type == int
        assert params[0].required is True
        assert params[1].name == "output_value"
        assert params[1].required is False
    
    def test_module_status_property(self):
        """Test module status property."""
        module = TestModuleImpl()
        
        # Initial status should be PENDING
        assert module.status == Status.PENDING
        
        # Should be able to set status
        module.status = Status.RUNNING
        assert module.status == Status.RUNNING
    
    def test_module_str_representation(self):
        """Test module string representation."""
        module = TestModuleImpl()
        str_repr = str(module)
        assert "TestModuleImpl" in str_repr
    
    def test_validate_inputs_with_edge_cases(self):
        """Test validate_inputs with various edge cases."""
        module = TestModuleImpl()
        
        # Test with numeric conversion
        session = {"input_value": "42"}  # String that can convert to int
        # Should not raise exception due to numeric conversion
        module.validate_inputs(session)
        
        # Test with float conversion
        session = {"input_value": 42.5}  # Float value
        module.validate_inputs(session)
        
        # Test with None for optional parameter
        session = {"input_value": 42, "output_value": None}
        # Should not raise exception for optional param with None
        module.validate_inputs(session)
    
    def test_safe_execute_with_module_exception(self):
        """Test safe_execute handling of FlexifyException."""
        module = TestModuleImpl()
        module._should_raise_module_error = True
        
        session = {"input_value": 10}
        
        with pytest.raises(FlexifyException):
            module.safe_execute(session)
        
        # Status should be FAILED
        assert module.status == Status.FAILED
    
    def test_safe_execute_with_generic_exception(self):
        """Test safe_execute handling of generic exceptions."""
        module = TestModuleImpl()
        module._should_raise_generic_error = True
        
        session = {"input_value": 10}
        
        with pytest.raises(FlexifyException) as exc_info:
            module.safe_execute(session)
        
        # Should wrap generic exception in FlexifyException
        assert "Unexpected error during module execution" in str(exc_info.value)
        assert exc_info.value.original_error is not None
        assert module.status == Status.FAILED