# Tag Factory CLI

Tag Factoryのコマンドラインインターフェースツール

## インストール

開発モードでインストール：

```bash
# プロジェクトディレクトリ内で
pip install -e cli/
```

## 使い方

### 基本的なコマンド

バージョン確認：

```bash
tag-factory --version
```

ヘルプの表示：

```bash
tag-factory --help
```

### ワークスペース関連コマンド

ワークスペース一覧の表示：

```bash
tag-factory workspaces list
```

特定のワークスペースの詳細表示：

```bash
tag-factory workspaces get WORKSPACE_ID
```

現在のワークスペースを設定：

```bash
tag-factory use WORKSPACE_ID
```

### タグ関連コマンド

ワークスペース内のタグ一覧表示：

```bash
# 現在のワークスペースのタグ一覧（useコマンドで設定したワークスペース）
tag-factory tags list

# 特定のワークスペースのタグ一覧
tag-factory tags list --workspace WORKSPACE_ID
```

### ハッシュタグ関連コマンド

ワークスペース内のハッシュタグ一覧表示：

```bash
# 現在のワークスペースのハッシュタグ一覧
tag-factory hashtags list

# 特定のワークスペースのハッシュタグ一覧
tag-factory hashtags list --workspace WORKSPACE_ID
```

### データセット関連コマンド

ワークスペース内のデータセット一覧表示：

```bash
# 現在のワークスペースのデータセット一覧
tag-factory datasets list

# 特定のワークスペースのデータセット一覧
tag-factory datasets list --workspace WORKSPACE_ID
```

データセットのエクスポート：

```bash
# データセットをエクスポート
tag-factory datasets export DATASET_ID

# 出力先ディレクトリとタグファイルの拡張子を指定してエクスポート
tag-factory datasets export DATASET_ID --dest_dir /path/to/directory --tag_extension txt
```

エクスポートコマンドは、データセット内のすべての画像とそれに関連するタグをエクスポートします。
各画像に対して、以下の2つのファイルが作成されます：
- 画像ファイル：`{filename}.{extension}`
- タグファイル：`{filename}.{tag_extension}`（タグはカンマ区切りで1行に記述されます）

オプション：
- `--dest_dir`：エクスポート先ディレクトリ（デフォルト：カレントディレクトリ）
- `--tag_extension`：タグファイルの拡張子（デフォルト：txt）

## 設定

### 環境変数

環境変数を使用して設定します：

- `TAG_FACTORY_API_KEY`: API認証キー（必須）
- `TAG_FACTORY_API_URL`: API URL（オプション、デフォルトは `http://localhost:3000/api/cli`）

例：

```bash
# APIキーの設定
export TAG_FACTORY_API_KEY="your-api-key"

# カスタムAPIエンドポイントの設定（オプション）
export TAG_FACTORY_API_URL="https://your-api-url.com/api/cli"
```

### 設定ファイル

CLIツールは `~/.tag-factory/config.json` に設定情報を保存します。
特に「現在のワークスペース」の情報はこのファイルに保存され、各コマンドで `--workspace` オプションを省略した場合に使用されます。

## 開発

開発環境のセットアップ：

```bash
# 依存関係のインストール
pip install -e cli/
```

## PyPIへのパブリッシュ

このCLIツールは、「tag-factory」という名前でPyPIに公開することができます。
パブリッシュするには、同梱の `publish.sh` スクリプトを使用してください：

```bash
cd cli
./publish.sh
```

このスクリプトは以下の処理を行います：
1. パッケージをビルド
2. オプションでTest PyPIにアップロード（テスト用）
3. 本番PyPIにアップロード

PyPIにパブリッシュするには、以下のいずれかの方法で認証情報を提供する必要があります：
- 環境変数 `PYPI_API_TOKEN` の設定（推奨）
- パブリッシュ時に対話的にAPIトークンを入力
- `~/.pypirc` ファイルの設定（APIトークンを使用）

### PyPI APIトークンの取得方法

PyPIは現在ユーザー名/パスワード認証をサポートしていないため、APIトークンが必要です：

1. [PyPI](https://pypi.org/) にログイン
2. アカウントメニュー -> アカウント設定 -> APIトークン
3. 「APIトークンを追加」をクリック
4. スコープを「プロジェクト: tag-factory」に設定し、トークンを作成
5. 生成されたトークンを安全に保存（表示は1回のみ）

APIトークンを環境変数として設定：

```bash
export PYPI_API_TOKEN="pypi-AgEI..."
```

### インストール

パブリッシュ後は、以下のコマンドでインストールできます：

```bash
pip install tag-factory
```

## ライセンス

このCLIツールはTag Factoryの一部であり、商用ソフトウェアです。すべての権利が保有者に帰属し、無許可での使用、複製、配布は禁止されています。
