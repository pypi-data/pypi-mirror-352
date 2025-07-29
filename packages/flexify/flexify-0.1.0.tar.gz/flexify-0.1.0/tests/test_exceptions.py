"""
Tests for exception classes.
例外クラスのテスト。
"""

import pytest
from flexify.core import FlexifyException


class TestFlexifyException:
    """
    Test cases for FlexifyException exception.
    FlexifyException例外のテストケース。
    """
    
    def test_flexify_exception_basic(self):
        """
        Test basic FlexifyException creation and message.
        基本的なFlexifyExceptionの作成とメッセージをテストします。
        """
        error = FlexifyException("Test error message")
        assert str(error) == "Test error message"
        assert error.module_name is None
        assert error.original_error is None
    
    def test_flexify_exception_with_module_name(self):
        """
        Test FlexifyException with module name.
        モジュール名を持つFlexifyExceptionをテストします。
        """
        error = FlexifyException("Test error", module_name="TestModule")
        assert str(error) == "[TestModule] Test error"
        assert error.module_name == "TestModule"
    
    def test_flexify_exception_with_original_error(self):
        """
        Test FlexifyException with original exception.
        元の例外を持つFlexifyExceptionをテストします。
        """
        original = ValueError("Original error")
        error = FlexifyException("Wrapped error", original_error=original)
        assert error.original_error == original
        assert isinstance(error.original_error, ValueError)
    
    def test_flexify_exception_inheritance(self):
        """
        Test that FlexifyException inherits from Exception.
        FlexifyExceptionがExceptionを継承していることをテストします。
        """
        error = FlexifyException("Test error")
        assert isinstance(error, Exception)
    
    def test_flexify_exception_raising(self):
        """
        Test raising and catching FlexifyException.
        FlexifyExceptionの発生とキャッチをテストします。
        """
        with pytest.raises(FlexifyException) as exc_info:
            raise FlexifyException("Test error", module_name="TestModule")
        
        assert "Test error" in str(exc_info.value)
        assert exc_info.value.module_name == "TestModule"