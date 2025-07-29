# Flexify 開発タスクリスト

## 高優先度 (High)
- [x] 要件定義書(requirements.md)の作成
- [x] アーキテクチャ設計書(architecture.md)の作成
- [x] pyproject.tomlの修正（--cov=oneenvを--cov=flexifyに変更）
- [x] 文書間矛盾検証
- [x] 文書間の矛盾修正
- [x] 基本データクラス（Module, ParamInfo）の実装
- [x] 基本データクラスのテスト作成・検証

## 中優先度 (Medium)
- [x] ユースケース仕様書(usecase_spec.md)の作成
- [x] 機能仕様書(function_spec.md)の作成
- [x] Runnerインターフェースの実装
- [x] Runnerインターフェースのテスト作成・検証
- [x] SimpleRunnerの実装
- [x] SimpleRunnerのテスト作成・検証

## 低優先度 (Low)
- [x] YAMLパーサーの実装
- [x] YAMLパーサーのテスト作成・検証
- [x] サンプルモジュールの作成
- [x] README.mdの作成（英語）
- [x] README_ja.mdの作成（日本語）

## 実装順序の方針
1. 設計文書の作成（要件定義書→アーキテクチャ設計書→ユースケース仕様書→機能仕様書）
2. 文書間の矛盾修正
3. 基本データクラスの実装とテスト（Module, ParamInfo）
4. Runnerインターフェースの実装とテスト
5. SimpleRunnerの実装とテスト
6. YAMLパーサーとサンプルの作成
7. ドキュメントの整備

## 発見された文書間の矛盾点

### 修正が必要な項目
1. **メソッド名のタイポ**
   - concept.md: `Module#get_parm_info()` → `Module#get_param_info()`

2. **Sessionの実装方法**
   - concept.md: sessionはdict型
   - architecture.md: Sessionは独立したクラス
   - 決定: シンプルにdict型として実装する

3. **Pythonバージョンの統一**
   - requirements.md: Python 3.8+
   - pyproject.toml: Python 3.10+
   - 決定: Python 3.10+に統一

4. **executeメソッドの戻り値**
   - concept.mdで明示されていない
   - architecture.md: Dict型を返す
   - 決定: Dict型（更新されたsession）を返す

5. **FlexifyException例外クラス**
   - requirements.mdで言及されているが定義がない
   - 決定: ドメイン層に追加する（FlexifyExceptionとして実装済み）

6. **WorkflowParserインターフェース**
   - YAMLParser/JSONParserの共通インターフェースとして明確化が必要