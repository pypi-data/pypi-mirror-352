# sphinxcontrib-jsontable

[![Tests](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml/badge.svg)](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable/graph/badge.svg)](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable)
[![Python](https://img.shields.io/pypi/pyversions/sphinxcontrib-jsontable.svg)](https://pypi.org/project/sphinxcontrib-jsontable/)

**言語:** [English](README.md) | [日本語](README_ja.md)

JSONデータ（ファイルまたはインラインコンテンツ）を美しくフォーマットされたreStructuredTextテーブルとしてレンダリングする強力なSphinx拡張機能です。構造化データ、APIサンプル、設定リファレンス、データ駆動型コンテンツを表示するドキュメントに最適です。

## 背景・動機

近年、Retrieval Augmented Generation（RAG）のデータソースとしてドキュメントを活用する傾向が強まっています。しかし、ドキュメント内の表形式データは、RAGシステムに取り込まれる過程で構造的な関連性を失うことが多く、元の構造化データが持つ価値を十分に活用できないという課題がありました。

このような背景から、JSONなどの構造化データをSphinxで生成されるドキュメントに直接、意味のあるテーブルとして埋め込むことで、可読性とデータソースとしての価値を効果的に両立させることを目的として、sphinxcontrib-jsontableが開発されました。

## 機能

✨ **柔軟なデータソース**
* Sphinxプロジェクト内のJSONファイルの読み込み
* ドキュメントに直接JSONを埋め込み
* 安全なパス解決機能付きの相対ファイルパス対応

📊 **複数のデータ形式**
* JSONオブジェクト（単一または配列）
* オプションヘッダー付きの2次元配列
* 自動文字列変換機能付きの混合データ型
* ネストされたデータ構造（適切にフラット化）

🎛️ **カスタマイズ可能な出力**
* 自動キー抽出機能付きのオプションヘッダー行
* 大規模データセット用の行制限
* カスタムファイルエンコーディング対応
* レスポンシブテーブルフォーマット

🔒 **堅牢で安全**
* パストラバーサル攻撃防止
* 包括的なエラーハンドリング
* エンコーディング検証
* デバッグ用詳細ログ

## インストール

### PyPIから
```bash
pip install sphinxcontrib-jsontable
```

### ソースから
```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e .
```

## クイックスタート

### 1. 拡張機能を有効化

`conf.py`に追加：

```python
extensions = [
    # ... その他の拡張機能
    'sphinxcontrib.jsontable',
]
```

### 2. サンプルデータを作成

`data/users.json`を作成：
```json
[
  {
    "id": 1,
    "name": "田中太郎",
    "email": "tanaka@example.com",
    "department": "エンジニアリング",
    "active": true
  },
  {
    "id": 2,
    "name": "佐藤花子",
    "email": "sato@example.com", 
    "department": "マーケティング",
    "active": false
  }
]
```

### 3. ドキュメントに追加

**reStructuredText (.rst) の場合：**
```rst
ユーザーデータベース
==================

.. jsontable:: data/users.json
   :header:
   :limit: 10
```

**Markdown（myst-parser使用）の場合：**
````markdown
# ユーザーデータベース

```{jsontable} data/users.json
:header:
:limit: 10
```
````

### 4. ドキュメントをビルド

```bash
sphinx-build -b html docs/ build/html/
```

## 包括的な使用ガイド

### データ形式サポート

#### オブジェクトの配列（最も一般的）

データベースレコード、APIレスポンス、設定リストに最適：

```json
[
  {"name": "Redis", "port": 6379, "ssl": false},
  {"name": "PostgreSQL", "port": 5432, "ssl": true},
  {"name": "MongoDB", "port": 27017, "ssl": true}
]
```

```rst
.. jsontable:: data/services.json
   :header:
```

**出力：** オブジェクトキー（name、port、ssl）から自動的にヘッダーを生成。

#### ヘッダー付き2次元配列

CSV形式のデータ、レポート、マトリックスに最適：

```json
[
  ["サービス", "ポート", "プロトコル", "状態"],
  ["HTTP", 80, "TCP", "アクティブ"],
  ["HTTPS", 443, "TCP", "アクティブ"],
  ["SSH", 22, "TCP", "非アクティブ"]
]
```

```rst
.. jsontable:: data/ports.json
   :header:
```

**出力：** 最初の行がテーブルヘッダーになります。

#### ヘッダーなし2次元配列

シンプルな表形式データ：

```json
[
  ["月曜日", "晴れ", "24°C"],
  ["火曜日", "曇り", "20°C"],
  ["水曜日", "雨", "17°C"]
]
```

```rst
.. jsontable:: data/weather.json
```

**出力：** すべての行がデータとして扱われます（ヘッダーなし）。

#### 単一オブジェクト

設定オブジェクト、設定、メタデータ：

```json
{
  "database_host": "localhost",
  "database_port": 5432,
  "debug_mode": true,
  "max_connections": 100
}
```

```rst
.. jsontable:: data/config.json
   :header:
```

**出力：** キーが1つの列、値が別の列になります。

### ディレクティブオプション一覧

| オプション | 型 | デフォルト | 説明 | 例 |
|------------|----|-----------|----|---|
| `header` | フラグ | off | 最初の行をテーブルヘッダーとして含める | `:header:` |
| `encoding` | 文字列 | `utf-8` | JSONファイルのファイルエンコーディング | `:encoding: utf-16` |
| `limit` | 正の整数 | 無制限 | 表示する最大行数 | `:limit: 50` |

### 高度な例

#### ページネーション付き大規模データセット

大規模データセットでのパフォーマンスと可読性のため：

```rst
.. jsontable:: data/large_dataset.json
   :header:
   :limit: 20

*1000+レコードの最初の20件を表示。完全なデータセットはソースファイルを参照してください。*
```

#### 非UTF8エンコーディング

レガシーシステムや特定の文字エンコーディングでの作業：

```rst
.. jsontable:: data/legacy_data.json
   :encoding: iso-8859-1
   :header:
```

#### サンプル用インラインJSON

APIドキュメント、サンプル、チュートリアルに最適：

```rst
APIレスポンス形式
================

ユーザーエンドポイントは以下の形式でデータを返します：

.. jsontable::

   {
     "user_id": 12345,
     "username": "tanaka_taro",
     "email": "tanaka@example.com",
     "created_at": "2024-01-15T10:30:00Z",
     "is_verified": true,
     "profile": {
       "first_name": "太郎",
       "last_name": "田中",
       "avatar_url": "https://example.com/avatar.jpg"
     }
   }
```

#### 複雑なネストされたデータ

ネストされたJSONの場合、拡張機能は適切にフラット化します：

```rst
.. jsontable::

   [
     {
       "id": 1,
       "name": "製品A",
       "category": {"name": "電子機器", "id": 10},
       "tags": ["人気", "セール"],
       "price": 99.99
     }
   ]
```

**注意：** 値内のオブジェクトと配列は文字列表現に変換されます。

### 統合例

#### Sphinx Tabsとの連携

sphinx-tabsと組み合わせて多形式ドキュメント作成：

```rst
.. tabs::

   .. tab:: JSONデータ

      .. jsontable:: data/api_response.json
         :header:

   .. tab:: 生JSON

      .. literalinclude:: data/api_response.json
         :language: json
```

#### コードブロックとの連携

リクエスト/レスポンス例でAPIエンドポイントを文書化：

```rst
ユーザー取得エンドポイント
========================

**リクエスト：**

.. code-block:: http

   GET /api/v1/users HTTP/1.1
   Host: api.example.com
   Authorization: Bearer <token>

**レスポンス：**

.. jsontable::

   [
     {
       "id": 1,
       "username": "alice",
       "email": "alice@example.com",
       "status": "active"
     },
     {
       "id": 2, 
       "username": "bob",
       "email": "bob@example.com",
       "status": "inactive"
     }
   ]
```

#### MyST Markdownでの使用

モダンなドキュメントワークフロー用の完全なMyST Markdownサポート：

````markdown
# 設定リファレンス

## データベース設定

```{jsontable} config/database.json
:header:
:encoding: utf-8
```

## 機能フラグ

```{jsontable}
[
  {"feature": "ダークモード", "enabled": true, "rollout": "100%"},
  {"feature": "新ダッシュボード", "enabled": false, "rollout": "0%"},
  {"feature": "高度な検索", "enabled": true, "rollout": "50%"}
]
```
````

### ファイル構成のベストプラクティス

#### 推奨ディレクトリ構造

```
docs/
├── conf.py
├── index.rst
├── data/
│   ├── users.json
│   ├── products.json
│   ├── config/
│   │   ├── database.json
│   │   └── features.json
│   └── examples/
│       ├── api_responses.json
│       └── error_codes.json
└── api/
    └── endpoints.rst
```

#### 命名規則

- 説明的なファイル名を使用：`data1.json`ではなく`user_permissions.json`
- 関連データをサブディレクトリにグループ化：`config/`、`examples/`、`test_data/`
- 適切な場合はバージョンや日付を含める：`api_v2_responses.json`

### パフォーマンス考慮事項

#### 大きなファイル

1000行を超えるファイルの場合：

```rst
.. jsontable:: data/large_dataset.json
   :header:
   :limit: 100

.. note::
   このテーブルは最初の100エントリを表示しています。完全なデータセットをダウンロード： 
   :download:`large_dataset.json <data/large_dataset.json>`
```

#### ビルド時間の最適化

- 非常に大きなデータセットには`:limit:`を使用
- 大きなファイルを小さなチャンクに分割することを検討
- 可能な場合は処理済みJSONをキャッシュ

#### メモリ使用量

拡張機能はJSONファイル全体をメモリに読み込みます。極端に大きなファイル（>100MB）の場合：
- データを小さなチャンクに前処理
- 静的JSONの代わりにデータベースビューを使用
- カスタムページネーションの実装

### トラブルシューティング

#### 一般的な問題

**エラー：「No JSON data source provided」**
```rst
# ❌ ファイルパスまたはコンテンツが不足
.. jsontable::

# ✅ ファイルパスまたはインラインコンテンツを提供  
.. jsontable:: data/example.json
```

**エラー：「JSON file not found」**
- ソースディレクトリからの相対ファイルパスを確認
- ファイルが存在し、正しい権限があることを確認
- ファイル名のタイプミスがないことを確認

**エラー：「Invalid inline JSON」**
- オンラインバリデーターでJSON構文を検証
- 末尾カンマ、引用符なしキーをチェック
- 特殊文字の適切なエスケープを確認

**エンコーディング問題**
```rst
# 非UTF8ファイルの場合
.. jsontable:: data/legacy.json
   :encoding: iso-8859-1
```

**空のテーブル**
- JSONファイルが空またはnullでないかチェック
- JSON構造を確認（配列またはオブジェクトである必要）
- `:limit:`オプションを使用して制限を超えたデータの存在を確認

#### デバッグモード

`conf.py`で詳細ログを有効化：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Sphinx固有のログの場合
extensions = ['sphinxcontrib.jsontable']
```

#### 設定テスト

セットアップを確認するシンプルなテストファイルを作成：

```json
[{"test": "success", "status": "ok"}]
```

```rst
.. jsontable:: test.json
   :header:
```

### セキュリティ考慮事項

#### パストラバーサル攻撃の防止

拡張機能は自動的にディレクトリトラバーサル攻撃を防止します：

```rst
# ❌ これはブロックされます
.. jsontable:: ../../etc/passwd

# ✅ 安全な相対パスのみ
.. jsontable:: data/safe_file.json
```

#### ファイルアクセス

- Sphinxソースディレクトリ内のファイルのみアクセス可能
- ネットワークURLや絶対システムパスは許可されません
- システムによってファイル権限が尊重されます

### 移行ガイド

#### 他の拡張機能から

**sphinx-jsonschemaから：**
- `.. jsonschema::`を`.. jsontable::`に置換
- スキーマ検証オプションを削除
- 必要に応じて`:header:`オプションを追加

**カスタムソリューションから：**
- データをJSON形式にエクスポート
- カスタムテーブル生成を`.. jsontable::`に置換
- ファイルパスをソースディレクトリ相対に更新

#### バージョン互換性

- **Sphinx：** 3.0+（推奨：4.0+）
- **Python：** 3.10+（推奨：3.11+）
- **Docutils：** 0.14+

### APIリファレンス

#### コアクラス

**`JsonTableDirective`**
- メインのSphinxディレクティブクラス
- オプション解析と実行を処理
- データ読み込み、変換、レンダリングを調整

**`JsonDataLoader`**  
- ファイルまたはインラインコンテンツからJSONを読み込み
- エンコーディングとファイルパスを検証
- 安全なファイルアクセスを提供

**`TableConverter`**
- JSON構造を2次元テーブルデータに変換
- 異なるデータ形式を処理（オブジェクト、配列、混合）
- ヘッダー抽出と行制限を管理

**`TableBuilder`**
- Docutilsテーブルノードを生成
- ヘッダー/ボディ付きの適切なテーブル構造を作成
- セルフォーマットとパディングを処理

#### エラーハンドリング

すべてのエラーは`JsonTableError`から継承：
- ファイルアクセスエラー
- JSON解析エラー  
- 無効なデータ構造エラー
- パストラバーサル試行

### コントリビューション

コントリビューションを歓迎します！詳細は[CONTRIBUTING.md](CONTRIBUTING.md)を参照：
- 開発環境セットアップ
- コードスタイルガイドライン
- テスト手順
- プルリクエストプロセス

#### 開発環境セットアップ

```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e ".[dev]"
pytest
```

#### テスト実行

```bash
# 全テスト実行
pytest

# カバレッジ付き実行
pytest --cov=sphinxcontrib.jsontable

# 特定テスト実行
pytest tests/test_directives.py::test_json_table_basic
```

### サンプルリポジトリ

[`examples/`](examples/)ディレクトリで以下を参照：
- 完全なSphinxプロジェクトセットアップ
- 様々なデータ形式の例  
- 他の拡張機能との統合
- 高度な設定例

```bash
cd examples/
sphinx-build -b html . _build/html/
```

### ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下でライセンスされています。

### 変更履歴

詳細なバージョン履歴とリリースノートは[CHANGELOG.md](CHANGELOG.md)を参照してください。

### サポート

- **ドキュメント：** [GitHub Pages](https://sasakama-code.github.io/sphinxcontrib-jsontable/)
- **問題報告：** [GitHub Issues](https://github.com/sasakama-code/sphinxcontrib-jsontable/issues)
- **ディスカッション：** [GitHub Discussions](https://github.com/sasakama-code/sphinxcontrib-jsontable/discussions)
