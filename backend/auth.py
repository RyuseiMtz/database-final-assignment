"""
認証ロジック
"""
import bcrypt
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models import User


def hash_password(password: str) -> str:
    """パスワードをハッシュ化"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """パスワードを検証"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def create_user(db: Session, username: str, email: str, password: str, full_name: str = None, role: str = "member") -> User:
    """新しいユーザーを作成"""
    # ユーザーが既に存在するか確認
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        raise ValueError("ユーザー名またはメールアドレスは既に使用されています")
    
    # パスワードをハッシュ化
    password_hash = hash_password(password)
    
    # 新しいユーザーを作成
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name or username,
        role=role,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def authenticate_user(db: Session, username: str, password: str) -> User:
    """ユーザーを認証"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def get_user_by_id(db: Session, user_id: int) -> User:
    """IDでユーザーを取得"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User:
    """ユーザー名でユーザーを取得"""
    return db.query(User).filter(User.username == username).first()


def update_user(db: Session, user_id: int, **kwargs) -> User:
    """ユーザー情報を更新"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    for key, value in kwargs.items():
        if key == "password":
            user.password_hash = hash_password(value)
        elif hasattr(user, key):
            setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user
