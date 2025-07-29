"""
Tests for SimpleRunner.
SimpleRunnerのテスト。
"""

import pytest
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List
from flexify.core import Module, ParamInfo, Status, FlexifyException
from flexify.runner import SimpleRunner, WorkflowConfig, ModuleConfig
from flexify.registry import ModuleRegistry


class AddModule(Module):
    """Module that adds two numbers."""
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        a = session.get("a", 0)
        b = session.get("b", 0)
        session["result"] = a + b
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        return [
            ParamInfo(name="a", type=int, required=True),
            ParamInfo(name="b", type=int, required=True),
            ParamInfo(name="result", type=int, required=False, default=0)
        ]


class MultiplyModule(Module):
    """Module that multiplies a number by a factor."""
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        value = session.get("value", 0)
        factor = session.get("factor", 1)
        session["result"] = value * factor
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        return [
            ParamInfo(name="value", type=int, required=True),
            ParamInfo(name="factor", type=int, required=False, default=1),
            ParamInfo(name="result", type=int, required=False, default=0)
        ]


class ErrorModule(Module):
    """Module that always raises an error."""
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        raise ValueError("Test error from module")
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        return []


class TestSimpleRunner:
    """
    Test cases for SimpleRunner.
    SimpleRunnerのテストケース。
    """
    
    @pytest.fixture
    def registry(self):
        """Create a test registry with modules."""
        registry = ModuleRegistry()
        registry.register("AddModule", AddModule)
        registry.register("MultiplyModule", MultiplyModule)
        registry.register("ErrorModule", ErrorModule)
        return registry
    
    @pytest.fixture
    def runner(self, registry):
        """Create a SimpleRunner with test registry."""
        return SimpleRunner(registry=registry)
    
    def test_runner_initialization(self, runner):
        """
        Test runner initialization.
        ランナーの初期化をテストします。
        """
        status = runner.get_status()
        assert status.workflow_name == "No workflow"
        assert not status.is_running()
        assert not status.is_completed()
    
    def test_run_from_config_simple(self, runner):
        """
        Test running a simple workflow from config.
        設定から簡単なワークフローを実行することをテストします。
        """
        config = WorkflowConfig(
            name="test_workflow",
            modules=[
                ModuleConfig(
                    name="add_step",
                    class_name="AddModule",
                    params={"a": 5, "b": 3}
                )
            ]
        )
        
        result = runner.run_from_config(config)
        assert result["result"] == 8
        
        status = runner.get_status()
        assert status.workflow_name == "test_workflow"
        assert status.is_completed()
        assert not status.is_running()
        assert "add_step" in status.completed_modules
        assert status.module_statuses["add_step"] == Status.SUCCESS
    
    def test_run_from_config_with_initial_session(self, runner):
        """
        Test running workflow with initial session data.
        初期セッションデータを持つワークフローの実行をテストします。
        """
        config = WorkflowConfig(
            name="test_workflow",
            initial_session={"a": 10, "b": 20},
            modules=[
                ModuleConfig(
                    name="add_step",
                    class_name="AddModule"
                )
            ]
        )
        
        result = runner.run_from_config(config)
        assert result["result"] == 30
    
    def test_run_from_config_with_input_output_mapping(self, runner):
        """
        Test workflow with input/output mapping.
        入出力マッピングを持つワークフローをテストします。
        """
        config = WorkflowConfig(
            name="mapped_workflow",
            initial_session={"x": 5, "y": 3},
            modules=[
                ModuleConfig(
                    name="add_step",
                    class_name="AddModule",
                    inputs={"a": "x", "b": "y"},
                    outputs={"result": "sum"}
                )
            ]
        )
        
        result = runner.run_from_config(config)
        assert result["sum"] == 8
        assert "x" in result  # Original values preserved
        assert "y" in result
    
    def test_run_from_config_multiple_modules(self, runner):
        """
        Test workflow with multiple modules.
        複数のモジュールを持つワークフローをテストします。
        """
        config = WorkflowConfig(
            name="multi_step_workflow",
            initial_session={"a": 5, "b": 3},
            modules=[
                ModuleConfig(
                    name="add_step",
                    class_name="AddModule"
                ),
                ModuleConfig(
                    name="multiply_step",
                    class_name="MultiplyModule",
                    inputs={"value": "result"},
                    params={"factor": 2},
                    outputs={"result": "final_result"}
                )
            ]
        )
        
        result = runner.run_from_config(config)
        assert result["result"] == 8  # From add_step
        assert result["final_result"] == 16  # 8 * 2
        
        status = runner.get_status()
        assert len(status.completed_modules) == 2
        assert status.module_statuses["add_step"] == Status.SUCCESS
        assert status.module_statuses["multiply_step"] == Status.SUCCESS
    
    def test_run_from_config_error_handling(self, runner):
        """
        Test error handling in workflow execution.
        ワークフロー実行でのエラーハンドリングをテストします。
        """
        config = WorkflowConfig(
            name="error_workflow",
            modules=[
                ModuleConfig(
                    name="error_step",
                    class_name="ErrorModule"
                )
            ]
        )
        
        with pytest.raises(FlexifyException) as exc_info:
            runner.run_from_config(config)
        
        assert "Test error from module" in str(exc_info.value)
        
        status = runner.get_status()
        assert status.is_completed()  # Workflow marked as completed even on error
        assert status.module_statuses["error_step"] == Status.FAILED
    
    def test_run_from_yaml_file(self, runner, tmp_path):
        """
        Test running workflow from YAML file.
        YAMLファイルからワークフローを実行することをテストします。
        """
        workflow_yaml = """
name: yaml_workflow
version: 1.0.0
initial_session:
  a: 10
  b: 5
modules:
  - name: add_numbers
    class_name: AddModule
"""
        
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(workflow_yaml)
        
        result = runner.run(str(yaml_file))
        assert result["result"] == 15
        
        status = runner.get_status()
        assert status.workflow_name == "yaml_workflow"
    
    def test_run_from_json_file(self, runner, tmp_path):
        """
        Test running workflow from JSON file.
        JSONファイルからワークフローを実行することをテストします。
        """
        workflow_json = {
            "name": "json_workflow",
            "version": "2.0.0",
            "initial_session": {"a": 7, "b": 3},
            "modules": [
                {
                    "name": "add_numbers",
                    "class_name": "AddModule"
                }
            ]
        }
        
        json_file = tmp_path / "workflow.json"
        json_file.write_text(json.dumps(workflow_json))
        
        result = runner.run(str(json_file))
        assert result["result"] == 10
        
        status = runner.get_status()
        assert status.workflow_name == "json_workflow"
    
    def test_run_file_not_found(self, runner):
        """
        Test error when workflow file not found.
        ワークフローファイルが見つからない場合のエラーをテストします。
        """
        with pytest.raises(FileNotFoundError) as exc_info:
            runner.run("nonexistent_file.yaml")
        
        assert "Workflow file not found" in str(exc_info.value)
    
    def test_run_unsupported_file_format(self, runner, tmp_path):
        """
        Test error with unsupported file format.
        サポートされていないファイル形式でのエラーをテストします。
        """
        txt_file = tmp_path / "workflow.txt"
        txt_file.write_text("not a workflow")
        
        with pytest.raises(ValueError) as exc_info:
            runner.run(str(txt_file))
        
        assert "Unsupported file format" in str(exc_info.value)
    
    def test_run_invalid_yaml(self, runner, tmp_path):
        """
        Test error with invalid YAML content.
        無効なYAML内容でのエラーをテストします。
        """
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text("invalid: yaml: content:")
        
        with pytest.raises(ValueError) as exc_info:
            runner.run(str(yaml_file))
        
        assert "Failed to parse configuration file" in str(exc_info.value)
    
    def test_module_instance_reuse(self, runner):
        """
        Test that module instances are reused in the same workflow.
        同じワークフロー内でモジュールインスタンスが再利用されることをテストします。
        """
        config = WorkflowConfig(
            name="reuse_workflow",
            modules=[
                ModuleConfig(
                    name="step1",
                    class_name="AddModule",
                    params={"a": 1, "b": 2}
                ),
                ModuleConfig(
                    name="step2",
                    class_name="AddModule",  # Same class
                    params={"a": 3, "b": 4}
                )
            ]
        )
        
        runner.run_from_config(config)
        
        # Both steps should have their own instances
        assert len(runner._modules) == 2
        assert "step1" in runner._modules
        assert "step2" in runner._modules
    
    def test_get_or_import_with_full_path(self, runner):
        """
        Test importing module with full path.
        完全パスでのモジュールインポートをテストします。
        """
        config = WorkflowConfig(
            name="import_workflow",
            modules=[
                ModuleConfig(
                    name="add_step",
                    class_name="tests.test_simple_runner.AddModule",
                    params={"a": 5, "b": 5}
                )
            ]
        )
        
        result = runner.run_from_config(config)
        assert result["result"] == 10