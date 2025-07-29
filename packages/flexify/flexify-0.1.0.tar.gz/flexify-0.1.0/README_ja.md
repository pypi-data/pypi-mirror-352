# 🚀 Flexify

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)](https://github.com/yourusername/flexify)

**Flexify**は、ワークフローの構築と実行を驚くほど簡単にする、軽量でモジュラーなPythonタスク処理フレームワークです！ 🎯

## ✨ なぜFlexifyなのか？

こんなことでお困りではありませんか？
- 😩 同じ処理パターンを何度も何度も書いている
- 🔧 変更が困難にハードコーディングされたワークフロー
- 📊 複雑なデータパイプラインの可視化と追跡に苦労している
- 🏗️ ニーズに対して過剰すぎる重厚なワークフローエンジンの使用

**Flexifyなら簡単です！** 再利用可能なモジュールを定義し、YAMLやJSONでワークフローを記述するだけで、Flexifyが残りを処理します！

## 🎯 主な機能

- **🧩 モジュラー設計**: 任意の方法で組み合わせ可能な再利用可能な処理モジュールを作成
- **📝 シンプルな設定**: 人間が読みやすいYAMLまたはJSONファイルでワークフローを定義
- **🔄 柔軟なデータフロー**: モジュール間の簡単なパラメータマッピング
- **📊 ステータス追跡**: ワークフロー実行とモジュールステータスをリアルタイムで監視
- **🐍 Pure Python**: 複雑な依存関係や外部サービスは不要
- **🧪 十分にテスト済み**: 包括的なテストスイートで97%のテストカバレッジ
- **📚 豊富な例**: テキスト処理と数学演算のためのすぐに使える例モジュール

## 🚀 クイックスタート

### インストール

```bash
pip install flexify
```

### 最初のモジュールを作成

```python
from typing import Dict, Any, List
from flexify.core import Module, ParamInfo

class GreetingModule(Module):
    """挨拶を作成するシンプルなモジュール"""
    
    def execute(self, session: Dict[str, Any]) -> Dict[str, Any]:
        name = session.get("name", "World")
        greeting = f"こんにちは、{name}さん！"
        session["greeting"] = greeting
        return session
    
    @classmethod
    def get_param_info(cls) -> List[ParamInfo]:
        return [
            ParamInfo(name="name", type=str, required=False, default="World"),
            ParamInfo(name="greeting", type=str, required=False, default="")
        ]
```

### ワークフローを定義

ワークフローファイル `greeting_workflow.yaml` を作成：

```yaml
name: greeting_workflow
version: 1.0.0

modules:
  - name: greet_step
    class_name: your_module.GreetingModule
    params:
      name: "Flexifyユーザー"
```

### ワークフローを実行

```python
from flexify.runner import SimpleRunner

runner = SimpleRunner()
result = runner.run("greeting_workflow.yaml")
print(result["greeting"])  # 出力: こんにちは、Flexifyユーザーさん！
```

## 📖 ドキュメント

### モジュール開発

モジュールはFlexifyワークフローの構成要素です。各モジュールは：
- `Module`基底クラスを継承
- データを処理する`execute()`メソッドを実装
- `get_param_info()`を使用してパラメータを定義
- 実行ステータスを管理

### ワークフロー設定

ワークフローはYAMLまたはJSONで以下を含めて定義できます：
- **name**: ワークフロー識別子
- **modules**: 順番に実行するモジュールのリスト
- **initial_session**: ワークフローの開始データ

### 高度な機能

- **パラメータマッピング**: 入出力マッピングを使用してモジュール間でデータをルーティング
- **モジュールレジストリ**: モジュールの動的検出と読み込み
- **エラーハンドリング**: 包括的なエラー追跡とレポート
- **ステータス監視**: リアルタイムワークフロー実行ステータス

### エラーハンドリング

Flexifyは`FlexifyException`例外を通じて包括的なエラーハンドリングを提供します：

```python
try:
    runner = SimpleRunner()
    result = runner.run("workflow.yaml")
except FlexifyException as e:
    print(f"エラー: {e}")                    # [モジュール名] エラーメッセージ
    print(f"失敗モジュール: {e.module_name}") # モジュール名
    if e.original_error:
        print(f"元の例外: {e.original_error}")
```

一般的なエラーシナリオ：
- **必須パラメータ不足**: `Required input 'param_name' not found`
- **不正なパラメータ型**: `Input 'param_name' has invalid type`
- **モジュール実行失敗**: 実行中の例外をキャプチャしてラップ
- **インポートエラー**: 指定されたモジュールクラスが見つからない場合

### モジュール検出

モジュールは完全なクラスパスを使用して動的に読み込まれます：

```yaml
modules:
  - name: calculator
    class_name: "flexify.examples.math_modules.CalculatorModule"
```

`ModuleRegistry.get_or_import()`メソッドが処理する内容：
- モジュールクラスの動的インポート
- `Module`クラスを継承していることの検証
- パフォーマンス向上のための読み込み済みモジュールのキャッシュ

## 🛠️ 組み込みモジュール

### コア制御フローモジュール
- `LoopModule`: 配列を反復し、各要素に対してサブワークフローを実行
- `CaseModule`: 条件マッチングに基づいて異なるワークフローを実行

### テキスト処理モジュール
- `TextReaderModule`: テキストファイルの読み込み
- `TextTransformModule`: テキスト変換（大文字、小文字、タイトル、逆順）
- `WordCountModule`: テキスト統計の計算

### 数学演算モジュール
- `CalculatorModule`: 基本的な算術演算
- `StatisticsModule`: 統計指標の計算
- `FibonacciModule`: フィボナッチ数列の生成

### 制御フローの例

#### LoopModule
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

#### CaseModule
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

## 💻 システム要件

- **Python**: 3.10以上
- **依存関係**: YAMLサポート用のPyYAML
- **OS**: Windows、macOS、Linux

## 🤝 貢献

貢献を歓迎します！お気軽にイシューを投稿し、リポジトリをフォークして、プルリクエストを作成してください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🙏 謝辞

モダンなPythonのベストプラクティスとクリーンアーキテクチャの原則を使用して❤️で構築されています。

---

**ワークフローを柔軟にする準備はできましたか？** 今すぐFlexifyを始めましょう！ 🚀