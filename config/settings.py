"""
アプリケーション設定
"""
import os

# データベース設定
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/team_task_manager"
)

# アプリケーション設定
APP_NAME = "チームタスク管理システム"
APP_DESCRIPTION = "複数メンバーでタスクを管理・可視化するアプリケーション"

# セッション設定
SESSION_TIMEOUT = 3600  # 1時間

# ページ設定
PAGE_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "📋",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# ロール定義
ROLES = {
    "admin": "管理者",
    "manager": "マネージャー",
    "member": "メンバー"
}

# タスクステータス
TASK_STATUS = {
    "pending": "未開始",
    "in_progress": "進行中",
    "completed": "完了",
    "cancelled": "キャンセル"
}

# タスク優先度
TASK_PRIORITY = {
    "low": "低",
    "medium": "中",
    "high": "高"
}
