"""
Simple hello module for flexify package.
flexifyパッケージ用のシンプルなhelloモジュール。
"""


def say_hello(name: str = "World") -> str:
    """
    Returns a greeting message for the given name.
    指定された名前に対する挨拶メッセージを返します。
    
    Args:
        name (str, optional): The name to greet. Defaults to "World".
                              挨拶する名前。デフォルトは"World"。
    
    Returns:
        str: A greeting message.
             挨拶メッセージ。
    """
    return f"Hello, {name}!"


def say_goodbye(name: str = "World") -> str:
    """
    Returns a farewell message for the given name.
    指定された名前に対するお別れのメッセージを返します。
    
    Args:
        name (str, optional): The name to say goodbye to. Defaults to "World".
                              お別れを言う名前。デフォルトは"World"。
    
    Returns:
        str: A farewell message.
             お別れのメッセージ。
    """
    return f"Goodbye, {name}!"


def get_greeting_info() -> dict:
    """
    Returns information about available greeting functions.
    利用可能な挨拶機能に関する情報を返します。
    
    Returns:
        dict: Information about greeting functions.
              挨拶機能に関する情報。
    """
    return {
        "available_functions": ["say_hello", "say_goodbye"],
        "default_name": "World",
        "package": "flexify"
    }