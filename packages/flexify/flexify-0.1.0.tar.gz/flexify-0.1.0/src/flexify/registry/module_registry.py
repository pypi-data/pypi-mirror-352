"""
Module registry for discovering and managing modules.
モジュールの検出と管理のためのモジュールレジストリ。
"""

from typing import Dict, Type, Optional, List
import importlib
import inspect
from ..core import Module


class ModuleRegistry:
    """
    Registry for managing available modules.
    利用可能なモジュールを管理するレジストリ。
    
    This class provides functionality to register, discover, and retrieve
    module classes by name or class path.
    このクラスは、名前またはクラスパスによってモジュールクラスを
    登録、検出、取得する機能を提供します。
    """
    
    def __init__(self):
        """
        Initialize an empty module registry.
        空のモジュールレジストリを初期化します。
        """
        self._modules: Dict[str, Type[Module]] = {}
    
    def register(self, name: str, module_class: Type[Module]) -> None:
        """
        Register a module class with a given name.
        指定された名前でモジュールクラスを登録します。
        
        Args:
            name (str): Name to register the module under
            module_class (Type[Module]): Module class to register
        引数:
            name (str): モジュールを登録する名前
            module_class (Type[Module]): 登録するモジュールクラス
            
        Raises:
            ValueError: If name is already registered or class is not a Module
        例外:
            ValueError: 名前がすでに登録されているか、クラスがModuleでない場合
        """
        if name in self._modules:
            raise ValueError(f"Module '{name}' is already registered")
        
        if not issubclass(module_class, Module):
            raise ValueError(f"{module_class} is not a subclass of Module")
        
        self._modules[name] = module_class
    
    def get(self, name: str) -> Optional[Type[Module]]:
        """
        Get a module class by name.
        名前でモジュールクラスを取得します。
        
        Args:
            name (str): Name of the module to retrieve
        引数:
            name (str): 取得するモジュールの名前
            
        Returns:
            Optional[Type[Module]]: Module class if found, None otherwise
        戻り値:
            Optional[Type[Module]]: 見つかった場合はモジュールクラス、そうでない場合はNone
        """
        return self._modules.get(name)
    
    def get_or_import(self, class_path: str) -> Type[Module]:
        """
        Get a module by name or import it by class path.
        名前でモジュールを取得するか、クラスパスでインポートします。
        
        Args:
            class_path (str): Module name or full class path (e.g., "package.module.ClassName")
        引数:
            class_path (str): モジュール名または完全なクラスパス（例："package.module.ClassName"）
            
        Returns:
            Type[Module]: Module class
        戻り値:
            Type[Module]: モジュールクラス
            
        Raises:
            ImportError: If module cannot be imported
            ValueError: If class is not a Module subclass
        例外:
            ImportError: モジュールをインポートできない場合
            ValueError: クラスがModuleのサブクラスでない場合
        """
        # First try to get from registry
        module_class = self.get(class_path)
        if module_class:
            return module_class
        
        # Try to import the module
        try:
            if '.' in class_path:
                module_name, class_name = class_path.rsplit('.', 1)
                module = importlib.import_module(module_name)
                module_class = getattr(module, class_name)
            else:
                # Assume it's just a class name in the current module
                raise ImportError(f"Cannot import '{class_path}' without module path")
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Cannot import module '{class_path}': {str(e)}")
        
        if not issubclass(module_class, Module):
            raise ValueError(f"{class_path} is not a subclass of Module")
        
        return module_class
    
    def list_modules(self) -> List[str]:
        """
        List all registered module names.
        登録されているすべてのモジュール名をリストします。
        
        Returns:
            List[str]: List of registered module names
        戻り値:
            List[str]: 登録されているモジュール名のリスト
        """
        return list(self._modules.keys())
    
    def clear(self) -> None:
        """
        Clear all registered modules.
        すべての登録されたモジュールをクリアします。
        """
        self._modules.clear()


# Global registry instance
_global_registry = ModuleRegistry()


def get_global_registry() -> ModuleRegistry:
    """
    Get the global module registry instance.
    グローバルモジュールレジストリインスタンスを取得します。
    
    Returns:
        ModuleRegistry: Global registry instance
    戻り値:
        ModuleRegistry: グローバルレジストリインスタンス
    """
    return _global_registry