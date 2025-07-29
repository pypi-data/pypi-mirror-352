"""
Module execution status enumeration.
モジュール実行ステータスの列挙型。
"""

from enum import Enum, auto


class Status(Enum):
    """
    Represents the execution status of a module.
    モジュールの実行ステータスを表す列挙型。
    
    Attributes:
        PENDING: Module is waiting to be executed
        RUNNING: Module is currently executing
        SUCCESS: Module completed successfully
        FAILED: Module execution failed
        SKIPPED: Module execution was skipped
    属性:
        PENDING: モジュールは実行待ち状態
        RUNNING: モジュールは実行中
        SUCCESS: モジュールは正常に完了
        FAILED: モジュールの実行が失敗
        SKIPPED: モジュールの実行がスキップされた
    """
    
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()