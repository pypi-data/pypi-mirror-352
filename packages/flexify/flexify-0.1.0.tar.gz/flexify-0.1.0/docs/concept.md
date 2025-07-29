# Flexifyとは？

* yaml, jsonファイルで記載されたフローを実行することができるPythonライブラリです。

## Moduleクラス
* Moduleクラスは抽象型で、実行可能なモジュールを定義します。
* Moduleクラスのサブクラスを検索し、設定ファイルで記載された順に実行できます。
* Moduleサブクラスが必要とする引数、提供する返値(sessionにputする)は、Module#get_param_info() クラスメソッドで提供します。
* Moduleクラスはsession(dict型)を引数とする、executeメソッドを持ちます。executeメソッドでは設定ファイルで指定されたキーから引数を取得し、設定ファイルで指定されているキーへ値をputします。executeメソッドは更新されたsessionを返します。
* Moduleクラスはstatus属性を持ち、必要があれば、それを更新します。

## Runner
* Moduleのサブクラスの実行を行うのがRunnerインターフェースです。
* Runnerインターフェースの責務は、与えられたファイル、それをパースしたオブジェクトから、初期値とモジュール処理手順を読み取り実行します。
* Runnerではどこのモジュールまで完了しているか、それぞれのModuleのステータスが何かを取得し、必要に応じて進捗状況のリクエストに応答することができます。
* まずは単純に実行するSimpleRunnerを実装します。

## ParamInfoクラス
* ParamInfoクラスはModule#get_param_info()で返却されます。
* 個々のパラメータ名、型、必須/オプションの情報が得られます。

## 将来計画
* デコレートされた関数を、アノテーションと型ヒントを使用して検出し、それもモジュールとして扱います。
* 将来的にFastAPI / Tokenを持たせて、送信されたファイルをキューにし、実行できるようにします。
* flexify web startでスタート
* flexify web stopでストップ
* 将来的にはRunnerをPrefect/AirFlowなどの分散環境で実行できるようにします。