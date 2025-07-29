"""
Tests for ParamInfo data class.
ParamInfoデータクラスのテスト。
"""

import pytest
from typing import Dict
from flexify.core import ParamInfo


class TestParamInfo:
    """
    Test cases for ParamInfo data class.
    ParamInfoデータクラスのテストケース。
    """
    
    def test_required_param_creation(self):
        """
        Test creation of a required parameter.
        必須パラメータの作成をテストします。
        """
        param = ParamInfo(
            name="test_param",
            type=str,
            required=True,
            description="Test parameter"
        )
        
        assert param.name == "test_param"
        assert param.type == str
        assert param.required is True
        assert param.default is None
        assert param.description == "Test parameter"
    
    def test_optional_param_with_default(self):
        """
        Test creation of an optional parameter with default value.
        デフォルト値を持つオプションパラメータの作成をテストします。
        """
        param = ParamInfo(
            name="optional_param",
            type=int,
            required=False,
            default=42,
            description="Optional parameter"
        )
        
        assert param.required is False
        assert param.default == 42
    
    def test_optional_param_with_none_default_allowed(self):
        """
        Test that optional parameter with None default is now allowed.
        デフォルト値がNoneのオプションパラメータが許可されることをテストします。
        """
        # This should not raise an error anymore
        param = ParamInfo(
            name="optional_param",
            type=str,
            required=False,
            default=None
        )
        
        assert param.default is None
        assert param.required is False
    
    def test_validate_value_with_correct_type(self):
        """
        Test value validation with correct type.
        正しい型での値検証をテストします。
        """
        param = ParamInfo(name="test", type=str, required=True)
        assert param.validate_value("hello") is True
        assert param.validate_value("") is True
    
    def test_validate_value_with_incorrect_type(self):
        """
        Test value validation with incorrect type.
        間違った型での値検証をテストします。
        """
        param = ParamInfo(name="test", type=str, required=True)
        assert param.validate_value(123) is False
        assert param.validate_value([]) is False
    
    def test_validate_value_none_for_required(self):
        """
        Test None validation for required parameter.
        必須パラメータのNone検証をテストします。
        """
        param = ParamInfo(name="test", type=str, required=True)
        assert param.validate_value(None) is False
    
    def test_validate_value_none_for_optional(self):
        """
        Test None validation for optional parameter.
        オプションパラメータのNone検証をテストします。
        """
        param = ParamInfo(name="test", type=str, required=False, default="default")
        assert param.validate_value(None) is True
    
    def test_validate_dict_type(self):
        """
        Test validation of dict type.
        dict型の検証をテストします。
        """
        param = ParamInfo(name="test", type=dict, required=True)
        assert param.validate_value({}) is True
        assert param.validate_value({"key": "value"}) is True
        assert param.validate_value("not a dict") is False
    
    def test_different_types(self):
        """
        Test ParamInfo with different types.
        異なる型でのParamInfoをテストします。
        """
        # Test with int (numeric conversion is now allowed)
        int_param = ParamInfo(name="int_param", type=int, required=True)
        assert int_param.validate_value(42) is True
        assert int_param.validate_value("42") is True  # String that can be converted to int
        
        # Test with list
        list_param = ParamInfo(name="list_param", type=list, required=True)
        assert list_param.validate_value([1, 2, 3]) is True
        assert list_param.validate_value("not a list") is False
        
        # Test with bool
        bool_param = ParamInfo(name="bool_param", type=bool, required=True)
        assert bool_param.validate_value(True) is True
        assert bool_param.validate_value(False) is True
        assert bool_param.validate_value(1) is False