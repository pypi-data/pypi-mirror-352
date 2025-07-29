"""
Parameter information data class for modules.
モジュールのパラメータ情報データクラス。
"""

from dataclasses import dataclass, field
from typing import Any, Type, Optional, Dict


@dataclass
class ParamInfo:
    """
    Holds information about a module parameter.
    モジュールパラメータに関する情報を保持します。
    
    This class is used to define and validate parameters that modules
    require for execution or provide as output.
    このクラスは、モジュールが実行に必要とする、または出力として提供する
    パラメータを定義し検証するために使用されます。
    
    Attributes:
        name (str): The name of the parameter
        type (Type): The expected type of the parameter
        required (bool): Whether the parameter is required
        default (Any): Default value if parameter is not provided
        description (str): Human-readable description of the parameter
    属性:
        name (str): パラメータの名前
        type (Type): パラメータの期待される型
        required (bool): パラメータが必須かどうか
        default (Any): パラメータが提供されない場合のデフォルト値
        description (str): パラメータの人間が読める説明
    """
    
    name: str
    type: Type
    required: bool = True
    default: Any = None
    description: str = ""
    
    def __post_init__(self):
        """
        Validate parameter consistency after initialization.
        初期化後にパラメータの整合性を検証します。
        
        Raises:
            ValueError: If parameter configuration is invalid
        例外:
            ValueError: パラメータ設定が無効な場合
        """
        # Allow None as a valid default value for optional parameters
        pass
    
    def validate_value(self, value: Any) -> bool:
        """
        Validate if a value matches the expected type.
        値が期待される型と一致するかを検証します。
        
        Args:
            value (Any): The value to validate
        引数:
            value (Any): 検証する値
            
        Returns:
            bool: True if value is valid, False otherwise
        戻り値:
            bool: 値が有効な場合はTrue、そうでない場合はFalse
        """
        if value is None:
            return not self.required
        
        # Handle special case for dict type hint
        if self.type == dict or self.type == Dict:
            return isinstance(value, dict)
        
        # Handle numeric type conversions
        if self.type in (int, float):
            try:
                # Try to convert to the target type
                self.type(value)
                return True
            except (ValueError, TypeError):
                return False
        
        return isinstance(value, self.type)