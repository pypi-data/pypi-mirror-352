"""
Simple implementation of the Runner interface.
Runnerインターフェースのシンプルな実装。
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from .runner import Runner
from .models import WorkflowConfig, RunnerStatus, ModuleConfig
from ..core import Module, FlexifyException, Status
from ..registry import ModuleRegistry, get_global_registry


class SimpleRunner(Runner):
    """
    Simple sequential workflow runner.
    シンプルなシーケンシャルワークフローランナー。
    
    This runner executes modules in sequential order as defined in the workflow
    configuration. It provides basic error handling and status tracking.
    このランナーは、ワークフロー設定で定義された順序でモジュールを
    順次実行します。基本的なエラーハンドリングとステータス追跡を提供します。
    """
    
    def __init__(self, registry: Optional[ModuleRegistry] = None):
        """
        Initialize SimpleRunner with optional module registry.
        オプションのモジュールレジストリでSimpleRunnerを初期化します。
        
        Args:
            registry (Optional[ModuleRegistry]): Module registry to use, defaults to global
        引数:
            registry (Optional[ModuleRegistry]): 使用するモジュールレジストリ、デフォルトはグローバル
        """
        self.registry = registry or get_global_registry()
        self._current_status: Optional[RunnerStatus] = None
        self._modules: Dict[str, Module] = {}
    
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
        path = Path(workflow_path)
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {workflow_path}")
        
        # Load configuration from file
        config = self._load_config_from_file(path)
        
        # Run with the loaded configuration
        return self.run_from_config(config)
    
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
        # Initialize status
        self._current_status = RunnerStatus(
            workflow_name=config.name,
            start_time=datetime.now()
        )
        
        # Initialize session with initial data
        session = config.initial_session.copy()
        
        # Clear previous modules
        self._modules.clear()
        
        try:
            # Execute modules in sequence
            for module_config in config.modules:
                session = self._execute_module(module_config, session)
                self._current_status.completed_modules.append(module_config.name)
            
            # Mark workflow as completed
            self._current_status.end_time = datetime.now()
            self._current_status.current_module = None
            
            return session
            
        except Exception as e:
            # Mark workflow as failed
            self._current_status.end_time = datetime.now()
            if isinstance(e, FlexifyException):
                raise
            else:
                raise FlexifyException(
                    f"Workflow execution failed: {str(e)}",
                    module_name=self._current_status.current_module,
                    original_error=e
                )
    
    def get_status(self) -> RunnerStatus:
        """
        Get the current execution status.
        現在の実行ステータスを取得します。
        
        Returns:
            RunnerStatus: Current status of the workflow execution
        戻り値:
            RunnerStatus: ワークフロー実行の現在のステータス
        """
        if self._current_status is None:
            return RunnerStatus(workflow_name="No workflow")
        return self._current_status
    
    def _load_config_from_file(self, path: Path) -> WorkflowConfig:
        """
        Load workflow configuration from a file.
        ファイルからワークフロー設定を読み込みます。
        
        Args:
            path (Path): Path to the configuration file
        引数:
            path (Path): 設定ファイルへのパス
            
        Returns:
            WorkflowConfig: Loaded workflow configuration
        戻り値:
            WorkflowConfig: 読み込まれたワークフロー設定
            
        Raises:
            ValueError: If file format is not supported or content is invalid
        例外:
            ValueError: ファイル形式がサポートされていないか、内容が無効な場合
        """
        try:
            content = path.read_text()
            
            if path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(content)
            elif path.suffix.lower() == '.json':
                data = json.loads(content)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
            
            # Convert dictionary to WorkflowConfig
            return self._dict_to_workflow_config(data)
            
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse configuration file: {str(e)}")
    
    def _dict_to_workflow_config(self, data: Dict[str, Any]) -> WorkflowConfig:
        """
        Convert dictionary to WorkflowConfig object.
        辞書をWorkflowConfigオブジェクトに変換します。
        
        Args:
            data (Dict[str, Any]): Configuration dictionary
        引数:
            data (Dict[str, Any]): 設定辞書
            
        Returns:
            WorkflowConfig: Workflow configuration object
        戻り値:
            WorkflowConfig: ワークフロー設定オブジェクト
        """
        modules = []
        for module_data in data.get('modules', []):
            module_config = ModuleConfig(
                name=module_data['name'],
                class_name=module_data['class_name'],
                params=module_data.get('params', {}),
                inputs=module_data.get('inputs', {}),
                outputs=module_data.get('outputs', {})
            )
            modules.append(module_config)
        
        return WorkflowConfig(
            name=data['name'],
            version=data.get('version', '1.0.0'),
            modules=modules,
            initial_session=data.get('initial_session', {})
        )
    
    def _execute_module(self, config: ModuleConfig, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single module with the given configuration.
        指定された設定で単一のモジュールを実行します。
        
        Args:
            config (ModuleConfig): Module configuration
            session (Dict[str, Any]): Current session state
        引数:
            config (ModuleConfig): モジュール設定
            session (Dict[str, Any]): 現在のセッション状態
            
        Returns:
            Dict[str, Any]: Updated session state
        戻り値:
            Dict[str, Any]: 更新されたセッション状態
        """
        # Update status
        self._current_status.current_module = config.name
        self._current_status.module_statuses[config.name] = Status.PENDING
        
        try:
            # Get or create module instance
            if config.name not in self._modules:
                module_class = self.registry.get_or_import(config.class_name)
                self._modules[config.name] = module_class()
            
            module = self._modules[config.name]
            
            # Prepare module session with mapped inputs
            module_session = {}
            
            # If no input mapping is specified, use session directly
            if config.inputs:
                for module_key, session_key in config.inputs.items():
                    if session_key in session:
                        module_session[module_key] = session[session_key]
            else:
                # Copy all session data to module session
                module_session.update(session)
            
            # Add parameters to module session (overrides session values)
            module_session.update(config.params)
            
            # Update module status
            self._current_status.module_statuses[config.name] = Status.RUNNING
            
            # Execute module
            result_session = module.safe_execute(module_session)
            
            # Map outputs back to main session
            if config.outputs:
                for module_key, session_key in config.outputs.items():
                    if module_key in result_session:
                        session[session_key] = result_session[module_key]
            else:
                # If no output mapping, update session with all results
                session.update(result_session)
            
            # Update status
            self._current_status.module_statuses[config.name] = module.status
            
            return session
            
        except Exception as e:
            self._current_status.module_statuses[config.name] = Status.FAILED
            if isinstance(e, FlexifyException):
                raise
            else:
                raise FlexifyException(
                    f"Module execution failed: {str(e)}",
                    module_name=config.name,
                    original_error=e
                )