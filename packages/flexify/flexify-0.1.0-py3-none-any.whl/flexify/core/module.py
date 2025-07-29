"""
Abstract base class for executable modules.
実行可能なモジュールの抽象基底クラス。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type
from .status import Status
from .param_info import ParamInfo
from .exceptions import FlexifyException


class Module(ABC):
    """
    Abstract base class for all executable modules in Flexify.
    Flexifyのすべての実行可能モジュールの抽象基底クラス。
    
    This class defines the interface that all modules must implement.
    Modules process data from a session dictionary and return the updated session.
    このクラスは、すべてのモジュールが実装しなければならないインターフェースを定義します。
    モジュールはセッション辞書からデータを処理し、更新されたセッションを返します。
    
    Attributes:
        status (Status): Current execution status of the module
    属性:
        status (Status): モジュールの現在の実行ステータス
    """
    
    def __init__(self):
        """
        Initialize the module with PENDING status.
        モジュールをPENDINGステータスで初期化します。
        """
        self.status = Status.PENDING
    
    @abstractmethod
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the module's main logic.
        モジュールのメインロジックを実行します。
        
        This method must be implemented by all subclasses. It receives a session
        dictionary containing input data and should return an updated session
        dictionary with output data.
        このメソッドはすべてのサブクラスで実装される必要があります。入力データを含む
        セッション辞書を受け取り、出力データを含む更新されたセッション辞書を返す必要があります。
        
        Args:
            session (Dict[str, Any]): Input session data
        引数:
            session (Dict[str, Any]): 入力セッションデータ
            
        Returns:
            Dict[str, Any]: Updated session data with outputs
        戻り値:
            Dict[str, Any]: 出力を含む更新されたセッションデータ
            
        Raises:
            FlexifyException: If an error occurs during execution
        例外:
            FlexifyException: 実行中にエラーが発生した場合
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_param_info(cls) -> List[ParamInfo]:
        """
        Get parameter information for this module.
        このモジュールのパラメータ情報を取得します。
        
        This method must be implemented by all subclasses to define
        what parameters the module requires as input and provides as output.
        このメソッドは、モジュールが入力として必要とし、出力として提供する
        パラメータを定義するために、すべてのサブクラスで実装される必要があります。
        
        Returns:
            List[ParamInfo]: List of parameter information objects
        戻り値:
            List[ParamInfo]: パラメータ情報オブジェクトのリスト
        """
        pass
    
    def validate_inputs(self, session: Dict[str, Any]) -> None:
        """
        Validate that required inputs are present in the session.
        必要な入力がセッションに存在することを検証します。
        
        Args:
            session (Dict[str, Any]): Session data to validate
        引数:
            session (Dict[str, Any]): 検証するセッションデータ
            
        Raises:
            FlexifyException: If required inputs are missing or invalid
        例外:
            FlexifyException: 必要な入力が欠落しているか無効な場合
        """
        param_infos = self.get_param_info()
        
        for param in param_infos:
            # Handle input parameters - they should directly match session keys
            if param.name in session:
                if not param.validate_value(session[param.name]):
                    raise FlexifyException(
                        f"Input '{param.name}' has invalid type. Expected {param.type.__name__}",
                        module_name=self.__class__.__name__
                    )
            elif param.required and not param.name.startswith("output_"):
                # If it's required and not an output parameter, it must be present
                raise FlexifyException(
                    f"Required input '{param.name}' not found in session",
                    module_name=self.__class__.__name__
                )
    
    def safe_execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the module with error handling and status management.
        エラーハンドリングとステータス管理を伴ってモジュールを実行します。
        
        Args:
            session (Dict[str, Any]): Input session data
        引数:
            session (Dict[str, Any]): 入力セッションデータ
            
        Returns:
            Dict[str, Any]: Updated session data
        戻り値:
            Dict[str, Any]: 更新されたセッションデータ
            
        Raises:
            FlexifyException: If execution fails
        例外:
            FlexifyException: 実行が失敗した場合
        """
        try:
            self.status = Status.RUNNING
            self.validate_inputs(session)
            result = self.execute(session)
            self.status = Status.SUCCESS
            return result
        except FlexifyException:
            self.status = Status.FAILED
            raise
        except Exception as e:
            self.status = Status.FAILED
            raise FlexifyException(
                f"Unexpected error during module execution: {str(e)}",
                module_name=self.__class__.__name__,
                original_error=e
            )