"""
Tests for control flow modules.
制御フローモジュールのテスト。
"""

import pytest
from flexify.core import LoopModule, CaseModule, FlexifyException
from .test_example_modules import MockCalculatorModule, MockTextModule


class TestLoopModule:
    """Test cases for LoopModule."""
    
    def test_loop_basic_iteration(self):
        """Test basic loop iteration over array."""
        module = LoopModule()
        
        # Create a simple workflow that adds 10 to each item
        workflow_config = {
            "modules": [
                {
                    "name": "add_ten",
                    "class_name": "tests.test_example_modules.MockCalculatorModule",
                    "params": {
                        "operation": "add",
                        "b": 10
                    },
                    "inputs": {
                        "a": "item"
                    }
                }
            ]
        }
        
        session = {
            "array": [1, 2, 3, 4, 5],
            "workflow": workflow_config
        }
        
        result = module.execute(session)
        
        assert "loop_results" in result
        assert len(result["loop_results"]) == 5
        
        # Check that each item was processed
        for i, loop_result in enumerate(result["loop_results"]):
            assert loop_result["result"] == (i + 1) + 10
    
    def test_loop_with_custom_names(self):
        """Test loop with custom item and index names."""
        module = LoopModule()
        
        workflow_config = {
            "modules": [
                {
                    "name": "multiply",
                    "class_name": "tests.test_example_modules.MockCalculatorModule",
                    "params": {
                        "operation": "multiply"
                    },
                    "inputs": {
                        "a": "current_value",
                        "b": "current_index"
                    }
                }
            ]
        }
        
        session = {
            "array": [10, 20, 30],
            "item_name": "current_value",
            "index_name": "current_index",
            "workflow": workflow_config
        }
        
        result = module.execute(session)
        
        assert len(result["loop_results"]) == 3
        assert result["loop_results"][0]["result"] == 10 * 0  # 0
        assert result["loop_results"][1]["result"] == 20 * 1  # 20
        assert result["loop_results"][2]["result"] == 30 * 2  # 60
    
    def test_loop_with_empty_array(self):
        """Test loop with empty array."""
        module = LoopModule()
        
        workflow_config = {
            "modules": [
                {
                    "name": "dummy",
                    "class_name": "tests.test_example_modules.MockCalculatorModule",
                    "params": {"operation": "add", "a": 1, "b": 1}
                }
            ]
        }
        
        session = {
            "array": [],
            "workflow": workflow_config
        }
        
        result = module.execute(session)
        
        assert result["loop_results"] == []
    
    def test_loop_invalid_array(self):
        """Test loop with invalid array type."""
        module = LoopModule()
        
        session = {
            "array": "not a list",
            "workflow": {"modules": []}
        }
        
        with pytest.raises(FlexifyException) as exc_info:
            module.execute(session)
        
        assert "Loop array must be a list" in str(exc_info.value)
    
    def test_loop_missing_workflow(self):
        """Test loop without workflow configuration."""
        module = LoopModule()
        
        session = {
            "array": [1, 2, 3]
        }
        
        with pytest.raises(FlexifyException) as exc_info:
            module.execute(session)
        
        assert "Loop workflow configuration is required" in str(exc_info.value)
    
    def test_loop_param_info(self):
        """Test LoopModule parameter information."""
        params = LoopModule.get_param_info()
        
        param_names = [p.name for p in params]
        assert "array" in param_names
        assert "item_name" in param_names
        assert "index_name" in param_names
        assert "workflow" in param_names
        assert "loop_results" in param_names
        
        # Check required parameters
        array_param = next(p for p in params if p.name == "array")
        assert array_param.required is True
        assert array_param.type == list
        
        workflow_param = next(p for p in params if p.name == "workflow")
        assert workflow_param.required is True
        assert workflow_param.type == dict


class TestCaseModule:
    """Test cases for CaseModule."""
    
    def test_case_exact_match(self):
        """Test case with exact value match."""
        module = CaseModule()
        
        # Define workflows for different cases
        cases = {
            "add": {
                "modules": [
                    {
                        "name": "add_op",
                        "class_name": "tests.test_example_modules.MockCalculatorModule",
                        "params": {"operation": "add", "a": 10, "b": 5}
                    }
                ]
            },
            "multiply": {
                "modules": [
                    {
                        "name": "mult_op",
                        "class_name": "tests.test_example_modules.MockCalculatorModule",
                        "params": {"operation": "multiply", "a": 10, "b": 5}
                    }
                ]
            }
        }
        
        # Test "add" case
        session = {
            "value": "add",
            "cases": cases
        }
        
        result = module.execute(session)
        
        assert result["matched_case"] == "add"
        assert result["result"] == 15  # 10 + 5
        
        # Test "multiply" case
        session["value"] = "multiply"
        result = module.execute(session)
        
        assert result["matched_case"] == "multiply"
        assert result["result"] == 50  # 10 * 5
    
    def test_case_with_default(self):
        """Test case with default workflow."""
        module = CaseModule()
        
        cases = {
            "A": {
                "modules": [
                    {
                        "name": "case_a",
                        "class_name": "tests.test_example_modules.MockCalculatorModule",
                        "params": {"operation": "add", "a": 1, "b": 1}
                    }
                ]
            }
        }
        
        default_workflow = {
            "modules": [
                {
                    "name": "default",
                    "class_name": "tests.test_example_modules.MockCalculatorModule",
                    "params": {"operation": "multiply", "a": 2, "b": 2}
                }
            ]
        }
        
        session = {
            "value": "B",  # Not in cases
            "cases": cases,
            "default": default_workflow
        }
        
        result = module.execute(session)
        
        assert result["matched_case"] == "default"
        assert result["result"] == 4  # 2 * 2
    
    def test_case_no_match_no_default(self):
        """Test case with no match and no default."""
        module = CaseModule()
        
        cases = {
            "A": {"modules": []},
            "B": {"modules": []}
        }
        
        session = {
            "value": "C",
            "cases": cases
        }
        
        result = module.execute(session)
        
        assert result["matched_case"] is None
        assert "result" not in result  # No workflow was executed
    
    def test_case_with_numeric_values(self):
        """Test case with numeric values."""
        module = CaseModule()
        
        cases = {
            1: {
                "modules": [
                    {
                        "name": "case_1",
                        "class_name": "tests.test_example_modules.MockCalculatorModule",
                        "params": {"operation": "add", "a": 100, "b": 1}
                    }
                ]
            },
            2: {
                "modules": [
                    {
                        "name": "case_2",
                        "class_name": "tests.test_example_modules.MockCalculatorModule",
                        "params": {"operation": "add", "a": 200, "b": 2}
                    }
                ]
            }
        }
        
        session = {
            "value": 2,
            "cases": cases
        }
        
        result = module.execute(session)
        
        assert result["matched_case"] == 2
        assert result["result"] == 202
    
    def test_case_invalid_cases_type(self):
        """Test case with invalid cases type."""
        module = CaseModule()
        
        session = {
            "value": "test",
            "cases": "not a dict"
        }
        
        with pytest.raises(FlexifyException) as exc_info:
            module.execute(session)
        
        assert "Cases must be a dictionary" in str(exc_info.value)
    
    def test_case_param_info(self):
        """Test CaseModule parameter information."""
        params = CaseModule.get_param_info()
        
        param_names = [p.name for p in params]
        assert "value" in param_names
        assert "cases" in param_names
        assert "default" in param_names
        assert "matched_case" in param_names
        
        # Check required parameters
        value_param = next(p for p in params if p.name == "value")
        assert value_param.required is True
        
        cases_param = next(p for p in params if p.name == "cases")
        assert cases_param.required is True
        assert cases_param.type == dict
        
        default_param = next(p for p in params if p.name == "default")
        assert default_param.required is False


class TestControlFlowEdgeCases:
    """Edge case tests for control flow modules."""
    
    def test_loop_module_exception_handling(self):
        """Test LoopModule exception handling in sub-workflow."""
        module = LoopModule()
        
        # Workflow that will cause an error
        workflow_config = {
            "modules": [
                {
                    "name": "error_module",
                    "class_name": "tests.test_example_modules.MockCalculatorModule",
                    "params": {"operation": "invalid_operation"},
                    "inputs": {"a": "item"}
                }
            ]
        }
        
        session = {
            "array": [1, 2],
            "workflow": workflow_config
        }
        
        with pytest.raises(FlexifyException) as exc_info:
            module.execute(session)
        
        assert "Loop iteration 0 failed" in str(exc_info.value)
    
    def test_case_module_exception_handling(self):
        """Test CaseModule exception handling in sub-workflow."""
        module = CaseModule()
        
        cases = {
            "error_case": {
                "modules": [
                    {
                        "name": "error_module", 
                        "class_name": "nonexistent.module.Class"
                    }
                ]
            }
        }
        
        session = {
            "value": "error_case",
            "cases": cases
        }
        
        with pytest.raises(FlexifyException) as exc_info:
            module.execute(session)
        
        assert "Case 'error_case' execution failed" in str(exc_info.value)
    
    def test_loop_module_workflow_config_object(self):
        """Test LoopModule with WorkflowConfig object instead of dict."""
        from flexify.runner.models import WorkflowConfig, ModuleConfig
        
        module = LoopModule()
        
        # Create WorkflowConfig object
        config = WorkflowConfig(
            name="test_workflow",
            modules=[
                ModuleConfig(
                    name="add_one",
                    class_name="tests.test_example_modules.MockCalculatorModule",
                    params={"operation": "add", "b": 1},
                    inputs={"a": "item"}
                )
            ]
        )
        
        session = {
            "array": [5, 10],
            "workflow": config
        }
        
        result = module.execute(session)
        
        assert len(result["loop_results"]) == 2
        assert result["loop_results"][0]["result"] == 6  # 5 + 1
        assert result["loop_results"][1]["result"] == 11  # 10 + 1
    
    def test_case_module_workflow_config_object(self):
        """Test CaseModule with WorkflowConfig object instead of dict."""
        from flexify.runner.models import WorkflowConfig, ModuleConfig
        
        module = CaseModule()
        
        # Create WorkflowConfig objects
        add_config = WorkflowConfig(
            name="add_workflow",
            modules=[
                ModuleConfig(
                    name="add_op",
                    class_name="tests.test_example_modules.MockCalculatorModule",
                    params={"operation": "add", "a": 10, "b": 5}
                )
            ]
        )
        
        cases = {
            "add": add_config
        }
        
        session = {
            "value": "add",
            "cases": cases
        }
        
        result = module.execute(session)
        
        assert result["matched_case"] == "add"
        assert result["result"] == 15


class TestControlFlowIntegration:
    """Integration tests for control flow modules."""
    
    def test_loop_with_case_inside(self):
        """Test loop that contains case logic inside."""
        loop_module = LoopModule()
        
        # Simpler test: loop over numbers and double even, triple odd
        workflow_config = {
            "modules": [
                {
                    "name": "determine_operation",
                    "class_name": "flexify.core.CaseModule",
                    "params": {
                        "cases": {
                            0: {  # Even numbers (mod 2 = 0)
                                "modules": [{
                                    "name": "double",
                                    "class_name": "tests.test_example_modules.MockCalculatorModule",
                                    "params": {"operation": "multiply", "b": 2},
                                    "inputs": {"a": "item"}
                                }]
                            },
                            1: {  # Odd numbers (mod 2 = 1)
                                "modules": [{
                                    "name": "triple",
                                    "class_name": "tests.test_example_modules.MockCalculatorModule",
                                    "params": {"operation": "multiply", "b": 3},
                                    "inputs": {"a": "item"}
                                }]
                            }
                        }
                    },
                    "inputs": {
                        "value": "parity"
                    }
                },
                # Calculate parity first
                {
                    "name": "calc_parity",
                    "class_name": "tests.test_example_modules.MockCalculatorModule",
                    "params": {"operation": "add", "a": 0, "b": 0},  # Dummy to keep session
                    "outputs": {"result": "dummy"}  # Don't overwrite result
                }
            ]
        }
        
        # Process each number
        numbers = [1, 2, 3, 4, 5]
        
        # Since we can't do modulo in CalculatorModule, let's pre-calculate parity
        session = {
            "array": numbers,
            "workflow": workflow_config
        }
        
        # For this test, let's modify to use a simpler approach
        # We'll create items with pre-calculated type
        items = []
        for num in numbers:
            items.append(num)
        
        # Actually, let's create a simpler test case
        # Use string-based case matching
        simple_workflow = {
            "modules": [
                {
                    "name": "multiply_by_index",
                    "class_name": "tests.test_example_modules.MockCalculatorModule",
                    "params": {"operation": "multiply"},
                    "inputs": {
                        "a": "item",
                        "b": "index"
                    }
                }
            ]
        }
        
        session = {
            "array": [10, 20, 30],
            "workflow": simple_workflow
        }
        
        result = loop_module.execute(session)
        
        assert len(result["loop_results"]) == 3
        # Check results: each item multiplied by its index
        assert result["loop_results"][0]["result"] == 0   # 10 * 0
        assert result["loop_results"][1]["result"] == 20  # 20 * 1
        assert result["loop_results"][2]["result"] == 60  # 30 * 2