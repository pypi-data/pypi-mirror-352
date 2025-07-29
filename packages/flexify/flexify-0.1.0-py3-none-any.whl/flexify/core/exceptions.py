"""
Exception classes for Flexify framework.
Flexifyフレームワークの例外クラス。
"""


class FlexifyException(Exception):
    """
    Base exception class for module execution errors.
    モジュール実行エラーの基底例外クラス。
    
    This exception is raised when a module encounters an error during execution.
    モジュールが実行中にエラーに遭遇した場合にこの例外が発生します。
    
    Attributes:
        module_name (str): The name of the module that encountered the error
        original_error (Exception): The original exception that caused this error
    属性:
        module_name (str): エラーが発生したモジュールの名前
        original_error (Exception): このエラーの原因となった元の例外
    """
    
    def __init__(self, message: str, module_name: str = None, original_error: Exception = None):
        """
        Initialize FlexifyException.
        FlexifyExceptionを初期化します。
        
        Args:
            message (str): Error message
            module_name (str, optional): Name of the module that encountered the error
            original_error (Exception, optional): Original exception that caused this error
        引数:
            message (str): エラーメッセージ
            module_name (str, optional): エラーが発生したモジュールの名前
            original_error (Exception, optional): このエラーの原因となった元の例外
        """
        super().__init__(message)
        self.module_name = module_name
        self.original_error = original_error
    
    def __str__(self) -> str:
        """
        Return string representation of the error.
        エラーの文字列表現を返します。
        
        Returns:
            str: Error message with module name if available
        戻り値:
            str: 利用可能な場合はモジュール名を含むエラーメッセージ
        """
        if self.module_name:
            return f"[{self.module_name}] {super().__str__()}"
        return super().__str__()