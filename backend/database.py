"""
データベース接続管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from config.settings import DATABASE_URL
from backend.models import Base
import os

# SQLiteを使用する場合（開発用）
USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

if USE_SQLITE:
    # SQLiteデータベース（開発用）
    DATABASE_URL = "sqlite:///./team_task_manager.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQLデータベース（本番用）
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """データベースを初期化"""
    Base.metadata.create_all(bind=engine)
    print("✓ データベースが初期化されました")


def drop_db():
    """データベースをドロップ（開発用）"""
    Base.metadata.drop_all(bind=engine)
    print("✓ データベースがドロップされました")
