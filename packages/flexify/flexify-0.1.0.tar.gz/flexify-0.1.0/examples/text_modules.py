"""
Text processing example modules.
テキスト処理のサンプルモジュール。
"""

from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from flexify.core import Module, ParamInfo


class TextReaderModule(Module):
    """
    Module that reads text from a file.
    ファイルからテキストを読み込むモジュール。
    
    This module reads the contents of a text file and stores it in the session.
    このモジュールはテキストファイルの内容を読み込み、セッションに保存します。
    """
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read text from file specified in session.
        セッションで指定されたファイルからテキストを読み込みます。
        """
        file_path = session.get("file_path", "")
        encoding = session.get("encoding", "utf-8")
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            session["content"] = content
            session["line_count"] = len(content.splitlines())
            session["char_count"] = len(content)
        except FileNotFoundError:
            session["error"] = f"File not found: {file_path}"
            session["content"] = ""
            session["line_count"] = 0
            session["char_count"] = 0
        except Exception as e:
            session["error"] = str(e)
            session["content"] = ""
            session["line_count"] = 0
            session["char_count"] = 0
        
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        """
        Get parameter information for TextReaderModule.
        TextReaderModuleのパラメータ情報を取得します。
        """
        return [
            ParamInfo(
                name="file_path",
                type=str,
                required=True,
                description="Path to the text file to read"
            ),
            ParamInfo(
                name="encoding",
                type=str,
                required=False,
                default="utf-8",
                description="File encoding"
            ),
            ParamInfo(
                name="content",
                type=str,
                required=False,
                default="",
                description="Output: File content"
            ),
            ParamInfo(
                name="line_count",
                type=int,
                required=False,
                default=0,
                description="Output: Number of lines"
            ),
            ParamInfo(
                name="char_count",
                type=int,
                required=False,
                default=0,
                description="Output: Number of characters"
            ),
            ParamInfo(
                name="error",
                type=str,
                required=False,
                default="",
                description="Output: Error message if any"
            )
        ]


class TextTransformModule(Module):
    """
    Module that transforms text based on specified operation.
    指定された操作に基づいてテキストを変換するモジュール。
    
    Supports operations: upper, lower, title, reverse
    サポートする操作: upper, lower, title, reverse
    """
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform text based on operation.
        操作に基づいてテキストを変換します。
        """
        text = session.get("text", "")
        operation = session.get("operation", "none")
        
        if operation == "upper":
            result = text.upper()
        elif operation == "lower":
            result = text.lower()
        elif operation == "title":
            result = text.title()
        elif operation == "reverse":
            result = text[::-1]
        else:
            result = text
        
        session["transformed_text"] = result
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        """
        Get parameter information for TextTransformModule.
        TextTransformModuleのパラメータ情報を取得します。
        """
        return [
            ParamInfo(
                name="text",
                type=str,
                required=True,
                description="Input text to transform"
            ),
            ParamInfo(
                name="operation",
                type=str,
                required=False,
                default="none",
                description="Transform operation: upper, lower, title, reverse"
            ),
            ParamInfo(
                name="transformed_text",
                type=str,
                required=False,
                default="",
                description="Output: Transformed text"
            )
        ]


class WordCountModule(Module):
    """
    Module that counts words and provides text statistics.
    単語を数えてテキスト統計を提供するモジュール。
    """
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Count words and calculate statistics.
        単語を数えて統計を計算します。
        """
        text = session.get("text", "")
        
        # Basic statistics
        words = text.split()
        word_count = len(words)
        unique_words = set(words)
        unique_word_count = len(unique_words)
        
        # Character statistics
        char_count = len(text)
        char_count_no_spaces = len(text.replace(" ", ""))
        
        # Line statistics
        lines = text.splitlines()
        line_count = len(lines)
        
        # Average calculations
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        avg_words_per_line = word_count / line_count if line_count > 0 else 0
        
        # Update session with results
        session.update({
            "word_count": word_count,
            "unique_word_count": unique_word_count,
            "char_count": char_count,
            "char_count_no_spaces": char_count_no_spaces,
            "line_count": line_count,
            "avg_word_length": round(avg_word_length, 2),
            "avg_words_per_line": round(avg_words_per_line, 2)
        })
        
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        """
        Get parameter information for WordCountModule.
        WordCountModuleのパラメータ情報を取得します。
        """
        return [
            ParamInfo(
                name="text",
                type=str,
                required=True,
                description="Input text to analyze"
            ),
            ParamInfo(
                name="word_count",
                type=int,
                required=False,
                default=0,
                description="Output: Total word count"
            ),
            ParamInfo(
                name="unique_word_count",
                type=int,
                required=False,
                default=0,
                description="Output: Unique word count"
            ),
            ParamInfo(
                name="char_count",
                type=int,
                required=False,
                default=0,
                description="Output: Total character count"
            ),
            ParamInfo(
                name="char_count_no_spaces",
                type=int,
                required=False,
                default=0,
                description="Output: Character count excluding spaces"
            ),
            ParamInfo(
                name="line_count",
                type=int,
                required=False,
                default=0,
                description="Output: Number of lines"
            ),
            ParamInfo(
                name="avg_word_length",
                type=float,
                required=False,
                default=0.0,
                description="Output: Average word length"
            ),
            ParamInfo(
                name="avg_words_per_line",
                type=float,
                required=False,
                default=0.0,
                description="Output: Average words per line"
            )
        ]