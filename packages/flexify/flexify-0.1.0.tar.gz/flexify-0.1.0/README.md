# 🚀 Flexify

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)](https://github.com/yourusername/flexify)

**Flexify** is a lightweight, modular task processing framework for Python that makes it incredibly easy to build and execute workflows! 🎯

## ✨ Why Flexify?

Do you find yourself:
- 😩 Writing the same processing patterns over and over?
- 🔧 Hard-coding workflows that are difficult to modify?
- 📊 Struggling to visualize and track complex data pipelines?
- 🏗️ Dealing with heavyweight workflow engines that are overkill for your needs?

**Flexify makes it simple!** Define reusable modules, describe your workflow in YAML or JSON, and let Flexify handle the rest!

## 🎯 Key Features

- **🧩 Modular Design**: Create reusable processing modules that can be combined in any way
- **📝 Simple Configuration**: Define workflows in human-readable YAML or JSON files
- **🔄 Flexible Data Flow**: Easy parameter mapping between modules
- **📊 Status Tracking**: Monitor workflow execution and module status in real-time
- **🐍 Pure Python**: No complex dependencies or external services required
- **🧪 Well-Tested**: 97% test coverage with comprehensive test suite
- **📚 Rich Examples**: Ready-to-use example modules for text processing and math operations

## 🚀 Quick Start

### Installation

```bash
pip install flexify
```

### Create Your First Module

```python
from typing import Dict, Any, List
from flexify.core import Module, ParamInfo

class GreetingModule(Module):
    """A simple module that creates greetings."""
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        name = session.get("name", "World")
        greeting = f"Hello, {name}!"
        session["greeting"] = greeting
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        return [
            ParamInfo(name="name", type=str, required=False, default="World"),
            ParamInfo(name="greeting", type=str, required=False, default="")
        ]
```

### Define a Workflow

Create a workflow file `greeting_workflow.yaml`:

```yaml
name: greeting_workflow
version: 1.0.0

modules:
  - name: greet_step
    class_name: your_module.GreetingModule
    params:
      name: "Flexify User"
```

### Run Your Workflow

```python
from flexify.runner import SimpleRunner

runner = SimpleRunner()
result = runner.run("greeting_workflow.yaml")
print(result["greeting"])  # Output: Hello, Flexify User!
```

## 📖 Documentation

### Module Development

Modules are the building blocks of Flexify workflows. Each module:
- Inherits from the `Module` base class
- Implements an `execute()` method that processes data
- Defines parameters using `get_param_info()`
- Maintains its execution status

### Workflow Configuration

Workflows can be defined in YAML or JSON with:
- **name**: Workflow identifier
- **modules**: List of modules to execute in sequence
- **initial_session**: Starting data for the workflow

### Advanced Features

- **Parameter Mapping**: Route data between modules using input/output mappings
- **Module Registry**: Dynamically discover and load modules
- **Error Handling**: Comprehensive error tracking and reporting
- **Status Monitoring**: Real-time workflow execution status

### Error Handling

Flexify provides comprehensive error handling through the `FlexifyException` exception:

```python
try:
    runner = SimpleRunner()
    result = runner.run("workflow.yaml")
except FlexifyException as e:
    print(f"Error: {e}")                    # [ModuleName] Error message
    print(f"Failed module: {e.module_name}") # ModuleName
    if e.original_error:
        print(f"Original error: {e.original_error}")
```

Common error scenarios:
- **Missing required parameters**: `Required input 'param_name' not found`
- **Invalid parameter types**: `Input 'param_name' has invalid type`
- **Module execution failures**: Captures and wraps any exceptions during execution
- **Import errors**: When specified module classes cannot be found

### Module Discovery

Modules are loaded dynamically using their full class path:

```yaml
modules:
  - name: calculator
    class_name: "flexify.examples.math_modules.CalculatorModule"
```

The `ModuleRegistry.get_or_import()` method handles:
- Dynamic importing of module classes
- Validation that classes inherit from `Module`
- Caching of loaded modules for performance

## 🛠️ Built-in Modules

### Core Control Flow Modules
- `LoopModule`: Iterate over arrays and execute sub-workflows for each element
- `CaseModule`: Execute different workflows based on condition matching

### Text Processing Modules
- `TextReaderModule`: Read text files
- `TextTransformModule`: Transform text (upper, lower, title, reverse)
- `WordCountModule`: Calculate text statistics

### Math Operations Modules
- `CalculatorModule`: Basic arithmetic operations
- `StatisticsModule`: Calculate statistical measures
- `FibonacciModule`: Generate Fibonacci sequences

### Control Flow Examples

#### Loop Module
```yaml
modules:
  - name: process_array
    class_name: flexify.core.LoopModule
    params:
      workflow:
        modules:
          - name: square
            class_name: flexify.examples.math_modules.CalculatorModule
            params: {operation: multiply}
            inputs: {a: item, b: item}
    inputs:
      array: numbers
```

#### Case Module
```yaml
modules:
  - name: process_by_type
    class_name: flexify.core.CaseModule
    params:
      cases:
        add:
          modules: [{name: add_op, class_name: ..., params: {operation: add}}]
        multiply:
          modules: [{name: mult_op, class_name: ..., params: {operation: multiply}}]
    inputs:
      value: operation_type
```

## 💻 System Requirements

- **Python**: 3.10 or higher
- **Dependencies**: PyYAML for YAML support
- **OS**: Windows, macOS, Linux

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, fork the repository, and create pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with ❤️ using modern Python best practices and clean architecture principles.

---

**Ready to make your workflows flexible?** Get started with Flexify today! 🚀