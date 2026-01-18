# チームタスク管理アプリケーション

Streamlitを使用したチームタスク管理システムです。複数のメンバーがタスクを作成・管理・可視化できます。

## プロジェクト構成

```
database-final-assignment/
├── app/                    # Streamlitフロントエンド
│   ├── main.py            # フル機能版
│   └── main_simple.py     # 簡略版（推奨）
├── backend/               # バックエンドロジック
│   ├── database.py        # データベース接続
│   ├── models.py          # ORM モデル
│   ├── auth.py            # 認証ロジック
│   └── crud.py            # CRUD操作
├── config/                # 設定ファイル
│   └── settings.py        # アプリケーション設定
├── requirements.txt       # 依存パッケージ
└── team_task_manager.db        # SQLiteデータベース
```

## 機能

- **ユーザー認証**: ハッシュベースの認証システム（bcrypt）
- **タスク管理**: CRUD操作（作成、読取、更新、削除）
- **チーム管理**: 複数メンバーの管理
- **データ可視化**: チャートとダッシュボード
- **アクティビティログ**: ユーザーのアクション管理

## セットアップ

1. リポジトリをクローン
```bash
git clone https://github.com/RyuseiMtz/database-final-assignment.git
cd database-final-assignment
```

2. 仮想環境を作成
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

3. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

4. Streamlitアプリケーションを起動
```bash
streamlit run app/main_simple.py
```

## 使用技術

- **フロントエンド**: Streamlit
- **バックエンド**: Python 3.11
- **データベース**: SQLite
- **ORM**: SQLAlchemy
- **可視化**: Plotly, Matplotlib, Seaborn
