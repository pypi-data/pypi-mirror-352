"""
Test module for flexify.hello module.
flexify.helloモジュールのテストモジュール。
"""

import pytest
from flexify.hello import say_hello, say_goodbye, get_greeting_info


class TestSayHello:
    """
    Test class for say_hello function.
    say_hello関数のテストクラス。
    """
    
    def test_say_hello_default(self):
        """
        Test say_hello with default parameter.
        デフォルトパラメータでのsay_helloのテスト。
        """
        result = say_hello()
        assert result == "Hello, World!"
    
    def test_say_hello_with_name(self):
        """
        Test say_hello with specific name.
        特定の名前でのsay_helloのテスト。
        """
        result = say_hello("Alice")
        assert result == "Hello, Alice!"
    
    def test_say_hello_with_empty_string(self):
        """
        Test say_hello with empty string.
        空文字でのsay_helloのテスト。
        """
        result = say_hello("")
        assert result == "Hello, !"
    
    def test_say_hello_return_type(self):
        """
        Test that say_hello returns a string.
        say_helloが文字列を返すことのテスト。
        """
        result = say_hello("Test")
        assert isinstance(result, str)


class TestSayGoodbye:
    """
    Test class for say_goodbye function.
    say_goodbye関数のテストクラス。
    """
    
    def test_say_goodbye_default(self):
        """
        Test say_goodbye with default parameter.
        デフォルトパラメータでのsay_goodbyeのテスト。
        """
        result = say_goodbye()
        assert result == "Goodbye, World!"
    
    def test_say_goodbye_with_name(self):
        """
        Test say_goodbye with specific name.
        特定の名前でのsay_goodbyeのテスト。
        """
        result = say_goodbye("Bob")
        assert result == "Goodbye, Bob!"
    
    def test_say_goodbye_with_empty_string(self):
        """
        Test say_goodbye with empty string.
        空文字でのsay_goodbyeのテスト。
        """
        result = say_goodbye("")
        assert result == "Goodbye, !"
    
    def test_say_goodbye_return_type(self):
        """
        Test that say_goodbye returns a string.
        say_goodbyeが文字列を返すことのテスト。
        """
        result = say_goodbye("Test")
        assert isinstance(result, str)


class TestGetGreetingInfo:
    """
    Test class for get_greeting_info function.
    get_greeting_info関数のテストクラス。
    """
    
    def test_get_greeting_info_structure(self):
        """
        Test that get_greeting_info returns expected structure.
        get_greeting_infoが期待される構造を返すことのテスト。
        """
        result = get_greeting_info()
        assert isinstance(result, dict)
        assert "available_functions" in result
        assert "default_name" in result
        assert "package" in result
    
    def test_get_greeting_info_content(self):
        """
        Test that get_greeting_info returns expected content.
        get_greeting_infoが期待される内容を返すことのテスト。
        """
        result = get_greeting_info()
        assert result["available_functions"] == ["say_hello", "say_goodbye"]
        assert result["default_name"] == "World"
        assert result["package"] == "flexify"
    
    def test_get_greeting_info_available_functions_type(self):
        """
        Test that available_functions is a list.
        available_functionsがリストであることのテスト。
        """
        result = get_greeting_info()
        assert isinstance(result["available_functions"], list)
        assert len(result["available_functions"]) == 2