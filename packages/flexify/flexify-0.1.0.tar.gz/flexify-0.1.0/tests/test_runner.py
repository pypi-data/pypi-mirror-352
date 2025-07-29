"""
Tests for Runner abstract base class.
Runner抽象基底クラスのテスト。
"""

import pytest
from typing import Dict, Any
from flexify.runner import Runner, WorkflowConfig, RunnerStatus


class ConcreteRunner(Runner):
    """
    Concrete implementation of Runner for testing.
    テスト用のRunnerの具体的な実装。
    """
    
    def __init__(self):
        self.status = RunnerStatus(workflow_name="test")
        self.last_config = None
        self.last_path = None
    
    def run(self, workflow_path: str) -> Dict[str, Any]:
        """Test implementation of run."""
        self.last_path = workflow_path
        return {"result": "from_path"}
    
    def run_from_config(self, config: WorkflowConfig) -> Dict[str, Any]:
        """Test implementation of run_from_config."""
        self.last_config = config
        self.status.workflow_name = config.name
        return {"result": "from_config"}
    
    def get_status(self) -> RunnerStatus:
        """Test implementation of get_status."""
        return self.status


class TestRunner:
    """
    Test cases for Runner abstract base class.
    Runner抽象基底クラスのテストケース。
    """
    
    def test_cannot_instantiate_abstract_runner(self):
        """
        Test that abstract Runner cannot be instantiated.
        抽象Runnerがインスタンス化できないことをテストします。
        """
        with pytest.raises(TypeError):
            Runner()
    
    def test_concrete_runner_implementation(self):
        """
        Test that concrete Runner can be instantiated and used.
        具体的なRunnerがインスタンス化して使用できることをテストします。
        """
        runner = ConcreteRunner()
        
        # Test run method
        result = runner.run("test.yaml")
        assert result == {"result": "from_path"}
        assert runner.last_path == "test.yaml"
        
        # Test run_from_config method
        config = WorkflowConfig(name="test_workflow")
        result = runner.run_from_config(config)
        assert result == {"result": "from_config"}
        assert runner.last_config == config
        
        # Test get_status method
        status = runner.get_status()
        assert status.workflow_name == "test_workflow"
    
    def test_runner_interface_methods(self):
        """
        Test that Runner interface defines all required methods.
        Runnerインターフェースが必要なすべてのメソッドを定義していることをテストします。
        """
        # Check that Runner has all required abstract methods
        assert hasattr(Runner, 'run')
        assert hasattr(Runner, 'run_from_config')
        assert hasattr(Runner, 'get_status')
        
        # Check that methods are abstract
        assert getattr(Runner.run, '__isabstractmethod__', False)
        assert getattr(Runner.run_from_config, '__isabstractmethod__', False)
        assert getattr(Runner.get_status, '__isabstractmethod__', False)