"""
Control flow modules for Flexify framework.
Flexifyフレームワークの制御フローモジュール。
"""

from typing import Dict, Any, List, Optional, Union
from .module import Module
from .param_info import ParamInfo
from .status import Status
from .exceptions import FlexifyException
from ..runner.models import WorkflowConfig, ModuleConfig


class LoopModule(Module):
    """
    Module that iterates over an array and executes sub-workflow for each element.
    配列を反復し、各要素に対してサブワークフローを実行するモジュール。
    
    This module takes an array input and executes a defined sub-workflow
    for each element, setting the current element to a specified parameter.
    このモジュールは配列入力を受け取り、各要素に対して定義された
    サブワークフローを実行し、現在の要素を指定されたパラメータに設定します。
    """
    
    def __init__(self):
        """
        Initialize LoopModule.
        LoopModuleを初期化します。
        """
        super().__init__()
        self._runner = None
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute loop iteration over array elements.
        配列要素に対するループ反復を実行します。
        
        Args:
            session (Dict[str, Any]): Session containing array and loop configuration
        引数:
            session (Dict[str, Any]): 配列とループ設定を含むセッション
            
        Returns:
            Dict[str, Any]: Updated session with loop results
        戻り値:
            Dict[str, Any]: ループ結果で更新されたセッション
        """
        # Get loop parameters
        array = session.get("array", [])
        item_name = session.get("item_name", "item")
        index_name = session.get("index_name", "index")
        workflow_config = session.get("workflow", None)
        
        if not isinstance(array, list):
            raise FlexifyException(
                f"Loop array must be a list, got {type(array).__name__}",
                module_name=self.__class__.__name__
            )
        
        if not workflow_config:
            raise FlexifyException(
                "Loop workflow configuration is required",
                module_name=self.__class__.__name__
            )
        
        # Initialize runner if needed
        if self._runner is None:
            from ..runner import SimpleRunner
            self._runner = SimpleRunner()
        
        # Store loop results
        results = []
        
        # Execute workflow for each item
        for index, item in enumerate(array):
            # Create loop context
            loop_session = session.copy()
            loop_session[item_name] = item
            loop_session[index_name] = index
            
            try:
                # Parse workflow config if it's a dict
                if isinstance(workflow_config, dict):
                    modules = []
                    for module_data in workflow_config.get('modules', []):
                        module_config = ModuleConfig(
                            name=module_data['name'],
                            class_name=module_data['class_name'],
                            params=module_data.get('params', {}),
                            inputs=module_data.get('inputs', {}),
                            outputs=module_data.get('outputs', {})
                        )
                        modules.append(module_config)
                    
                    config = WorkflowConfig(
                        name=f"loop_iteration_{index}",
                        modules=modules,
                        initial_session=loop_session
                    )
                else:
                    config = workflow_config
                    config.initial_session = loop_session
                
                # Execute sub-workflow
                result = self._runner.run_from_config(config)
                results.append(result)
                
            except Exception as e:
                raise FlexifyException(
                    f"Loop iteration {index} failed: {str(e)}",
                    module_name=self.__class__.__name__,
                    original_error=e
                )
        
        # Store results in session
        session["loop_results"] = results
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        """
        Get parameter information for LoopModule.
        LoopModuleのパラメータ情報を取得します。
        
        Returns:
            List[ParamInfo]: List of parameter information
        戻り値:
            List[ParamInfo]: パラメータ情報のリスト
        """
        return [
            ParamInfo(
                name="array",
                type=list,
                required=True,
                description="Array to iterate over"
            ),
            ParamInfo(
                name="item_name",
                type=str,
                required=False,
                default="item",
                description="Name of the parameter to store current item"
            ),
            ParamInfo(
                name="index_name",
                type=str,
                required=False,
                default="index",
                description="Name of the parameter to store current index"
            ),
            ParamInfo(
                name="workflow",
                type=dict,
                required=True,
                description="Workflow configuration to execute for each item"
            ),
            ParamInfo(
                name="loop_results",
                type=list,
                required=False,
                default=[],
                description="Output: Results from each iteration"
            )
        ]


class CaseModule(Module):
    """
    Module that executes different workflows based on condition matching.
    条件マッチングに基づいて異なるワークフローを実行するモジュール。
    
    This module evaluates a value against defined cases and executes
    the corresponding workflow for the matching case.
    このモジュールは値を定義されたケースと照合し、
    マッチするケースに対応するワークフローを実行します。
    """
    
    def __init__(self):
        """
        Initialize CaseModule.
        CaseModuleを初期化します。
        """
        super().__init__()
        self._runner = None
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute workflow based on case matching.
        ケースマッチングに基づいてワークフローを実行します。
        
        Args:
            session (Dict[str, Any]): Session containing value and cases
        引数:
            session (Dict[str, Any]): 値とケースを含むセッション
            
        Returns:
            Dict[str, Any]: Updated session with case execution results
        戻り値:
            Dict[str, Any]: ケース実行結果で更新されたセッション
        """
        # Get case parameters
        value = session.get("value")
        cases = session.get("cases", {})
        default_workflow = session.get("default", None)
        
        if not isinstance(cases, dict):
            raise FlexifyException(
                f"Cases must be a dictionary, got {type(cases).__name__}",
                module_name=self.__class__.__name__
            )
        
        # Initialize runner if needed
        if self._runner is None:
            from ..runner import SimpleRunner
            self._runner = SimpleRunner()
        
        # Find matching case
        matched_case = None
        workflow_config = None
        
        # Check for exact match
        if value in cases:
            matched_case = value
            workflow_config = cases[value]
        # Check for default case
        elif default_workflow:
            matched_case = "default"
            workflow_config = default_workflow
        
        if workflow_config is None:
            # No matching case, return session as-is
            session["matched_case"] = None
            return session
        
        # Execute matched workflow
        try:
            # Parse workflow config if it's a dict
            if isinstance(workflow_config, dict):
                modules = []
                for module_data in workflow_config.get('modules', []):
                    module_config = ModuleConfig(
                        name=module_data['name'],
                        class_name=module_data['class_name'],
                        params=module_data.get('params', {}),
                        inputs=module_data.get('inputs', {}),
                        outputs=module_data.get('outputs', {})
                    )
                    modules.append(module_config)
                
                config = WorkflowConfig(
                    name=f"case_{matched_case}",
                    modules=modules,
                    initial_session=session.copy()
                )
            else:
                config = workflow_config
                config.initial_session = session.copy()
            
            # Execute workflow
            result = self._runner.run_from_config(config)
            
            # Update session with results
            session.update(result)
            session["matched_case"] = matched_case
            
        except Exception as e:
            raise FlexifyException(
                f"Case '{matched_case}' execution failed: {str(e)}",
                module_name=self.__class__.__name__,
                original_error=e
            )
        
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        """
        Get parameter information for CaseModule.
        CaseModuleのパラメータ情報を取得します。
        
        Returns:
            List[ParamInfo]: List of parameter information
        戻り値:
            List[ParamInfo]: パラメータ情報のリスト
        """
        return [
            ParamInfo(
                name="value",
                type=Any,
                required=True,
                description="Value to match against cases"
            ),
            ParamInfo(
                name="cases",
                type=dict,
                required=True,
                description="Dictionary of case values to workflow configurations"
            ),
            ParamInfo(
                name="default",
                type=dict,
                required=False,
                default=None,
                description="Default workflow configuration if no case matches"
            ),
            ParamInfo(
                name="matched_case",
                type=str,
                required=False,
                default=None,
                description="Output: The case that was matched"
            )
        ]