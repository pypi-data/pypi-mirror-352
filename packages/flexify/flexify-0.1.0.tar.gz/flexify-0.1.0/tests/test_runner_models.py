"""
Tests for runner data models.
ランナーデータモデルのテスト。
"""

import pytest
from datetime import datetime
from flexify.runner import ModuleConfig, WorkflowConfig, RunnerStatus
from flexify.core import Status


class TestModuleConfig:
    """
    Test cases for ModuleConfig data class.
    ModuleConfigデータクラスのテストケース。
    """
    
    def test_module_config_creation_minimal(self):
        """
        Test creation of ModuleConfig with minimal parameters.
        最小限のパラメータでのModuleConfigの作成をテストします。
        """
        config = ModuleConfig(
            name="test_module",
            class_name="TestModule"
        )
        
        assert config.name == "test_module"
        assert config.class_name == "TestModule"
        assert config.params == {}
        assert config.inputs == {}
        assert config.outputs == {}
    
    def test_module_config_creation_full(self):
        """
        Test creation of ModuleConfig with all parameters.
        すべてのパラメータでのModuleConfigの作成をテストします。
        """
        params = {"param1": "value1", "param2": 42}
        inputs = {"input_key": "session_key"}
        outputs = {"output_key": "result_key"}
        
        config = ModuleConfig(
            name="full_module",
            class_name="package.module.FullModule",
            params=params,
            inputs=inputs,
            outputs=outputs
        )
        
        assert config.name == "full_module"
        assert config.class_name == "package.module.FullModule"
        assert config.params == params
        assert config.inputs == inputs
        assert config.outputs == outputs


class TestWorkflowConfig:
    """
    Test cases for WorkflowConfig data class.
    WorkflowConfigデータクラスのテストケース。
    """
    
    def test_workflow_config_creation_minimal(self):
        """
        Test creation of WorkflowConfig with minimal parameters.
        最小限のパラメータでのWorkflowConfigの作成をテストします。
        """
        config = WorkflowConfig(name="test_workflow")
        
        assert config.name == "test_workflow"
        assert config.version == "1.0.0"
        assert config.modules == []
        assert config.initial_session == {}
    
    def test_workflow_config_creation_full(self):
        """
        Test creation of WorkflowConfig with all parameters.
        すべてのパラメータでのWorkflowConfigの作成をテストします。
        """
        module1 = ModuleConfig(name="module1", class_name="Module1")
        module2 = ModuleConfig(name="module2", class_name="Module2")
        modules = [module1, module2]
        initial_session = {"key": "value"}
        
        config = WorkflowConfig(
            name="full_workflow",
            version="2.0.0",
            modules=modules,
            initial_session=initial_session
        )
        
        assert config.name == "full_workflow"
        assert config.version == "2.0.0"
        assert config.modules == modules
        assert len(config.modules) == 2
        assert config.initial_session == initial_session


class TestRunnerStatus:
    """
    Test cases for RunnerStatus data class.
    RunnerStatusデータクラスのテストケース。
    """
    
    def test_runner_status_creation_minimal(self):
        """
        Test creation of RunnerStatus with minimal parameters.
        最小限のパラメータでのRunnerStatusの作成をテストします。
        """
        status = RunnerStatus(workflow_name="test_workflow")
        
        assert status.workflow_name == "test_workflow"
        assert status.current_module is None
        assert status.completed_modules == []
        assert status.module_statuses == {}
        assert isinstance(status.start_time, datetime)
        assert status.end_time is None
    
    def test_runner_status_creation_full(self):
        """
        Test creation of RunnerStatus with all parameters.
        すべてのパラメータでのRunnerStatusの作成をテストします。
        """
        start_time = datetime.now()
        end_time = datetime.now()
        module_statuses = {
            "module1": Status.SUCCESS,
            "module2": Status.RUNNING
        }
        
        status = RunnerStatus(
            workflow_name="full_workflow",
            current_module="module2",
            completed_modules=["module1"],
            module_statuses=module_statuses,
            start_time=start_time,
            end_time=end_time
        )
        
        assert status.workflow_name == "full_workflow"
        assert status.current_module == "module2"
        assert status.completed_modules == ["module1"]
        assert status.module_statuses == module_statuses
        assert status.start_time == start_time
        assert status.end_time == end_time
    
    def test_is_running_true(self):
        """
        Test is_running returns True when workflow is running.
        ワークフローが実行中の場合、is_runningがTrueを返すことをテストします。
        """
        status = RunnerStatus(
            workflow_name="test",
            current_module="module1",
            end_time=None
        )
        
        assert status.is_running() is True
    
    def test_is_running_false_completed(self):
        """
        Test is_running returns False when workflow is completed.
        ワークフローが完了した場合、is_runningがFalseを返すことをテストします。
        """
        status = RunnerStatus(
            workflow_name="test",
            current_module=None,
            end_time=datetime.now()
        )
        
        assert status.is_running() is False
    
    def test_is_running_false_not_started(self):
        """
        Test is_running returns False when workflow hasn't started.
        ワークフローが開始していない場合、is_runningがFalseを返すことをテストします。
        """
        status = RunnerStatus(
            workflow_name="test",
            current_module=None,
            end_time=None
        )
        
        assert status.is_running() is False
    
    def test_is_completed_true(self):
        """
        Test is_completed returns True when workflow is completed.
        ワークフローが完了した場合、is_completedがTrueを返すことをテストします。
        """
        status = RunnerStatus(
            workflow_name="test",
            end_time=datetime.now()
        )
        
        assert status.is_completed() is True
    
    def test_is_completed_false(self):
        """
        Test is_completed returns False when workflow is not completed.
        ワークフローが完了していない場合、is_completedがFalseを返すことをテストします。
        """
        status = RunnerStatus(
            workflow_name="test",
            end_time=None
        )
        
        assert status.is_completed() is False