"""
Tests for ModuleRegistry.
ModuleRegistryのテスト。
"""

import pytest
from typing import Dict, Any
from flexify.core import Module, ParamInfo
from flexify.registry import ModuleRegistry, get_global_registry


class TestModuleA(Module):
    """Test module A for registry testing."""
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        session["result"] = "A"
        return session
    
    @classmethod
    def get_param_info(cls):
        return []


class TestModuleB(Module):
    """Test module B for registry testing."""
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        session["result"] = "B"
        return session
    
    @classmethod
    def get_param_info(cls):
        return []


class NotAModule:
    """Not a module class for testing."""
    pass


class TestModuleRegistry:
    """
    Test cases for ModuleRegistry.
    ModuleRegistryのテストケース。
    """
    
    def test_registry_initialization(self):
        """
        Test registry starts empty.
        レジストリが空で開始することをテストします。
        """
        registry = ModuleRegistry()
        assert registry.list_modules() == []
    
    def test_register_module(self):
        """
        Test registering a module.
        モジュールの登録をテストします。
        """
        registry = ModuleRegistry()
        registry.register("module_a", TestModuleA)
        
        assert "module_a" in registry.list_modules()
        assert registry.get("module_a") == TestModuleA
    
    def test_register_multiple_modules(self):
        """
        Test registering multiple modules.
        複数のモジュールの登録をテストします。
        """
        registry = ModuleRegistry()
        registry.register("module_a", TestModuleA)
        registry.register("module_b", TestModuleB)
        
        modules = registry.list_modules()
        assert len(modules) == 2
        assert "module_a" in modules
        assert "module_b" in modules
    
    def test_register_duplicate_name_raises_error(self):
        """
        Test registering duplicate name raises error.
        重複する名前の登録がエラーを発生させることをテストします。
        """
        registry = ModuleRegistry()
        registry.register("module_a", TestModuleA)
        
        with pytest.raises(ValueError) as exc_info:
            registry.register("module_a", TestModuleB)
        
        assert "already registered" in str(exc_info.value)
    
    def test_register_non_module_raises_error(self):
        """
        Test registering non-module class raises error.
        モジュールでないクラスの登録がエラーを発生させることをテストします。
        """
        registry = ModuleRegistry()
        
        with pytest.raises(ValueError) as exc_info:
            registry.register("not_module", NotAModule)
        
        assert "not a subclass of Module" in str(exc_info.value)
    
    def test_get_nonexistent_module(self):
        """
        Test getting nonexistent module returns None.
        存在しないモジュールの取得がNoneを返すことをテストします。
        """
        registry = ModuleRegistry()
        assert registry.get("nonexistent") is None
    
    def test_get_or_import_from_registry(self):
        """
        Test get_or_import retrieves from registry first.
        get_or_importが最初にレジストリから取得することをテストします。
        """
        registry = ModuleRegistry()
        registry.register("test_module", TestModuleA)
        
        module_class = registry.get_or_import("test_module")
        assert module_class == TestModuleA
    
    def test_get_or_import_with_class_path(self):
        """
        Test get_or_import with full class path.
        完全なクラスパスでのget_or_importをテストします。
        """
        registry = ModuleRegistry()
        
        module_class = registry.get_or_import("tests.test_module_registry.TestModuleA")
        assert module_class == TestModuleA
    
    def test_get_or_import_invalid_path_raises_error(self):
        """
        Test get_or_import with invalid path raises error.
        無効なパスでのget_or_importがエラーを発生させることをテストします。
        """
        registry = ModuleRegistry()
        
        with pytest.raises(ImportError) as exc_info:
            registry.get_or_import("nonexistent.module.Class")
        
        assert "Cannot import module" in str(exc_info.value)
    
    def test_get_or_import_without_module_path_raises_error(self):
        """
        Test get_or_import without module path raises error.
        モジュールパスなしのget_or_importがエラーを発生させることをテストします。
        """
        registry = ModuleRegistry()
        
        with pytest.raises(ImportError) as exc_info:
            registry.get_or_import("JustClassName")
        
        assert "without module path" in str(exc_info.value)
    
    def test_get_or_import_non_module_class_raises_error(self):
        """
        Test get_or_import with non-Module class raises error.
        Module以外のクラスでのget_or_importがエラーを発生させることをテストします。
        """
        registry = ModuleRegistry()
        
        with pytest.raises(ValueError) as exc_info:
            registry.get_or_import("tests.test_module_registry.NotAModule")
        
        assert "not a subclass of Module" in str(exc_info.value)
    
    def test_clear_registry(self):
        """
        Test clearing the registry.
        レジストリのクリアをテストします。
        """
        registry = ModuleRegistry()
        registry.register("module_a", TestModuleA)
        registry.register("module_b", TestModuleB)
        
        assert len(registry.list_modules()) == 2
        
        registry.clear()
        assert len(registry.list_modules()) == 0
    
    def test_global_registry(self):
        """
        Test global registry instance.
        グローバルレジストリインスタンスをテストします。
        """
        registry1 = get_global_registry()
        registry2 = get_global_registry()
        
        # Should be the same instance
        assert registry1 is registry2