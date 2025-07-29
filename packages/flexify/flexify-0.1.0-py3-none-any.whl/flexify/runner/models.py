"""
Data models for workflow configuration and runner status.
ワークフロー設定とランナーステータスのデータモデル。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..core import Status


@dataclass
class ModuleConfig:
    """
    Configuration for a single module in a workflow.
    ワークフロー内の単一モジュールの設定。
    
    Attributes:
        name (str): Unique name for this module instance
        class_name (str): Full class name or module path
        params (Dict[str, Any]): Parameters to pass to the module
        inputs (Dict[str, str]): Mapping of module inputs to session keys
        outputs (Dict[str, str]): Mapping of module outputs to session keys
    属性:
        name (str): このモジュールインスタンスの一意な名前
        class_name (str): 完全なクラス名またはモジュールパス
        params (Dict[str, Any]): モジュールに渡すパラメータ
        inputs (Dict[str, str]): モジュール入力からセッションキーへのマッピング
        outputs (Dict[str, str]): モジュール出力からセッションキーへのマッピング
    """
    
    name: str
    class_name: str
    params: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, str] = field(default_factory=dict)
    outputs: Dict[str, str] = field(default_factory=dict)


@dataclass
class WorkflowConfig:
    """
    Configuration for an entire workflow.
    ワークフロー全体の設定。
    
    Attributes:
        name (str): Name of the workflow
        version (str): Version of the workflow configuration
        modules (List[ModuleConfig]): List of modules to execute in order
        initial_session (Dict[str, Any]): Initial session data
    属性:
        name (str): ワークフローの名前
        version (str): ワークフロー設定のバージョン
        modules (List[ModuleConfig]): 順番に実行するモジュールのリスト
        initial_session (Dict[str, Any]): 初期セッションデータ
    """
    
    name: str
    version: str = "1.0.0"
    modules: List[ModuleConfig] = field(default_factory=list)
    initial_session: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunnerStatus:
    """
    Current status of a workflow execution.
    ワークフロー実行の現在のステータス。
    
    Attributes:
        workflow_name (str): Name of the executing workflow
        current_module (Optional[str]): Currently executing module name
        completed_modules (List[str]): List of completed module names
        module_statuses (Dict[str, Status]): Status of each module
        start_time (datetime): When the workflow started
        end_time (Optional[datetime]): When the workflow ended
    属性:
        workflow_name (str): 実行中のワークフローの名前
        current_module (Optional[str]): 現在実行中のモジュール名
        completed_modules (List[str]): 完了したモジュール名のリスト
        module_statuses (Dict[str, Status]): 各モジュールのステータス
        start_time (datetime): ワークフローが開始した時刻
        end_time (Optional[datetime]): ワークフローが終了した時刻
    """
    
    workflow_name: str
    current_module: Optional[str] = None
    completed_modules: List[str] = field(default_factory=list)
    module_statuses: Dict[str, Status] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    def is_running(self) -> bool:
        """
        Check if the workflow is still running.
        ワークフローがまだ実行中かどうかを確認します。
        
        Returns:
            bool: True if running, False otherwise
        戻り値:
            bool: 実行中の場合はTrue、そうでない場合はFalse
        """
        return self.end_time is None and self.current_module is not None
    
    def is_completed(self) -> bool:
        """
        Check if the workflow has completed.
        ワークフローが完了したかどうかを確認します。
        
        Returns:
            bool: True if completed, False otherwise
        戻り値:
            bool: 完了した場合はTrue、そうでない場合はFalse
        """
        return self.end_time is not None