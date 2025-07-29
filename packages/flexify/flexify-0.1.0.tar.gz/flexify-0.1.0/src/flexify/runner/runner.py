"""
Abstract base class for workflow runners.
ワークフローランナーの抽象基底クラス。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from .models import WorkflowConfig, RunnerStatus


class Runner(ABC):
    """
    Abstract interface for workflow execution.
    ワークフロー実行の抽象インターフェース。
    
    This interface defines the contract that all workflow runners must implement.
    Runners are responsible for executing workflows defined in configuration files
    or objects and managing the execution state.
    このインターフェースは、すべてのワークフローランナーが実装しなければならない
    契約を定義します。ランナーは設定ファイルまたはオブジェクトで定義された
    ワークフローを実行し、実行状態を管理する責任があります。
    """
    
    @abstractmethod
    def run(self, workflow_path: str) -> Dict[str, Any]:
        """
        Execute a workflow from a file path.
        ファイルパスからワークフローを実行します。
        
        Args:
            workflow_path (str): Path to the workflow configuration file
        引数:
            workflow_path (str): ワークフロー設定ファイルへのパス
            
        Returns:
            Dict[str, Any]: Final session state after workflow execution
        戻り値:
            Dict[str, Any]: ワークフロー実行後の最終セッション状態
            
        Raises:
            FileNotFoundError: If workflow file doesn't exist
            ValueError: If workflow configuration is invalid
            FlexifyException: If module execution fails
        例外:
            FileNotFoundError: ワークフローファイルが存在しない場合
            ValueError: ワークフロー設定が無効な場合
            FlexifyException: モジュール実行が失敗した場合
        """
        pass
    
    @abstractmethod
    def run_from_config(self, config: WorkflowConfig) -> Dict[str, Any]:
        """
        Execute a workflow from a configuration object.
        設定オブジェクトからワークフローを実行します。
        
        Args:
            config (WorkflowConfig): Workflow configuration object
        引数:
            config (WorkflowConfig): ワークフロー設定オブジェクト
            
        Returns:
            Dict[str, Any]: Final session state after workflow execution
        戻り値:
            Dict[str, Any]: ワークフロー実行後の最終セッション状態
            
        Raises:
            ValueError: If workflow configuration is invalid
            FlexifyException: If module execution fails
        例外:
            ValueError: ワークフロー設定が無効な場合
            FlexifyException: モジュール実行が失敗した場合
        """
        pass
    
    @abstractmethod
    def get_status(self) -> RunnerStatus:
        """
        Get the current execution status.
        現在の実行ステータスを取得します。
        
        Returns:
            RunnerStatus: Current status of the workflow execution
        戻り値:
            RunnerStatus: ワークフロー実行の現在のステータス
        """
        pass